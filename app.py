
import streamlit as st
import requests
import pandas as pd
from datetime import datetime


# -----------------------------
# 1) รายชื่อจังหวัดในประเทศไทย (สำหรับ Drop-down)
# -----------------------------
THAI_PROVINCES = [
    "Bangkok",
    "Samut Prakan",
    "Nonthaburi",
    "Pathum Thani",
    "Phra Nakhon Si Ayutthaya",
    "Ang Thong",
    "Lop Buri",
    "Sing Buri",
    "Chai Nat",
    "Saraburi",
    "Chon Buri",
    "Rayong",
    "Chanthaburi",
    "Trat",
    "Chachoengsao",
    "Prachin Buri",
    "Nakhon Nayok",
    "Sa Kaeo",
    "Nakhon Ratchasima",
    "Buri Ram",
    "Surin",
    "Si Sa Ket",
    "Ubon Ratchathani",
    "Yasothon",
    "Chaiyaphum",
    "Amnat Charoen",
    "Bueng Kan",
    "Nong Bua Lamphu",
    "Khon Kaen",
    "Udon Thani",
    "Loei",
    "Nong Khai",
    "Maha Sarakham",
    "Roi Et",
    "Kalasin",
    "Sakon Nakhon",
    "Nakhon Phanom",
    "Mukdahan",
    "Chiang Mai",
    "Lamphun",
    "Lampang",
    "Uttaradit",
    "Phrae",
    "Nan",
    "Phayao",
    "Chiang Rai",
    "Mae Hong Son",
    "Nakhon Sawan",
    "Uthai Thani",
    "Kamphaeng Phet",
    "Tak",
    "Sukhothai",
    "Phitsanulok",
    "Phichit",
    "Phetchabun",
    "Ratchaburi",
    "Kanchanaburi",
    "Suphan Buri",
    "Nakhon Pathom",
    "Samut Sakhon",
    "Samut Songkhram",
    "Phetchaburi",
    "Prachuap Khiri Khan",
    "Nakhon Si Thammarat",
    "Krabi",
    "Phangnga",
    "Phuket",
    "Surat Thani",
    "Ranong",
    "Chumphon",
    "Songkhla",
    "Satun",
    "Trang",
    "Phatthalung",
    "Pattani",
    "Yala",
    "Narathiwat",
]


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


@st.cache_data(show_spinner=False)
def geocode_location(name: str):
    """แปลงชื่อจังหวัด → latitude, longitude โดยใช้ Open-Meteo Geocoding API"""
    params = {
        "name": name,
        "count": 1,
        "language": "en",
        "format": "json",
    }
    resp = requests.get(GEOCODING_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    if not results:
        raise ValueError(f"ไม่พบข้อมูลพิกัดของจังหวัด: {name}")
    first = results[0]
    return first["latitude"], first["longitude"]


@st.cache_data(show_spinner=False)
def fetch_weather_for_location(lat: float, lon: float) -> pd.DataFrame:
    """ดึงข้อมูลอากาศจริงจาก Open-Meteo API สำหรับพิกัดที่กำหนด"""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
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
    page_title="Thailand City Weather Dashboard (Agent-style HMI)",
    layout="wide",
)

st.title("🌏 City Weather Dashboard (Real Public Data)")
st.caption("Agent-style HMI Dashboard • ข้อมูลจริงจาก Open-Meteo (Public API) • จังหวัดทั่วประเทศไทย")


# -----------------------------
# 3) Drop-down เลือกจังหวัด
# -----------------------------
st.sidebar.header("เลือกจังหวัด (Province Selector)")
province = st.sidebar.selectbox(
    "เลือกจังหวัดที่ต้องการดูข้อมูล",
    THAI_PROVINCES,
)

st.sidebar.markdown("---")
st.sidebar.write("ข้อมูลทั้งหมดดึงจาก **Open-Meteo Public API**")
st.sidebar.write("ข้อมูลที่ API ให้มาเป็นแบบรายชั่วโมง (Hourly)")


