#!/usr/bin/env python3
"""
Teste de Correção no Código Fonte
Testa o fluxo completo: preview → aplicação → validação
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path

FORGELOGS_URL = "http://localhost:8002"
FORGE_EXPERIENCE_DESIGN_URL = "http://localhost:8003"
FORGETEST_STUDIO_PATH = "/home/gabriel/softhill/forgetest-studio"
APPLICATION_ID = "forgetest-studio"


async def check_services():
    """Verifica se serviços estão rodando."""
    print("=" * 60)
    print("Verificando Serviços")
    print("=" * 60)
    
    services_ok = True
    
    # Verificar ForgeLogs
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FORGELOGS_URL}/api/logs", timeout=5.0)
            if response.status_code in [200, 404]:
                print("✅ ForgeLogs: OK")
            else:
                print(f"⚠️  ForgeLogs: Status {response.status_code}")
                # Não falhar se ForgeLogs não estiver disponível
    except Exception as e:
        print(f"⚠️  ForgeLogs: {e} (continuando mesmo assim)")
    
    # Verificar ForgeExperienceDesign
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/rules", timeout=5.0)
            if response.status_code == 200:
                print("✅ ForgeExperienceDesign: OK")
            else:
                print(f"⚠️  ForgeExperienceDesign: Status {response.status_code}")
                services_ok = False
    except Exception as e:
        print(f"❌ ForgeExperienceDesign: {e}")
        services_ok = False
    
    return services_ok


async def create_test_issue():
    """Cria problema de teste no ForgeLogs."""
    print("\n" + "=" * 60)
    print("Criando Problema de Teste")
    print("=" * 60)
    
    issue = {
        "application_id": APPLICATION_ID,
        "log_type": "ui_issue",
        "severity": "high",
        "category": "ui",
        "session_id": "test-session-source",
        "page_url": "http://localhost:3000",
        "data": {
            "type": "small_touch_target",
            "message": "Botão muito pequeno para teste de correção no código fonte",
            "element": ".btn-base",
            "details": {
                "width": 20,
                "height": 20,
                "selector": ".btn-base",
                "recommended_min": 44
            }
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(f"{FORGELOGS_URL}/api/logs", json=issue)
            if response.status_code in [200, 201]:
                print("✅ Problema criado no ForgeLogs")
                return True
            else:
                print(f"⚠️  Status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False


async def generate_fix():
    """Gera correção."""
    print("\n" + "=" * 60)
    print("Gerando Correção")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/generate",
                params={"application_id": APPLICATION_ID, "limit": 1}
            )
            
            if response.status_code == 200:
                fixes = response.json()
                if fixes:
                    fix = fixes[0]
                    print(f"✅ Correção gerada: {fix.get('id', 'N/A')}")
                    print(f"   Seletor: {fix.get('target_selector', 'N/A')}")
                    print(f"   Mudanças: {len(fix.get('changes', []))}")
                    return fix
                else:
                    print("⚠️  Nenhuma correção gerada")
                    return None
            else:
                print(f"❌ Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None


async def test_preview(fix_id: str):
    """Testa preview de correção."""
    print("\n" + "=" * 60)
    print("Testando Preview")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/{fix_id}/preview"
            )
            
            if response.status_code == 200:
                preview = response.json()
                print(f"✅ Preview gerado")
                print(f"   Arquivo: {preview.get('file_path', 'N/A')}")
                print(f"   Linhas adicionadas: {preview.get('statistics', {}).get('added_lines', 0)}")
                print(f"   Linhas removidas: {preview.get('statistics', {}).get('removed_lines', 0)}")
                print(f"   Diff: {len(preview.get('diff', ''))} caracteres")
                return preview
            else:
                print(f"❌ Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None


async def test_apply_source(fix_id: str):
    """Testa aplicação no código fonte."""
    print("\n" + "=" * 60)
    print("Testando Aplicação no Código Fonte")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/{fix_id}/apply-source",
                params={"create_backup": True}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Correção aplicada com sucesso!")
                    print(f"   Arquivo: {result.get('file_path', 'N/A')}")
                    print(f"   Backup: {result.get('backup_path', 'N/A')}")
                    print(f"   Mudanças: {len(result.get('changes_applied', []))}")
                    return result
                else:
                    print(f"❌ Falha: {result.get('errors', [])}")
                    return None
            else:
                print(f"❌ Status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None


def verify_file_changes(file_path: str, changes: list):
    """Verifica se arquivo foi modificado corretamente."""
    print("\n" + "=" * 60)
    print("Verificando Mudanças no Arquivo")
    print("=" * 60)
    
    full_path = Path(FORGETEST_STUDIO_PATH) / file_path
    
    if not full_path.exists():
        print(f"❌ Arquivo não encontrado: {full_path}")
        return False
    
    try:
        content = full_path.read_text(encoding='utf-8')
        
        # Verificar se mudanças foram aplicadas
        all_applied = True
        for change in changes:
            property_name = change.get("property", "")
            value = change.get("value", "")
            
            # Verificar se propriedade existe no arquivo
            if property_name and value:
                # Procurar propriedade com valor
                pattern = f"{property_name}\\s*:\\s*{value.replace('px', 'px')}"
                import re
                if re.search(pattern, content):
                    print(f"✅ {property_name}: {value} - Aplicado")
                else:
                    print(f"⚠️  {property_name}: {value} - Não encontrado")
                    all_applied = False
        
        return all_applied
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False


async def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTE DE CORREÇÃO NO CÓDIGO FONTE")
    print("=" * 60)
    print()
    
    # 1. Verificar serviços
    await check_services()
    # Continuar mesmo se alguns serviços não estiverem disponíveis
    
    # 2. Criar problema
    if not await create_test_issue():
        print("\n⚠️  Continuando mesmo sem criar problema (pode já existir)")
    
    await asyncio.sleep(2)
    
    # 3. Gerar correção
    fix = await generate_fix()
    if not fix:
        print("\n❌ Não foi possível gerar correção")
        return
    
    fix_id = fix.get("id")
    if not fix_id:
        print("\n❌ Fix sem ID")
        return
    
    await asyncio.sleep(1)
    
    # 4. Testar preview
    preview = await test_preview(fix_id)
    if not preview:
        print("\n❌ Preview falhou")
        return
    
    await asyncio.sleep(1)
    
    # 5. Testar aplicação
    apply_result = await test_apply_source(fix_id)
    if not apply_result:
        print("\n❌ Aplicação falhou")
        return
    
    # 6. Verificar arquivo
    file_path = apply_result.get("file_path")
    changes = apply_result.get("changes_applied", [])
    
    if file_path:
        verify_file_changes(file_path, changes)
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print("✅ Teste completo executado!")
    print(f"   Correção ID: {fix_id}")
    print(f"   Arquivo modificado: {file_path}")
    print(f"   Backup criado: {apply_result.get('backup_path', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

