# 그래프·표 스타일 가이드

이 문서는 블로그에 삽입할 그래프와 표의 시각 규칙을 일관되게 유지하기 위한 기준이다.
새 시각 자료를 만들 때 특별한 이유가 없다면 아래 규격을 기본값으로 사용한다.

## 1. 기본 원칙

- 최종 결과는 네이버 블로그에서 읽기 쉬운 크기와 대비를 우선한다.
- 장식보다 데이터 비교와 숫자 가독성을 우선한다.
- 그래프와 표의 글꼴, 색상, 숫자 표기법을 통일한다.
- 네이버 블로그 본문과 자연스럽게 이어지도록 순백색 배경을 사용한다.
- PNG는 블로그 표시 크기보다 크게 생성해 축소했을 때도 선명하게 보이도록 한다.

## 2. 글꼴

기본 글꼴은 **Pretendard**로 통일한다.

권장 굵기:

- 전체 제목: Pretendard Bold
- 패널 제목과 핵심 데이터 라벨: Pretendard SemiBold 또는 Bold
- 부제, 축, 범례, 표 본문: Pretendard Regular
- 각주: Pretendard Regular

Matplotlib 글꼴 후보는 다음 순서를 사용한다.

```python
FONT_CANDIDATES = (
    "Pretendard",
    "Apple SD Gothic Neo",
    "Noto Sans CJK KR",
    "Malgun Gothic",
)
```

Pretendard가 설치되지 않은 환경에서는 첫 번째로 발견되는 대체 글꼴을 사용한다. 재현성이 중요한 환경에서는 실행 전에 Pretendard를 설치하거나 코드에서 글꼴 파일을 등록한다.

## 3. 색상

```python
QQQ_COLOR = "#2F7DD3"           # 주요 데이터, QQQ
DEPOSIT_COLOR = "#8D8B85"       # 예금 및 보조 비교선
DEPLETION_COLOR = "#F06432"      # 고갈 지점
REFERENCE_COLOR = "#F59E0B"      # 기준선
BACKGROUND_COLOR = "#FFFFFF"     # 전체 및 축 배경
GRID_COLOR = "#DEDCD6"           # 그리드와 구분선
TEXT_COLOR = "#0B0B0B"           # 제목과 핵심 텍스트
SECONDARY_TEXT_COLOR = "#666666" # 부제
TICK_COLOR = "#777777"           # 축 제목과 눈금
FOOTNOTE_COLOR = "#777777"       # 각주

# 표 전용 색상
TABLE_HEADER_COLOR = "#2B4A75"
TABLE_HEADER_RULE_COLOR = "#7FB3D5"
TABLE_TEXT_COLOR = "#1E293B"
TABLE_MUTED_TEXT_COLOR = "#64748B"
TABLE_BORDER_COLOR = "#F0F2F5"
TABLE_STRIPE_COLOR = "#FAFBFC"
TABLE_HOVER_COLOR = "#EFF6FF"
TABLE_TOTAL_COLOR = "#E8EDF3"
TABLE_TOTAL_RULE_COLOR = "#94A3B8"
```

- 주요 데이터는 블루, 예금은 웜그레이를 사용한다.
- 강조색은 의미가 있을 때만 사용한다. 고갈은 오렌지, 기준선은 앰버로 고정한다.
- 동일한 의미의 데이터에는 모든 그래프와 표에서 같은 색을 사용한다.

## 4. 그래프 타이포그래피

| 요소 | 크기 | 굵기 | 색상 |
|---|---:|---|---|
| 전체 제목 | 21pt | Bold | `#0B0B0B` |
| 부제 | 15.5pt | Regular | `#666666` |
| 패널 제목 | 18pt | Bold | `#0B0B0B` |
| 축 제목 | 13.5pt | Regular | `#777777` |
| 축 눈금 | 12pt | Regular | `#777777` |
| 범례 | 11.5pt | Regular | 기본 텍스트색 |
| 데이터 라벨 | 13pt | Bold | 해당 데이터 색상 |
| 각주 | 13pt | Regular | `#777777` |

대표 제목과 부제 형식:

```text
성장 준비금 10년 잔액 변화 | QQQ vs 연 3% 예금
초기 준비금 1억원 · 매월 100만원 인출 · 10년
```

각주 형식:

```text
QQQ 배당·분할 및 환율 반영
※ 세금·수수료 제외
```

## 5. 그래프 구성

