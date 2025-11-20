#!/usr/bin/env python3
"""
Teste Real com ForgeTest Studio
Testa o fluxo completo: problemas reais → correções → aplicação no código
"""

import asyncio
import httpx
import sys
from pathlib import Path
from datetime import datetime

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

FORGELOGS_URL = "http://localhost:8002"
FORGE_EXPERIENCE_DESIGN_URL = "http://localhost:8003"
FORGETEST_STUDIO_URL = "http://localhost:3000"
FORGETEST_STUDIO_PATH = "/home/gabriel/softhill/forgetest-studio"
APPLICATION_ID = "forgetest-studio"


async def check_all_services():
    """Verifica se todos os serviços estão rodando."""
    print("=" * 60)
    print("Verificando Serviços")
    print("=" * 60)
    
    services = {}
    
    # ForgeTest Studio
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(FORGETEST_STUDIO_URL, timeout=5.0)
            services['forgetest-studio'] = response.status_code in [200, 404]
            print(f"{'✅' if services['forgetest-studio'] else '❌'} ForgeTest Studio: {FORGETEST_STUDIO_URL}")
    except Exception as e:
        services['forgetest-studio'] = False
        print(f"❌ ForgeTest Studio: {e}")
    
    # ForgeLogs
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FORGELOGS_URL}/api/logs", timeout=5.0)
            services['forgelogs'] = response.status_code in [200, 404, 500]
            print(f"{'✅' if services['forgelogs'] else '❌'} ForgeLogs: {FORGELOGS_URL}")
    except Exception as e:
        services['forgelogs'] = False
        print(f"❌ ForgeLogs: {e}")
    
    # ForgeExperienceDesign
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/rules", timeout=5.0)
            services['forgedesign'] = response.status_code == 200
            print(f"{'✅' if services['forgedesign'] else '❌'} ForgeExperienceDesign: {FORGE_EXPERIENCE_DESIGN_URL}")
    except Exception as e:
        services['forgedesign'] = False
        print(f"❌ ForgeExperienceDesign: {e}")
    
    return services


