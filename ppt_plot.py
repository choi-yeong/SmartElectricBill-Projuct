# 이 곳은 PPT에 올라갈 자료들을 시각화 하는 파일입니다.
# 함부로 수정하지마세요~
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager,rc
import seaborn as sns
import numpy as np



################# [ 여기 박스 안의 a,b만 수정하며 테스트해보세요~ ] ######################
a=0.5    #경고비 (최소금액~최대금액:0~100%로 봤을때 몇%를 경고금액으로 둘것인가?)
b=0.7    #낭비비 (경고금액을 넘었을 때 얼마나 절약하지 않을것인가?)
#############################################################################################
# 한글폰트 적용
path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 맑은 고딕 폰트 경로
font = font_manager.FontProperties(fname=path).get_name()
rc('font',family=font)
# csv 파일 불러오기
smp="csv/smp_land_merged.csv"
df_smp=pd.read_csv(smp)
df_smp['구분']=pd.to_datetime(df_smp['구분'],format='%Y%m%d')#YYYYMMDD형식으로 바꾸기 
real="csv/15~23년 전력통계.csv"
real=pd.read_csv(real)
########## [ 함수들] ##########################################################################
def PastYearAvg(): #(실제) 기존 3단 누진세 방법 시행시 가구당 평균 연간전기요금
    real['가구당 1년 전기요금(원)'] = real['가구당 1년 전기요금(원)'].str.replace(",", "").astype(int)
    real['가구당 1년전력소비량(kWh)'] = real['가구당 1년전력소비량(kWh)'].str.replace(",", "").astype(int)
    past_year_bill = real[['연도(년)','가구당 1년 전기요금(원)','가구당 1년전력소비량(kWh)']] # 2015~2023년 전기요금
    return past_year_bill
def AvrHourElec(year):  #해당연도 가구당 1시간 평균 소비전력 (kWh/h)
    df_watt=real.loc[real['연도(년)']==year, '가정용판매전력량(MWh)'].values[0]
    df_popu=real.loc[real['연도(년)']==year, '가정용수용호수(호)'].values[0]
    watt=int(str(df_watt).replace(",",""))
    popu=int(str(df_popu).replace(",",""))
    Kwh_per=(watt*1000)/popu/365/24 #가구당 1시간 평균 소비전력 (kWh/h)
    return Kwh_per
def RealToSMP(warn_rate=0.5,weast_rate=0.5): # SEB 시행시 전기요금 및 사용량
    year_cost = {2020: {"cost": 0, "power": 0}, 
             2021: {"cost": 0, "power": 0}, 
             2022: {"cost": 0, "power": 0}, 
             2023: {"cost": 0, "power": 0}} # 딕셔너리로 저장 
    warn_cost=0 #경고금액 (경고비에 비례한 경고금액이다.)
    max_cost=0
    min_cost=999
    for date in df_smp['구분']:  # 모든 날짜를 반복한다(YYYYMMDD)
        year = int(str(date)[:4])  # 연도 추출
        elec_hour_avr_year = AvrHourElec(year)  # 당해 시간당 평균 전력 사용량
        if year not in [2020, 2021, 2022, 2023]:
            continue  # 2020~2023년도가 아니면 넘어감
        # 해당 날짜를 기준으로 최근 7일 간의 데이터를 추출
        date_range = pd.date_range(end=date, periods=7).strftime('%Y%m%d').tolist()
        date_range = pd.to_datetime(date_range, format='%Y%m%d')
        # 최근 7일 간의 데이터를 필터링
        recent_data = df_smp[df_smp['구분'].isin(date_range)]
        recent_min = recent_data.loc[:,'최소'].isin(date_range)
        recent_max = recent_data.loc[:,'최대'].isin(date_range)
        for i in recent_max:
            if max_cost<i:
                max_cost=i
        for i in recent_min:
            if min_cost>i:
                min_cost=i
        warn_cost=(warn_rate*(max_cost-min_cost))+min_cost

        for hour in range(1, 25):  # 1~24h를 반복한다.
            hour_column = f"{hour}h"
            smp_price = df_smp.loc[df_smp['구분'] == date, hour_column].values[0]
            # watt_hour = smp_price * elec_hour_avr_year
            if smp_price>warn_cost:
                year_cost[year]["cost"] += smp_price * elec_hour_avr_year*weast_rate  # 전기요금 합산
                year_cost[year]["power"] += elec_hour_avr_year*weast_rate  # 소모전력 합산
            else:
                year_cost[year]["cost"] += smp_price * elec_hour_avr_year  # 전기요금 합산
                year_cost[year]["power"] += elec_hour_avr_year  # 소모전력 합산

    # 딕셔너리 -> 데이터프레임 변환
    result_2d = pd.DataFrame.from_dict(year_cost, orient='index')
    result_2d.reset_index(inplace=True)
    result_2d.columns = ["연도(년)", "전기요금(원)", "소모전력(kWh)"]  # 컬럼명 변경
    
    result_2d['전기요금(원)'] = result_2d['전기요금(원)'].astype(int)  # 전기요금은 정수로 변환
    result_2d['소모전력(kWh)'] = result_2d['소모전력(kWh)'].astype(int)  # 전기요금은 정수로 변환
    return result_2d
