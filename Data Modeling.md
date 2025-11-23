#  Data Modeling (Bonus)

## Real-Time Dashboards 

This layer stores near-real-time aggregates over rolling or hopping windows.

### **Table: realtime_event_metrics**

| Column            | Type      | Description                                   |
|------------------|-----------|-----------------------------------------------|
| tenant_id        | STRING    | Client identifier                              |
| event_type       | STRING    | click, view, error, etc.                      |
| window_start_ts  | TIMESTAMP | Start of the rolling window                    |
| window_end_ts    | TIMESTAMP | End of the rolling window                      |
| occurrences      | INTEGER   | Number of events in the window                 |
| last_event_ts    | TIMESTAMP | Timestamp of the last event received           |

Stored in memory or fast local storage (ex: Faust tables or DuckDB live)

---

### Example Real-Time Indicators

**Events per Tenant (last X seconds)**

| Tenant    | Events (X s) |
|-----------|--------------|
| tenant_a  | 124          |
| tenant_b  | 87           |
| tenant_c  | 66           |

---

**Event Type Distribution (last x minutes)**

- 60% click  
- 32% view  
- 8% error  

---

#  Historical Analytics

Historical dashboards require long retention and aggregated metrics.

### **Table: fact_events_daily**
| Column        | Type    | Description                         |
|---------------|---------|-------------------------------------|
| date          | DATE    | Partition key                       |
| tenant_id     | STRING  |                                     |
| event_type    | STRING  |                                     |
| total_events  | INTEGER | Number of events that day           |
| error_events  | INTEGER | Number of error events              |

### **Table: fact_session_daily**

| Column                | Type    | Description                               |
|-----------------------|---------|-------------------------------------------|
| date                  | DATE    | Partition key                             |
| tenant_id             | STRING  |                                           |
| total_sessions_unique | INTEGER | Number of completed sessions              |
| avg_session_duration  | FLOAT   | Average duration of sessions for that day |
| max_session_duration  | FLOAT   | Longest session                           |
| min_session_duration  | FLOAT   | Shortest session                          |

For this use case, the historical storage layer would be implemented using local Parquet files.
This keeps the entire solution fully runnable on a personal machine without external services. 
Parquet works well for a self-contained environment because it is lightweight, columnar, and easy to query locally using engines like Pandas or DuckDB.

However, in a real production environment, long-term analytical storage 
would not rely on raw Parquet files. 
Instead, a scalable data warehouse or lakehouse would be used to support higher volumes, stronger guarantees, and richer query capabilities.
Technologies such as Snowflake, BigQuery or Databricks provide ACID transactions, automatic partitioning, schema evolution and other advantages.

---

### Example Historical Indicators
**Daily Events per Tenant**

It highlights usage volume, peak activity periods, and long-term growth trends.
It allows to identify days with unusual spikes or drops in traffic.
```sql
SELECT 
    date,
    tenant_id,
    SUM(total_events) AS daily_events
FROM fact_events_daily
GROUP BY date, tenant_id
ORDER BY date, tenant_id;
```

---

**Weekly Error Rate**

The weekly error rate measures the proportion of failing events over an entire week.
It is especially useful for detecting recurring problems and comparing reliability across tenants.

```sql
SELECT
    DATE_TRUNC('week', date) AS week,
    SUM(error_events) * 1.0 / NULLIF(SUM(total_events), 0) AS weekly_error_rate
FROM fact_events_daily
GROUP BY week
ORDER BY week;
```
---

**Average Number of Events per Session per Tenant per Day**

This metric combines event volume with session volume to measure how much activity happens inside each session.
It reflects user engagement and the volume of interactions.
It helps distinguish between tenants with many light sessions versus fewer but highly engaged sessions.
```sql
SELECT
    e.date,
    e.tenant_id,
    SUM(e.total_events) * 1.0 / NULLIF(SUM(s.total_sessions), 0) 
        AS avg_events_per_session
FROM fact_events_daily e
JOIN fact_session_daily s
    ON e.date = s.date
   AND e.tenant_id = s.tenant_id
GROUP BY e.date, e.tenant_id
ORDER BY e.date, e.tenant_id;
```
---
