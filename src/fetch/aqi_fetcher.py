import asyncio
from typing import Any, Dict

import backoff
import httpx
import pandas as pd
from loguru import logger

from ..config import AppConfig
from .utils import build_output_path, generate_jalali_dates, process_dataframe


class AQIDataFetcher:
    def __init__(self, config: AppConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENT)
        self.transport = httpx.AsyncHTTPTransport(retries=2)

    async def fetch_data(
        self, session: httpx.AsyncClient, payload: Dict[str, str]
    ) -> Dict[str, Any]:
        @backoff.on_exception(
            backoff.expo,
            (httpx.RequestError, httpx.HTTPStatusError),
            max_tries=5,
            jitter=None,
        )
        async def _fetch():
            response = await session.post(
                self.config.BASE_URL, data=payload, timeout=10.0
            )
            response.raise_for_status()
            return response.json()

        return await _fetch()

    async def fetch_and_save(
        self,
        session: httpx.AsyncClient,
        date: str,
        time: str = "11:00",
        region_type: int = 1,
    ) -> None:
        output_file = build_output_path(self.config.OUTPUT_DIR, date)
        if output_file.exists():
            logger.info(f"Skipping {date} (already exists)")
            return

        payload = {"Date": f"{date} {time}", "type": str(region_type)}

        try:
            async with self.semaphore:
                logger.debug(f"Fetching {date}")
                json_data = await self.fetch_data(session, payload)
        except Exception as e:
            logger.error(f"Failed for {date}: {e}")
            return

        if (
            not isinstance(json_data, dict)
            or "Data" not in json_data
            or not json_data["Data"]
        ):
            logger.warning(f"No data for {date}")
            return

        df = pd.DataFrame(json_data["Data"])
        df["requested_date"] = date
        df = process_dataframe(df)
        df.to_parquet(output_file, index=False, compression="snappy")
        logger.success(f"Saved {len(df)} records to {output_file}")

    async def fetch_all(self) -> None:
        dates = generate_jalali_dates(self.config.START_DATE, self.config.END_DATE)
        self.config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(
            headers=self.config.HEADERS,
            cookies=self.config.COOKIES,
            transport=self.transport,
        ) as client:
            tasks = [self.fetch_and_save(client, date) for date in dates]
            await asyncio.gather(*tasks)


async def fetch_aqi_data(config: AppConfig) -> None:
    fetcher = AQIDataFetcher(config)
    await fetcher.fetch_all()
