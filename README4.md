
# 🌏 City Weather Dashboard HMI (Agent-style Programming)

เวอร์ชันนี้รวม **ทุกหัวข้อที่โจทย์กำหนด** และปรับ UI ให้คล้ายแอปพยากรณ์อากาศ:

1. **Dashboard HMI**
   - ใช้ Streamlit สร้างหน้าเว็บ
   - แสดงค่าปัจจุบัน (Current) เป็นบล็อกใหญ่ เห็นอุณหภูมิและสภาพอากาศชัดเจน
   - มีเวลาอัปเดตชัดเจน (Asia/Bangkok)

2. **การแสดงผลการตรวจวัดของเมือง (Real Public Data)**
   - ใช้ Open-Meteo Public API (ไม่ต้องมี Sensor จริง)
   - ตัวแปรอย่างน้อย 4–5 ตัวแปร:
     - Temperature (°C)
     - Humidity (%RH)
     - Apparent Temperature (°C)
     - Wind speed 10 m (m/s)
     - Surface Pressure (hPa)
     - Precipitation (mm)
     - Weather Code (ใช้แปลงเป็นข้อความอธิบายสภาพอากาศ)

3. **Drop-down Menu สำหรับเลือกจังหวัด**
   - เลือกจังหวัดได้ครบทุกจังหวัดในประเทศไทย
   - ระบบใช้ Geocoding API แปลงชื่อจังหวัด → lat/lon อัตโนมัติ

4. **Plot Graph (มี Timestamp)**
   - กราฟ Time-series แสดง Temperature & Humidity
   - เป็นข้อมูล **ย้อนหลังจนถึงชั่วโมงล่าสุดในเวลาปัจจุบัน**
   - ปรับจำนวนชั่วโมงย้อนหลังที่ดูได้ด้วย Slider

5. **เขียนข้อมูลลงไฟล์ Excel (.csv)**
   - ปุ่มดาวน์โหลดข้อมูลย้อนหลังจนถึงปัจจุบัน (Historical Data)
   - ไฟล์ `.csv` เปิดใน Excel / Google Sheets ได้ทันที

6. **พยากรณ์อากาศล่วงหน้า 24 ชม.**
   - แบ่งข้อมูลจาก API เป็น 2 ส่วน:
     - Historical (<= เวลาปัจจุบัน)
     - Forecast (> เวลาปัจจุบัน)
   - แสดง Forecast แบบรายชั่วโมงล่วงหน้า 24 ชม. พร้อมข้อความอธิบายสภาพอากาศ

## วิธีรัน

1. ติดตั้ง Library

```bash
pip install -r requirements.txt
```

2. รัน Streamlit

```bash
streamlit run app.py
```

3. เปิด Browser ที่ URL ที่ Streamlit แจ้ง (เช่น http://localhost:8501)