- 범례는 별도 영역으로 멀리 떼지 않고 첫 번째 그래프의 우측 상단에 둔다.
- 범례의 기준선 이름은 본문과 부제의 중복을 피하도록 `시작 준비금`으로 간결하게 쓴다.
- 그래프가 여러 패널이면 Y축 범위를 동일하게 유지해 직접 비교할 수 있게 한다.
- 수평 그리드만 사용하고 세로 그리드는 기본적으로 생략한다.
- 위·오른쪽·왼쪽 테두리는 제거하고 아래쪽 테두리만 연하게 남긴다.
- QQQ 선은 약 3.2pt, 예금 선은 약 2.6pt로 표시한다.
- 예금은 그레이 점선으로 표시해 색상 외에도 QQQ와 구분한다.
- 기준선은 가는 앰버 점선으로 표시한다.
- 데이터 라벨은 선과 겹치지 않게 배치하고, 흰색 또는 오프화이트 배경을 둘 수 있다.
- 같은 높이에서 고갈되는 계열의 라벨은 세로 오프셋을 달리해 겹치지 않게 한다.
- 제목과 첫 번째 패널 사이에는 부제와 최소한의 여백만 둔다.
- 여러 패널 사이의 간격은 기본값보다 약 10% 줄여 세로 길이를 과도하게 늘리지 않는다.
- 그래프 영역의 좌우 여백은 각각 4%를 기본값으로 사용해 균형을 맞춘다.
- 왼쪽 위에는 `대도시 연구실` 출처 표시를 9pt 회색으로 작게 넣는다.

권장 Matplotlib 설정:

```python
fig.patch.set_facecolor(BACKGROUND_COLOR)
ax.set_facecolor(BACKGROUND_COLOR)
ax.grid(axis="y", color=GRID_COLOR, linewidth=0.9)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.spines["bottom"].set_color(GRID_COLOR)
ax.tick_params(axis="both", colors=TICK_COLOR, labelsize=12, length=0)
```

## 6. 표 구성

표의 기준 구현은 `mortgage_calculator/mortgage_calculator.ipynb`로 한다. 다른 일반 규칙과 충돌하면 표에 대해서는 이 절의 규격을 우선한다.

### 6.1 기본 레이아웃

- 표는 최대 너비 `700px`의 래퍼 안에 배치한다.
- 래퍼 바깥 여백은 위 `12px`, 아래 `28px`를 기본값으로 한다.
- 래퍼에는 `1px solid #F0F2F5` 테두리와 `12px` 모서리 반경을 적용한다.
- 좁은 화면에서는 내용이 찌그러지지 않도록 `overflow-x: auto`를 사용한다.
- 표 너비는 `100%`, `border-collapse: separate`, `border-spacing: 0`으로 설정한다.
- 표 배경은 흰색을 사용하며 과한 그림자는 넣지 않는다.

### 6.2 글꼴과 숫자

- 기본 글꼴은 Pretendard이며 시스템 글꼴을 대체 후보로 둔다.
- 표 본문과 헤더의 기본 크기는 `13px`로 한다.
- 숫자 폭이 행마다 흔들리지 않도록 `font-variant-numeric: tabular-nums`를 사용한다.
- 금액과 수치는 오른쪽 정렬한다.
- 상환 방식, 연차, 사례명처럼 행을 식별하는 첫 번째 열은 가운데 정렬한다.
- 요약표의 첫 번째 열은 `font-weight: 600`으로 강조한다.
- 상세표의 첫 번째 열은 `#64748B`, Regular로 두어 금액보다 시각적 우선순위를 낮춘다.

### 6.3 제목과 캡션

| 요소 | 크기 | 굵기 | 색상 | 여백 |
|---|---:|---:|---|---|
| 표 제목 | 20px | 700 | `#0F172A` | `30px 0 8px` |
| 표 캡션 | 12px | 400 | `#64748B` | `0 0 10px` |
| 표 헤더 | 13px | 700 | 흰색 | 셀 내부 `8px 12px` |
| 표 본문 | 13px | 400 | `#1E293B` | 셀 내부 `7px 12px` |

- 제목은 `{상환 방식} 연도별 내역`처럼 표의 내용을 바로 알 수 있게 쓴다.
- 캡션은 `상환 방식 │ 대출금액 │ 금리 │ 기간`처럼 핵심 조건만 한 줄로 표시한다.
- 같은 정보를 제목과 캡션에서 반복하지 않는다.

### 6.4 헤더와 본문 행

- 헤더 배경은 `#2B4A75`, 텍스트는 흰색으로 한다.
- 헤더 아래에는 `2px solid #7FB3D5` 구분선을 둔다.
- 긴 표를 노트북에서 볼 때는 헤더에 `position: sticky; top: 0`을 적용할 수 있다.
- 본문 행 구분선은 `1px solid #F0F2F5`로 얇게 처리한다.
- 짝수 행에는 `#FAFBFC` 배경을 적용한다.
- 노트북에서 마우스를 올린 행은 `#EFF6FF`로 표시할 수 있다. 캡처용 정적 표에서는 hover 효과에 의존하지 않는다.
- 마지막 일반 행의 아래쪽 테두리는 제거한다.
- 텍스트와 금액은 줄바꿈하지 않도록 `white-space: nowrap`을 기본값으로 한다.

### 6.5 합계 행

