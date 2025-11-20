# Explicação do Fluxo - ForgeExperienceDesign

## ❓ Onde as Correções São Aplicadas?

### Situação Atual

**As correções são APENAS salvas no banco de dados do ForgeExperienceDesign.**

Elas NÃO são aplicadas automaticamente em lugar nenhum!

### Onde DEVERIAM ser aplicadas

1. **Interface do ForgeTest Studio** (frontend React)
   - Quando o usuário está usando o ForgeTest Studio
   - Correções devem ser injetadas via CSS na página

2. **Qualquer aplicação web** que:
   - Injetar o script `fix-injector.js`
   - Ou consumir a API do ForgeExperienceDesign

## 🔄 Fluxo Completo (Como Deveria Funcionar)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ForgeTest Studio (Aplicação Web)                        │
│    - Usuário interage com a interface                      │
│    - Problemas de UI são detectados (botão pequeno, etc.)  │
└────────────────────┬───────────────────────────────────────┘
                     │
                     │ Envia logs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ForgeLogs (Armazenamento)                                │
│    - Recebe e armazena logs de problemas de UI              │
│    - API: POST /api/logs                                    │
└────────────────────┬───────────────────────────────────────┘
                     │
                     │ Consulta logs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ForgeExperienceDesign (Análise e Geração)                │
│    - Consulta ForgeLogs periodicamente                      │
│    - Analisa problemas detectados                           │
│    - Gera correções CSS usando regras ou IA                │
│    - Salva correções no banco SQLite                        │
│    - API: GET /api/fixes/generate                           │
└────────────────────┬───────────────────────────────────────┘
                     │
                     │ Correções disponíveis via API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FixInjector (Aplicação das Correções)                    │
│    - Script JavaScript injetado no ForgeTest Studio         │
│    - Busca correções da API do ForgeExperienceDesign        │
│    - Aplica CSS automaticamente na página                   │
│    - Correções visíveis imediatamente                       │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Como Testar Automaticamente

### Método 1: Página HTML de Teste

1. **Criar página HTML** com problemas conhecidos:
   - Botão pequeno (20x20px)
   - Texto com contraste baixo
   - Elemento com dimensões zero

2. **Injetar FixInjector**:
   ```html
   <script src="http://localhost:3001/static/fix-injector.js"></script>
   ```

3. **Verificar automaticamente**:
   - JavaScript verifica se CSS foi aplicado
   - Compara dimensões antes/depois
   - Valida se problemas foram corrigidos

### Método 2: Teste com Playwright

```python
from playwright.sync_api import sync_playwright

def test_fixes():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Abrir página de teste
        page.goto("http://localhost:3001/test/test_page.html")
        
        # Aguardar correções serem aplicadas
        page.wait_for_timeout(10000)
        
        # Verificar se botão foi corrigido
        button = page.locator(".small-button")
        style = button.evaluate("el => window.getComputedStyle(el)")
        
        assert int(style['minWidth'].replace('px', '')) >= 44
        assert int(style['minHeight'].replace('px', '')) >= 44
        
        browser.close()
```

### Método 3: Teste de API

```python
# 1. Criar problemas no ForgeLogs
# 2. Gerar correções
# 3. Verificar se correções existem no banco
# 4. Aplicar correção via API
# 5. Verificar se status mudou para "applied"
```

## 📍 Onde Aplicar Correções no ForgeTest Studio

### Opção 1: Injetar Script no HTML

No `index.html` do ForgeTest Studio:

```html
<!-- No final do <body> -->
<script src="http://localhost:3001/static/fix-injector.js"></script>
<script>
  window.FORGE_EXPERIENCE_DESIGN_CONFIG = {
    apiUrl: 'http://localhost:8003',
    applicationId: 'forgetest-studio',
    autoApply: true,
    pollInterval: 30000
  };
</script>
```

### Opção 2: Integrar no React

No componente principal do ForgeTest Studio:

```tsx
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Carregar FixInjector
    const script = document.createElement('script');
    script.src = 'http://localhost:3001/static/fix-injector.js';
    script.onload = () => {
      if (window.forgeExperienceDesign) {
        window.forgeExperienceDesign.start();
      }
    };
    document.body.appendChild(script);
  }, []);
  
  // ... resto do componente
}
```

### Opção 3: Via API do ForgeTest Studio

Criar endpoint no backend do ForgeTest Studio:

```python
@router.get("/api/fixes/active")
async def get_active_fixes():
    # Buscar correções do ForgeExperienceDesign
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8003/api/fixes",
            params={"status": "applied", "application_id": "forgetest-studio"}
        )
        fixes = response.json()
    
    # Retornar CSS para injetar
    css = generate_css_from_fixes(fixes)
    return {"css": css}
```

E no frontend:

```tsx
useEffect(() => {
  fetch('/api/fixes/active')
    .then(res => res.json())
    .then(data => {
      const style = document.createElement('style');
      style.textContent = data.css;
      document.head.appendChild(style);
    });
}, []);
```

## ✅ Resumo

**Problema atual:**
- Correções são geradas e salvas
- Mas NÃO são aplicadas automaticamente

**Solução:**
- Injetar `fix-injector.js` no ForgeTest Studio
- Ou criar integração via API
- Ou usar WebSocket para push automático

**Como testar:**
- Página HTML de teste com problemas conhecidos
- Script JavaScript que valida correções
- Ou Playwright para teste automatizado completo

