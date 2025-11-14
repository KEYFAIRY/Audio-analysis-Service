# Audio-analysis-Service
Audio analysis service for detecting music mistakes


## Requirements

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine (Linux).
* `.env` file with environment variables.
* Deployed Kafka broker, MongoDB, and MySQL.

##  Project structure 📁

```bash
📁 AUDIO-ANALYSIS-SERVICE/               # Root directory of the service
│
├── 📁 app/                             # Main application code
│   ├── main.py                         # Entry point: starts Kafka consumer + FastAPI app
│   │
│   ├── 📁 core/                        # Core configurations
│   │   ├── config.py                   # Environment variables (Kafka, DBs, storage path)
│   │   ├── logging.py                  # Logging configuration
│   │   └── exceptions.py               # Custom exception definitions
│   │
│   ├── 📁 domain/                      # Business logic (independent of tech)
│   │   ├── 📁 entities/                # Core entities (e.g., MusicalError)
│   │   ├── 📁 repositories/            # Repository interfaces (e.g., IMongoRepo, IMySQLRepo)
│   │   └── 📁 services/                # Domain services (e.g., MusicalErrorService)
│   │
│   ├── 📁 messages/                    # Comunication with broker
│   │
│   ├── 📁 application/                 # Application layer (use case orchestration)
│   │   ├── 📁 use_cases/               # Use cases (e.g., process_and_store_error.py)
│   │   ├── 📁 dto/                     # Data Transfer Objects
│   │
│   ├── 📁 infrastructure/              # Technical implementations
│   │   ├── 📁 database/                # Database adapters
│   │   │   └── 📁 models/              # Database models
│   │   └── 📁 repositories/            # Concrete repository implementations
│   │
│   └── 📁 shared/                      # Shared utilities
│       ├── constants.py                # Global constants
│       ├── enums.py                    # Enumerations
│       └── utils.py                    # Helper functions
│
├── 📁 tests/                           # Unit tests
│
├── 📁 scripts/                         # Helper scripts
│   └── start.sh                        # Script to start the service
│
├── .env                                # Environment variables (not committed to Git)
├── Dockerfile                          # Instructions to build Docker image
├── docker-compose.yml                  # Runs only this service container
├── requirements.txt                    # Python dependencies
└── README.md                           # Project documentation

```


## Steps to run the project

### Create .env file, for example:

Edit the .example.env file with yout actual variables, and rename it to .env


### Run the service

```bash
docker compose up --build -d
```

### Check running containers in Docker Desktop / Docker Engine

```bash
docker ps
```

### Test the service

Developing unit tests

### Stop the service

```bash
docker compose down
```


## Steps to run unit tests

### Create virtual environment :

```bash
python -m venv venv
```

### Activate virtual environment:

```bash
.\venv\Scripts\Activate.ps1
```

### Install pip:

```bash
python -m pip install --upgrade pip
```

### Install required test tools and project requirements:

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Check installation:

```bash
pytest --version
```

### Execute test:

```bash
python -m pytest tests/[name.py] -v --tb=short
```