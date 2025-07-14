from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import matplotlib as mpl

from .utils import load_fonts

@dataclass
class PlotConfig:
    font_regular_path: Path
    font_bold_path: Path
    output_dir: Path
    dpi: int = 400

    def __post_init__(self):
        self.regular_font, self.bold_font = load_fonts(
            self.font_regular_path, self.font_bold_path
        )
        mpl.rcParams["font.family"] = self.regular_font.get_name()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_output_path(self, filename: str) -> Path:
        return self.output_dir / filename


class AQIRanges:
    RANGES: List[Tuple[int, int, str, str]] = [
        (0, 50, "#00e400", "پاک"),
        (51, 100, "#ffff00", "قابل قبول"),
        (101, 150, "#ff7e00", "ناسالم برای گروه‌های حساس"),
        (151, 200, "#ff0000", "ناسالم"),
        (201, 300, "#99004c", "بسیار ناسالم"),
        (301, 500, "#7e0023", "خطرناک"),
    ]
