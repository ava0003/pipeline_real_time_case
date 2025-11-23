from pathlib import Path
from typing import Any, Dict
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def save_parquet(data: Dict[str, Any], filename: str ):
    path = Path("storage")
    path.mkdir(exist_ok=True)

    file_path = path / filename
    new_df = pd.DataFrame([data])

    if not file_path.exists():
        table = pa.Table.from_pandas(new_df)
        pq.write_table(table, file_path)
        return

    # If existing : Read
    try:
        existing_table = pq.read_table(file_path)
        existing_df = existing_table.to_pandas()
    except Exception as e:
        print("Error opening parquet, recreating:", e)
        table = pa.Table.from_pandas(new_df)
        pq.write_table(table, file_path)
        return

    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    # Overwrite
    combined_table = pa.Table.from_pandas(combined_df)
    pq.write_table(combined_table, file_path)

