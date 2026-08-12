# 그래프·표 스타일 가이드

블로그용 그래프와 표를 같은 인상과 가독성으로 만들기 위한 저장소 공통 규격이다.
새 시각 자료는 이 문서의 **공통 토큰**을 먼저 적용하고, 자료 유형에 맞는 규칙만
추가한다. 특별한 이유로 규격을 벗어날 때는 코드 가까이에 이유를 남긴다.

## 1. 적용 우선순위

1. 색상·글꼴·크기 같은 공통 토큰을 사용한다.
2. 선그래프, 막대그래프, 표 중 해당 유형의 규칙을 적용한다.
3. 데이터 겹침이나 잘림이 있으면 위치와 여백만 조정한다.
4. 특정 연도나 값만을 위한 예외문보다 좌표 계산과 정렬 방식을 개선한다.

핵심 원칙:

- 네이버 블로그에서 축소해도 숫자와 문구가 읽혀야 한다.
- 장식보다 비교, 숫자, 상태의 전달력을 우선한다.
- 같은 의미는 모든 프로젝트에서 같은 색과 문구로 표현한다.
- 계산용 숫자와 화면 표시용 문자열을 분리한다.
- 제목·부제·각주에 같은 조건을 반복하지 않는다.
- 배경은 흰색, 결과 이미지는 고해상도 PNG를 기본으로 한다.

## 2. 공통 디자인 토큰

### 2.1 글꼴

기본 글꼴은 Pretendard다. 설치되지 않은 환경에서는 아래 순서로 대체한다.

```python
FONT_CANDIDATES = (
    "Pretendard",
    "Apple SD Gothic Neo",
    "Noto Sans CJK KR",
    "Malgun Gothic",
)
```

### 2.2 그래프 글자 규격

| 요소 | 크기 | 굵기 | 색상 |
|---|---:|---|---|
| 브랜드 라벨 (`대도시 연구실`) | 13pt | Regular | `#777777` |
| 전체 제목 | 21pt | Bold | `#0B0B0B` |
| 부제 | 16pt | Regular | `#666666` |
| 패널 제목 | 18pt | Bold | `#0B0B0B` |
| X·Y축 제목 | 15pt | Regular | `#777777` |
| X·Y축 눈금 | 15pt | Regular | `#777777` |
| 범례 | 15pt | **Regular** | 기본 텍스트색 |
| 막대 위 수치·선 끝 잔액·고갈 문구 | 14pt | Bold | 해당 데이터 색상 |
| 기준선 직접 라벨 | 14pt | Regular | `#F59E0B` |
| 하단 각주 | 13pt | Regular | `#777777` |

범례는 강조 대상이 아니므로 볼드를 사용하지 않는다. 핵심 데이터 라벨만 Bold로
두어 시각적 위계를 만든다.

재사용할 상수:

```python
BRAND_SIZE = 13
TITLE_SIZE = 21
SUBTITLE_SIZE = 16
PANEL_TITLE_SIZE = 18
AXIS_TITLE_SIZE = 15
TICK_SIZE = 15
LEGEND_SIZE = 15
DATA_LABEL_SIZE = 14
REFERENCE_LABEL_SIZE = 14
FOOTNOTE_SIZE = 13
```

### 2.3 색상

```python
QQQ_COLOR = "#2F7DD3"
SMH_COLOR = "#F06432"
SPY_COLOR = "#1FAE7A"
BRKB_COLOR = "#F2A000"
DEPOSIT_COLOR = "#8D8B85"
DEPLETION_COLOR = "#F06432"
REFERENCE_COLOR = "#F59E0B"
SURVIVAL_FACE_COLOR = "#F3F7FD"
SURVIVAL_EDGE_COLOR = "#C5D9F4"

BACKGROUND_COLOR = "#FFFFFF"
GRID_COLOR = "#DEDCD6"
TEXT_COLOR = "#0B0B0B"
SECONDARY_TEXT_COLOR = "#666666"
TICK_COLOR = "#777777"
FOOTNOTE_COLOR = "#777777"

TABLE_HEADER_COLOR = "#2B4A75"
TABLE_HEADER_RULE_COLOR = "#7FB3D5"
TABLE_TEXT_COLOR = "#1E293B"
TABLE_MUTED_TEXT_COLOR = "#64748B"
TABLE_BORDER_COLOR = "#F0F2F5"
TABLE_STRIPE_COLOR = "#FAFBFC"
TABLE_HOVER_COLOR = "#EFF6FF"
TABLE_SUMMARY_COLOR = "#E8EDF3"
TABLE_SUMMARY_RULE_COLOR = "#94A3B8"
```

색상의 의미:

