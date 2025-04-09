#!/bin/bash

# Install system dependencies
apt-get update && \
    apt-get install -y --no-install-recommends git wget build-essential libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- Conda Environment Setup ---
echo "Creating Conda environment 'sam-hq' with Python 3.8..."
conda create --name sam-hq python=3.10 -y

echo "Activating Conda environment 'sam-hq'..."
CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
conda activate sam-hq

echo "Installing dependencies from requirements.txt (including PyTorch/GPU libraries)..."
python -m pip install -r requirements.txt

echo "Installing segment-anything-hq package..."
python -m pip install -e .
export PYTHONPATH=$(pwd)

echo "Creating pretrained checkpoint directory..."
mkdir -p pretrained_checkpoint

echo "Downloading models using downloader script..."
python models/model_downloader.py
echo "Model check/download complete."

# conda deactivate # Optional: uncomment if you want to deactivate at the end

echo "Setup complete. To use, activate the environment: conda activate sam-hq"
