
 # City Weather Dashboard HMI (Agent-style Programming)

Dashboard นี้ถูกออกแบบให้ใช้เป็นตัวอย่าง **Agent Programming + HMI Dashboard**
 โดยใช้ข้อมูลจริงจาก **Public API (Open-Meteo)** แทนการใช้ Sensor จริง

ฟีเจอร์ที่ทำให้ตรงกับเงื่อนไขโจทย์:

1. **หน้าจอ Dashboard HMI**
    - ใช้ `Streamlit` ในการสร้างหน้าเว็บ Dashboard
    - แสดงค่าตัวแปรสำคัญในรูปแบบการ์ด (metric) คล้าย HMI

2. **แสดงผลการตรวจวัดของเมือง (Real Public Data)**
    - ใช้ Open-Meteo Public API ดึงข้อมูลอากาศจริงแบบรายชั่วโมง
    - ตัวแปรที่ใช้ (อย่างน้อย 4–5 ตัวแปร)
      - Temperature (°C)
      - Humidity (%RH)
      - Apparent Temperature (°C)
      - Wind speed 10 m (m/s)
      - Surface Pressure (hPa)
      - Precipitation (mm)

3. **Drop-down Menu สำหรับเลือกเมือง**
    - เลือกเมืองได้จากเมนูด้านซ้าย เช่น Bangkok, Chiang Mai, Khon Kaen, Phuket
    - เมื่อเปลี่ยนเมือง ระบบจะดึงข้อมูลจริงของเมืองนั้นมาแสดง

4. **Plot Graph (มี Timestamp)** 
    - กราฟ Time-series ระหว่าง
      - Temperature (°C)
      - Humidity (%RH)
    - แกน x คือเวลา (Timestamp)
    - สามารถเลือกช่วงเวลาล่าสุดที่จะแสดงได้ (เช่น 24 ชั่วโมงล่าสุด)

5. **เขียนข้อมูลลงไฟล์ Excel (.csv)**
    - มีปุ่มให้ดาวน์โหลดไฟล์ `.csv`
    - ไฟล์ `.csv` เปิดด้วย Excel / Google Sheets ได้ทันที
    - ข้อมูลภายในไฟล์คือข้อมูลจริงที่ดึงมาจาก Public API

---

## โครงสร้างไฟล์โปรเจกต์

 ```text
 agent_dashboard_project/
 ├─ app.py           # ไฟล์หลักของ Streamlit Dashboard
 ├─ README.md        # คู่มือการใช้งาน (ไฟล์นี้)
 └─ requirements.txt # รายชื่อ library ที่ต้องติดตั้ง
 ```

---

 ## ขั้นตอนการรัน (How to Run)

 ### 1) เตรียม Python Environment

 แนะนำให้ใช้ Python 3.9 ขึ้นไป

 ตรวจสอบว่าเครื่องมี Python แล้วหรือยัง

 ```bash
 python --version
 ```

 หรือบนบางเครื่องอาจใช้คำสั่ง

 ```bash
 py --version
 ```

 ### 2) ติดตั้ง Library ที่จำเป็น

 เปิด Terminal / CMD ในโฟลเดอร์ `agent_dashboard_project`

 ```bash
 cd agent_dashboard_project
 ```

 จากนั้นติดตั้ง library ด้วยคำสั่ง

 ```bash
 pip install -r requirements.txt
 ```

 Library ที่ใช้มี:
 - `streamlit` – สำหรับสร้าง Web Dashboard / HMI
 - `requests` – สำหรับดึงข้อมูลจาก Public API
 - `pandas` – สำหรับจัดการข้อมูลแบบตารางและ export CSV

 ### 3) รัน Dashboard

 เมื่อ `pip install` เสร็จแล้ว ให้รันคำสั่ง

 ```bash
 streamlit run app.py
 ```

 จากนั้น Browser จะเปิดอัตโนมัติที่ URL คล้าย ๆ:

 ```text
 http://localhost:8501
 ```

 ถ้าไม่เปิด ให้เปิด Browser แล้วพิมพ์ URL ข้างบนเอง

 ### 4) การใช้งานหน้า Dashboard

 1. เลือกเมืองจากเมนูด้านซ้าย (Bangkok / Chiang Mai / Khon Kaen / Phuket)
 2. รอให้ระบบดึงข้อมูลจริงจาก Open-Meteo API
 3. ดูค่าล่าสุดของตัวแปรต่าง ๆ จากการ์ดด้านบน (Temperature, Humidity, ฯลฯ)
 4. เลื่อนสไลด์เพื่อเลือกจำนวนชั่วโมงล่าสุดสำหรับกราฟ
 5. ดูกราฟ Time-series ของ Temperature & Humidity ตามเวลา
 6. เลื่อนลงมาดูตารางข้อมูลดิบ (Raw Data) ด้านล่าง
 7. กดปุ่ม **"ดาวน์โหลดข้อมูลเป็นไฟล์ .csv (Excel)"**
    - จะได้ไฟล์ เช่น `bangkok_กรุงเทพฯ_weather.csv`
    - นำไฟล์ไปเปิดใน Excel / Google Sheets หรือแนบในรายงานได้

 ---

 ## แนวคิดเชิง Agent Programming

 ถึงแม้โค้ดนี้จะใช้เพียง 1 ไฟล์ (`app.py`) เพื่อให้รันง่าย
 แต่โครงสร้างภายในสามารถอธิบายในเชิง Agent ได้ดังนี้:

 - **Sensor Agent (Data Agent)** – ฟังก์ชัน `fetch_city_weather()`
   - ทำหน้าที่ดึงข้อมูลจากโลกภายนอก (Public API)
   - แปลงข้อมูลให้อยู่ในรูปแบบที่ Agent อื่นเข้าใจ (pandas DataFrame)

 - **HMI / Dashboard Agent** – ส่วนของ `Streamlit UI`
   - รับข้อมูลจาก Sensor Agent
   - แสดงผลออกมาเป็น HMI / Dashboard ให้มนุษย์ดู
   - อนุญาตให้ผู้ใช้เลือกเมือง (City) → เหมือนการส่ง message/command ไปที่ Sensor Agent

 ถ้าต้องการขยายให้เป็น Multi-Agent เต็มรูปแบบภายหลัง
 สามารถแยกโค้ดออกเป็นหลายไฟล์ + ใช้ framework เช่น SPADE มาจัดการการสื่อสารระหว่าง Agent ได้

 ---

 ## หมายเหตุสำหรับการส่งงาน

 - สามารถ zip โฟลเดอร์ `agent_dashboard_project` แล้วส่งเป็นไฟล์งาน
 - แนบรูป Screenshot หน้า Dashboard
   - ตอนเลือกเมืองต่างกัน
   - ตอนแสดงกราฟ
   - ตอน export ไฟล์ .csv
 - ในรายงานสามารถระบุชัดเจนว่า
   - ข้อมูลทั้งหมดมาจาก **Open-Meteo Public API**
   - ไม่ได้ใช้ Sensor จริง แต่เป็นข้อมูล Real-time จากแหล่ง Open Data

 ถ้าต้องการต่อยอดเป็นเวอร์ชัน Multi-Agent ที่เต็มขึ้น
 สามารถขอให้โมเดลช่วยแตกไฟล์ออกและเพิ่ม SPADE/Agent Framework ได้ภายหลัง
