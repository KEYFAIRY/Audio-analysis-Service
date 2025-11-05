from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import time
from functools import wraps
import os

# http_requests_total = Counter(
#     'audio_http_requests_total',
#     'Total HTTP requests',
#     ['method', 'endpoint', 'status']
# )

# http_request_duration_seconds = Histogram(
#     'audio_http_request_duration_seconds',
#     'HTTP request duration',
#     ['method', 'endpoint'],
#     buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
# )


kafka_messages_processed = Counter(
    'audio_kafka_messages_commited_total',
    'Total Kafka messages processed',
    ['topic', 'status']
)

kafka_messages_polled = Counter(
    'audio_kafka_messages_polled_total',
    'Total messages polled from Kafka (before processing)',
    ['topic']
)

videos_in_progress = Gauge(
    'audios_in_progress',
    'Videos currently being processed'
)


video_processing_duration = Histogram(
    'audio_processing_duration_seconds',
    'Time to process a video',
    buckets=(2, 4, 6, 8, 10, 15, 20, 25)
)

db_operations = Counter(
    'audio_db_operations_total',
    'Total database operations performed by the audio analysis service',
    ['operation', 'database', 'status'] 
)

db_operation_duration = Histogram(
    'audio_db_operation_duration_seconds',
    'Duration of database write/read operations',
    ['operation', 'database'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

def start_metrics_server(port: int | None = None):
    port = port or int(os.getenv('PROMETHEUS_PORT', '8015'))
    start_http_server(port)