def heat_df():
    waste_rates=np.round(np.arange(0,0.01,0.01),2)
    warn_rates=np.round(np.arange(0,0.01,0.01),2)
    heat_dict={}
    for warn in warn_rates:
        print(f"경고비 :{warn} 분석중")
        heat_dict[warn]={waste: RealToSMP(warn,waste).loc['소모전력(kWh)'].sum() for waste in waste_rates} # 수식을 제대로 짜야함.
    df=pd.DataFrame.from_dict(heat_dict)
    print(df.head())
    df.index.name = "경고비"
    df.columns.name = "낭비비"
    df.to_csv("heatmap_data.csv",encoding="utf-8-sig")
    return 0
########## [ 데이터들 ] #######################################################################
#실제 전기 요금
# df_3elecbill=PastYearAvg()
# df_RTSMP=RealToSMP(a,b)
#SMP 세상 전기요금 (경고비:낭비비=0:100)

# heat_df()

########## [ 수식 구현 ] ######################################################################


########## [ 그래프 구현 ] ##################################################################
############ 실제 연도당 전기요금과 SMP적용시 전기요금(경고비,낭비비:0%,100%)############
# # 데이터 준비
# df_filtered = df_3elecbill[df_3elecbill['연도(년)'].between(2020, 2023)]
# # 그래프 그리기
# fig, ax1 = plt.subplots(figsize=(10, 6))

# # 첫 번째 y축: 실제 전기요금과 SMP 전기요금 (선 그래프)
# ax1.plot(df_filtered['연도(년)'], df_filtered['가구당 1년전력소비량(kWh)'], 
#          marker='o', linestyle='-', color='r', label='실제 3단누진제 사용전력[kWh]')
# ax1.plot(df_RTSMP['연도(년)'],df_RTSMP['소모전력(kWh)'],
#          marker='x', linestyle='-', color='b', label='가상 SMP시행시 사용전력[kWh]')
# ax1.set_xlabel('연도')
# ax1.set_ylabel('전기요금/소모전력 (kWh)')
# ax1.tick_params(axis='y', labelcolor='r')
# # 두 번째 y축: 전기요금 (막대그래프)
# ax2 = ax1.twinx()  # 두 번째 y축 추가
# ax2.bar(df_filtered['연도(년)']-0.125, df_filtered['가구당 1년 전기요금(원)']/1000, 
#         width=0.25, color='r', label='실제 전기요금[천원]', align='center',alpha=0.5)
# ax2.bar(df_RTSMP['연도(년)']+0.125, df_RTSMP['전기요금(원)']/1000, 
#         width=0.25, color='b', label='SMP 전기요금[천원]', align='center',alpha=0.5)

# ax2.set_ylabel('전기요금 (천원)')
# ax2.tick_params(axis='y', labelcolor='purple')

# # 범례 추가
# ax1.legend(loc='upper left')
# ax2.legend(loc='upper right')
# plt.xticks(df_filtered['연도(년)'])
# # 그래프 스타일 설정
# plt.title('2020~2023년 가구당 연간 전기요금 및 전력사용량')
# ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
# # 그래프 표시
# plt.show()


###################################################################################################################
