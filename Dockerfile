# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Instalar dependencias del sistema para compilar mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
	ffmpeg \
	libsndfile1 \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)" && \
    python -c "from basic_pitch import ICASSP_2022_MODEL_PATH; print('Model path:', ICASSP_2022_MODEL_PATH)" && \
    python -c "import os; os.environ['TF_CPP_MIN_LOG_LEVEL']='2'; from basic_pitch.inference import predict; print('basic_pitch loaded')"

# Copiar todo el código fuente
COPY . .

# Comando por defecto al iniciar el contenedor
CMD ["python", "-m", "app.main"]