| 대상 | 색상·표현 |
|---|---|
| QQQ | 블루 `#2F7DD3` |
| SMH 또는 고갈 강조 | 오렌지 `#F06432` |
| SPY | 그린 `#1FAE7A` |
| BRK-B 또는 보조 앰버 계열 | 앰버 `#F2A000` |
| 예금·보조 비교선 | 웜그레이 `#8D8B85` |
| 시작 준비금 기준선 | 앰버 `#F59E0B` |
| 완주(미소진) 상태 | 연한 블루 배경, 블루 테두리, `///` 해치 |

종목색은 데이터의 정체성을, 고갈·완주 표현은 상태를 나타낸다. 두 의미를
섞지 않는다. 같은 색을 공유하더라도 범례와 문구로 의미가 분명해야 한다.

## 3. 그래프 공통 구조

위에서 아래로 다음 순서를 사용한다.

```text
대도시 연구실
전체 제목
부제
범례
그래프 또는 첫 번째 패널
각주
```

- 브랜드·제목·부제 세 줄은 한 덩어리로 보이도록 간격을 좁힌다.
- 제목과 부제는 가깝게 두되 글자가 닿지 않게 한다.
- 범례는 제목 영역과 그래프 사이에 두고 양쪽과 과도하게 떨어뜨리지 않는다.
- 패널 제목은 전체 제목보다 작게 쓰며 그래프와 가깝게 둔다.
- 그래프 좌우 여백은 각각 약 4%를 시작값으로 삼는다.
- 여러 패널의 세로 간격은 기본값보다 약 10% 좁게 시작한다.
- 수평 그리드만 사용하고 세로 그리드는 기본적으로 생략한다.
- 위·오른쪽·왼쪽 테두리는 제거하고 아래 테두리만 연하게 남긴다.
- 비교 패널은 같은 Y축 범위와 단위를 사용한다.
- Y축은 특별한 이유가 없으면 0에서 시작한다.

기본 축 설정:

```python
fig.patch.set_facecolor(BACKGROUND_COLOR)
ax.set_facecolor(BACKGROUND_COLOR)
ax.grid(axis="y", color=GRID_COLOR, linewidth=0.9)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.spines["bottom"].set_color(GRID_COLOR)
ax.tick_params(
    axis="both",
    colors=TICK_COLOR,
    labelsize=TICK_SIZE,
    length=0,
)
ax.set_xlabel("연도", fontsize=AXIS_TITLE_SIZE, color=TICK_COLOR)
ax.set_ylabel("잔액(억원)", fontsize=AXIS_TITLE_SIZE, color=TICK_COLOR)
```

범례 기본 설정:

```python
ax.legend(
    frameon=False,
    prop={"size": LEGEND_SIZE},  # Regular: weight를 지정하지 않는다.
)
```

## 4. 제목·문구 규칙

### 4.1 제목과 부제

제목은 무엇을 비교했는지, 부제는 핵심 입력 조건만 보여준다.

```text
성장 준비금 10년 잔액 변화 | QQQ vs 연 3% 예금
초기 준비금 1억원 · 매월 100만원 인출 · 10년
```

- 제목은 한 줄을 우선하며 중복되는 단어를 줄인다.
- 축에는 문맥상 자연스러운 `잔액`을 우선한다.
- 입력한 종목, 기간, 금액은 하드코딩하지 말고 동적으로 만든다.
- `대도시 연구실`은 출처 각주가 아니라 상단 브랜드 라벨로 취급한다.

### 4.2 상태와 기간

- 유지 상태: `✓ 유지` 또는 문맥상 `10년 유지`
- 고갈 상태: `✕ 고갈`
- 고갈 기간: `6년 5개월` 또는 `6년 5개월 후 고갈`
- 고갈 시점 열에서 해당 값이 없으면 `-`
- 결과표 문구와 그래프 문구는 같은 용어를 사용한다.

이모지 모양의 큰 아이콘보다 절제된 `✓`, `✕` 기호를 사용한다.

### 4.3 금액과 비율

- 원화는 `억원`, `만원` 단위로 읽기 쉽게 표시한다.
- 예: `1억원`, `1억 9,023만원`, `324만원`.
- 생존율은 `100% (15/15)`처럼 비율과 건수를 함께 표시한다.
- 평균 최종 잔액은 금액만 표시하고 비교 비율은 표 아래 설명으로 분리할 수 있다.
- 계산용 DataFrame은 숫자형으로 유지하고 표시용 복사본만 문자열로 변환한다.

### 4.4 각주

데이터 반영 사항과 제외 조건 중 독자의 해석에 필요한 내용만 짧게 적는다.

```text
QQQ 배당·분할 및 환율 반영
※ 세금·수수료 제외
```

