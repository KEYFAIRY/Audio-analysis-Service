from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, start_http_server
import time
from functools import wraps
import os

# metrics
http_requests_total = Counter(
    'audio_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'audio_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
)

kafka_messages_processed = Counter(
    'audio_kafka_messages_processed_total',
    'Total Kafka messages processed',
    ['topic', 'status']
)

videos_in_progress = Gauge(
    'audios_in_progress',
    'Videos currently being processed'
)

video_processing_duration = Histogram(
    'audio_processing_duration_seconds',
    'Time to process a video',
    buckets=(2, 4, 6, 8, 10, 15)
)

def start_metrics_server(port: int | None = None):
    port = port or int(os.getenv('PROMETHEUS_PORT', '8015'))
    start_http_server(port)
