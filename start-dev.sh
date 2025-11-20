#!/bin/bash

# Start Script - ForgeExperienceDesign
# Inicia backend e frontend em background

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Arquivo para armazenar PIDs
PIDS_FILE=".pids"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}Parando processos...${NC}"
    if [ -f "$PIDS_FILE" ]; then
        while read pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PIDS_FILE"
        rm -f "$PIDS_FILE"
    fi
    echo -e "${GREEN}Processos parados.${NC}"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

echo "=========================================="
echo "ForgeExperienceDesign - Iniciando Serviços"
echo "=========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Erro: Execute este script na raiz do projeto.${NC}"
    exit 1
fi

# Ativar venv se existir
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Limpar PIDs anteriores
rm -f "$PIDS_FILE"

# Verificar e liberar portas se necessário
check_and_free_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}Porta $port ($name) está em uso. Tentando liberar...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            echo -e "${RED}Erro: Não foi possível liberar a porta $port.${NC}"
            echo "   Execute manualmente: lsof -ti:$port | xargs kill -9"
            exit 1
        else
            echo -e "${GREEN}  ✓ Porta $port liberada${NC}"
        fi
    fi
}

check_and_free_port 8003 "Backend"
check_and_free_port 3001 "Frontend"

# Criar diretório logs se não existir
mkdir -p logs

# Iniciar Backend
echo -e "${YELLOW}Iniciando Backend na porta 8003...${NC}"
python3 backend/main.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" >> "$PIDS_FILE"
echo -e "${GREEN}  ✓ Backend iniciado (PID: $BACKEND_PID)${NC}"

# Aguardar Backend iniciar
sleep 3

# Verificar se Backend está rodando
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo -e "${RED}Erro: Backend não iniciou corretamente. Verifique logs/backend.log${NC}"
    exit 1
fi

# Iniciar Frontend
echo -e "${YELLOW}Iniciando Frontend na porta 3001...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "$FRONTEND_PID" >> "$PIDS_FILE"
echo -e "${GREEN}  ✓ Frontend iniciado (PID: $FRONTEND_PID)${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Serviços iniciados com sucesso!${NC}"
echo "=========================================="
echo ""
echo "URLs:"
echo "  - Frontend: http://localhost:3001"
echo "  - API:      http://localhost:8003"
echo "  - API Docs: http://localhost:8003/api/docs"
echo ""
echo "Logs:"
echo "  - Backend:  logs/backend.log"
echo "  - Frontend: logs/frontend.log"
echo ""
echo "PIDs salvos em: $PIDS_FILE"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para parar os serviços${NC}"
echo ""

# Aguardar indefinidamente
wait

