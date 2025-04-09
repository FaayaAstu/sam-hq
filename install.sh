apt-get update && \
    apt-get install -y --no-install-recommends git wget build-essential libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

update-alternatives --install /usr/bin/python python /usr/bin/python3 1

pip install -r requirements.txt

pip install -e .
export PYTHONPATH=$(pwd)

echo "Creating pretrained checkpoint directory..."
mkdir -p pretrained_checkpoint

echo "Downloading models using downloader script..."
python models/model_downloader.py
echo "Model check/download complete."
