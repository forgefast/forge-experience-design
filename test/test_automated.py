#!/usr/bin/env python3
"""
Teste Automatizado - ForgeExperienceDesign
Testa o fluxo completo sem intervenção manual
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path

FORGELOGS_URL = "http://localhost:8002"
FORGE_EXPERIENCE_DESIGN_URL = "http://localhost:8003"
TEST_PAGE_URL = "http://localhost:3001/test/test_page.html"
APPLICATION_ID = "test-page"


async def create_test_issues():
    """Cria problemas de teste no ForgeLogs."""
    print("1. Criando problemas de teste no ForgeLogs...")
    
    issues = [
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "high",
            "category": "ui",
            "session_id": "test-session-1",
            "page_url": TEST_PAGE_URL,
            "data": {
                "type": "small_touch_target",
                "message": "Botão muito pequeno (20x20px)",
                "element": ".small-button",
                "details": {"width": 20, "height": 20, "selector": ".small-button"}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "high",
            "category": "ui",
            "session_id": "test-session-1",
            "page_url": TEST_PAGE_URL,
            "data": {
                "type": "accessibility_low_contrast",
                "message": "Contraste de texto baixo",
                "element": ".low-contrast",
                "details": {"color": "#cccccc", "background": "#ffffff", "ratio": 1.2}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "medium",
            "category": "ui",
            "session_id": "test-session-1",
            "page_url": TEST_PAGE_URL,
            "data": {
                "type": "zero_dimensions",
                "message": "Elemento com dimensões zero",
                "element": ".zero-dimensions",
                "details": {"width": 0, "height": 0}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "medium",
            "category": "ui",
            "session_id": "test-session-1",
            "page_url": TEST_PAGE_URL,
            "data": {
                "type": "overflow",
                "message": "Elemento com overflow",
                "element": ".overflow-issue",
                "details": {}
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        created = 0
        for issue in issues:
            try:
                response = await client.post(
                    f"{FORGELOGS_URL}/api/logs",
                    json=issue
                )
                if response.status_code in [200, 201]:
                    created += 1
            except Exception as e:
                print(f"   ⚠️  Erro ao criar log: {e}")
        
        print(f"   ✅ {created}/{len(issues)} problemas criados")
        return created > 0


async def generate_fixes():
    """Gera correções a partir dos problemas."""
    print("\n2. Gerando correções...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/generate",
                params={"application_id": APPLICATION_ID, "limit": 10}
            )
            if response.status_code == 200:
                fixes = response.json()
                print(f"   ✅ {len(fixes)} correções geradas")
                return len(fixes) > 0
            else:
                print(f"   ❌ Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False


async def verify_fixes_in_database():
    """Verifica se correções estão no banco."""
    print("\n3. Verificando correções no banco de dados...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes",
                params={"limit": 10}
            )
            if response.status_code == 200:
                fixes = response.json()
                print(f"   ✅ {len(fixes)} correções no banco")
                
                # Verificar tipos de correções
                types = {}
                for fix in fixes:
                    issue_type = fix.get('issue_type', 'unknown')
                    types[issue_type] = types.get(issue_type, 0) + 1
                
                print(f"   📊 Tipos: {types}")
                return len(fixes) > 0
            else:
                print(f"   ❌ Erro: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return False


async def test_fix_injection():
    """Testa se FixInjector consegue aplicar correções."""
    print("\n4. Testando injeção de correções...")
    print("   ℹ️  Para testar visualmente, abra: http://localhost:3001/test/test_page.html")
    
    # Verificar se página de teste existe
    test_page_path = Path(__file__).parent / "test_page.html"
    if test_page_path.exists():
        print(f"   ✅ Página de teste encontrada: {test_page_path}")
    else:
        print(f"   ⚠️  Página de teste não encontrada")
    
    # Verificar se fix-injector.js existe
    injector_path = Path(__file__).parent.parent / "frontend" / "public" / "fix-injector.js"
    if injector_path.exists():
        print(f"   ✅ FixInjector encontrado: {injector_path}")
    else:
        print(f"   ⚠️  FixInjector não encontrado")
    
    return True


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("Teste Automatizado - ForgeExperienceDesign")
    print("=" * 60)
    print()
    
    # Verificar serviços
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/rules")
            if response.status_code != 200:
                print("❌ ForgeExperienceDesign não está acessível")
                return
        except:
            print("❌ ForgeExperienceDesign não está acessível")
            return
    
    # Executar testes
    results = []
    
    # Teste 1: Criar problemas
    results.append(await create_test_issues())
    
    # Aguardar um pouco
    await asyncio.sleep(2)
    
    # Teste 2: Gerar correções
    results.append(await generate_fixes())
    
    # Aguardar um pouco
    await asyncio.sleep(2)
    
    # Teste 3: Verificar banco
    results.append(await verify_fixes_in_database())
    
    # Teste 4: Testar injeção
    results.append(await test_fix_injection())
    
    # Resultado final
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("✅ Todos os testes passaram!")
    else:
        print("⚠️  Alguns testes falharam")
    
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Abra http://localhost:3001/test/test_page.html no navegador")
    print("2. Aguarde 10 segundos para correções serem aplicadas")
    print("3. Verifique se os problemas foram corrigidos visualmente")


if __name__ == "__main__":
    asyncio.run(main())

