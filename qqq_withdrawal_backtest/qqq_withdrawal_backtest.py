#!/usr/bin/env python3
"""QQQ 시작연도별 10년 원리금 인출 백테스트.

기본 조건
---------
* 초기 준비금: 1억원
* 월 인출액: 매월 말 100만원
* 투자 시작연도: 2002년~2016년
* 투자 기간: 120개월(10년)
* QQQ 수익률: Yahoo Finance 수정주가 사용(배당 및 주식분할 반영)
* 원/달러 환율: 미국 연준 FRED DEXKOUS 사용(1달러당 원화 환율)
* 제외 항목: 세금, 환전·거래 수수료, 물가상승률

초기 준비금을 시작 시점의 환율로 달러 환산하여 QQQ에 투자한다.
이후 매월 말 당시의 환율을 적용해 원화 100만원에 해당하는 달러 금액을
투자 잔액에서 인출한다.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, Patch
import pandas as pd
import yfinance as yf


# =============================================================================
# 1. 데이터 수집
# =============================================================================


def download_monthly_series(
    ticker: str,
    first_start_year: int,
    last_start_year: int,
    years: int,
    price_column: str = "Adj Close",
) -> pd.Series:
    """Yahoo Finance에서 전년도 12월을 포함한 월말 가격을 내려받는다."""
    start = f"{first_start_year - 1}-12-01"
    # yfinance의 종료일은 포함되지 않으므로 필요한 기간보다 넉넉하게 설정한다.
    end = f"{last_start_year + years + 1}-01-01"
    raw = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        actions=False,
    )
    if raw is None or raw.empty:
        raise RuntimeError(f"{ticker} 가격 데이터를 내려받지 못했습니다.")

    series = raw[price_column]
    if isinstance(series, pd.DataFrame):
        frame = cast(pd.DataFrame, series)
        series = frame[ticker] if ticker in frame.columns else frame.iloc[:, 0]
    series = series.dropna().astype(float)
    monthly = series.resample("ME").last()
    monthly.name = ticker
    return monthly


def download_monthly_usdkrw(
    first_start_year: int, last_start_year: int, years: int
) -> pd.Series:
    """미국 연준 FRED에서 월말 원/달러 환율을 내려받는다."""
    start = f"{first_start_year - 1}-12-01"
    end = f"{last_start_year + years}-12-31"
    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id=DEXKOUS&cosd={start}&coed={end}"
    )
    raw = pd.read_csv(url)
    date_column = "observation_date" if "observation_date" in raw.columns else "DATE"
    raw[date_column] = pd.to_datetime(raw[date_column])
    values = pd.to_numeric(raw["DEXKOUS"], errors="coerce")
    daily = pd.Series(values.to_numpy(), index=raw[date_column], name="usdkrw").dropna()
    return daily.resample("ME").last()


def load_market_data(
    ticker: str, first_start_year: int, last_start_year: int, years: int
) -> tuple[pd.Series, pd.Series]:
    """백테스트에 필요한 QQQ 수정주가와 원/달러 환율을 준비한다."""
    prices = download_monthly_series(
        ticker, first_start_year, last_start_year, years, "Adj Close"
    )
    fx_rates = download_monthly_usdkrw(first_start_year, last_start_year, years)
    return prices, fx_rates


# =============================================================================
# 2. 백테스트 계산
# =============================================================================


def simulate_one_start(
    monthly_prices: pd.Series,
    monthly_fx: pd.Series,
    start_year: int,
    initial_reserve: float,
    monthly_withdrawal: float,
    years: int,
) -> tuple[dict, pd.DataFrame]:
    """월 수익률을 적용한 뒤 매월 말 정해진 원화 금액을 인출한다."""
    first_month = pd.Timestamp(start_year, 1, 31)
    previous_month = first_month - pd.offsets.MonthEnd(1)
    final_month = first_month + pd.offsets.MonthEnd(years * 12 - 1)

    required = monthly_prices.loc[previous_month:final_month]
    required_fx = monthly_fx.loc[previous_month:final_month]
    expected_count = years * 12 + 1
    if len(required) != expected_count:
        raise RuntimeError(
            f"{start_year}년: 월말 가격 {expected_count}개가 필요하지만 "
            f"{len(required)}개만 확인됐습니다."
        )
    if len(required_fx) != expected_count:
        raise RuntimeError(
            f"{start_year}년: 환율 데이터 {expected_count}개가 필요하지만 "
            f"{len(required_fx)}개만 확인됐습니다."
        )

    starting_fx = float(required_fx.iloc[0])
    balance_usd = initial_reserve / starting_fx
    rows: list[dict] = []
    depletion_date: pd.Timestamp | None = None

    for date in required.index[1:]:
        previous_price = required.loc[date - pd.offsets.MonthEnd(1)]
        monthly_return = required.loc[date] / previous_price - 1
        fx_rate = float(required_fx.loc[date])
        before_withdrawal_usd = balance_usd * (1 + monthly_return)
        requested_withdrawal_usd = monthly_withdrawal / fx_rate
        actual_withdrawal_usd = min(
            requested_withdrawal_usd, max(before_withdrawal_usd, 0.0)
        )
        actual_withdrawal_krw = actual_withdrawal_usd * fx_rate
        balance_usd = max(before_withdrawal_usd - actual_withdrawal_usd, 0.0)
        ending_balance_krw = balance_usd * fx_rate

        if balance_usd <= 0 and depletion_date is None:
            depletion_date = date

        rows.append(
            {
                "start_year": start_year,
                "date": date,
                "usdkrw": fx_rate,
                "monthly_return": monthly_return,
                "balance_before_withdrawal_usd": before_withdrawal_usd,
                "requested_withdrawal_krw": monthly_withdrawal,
                "withdrawal_usd": actual_withdrawal_usd,
                "withdrawal_krw": actual_withdrawal_krw,
                "ending_balance_usd": balance_usd,
                "ending_balance_krw": ending_balance_krw,
            }
        )

        if depletion_date is not None:
            break

    result = {
        "start_year": start_year,
        "depleted_within_10y": depletion_date is not None,
        "depletion_month": depletion_date.strftime("%Y-%m") if depletion_date else "-",
        "months_survived": len(rows),
        "starting_fx": starting_fx,
        "ending_fx": float(required_fx.loc[rows[-1]["date"]]),
        "ending_balance": rows[-1]["ending_balance_krw"],
        "total_withdrawn": sum(row["withdrawal_krw"] for row in rows),
    }
    return result, pd.DataFrame(rows)


def calculate_backtest_results(
    prices: pd.Series,
    fx_rates: pd.Series,
    first_start_year: int,
    last_start_year: int,
    years: int,
    initial_reserve: float,
    monthly_withdrawal: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """모든 시작연도의 요약 결과와 월별 상세 내역을 계산한다."""
    summaries: list[dict] = []
    details: list[pd.DataFrame] = []

    for start_year in range(first_start_year, last_start_year + 1):
        summary, detail = simulate_one_start(
            prices, fx_rates, start_year, initial_reserve, monthly_withdrawal, years
        )
        summaries.append(summary)
        details.append(detail)

    return pd.DataFrame(summaries), pd.concat(details, ignore_index=True)


# =============================================================================
# 3. 그래프 작성
# =============================================================================

BLUE = "#3479D1"
ORANGE = "#F06432"
TEXT_COLOR = "#55534F"
MUTED_TEXT_COLOR = "#85827C"
GRID_COLOR = "#DEDDD8"
BACKGROUND_COLOR = "#FAFAF9"


def configure_korean_font() -> None:
    """macOS에서는 AppleGothic을 사용하고, 음수 기호 깨짐을 방지한다."""
    korean_font_path = Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf")
    if korean_font_path.exists():
        korean_font = font_manager.FontProperties(fname=korean_font_path)
        plt.rcParams["font.family"] = korean_font.get_name()
    plt.rcParams["axes.unicode_minus"] = False


def draw_rounded_bars(
    ax: Axes,
    x_positions: list[int],
    amounts_in_100m: pd.Series,
    depleted_flags: pd.Series,
) -> list[FancyBboxPatch]:
    """잔액은 파란 막대, 고갈은 주황색 사선 막대로 표시한다."""
    base_bars = ax.bar(x_positions, amounts_in_100m, width=0.62, color="none")
    rounded_bars: list[FancyBboxPatch] = []
    for bar, value, depleted in zip(
        base_bars, amounts_in_100m, depleted_flags
    ):
        height = 0.035 if depleted else float(value)
        rounded = FancyBboxPatch(
            (bar.get_x(), 0),
            bar.get_width(),
            height,
            boxstyle="round,pad=0,rounding_size=0.055",
            linewidth=1.5 if depleted else 0,
            edgecolor=ORANGE if depleted else BLUE,
            facecolor="#FFF4EF" if depleted else BLUE,
            hatch="///" if depleted else None,
            zorder=3,
        )
        ax.add_patch(rounded)
        rounded_bars.append(rounded)
    for bar in base_bars:
        bar.remove()
    return rounded_bars


def add_chart_header(fig: Figure) -> None:
    """제목, 조건 설명과 범례를 추가한다."""
    fig.text(
        0.055,
        0.965,
        "QQQ 투자 시작연도별 10년 후 준비금",
        fontsize=18,
        color=TEXT_COLOR,
        fontweight="semibold",
        ha="left",
        va="top",
    )
    fig.text(
        0.055,
        0.915,
        "초기 1억원 · 매월 말 100만원 인출 · 실제 원/달러 환율 반영",
        fontsize=11,
        color=MUTED_TEXT_COLOR,
        ha="left",
        va="top",
    )
    legend_items = [
        Patch(facecolor=BLUE, edgecolor=BLUE, label="10년 후 잔액"),
        Patch(facecolor="#FFF4EF", edgecolor=ORANGE, hatch="///", label="고갈"),
    ]
    fig.legend(
        handles=legend_items,
        loc="upper left",
        bbox_to_anchor=(0.055, 0.875),
        frameon=False,
        ncol=2,
        fontsize=10,
        handlelength=1.0,
        columnspacing=1.5,
    )


def style_chart_axes(ax: Axes, summary: pd.DataFrame) -> None:
    """축, 눈금, 그리드와 여백을 정리한다."""
    x_positions = list(range(len(summary)))
    ax.set_xlabel("투자 시작연도", color=TEXT_COLOR, labelpad=12)
    ax.set_ylabel("10년 후 준비금 (억원)", color=TEXT_COLOR, labelpad=10)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.1f}"))
    ax.set_xticks(x_positions, summary["start_year"].astype(str))
    ax.tick_params(axis="both", colors=MUTED_TEXT_COLOR, labelsize=10, length=0)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.margins(x=0.025)


def add_bar_labels(
    ax: Axes, rounded_bars: list[FancyBboxPatch], summary: pd.DataFrame
) -> None:
    """각 막대 위에 잔액 또는 고갈 표시를 붙인다."""
    for bar, value, depleted in zip(
        rounded_bars, summary["ending_balance"], summary["depleted_within_10y"]
    ):
        label = "고갈" if depleted else f"{value / 100_000_000:.2f}"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.025,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
            color=ORANGE if depleted else TEXT_COLOR,
            fontweight="semibold",
        )



def save_chart(summary: pd.DataFrame, output_path: Path) -> None:
    """요약 결과를 참고 이미지 스타일의 PNG 막대그래프로 저장한다."""
    configure_korean_font()
    amounts_in_100m = summary["ending_balance"] / 100_000_000
    x_positions = list(range(len(summary)))

    fig, ax = plt.subplots(figsize=(12.5, 6.5), facecolor=BACKGROUND_COLOR)
    ax.set_facecolor(BACKGROUND_COLOR)

    rounded_bars = draw_rounded_bars(
        ax, x_positions, amounts_in_100m, summary["depleted_within_10y"]
    )
    add_chart_header(fig)
    style_chart_axes(ax, summary)
    add_bar_labels(ax, rounded_bars, summary)

    fig.text(
        0.01,
        0.01,
        "QQQ 배당·분할 및 원/달러 환율 반영 · 세금, 환전/거래 수수료 및 물가 제외",
        fontsize=8,
        color=MUTED_TEXT_COLOR,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.80))
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# 4. 결과 저장 및 화면 출력
# =============================================================================


def save_results(
    summary: pd.DataFrame, detail: pd.DataFrame, output_dir: Path
) -> tuple[Path, Path, Path]:
    """CSV 2개와 PNG 그래프를 저장하고 각 경로를 반환한다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "qqq_10y_summary.csv"
    detail_path = output_dir / "qqq_monthly_detail.csv"
    chart_path = output_dir / "qqq_10y_ending_reserve.png"

    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    detail.to_csv(detail_path, index=False, encoding="utf-8-sig")
    save_chart(summary, chart_path)
    return summary_path, detail_path, chart_path


