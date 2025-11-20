#!/usr/bin/env python3
"""
Teste Direto de Correção no Código Fonte
Testa preview e aplicação sem depender do ForgeLogs
"""

import asyncio
import httpx
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

FORGE_EXPERIENCE_DESIGN_URL = "http://localhost:8003"
FORGETEST_STUDIO_PATH = "/home/gabriel/softhill/forgetest-studio"


async def create_test_fix_directly():
    """Cria correção de teste diretamente no banco."""
    print("=" * 60)
    print("Criando Correção de Teste")
    print("=" * 60)
    
    from backend.infrastructure.storage.fix_repository import FixRepository
    
    fix_repository = FixRepository()
    await fix_repository.initialize()
    
    # Criar correção de teste
    test_fix = {
        "type": "css",
        "target_element": ".btn-base",
        "target_selector": ".btn-base",
        "changes": [
            {
                "property": "min-width",
                "value": "44px",
                "action": "modify",
                "reason": "Aumentar tamanho mínimo para acessibilidade"
            },
            {
                "property": "min-height",
                "value": "44px",
                "action": "modify",
                "reason": "Aumentar altura mínima para acessibilidade"
            }
        ],
        "priority": 9,
        "status": "pending",
        "issue_type": "small_touch_target"
    }
    
    fix_id = await fix_repository.save_fix(test_fix)
    print(f"✅ Correção criada: {fix_id}")
    return fix_id


async def test_preview(fix_id: str):
    """Testa preview de correção."""
    print("\n" + "=" * 60)
    print("Testando Preview")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/{fix_id}/preview",
                params={"project_id": "forgetest-studio"}
            )
            
            if response.status_code == 200:
                preview = response.json()
                print(f"✅ Preview gerado com sucesso!")
                print(f"   Arquivo: {preview.get('file_path', 'N/A')}")
                print(f"   Linhas adicionadas: {preview.get('statistics', {}).get('added_lines', 0)}")
                print(f"   Linhas removidas: {preview.get('statistics', {}).get('removed_lines', 0)}")
                
                # Mostrar parte do diff
                diff = preview.get('diff', '')
                if diff:
                    lines = diff.split('\n')[:10]
                    print(f"\n   Primeiras linhas do diff:")
                    for line in lines:
                        print(f"   {line}")
                
                return preview
            else:
                print(f"❌ Status {response.status_code}")
                print(f"   Resposta: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
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
                    changes = result.get('changes_applied', [])
                    print(f"   Mudanças aplicadas: {len(changes)}")
                    for change in changes:
                        print(f"     - {change.get('property')}: {change.get('action')}")
                    return result
                else:
                    print(f"❌ Falha: {result.get('errors', [])}")
                    return None
            else:
                print(f"❌ Status {response.status_code}")
                print(f"   Resposta: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
            return None


def verify_file_changes(file_path: str):
    """Verifica se arquivo foi modificado."""
    print("\n" + "=" * 60)
    print("Verificando Mudanças no Arquivo")
    print("=" * 60)
    
    full_path = Path(FORGETEST_STUDIO_PATH) / file_path
    
    if not full_path.exists():
        print(f"❌ Arquivo não encontrado: {full_path}")
        return False
    
    try:
        content = full_path.read_text(encoding='utf-8')
        
        # Verificar se min-width e min-height foram aplicados
        has_min_width = "min-width" in content and "44px" in content
        has_min_height = "min-height" in content and "44px" in content
        
        if has_min_width:
            print("✅ min-width: 44px encontrado")
        else:
            print("⚠️  min-width: 44px não encontrado")
        
        if has_min_height:
            print("✅ min-height: 44px encontrado")
        else:
            print("⚠️  min-height: 44px não encontrado")
        
        # Mostrar contexto do seletor .btn-base
        import re
        btn_base_match = re.search(r'\.btn-base\s*\{[^}]*\}', content, re.DOTALL)
        if btn_base_match:
            print(f"\n   Conteúdo do seletor .btn-base:")
            block = btn_base_match.group(0)
            lines = block.split('\n')[:10]
            for line in lines:
                print(f"   {line}")
        
        return has_min_width or has_min_height
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False


async def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTE DIRETO DE CORREÇÃO NO CÓDIGO FONTE")
    print("=" * 60)
    print()
    
    # Verificar se ForgeExperienceDesign está rodando
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/rules")
            if response.status_code != 200:
                print("❌ ForgeExperienceDesign não está acessível")
                return
            print("✅ ForgeExperienceDesign está rodando")
    except Exception as e:
        print(f"❌ ForgeExperienceDesign não está acessível: {e}")
        print("   Inicie o servidor com: cd forge-experience-design && python3 -m backend.main")
        return
    
    # 1. Criar correção de teste
    fix_id = await create_test_fix_directly()
    if not fix_id:
        print("❌ Não foi possível criar correção")
        return
    
    await asyncio.sleep(1)
    
    # 2. Testar preview
    preview = await test_preview(fix_id)
    if not preview:
        print("\n❌ Preview falhou")
        return
    
    await asyncio.sleep(1)
    
    # 3. Testar aplicação
    apply_result = await test_apply_source(fix_id)
    if not apply_result:
        print("\n❌ Aplicação falhou")
        return
    
    # 4. Verificar arquivo
    file_path = apply_result.get("file_path")
    if file_path:
        verify_file_changes(file_path)
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print("✅ Teste completo executado!")
    print(f"   Correção ID: {fix_id}")
    print(f"   Arquivo modificado: {file_path}")
    print(f"   Backup criado: {apply_result.get('backup_path', 'N/A')}")
    print("\n💡 Para ver as mudanças:")
    print(f"   cat {FORGETEST_STUDIO_PATH}/{file_path}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

