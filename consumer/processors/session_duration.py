from consumer.storage import save_parquet
from constants import SESSION_DURATION_PARQUET

def process_session(event, session_starts, session_stats):
    session_id = event.payload.get("session_id")

    if not session_id:
        return

    if event.event_type == "session_start":
        session_starts[session_id] = event.timestamp
        return

    if event.event_type == "session_end":
        start_ts = session_starts.get(session_id)
        if not start_ts:
            return

        duration = event.timestamp - start_ts

        stats = session_stats[event.tenant_id]
        stats["total_duration"] += duration
        stats["count"] += 1
        session_stats[event.tenant_id] = stats

        avg_duration = stats["total_duration"] / stats["count"]

        snapshot = {
            "tenant": event.tenant_id,
            "last_session_duration": duration,
            "avg_session_duration": avg_duration,
            "session_count": stats["count"],
        }

        save_parquet(snapshot, SESSION_DURATION_PARQUET)

        del session_starts[session_id]
