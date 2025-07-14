from typing import Dict, Final, List, Tuple


class AQIRanges:
    RANGES: List[Tuple[int, int, str, str]] = [
        (0, 50, "#00e400", "پاک"),
        (51, 100, "#ffff00", "قابل قبول"),
        (101, 150, "#ff7e00", "ناسالم برای گروه‌های حساس"),
        (151, 200, "#ff0000", "ناسالم"),
        (201, 300, "#99004c", "بسیار ناسالم"),
        (301, 500, "#7e0023", "خطرناک"),
    ]


class AQIColumns:
    MAPPING: Final[Dict[str, str]] = {
        "Id": "id",
        "StateId": "state_id",
        "RegionId": "region_id",
        "CO": "co",
        "O3": "o3",
        "NO2": "no2",
        "SO2": "so2",
        "PM10": "pm10",
        "PM2_5": "pm2_5",
        "AQI": "aqi",
        "Pollutant": "main_pollutant",
        "StateName_Fa": "state_name_fa",
        "StateName_En": "state_name_en",
        "Region_Fa": "region_name_fa",
        "Region_En": "region_name_en",
        "RegionLatitude": "region_latitude",
        "RegionLongitude": "region_longitude",
        "CreateDate": "create_date",
        "ModifyDate": "modify_date",
        "Date": "date",
        "requested_date": "jalali_date",
    }
