# Integração com ForgeTest Studio

Este documento descreve como integrar ForgeExperienceDesign com ForgeTest Studio via ForgeLogs.

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

## Configuração

### 1. Configurar ForgeLogs

Certifique-se de que ForgeLogs está rodando e recebendo logs do ForgeTest Studio.

### 2. Configurar ForgeExperienceDesign

Criar arquivo `.env`:

```
FORGELOGS_URL=http://localhost:8002
APPLICATION_ID=forgetest-studio
```

### 3. Iniciar ForgeExperienceDesign

```bash
cd forge-experience-design
./setup.sh
./start.sh
```

## Funcionamento

ForgeExperienceDesign:

1. Consulta logs de UI/UX do ForgeLogs periodicamente
2. Identifica problemas recorrentes
3. Gera correções baseadas em regras
4. Aplica correções automaticamente via CSS
5. Valida se correções resolveram problemas
6. Faz rollback se necessário

## Correções Aplicadas

As correções são aplicadas via CSS injetado na página. Exemplos:

- **Botões pequenos**: Aumenta tamanho mínimo para 44x44px
- **Dimensões zero**: Adiciona min-width/min-height
- **Overflow**: Adiciona overflow: hidden
- **Sobreposição**: Ajusta z-index

## Dashboard

Acesse o dashboard do ForgeExperienceDesign para:

- Visualizar problemas detectados
- Ver correções aplicadas
- Gerenciar regras de correção
- Ver métricas de melhoria

