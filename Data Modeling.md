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

| Column               | Type    | Description                          |
|----------------------|---------|--------------------------------------|
| date                 | DATE    | Partition key                        |
| tenant_id            | STRING  | Client identifier                     |
| event_type           | STRING  |                                      |
| total_events         | INTEGER | Events count for that day             |
| error_events         | INTEGER | Error count                           |
| avg_session_duration | FLOAT   | Average session duration              |
| unique_sessions      | INTEGER |                               |

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
```sql
SELECT 
    date,
    tenant_id,
    SUM(total_events) AS events
FROM fact_events_daily
GROUP BY 1,2
ORDER BY date;
```

---

**Weekly Error Rate**
```sql
SELECT
    DATE_TRUNC('week', date) AS week,
    tenant_id,
    SUM(error_events) / SUM(total_events) AS error_rate
FROM fact_events_daily
GROUP BY 1,2;
```
---