- 제목이나 본문에 이미 설명한 조건을 반복하지 않는다.
- 실제 계산에서 제외하지 않았거나 설명 가치가 낮은 항목을 관성적으로 나열하지 않는다.
- 기본 각주 글자는 13pt Regular다.

## 5. 선그래프

- 주요 선은 약 3.2pt, 보조 비교선은 약 2.6pt를 시작값으로 사용한다.
- 예금은 웜그레이 점선으로 표시해 색상 외에도 투자자산과 구분한다.
- 시작 준비금은 가는 앰버 점선으로 표시한다.
- 기준선 문구가 데이터를 가리면 직접 라벨을 제거해도 된다.
- 직접 라벨을 쓸 때는 `시작 준비금 1억원`처럼 기준과 금액을 함께 적고,
  데이터가 적은 왼쪽 구간 등 빈 공간에 둔다.
- 선 끝 잔액과 고갈 문구는 14pt Bold로 표시한다.
- 선이나 다른 라벨과 겹치면 세로 오프셋을 조정하고 필요하면 흰 배경을 둔다.
- 같은 지점에서 끝나는 여러 계열은 오프셋을 달리해 모두 읽히게 한다.

## 6. 막대그래프

- 같은 시작연도의 막대와 라벨은 하나의 그룹으로 인식되게 배치한다.
- 막대 위 수치와 고갈 문구는 14pt Bold로 표시한다.
- 라벨의 X좌표는 막대 중심(`bar.get_x() + bar.get_width() / 2`)에서 계산한다.
- 여러 줄 고갈 문구도 막대 중심을 기준으로 가운데 정렬한다.
- 특정 연도만 옮기는 `if` 문을 두지 말고 텍스트 폭, 그룹 중심, 좌표 변환을
  이용해 공통 배치 문제를 해결한다.
- 고갈 막대가 없더라도 범례나 해치로 막대가 없는 이유를 설명한다.
- 최고·최저 막대의 별도 강조색은 해석상 꼭 필요할 때만 사용한다.

```python
x_center = bar.get_x() + bar.get_width() / 2
ax.annotate(
    label,
    xy=(x_center, bar.get_height()),
    xytext=(0, 5),
    textcoords="offset points",
    ha="center",
    va="bottom",
    fontsize=DATA_LABEL_SIZE,
    fontweight="bold",
)
```

## 7. 표

### 7.1 공통 레이아웃

- 표는 최대 너비 `700px`의 래퍼에 넣으며, 열이 많아도 이 기준을 늘리지 않는다.
- 같은 표에 속한 제목, 캡션, 표 래퍼와 각주는 모두 `max-width: 700px`로
  통일한다. 열이 넘치면 래퍼의 가로 스크롤로 표시한다.
- 래퍼는 `overflow-x: auto`, 흰 배경, `1px` 연한 테두리, `12px` 모서리를 사용한다.
- 표 너비는 `100%`, `border-collapse: separate`, `border-spacing: 0`으로 한다.
- 과한 그림자는 사용하지 않는다.
- 블로그 표에는 판단에 필요한 핵심 열만 남기고 상세 데이터는 CSV로 분리한다.

### 7.2 글꼴과 정렬

| 요소 | 크기 | 굵기 | 색상 | 기본 여백 |
|---|---:|---:|---|---|
| 표 제목 | 20px | 700 | `#0F172A` | `30px 0 8px` |
| 표 캡션 | 13px | 400 | `#64748B` | `0 0 10px` |
| 표 헤더 | 13px | 700 | 흰색 | `8px 12px` |
| 표 본문 | 13px | 400 | `#1E293B` | `7px 12px` |

- 숫자는 `font-variant-numeric: tabular-nums`와 오른쪽 정렬을 사용한다.
- 표 캡션은 하단 각주와 같은 `13px`를 사용해 보조 설명의 가독성을
  일관되게 유지한다.
- 시작연도·사례명 등 행 식별 열은 가운데 정렬한다.
- 요약표의 식별 열은 필요할 때 `font-weight: 600`으로 강조한다.
- 금액 열을 관성적으로 Bold 처리하지 않는다.
- 음수 또는 고갈 금액을 강조할 때만 `#F06432`를 사용할 수 있다.

### 7.3 행과 요약값

- 헤더는 `#2B4A75`, 흰 글자, 아래 `2px solid #7FB3D5`를 사용한다.
- 본문 구분선은 `1px solid #F0F2F5`, 짝수 행은 `#FAFBFC`를 사용한다.
- 노트북에서는 hover와 sticky header를 쓸 수 있지만 정적 캡처가 없어도 읽혀야 한다.
- 합계, 평균, 생존율은 실제로 필요한 행만 표 마지막에 둔다.
- 강조 여부는 자료 목적에 따라 결정하되, 동일한 요약 행끼리는 같은 굵기를 사용한다.
- 계산용 음수와 화면용 `고갈` 문구를 별도 값으로 관리한다.

