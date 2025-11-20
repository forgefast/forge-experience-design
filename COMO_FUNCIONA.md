# Como Funciona - ForgeExperienceDesign

## 🎯 Objetivo

Corrigir problemas de UI/UX **automaticamente** na interface do ForgeTest Studio (ou qualquer aplicação web).

## 🔄 Fluxo Completo

### 1. Detecção (ForgeTest Studio)
```
Usuário usa ForgeTest Studio
  ↓
Problemas detectados (botão pequeno, contraste baixo, etc.)
  ↓
Logs enviados para ForgeLogs
```

### 2. Armazenamento (ForgeLogs)
```
ForgeLogs recebe logs
  ↓
Armazena no banco de dados
  ↓
Disponível via API: GET /api/logs
```

### 3. Análise (ForgeExperienceDesign Backend)
```
ForgeExperienceDesign consulta ForgeLogs
  ↓
Analisa problemas
  ↓
Gera correções CSS usando regras ou IA
  ↓
Salva no banco SQLite
  ↓
Disponível via API: GET /api/fixes/generate
```

### 4. Aplicação (ForgeTest Studio Frontend - NO NAVEGADOR)
```
useForgeExperienceDesign() hook ativo
  ↓
Polling a cada 30s: GET /api/fixes/generate
  ↓
Recebe correções
  ↓
FixApplier aplica CSS:
  - Cria <style id="forge-experience-design-fixes">
  - Adiciona CSS: selector { property: value !important; }
  ↓
CSS aplicado IMEDIATAMENTE na página
  ↓
Correções visíveis SEM recarregar
```

## 📍 Onde as Correções São Aplicadas?

### Resposta: NO NAVEGADOR

**Tecnicamente:**
- JavaScript cria elemento `<style>` no `<head>`
- CSS é injetado dinamicamente
- Aplicado apenas na página atual
- Temporário (só enquanto página está aberta)

**Visualmente:**
- Você vê as mudanças na interface do ForgeTest Studio
- Botões ficam maiores
- Texto fica mais legível
- Elementos quebrados são corrigidos

## 🧪 Como Testar Automaticamente

### Teste com Playwright (100% Automatizado)

```bash
pip install playwright httpx
playwright install chromium
python3 test/test_with_playwright.py
```

**Faz tudo sozinho:**
1. Cria problemas
2. Gera correções
3. Abre navegador
4. Aplica correções
5. Valida resultado
6. Retorna sucesso/falha

**ZERO ajuda manual necessária!**

### O que o teste valida:

- ✅ Botão pequeno (20x20px) → Fica >= 44x44px
- ✅ Elemento zero → Ganha dimensões
- ✅ CSS injetado no `<head>`
- ✅ Correções visíveis na página

## 🔍 Verificação Manual

### No ForgeTest Studio

1. Abrir: http://localhost:3000
2. DevTools (F12) → Console
3. Procurar: "FixInjector iniciado" ou "ForgeExperienceDesign"
4. Elements → `<head>` → Procurar: `<style id="forge-experience-design-fixes">`

**Se o `<style>` existir = Correções estão sendo aplicadas!**

### Verificar CSS

```javascript
// Console do navegador
document.getElementById('forge-experience-design-fixes')?.textContent
```

## ⚠️ Problema Atual

**ForgeTest Studio tem integração, mas pode estar desabilitada:**

```tsx
// App.tsx
enabled: import.meta.env.DEV  // ← Só em desenvolvimento!
```

**Verificar se está ativo no console do navegador.**

## ✅ Resumo

- **Onde:** No navegador, via JavaScript
- **Como:** CSS injetado dinamicamente
- **Quando:** Automaticamente (polling a cada 30s)
- **Como testar:** Script Playwright automatizado
- **Status:** Funciona, mas precisa estar habilitado

