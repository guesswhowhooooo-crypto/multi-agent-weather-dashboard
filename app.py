
import streamlit as st
import requests
import pandas as pd
from datetime import timedelta

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
def fetch_weather_for_location(lat: float, lon: float):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,"
        "precipitation,surface_pressure,windspeed_10m,weathercode"
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
        "weather_code": hourly["weathercode"],
    })
    return df


WEATHER_DESC = {
    0: "ท้องฟ้าแจ่มใส",
    1: "มีเมฆเล็กน้อย",
    2: "มีเมฆเป็นส่วนมาก",
    3: "เมฆมาก",
    45: "หมอก",
    48: "หมอกมีน้ำแข็ง",
    51: "ฝนปรอยเล็กน้อย",
    53: "ฝนปรอยปานกลาง",
    55: "ฝนปรอยหนัก",
    61: "ฝนเล็กน้อย",
    63: "ฝนปานกลาง",
    65: "ฝนหนัก",
    71: "หิมะเล็กน้อย",
    80: "ฝนซู่เล็กน้อย",
    81: "ฝนซู่ปานกลาง",
    82: "ฝนซู่หนัก",
}


def describe_weather(code: int) -> str:
    return WEATHER_DESC.get(code, "สภาพอากาศไม่ทราบแน่ชัด")


st.set_page_config(
    page_title="Thailand City Weather Dashboard (Agent-style HMI)",
    layout="wide",
)

st.title("🌏 City Weather Dashboard (Real Public Data)")
st.caption("Agent-style HMI Dashboard • ข้อมูลจริงจาก Open-Meteo (Public API) • จังหวัดทั่วประเทศไทย")

st.sidebar.header("เลือกจังหวัด (Province Selector)")
province = st.sidebar.selectbox(
    "เลือกจังหวัดที่ต้องการดูข้อมูล",
    THAI_PROVINCES,
)

st.sidebar.markdown("---")
st.sidebar.write("ข้อมูลทั้งหมดดึงจาก **Open-Meteo Public API**")
st.sidebar.write("ข้อมูลเป็นแบบรายชั่วโมง (Hourly)")

now_local = pd.Timestamp.now(tz="Asia/Bangkok")
now_floor_hour = now_local.floor("H").tz_localize(None)
st.info(
    f"🕒 Dashboard refreshed at: **{now_local.strftime('%Y-%m-%d %H:%M:%S')}** Asia/Bangkok"
)

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

df_sorted = df.sort_values("time").reset_index(drop=True)

df_past = df_sorted[df_sorted["time"] <= now_floor_hour]
df_future = df_sorted[df_sorted["time"] > now_floor_hour]

if df_past.empty:
    df_past = df_sorted.iloc[:1]

current = df_past.iloc[-1]
current_time = current["time"]

forecast_end = current_time + timedelta(hours=24)
df_forecast_24h = df_future[df_future["time"] <= forecast_end]

# ---------------- Current Conditions ----------------
st.subheader(f"☀️ Current Weather – {province}")
current_desc = describe_weather(int(current["weather_code"]))

col_main, col_side = st.columns([2, 1])

