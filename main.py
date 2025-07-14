import asyncio
from pathlib import Path

from loguru import logger

from src.config import AppConfig
from src.fetch.aqi_fetcher import fetch_aqi_data
from src.process.data_processor import process_aqi_data
from src.visualize.yearly_report import create_aqi_yearly_trend_report


def setup_logging() -> None:
    log_path = Path("log")
    log_path.mkdir(exist_ok=True)
    logger.add(
        log_path / "aqi_pipeline.log",
        rotation="10 MB",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


async def main() -> None:
    setup_logging()
    config = AppConfig.load()
    logger.warning(
        # "!!!",
        # config,
        str(config.FONT_REGULAR_PATH),
        str(config.FONT_BOLD_PATH),
    )
    # Step 1: Fetch Data (async)
    logger.info("Starting data fetch...")
    await fetch_aqi_data(config)

    # Step 2: Process Data
    logger.info("Reading and processing data...")
    df = process_aqi_data(config.INPUT_DIR)
    if df.empty:
        logger.error("No data to process")
        return

    # Step 3: Create Visualizations
    logger.info("Creating visualizations...")
    for region in config.PLOT_REGIONS:
        create_aqi_yearly_trend_report(df, region=region, config=config)

    logger.info("Pipeline completed")


if __name__ == "__main__":
    asyncio.run(main())
