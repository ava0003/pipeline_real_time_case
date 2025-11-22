from consumer.storage import save_parquet
from constants import ROLLING_WINDOW_RESULTS_PARQUET

def process_rolling_window(event, event_counts, window_size):

    event_counts[event.tenant_id, event.event_type] += 1

    current_count = int(event_counts[event.tenant_id, event.event_type].now())

    snapshot = {
        "tenant": event.tenant_id,
        "event_type": event.event_type,
        "occurrences": current_count,
        "window_size_seconds": window_size,
    }

    save_parquet(snapshot, ROLLING_WINDOW_RESULTS_PARQUET)
