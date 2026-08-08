#!/usr/bin/env python3
"""QQQ와 연 3% 예금의 10년 원리금 인출 경로를 세 사례로 비교한다.

QQQ와 원/달러 환율 데이터를 직접 내려받아 월별 CSV와 그래프를 생성한다.
두 상품 모두 준비금 1억원에서 시작해 매월 말 100만원을 인출하며, 예금은
연 3%를 월 복리로 환산한다. 세금과 거래·환전 수수료는 반영하지 않는다.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
from typing import cast
from urllib.request import urlretrieve

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import font_manager
import pandas as pd


def is_colab_runtime() -> bool:
    """현재 코드가 Google Colab에서 실행 중인지 확인한다."""
    return bool(os.environ.get("COLAB_RELEASE_TAG")) or Path("/content").exists()


IS_COLAB = is_colab_runtime()

try:
    import yfinance as yf
except ImportError:
    if IS_COLAB:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "yfinance"]
        )
        import yfinance as yf
    else:
        raise


SCRIPT_DIR = (
    Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
)
DEFAULT_OUTPUT_DIR = Path("/content/output") if IS_COLAB else SCRIPT_DIR / "output"
DEFAULT_DETAIL_OUTPUT = (
    DEFAULT_OUTPUT_DIR / "qqq_vs_deposit_balance_flow_monthly_detail.csv"
)
DEFAULT_OUTPUT = DEFAULT_OUTPUT_DIR / "qqq_vs_deposit_balance_flow.png"

# 비교할 세 사례의 시작연도를 직접 입력하세요.
LOW_PERFORMANCE_START_YEAR = 2002
MIDDLE_PERFORMANCE_START_YEAR = 2010
HIGH_PERFORMANCE_START_YEAR = 2016

CASES = (
    (LOW_PERFORMANCE_START_YEAR, "최저 성과(고갈)"),
    (MIDDLE_PERFORMANCE_START_YEAR, "중간 성과"),
    (HIGH_PERFORMANCE_START_YEAR, "높은 성과"),
)

INITIAL_RESERVE = 100_000_000
MONTHLY_WITHDRAWAL = 1_000_000
ANNUAL_DEPOSIT_RATE = 0.03
MONTHS = 120

QQQ_COLOR = "#2563EB"
DEPOSIT_COLOR = "#6B7280"
DEPLETION_COLOR = "#DC2626"
REFERENCE_COLOR = "#F59E0B"
GRID_COLOR = "#E5E7EB"
TEXT_COLOR = "#111827"
SECONDARY_TEXT_COLOR = "#4B5563"
TICK_COLOR = "#6B7280"


# =============================================================================
# 1. 실행 환경과 한글 글꼴
# =============================================================================


def configure_korean_font() -> None:
    """사용 가능한 한글 글꼴을 Matplotlib에 설정한다."""
    candidates = (
        "Apple SD Gothic Neo",
        "NanumGothic",
        "Noto Sans CJK KR",
        "Malgun Gothic",
    )
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in candidates:
        if candidate in installed:
            plt.rcParams["font.family"] = candidate
            plt.rcParams["axes.unicode_minus"] = False
            return

    if IS_COLAB:
        font_path = Path("/content/.fonts/NanumGothic-Regular.ttf")
        font_path.parent.mkdir(parents=True, exist_ok=True)
        if not font_path.exists():
            font_url = (
                "https://raw.githubusercontent.com/google/fonts/main/"
                "ofl/nanumgothic/NanumGothic-Regular.ttf"
            )
            urlretrieve(font_url, font_path)
        font_manager.fontManager.addfont(font_path)
        plt.rcParams["font.family"] = font_manager.FontProperties(
            fname=font_path
        ).get_name()
    plt.rcParams["axes.unicode_minus"] = False


# =============================================================================
# 2. 시장 데이터 수집
# =============================================================================


def download_monthly_qqq(start: str, end: str) -> pd.Series:
    """Yahoo Finance에서 QQQ 월말 수정주가를 내려받는다."""
    raw_prices = yf.download(
        "QQQ",
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
        actions=False,
    )
    if raw_prices is None or raw_prices.empty:
        raise RuntimeError("QQQ 가격 데이터를 내려받지 못했습니다.")
    prices = raw_prices["Adj Close"]
    if isinstance(prices, pd.DataFrame):
        price_frame = cast(pd.DataFrame, prices)
        prices = (
            price_frame["QQQ"] if "QQQ" in price_frame else price_frame.iloc[:, 0]
        )
    return prices.dropna().astype(float).resample("ME").last()


def download_monthly_usdkrw(start: str, end: str) -> pd.Series:
    """FRED에서 월말 원/달러 환율을 내려받는다."""
    fred_url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id=DEXKOUS&cosd={start}&coed={end}"
    )
    raw_fx = pd.read_csv(fred_url)
    date_column = "observation_date" if "observation_date" in raw_fx else "DATE"
    raw_fx[date_column] = pd.to_datetime(raw_fx[date_column])
    fx_values = pd.to_numeric(raw_fx["DEXKOUS"], errors="coerce")
    daily_fx = pd.Series(
        fx_values.to_numpy(), index=raw_fx[date_column], name="원달러환율"
    ).dropna()
    return daily_fx.resample("ME").last()


def download_monthly_market_data() -> tuple[pd.Series, pd.Series]:
    """세 사례 전체를 계산하는 데 필요한 시장 데이터를 준비한다."""
    first_year = min(year for year, _ in CASES)
    last_year = max(year for year, _ in CASES)
    start = f"{first_year - 1}-12-01"
    end = f"{last_year + 10}-12-31"
    yahoo_end = f"{last_year + 11}-01-01"  # Yahoo 종료일은 포함되지 않는다.
    return download_monthly_qqq(start, yahoo_end), download_monthly_usdkrw(
        start, end
    )


# =============================================================================
# 3. QQQ와 예금 백테스트
# =============================================================================


def simulate_qqq_case(
    monthly_prices: pd.Series, monthly_fx: pd.Series, start_year: int
) -> pd.DataFrame:
    """한 시작 연도의 QQQ 월별 인출 과정과 잔액을 계산한다."""
    first_month = pd.Timestamp(start_year, 1, 31)
    previous_month = first_month - pd.offsets.MonthEnd(1)
    final_month = first_month + pd.offsets.MonthEnd(MONTHS - 1)
    prices = monthly_prices.loc[previous_month:final_month]
    fx_rates = monthly_fx.loc[previous_month:final_month]
    expected_count = MONTHS + 1
    if len(prices) != expected_count or len(fx_rates) != expected_count:
        raise RuntimeError(
            f"{start_year}년 데이터가 부족합니다: "
            f"QQQ {len(prices)}개, 환율 {len(fx_rates)}개 "
            f"(각 {expected_count}개 필요)"
        )

    balance_usd = INITIAL_RESERVE / float(fx_rates.iloc[0])
    rows: list[dict] = []
    for date in prices.index[1:]:
        previous_price = float(prices.loc[date - pd.offsets.MonthEnd(1)])
        monthly_return = float(prices.loc[date]) / previous_price - 1
        fx_rate = float(fx_rates.loc[date])
        before_withdrawal_usd = balance_usd * (1 + monthly_return)
        requested_withdrawal_usd = MONTHLY_WITHDRAWAL / fx_rate
        withdrawal_usd = min(
            requested_withdrawal_usd, max(before_withdrawal_usd, 0.0)
        )
        withdrawal_krw = withdrawal_usd * fx_rate
        balance_usd = max(before_withdrawal_usd - withdrawal_usd, 0.0)
        rows.append(
            {
                "시작연도": start_year,
                "날짜": date,
                "원달러환율": fx_rate,
                "월수익률": monthly_return,
                "인출전잔액(달러)": before_withdrawal_usd,
                "요청인출액(원)": MONTHLY_WITHDRAWAL,
                "실제인출액(달러)": withdrawal_usd,
                "실제인출액(원)": withdrawal_krw,
                "월말잔액(달러)": balance_usd,
                "월말잔액(원)": balance_usd * fx_rate,
            }
        )
        if balance_usd <= 0:
            break
    return pd.DataFrame(rows)


def create_detail_csv(output_path: Path) -> Path:
    """시장 데이터를 받아 세 사례의 월별 상세 CSV를 생성한다."""
    monthly_prices, monthly_fx = download_monthly_market_data()
    detail = pd.concat(
        [simulate_qqq_case(monthly_prices, monthly_fx, year) for year, _ in CASES],
        ignore_index=True,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    detail.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def load_qqq_paths(detail_csv: Path) -> dict[int, list[float]]:
    """상세 CSV에서 각 사례의 월말 원화 잔액을 120개월 길이로 만든다."""
    if not detail_csv.exists():
        raise FileNotFoundError(
            f"월별 상세 CSV가 없습니다: {detail_csv}\n"
            "--detail-csv 경로를 확인하거나 옵션 없이 새 CSV를 생성해 주세요."
        )

    detail = pd.read_csv(detail_csv)
    required_columns = {"시작연도", "날짜", "월말잔액(원)"}
    missing = required_columns - set(detail.columns)
    if missing:
        raise ValueError(f"상세 CSV에 필요한 열이 없습니다: {sorted(missing)}")

    paths: dict[int, list[float]] = {}
    for year, _ in CASES:
        rows = detail.loc[detail["시작연도"] == year].sort_values("날짜")
        if rows.empty:
            raise ValueError(f"상세 CSV에 {year}년 데이터가 없습니다.")

        balances = rows["월말잔액(원)"].astype(float).tolist()
        balances = balances[:MONTHS]
        if len(balances) < MONTHS and balances[-1] > 0:
            raise ValueError(
                f"{year}년 데이터가 {len(balances)}개월에서 끝났지만 "
                "마지막 잔액이 0원이 아닙니다."
            )
        balances.extend([0.0] * (MONTHS - len(balances)))
        paths[year] = [float(INITIAL_RESERVE), *balances]
    return paths


def calculate_deposit_path() -> list[float]:
    """연 3% 예금에서 매월 말 100만원을 인출한 잔액 경로를 계산한다."""
    monthly_rate = (1 + ANNUAL_DEPOSIT_RATE) ** (1 / 12) - 1
    balance = float(INITIAL_RESERVE)
    path = [balance]
    for _ in range(MONTHS):
        balance = max(balance * (1 + monthly_rate) - MONTHLY_WITHDRAWAL, 0.0)
        path.append(balance)
    return path


def first_depletion_month(path: list[float]) -> int | None:
    """최초 고갈 월을 반환하고 고갈되지 않으면 None을 반환한다."""
    return next(
        (month for month, balance in enumerate(path[1:], 1) if balance <= 0),
        None,
    )


# =============================================================================
# 4. 그래프 작성
# =============================================================================


def format_balance(amount: float) -> str:
    """그래프 주석용 원화 잔액을 억원/만원 단위로 표시한다."""
    rounded_manwon = int(amount / 10_000 + 0.5)
    if rounded_manwon == 0:
        return "0원"
    eok, manwon = divmod(rounded_manwon, 10_000)
    if eok and manwon:
        return f"{eok}억 {manwon:,}만원"
    if eok:
        return f"{eok}억원"
    return f"{manwon:,}만원"


def format_eok_axis(value: float, _: float) -> str:
    """억원 축 눈금에서 불필요한 소수점 0을 제거한다."""
    return f"{value / 1e8:.1f}".rstrip("0").rstrip(".")


def add_path_annotation(
    ax: plt.Axes, path: list[float], color: str, start_year: int
) -> None:
    """고갈 지점 또는 10년 후 잔액을 선 위에 표시한다."""
    depletion_month = first_depletion_month(path)
    if depletion_month is not None:
        years, months = divmod(depletion_month, 12)
        duration = f"{years}년" if months == 0 else f"{years}년 {months}개월"
        depletion_year = start_year + depletion_month / 12
        ax.scatter(depletion_year, 0, s=65, color=DEPLETION_COLOR, zorder=5)
        ax.annotate(
            f"{duration} 후 고갈",
            xy=(depletion_year, 0),
            xytext=(0, 17),
            textcoords="offset points",
            ha="center",
            color=color,
            fontsize=13,
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.82,
            },
        )
    else:
        ending_year = start_year + MONTHS / 12
        ax.scatter(ending_year, path[-1], s=38, color=color, zorder=5)
        ax.annotate(
            format_balance(path[-1]),
            xy=(ending_year, path[-1]),
            xytext=(-8, 8),
            textcoords="offset points",
            ha="right",
            color=color,
            fontsize=13,
            fontweight="bold",
        )


def draw_case_panel(
    ax: plt.Axes,
    start_year: int,
    case_label: str,
    qqq_path: list[float],
    deposit_path: list[float],
    y_max: float,
) -> None:
    """한 시작 연도의 QQQ·예금 잔액 경로를 패널 하나에 그린다."""
    calendar_years = [
        start_year + month / 12 for month in range(MONTHS + 1)
    ]
    ax.plot(
        calendar_years,
        qqq_path,
        color=QQQ_COLOR,
        linewidth=2.6,
        label="QQQ",
    )
    ax.plot(
        calendar_years,
        deposit_path,
        color=DEPOSIT_COLOR,
        linewidth=2.2,
        linestyle="--",
        label="예금(연 3%)",
    )
    ax.axhline(
        INITIAL_RESERVE,
        color=REFERENCE_COLOR,
        linewidth=2.0,
        linestyle=":",
        label="시작 준비금 1억원",
        zorder=0,
    )
    add_path_annotation(ax, qqq_path, QQQ_COLOR, start_year)
    add_path_annotation(ax, deposit_path, DEPOSIT_COLOR, start_year)

    ax.set_title(
        f"{start_year}년 시작 · {case_label}",
        loc="left",
        fontsize=18,
        fontweight="bold",
        color=TEXT_COLOR,
        pad=12,
    )
    ax.set_ylim(0, y_max)
    ax.set_ylabel("잔액(억원)", color=SECONDARY_TEXT_COLOR, fontsize=13)
    ax.set_xlabel("연도", color=SECONDARY_TEXT_COLOR, fontsize=13)
    ax.set_xticks(range(start_year, start_year + 11))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_eok_axis))
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(
        axis="both",
        colors=TICK_COLOR,
        labelsize=11,
        labelbottom=True,
        length=0,
    )


def save_comparison_chart(
    qqq_paths: dict[int, list[float]], deposit_path: list[float], output_path: Path
) -> None:
    """고갈·중간·상승 사례를 세로 3단 선그래프로 저장한다."""
    configure_korean_font()
    max_balance = max(max(path) for path in qqq_paths.values())
    y_max = max(400_000_000, max_balance * 1.12)

    fig, axes = plt.subplots(3, 1, figsize=(11, 14), sharey=True)
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "성장 준비금 10년 잔액 변화｜QQQ vs 연 3% 예금",
        x=0.08,
        y=0.985,
        ha="left",
        fontsize=25,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    fig.text(
        0.08,
        0.943,
        "초기 준비금 1억원 · 매월 말 100만원 인출 · 10년간 월별 잔액 비교",
        ha="left",
        fontsize=14,
        color=SECONDARY_TEXT_COLOR,
    )

    for ax, (year, case_label) in zip(axes, CASES):
        draw_case_panel(
            ax,
            start_year=year,
            case_label=case_label,
            qqq_path=qqq_paths[year],
            deposit_path=deposit_path,
            y_max=y_max,
        )

    axes[0].legend(frameon=False, loc="upper right", ncol=3, fontsize=12)

    fig.text(
        0.08,
        0.02,
        "QQQ: 배당·분할 및 원/달러 환율 반영 · 예금: 연 3% 월 복리 환산 · 세금과 수수료 제외",
        fontsize=11,
        color=TICK_COLOR,
    )
    fig.tight_layout(rect=(0.04, 0.045, 0.98, 0.915), h_pad=2.5)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# 5. 실행 옵션과 진입점
# =============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--detail-csv",
        type=Path,
        help="기존 상세 CSV를 사용할 때만 지정합니다.",
    )
    parser.add_argument(
        "--detail-output", type=Path, default=DEFAULT_DETAIL_OUTPUT
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    if IS_COLAB:
        args, _ = parser.parse_known_args()
        return args
    return parser.parse_args()


def prepare_detail_csv(args: argparse.Namespace) -> Path:
    """기존 CSV를 선택하거나 새 백테스트 CSV를 생성한다."""
    if args.detail_csv is not None:
        return args.detail_csv.expanduser().resolve()
    return create_detail_csv(args.detail_output)


def main() -> None:
    args = parse_args()
    detail_csv = prepare_detail_csv(args)
    qqq_paths = load_qqq_paths(detail_csv)
    deposit_path = calculate_deposit_path()
    save_comparison_chart(qqq_paths, deposit_path, args.output)
    print(f"Saved: {detail_csv}")
    print(f"Saved: {args.output}")

    if IS_COLAB:
        from IPython.display import Image, display

        display(Image(filename=str(args.output)))


if __name__ == "__main__":
    main()
