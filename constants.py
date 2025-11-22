
# Producer send
PRODUCER_SEND_INTERVAL = 1

# Tenant list
TENANTS = ["tenant_a", "tenant_b", "tenant_c"]

# Valid event types
EVENT_TYPES = [
    "click",
    "view",
    "error",
    "session_start",
    "session_end",
]

# KAFKA
KAFKA_BOOTSTRAP = "localhost:9092"
EVENTS_TOPIC = "events"
DLQ_TOPIC = "events_dlq"

#  FAUST
#  ROLLING WINDOW
WINDOW_SIZE_SECONDS = 20.0
WINDOW_STEP_SECONDS = 1.0
WINDOW_EXPIRES_SECONDS = 30.0

# STORAGE
ROLLING_WINDOW_RESULTS_PARQUET = "rolling_window_results.parquet"
SESSION_DURATION_PARQUET = "session_duration.parquet"


