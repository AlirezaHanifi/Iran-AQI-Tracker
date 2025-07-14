import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger
from matplotlib.ticker import FixedLocator

from ..config import AppConfig
from ..constants import AQIRanges
from .utils import fa, fa_num, load_fonts


class AQIYearlyTrendVisualizer:
    def __init__(self, config: AppConfig, dpi: int = 400):
        self.config = config
        self.dpi = dpi
        self.regular_font, self.bold_font = load_fonts(
            config.FONT_REGULAR_PATH, config.FONT_BOLD_PATH
        )
        mpl.rcParams["font.family"] = self.regular_font.get_name()
        config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def format_aqi_range_label(self, label: str, start: int, end: int) -> str:
        return fa(f"{label}\n({fa_num(start)}–{fa_num(end)})")

    def draw_aqi_background_ranges(self, ax: plt.Axes) -> None:
        for start, end, color, _ in AQIRanges.RANGES:
            ax.axhspan(start, end, color=color, alpha=0.05, zorder=0)

    def plot_yearly_trend_lines(self, ax: plt.Axes, pivot_df: pd.DataFrame) -> None:
        years = sorted(pivot_df.columns)
        latest_year = max(years)
        n_years = len(years)

        for i, year in enumerate(years):
            color_shade = 0.9 - (i / max(1, (n_years - 1))) * 0.4
            self.add_trend_line(ax, pivot_df, year, latest_year, color_shade)

    def add_trend_line(
        self,
        ax: plt.Axes,
        pivot_df: pd.DataFrame,
        year: str,
        latest_year: str,
        color_shade: float,
    ) -> None:
        is_latest = year == latest_year
        ax.plot(
            pivot_df.index,
            pivot_df[year],
            label=fa_num(year),
            color="red" if is_latest else str(round(color_shade, 2)),
            linewidth=1.5 if is_latest else 1,
            alpha=1.0 if is_latest else 0.9,
            zorder=2,
        )

    def create_aqi_range_legend(self, ax: plt.Axes) -> None:
        for start, end, color, label in AQIRanges.RANGES:
            ax.barh(
                y=(start + end) / 2,
                width=1,
                height=end - start,
                left=0,
                color=color,
                alpha=0.3,
                edgecolor="none",
            )
            ax.text(
                0.5,
                (start + end) / 2,
                self.format_aqi_range_label(label, start, end),
                ha="center",
                va="center",
                fontsize=9,
                fontproperties=self.config.FONT_REGULAR_PATH,
            )

        ax.set_xlim(0, 1)
        ax.set_xticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelleft=False, left=False)

    def generate_yearly_trend_report(
        self,
        df: pd.DataFrame,
        region: str,
        date_col: str = "jalali_date",
        aqi_col: str = "aqi",
    ) -> None:
        logger.debug(f"Starting AQI yearly comparison chart for {region}")

        df = df[df["region_name_en"] == region].copy()
        if df.empty:
            logger.warning(f"No data found for region: {region}")
            return

        pivot_df = self.prepare_trend_data(df, date_col, aqi_col)
        if pivot_df.empty:
            logger.warning("Pivot table is empty")
            return

        fig = self.create_trend_plot(df, pivot_df, date_col)
        self.save_trend_plot(fig, region)

    def prepare_trend_data(
        self, df: pd.DataFrame, date_col: str, aqi_col: str
    ) -> pd.DataFrame:
        df[["year", "month_day"]] = df[date_col].str.split("/", n=1, expand=True)
        return df.pivot(index="month_day", columns="year", values=aqi_col).sort_index()

    def create_trend_plot(
        self, df: pd.DataFrame, pivot_df: pd.DataFrame, date_col: str
    ) -> plt.Figure:
        fig = plt.figure(figsize=(22, 8))
        grid = fig.add_gridspec(1, 12)
        ax_main = fig.add_subplot(grid[0, :11])
        ax_bar = fig.add_subplot(grid[0, 11], sharey=ax_main)

        self.setup_main_plot_area(ax_main, pivot_df, df, date_col)
        self.create_aqi_range_legend(ax_bar)
        fig.subplots_adjust(left=0.03, right=0.99, top=0.92, bottom=0.1, wspace=0.1)

        return fig

    def setup_main_plot_area(
        self, ax: plt.Axes, pivot_df: pd.DataFrame, df: pd.DataFrame, date_col: str
    ) -> None:
        self.draw_aqi_background_ranges(ax)
        self.plot_yearly_trend_lines(ax, pivot_df)
        self.configure_axis_labels(ax, pivot_df, df, date_col)

    def configure_axis_labels(
        self, ax: plt.Axes, pivot_df: pd.DataFrame, df: pd.DataFrame, date_col: str
    ) -> None:
        region_fa: str = df["region_name_fa"].iloc[0]
        min_date, max_date = df[date_col].min(), df[date_col].max()

        self.set_plot_title(ax, region_fa, min_date, max_date)
        self.configure_axis_ticks(ax, pivot_df)

        ax.set_xlabel(
            fa("تاریخ (ماه/روز)"),
            fontsize=12,
            fontproperties=self.config.FONT_REGULAR_PATH,
        )
        ax.set_ylabel(
            fa("شاخص آلودگی هوا"),
            fontsize=12,
            fontproperties=self.config.FONT_REGULAR_PATH,
        )
        ax.set_ylim(bottom=0)
        ax.margins(x=0)
        ax.grid(False)

    def set_plot_title(
        self, ax: plt.Axes, region_fa: str, min_date: str, max_date: str
    ) -> None:
        date_range = f"{fa_num(min_date)} تا {fa_num(max_date)}"
        title = fa(f"مقایسه شاخص آلودگی هوا (AQI) {region_fa}\n") + fa(
            f"بازه زمانی: {date_range}"
        )
        ax.set_title(
            title, fontsize=24, fontproperties=self.config.FONT_BOLD_PATH, pad=10
        )

    def configure_axis_ticks(self, ax: plt.Axes, pivot_df: pd.DataFrame) -> None:
        tick_positions = [
            i for i, val in enumerate(pivot_df.index) if val.endswith("/01")
        ]
        tick_labels = [fa_num(pivot_df.index[i]) for i in tick_positions]

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(
            tick_labels,
            rotation=45,
            ha="right",
            fontsize=9,
            fontproperties=self.config.FONT_REGULAR_PATH,
        )

        for x in tick_positions:
            ax.axvline(x=x, color="lightgray", linestyle="--", linewidth=0.6, zorder=0)

        yticks = ax.get_yticks().tolist()
        ax.yaxis.set_major_locator(FixedLocator(yticks))
        ax.set_yticklabels(
            [fa_num(f"{tick:.0f}") for tick in yticks],
            fontproperties=self.config.FONT_REGULAR_PATH,
        )

    def save_trend_plot(self, fig: plt.Figure, region: str) -> None:
        self.config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = (
            self.config.PLOTS_DIR / f"aqi_yearly_comparison_{region.lower()}.png"
        )
        fig.savefig(output_path, dpi=self.dpi)
        plt.close(fig)
        logger.success(f"Plot saved successfully: {output_path}")


def create_aqi_yearly_trend_report(
    df: pd.DataFrame,
    region: str,
    config: AppConfig,
    dpi: int = 400,
) -> None:
    visualizer = AQIYearlyTrendVisualizer(config, dpi)
    visualizer.generate_yearly_trend_report(df, region)
