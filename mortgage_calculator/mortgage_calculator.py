"""주택담보대출(주담대) 상환금 계산기 모듈."""

from typing import Any, Dict


# ==========================================
# [대출 설정값 상수] - 필요시 아래 값을 변경하세요.
# ==========================================
PRINCIPAL = 100_000_000  # 대출 금액 (원 단위, 예: 1억원)
YEARS = 30  # 대출 기간 (년 단위)
ANNUAL_RATE = 4.5  # 연이율 (퍼센트 단위)


class MortgageCalculator:
    """주택담보대출 월 상환금 계산기."""

    def __init__(self, principal: float, years: int, annual_rate: float):
        if principal <= 0:
            raise ValueError("대출금액은 0보다 커야 합니다.")
        if years <= 0:
            raise ValueError("대출기간은 1년 이상이어야 합니다.")
        if annual_rate < 0:
            raise ValueError("연이율은 0% 이상이어야 합니다.")

        self.principal = float(principal)
        self.years = int(years)
        self.months = self.years * 12
        self.annual_rate = float(annual_rate)
        self.monthly_rate = (self.annual_rate / 100) / 12

    def calculate_equal_principal_and_interest(self) -> Dict[str, Any]:
        """원리금균등상환 금액과 월별 상환 일정을 계산한다."""
        rate = self.monthly_rate
        months = self.months
        principal = self.principal

        if rate == 0:
            monthly_payment = principal / months
        else:
            compound = (1 + rate) ** months
            monthly_payment = principal * (rate * compound) / (compound - 1)

        schedule = []
        balance = principal
        total_interest = 0.0

        for month in range(1, months + 1):
            interest_payment = balance * rate
            principal_payment = monthly_payment - interest_payment

            # 마지막 달의 부동소수점 잔액 오차를 조정한다.
            if month == months:
                principal_payment = balance
                actual_payment = principal_payment + interest_payment
            else:
                actual_payment = monthly_payment

            balance -= principal_payment
            if abs(balance) < 1e-5:
                balance = 0.0
            total_interest += interest_payment

            schedule.append(
                {
                    "month": month,
                    "monthly_payment": round(actual_payment),
                    "principal_payment": round(principal_payment),
                    "interest_payment": round(interest_payment),
                    "remaining_balance": round(balance),
                }
            )

        return {
            "method_name": "원리금균등상환",
            "first_month_payment": round(monthly_payment),
            "last_month_payment": schedule[-1]["monthly_payment"],
            "total_interest": round(total_interest),
            "total_payment": round(principal + total_interest),
            "schedule": schedule,
        }

    def calculate_equal_principal(self) -> Dict[str, Any]:
        """원금균등상환 금액과 월별 상환 일정을 계산한다."""
        rate = self.monthly_rate
        months = self.months
        principal = self.principal
        monthly_principal = principal / months
        schedule = []
        balance = principal
        total_interest = 0.0

        for month in range(1, months + 1):
            interest_payment = balance * rate
            payment = monthly_principal + interest_payment
            balance -= monthly_principal
            if abs(balance) < 1e-5:
                balance = 0.0
            total_interest += interest_payment

            schedule.append(
                {
                    "month": month,
                    "monthly_payment": round(payment),
                    "principal_payment": round(monthly_principal),
                    "interest_payment": round(interest_payment),
                    "remaining_balance": round(balance),
                }
            )

        return {
            "method_name": "원금균등상환",
            "first_month_payment": schedule[0]["monthly_payment"],
            "last_month_payment": schedule[-1]["monthly_payment"],
            "total_interest": round(total_interest),
            "total_payment": round(principal + total_interest),
            "schedule": schedule,
        }

    def calculate_bullet_maturity(self) -> Dict[str, Any]:
        """만기일시상환 금액과 월별 상환 일정을 계산한다."""
        rate = self.monthly_rate
        months = self.months
        principal = self.principal
        monthly_interest = principal * rate
        total_interest = monthly_interest * months
        schedule = []

        for month in range(1, months + 1):
            is_last = month == months
            principal_payment = principal if is_last else 0.0
            payment = monthly_interest + principal_payment
            balance = 0.0 if is_last else principal

            schedule.append(
                {
                    "month": month,
                    "monthly_payment": round(payment),
                    "principal_payment": round(principal_payment),
                    "interest_payment": round(monthly_interest),
                    "remaining_balance": round(balance),
                }
            )

        return {
            "method_name": "만기일시상환",
            "first_month_payment": round(monthly_interest),
            "last_month_payment": schedule[-1]["monthly_payment"],
            "total_interest": round(total_interest),
            "total_payment": round(principal + total_interest),
            "schedule": schedule,
        }


