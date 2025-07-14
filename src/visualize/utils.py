from pathlib import Path
from typing import Tuple, Union

from arabic_reshaper import reshape
from bidi.algorithm import get_display
from matplotlib.font_manager import FontProperties
from persiantools import digits


def fa(text: str) -> str:
    return get_display(reshape(text))


def fa_num(text: Union[int, str]) -> str:
    return digits.en_to_fa(str(text))


def load_fonts(
    regular_path: Path, bold_path: Path
) -> Tuple[FontProperties, FontProperties]:
    return FontProperties(fname=regular_path), FontProperties(fname=bold_path)
