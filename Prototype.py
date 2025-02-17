
import requests, SmartElectric,time
import tkinter as tk
import tkinter.messagebox as messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bs4 import BeautifulSoup
from datetime import datetime
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

def window():
    def add_red_line():
        """경고 요금선을 추가하는 함수"""
        try:
            set_money_value = float(setmoney_ent.get())  # 입력값을 숫자로 변환

            # 기존 경고선 삭제
            for line in ax.lines:
                if line.get_color() == 'r':  # 경고선(빨간색)만 삭제
                    line.remove()

            # 새로운 경고선 추가
            xlim = ax.get_xlim()  
            ax.plot([xlim[0], xlim[1]],  
                    [set_money_value, set_money_value],  
                    'r--')  
            ax.set_xlim(xlim)  
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.set_title("SMP (전기요금 변화)")
            ax.set_xlabel("시간 (hour)")
            ax.set_ylabel("요금 (원/kWh)")
            if set_money_value>max(smp):
                ax.set_ylim(min(smp) - 1, set_money_value + 1)  # 최소값보다 1 낮게, 최대값보다 1 높게 설정
            elif set_money_value<min(smp):
                ax.set_ylim(set_money_value -1, max(smp) + 1)  # 최소값보다 1 낮게, 최대값보다 1 높게 설정
            else:
                ax.set_ylim(min(smp) - 1, max(smp) + 1)  # 최소값보다 1 낮게, 최대값보다 1 높게 설정
            if smp[7]>set_money_value:
                time.sleep(0.5)
                messagebox.showwarning("경고","현재 전기요금이 너무 비쌉니다.")
                
            canvas.draw()

        except ValueError:
            print("유효한 숫자를 입력하세요.")
        except Exception as e:
            print(f"오류 발생: {e}")

    def refresh_data(week_max_ent, week_min_ent):
        """데이터를 새로고침하고, 그래프와 UI 업데이트"""
        nonlocal smp, avg_max, avg_min

        now_hour = int(datetime.now().strftime("%H"))
        if now_hour == 0:
            now_hour = 24

        url = "https://new.kpx.or.kr/smpInland.es?mid=a10606080100&device=pc#main"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        # 최신 데이터 가져오기
        smp.clear()  # 기존 데이터 삭제 후 최신 데이터 반영
        for i in range(now_hour - 7, now_hour + 1):
            smp.append(float(soup.select_one(f"#contents_body > div.content_style > div.conTableGroup.scroll > table > tbody > tr:nth-child({i}) > td:nth-child(8)").text.strip()))

        before_max = []
        before_min = []
        for i in range(2, 9):
            before_max.append(float(soup.select_one(f"#contents_body > div.content_style > div.conTableGroup.scroll > table > tbody > tr:nth-child(25) > td:nth-child({i})").text.strip()))
            before_min.append(float(soup.select_one(f"#contents_body > div.content_style > div.conTableGroup.scroll > table > tbody > tr:nth-child(26) > td:nth-child({i})").text.strip()))

        avg_max = round(sum(before_max) / len(before_max), 2)  
        avg_min = round(sum(before_min) / len(before_min), 2)  

        # UI 업데이트
        week_max_ent.config(state="normal")
        week_max_ent.delete(0, tk.END)
        week_max_ent.insert(0, avg_max)
        week_max_ent.config(state="readonly")

        week_min_ent.config(state="normal")
        week_min_ent.delete(0, tk.END)
        week_min_ent.insert(0, avg_min)
        week_min_ent.config(state="readonly")

        # 그래프 갱신
        ax.clear()
        ax.set_title("SMP (전기요금 변화)")
        ax.plot(range(now_hour - 7, now_hour + 1), smp, marker="o", linestyle="-", color="burlywood")
        
        for i, value in enumerate(smp):  # 마커 위에 텍스트 표기
            ax.text(now_hour - 7 + i, value+0.2, f"{value:.2f}", fontsize=7, ha='center', va='bottom', color="black")
        
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_xlabel("시간 (hour)")
        ax.set_ylabel("요금 (원/kWh)")
        ax.set_ylim(min(smp) - 1, max(smp) + 1)  # 최소값보다 1 낮게, 최대값보다 1 높게 설정
        add_red_line()
        canvas.draw()

    smp = []
    avg_max = 0
    avg_min = 0
    
    root = tk.Tk()
    root.title("SmartElectricBill")
    root.geometry("650x625")

    price_frame = tk.Frame(root, bd=2, relief="solid", padx=5, pady=5)
    price_frame.grid(row=0, pady=10, padx=10,sticky='w')

    maxmoney_lab = tk.Label(price_frame, text="당월 누적 전기 요금")
    maxmoney_lab.grid(row=0, column=0, padx=5, pady=5)

    maxmoney_ent = tk.Entry(price_frame, width=20)
    maxmoney_ent.insert(0, "32,923")
    maxmoney_ent.config(state="readonly")
    maxmoney_ent.grid(row=0, column=1, padx=5)

    frame_container = tk.Frame(root)
    frame_container.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky="w")

    week_frame = tk.Frame(frame_container, bd=2, relief="solid", padx=5, pady=5)
    week_frame.grid(row=0, column=0, padx=10,sticky='w')

    warn_frame = tk.Frame(frame_container, bd=2, relief="solid", padx=5, pady=5)
    warn_frame.grid(row=0, column=1, padx=10, sticky='w')

    week_max_lab = tk.Label(week_frame, text="주간 최대 전기 요금")
    week_max_lab.grid(row=0, column=0, padx=5, pady=5)

    week_max_ent = tk.Entry(week_frame, width=20, background="white")
    week_max_ent.grid(row=0, column=1, padx=5)
    week_max_ent.insert(0, avg_max)
    week_max_ent.config(state="readonly")

    week_min_lab = tk.Label(week_frame, text="주간 최소 전기 요금")
    week_min_lab.grid(row=1, column=0, padx=5, pady=5)

    week_min_ent = tk.Entry(week_frame, width=20, background="white")
    week_min_ent.grid(row=1, column=1, padx=5)
    week_min_ent.insert(0, avg_min)
    week_min_ent.config(state="readonly")

    setmony_lab = tk.Label(warn_frame, text="경고 요금 설정")
    setmony_lab.grid(row=0, column=0, padx=5, pady=5)

    setmoney_ent = tk.Entry(warn_frame, width=20, background="white")
    setmoney_ent.grid(row=0, column=1, padx=5)

    setmoney_btn = tk.Button(warn_frame, text="확인", command=add_red_line)  
    setmoney_btn.grid(row=0, column=2, padx=5)

    refresh_btn = tk.Button(warn_frame, text="새로고침", command=lambda: refresh_data(week_max_ent, week_min_ent))
    refresh_btn.grid(row=1, column=1, padx=5)

    fig = Figure(figsize=(7, 4.5), dpi=100)
    global ax
    ax = fig.add_subplot(111)
    ax.set_title("SMP (전기요금 변화)")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlabel("시간 (hour)")
    ax.set_ylabel("요금 (원/kWh)")

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=4, pady=10, sticky="s")

    refresh_data(week_max_ent, week_min_ent)

    root.mainloop()

window()
