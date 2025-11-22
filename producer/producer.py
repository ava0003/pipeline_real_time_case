import time
import random
import logging
import orjson
from confluent_kafka import Producer

from constants import (
    EVENTS_TOPIC,
    KAFKA_BOOTSTRAP,
    EVENT_TYPES,
    TENANTS,
    PRODUCER_SEND_INTERVAL,
)
from models.event import Event


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | event_producer | %(message)s",
)
logger = logging.getLogger("event_producer")


def delivery_report(err, msg):
    if err is not None:
        logger.error("Delivery failed: %s", err)
    else:
        logger.info(
            "Event delivered | topic=%s partition=%s offset=%s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def flush_producer(producer):
    producer.flush()


def build_random_event() -> dict:
    tenant = random.choice(TENANTS)
    event_type = random.choice(EVENT_TYPES)

    payload = {
        "session_id": f"sess-{random.randint(1000, 9999)}",
        "path": "/home",
        "browser": "chrome",
    }

    event = Event(
        tenant_id=tenant,
        event_type=event_type,
        timestamp=time.time(),
        payload=payload,
    )

    return event.model_dump()


def main():
    config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "linger.ms": 10,
    }

    producer = Producer(config)

    logger.info("Starting event producer...")

    while True:
        event_data = build_random_event()
        event_bytes = orjson.dumps(event_data)

        producer.produce(
            EVENTS_TOPIC,
            value=event_bytes,
            on_delivery=delivery_report,
        )

        logger.info("Sending event | valid=%s | event_type=%s",
                    True, event_data.get("event_type"))

        producer.poll(0)
        time.sleep(PRODUCER_SEND_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Producer stopped by user.")
