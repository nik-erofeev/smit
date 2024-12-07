import asyncio

from app.kafka.producer import KafkaProducer


async def test_kafka_producer() -> None:
    producer = KafkaProducer(
        bootstrap_servers="localhost:29092",
        default_topic="default",
    )
    await producer.start()

    test_message = {"test": "message"}

    await producer.send_message(test_message, "123")

    await producer.stop()


if __name__ == "__main__":
    asyncio.run(test_kafka_producer())
