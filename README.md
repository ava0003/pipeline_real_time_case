# Real-Time Event Processing Pipeline 

This project implements a real-time streaming pipeline able to:

- Ingest live events from multiple tenants
- Validate schemas using Pydantic
- Process hopping windows with Faust
- Detect and compute session duration
- Store results in Parquet for analytics
- Handle invalid events through a Dead Letter Queue (DLQ)

The entire system runs locally using Kafka in KRaft mode.

## 1. Getting the Project

Clone the repository:

```bash
git clone https://github.com/ava0003/pipeline_real_time_case.git
cd <folder>
```

Create and activate a virtual environment:

**Mac Os**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate.bat
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. How to launch it
### Single-command execution (macOS & Windows)

To make the project easy to run locally, the entire stackcan be launched with one command, depending on your operating system.

This allows you to start the full real-time pipeline without opening multiple terminals manually.

### ***a. macOS***
- Use the provided shell script:
```
./run_all.sh
```

***Make sure it's executable:***
```
chmod +x run_all.sh
```
### ***b. Windows***

Use the batch script:
```
run_windows.bat
```
In both cases, the script will automatically:

- Start Kafka through Docker Compose

- Open a new terminal running the Faust consumer

- Open another terminal running the event producer

- Activate the virtual environment for each process

**Notes**

- Kafka must not already be running (otherwise stop previous containers with docker compose down)
- Both scripts assume your virtual environment is named venv at the root of the project 

### Step by step execution 

### I. Starting Kafka

```bash
docker compose up -d
```

Check Kafka:

```bash
docker ps
```
You should find something like this: 

![img.png](img.png)

### II. Launch the Consumer

```bash
source venv/bin/activate
python -m consumer.consumer_faust worker -l info
```

### III. Launch the Producer

```bash
source venv/bin/activate
python -m producer.producer
```

### IV. Find outputs

Stored under `/storage/`

### V. Reading the Outputs

```python
import pandas as pd
df = pd.read_parquet("storage/rolling_window_results.parquet")
print(df.head())
```

### VI. Cleaning Kafka

```bash
docker compose down -v
```

---

## 3. Stream processing explanation

### 1. Rolling Window
`storage/rolling_window_results.parquet`

The goal is to track how many times a specific event type occurs for each tenant within a recent time window.

#### How it works

Every incoming event updates a Faust hopping window with:

**a window size (e.g., 10 seconds)**

**a window step (e.g., 2 seconds)**

This means each event belongs to overlapping windows, giving a smooth real-time trend rather than "hard resets."

At each event arrival, the consumer writes a Parquet snapshot containing:

- tenant  
- event_type  
- occurrences (current window count)  
- window_size  

### 2. Session Duration
`storage/session_stats.parquet`

Some events include a session_id.
To estimate session duration, we track:

when a session starts (session_start)
when it ends (session_end)

#### How it works

- When a session_start arrives we store the timestamp in a Faust table **(session_starts[session_id])**

- When the corresponding session_end arrives we retrieve the start time and compute:
```
duration = end_timestamp − start_timestamp
```
- Update a cumulative statistics table (per tenant):
  - total_duration 
  - count (number of completed sessions)

- Compute average session duration:
```
avg_duration = total_duration / count
```
- Write to Parquet:
  - tenant
  - last_session_duration
  - avg_session_duration
  - session_count

-----


## 4. Local Architecture Overview

The system is composed of:

### Producer
Generates live events (valid + invalid) for multiple tenants.

### Kafka (KRaft mode)
Message broker handling ingestion and replay.

### Faust Consumer
- Consume events in streaming.
- Validate schema
- Send invalid events to DLQ
- Update rolling windows
- Compute session statistics
- Store analytics in Parquet

### Parquet Storage
Two analytical outputs:
- Rolling window event counts
- Session durations and aggregated metrics