def print_summary(summary: pd.DataFrame) -> None:
    """터미널에서 읽기 쉬운 형식으로 요약 결과를 표시한다."""
    printable = summary.copy()
    printable["depleted_within_10y"] = printable["depleted_within_10y"].map(
        {True: "YES", False: "NO"}
    )
    printable["ending_balance"] = printable["ending_balance"].map(lambda x: f"{x:,.0f}")
    printable["total_withdrawn"] = printable["total_withdrawn"].map(lambda x: f"{x:,.0f}")
    print(printable.to_string(index=False))


# =============================================================================
# 5. 실행 설정 및 진입점
# =============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", default="QQQ")
    parser.add_argument("--first-start-year", type=int, default=2002)
    parser.add_argument("--last-start-year", type=int, default=2016)
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--initial-reserve", type=float, default=100_000_000)
    parser.add_argument("--monthly-withdrawal", type=float, default=1_000_000)
    parser.add_argument("--output-dir", type=Path, default=Path("qqq_backtest_output"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.first_start_year > args.last_start_year:
        raise ValueError("첫 시작연도는 마지막 시작연도보다 늦을 수 없습니다.")
    if args.years <= 0 or args.initial_reserve <= 0 or args.monthly_withdrawal < 0:
        raise ValueError("투자 기간과 준비금은 양수, 월 인출액은 0 이상이어야 합니다.")

    prices, fx_rates = load_market_data(
        ticker=args.ticker,
        first_start_year=args.first_start_year,
        last_start_year=args.last_start_year,
        years=args.years,
    )
    summary, detail = calculate_backtest_results(
        prices=prices,
        fx_rates=fx_rates,
        first_start_year=args.first_start_year,
        last_start_year=args.last_start_year,
        years=args.years,
        initial_reserve=args.initial_reserve,
        monthly_withdrawal=args.monthly_withdrawal,
    )

    summary_path, detail_path, chart_path = save_results(
        summary, detail, args.output_dir
    )
    print_summary(summary)
    print(f"\nSaved: {summary_path}, {detail_path}, {chart_path}")


if __name__ == "__main__":
    main()
