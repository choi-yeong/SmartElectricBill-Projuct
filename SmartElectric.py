import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager, rc
import seaborn as sns
import numpy as np

################# [ 여기 박스 안의 a,b만 수정하며 테스트해보세요~ ] ######################
a = 0.5  # 경고비 (최소금액~최대금액:0~100%로 봤을때 몇%를 경고금액으로 둘것인가?)
b = 0.7  # 낭비비 (경고금액을 넘었을 때 얼마나 절약하지 않을것인가?)
########################################################################################

# 한글폰트 적용
path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 맑은 고딕 폰트 경로
font = font_manager.FontProperties(fname=path).get_name()
rc('font', family=font)

# CSV 파일 불러오기
smp = "csv/smp_land_merged.csv"  # 2020~2023년 SMP 가격들 merge한 csv파일로 불러옴.
df_smp = pd.read_csv(smp, parse_dates=['구분'])  # '구분' 컬럼을 datetime으로 변환

real = "csv/15~23년 전력통계.csv" # 2020~2023년 전력 통계 파일(판매량, 수용호수, 전력사용량)
real = pd.read_csv(real)

def AvrHourElec(year): # 20~23년 시간당 평균 전력소비량.
    row = real.loc[real['연도(년)'] == year]
    if row.empty:
        return 0  # 데이터가 없으면 0 반환

    watt = int(str(row['가정용판매전력량(MWh)'].values[0]).replace(",", ""))
    popu = int(str(row['가정용수용호수(호)'].values[0]).replace(",", ""))
    return (watt * 1000) / popu / 365 / 24

def RealToSMP(warn_rate=0.5, weast_rate=0.5): #SEB 시행 시 전기요금 및 사용량 계산
    year_cost = {year: {"cost": 0, "power": 0} for year in range(2020, 2024)}

    for date in df_smp['구분']:
        year = date.year
        if year not in year_cost:
            continue

        elec_hour_avr_year = AvrHourElec(year)
        start_date = date - pd.Timedelta(days=6)  # 최근 7일(오늘 포함)
        recent_data = df_smp[df_smp['구분'].between(start_date, date)]  # 안전한 필터링 방법

        if recent_data.empty: # 최근 7일이 없으면 무시
            continue 

        max_cost = recent_data["최대"].max() #최근 7일 중 가장 높은 값을 최대에 저장
        min_cost = recent_data["최소"].min() #최근 7일 중 가장 낮은 값을 최소에 저장
        warn_cost = (warn_rate * (max_cost - min_cost)) + min_cost #최대값과 최소값을 0~100%로 두고 경고비%에 따른 경고금액을 설정

        for hour in range(1, 25): #날짜당 시간별로 반복한다.
            hour_column = f"{hour}h" #칼럼 문자열을 맞추기 위한 작업
            smp_price_series = df_smp.loc[df_smp['구분'] == date, hour_column] #해당 행(날짜)와 칼럼(시간)에 맞는 값(smp값)을 찾는다.

            if smp_price_series.empty: #없으면 무시
                continue

            smp_price = smp_price_series.values[0] 

            if smp_price > warn_cost: #만약 smp가격이 경고비보다 높다면
                year_cost[year]["cost"] += smp_price * elec_hour_avr_year * weast_rate #낭비비율에 따라 곱해준다.
                year_cost[year]["power"] += elec_hour_avr_year * weast_rate
            else:
                year_cost[year]["cost"] += smp_price * elec_hour_avr_year #smp 가격이 경고비보다 낮다면 그냥 평소대로 100% 쓴다.
                year_cost[year]["power"] += elec_hour_avr_year

    # 딕셔너리 → 데이터프레임 변환
    result_df = pd.DataFrame.from_dict(year_cost, orient='index').reset_index()
    result_df.columns = ["연도(년)", "전기요금(원)", "소모전력(kWh)"] # date, cost, power를 한글화함

    return result_df.astype({"전기요금(원)": int, "소모전력(kWh)": int}) # 각 value의 반환 데이터형태를 int로 함.

def heat_df(): #해당연도 얼마나 전력을 아꼈는가?
    """ 경고비(warn_rate)와 낭비비(weast_rate)에 따른 전력 소비량 변화 """
    waste_rates = np.round(np.arange(0.0, 1.1, 0.1), 2)
    warn_rates = np.round(np.arange(0.0, 1.1, 0.1), 2)
    heat_dict = {waste: {} for waste in waste_rates}  # 변경된 딕셔너리 구조

    for warn in warn_rates:
        print(f"경고비 {warn} 분석 중...")
        for waste in waste_rates:
            print(f"경고비 {warn}, 낭비비 {waste} 분석 중...")
            result = RealToSMP(warn, waste) #0부터 1까지 경고비와 낭비비를 대입하며 비교
            heat_dict[waste][warn] = result['소모전력(kWh)'].sum() #결과의 1년치소모전력의 합을 반환후 변수저장

    df_heat = pd.DataFrame.from_dict(heat_dict, orient='index') #저장한 변수를 dataframe으로 저장한다.
    df_heat.index.name = "낭비비"
    df_heat.columns.name = "경고비"
    df_heat.to_csv("heatmap_data_2023.csv", encoding="utf-8-sig")

    return df_heat


# df_result = heat_df()
# print(df_result.head())

def comp():
    waste_rates = np.round(np.arange(0.0, 1.1, 0.1), 1)  # np.float64 대신 float로
    warn_rates = np.round(np.arange(0.0, 1.1, 0.1), 1)  # np.float64 대신 float로
    comp_dict = {waste: {} for waste in waste_rates}
    
    # 각 연도별 데이터프레임을 읽어옵니다.
    # df1 = pd.read_csv("heatmap_data_2020.csv", index_col=0)
    # df2 = pd.read_csv("heatmap_data_2021.csv", index_col=0)
    df3 = pd.read_csv("heatmap_data_2022.csv", index_col=0)
    # df4 = pd.read_csv("heatmap_data_2023.csv", index_col=0)
    df3.columns = pd.to_numeric(df3.columns, errors='coerce')  # 변환할 수 없는 값은 NaN으로 처리
    print("df 컬럼 타입:", df3.columns)

    # df1의 인덱스도 float로 변환 (필요한 경우)
    df3.index = df3.index.astype(float)
    for waste in waste_rates:
        print("낭비비",waste)
        for warn in warn_rates:
            print("낭비비",waste,"경고비",waste,"분석중")
            comp_dict[waste][warn]=round(df3.loc[warn,waste]/5673,2)
    df_comp = pd.DataFrame.from_dict(comp_dict, orient='index')
    df_comp.index.name = "낭비비"
    df_comp.columns.name = "경고비"
    df_comp.to_csv("comp_data_2022.csv", encoding="utf-8-sig")

    return df_comp
