
import streamlit as st
import requests
import pandas as pd


# -----------------------------
# 1) ข้อมูลพิกัดของเมือง (City Database)
# -----------------------------
CITY_COORDS = {
    "Bangkok (กรุงเทพฯ)": {"lat": 13.7563, "lon": 100.5018},
    "Chiang Mai (เชียงใหม่)": {"lat": 18.7883, "lon": 98.9853},
    "Khon Kaen (ขอนแก่น)": {"lat": 16.4419, "lon": 102.8350},
    "Phuket (ภูเก็ต)": {"lat": 7.8804, "lon": 98.3923},
}


def fetch_city_weather(city_name: str) -> pd.DataFrame:
    """
    ดึงข้อมูลอากาศจริงจาก Open-Meteo API (Public / Free / ไม่ต้องใช้ API key)
    คืนค่าเป็น pandas.DataFrame ที่มีคอลัมน์:
    time, temperature_C, humidity_%, apparent_temperature_C,
    precipitation_mm, surface_pressure_hPa, windspeed_10m_m_s
    """
    coords = CITY_COORDS[city_name]
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['lat']}&longitude={coords['lon']}"
        "&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,"
        "precipitation,surface_pressure,windspeed_10m"
        "&timezone=Asia%2FBangkok"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    hourly = data["hourly"]

    df = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "temperature_C": hourly["temperature_2m"],
        "humidity_%": hourly["relativehumidity_2m"],
        "apparent_temperature_C": hourly["apparent_temperature"],
        "precipitation_mm": hourly["precipitation"],
        "surface_pressure_hPa": hourly["surface_pressure"],
        "windspeed_10m_m_s": hourly["windspeed_10m"],
    })
    return df


# -----------------------------
# 2) ตั้งค่าหน้าจอ Dashboard HMI
# -----------------------------
st.set_page_config(
    page_title="City Weather Dashboard (Agent-style HMI)",
    layout="wide",
)

st.title("🌏 City Weather Dashboard (Real Public Data)")
st.caption("Agent-style HMI Dashboard • ข้อมูลจริงจาก Open-Meteo (Public API)")


# -----------------------------
# 3) Drop-down เลือกเมือง
# -----------------------------
st.sidebar.header("เลือกเมือง (City Selector)")
city = st.sidebar.selectbox(
    "เลือกเมืองที่ต้องการดูข้อมูล (Choose a city)",
    list(CITY_COORDS.keys())
)

st.sidebar.markdown("---")
st.sidebar.write("ข้อมูลทั้งหมดดึงจาก **Open-Meteo Public API** แบบเรียลไทม์")
st.sidebar.write("เมื่อเปลี่ยนเมือง ระบบจะดึงข้อมูลใหม่ให้อัตโนมัติ")


# -----------------------------
# 4) ดึงข้อมูลจริงจาก API (ทำหน้าที่เหมือน Sensor Agent)
# -----------------------------
try:
    with st.spinner("กำลังดึงข้อมูลจริงจาก Open-Meteo API ..."):
        df = fetch_city_weather(city)
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก API: {e}")
    st.stop()


# -----------------------------
# 5) แสดงค่าล่าสุด (Latest Snapshot) ในรูปแบบการ์ด HMI
# -----------------------------
st.subheader(f"📡 Latest Measurements for {city}")
latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperature (°C)", f"{latest['temperature_C']:.1f}")
col2.metric("Humidity (%RH)", f"{latest['humidity_%']:.0f}")
col3.metric("Apparent Temp (°C)", f"{latest['apparent_temperature_C']:.1f}")
col4.metric("Wind speed 10 m (m/s)", f"{latest['windspeed_10m_m_s']:.1f}")

col5, col6 = st.columns(2)
col5.metric("Surface Pressure (hPa)", f"{latest['surface_pressure_hPa']:.1f}")
col6.metric("Precipitation (mm)", f"{latest['precipitation_mm']:.2f}")


# -----------------------------
# 6) Plot Graph (Time‑series with Timestamp)
# -----------------------------
st.subheader("📈 Time-series Graph (Temperature & Humidity vs Time)")

# เลือกช่วงเวลาที่ต้องการแสดง (ชั่วโมงล่าสุด)
hours_to_show = st.slider(
    "เลือกจำนวนชั่วโมงล่าสุดที่ต้องการดู",
    min_value=6,
    max_value=72,
    value=24,
    step=6,
)

df_sorted = df.sort_values("time")
df_recent = df_sorted.tail(hours_to_show)

# ใช้ time เป็น index
df_plot = df_recent.set_index("time")[["temperature_C", "humidity_%"]]

st.line_chart(df_plot)

st.markdown(
    "กราฟแสดงความสัมพันธ์ของ **Temperature (°C)** และ **Humidity (%RH)** "
    "ตามเวลา (Timestamp) ในช่วงชั่วโมงล่าสุดที่เลือก"
)


# -----------------------------
# 7) แสดงตารางข้อมูลดิบ (Raw Data)
# -----------------------------
st.subheader("🧾 Raw Data Table (ล่าสุดบางส่วน)")
st.dataframe(df_recent, width="stretch")



# -----------------------------
# 8) เขียนข้อมูลลงไฟล์ Excel (.csv) และให้ดาวน์โหลด
# -----------------------------
st.subheader("💾 Export to Excel (.csv)")

csv_bytes = df_sorted.to_csv(index=False).encode("utf-8-sig")
file_name = city.replace(" ", "_").replace("(", "").replace(")", "").lower() + "_weather.csv"

st.download_button(
    label="ดาวน์โหลดข้อมูลเป็นไฟล์ .csv (Excel)",
    data=csv_bytes,
    file_name=file_name,
    mime="text/csv",
    help="ไฟล์ .csv สามารถเปิดด้วย Microsoft Excel / Google Sheets ได้",
)


st.info(
    "ไฟล์ .csv ที่ดาวน์โหลดไปคือการบันทึกข้อมูลจริงที่ดึงมาจาก Public API "
    "ซึ่งสามารถใช้เป็นหลักฐานในรายงานได้ว่าเป็นข้อมูล Real-time"
)
