#!/usr/bin/env python3
"""
Script de teste de integração ForgeExperienceDesign + ForgeLogs + ForgeTest Studio
"""

import asyncio
import httpx
import json
from datetime import datetime

FORGELOGS_URL = "http://localhost:8002"
FORGE_EXPERIENCE_DESIGN_URL = "http://localhost:8003"
APPLICATION_ID = "forgetest-studio"


async def test_integration():
    """Testa integração completa."""
    print("=" * 60)
    print("Teste de Integração - ForgeExperienceDesign")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Verificar ForgeLogs
        print("1. Verificando ForgeLogs...")
        try:
            response = await client.get(f"{FORGELOGS_URL}/api/health")
            if response.status_code == 200:
                print("   ✅ ForgeLogs está rodando")
            else:
                print(f"   ⚠️  ForgeLogs respondeu com status {response.status_code}")
        except Exception as e:
            print(f"   ❌ ForgeLogs não está acessível: {e}")
            print("   💡 Inicie o ForgeLogs: cd forgelogs && ./start.sh")
            return
        
        # 2. Criar logs de teste
        print("\n2. Criando logs de problemas de UI...")
        test_issues = [
            {
                "application_id": APPLICATION_ID,
                "log_type": "ui_issue",
                "severity": "high",
                "category": "ui",
                "data": {
                    "type": "small_touch_target",
                    "message": "Botão de login muito pequeno (20x20px)",
                    "element": "button.login-btn",
                    "details": {"width": 20, "height": 20, "selector": "button.login-btn"}
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            {
                "application_id": APPLICATION_ID,
                "log_type": "ui_issue",
                "severity": "high",
                "category": "ui",
                "data": {
                    "type": "accessibility_low_contrast",
                    "message": "Contraste de texto baixo na descrição",
                    "element": "p.description",
                    "details": {"color": "#cccccc", "background": "#ffffff", "ratio": 1.2}
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            {
                "application_id": APPLICATION_ID,
                "log_type": "ui_issue",
                "severity": "medium",
                "category": "ui",
                "data": {
                    "type": "zero_dimensions",
                    "message": "Elemento com dimensões zero detectado",
                    "element": "div.container",
                    "details": {"width": 0, "height": 0}
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        ]
        
        created_logs = 0
        for issue in test_issues:
            try:
                response = await client.post(
                    f"{FORGELOGS_URL}/api/logs",
                    json=issue
                )
                if response.status_code in [200, 201]:
                    created_logs += 1
                    print(f"   ✅ Log criado: {issue['data']['type']}")
                else:
                    print(f"   ⚠️  Erro ao criar log: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        print(f"\n   📊 Total de logs criados: {created_logs}/{len(test_issues)}")
        
        # 3. Verificar se ForgeExperienceDesign consegue ler
        print("\n3. Verificando ForgeExperienceDesign...")
        try:
            response = await client.get(f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/rules")
            if response.status_code == 200:
                rules = response.json()
                print(f"   ✅ ForgeExperienceDesign está rodando ({len(rules)} regras)")
            else:
                print(f"   ⚠️  Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ ForgeExperienceDesign não acessível: {e}")
            return
        
        # 4. Gerar correções
        print("\n4. Gerando correções a partir dos logs...")
        try:
            response = await client.get(
                f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes/generate",
                params={"application_id": APPLICATION_ID, "limit": 10}
            )
            if response.status_code == 200:
                fixes = response.json()
                print(f"   ✅ {len(fixes)} correções geradas!")
                for i, fix in enumerate(fixes[:3], 1):
                    print(f"   {i}. {fix.get('target_element')} - {len(fix.get('changes', []))} alterações")
            else:
                print(f"   ⚠️  Erro: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Erro ao gerar correções: {e}")
        
        # 5. Listar correções salvas
        print("\n5. Listando correções salvas...")
        try:
            response = await client.get(f"{FORGE_EXPERIENCE_DESIGN_URL}/api/fixes")
            if response.status_code == 200:
                fixes = response.json()
                print(f"   ✅ {len(fixes)} correções no banco de dados")
            else:
                print(f"   ⚠️  Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Teste de integração concluído!")
        print("=" * 60)
        print("\nPróximos passos:")
        print("1. Acesse http://localhost:3001 para ver o dashboard")
        print("2. Clique em 'Atualizar' para ver as correções geradas")
        print("3. Aplique as correções para testar")


if __name__ == "__main__":
    asyncio.run(test_integration())

