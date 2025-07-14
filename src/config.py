import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final, List

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    INPUT_DIR: Final[Path]
    OUTPUT_DIR: Final[Path]
    PLOTS_DIR: Final[Path]
    START_DATE: Final[str]
    END_DATE: Final[str]
    MAX_CONCURRENT: Final[int]
    PLOT_REGIONS: Final[List[str]]
    FONT_REGULAR_PATH: Final[Path]
    FONT_BOLD_PATH: Final[Path]
    HEADERS: Final[dict]
    COOKIES: Final[dict]
    BASE_URL: Final[str]

    @classmethod
    def load(cls) -> "AppConfig":
        load_dotenv()
        base_dir = Path(__file__).parent.parent

        return cls(
            INPUT_DIR=base_dir / os.getenv("INPUT_DIR"),
            OUTPUT_DIR=base_dir / os.getenv("OUTPUT_DIR"),
            PLOTS_DIR=base_dir / os.getenv("PLOTS_DIR"),
            START_DATE=os.getenv("START_DATE", "1402/01/01"),
            END_DATE=os.getenv("END_DATE", "1402/12/29"),
            MAX_CONCURRENT=int(os.getenv("MAX_CONCURRENT", "10")),
            PLOT_REGIONS=os.getenv("PLOT_REGIONS", "Tehran").split(","),
            FONT_REGULAR_PATH=base_dir / os.getenv("FONT_REGULAR_PATH"),
            FONT_BOLD_PATH=base_dir / os.getenv("FONT_BOLD_PATH"),
            HEADERS={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://aqms.doe.ir",
                "Referer": "https://aqms.doe.ir/Home/AQI",
                "User-Agent": "Mozilla/5.0",
                "X-Requested-With": "XMLHttpRequest",
            },
            COOKIES={
                "_ga": os.getenv("COOKIES_GA", ""),
                "_gid": os.getenv("COOKIES_GID", ""),
                "ASP.NET_SessionId": os.getenv("COOKIES_SESSIONID", ""),
                "_gat": os.getenv("COOKIES_GAT", ""),
            },
            BASE_URL="https://aqms.doe.ir/Home/GetAQIDataByRegion/",
        )