with col_main:
    st.markdown(
        f"""
        <div style='font-size:60px; font-weight:bold;'>
            {current['temperature_C']:.1f}°C
        </div>
        <div style='font-size:20px;'>
            {current_desc}
        </div>
        <div style='font-size:14px; color:gray;'>
            ข้อมูลล่าสุดจาก API ณเวลา {current_time.strftime('%Y-%m-%d %H:%M')} (Asia/Bangkok)
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_side:
    st.metric("Humidity (%RH)", f"{current['humidity_%']:.0f}")
    st.metric("Apparent Temp (°C)", f"{current['apparent_temperature_C']:.1f}")
    st.metric("Wind speed 10 m (m/s)", f"{current['windspeed_10m_m_s']:.1f}")
    st.metric("Precipitation (mm)", f"{current['precipitation_mm']:.2f}")

st.markdown("---")

# ---------------- 24-hour Forecast ----------------
st.subheader("📅 พยากรณ์อากาศล่วงหน้า 24 ชม. (24-hour Forecast)")

if df_forecast_24h.empty:
    st.write("ไม่มีข้อมูลพยากรณ์ 24 ชั่วโมงข้างหน้าจาก API")
else:
    df_forecast_display = df_forecast_24h.copy()
    df_forecast_display["time_str"] = df_forecast_display["time"].dt.strftime("%d %b %H:%M")
    df_forecast_display["description"] = df_forecast_display["weather_code"].astype(int).map(describe_weather)

    st.dataframe(
        df_forecast_display[[
            "time_str",
            "temperature_C",
            "humidity_%",
            "windspeed_10m_m_s",
            "precipitation_mm",
            "description",
        ]].rename(columns={
            "time_str": "เวลา",
            "temperature_C": "Temp (°C)",
            "humidity_%": "Humidity (%)",
            "windspeed_10m_m_s": "Wind (m/s)",
            "precipitation_mm": "Rain (mm)",
            "description": "สภาพอากาศ",
        }),
        use_container_width=True,
    )

st.markdown(
    "ส่วนนี้คือ **การพยากรณ์อากาศล่วงหน้า 24 ชั่วโมง** จากเวลาปัจจุบัน "
    "โดยอ้างอิงจากโมเดลพยากรณ์ของ Open-Meteo (Forecast Data)"
)

st.markdown("---")

# ---------------- Historical Time-series ----------------
st.subheader("📈 Historical Time-series (ย้อนหลังจนถึงเวลาปัจจุบัน)")

hours_to_show = st.slider(
    "เลือกจำนวนชั่วโมงย้อนหลังที่ต้องการดู (ข้อมูลถึงปัจจุบัน)",
    min_value=6,
    max_value=72,
    value=24,
    step=6,
)

df_past_recent = df_past.tail(hours_to_show)
df_plot = df_past_recent.set_index("time")[["temperature_C", "humidity_%"]]

st.line_chart(df_plot)

st.markdown(
    "กราฟนี้แสดงข้อมูลย้อนหลังตามชั่วโมงที่เลือก "
    "ตั้งแต่ในอดีตจนถึง 'ชั่วโมงล่าสุดในเวลาปัจจุบัน' (Historical Data)"
)

# ---------------- Raw Data + CSV Export ----------------
st.subheader("🧾 Raw Data Table (Historical up to Now)")

st.markdown(
    """
    ตารางนี้คือ **ข้อมูลดิบ (Raw Data)** ที่ดึงมาจาก Open-Meteo API
    และถูกแบ่งเป็นข้อมูล **ย้อนหลังจนถึงปัจจุบัน (Historical)** และ **พยากรณ์ล่วงหน้า 24 ชม. (Forecast)**

    ในตารางด้านล่างนี้จะแสดงเฉพาะข้อมูล **ย้อนหลังจนถึงเวลาปัจจุบัน** เท่านั้น
    - `time` : วัน–เวลาของข้อมูล (อัปเดตรายชั่วโมง)
    - `temperature_C` : อุณหภูมิอากาศ (°C)
    - `humidity_%` : ความชื้นสัมพัทธ์ในอากาศ (%RH)
    - `apparent_temperature_C` : อุณหภูมิที่รู้สึกได้ (°C)
    - `precipitation_mm` : ปริมาณน้ำฝน (มม.) ในชั่วโมงนั้น
    - `surface_pressure_hPa` : ความกดอากาศที่ผิวพื้น (hPa)
    - `windspeed_10m_m_s` : ความเร็วลมที่ความสูง 10 เมตร (m/s)
    - `weather_code` : รหัสสภาพอากาศตามมาตรฐาน Open-Meteo
    """,
)

st.dataframe(df_past.tail(72), use_container_width=True)

st.subheader("💾 Export to Excel (.csv)")

csv_bytes = df_past.to_csv(index=False).encode("utf-8-sig")
file_name = f"{province.replace(' ', '_').lower()}_weather_historical_upto_now.csv"

st.download_button(
    label="ดาวน์โหลดข้อมูลย้อนหลังจนถึงปัจจุบันเป็นไฟล์ .csv (Historical Data)",
    data=csv_bytes,
    file_name=file_name,
    mime="text/csv",
    help="ไฟล์ .csv สามารถเปิดด้วย Microsoft Excel / Google Sheets ได้",
)

st.info(
    "ℹ️ หมายเหตุ: ระบบนี้ใช้ข้อมูลจริงจาก Open-Meteo Public API "
    "ข้อมูลแสดงผลเป็น 2 ส่วนหลัก: "
    "1) ข้อมูลย้อนหลังจนถึงปัจจุบัน (Historical) และ "
    "2) การพยากรณ์ล่วงหน้า 24 ชม. (Forecast) "
    "ข้อมูลทั้งหมดเป็นระดับรายชั่วโมง (Hourly) ไม่ใช่ทุกนาทีเหมือน Sensor จริง"
)
