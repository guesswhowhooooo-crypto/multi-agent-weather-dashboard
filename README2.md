
# City Weather Dashboard HMI (Thailand Provinces)

เวอร์ชันนี้ปรับปรุงจากตัวอย่างเดิมให้:
- เลือกได้ **ทุกจังหวัดในประเทศไทย** จาก Drop-down
- แสดง **เวลา Refresh ของ Dashboard** (ตามเครื่องผู้ใช้)
- แสดง **Timestamp ของข้อมูลล่าสุดจาก API**
- ยังคงใช้ข้อมูลจริงจาก **Open-Meteo Public API + Geocoding API**

ข้อจำกัด: ข้อมูลเป็นแบบ **รายชั่วโมง (Hourly)** ไม่ใช่ realtime ทุกวินาที/ทุกนาที
แต่สามารถ Refresh หน้าเว็บเพื่อดึงข้อมูลล่าสุดได้ตลอดเวลา