async def create_real_issues():
    """Cria problemas reais baseados no ForgeTest Studio."""
    print("\n" + "=" * 60)
    print("Criando Problemas Reais")
    print("=" * 60)
    
    issues = [
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "high",
            "category": "ui",
            "session_id": f"test-real-{datetime.now().timestamp()}",
            "page_url": FORGETEST_STUDIO_URL,
            "data": {
                "type": "small_touch_target",
                "message": "Botão .btn-base muito pequeno (20x20px detectado)",
                "element": ".btn-base",
                "details": {
                    "width": 20,
                    "height": 20,
                    "selector": ".btn-base",
                    "recommended_min": 44,
                    "file": "gui/frontend/src/styles/components.css"
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        {
            "application_id": APPLICATION_ID,
            "log_type": "ui_issue",
            "severity": "medium",
            "category": "ui",
            "session_id": f"test-real-{datetime.now().timestamp()}",
            "page_url": FORGETEST_STUDIO_URL,
            "data": {
                "type": "accessibility_missing_focus",
                "message": "Elemento .btn-base sem indicador de foco visível",
                "element": ".btn-base",
                "details": {
                    "selector": ".btn-base",
                    "file": "gui/frontend/src/styles/components.css"
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    created = 0
    async with httpx.AsyncClient(timeout=10.0) as client:
        for issue in issues:
            try:
                response = await client.post(f"{FORGELOGS_URL}/api/logs", json=issue)
                if response.status_code in [200, 201]:
                    created += 1
                    print(f"✅ Problema criado: {issue['data']['type']}")
                else:
                    print(f"⚠️  Status {response.status_code} para {issue['data']['type']}")
            except Exception as e:
                print(f"⚠️  Erro ao criar {issue['data']['type']}: {e}")
    
    print(f"\n✅ {created}/{len(issues)} problemas criados")
    return created > 0


async def generate_fixes_from_issues():
    """Gera correções a partir dos problemas."""
    print("\n" + "=" * 60)
    print("Gerando Correções")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/generate",
                params={"application_id": APPLICATION_ID, "limit": 10}
            )
            
            if response.status_code == 200:
                fixes = response.json()
                print(f"✅ {len(fixes)} correções geradas")
                
                for fix in fixes[:3]:  # Mostrar primeiras 3
                    print(f"   - {fix.get('target_selector', 'N/A')}: {len(fix.get('changes', []))} mudanças")
                
                return fixes
            else:
                print(f"❌ Status {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return []


async def test_preview_and_apply(fix_id: str):
    """Testa preview e aplicação de uma correção."""
    print("\n" + "=" * 60)
    print(f"Testando Correção: {fix_id}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Preview
        print("\n1. Gerando Preview...")
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/{fix_id}/preview",
                params={"project_id": APPLICATION_ID}
            )
            
            if response.status_code == 200:
                preview = response.json()
                print(f"   ✅ Preview gerado")
                print(f"   Arquivo: {preview.get('file_path', 'N/A')}")
                stats = preview.get('statistics', {})
                print(f"   +{stats.get('added_lines', 0)} / -{stats.get('removed_lines', 0)} linhas")
                return preview
            else:
                print(f"   ❌ Preview falhou: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"   ❌ Erro no preview: {e}")
            return None


async def apply_fix_to_source(fix_id: str):
    """Aplica correção no código fonte."""
    print("\n2. Aplicando no Código Fonte...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/{fix_id}/apply-source",
                params={"create_backup": True, "project_id": APPLICATION_ID}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ Correção aplicada!")
                    print(f"   Arquivo: {result.get('file_path', 'N/A')}")
                    print(f"   Backup: {result.get('backup_path', 'N/A')}")
                    changes = result.get('changes_applied', [])
                    print(f"   Mudanças: {len(changes)}")
                    for change in changes:
                        print(f"     - {change.get('property')}: {change.get('action')}")
                    return result
                else:
                    print(f"   ❌ Falha: {result.get('errors', [])}")
                    return None
            else:
                print(f"   ❌ Status {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return None
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return None


def verify_file_changes(file_path: str, expected_changes: list):
    """Verifica se arquivo foi modificado corretamente."""
    print("\n3. Verificando Mudanças no Arquivo...")
    
    full_path = Path(FORGETEST_STUDIO_PATH) / file_path
    
    if not full_path.exists():
        print(f"   ❌ Arquivo não encontrado: {full_path}")
        return False
    
    try:
        content = full_path.read_text(encoding='utf-8')
        
        # Verificar seletor .btn-base
        import re
        btn_base_match = re.search(r'\.btn-base\s*\{[^}]*\}', content, re.DOTALL)
        
        if btn_base_match:
            block = btn_base_match.group(0)
            print(f"   ✅ Seletor .btn-base encontrado")
            
            # Verificar mudanças esperadas
            all_found = True
            for change in expected_changes:
                prop = change.get('property', '')
                value = change.get('value', '')
                if prop and value:
                    # Procurar propriedade
                    if prop in block and value in block:
                        print(f"   ✅ {prop}: {value} encontrado")
                    else:
                        print(f"   ⚠️  {prop}: {value} não encontrado")
                        all_found = False
            
            # Mostrar bloco modificado
            print(f"\n   Conteúdo do seletor .btn-base:")
            lines = block.split('\n')[:15]
            for i, line in enumerate(lines, 1):
                marker = ">>>" if any(c.get('property') in line for c in expected_changes) else "   "
                print(f"   {marker} {line}")
            
            return all_found
        else:
            print(f"   ❌ Seletor .btn-base não encontrado no arquivo")
            return False
    
    except Exception as e:
        print(f"   ❌ Erro ao ler arquivo: {e}")
        return False


async def main():
    """Executa teste completo."""
    print("\n" + "=" * 60)
    print("TESTE REAL COM FORGETEST STUDIO")
    print("=" * 60)
    print()
    
    # 1. Verificar serviços
    services = await check_all_services()
    
    if not services.get('forgedesign'):
        print("\n❌ ForgeExperienceDesign não está rodando!")
        print("   Inicie com: cd forge-experience-design && python3 -m backend.main")
        return
    
    if not services.get('forgetest-studio'):
        print("\n⚠️  ForgeTest Studio não está rodando (opcional para este teste)")
    
    await asyncio.sleep(1)
    
    # 2. Criar problemas
    if services.get('forgelogs'):
        await create_real_issues()
        await asyncio.sleep(2)
    else:
        print("\n⚠️  ForgeLogs não disponível, usando correções existentes")
    
    # 3. Gerar correções
    fixes = await generate_fixes_from_issues()
    
    if not fixes:
        print("\n❌ Nenhuma correção gerada")
        return
    
    # 4. Testar primeira correção
    fix = fixes[0]
    fix_id = fix.get('id')
    
    if not fix_id:
        print("\n❌ Fix sem ID")
        return
    
    # 5. Preview e Aplicação
    preview = await test_preview_and_apply(fix_id)
    
    if preview:
        file_path = preview.get('file_path')
        changes_summary = preview.get('changes_summary', [])
        
        # 6. Aplicar
        apply_result = await apply_fix_to_source(fix_id)
        
        if apply_result:
            # 7. Verificar arquivo
            verify_file_changes(file_path, changes_summary)
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print("✅ Teste completo executado!")
    print(f"   Correções geradas: {len(fixes)}")
    if preview:
        print(f"   Arquivo modificado: {preview.get('file_path', 'N/A')}")
    print("\n💡 Para ver as mudanças:")
    if preview:
        print(f"   cat {FORGETEST_STUDIO_PATH}/{preview.get('file_path', '')}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