# เวลา refresh ของ Dashboard (ตามเครื่องผู้ใช้)
now_th = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.info(f"🕒 Dashboard refreshed at (เวลาระบบ): **{now_th}**  Asia/Bangkok")


# -----------------------------
# 4) แปลงชื่อจังหวัด → พิกัด แล้วดึงข้อมูลจริงจาก API
# -----------------------------
try:
    lat, lon = geocode_location(province)
except Exception as e:
    st.error(f"เกิดปัญหาในการแปลงจังหวัดเป็นพิกัด (Geocoding): {e}")
    st.stop()

try:
    with st.spinner("กำลังดึงข้อมูลจริงจาก Open-Meteo API ..."):
        df = fetch_weather_for_location(lat, lon)
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก API: {e}")
    st.stop()


# -----------------------------
# 5) แสดงค่าล่าสุด (Latest Snapshot)
# -----------------------------
st.subheader(f"📡 Latest Measurements for {province}")

df_sorted = df.sort_values("time")
latest = df_sorted.iloc[-1]
latest_time_str = latest["time"].strftime("%Y-%m-%d %H:%M")
st.caption(f"ข้อมูลชั่วโมงล่าสุดจาก API ณเวลา: **{latest_time_str}** Asia/Bangkok")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperature (°C)", f"{latest['temperature_C']:.1f}")
col2.metric("Humidity (%RH)", f"{latest['humidity_%']:.0f}")
col3.metric("Apparent Temp (°C)", f"{latest['apparent_temperature_C']:.1f}")
col4.metric("Wind speed 10 m (m/s)", f"{latest['windspeed_10m_m_s']:.1f}")

col5, col6 = st.columns(2)
col5.metric("Surface Pressure (hPa)", f"{latest['surface_pressure_hPa']:.1f}")
col6.metric("Precipitation (mm)", f"{latest['precipitation_mm']:.2f}")


# -----------------------------
# 6) Plot Graph (Time-series)
# -----------------------------
st.subheader("📈 Time-series Graph (Temperature & Humidity vs Time)")

hours_to_show = st.slider(
    "เลือกจำนวนชั่วโมงล่าสุดที่ต้องการดู",
    min_value=6,
    max_value=72,
    value=24,
    step=6,
)

df_recent = df_sorted.tail(hours_to_show)
df_plot = df_recent.set_index("time")[["temperature_C", "humidity_%"]]

st.line_chart(df_plot)

st.markdown(
    "กราฟแสดงความสัมพันธ์ของ **Temperature (°C)** และ **Humidity (%RH)** "
    "ตามเวลา (Timestamp) ในช่วงชั่วโมงล่าสุดที่เลือก"
)


# -----------------------------
# 7) Raw Data Table
# -----------------------------
st.subheader("🧾 Raw Data Table (ล่าสุดบางส่วน)")
st.dataframe(df_recent, width="stretch")


# -----------------------------
# 8) Export CSV
# -----------------------------
st.subheader("💾 Export to Excel (.csv)")

csv_bytes = df_sorted.to_csv(index=False).encode("utf-8-sig")
file_name = f"{province.replace(' ', '_').lower()}_weather.csv"

st.download_button(
    label="ดาวน์โหลดข้อมูลเป็นไฟล์ .csv (Excel)",
    data=csv_bytes,
    file_name=file_name,
    mime="text/csv",
    help="ไฟล์ .csv สามารถเปิดด้วย Microsoft Excel / Google Sheets ได้",
)


st.info(
    "⚠ หมายเหตุ: ข้อมูลจาก Open-Meteo API เป็นแบบรายชั่วโมง (Hourly) "
    "ไม่ใช่ realtime ทุกวินาที / ทุกนาที แต่เป็นข้อมูลจริงจาก Public API "
    "สามารถ Refresh หน้าเว็บบ่อย ๆ เพื่อดึงข้อมูลล่าสุดได้"
)
