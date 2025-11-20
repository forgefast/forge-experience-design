# Como Testar ForgeExperienceDesign

## 🧪 Teste Automatizado (Recomendado)

### Pré-requisitos
```bash
pip install playwright httpx
playwright install chromium
```

### Executar
```bash
cd forge-experience-design
source venv/bin/activate
python3 test/test_with_playwright.py
```

**O que faz:**
- ✅ Cria problemas automaticamente
- ✅ Gera correções automaticamente  
- ✅ Abre navegador automaticamente
- ✅ Valida se correções funcionaram
- ✅ Retorna sucesso/falha

**NÃO PRECISA DE SUA AJUDA!**

## 📄 Teste Manual com Página HTML

1. Abrir: http://localhost:3001/test/test_page.html
2. Aguardar 10-15 segundos
3. Verificar status na página (✅ ou ❌)

## 🔍 Verificar no ForgeTest Studio

1. Abrir: http://localhost:3000
2. DevTools (F12) → Console
3. Procurar mensagens do FixInjector
4. Elements → `<head>` → Procurar `<style id="forge-experience-design-fixes">`

Se o `<style>` existir, correções estão sendo aplicadas!
