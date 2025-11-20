# ForgeExperienceDesign

Ferramenta focada em UI/UX que consome logs do ForgeLogs e corrige pró-ativamente a interface, aplicando melhorias automáticas.

## Características

- **Análise de Logs**: Consulta logs de UI/UX do ForgeLogs
- **Geração de Correções**: Regras automáticas e IA para gerar correções
- **Aplicação Automática**: Aplica correções via CSS/JavaScript
- **Validação**: Valida se correções resolveram problemas
- **Rollback**: Reverte correções se necessário
- **Dashboard**: Visualização de problemas e correções aplicadas
- **18 Regras de Correção**: Acessibilidade, responsividade, visual
- **IA Integrada**: Gera correções inteligentes usando LLM (opcional)

## Instalação

```bash
# Instalar dependências
./setup.sh

# Iniciar servidor (backend + frontend)
./start-dev.sh
```

## Configuração

Copie `.env.example` para `.env` e configure:

```env
# ForgeLogs
FORGELOGS_URL=http://localhost:8002
APPLICATION_ID=forgetest-studio

# OpenAI (opcional, para IA)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Monitor
MONITOR_INTERVAL=60
```

## Uso

### Dashboard Web

Acesse http://localhost:3001 para:
- Visualizar problemas detectados
- Ver correções geradas
- Aplicar/reverter correções
- Gerenciar regras

### API

Documentação: http://localhost:8003/api/docs

Endpoints principais:
- `GET /api/fixes/generate` - Gera correções
- `GET /api/fixes` - Lista correções
- `POST /api/fixes/{id}/apply` - Aplica correção
- `POST /api/fixes/{id}/rollback` - Reverte correção

### Integração em Outras Aplicações

Para aplicar correções automaticamente no ForgeTest Studio ou outras aplicações:

```html
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

Ou use programaticamente:

```javascript
import { createFixInjector } from './fix-injector';

const injector = createFixInjector({
  apiUrl: 'http://localhost:8003',
  applicationId: 'forgetest-studio',
  autoApply: true,
  pollInterval: 30000
});

injector.start();
```

## Regras de Correção

### Acessibilidade
- Contraste de texto
- Indicadores de foco
- Tamanho de texto
- Aria-labels

### Responsividade
- Largura fixa → responsiva
- Overflow em mobile
- Viewport

### Visual
- Espaçamento
- Alinhamento
- Tipografia
- Imagens quebradas
- Estilo de botões
- Z-index

## Arquitetura

```
ForgeTest Studio (aplicação)
    ↓ (envia logs)
ForgeLogs (armazena logs)
    ↓ (consulta logs)
ForgeExperienceDesign (analisa e aplica correções)
    ↓ (aplica correções)
ForgeTest Studio (interface corrigida)
```

## Tecnologias

- **Backend**: Python 3.11+, FastAPI, SQLite
- **Frontend**: React, TypeScript, Tailwind CSS
- **IA**: OpenAI (opcional)
- **Validação**: axe-core, stylelint

## Documentação

- [README Frontend](README_FRONTEND.md)
- [Resumo da Implementação](IMPLEMENTATION_SUMMARY.md)
- [Integração](docs/integration.md)

## Licença

MIT
