import pandas as pd
################# [ 여기 박스 안의 a,b만 수정하며 테스트해보세요~ ] ######################
a=0.5    #경고비 (최소금액~최대금액:0~100%로 봤을때 몇%를 경고금액으로 둘것인가?)
b=0.7    #낭비비 (경고금액을 넘었을 때 얼마나 절약하지 않을것인가?)
########## [ 함수들] ##########################################################################
def PastYearAvg(): #(실제) 기존 3단 누진세 방법 시행시 가구당 평균 연간전기요금
    csv_3elecbill="csv/15~23년 전력통계.csv"
    df_3elecbill=pd.read_csv(csv_3elecbill)
    df_3elecbill['가구당 1년 전기요금(원)'] = df_3elecbill['가구당 1년 전기요금(원)'].str.replace(",", "").astype(int)
    df_3elecbill['가구당 1년전력소비량(kWh)'] = df_3elecbill['가구당 1년전력소비량(kWh)'].str.replace(",", "").astype(int)
    past_year_bill = df_3elecbill[['연도(년)','가구당 1년 전기요금(원)','가구당 1년전력소비량(kWh)']] # 2015~2023년 전기요금
    print(past_year_bill)
    return past_year_bill
def AvrHourElec(year):  #해당연도 가구당 1시간 평균 소비전력 (kWh/h)
    csv="csv/15~23년 전력통계.csv"
    df=pd.read_csv(csv)
    # print(df.head())
    df_watt=df.loc[df['연도(년)']==year, '가정용판매전력량(MWh)'].values[0]
    df_popu=df.loc[df['연도(년)']==year, '가정용수용호수(호)'].values[0]
    watt=int(str(df_watt).replace(",",""))
    popu=int(str(df_popu).replace(",",""))
    Kwh_per=(watt*1000)/popu/365/24 #가구당 1시간 평균 소비전력 (kWh/h)
    return Kwh_per
def RealToSMP(warn_rate=0.5,weast_rate=0.5): # SEB 시행시 전기요금 및 사용량
    year_cost = {2020: {"cost": 0, "power": 0}, 
             2021: {"cost": 0, "power": 0}, 
             2022: {"cost": 0, "power": 0}, 
             2023: {"cost": 0, "power": 0}} # 딕셔너리로 저장
    csv_smp = "csv/smp_land_merged.csv"
    df_smp = pd.read_csv(csv_smp)
    df_smp['구분']=pd.to_datetime(df_smp['구분'],format='%Y%m%d')#YYYYMMDD형식으로 바꾸기  

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
    result = pd.DataFrame.from_dict(year_cost, orient='index')
    result.reset_index(inplace=True)
    result.columns = ["연도(년)", "전기요금(원)", "소모전력(kWh)"]  # 컬럼명 변경
    
    result['전기요금(원)'] = result['전기요금(원)'].astype(int)  # 전기요금은 정수로 변환
    result['소모전력(kWh)'] = result['소모전력(kWh)'].astype(int)  # 전기요금은 정수로 변환
    print(result)
    return result
########## [ 데이터들 ] #######################################################################
#실제 전기 요금
df_3elecbill=PastYearAvg()
df_RTSMP=RealToSMP(a,b)
#SMP 세상 전기요금 (경고비:낭비비=0:100)