# Quick Start - ForgeExperienceDesign

## Instalação Rápida

```bash
# 1. Instalar dependências
./setup.sh

# 2. Configurar (opcional)
cp .env.example .env
# Edite .env e adicione OPENAI_API_KEY se quiser usar IA

# 3. Iniciar
./start-dev.sh
```

## Acessar

- **Dashboard**: http://localhost:3001
- **API Docs**: http://localhost:8003/api/docs

## Testar

### 1. Gerar Correções

```bash
curl http://localhost:8003/api/fixes/generate?application_id=forgetest-studio
```

### 2. Listar Correções

```bash
curl http://localhost:8003/api/fixes
```

### 3. Aplicar Correção

```bash
curl -X POST http://localhost:8003/api/fixes/{fix_id}/apply
```

## Integrar no ForgeTest Studio

Adicione no HTML do ForgeTest Studio:

```html
<script src="http://localhost:3001/static/fix-injector.js"></script>
```

As correções serão aplicadas automaticamente!

## Troubleshooting

### Erro: "Module not found"
```bash
# Reinstalar dependências
pip install -r requirements.txt
cd frontend && npm install
```

### Erro: "Database not initialized"
```bash
python3 backend/scripts/init_db.py
```

### Erro: "ForgeLogs connection failed"
- Verifique se ForgeLogs está rodando em http://localhost:8002
- Configure `FORGELOGS_URL` no `.env`

