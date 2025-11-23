
# Architecture & Failure Scenarios

## 1. Architecture Schema

This project follows a simple real-time architecture:  
events are generated, validated, processed, aggregated, and finally stored in an analytical format.

Here’s a clear explanation of what each component does:

### **Python (Producer)**
The producer simulates a realistic stream of events coming from different tenants.  
It generates valid traffic (views, clicks, session events) as well as malformed or incomplete messages.

### **Kafka (KRaft)**
Kafka acts as the central event hub.  
Every event from every tenant goes through Kafka first.  
Kafka ensures that:
- no events are lost,
- events arrive in order,
- consumers can read at their own pace,
- and events can be replayed if needed.

### **Faust (Stream Processor)**
Faust is the engine that processes events in real time.  
It allows me to build the logic entirely in Python, which keeps development fast and accessible.  
With Faust I can:
- maintain state between events (rolling counters, session timers),
- define time windows without manual implementation,
- handle multiple tenants naturally,
- and process events asynchronously as soon as they arrive.

### **Pydantic (Validation Layer)**
Pydantic ensures that every event has the expected structure.  
If an event is missing fields or contains wrong types, it is rejected and sent to the DLQ (Dead Letter Queue).  
This keeps the main pipeline clean and prevents corrupted data from polluting the system.

### **Parquet (Storage Layer)**
The processed data is stored in **Parquet**, which is much more suitable for analytics than JSON.


### **Docker**
Docker ensures that the entire environment—Kafka, the producer, and the consumer—can be started locally with a single command.  
It removes installation friction and guarantees everyone runs the pipeline the same way, independent of system configuration.  


                     ┌─────────────────────┐
                     │     Event Producer  │
                     │  (Python + orjson)  │
                     │ Simulates tenants,  │
                     │ valid & invalid evts│
                     └───────────┬─────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │        Kafka Broker    │
                    │      (KRaft mode)      │
                    │  - Topic: events       │
                    │  - Topic: events_dlq   │
                    └───────────┬────────────┘
                                │
                                ▼
                 ┌────────────────────────────┐
                 │        Faust Consumer      │
                 │  - Schema validation       │
                 │  - DLQ routing             │
                 │  - Rolling windows         │
                 │  - Session durations       │
                 │  - Persist to Parquet      │
                 └──────────────┬─────────────┘
                                │
                                ▼
                ┌────────────────────────────────┐
                │      Local Parquet Storage     │
                └────────────────────────────────┘
---

## 2. Justification of Technology Choices

### **Kafka (KRaft)**
Kafka provides a stable backbone for the event stream.  
It handles bursts of traffic, guarantees delivery, and keeps the producer and consumer fully decoupled.  
Using the KRaft configuration simplifies local deployments and avoids the overhead of managing ZooKeeper.


### **Faust**
Faust allows me to write real-time streaming logic directly in Python, which makes the implementation approachable and fast to iterate on.  
It gives me built-in windowing, state tables, async processing, and a clean way to express streaming logic without complexity.  
For a problem like this, Faust strikes the right balance between power and simplicity.

### **Pydantic**
Pydantic ensures the pipeline only processes well‑formed events.  
It prevents malformed data from breaking the consumer and keeps the system robust.  
Pydantic also makes DLQ routing straightforward.

### **Parquet**
Parquet is the right format for the type of analytics this pipeline produces.  
It’s compact, fast to query, and compatible with analytical engines like DuckDB or Spark.  
While JSON might be enough for a tiny use case, Parquet is the format you would choose in production.

### **Docker**
Docker provides a consistent environment and lets the entire system run with predictable behavior.  
It avoids configuration errors, makes setup trivial, and ensures the same behaviour across machines.

---

## 3. Limitations
### Single-broker Kafka

For simplicity, the architecture uses a single Kafka broker.
This is not fault-tolerant and would not support production availability requirements.
A real deployment would require a multi-broker cluster with replication.

### In-memory Faust tables

Faust tables are stored in memory, meaning:
- No persistence across restarts

- Limited scalability


### Simplified session logic

Sessions are inferred only from session_start and session_end events.
A real system may require timeout-based session detection and cross-event correlation.

### Parquet append for each event

Writing to Parquet on every event is acceptable for a use case, but inefficient at scale.
A production pipeline would batch writes or stream into a warehouse (e.g., BigQuery, Snowflake).



# 4. Failure Scenarios & Mitigation

### Invalid events in the system**

In a real system, some events will  be incomplete, incorrectly formatted, or missing important fields such as the tenant ID or the timestamp.
If these events were processed directly, they could break the consumer logic or corrupt the analytical results (for example by creating bad session durations or invalid window counts).

**Mitigation:** 
**Schema validation + Dead Letter Queue (DLQ)**

Before any event is processed, it goes through a strict Pydantic validation step.
If the schema is invalid, the event is immediately redirected to a dedicated DLQ Kafka topic instead of entering the main pipeline.
This keeps the system healthy: valid events continue to be processed normally, while invalid ones are isolated for inspection without interrupting the flow.



### Kafka becomes temporarily unavailable

In a real environment, the Kafka broker may restart or become unreachable for a few seconds.
When this happens, the consumer cannot read new events and the producer cannot deliver them.
In this case, the pipeline would stop and incoming events could be lost.

**Mitigation:** 
**Automatic retries + Kafka’s persisted log**

Both the producer and the Faust consumer automatically retry connecting to Kafka when it becomes available again.
Since Kafka stores all events durably in its internal log, no messages are lost during the outage.
Once the connection is restored, the consumer continues processing from where it left off, and the system returns to normal without manual intervention.