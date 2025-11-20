#!/bin/bash

set -e

# Ativar virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Iniciar servidor
echo "Starting ForgeExperienceDesign backend server..."
python backend/main.py

