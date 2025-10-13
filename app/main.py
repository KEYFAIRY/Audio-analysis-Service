import logging
import asyncio
import numpy as np
import soundfile as sf
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.infrastructure.audio.model_manager import ModelManager
from app.infrastructure.database import mongo_connection, mysql_connection
from app.infrastructure.kafka.kafka_consumer import start_kafka_consumer
from app.infrastructure.kafka.kafka_producer import KafkaProducer
from contextlib import asynccontextmanager



# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")

    # ---- DB COnnections ----
    try:
        # MySQL
        mysql_connection.mysql_connection.init_engine()
        logger.info("MySQL connection initialized")

        # Mongo
        mongo_connection.mongo_connection.connect()
        logger.info("MongoDB connection initialized")

    except Exception as e:
        logger.exception("Error initializing database connections")
        raise

    # ---- Load Audio Models ----
    try:
        logger.info("Pre-loading audio analysis models...")
        predict, model_path = ModelManager.get_basic_pitch()
        # Load model weights by running predict on dummy audio

        # Write a short silent WAV file
        dummy_path = "dummy.wav"
        sf.write(dummy_path, np.zeros(48000), 48000)  # 1 second of silence at 48kHz

        # Actually load the model weights
        predict(dummy_path, model_or_model_path=model_path)
        logger.info("Audio models loaded successfully")
    except Exception as e:
        logger.exception("Error loading audio models")
        raise

    # ---- Kafka ----
    producer = KafkaProducer(bootstrap_servers=settings.KAFKA_BROKER)
    await producer.start()

    loop = asyncio.get_event_loop()
    consumer_task = loop.create_task(start_kafka_consumer(producer))

    yield

    # ---- Shutdown ----
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Kafka consumer stopped")

    await producer.stop()
    logger.info("Kafka producer stopped")

    # Close DBs
    await mysql_connection.mysql_connection.close_connections()
    await mongo_connection.mongo_connection.close()

    logger.info("Database connections closed")


async def main():
    async with lifespan():
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped manually (Ctrl+C)")