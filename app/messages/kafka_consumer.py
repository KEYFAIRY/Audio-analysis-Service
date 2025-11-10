import asyncio
import json
import logging
import time

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition
from app.core.config import settings
from app.application.use_cases.process_and_store_error import ProcessAndStoreErrorUseCase
from app.domain.services.musical_error_service import MusicalErrorService
from app.domain.services.metadata_practice_service import MetadataPracticeService
from app.messages.kafka_message import KafkaMessage
from app.messages.kafka_producer import KafkaProducer
from app.infrastructure.repositories.local_video_repo import LocalVideoRepository
from app.infrastructure.repositories.mysql_musical_error_repo import MySQLMusicalErrorRepository
from app.infrastructure.repositories.mongo_metadata_repo import MongoMetadataRepo
from app.application.dto.practice_data_dto import PracticeDataDTO
from app.infrastructure.monitoring import metrics

logger = logging.getLogger(__name__)

MAX_CONCURRENT_VIDEOS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_VIDEOS)

async def start_kafka_consumer(kafka_producer: KafkaProducer):

    mysql_repo = MySQLMusicalErrorRepository()
    mongo_repo = MongoMetadataRepo()
    video_repo = LocalVideoRepository()

    music_service = MusicalErrorService(mysql_repo, video_repo)
    mongo_service = MetadataPracticeService(mongo_repo)

    use_case = ProcessAndStoreErrorUseCase(
        music_service=music_service,
        mongo_service=mongo_service,
        kafka_producer=kafka_producer,
    )

    consumer = AIOKafkaConsumer(
        settings.KAFKA_INPUT_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER,
        enable_auto_commit=False,
        auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
        group_id=settings.KAFKA_GROUP_ID,
        max_poll_interval_ms=300000,  
        session_timeout_ms=60000,     
        heartbeat_interval_ms=20000   
    )

    await consumer.start()
    tasks = []
    
    try:
        logger.info("Kafka consumer started")

        async def process_message(dto: PracticeDataDTO, tp: TopicPartition, offset: int):
            """Process a single message with concurrency control and instrument metrics"""
            async with semaphore:
                # Get topic label once
                topic_label = getattr(tp, 'topic', settings.KAFKA_INPUT_TOPIC)
                
                # Instrumentation: mark in-progress and start timer
                metrics.videos_in_progress.inc()
                
                try:
                    errors = await use_case.execute(dto)
                    
                    # Record successful processing
                    metrics.kafka_messages_processed.labels(
                        topic=topic_label, 
                        status='success'
                    ).inc()
                    
                    logger.info(
                        f"Successfully processed message - "
                        f"practice_id={dto.practice_id}, "
                        f"offset={offset}, "
                        f"errors_found={len(errors)}, "
                    )
                    return (tp, offset, True)
                    
                except Exception as e:
                    
                    # Record failed processing
                    metrics.kafka_messages_processed.labels(
                        topic=topic_label, 
                        status='error'
                    ).inc()
                    
                    logger.error(
                        f"Failed to process message - "
                        f"practice_id={dto.practice_id}, "
                        f"offset={offset}, "
                        f"error={e}",
                        exc_info=True
                    )
                    return (tp, offset, False)
                    
                finally:
                    metrics.videos_in_progress.dec()

        async for msg in consumer:
            try:
                decoded = msg.value.decode()
                logger.info(
                    f"Received message - "
                    f"offset={msg.offset}, "
                    f"partition={msg.partition}, "
                    f"payload={decoded[:100]}..."
                )

                topic_label = getattr(msg, 'topic', settings.KAFKA_INPUT_TOPIC)
                metrics.kafka_messages_polled.labels(
                    topic=topic_label
                ).inc()
                

                # Parse message
                data = json.loads(decoded)
                kafka_msg = KafkaMessage(**data)

                dto = PracticeDataDTO(
                    uid=kafka_msg.uid,
                    practice_id=kafka_msg.practice_id,
                    date=kafka_msg.date,
                    time=kafka_msg.time,
                    scale=kafka_msg.scale,
                    scale_type=kafka_msg.scale_type,
                    num_postural_errors=0,
                    num_musical_errors=0,
                    duration=kafka_msg.duration,
                    bpm=kafka_msg.bpm,
                    figure=kafka_msg.figure,
                    octaves=kafka_msg.octaves,
                )

                tp = TopicPartition(msg.topic, msg.partition)

                task = asyncio.create_task(process_message(dto, tp, msg.offset))
                tasks.append(task)
                logger.info(
                    f"Scheduled task for offset {msg.offset}. "
                    f"Active tasks: {len([t for t in tasks if not t.done()])}"
                )

                # Check and commit completed tasks
                done_tasks = [t for t in tasks if t.done()]
                if done_tasks:
                    logger.info(f"Found {len(done_tasks)} completed tasks to commit")
                    for task in done_tasks:
                        tp, offset, success = await task
                        if success:
                            await consumer.commit({tp: offset + 1})
                            logger.info(f"Committed offset {offset + 1} for {tp}")
                        else:
                            logger.warning(f"Skipping commit for failed offset {offset}")
                        tasks.remove(task)

            except json.JSONDecodeError as e:
                # Record invalid message
                topic_label = getattr(msg, 'topic', settings.KAFKA_INPUT_TOPIC)
                metrics.kafka_messages_processed.labels(
                    topic=topic_label, 
                    status='invalid'
                ).inc()
                
                logger.error(
                    f"Invalid JSON at offset {msg.offset}: {e}. "
                    f"Raw message: {msg.value}",
                    exc_info=True
                )
                
            except Exception as e:
                logger.error(
                    f"Unexpected error scheduling message at offset {msg.offset}: {e}",
                    exc_info=True
                )

    except asyncio.CancelledError:
        logger.info("Kafka consumer cancelled")
        raise
    except Exception as e:
        logger.error(f"Fatal error in Kafka consumer: {e}", exc_info=True)
        raise
    finally:
        logger.info("Stopping Kafka consumer...")
        await consumer.stop()
        
        # Wait for remaining tasks
        if tasks:
            logger.info(f"Waiting for {len(tasks)} remaining tasks to finish...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"All tasks finished. Results: {len(results)}")
            
        logger.info("Kafka consumer stopped")