- 합계는 별도 행으로 표의 마지막에 추가한다.
- 합계 행 배경은 `#E8EDF3`, 위쪽 구분선은 `2px solid #94A3B8`로 한다.
- 합계 행 텍스트는 `#0F172A`, `font-weight: 700`으로 표시한다.
- `합계 (30년)`처럼 합계의 기준 기간을 첫 번째 열에 함께 적는다.
- 단순히 마지막 데이터 행을 강조하지 말고, 계산된 합계 행일 때만 이 스타일을 사용한다.

### 6.6 열 너비

5열 연도별 상환표는 다음 비율을 기본값으로 사용한다.

| 열 | 권장 너비 |
|---|---:|
| 연차 | 9% |
| 연간 납입액 | 20% |
| 상환 원금 | 22% |
| 납부 이자 | 22% |
| 대출 잔액 | 27% |

- 열 수나 내용이 달라지면 비율은 조정하되, 금액 열에 충분한 너비를 먼저 배정한다.
- 열 너비를 고정할 때는 `table-layout: fixed`를 사용한다.

### 6.7 데이터 준비

- `DataFrame.to_html(index=False, border=0)`을 기본 출력 방식으로 사용한다.
- 원본 DataFrame은 계산 가능한 숫자 상태로 유지하고, 화면 출력용 복사본에서만 금액 문자열로 변환한다.
- 금액 단위와 자릿수는 열 전체에서 통일한다.
- 요약표와 상세표는 별도의 CSS 클래스(`summary-table`, `annual-table`)로 구분한다.
- 블로그용 표에는 핵심 열만 넣고 전체 상세 데이터는 CSV로 분리한다.

권장 HTML 구조:

```python
display_table = source_table.copy()
for column in display_table.columns[1:]:
    display_table[column] = display_table[column].map(format_korean_currency)

table_html = display_table.to_html(
    index=False,
    border=0,
    classes="loan-table annual-table",
)
display(HTML(f'<div class="loan-table-wrap">{table_html}</div>'))
```

권장 핵심 CSS:

```css
.loan-table-wrap {
    max-width: 700px;
    margin: 12px 0 28px;
    overflow-x: auto;
    border: 1px solid #f0f2f5;
    border-radius: 12px;
}
.loan-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    color: #1e293b;
}
.loan-table thead th {
    padding: 8px 12px;
    background: #2b4a75;
    border-bottom: 2px solid #7fb3d5;
    color: white;
    font-weight: 700;
    text-align: right;
    white-space: nowrap;
}
.loan-table tbody td {
    padding: 7px 12px;
    border-bottom: 1px solid #f0f2f5;
    background: white;
    text-align: right;
    white-space: nowrap;
}
.loan-table thead th:first-child,
.loan-table tbody td:first-child { text-align: center; }
.loan-table tbody tr:nth-child(even) td { background: #fafbfc; }
.loan-table tbody tr:hover td { background: #eff6ff; }
.loan-table tbody tr:last-child td { border-bottom: 0; }
.annual-table tbody tr:last-child td {
    background: #e8edf3;
    border-top: 2px solid #94a3b8;
    color: #0f172a;
    font-weight: 700;
}
```

## 7. 숫자와 문구

- 원화는 읽기 쉬운 `억원`, `만원` 단위로 표시한다.
- 예: `1억원`, `1억 9,023만원`, `100만원`.
- 기간은 `6년 5개월`처럼 한글 단위를 사용한다.
- 고갈되지 않은 경우에는 `고갈되지 않음`으로 명시한다.
- 비교 사례명은 `최저 사례`, `중간 사례`, `최고 사례`처럼 동일한 문법으로 통일한다.
- 제목과 라벨에서는 불필요한 전문 용어와 긴 설명을 피한다.

## 8. 이미지 출력

- PNG를 기본 형식으로 사용한다.
- `dpi=200`을 기본값으로 사용한다.
- 저장할 때 배경색을 명시해 투명 배경이나 흰색 불일치를 방지한다.
- 블로그에 올리기 전에 제목, 범례, 데이터 라벨, 각주가 잘리지 않았는지 원본 크기로 확인한다.

```python
fig.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight",
    facecolor=BACKGROUND_COLOR,
)
```

## 9. 최종 점검

- Pretendard가 실제로 적용됐는가?
- 제목, 부제, 축, 범례, 각주의 크기가 규격과 일치하는가?
- QQQ는 블루, 예금은 그레이로 표시됐는가?
- 축 범위와 단위가 비교에 적합한가?
- 데이터 라벨이 선이나 다른 글자와 겹치지 않는가?
- 블로그에서 축소해도 숫자와 각주를 읽을 수 있는가?
- 세금, 수수료, 배당, 환율 등 계산 전제가 각주에 적혀 있는가?
- 표의 숫자 열이 오른쪽 정렬되고 고정폭 숫자로 표시되는가?
- 표의 첫 번째 식별 열과 금액 열의 시각적 위계가 구분되는가?
- 합계 행이 실제 합계일 때만 별도 배경과 굵기로 강조되는가?
- 좁은 화면에서 표가 찌그러지지 않고 가로 스크롤되는가?
- 화면 표시용 금액 문자열과 계산용 숫자 데이터가 분리되어 있는가?
