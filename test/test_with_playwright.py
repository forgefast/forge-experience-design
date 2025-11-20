#!/usr/bin/env python3
"""
Teste Automatizado com Playwright
Testa o fluxo completo: problemas → correções → aplicação → validação
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path

# Tentar importar playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright não instalado. Instale com: pip install playwright && playwright install")

FORGELOGS_URL = "http://localhost:8002"
FORGE_EXPERIENCE_DESIGN_URL = "http://localhost:8003"
TEST_PAGE_URL = "http://localhost:3001/test/test_page.html"
APPLICATION_ID = "test-page"


async def setup_test_environment():
    """Prepara ambiente de teste."""
    print("=" * 60)
    print("Preparando Ambiente de Teste")
    print("=" * 60)
    
    # 1. Criar problemas no ForgeLogs
    print("\n1. Criando problemas de teste...")
    issues = [
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "high",
            "category": "ui",
            "session_id": "test-session",
            "page_url": TEST_PAGE_URL,
            "data": {
                "type": "small_touch_target",
                "message": "Botão muito pequeno",
                "element": ".small-button",
                "details": {"width": 20, "height": 20}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "high",
            "category": "ui",
            "session_id": "test-session",
            "page_url": TEST_PAGE_URL,
            "data": {
                "type": "zero_dimensions",
                "message": "Elemento com dimensões zero",
                "element": ".zero-dimensions",
                "details": {"width": 0, "height": 0}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        created = 0
        for issue in issues:
            try:
                response = await client.post(f"{FORGELOGS_URL}/api/logs", json=issue)
                if response.status_code in [200, 201]:
                    created += 1
            except Exception as e:
                print(f"   ⚠️  Erro: {e}")
        
        print(f"   ✅ {created}/{len(issues)} problemas criados")
    
    # 2. Gerar correções
    print("\n2. Gerando correções...")
    await asyncio.sleep(2)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/generate",
                params={"application_id": APPLICATION_ID, "limit": 10}
            )
            if response.status_code == 200:
                fixes = response.json()
                print(f"   ✅ {len(fixes)} correções geradas")
            else:
                print(f"   ⚠️  Status {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Erro: {e}")


def test_with_playwright():
    """Testa aplicação de correções com Playwright."""
    if not PLAYWRIGHT_AVAILABLE:
        print("\n❌ Playwright não disponível. Pulando teste visual.")
        return False
    
    print("\n" + "=" * 60)
    print("Teste Visual com Playwright")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False para ver
        page = browser.new_page()
        
        try:
            # 1. Abrir página de teste
            print("\n1. Abrindo página de teste...")
            page.goto(TEST_PAGE_URL, wait_until="networkidle")
            print("   ✅ Página carregada")
            
            # 2. Verificar problemas iniciais
            print("\n2. Verificando problemas iniciais...")
            small_button = page.locator(".small-button")
            initial_width = small_button.evaluate("el => parseInt(window.getComputedStyle(el).width)")
            initial_height = small_button.evaluate("el => parseInt(window.getComputedStyle(el).height)")
            print(f"   📏 Botão inicial: {initial_width}x{initial_height}px")
            
            # 3. Aguardar FixInjector aplicar correções
            print("\n3. Aguardando correções serem aplicadas (15 segundos)...")
            page.wait_for_timeout(15000)
            
            # 4. Verificar se correções foram aplicadas
            print("\n4. Verificando correções aplicadas...")
            
            # Verificar botão pequeno
            final_width = small_button.evaluate("el => parseInt(window.getComputedStyle(el).minWidth) || parseInt(window.getComputedStyle(el).width)")
            final_height = small_button.evaluate("el => parseInt(window.getComputedStyle(el).minHeight) || parseInt(window.getComputedStyle(el).height)")
            print(f"   📏 Botão após correção: {final_width}x{final_height}px")
            
            if final_width >= 44 and final_height >= 44:
                print("   ✅ Botão foi corrigido! (>= 44x44px)")
                button_fixed = True
            else:
                print(f"   ❌ Botão ainda pequeno ({final_width}x{final_height}px)")
                button_fixed = False
            
            # Verificar elemento com dimensões zero
            zero_elem = page.locator(".zero-dimensions")
            zero_width = zero_elem.evaluate("el => parseInt(window.getComputedStyle(el).minWidth) || parseInt(window.getComputedStyle(el).width)")
            zero_height = zero_elem.evaluate("el => parseInt(window.getComputedStyle(el).minHeight) || parseInt(window.getComputedStyle(el).height)")
            print(f"   📏 Elemento zero: {zero_width}x{zero_height}px")
            
            if zero_width > 0 or zero_height > 0:
                print("   ✅ Elemento zero foi corrigido!")
                zero_fixed = True
            else:
                print("   ❌ Elemento ainda tem dimensões zero")
                zero_fixed = False
            
            # Verificar se CSS foi injetado
            style_element = page.locator("#forge-experience-design-fixes")
            if style_element.count() > 0:
                css_content = style_element.inner_text()
                print(f"\n   ✅ CSS injetado ({len(css_content)} caracteres)")
                if "min-width" in css_content and "44px" in css_content:
                    print("   ✅ CSS contém correções esperadas")
                    css_injected = True
                else:
                    print("   ⚠️  CSS não contém correções esperadas")
                    css_injected = False
            else:
                print("   ❌ CSS não foi injetado")
                css_injected = False
            
            # Resultado final
            print("\n" + "=" * 60)
            results = [button_fixed, zero_fixed, css_injected]
            passed = sum(results)
            total = len(results)
            
            print(f"Resultado: {passed}/{total} verificações passaram")
            
            if passed == total:
                print("✅ TODOS OS TESTES PASSARAM!")
                return True
            else:
                print("⚠️  Alguns testes falharam")
                return False
            
        except Exception as e:
            print(f"\n❌ Erro durante teste: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Manter browser aberto por 5 segundos para inspeção
            print("\n📸 Browser ficará aberto por 5 segundos para inspeção...")
            page.wait_for_timeout(5000)
            browser.close()


async def main():
    """Executa todos os testes."""
    # Preparar ambiente
    await setup_test_environment()
    
    # Aguardar um pouco
    await asyncio.sleep(3)
    
    # Teste com Playwright
    if PLAYWRIGHT_AVAILABLE:
        success = test_with_playwright()
    else:
        print("\n⚠️  Para teste visual completo, instale Playwright:")
        print("   pip install playwright")
        print("   playwright install chromium")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TESTE COMPLETO PASSOU!")
    else:
        print("⚠️  Teste não pôde ser completado automaticamente")
    print("=" * 60)
    
    print("\nPara testar manualmente:")
    print(f"1. Abra: {TEST_PAGE_URL}")
    print("2. Aguarde 10-15 segundos")
    print("3. Verifique se os problemas foram corrigidos visualmente")


if __name__ == "__main__":
    asyncio.run(main())