권장 데이터 준비:

```python
display_table = result_table.copy()
display_table["최종 잔액"] = display_table["final_balance_krw"].map(
    format_korean_currency
)
table_html = display_table[DISPLAY_COLUMNS].to_html(
    index=False,
    border=0,
    classes="result-table summary-table",
)
```

### 7.4 재사용 CSS

```css
.table-wrap {
    max-width: 700px;
    margin: 12px 0 28px;
    overflow-x: auto;
    border: 1px solid #f0f2f5;
    border-radius: 12px;
}
.result-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    color: #1e293b;
}
.result-table th {
    padding: 8px 12px;
    background: #2b4a75;
    border-bottom: 2px solid #7fb3d5;
    color: white;
    font-weight: 700;
    white-space: nowrap;
}
.result-table td {
    padding: 7px 12px;
    border-bottom: 1px solid #f0f2f5;
    background: white;
    white-space: nowrap;
}
.result-table tbody tr:nth-child(even) td { background: #fafbfc; }
.result-table tbody tr:last-child td { border-bottom: 0; }
.result-table .number { text-align: right; }
.result-table .identifier { text-align: center; }
.result-table .depleted { color: #f06432; }
.result-table .summary-row td {
    background: #e8edf3;
    border-top: 2px solid #94a3b8;
}
```

## 8. 이미지 저장

- PNG와 `dpi=200`을 기본값으로 사용한다.
- 배경색을 명시하고 `bbox_inches="tight"`로 잘림을 방지한다.
- 그림 크기를 키우는 것만으로 글자를 작게 만들지 않는다. 블로그 축소를 고려해
  이 가이드의 절대 글자 크기를 유지한다.

```python
fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight",
    facecolor=BACKGROUND_COLOR,
)
```

## 9. 구현 순서

새 그래프나 표는 다음 순서로 만든다.

1. 공통 색상과 글자 크기 상수를 정의한다.
2. 계산 결과를 숫자형 DataFrame으로 준비한다.
3. 제목·부제·축·범례 문구를 입력값에서 생성한다.
4. 그래프 또는 표시용 표를 만든다.
5. 데이터 라벨의 중심 정렬과 겹침을 확인한다.
6. PNG를 저장하고 실제 블로그 표시 크기로 축소해 확인한다.
7. 특별한 예외 좌표나 중복 스타일 값이 남았는지 정리한다.

프로젝트마다 상수 이름을 새로 만들기보다 이 문서의 이름과 값을 그대로 재사용한다.
같은 노트북에서 여러 그래프를 만들면 공통 제목 영역, 축 스타일, 저장 로직을
작은 함수로 공유하되 한 줄짜리 래퍼를 과도하게 만들지 않는다.

## 10. 최종 점검

### 글꼴과 배치

- [ ] Pretendard 또는 지정한 대체 글꼴이 적용됐는가?
- [ ] 브랜드 13, 제목 21, 부제 16pt가 적용됐는가?
- [ ] 축과 범례 15, 데이터 라벨 14, 각주 13pt가 적용됐는가?
- [ ] 범례가 Regular이며 데이터 라벨만 Bold인가?
- [ ] 브랜드·제목·부제의 간격이 한 묶음처럼 보이는가?

### 그래프

- [ ] 축 단위와 범위가 비교에 적합하며 필요하면 0에서 시작하는가?
- [ ] 막대 라벨이 막대 중심에 있고 선 끝 라벨이 선과 겹치지 않는가?
- [ ] 특정 연도만을 위한 위치 예외문 없이 공통 좌표 계산을 사용하는가?
- [ ] 같은 의미의 데이터와 상태가 지정 색상으로 표시됐는가?
- [ ] 기준선 문구가 데이터를 가리거나 범례와 중복되지 않는가?

### 표와 문구

- [ ] 숫자 열은 오른쪽, 식별 열은 가운데 정렬됐는가?
- [ ] 계산용 숫자와 표시용 문자열이 분리됐는가?
- [ ] 유지·고갈·기간·생존율 문구가 일관적인가?
- [ ] 요약 행과 색상 강조가 꼭 필요한 곳에만 사용됐는가?
- [ ] 각주에는 실제로 적용된 반영·제외 조건만 적었는가?

### 출력

- [ ] PNG가 200dpi, 흰 배경으로 저장됐는가?
- [ ] 제목, 범례, 라벨, 각주가 잘리지 않았는가?
- [ ] 블로그에 축소해서도 모든 핵심 숫자를 읽을 수 있는가?
