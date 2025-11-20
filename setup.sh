#!/bin/bash

# Setup Script - ForgeExperienceDesign
# Instala dependências e configura ambiente

set -e

echo "=========================================="
echo "ForgeExperienceDesign - Setup"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.11+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar virtual environment se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando virtual environment..."
    python3 -m venv venv
fi

# Ativar venv
echo "🔧 Ativando virtual environment..."
source venv/bin/activate

# Atualizar pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Instalar dependências do frontend
if [ -d "frontend" ]; then
    echo "📦 Instalando dependências do frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p data logs

# Copiar .env.example para .env se não existir
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Criando arquivo .env a partir de .env.example..."
        cp .env.example .env
        echo "⚠️  Configure o arquivo .env com suas chaves de API"
    fi
fi

# Inicializar banco de dados
echo "🗄️  Inicializando banco de dados..."
python3 -m backend.scripts.init_db || python3 backend/scripts/init_db.py || echo "⚠️  Banco será inicializado na primeira execução"

echo ""
echo "=========================================="
echo "✅ Setup concluído!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Configure o arquivo .env (opcional, para IA)"
echo "2. Execute ./start-dev.sh para iniciar"
echo ""
