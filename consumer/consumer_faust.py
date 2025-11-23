import logging
import faust
import orjson

from constants import (
    KAFKA_BOOTSTRAP,
    EVENTS_TOPIC,
    DLQ_TOPIC,
    WINDOW_SIZE_SECONDS,
    WINDOW_STEP_SECONDS,
    WINDOW_EXPIRES_SECONDS,
)
from models.event import Event
from consumer.processors.rolling_window import process_rolling_window
from consumer.processors.session_duration import process_session

# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("faust_consumer")

# Faust
# App

app = faust.App(
    "events_stream_app",
    broker=f"kafka://{KAFKA_BOOTSTRAP}",
    value_serializer="raw",
)

# Tables

event_counts = app.Table(
    "event_counts",
    default=int,
    partitions=1,
).hopping(
    size=WINDOW_SIZE_SECONDS,
    step=WINDOW_STEP_SECONDS,
    expires=WINDOW_EXPIRES_SECONDS,
)

session_starts = app.Table(
    "session_starts",
    default=float,
    partitions=1,
)

session_stats = app.Table(
    "session_stats",
    default=lambda: {"total_duration": 0.0, "count": 0},
    partitions=1,
)

# Kafkq
# Topics

events_topic = app.topic(EVENTS_TOPIC)
dlq_topic = app.topic(DLQ_TOPIC)



@app.agent(events_topic)
async def process_events(stream):
    async for msg in stream:

        # Deserialize
        try:
            data = orjson.loads(msg)
        except Exception as e:
            logger.error("Error during deserialize process for message: %s | raw=%s", e, msg)
            continue

        logger.info("Raw event: %s", data)

        # Check schema
        try:
            event = Event(**data)
            logger.info(
                "Event | tenant=%s | type=%s | ts=%s",
                event.tenant_id,
                event.event_type,
                event.timestamp,
            )
        except Exception as e:
            logger.warning("Schema validation error: %s", e)
            logger.warning("Sending to DLQ: %s", data)
            await dlq_topic.send(value=msg)
            continue


        process_rolling_window(event, event_counts, WINDOW_SIZE_SECONDS)
        process_session(event, session_starts, session_stats)


if __name__ == "__main__":
    app.main()
