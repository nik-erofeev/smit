import json
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from loguru import logger

from app.settings import APP_CONFIG


class KafkaProducer:
    def __init__(self, bootstrap_servers: str, default_topic: str = "default_actions"):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None
        self.admin_client: AIOKafkaAdminClient | None = None
        self.batch_size = APP_CONFIG.kafka.batch_size
        self.batch: list[bytes] = []
        self.default_topic = default_topic

    async def start(self) -> None:
        self.admin_client = AIOKafkaAdminClient(
            bootstrap_servers=self.bootstrap_servers,
        )
        await self.admin_client.start()

        topics = await self.admin_client.list_topics()
        if self.default_topic not in topics:
            new_topic = NewTopic(
                name=self.default_topic,
                num_partitions=1,
                replication_factor=1,
            )
            await self.admin_client.create_topics([new_topic])
            logger.info(f"Topic '{self.default_topic}' created.")

        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()
        logger.info("Kafka producer connected to %s", self.bootstrap_servers)

    async def stop(self) -> None:
        if self.batch:
            await self.send_batch(self.default_topic)
        if self.producer is not None:
            await self.producer.stop()
            logger.info("Kafka producer disconnected")
        else:
            logger.warning("Producer was not started, cannot stop.")

    async def send_message(
        self,
        message: dict[str, Any],
        topic: str | None = None,
    ) -> None:
        if topic is None:
            topic = self.default_topic
        self.batch.append(json.dumps(message).encode("utf-8"))

        if len(self.batch) >= self.batch_size:
            await self.send_batch(topic)

    async def send_batch(self, topic: str) -> None:
        if self.batch:
            if self.producer is None:
                raise RuntimeError(
                    "Producer is not initialized. Call start() before sending messages",
                )

            for message in self.batch:
                await self.producer.send_and_wait(topic, message)
            logger.info(
                f"Batch of {len(self.batch)} messages sent to Kafka topic '{topic}'",
            )
            self.batch.clear()
