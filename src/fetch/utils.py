import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

import jdatetime
import pandas as pd

from ..constants import AQIColumns


def convert_ms_date(ms_date_str: str) -> str | None:
    match = re.search(r"/Date\((\d+)\)/", str(ms_date_str))
    if not match:
        return None
    return datetime.fromtimestamp(
        int(match.group(1)) / 1000, tz=timezone.utc
    ).isoformat()


def generate_jalali_dates(start: str, end: str) -> List[str]:
    start_j = jdatetime.datetime.strptime(start, "%Y/%m/%d")
    end_j = jdatetime.datetime.strptime(end, "%Y/%m/%d")
    delta = (end_j.togregorian() - start_j.togregorian()).days
    return [
        (start_j + timedelta(days=i)).strftime("%Y/%m/%d") for i in range(delta + 1)
    ]


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    available_columns = [col for col in AQIColumns.MAPPING]
    date_columns = ["CreateDate", "ModifyDate", "Date"]

    df = df.loc[:, available_columns].copy()
    for col in date_columns:
        df.loc[:, col] = df[col].apply(convert_ms_date)

    df = df.rename(columns=AQIColumns.MAPPING)
    return df


def build_output_path(base_dir: Path, date: str) -> Path:
    year, month, _ = date.split("/")
    subdir = base_dir / f"year={year}" / f"month={month}"
    subdir.mkdir(parents=True, exist_ok=True)
    return subdir / f"aqi_{date.replace('/', '_')}.parquet"
