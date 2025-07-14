from pathlib import Path
from typing import Union

import pandas as pd
from loguru import logger


def _clean_pollutant_names(df: pd.DataFrame) -> pd.DataFrame:
    pollutant_mapping = {
        "PM 2.5": "PM2.5",
        "PM 10": "PM10",
        "PM2.5": "PM2.5",
        "PM10": "PM10",
        "SO2": "SO2",
        "NO2": "NO2",
        "O3": "O3",
        "CO": "CO",
    }

    df["main_pollutant"] = (
        df["main_pollutant"]
        .fillna("")
        .str.strip()
        .replace(pollutant_mapping)
        .astype("category")
    )

    return df


def _add_pollutant_indicators(df: pd.DataFrame) -> pd.DataFrame:
    indicators = {
        "PM2.5": ["PM2.5"],
        "PM10": ["PM10"],
        "SO2": ["SO2"],
        "NO2": ["NO2"],
        "O3": ["O3"],
        "CO": ["CO"],
    }

    for pollutant, variants in indicators.items():
        col_name = f"has_{pollutant.lower().replace('.', '_')}"
        df[col_name] = df["main_pollutant"].isin(variants)

    return df


def _add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df["possible_fuel_oil_usage"] = ((df["so2"] > 75) & df["has_so2"]) | (
        (df["pm2_5"] > 100) & df["has_pm2_5"]
    )

    df["aqi_level"] = pd.cut(
        df["aqi"],
        bins=[0, 50, 100, 150, 200, 300, 500],
        labels=[
            "Good",
            "Moderate",
            "Unhealthy for Sensitive",
            "Unhealthy",
            "Very Unhealthy",
            "Hazardous",
        ],
        include_lowest=True,
    )

    return df


def _load_and_combine_data(base_dir: Union[str, Path]) -> pd.DataFrame:
    base_path = Path(base_dir).resolve()
    logger.info(f"Loading data from: {base_path}")

    parquet_files = list(base_path.rglob("*.parquet"))
    if not parquet_files:
        logger.warning(f"No parquet files found in: {base_path}")
        return pd.DataFrame()

    try:
        df = pd.read_parquet(parquet_files)
        logger.success(f"Loaded {len(df):,} records from {len(parquet_files)} files")
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        return pd.DataFrame()


def process_aqi_data(input_dir: Path) -> pd.DataFrame:
    logger.info("Starting data processing")

    df = _load_and_combine_data(input_dir)
    if df.empty:
        return df

    df = (
        df.pipe(_clean_pollutant_names)
        .pipe(_add_pollutant_indicators)
        .pipe(_add_derived_features)
    )

    logger.success("Data processing completed")
    return df
