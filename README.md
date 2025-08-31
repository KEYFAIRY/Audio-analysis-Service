# Audio-analysis-Service
Audio analysis service for detecting music mistakes


## Requirements

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine (Linux).
* `.env` file with environment variables.
* Deployed Kafka broker, MongoDB, and MySQL.

##  Project structure 📁

```bash
📁 VIDEO-WORKER-SERVICE/                # Root directory of the worker service
│
├── 📁 app/                             # Main application code
│   ├── main.py                         # Entry point: starts Kafka consumer loop
│   │
│   ├── 📁 core/                        # Core configurations
│   │   ├── config.py                   # Environment variables (Kafka, DBs, storage path)
│   │   ├── logging.py                  # Logging configuration
│   │   └── exceptions.py               # Custom exception definitions
│   │
│   ├── 📁 domain/                      # Business logic (independent of tech)
│   │   ├── 📁 entities/                # Core entities (e.g. Video, ProcessingResult)
│   │   ├── 📁 repositories/            # Repository interfaces (IMongoRepo, IMySQLRepo)
│   │   └── 📁 services/                # Domain services (e.g. VideoProcessor, transformations)
│   │
│   ├── 📁 application/                 # Application layer (use case orchestration)
│   │   ├── 📁 use_cases/               # Use cases (e.g. process_video_message.py)
│   │   ├── 📁 dto/                     # Data Transfer Objects
│   │   └── 📁 interfaces/              # Application-level interfaces
│   │
│   ├── 📁 infrastructure/              # Technical implementations
│   │   ├── 📁 kafka/                   # Kafka consumer and producer
│   │   ├── 📁 database/                # Database adapters
│   │   │   ├── mongo_repository.py     # MongoDB repository implementation
│   │   │   └── mysql_repository.py     # MySQL repository implementation
│   │   ├── 📁 storage/                 # Local file system access (read videos)
│   │   └── 📁 repositories/            # Concrete repo implementations
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

Developing kafdrop to manually test

### Stop the service

```bash
docker compose down
```