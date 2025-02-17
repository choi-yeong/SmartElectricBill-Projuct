# SmartElectricBill Project⚡

실시간전기요금확인 요금청구 어플리케이션

<!--
프로그래밍 입문 한달차 첫 프로젝트 작품.
-->
## 📝프로젝트 소개

* 주제 : 실시간전기요금데이터를 이용한 전력낭비 문제 해결.
* 기획의도 : 전력사용량, 전기요금 절감 및 전력예비율 조절을 위한 실시간 전기요금제의 실용성을 증명하기 위함.
* 기간 : 2025.02.05~ 2025.02.17 (12일) [17일 당일마감]


## 🔨사용한 기술

|카테고리|기술|
|:-|:-:|
|언어|파이썬|
|데이터수집|리퀘스트(request), 뷰티풀수프(Beatuifulsoup)|
|전처리과정|판다스(Pandas),넘파이(Numpy)|
|도표시각화|맷플롯립(matplotlib),씨본(Seaborn)|
|UI시각화|티킨터(Tkinter), FigureCanvasTkAgg(피규어캔버스)|

## ❓주요기술 채택이유
* 대부분 기술은 공부한 내용을 익히기 위해 사용.

## 🙋‍♂️내가 구현 기능

### 백엔드 (데이터 부분)
* 데이터 전처리
  * 과거 SMP가격데이터 csv파일을 호출하고 날짜와 요금 단위로 저장 및 관리
  * 과거 연간 전력판매량,수용호수,판매수익 csv파일을 호출하고 월단위로 기록하여 비교군 제작

### 프론트엔드 (프로토타입 부분)
* 데이터 수집
  * 실시간 SMP요금 데이터를 전력거래소 사이트를 스크래핑하여 호출.
* 데이터 전처리
  * 최근 7일간 일일 최대, 최소 요금을 불러오고 이상점(outlier)의 영향을 줄이기 위해 최대값의 평균, 최소값을 평균을 Tkinter에 표기
  * 최근 8시간동안 실시간 SMP요금을 꺽은선 그래프로 도식화하여 Tkinter에 FigureCanvasTkAgg로 조회할 수 있는 기능
  * 경고금액 설정 및 경고금액과 현재 요금을 비교하여 경고창을 띄우는 기능


## 🌲프로젝트 구조

```python
*
|-- csv          # csv 데이터 파일들 보관
|-- 자료         # 프로젝트를 진행하는데 참고 및 도움이 된 자료들 보관
|- ppt_plot.py      # 경고비와 낭비비를 임의로 설정하며 그래프로 나타내는 기능
|- heatmapmaker.py  # heatmap 그래프를 만드는 기능
|- Prototype.py     # 실전에서 어떻게 사용될지 예시를 보여주기 위해 Tkinter를 이용해 인터페이스를 구현함
`- SmartElectric.py # 프로젝트에 필요한 각종 함수를 모아둔 모듈용 파일
```
