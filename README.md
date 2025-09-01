# Audio-analysis-Service
Audio analysis service for detecting music mistakes


## Requirements

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine (Linux).
* `.env` file with environment variables.
* Deployed Kafka broker, MongoDB, and MySQL.

##  Project structure 📁

```bash
📁 AUDIO-ANALYSIS-SERVICE/                # Root directory of the worker service
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
│   │   ├── 📁 entities/                # Core entities (e.g., Video, ProcessingResult)
│   │   ├── 📁 repositories/            # Repository interfaces (IMongoRepo, IMySQLRepo)
│   │   └── 📁 services/                # Domain services (e.g., VideoProcessor, transformations)
│   │
│   ├── 📁 application/                 # Application layer (use case orchestration)
│   │   ├── 📁 use_cases/               # Use cases (e.g., process_video_message.py)
│   │   ├── 📁 dto/                     # Data Transfer Objects
│   │   └── 📁 interfaces/              # Application-level interfaces
│   │
│   ├── 📁 infrastructure/              # Technical implementations
│   │   ├── 📁 kafka/                   # Kafka consumer and producer
│   │   ├── 📁 database/                # Database adapters
│   │   │   └── 📁 models/              # Database models
│   │   ├── 📁 storage/                 # Local file system access (read videos)
│   │   └── 📁 repositories/            # Concrete repository implementations
│   │
│   ├── 📁 presentation/               # Presentation layer (API and external interfaces)
│   │   ├── 📁 api/                    # REST API endpoints
│   │   │   ├── 📁 v1/                 # API v1 endpoints
│   │   │   └── dependencies.py        # Shared dependencies (DI)
│   │   ├── 📁 schemas/                # Pydantic schemas (e.g., error_schema.py)
│   │   └── 📁 middleware/             # Custom middleware (CORS, logging, error handling)
│   │
│   └── 📁 shared/                      # Shared utilities
│       ├── constants.py                # Global constants
│       ├── enums.py                    # Enumerations
│       └── utils.py                    # Helper functions
│
├── 📁 workers/                         # Worker processes
│   └── video_consumer.py               # Kafka consumer loop that triggers use cases
│
├── 📁 tests/                           # Unit tests
│   ├── 📁 domain/
│   ├── 📁 application/
│   └── 📁 infrastructure/
│
├── 📁 scripts/                         # Helper scripts
│   └── run_worker.sh                   # Script to start the worker
│
├── .env                                # Environment variables (not committed to Git)
├── Dockerfile                          # Instructions to build Docker image
├── docker-compose.yml                  # Runs only this service container
├── requirements.txt                    # Python dependencies
└── README.md                            # Project documentation

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

Developing kafdrop to manually test

### Stop the service

```bash
docker compose down
```