def format_korean_currency(amount: float) -> str:
    """원화 금액을 읽기 쉬운 억/만원 단위 표기로 변환한다."""
    rounded_amount = int(round(amount))
    if rounded_amount == 0:
        return "0원"

    eok = rounded_amount // 100_000_000
    remainder = rounded_amount % 100_000_000
    man = remainder // 10_000
    won = remainder % 10_000

    parts = []
    if eok > 0:
        parts.append(f"{eok}억")
    if man > 0:
        parts.append(f"{man:,}만")
    if won > 0 or not parts:
        parts.append(f"{won:,}")

    return " ".join(parts) + "원"


def calculate_mortgage(
    principal: float,
    years: int,
    annual_rate: float,
    method: str = "원리금균등",
) -> Dict[str, Any]:
    """선택한 상환 방식으로 주택담보대출 상환금을 계산한다."""
    calculator = MortgageCalculator(principal, years, annual_rate)

    if method == "원리금균등":
        return calculator.calculate_equal_principal_and_interest()
    if method == "원금균등":
        return calculator.calculate_equal_principal()
    if method == "만기일시":
        return calculator.calculate_bullet_maturity()
    raise ValueError(
        "상환 방식은 '원리금균등', '원금균등', '만기일시' 중 선택해주세요."
    )


def format_currency_detail(amount: float) -> str:
    """한국식 단위와 원 단위 금액을 함께 표시한다."""
    return f"{format_korean_currency(amount)} ({amount:,.0f}원)"


def pad_korean_text(text: str, width: int) -> str:
    """한글의 터미널 표시 폭을 고려해 오른쪽 공백을 채운다."""
    display_width = sum(2 if ord(character) > 127 else 1 for character in text)
    return text + " " * max(0, width - display_width)


def print_method_summary(index: int, result: Dict[str, Any]) -> None:
    """상환 방식 하나의 핵심 금액을 같은 형식으로 출력한다."""
    rows = (
        ("첫 달 납입액", result["first_month_payment"]),
        ("마지막 달 납입액", result["last_month_payment"]),
        ("총 납부 이자", result["total_interest"]),
        ("총 상환 금액", result["total_payment"]),
    )

    print(f"\n[{index}] {result['method_name']}")
    print("-" * 72)
    for label, amount in rows:
        print(f"  {pad_korean_text(label, 18)} : {format_currency_detail(amount)}")


def print_summary(principal: float, years: int, annual_rate: float) -> None:
    """세 가지 상환 방식의 비교 리포트를 출력한다."""
    calculator = MortgageCalculator(principal, years, annual_rate)
    results = (
        calculator.calculate_equal_principal_and_interest(),
        calculator.calculate_equal_principal(),
        calculator.calculate_bullet_maturity(),
    )

    print("=" * 72)
    print("🏠 주택담보대출 상환금 비교")
    print("=" * 72)
    print(f"대출 금액 : {format_currency_detail(principal)}")
    print(f"대출 기간 : {years}년 ({years * 12:,}개월)")
    print(f"연 이율   : {annual_rate:g}%")

    for index, result in enumerate(results, start=1):
        print_method_summary(index, result)

    print("\n" + "=" * 72)


if __name__ == "__main__":
    print_summary(PRINCIPAL, YEARS, ANNUAL_RATE)
