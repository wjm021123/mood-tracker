import streamlit as st
import pandas as pd #csv 등 데이터를 통계 처리하기 위한 라이브러리 
import datetime as dt #시간을 다루기 위한 코드 묶음
import time
import pathlib as pl 
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from streamlit_js_eval import streamlit_js_eval #javascript을 돌리기 위한 것?
from datetime import datetime, timedelta #시간 계산을 위한 라이브러리
import uuid
import matplotlib.pyplot as plt #파이썬 기본 그래프 그리기 도구 라이브러리
from matplotlib import font_manager
import seaborn as sns # matplotlib 위에서 동작하는 그래프 그리기 라이브러리 
import emoji
import json
import os
import signal
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


try:
    from streamlit_calendar import calendar as streamlit_calendar
except ModuleNotFoundError:
    streamlit_calendar = None

BASE_DIR = pl.Path(__file__).parent
SETTINGS_PATH = BASE_DIR / "settings.json"
DATA_PATH = BASE_DIR / "mood_tracker_data.csv"
TRANSLATION_PATH = BASE_DIR / "translations.csv"


# =========================================
# Design
# =========================================

##FONT
# Matplotlib에게 ttf 인식시키기
plt.rcParams["axes.unicode_minus"] = False #'-' 기호가 한글 폰트에서 깨지지 않도록 해주는 코드
font_path = pl.Path(__file__).parent / "fonts" / "Pretendard-Regular.ttf" #app.py 가 속한 폴더(=__file__)를 기준으로 폰트의 위치를 지정함.
try:
    font_manager.fontManager.addfont(str(font_path)) #matplotlib에게 강제로 폴더 안의 폰트를 폰트 목록에 추가시킴
    pretendard_font_name = font_manager.FontProperties(fname=str(font_path)).get_name() 
    plt.rcParams["font.family"] = pretendard_font_name
except Exception:
    pass

# /*내용*/는 css의 주석과 같은 것. css는 Cascading Style Sheets.
# html은 화면 구조를 만드는 것, css는 그 구조를 꾸미는 것.
# div는 division. 화면의 공간? 구조?를 만듬. html의 것. 
# .stApp, stButton 등등은 css에서 꾸미기를 위해 사용되는 것. >는 포함 관계 의미.
st.markdown(
    """
    <style>

    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 전체 앱 배경색 */
    .stApp {
        background-color: #F7F4EE;
    }

    /* 기본 텍스트 색과 폰트*/

    html, body, .stApp, .stApp * {
        color: #4E463D;
        font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif !important;
    }

    /* 제목, 소제목 */
    .section-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #5C554B;
        border-bottom: 2px solid #CDBFAA;
        padding-bottom: 0.25rem;
        margin-top: 1.7rem;
        margin-bottom: 0.2rem;
        line-height: 1.3;
    }

    .subsection-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #5C554B;
        margin-top: 1.3rem;
        margin-bottom: 0.25rem;
        line-height: 1.4;
    }

    /* 버튼 색상 */
    .stButton > button {
        background-color: #E4DDD2;
        color: #4E463D;
        border: 1px solid #CFC5B7;
        border-radius: 10px;
    }

    .stButton > button:hover {
        background-color: #D7CCBC;
        border: 1px solid #BDAF9D;
        color: #3E372F;
    }

    /* selectbox / input */
    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input {
        background-color: #FCFAF6;
        color: #4E463D;
        border: 1px solid #D9D0C3;
        border-radius: 8px;
    }

    /* disabled text area (guide examples) */
    .stTextArea textarea:disabled {
    color: #4E463D !important;
    -webkit-text-fill-color:
    #4E463D !important;
    opacity: 1 !important;
    background-color:
    #F8F5eF !important;
    }

    /* slider */ 
    .stSlider [data-baseweb="slider"] div {
        color: #7A8B6F;
    }

    /* success/info/warning box */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* markdown separator */
    hr {
        border-color: #DDD4C7;
    }

    </style>
    """,
    unsafe_allow_html=True #streamli은 markdown 안에 html/css 삽입을 허용함. 
)

# ============================================
# Setting - Language
# ===============================================

#현재 설정을 json에서 불러오기.
#"r"는 json파일의 특정한 읽기 모드, utf-8은 한국어가 꺠지지 않게 하는 인코딩 설정. 
def load_settings():
    if pl.Path(SETTINGS_PATH).exists():
        try:
            with open(
                SETTINGS_PATH,
                "r",
                encoding="utf-8"
                        ) as f:
                return json.load(f) #f를 python dict로 바꿔줌.
        except Exception:
            pass #오류가 나도 앱을 멈추지 말고 넘어가라. 
    return {
        "language": "eng",
        "default_bed_time": "23:00",
        "default_wake_time": "07:00",
        "region": "Seoul",
        "latitude": 37.5665,
        "longitude": 126.9780,
        "location_mode": "ready"
    } #json 파일 읽기에 실패하면 기본 설정을 로딩함.

#현재 설정을 json에 저장.
#"w"는 json의 쓰기 모드. 
def save_settings():
    settings = {}
    settings["language"] = st.session_state.get("language", "eng")
    settings["default_bed_time"] = st.session_state.get("default_bed_time", "23:00")
    settings["default_wake_time"] = st.session_state.get("default_wake_time", "07:00")
    settings["region"] = st.session_state.get("region", "Seoul")
    settings["latitude"] = st.session_state.get("latitude", 37.5665)
    settings["longitude"] = st.session_state.get("longitude", 126.9780)
    settings["location_mode"] = st.session_state.get("location_mode", "ready")
    settings["default_free_text"] = st.session_state.get("default_free_text", "")
    # open: 파일이 없으면 새로 만들고, 있으면 기존 내용을 덮어씀
    with open(
        SETTINGS_PATH,
        "w",
        encoding="utf-8"
            ) as f:
        json.dump(settings, f, ensure_ascii=False, indent=2) 
        #python dict를 json 형식으로 바꿔서 저장. 
        # ensure_ascii=false는 한글이 깨지지 않도록 하는 설정, indent=2는 json 파일을 사람이 읽기 좋게 들여쓰기 2칸으로 저장하라는 것.

#settings.json파일 자동생성
if not SETTINGS_PATH.exists():
    save_settings()

#session state에 언어 설정이 없으면, json을 읽어온다. 
if "language" not in st.session_state:
    settings = load_settings()
    st.session_state.language = (
        settings.get(
            "language",
            "eng"
        )
    )

settings = load_settings()
defaults = {
    "language": "eng",
    "default_bed_time": "23:00",
    "default_wake_time": "07:00",
    "region": "Seoul",
    "latitude": 37.5665,
    "longitude": 126.9780,
    "location_mode": "ready",
    "default_free_text": ""
}
for key, fallback in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = settings.get(key, fallback)


region_and_timezone = {
    "Seoul": "Asia/Seoul",
    "Busan": "Asia/Seoul",

    "Tokyo": "Asia/Tokyo",
    "Osaka": "Asia/Tokyo",

    "Taipei": "Asia/Taipei",
    "Hong Kong": "Asia/Hong_Kong",
    "Singapore": "Asia/Singapore",
    "Bangkok": "Asia/Bangkok",
    "Hanoi": "Asia/Bangkok",
    "Ho Chi Minh City": "Asia/Ho_Chi_Minh",
    "Manila": "Asia/Manila",
    "Jakarta": "Asia/Jakarta",

    "Dubai": "Asia/Dubai",
    "Mumbai": "Asia/Kolkata",

    "Sydney": "Australia/Sydney",
    "Melbourne": "Australia/Melbourne",
    "Auckland": "Pacific/Auckland",

    "Cairo": "Africa/Cairo",
    "Cape Town": "Africa/Johannesburg",
    "Nairobi": "Africa/Nairobi",

    "New York": "America/New_York",
    "Boston": "America/New_York",
    "Washington DC": "America/New_York",

    "Chicago": "America/Chicago",

    "Los Angeles": "America/Los_Angeles",
    "San Francisco": "America/Los_Angeles",
    "Seattle": "America/Los_Angeles",

    "Vancouver": "America/Vancouver",
    "Toronto": "America/Toronto",

    "Mexico City": "America/Mexico_City",
    "Sao Paulo": "America/Sao_Paulo",
    "Buenos Aires": "America/Argentina/Buenos_Aires",

    "London": "Europe/London",
    "Paris": "Europe/Paris",
    "Berlin": "Europe/Berlin",
    "Rome": "Europe/Rome",
    "Madrid": "Europe/Madrid",
    "Amsterdam": "Europe/Amsterdam",
    "Stockholm": "Europe/Stockholm",
    "Oslo": "Europe/Oslo",
    "Copenhagen": "Europe/Copenhagen",
    "Helsinki": "Europe/Helsinki",

    "Reykjavik": "Atlantic/Reykjavik",
}

def time_text_to_time(time_text, fallback_time):
    try:
        hour, minute = map(int, str(time_text).split(":")[:2])
        return dt.time(hour=hour, minute=minute)
    except Exception:
        return fallback_time

#상관관계 문장 번역 
#번역csv 불러오기
@st.cache_data(ttl=60)
def load_translations():
    df = pd.read_csv(TRANSLATION_PATH)

    translations = {
        "kor": {},
        "eng": {}
    }

    for _, row in df.iterrows():

        key = row["key"]
        translations["kor"][key] = row["kor"]
        translations["eng"][key] = row["eng"]

    return translations

translations = load_translations()

def t(key):
    language = st.session_state.get("language", "eng")
    return translations.get(language, {}).get(key, key)

#상관관계 문장 생성&번역을 위한 t_sent 함수:
#kwargs는 keyword arguments. 이름 붙은 것들을 모두 dictionary로 모음.
def t_sent(key, **kwargs):
    language = st.session_state.get("language", "eng")

    sentence_translations = {
        "kor": {
            "event_event_ratio": "{column1_phrase}에 {selected_column2_phrase}이(가) 일어난 비율은 {event_o_mean_percent}이고, 그렇지 않은 날에 {selected_column2_phrase}이(가) 일어난 비율은 {event_x_mean_percent}입니다.",
            "event_event_no_relation": "{column1_name}이(가) {column2_name}에 미치는 영향은 거의 없는 것으로 보입니다.",
            "event_event_positive": "{column1_phrase}일 때 그렇지 않은 경우보다 {selected_column2_phrase}이(가) 평균적으로 {difference_percent_ee}p 더 나타났습니다.",
            "event_event_negative": "{column1_phrase}일 때 그렇지 않은 경우보다 {selected_column2_phrase}이(가) 평균적으로 {difference_percent_ee}p 더 적게 나타났습니다.",
            "event_scale_ratio": "{column1_phrase}에 {column2_name}의 평균값은 {event_o_mean:.2f}이고, 그렇지 않은 날에 {column2_name}의 평균값은 {event_x_mean:.2f}입니다.",
            "event_scale_no_relation": "{column1_phrase}과 그렇지 않은 날 사이에 {column2_name}의 뚜렷한 차이는 보이지 않습니다.",
            "event_scale_positive": "{column1_phrase}일 때 그렇지 않은 날보다 {column2_name}이(가) 평균적으로 {difference_percent_es} 더 높았습니다.",
            "event_scale_negative": "{column1_phrase}일 때 그렇지 않은 날보다 {column2_name}이(가) 평균적으로 {difference_percent_es} 더 낮았습니다.",
            "scale_scale_corr": "{column1_name}과 {column2_name}의 상관계수는 {correlation_num:.3f}입니다.",
            "scale_scale_strength": "{column1_name}과 {column2_name} 사이에는 {strength}.",
            "scale_scale_positive": "{column1_phrase} {selected_column2_phrase} 경향이 있습니다. 두 변수 사이에는 {strength}.",
            "scale_scale_negative": "{column1_phrase} {selected_column2_phrase} 경향이 있습니다. 두 변수 사이에는 {strength}.",
            "scale_event_corr":"{column1_name}과 {column2_name}의 상관계수는 {correlation_num:.3f}입니다.",
            "scale_event_strength": "{column1_name}의 변화에 따른 {column2_name}의 발생 여부에는 {strength}.",
            "scale_event_positive": "{column1_phrase} {selected_column2_phrase}이(가) 나타날 가능성이 더 높습니다. 두 변수 사이에는 {strength}.",
            "scale_event_negative": "{column1_phrase} {selected_column2_phrase}이(가) 나타날 가능성이 더 낮습니다. 두 변수 사이에는 {strength}."
        },
        "eng": {
            "event_event_ratio": "The occurrence rate of {column2_name} {column1_phrase} was {event_o_mean_percent}, compared to {event_x_mean_percent} on days without {column1_name}.",
            "event_event_no_relation": "{column1_name} appears to have little effect on {column2_name}.",
            "event_event_positive": "{selected_column2_phrase_shortened} occurred {difference_percent_ee}p more often {column1_phrase} than on days without it.",
            "event_event_negative": "{selected_column2_phrase_shortened} occurred {difference_percent_ee}p less often {column1_phrase} than on days without it.",
            "event_scale_ratio": "The average of {column2_name} {column1_phrase} is {event_o_mean:.2f}, compared to {event_x_mean:.2f} on other days.",
            "event_scale_no_relation": "There was no clear difference in {column2_name} between days with {column1_phrase} and days without it.",
            "event_scale_positive": "{column2_name} was on average {difference:.2f} higher {column1_phrase} than on days without it.",
            "event_scale_negative": "{column2_name} was on average {difference_percent_es} lower {column1_name} than on days without it.",
            "scale_scale_corr": "The correlation coefficient between {column1_name} and {column2_name} is {correlation_num:.3f}.",
            "scale_scale_strength": "{strength} {column1_name} and {column2_name}.",
            "scale_scale_positive": "When {column1_phrase}, {selected_column2_phrase}. {strength} the two variables.",
            "scale_scale_negative": "When {column1_phrase}, {selected_column2_phrase} tended to decrease/become worse. {strength} the two variables.",
            "scale_event_corr": "The relationship strength(correlation coefficient) between {column1_name} and {column2_name} is {correlation_num:.3f}.",
            "scale_event_strength": "{strength} {column1_name} and {column2_name}.",
            "scale_event_positive": "When {column1_phrase}, {selected_column2_phrase} more likely to occur. {strength} the two variables.",
            "scale_event_negative": "When {column1_phrase}, {selected_column2_phrase} less likely to occur. {strength} the two variables."
        }
    }
    template = sentence_translations.get(language, {}).get(key, key)
    return template.format(**kwargs)

def format_date_for_display(date_value):
    date_value = pd.to_datetime(date_value)
    language = st.session_state.get("language", "eng")

    if language == "kor":
        return date_value.strftime("%Y/%m/%d")
    elif language == "eng":
        return date_value.strftime("%B %d, %Y")
    
    return date_value.strftime("%Y/%m/%d")

# ===========================================
# Utility functions
# ==========================================

def to_five_level(score): 
    if score < 0.2:
        return 1
    elif score < 0.4:
        return 2
    elif score < 0.6:
        return 3
    elif score < 0.8:
        return 4
    else:
        return 5

level_text_map = {
    1: t("very_bad"),
    2: t("bad"),
    3: t("moderate"),
    4: t("good"),
    5: t("very_good")
}

def level_to_text(value):
    if pd.isna(value):
        return t("no_data")
    level_text_map = {
    1: t("very_bad"),
    2: t("bad"),
    3: t("moderate"),
    4: t("good"),
    5: t("very_good")
    }
    rounded_value = int(round(value))
    level_text = level_text_map.get(rounded_value, t("no_info"))
    return f"{rounded_value} ({level_text})"


def three_level_to_text(value):
    if pd.isna(value):
        return t("no_info")
    three_level_text_map = {
    0: t("none"),
    1: t("slightly_yes"),
    2: t("very_yes")
    }
    rounded_value = int(round(value))
    level_text = three_level_text_map.get(rounded_value, t("no_info"))
    return f"{rounded_value} ({level_text})"

def ox_to_text(value):
    if pd.isna(value):
        return t("no_info")
    if value == True or value == 1 or value == "true" or value == "True":
        return t("yes")
    elif value == False or value == 0 or value == "false" or value == "False":
        return t("no")
    else:
        return t("no_info")

#json 응답 처리 함수. 인터넷 요청, 재시도, 오류 처리를 원활히 하기 위해서 만들었음.
def get_json_with_retry(url, params, label, max_retries=3, timeout=20):
    last_error = None

    session = requests.Session()
    #retry는 재시도 규칙 (total은 저체 최대 재시도 횟수, read는 응답 읽기 실패 시 재시도 횟수 등등...)
    retry = Retry(
        total=max_retries,
        connect=max_retries,
        read=max_retries,
        status=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    #재시도 규칙을 실제 HTTP 요청 처리기에 부착. 
    adapter = HTTPAdapter(max_retries=retry)
    #http or https로 시작하는 요청에는 이 재시도 규칙을 적용하라.
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    #실제 API 요청 코드
    try:
        response = session.get(
            url,
            params=params,
            timeout=timeout
        )
        #응답 코드가 400 or 500번대면 예외를 발생시킴
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        last_error = e

    st.error(f"{label} : {t('failed_to_load_data_warning')}")
    st.caption(str(last_error))
    st.stop()


# =========================
##날씨 설명
# =========================

#weather tag 함수
weather_tags_map = {
    "clear": [
        "맑",
        "맑음",
        "clear",
        "sunny",
        "bright"
    ],
    "cloudy": [
        "구름",
        "흐림",
        "우중충",
        "꾸리꾸리",
        "회",
        "cloudy",
        "cloud",
        "grey",
        "overcast"
    ],
    "rain": [
        "비",
        "폭우",
        "소나기",
        "우박",
        "장마",
        "빗",
        "rain",
        "drizzle",
        "shower",
        "downpour"
    ],
    "snow": [
        "눈",
        "폭설",
        "진눈깨비",
        "싸락",
        "snow",
        "blizzard",
        "sleet"
    ],
    "thunderstorm": [
        "천둥",
        "번개",
        "뇌우",
        "thunder",
        "lightning",
        "storm"
    ]
}

def compute_weather_tags(weather_summary):
    if pd.isna(weather_summary):
        return set()
    text = str(weather_summary).strip().lower()
    weather_tags = set()
    for tag, keywords in weather_tags_map.items():
        if any(keyword in text for keyword in keywords):
            weather_tags.add(tag)
    return weather_tags

#맑은 날 가중치 부여
def clear_weather_bonus(weather_summary): #비 안 온 날만 가중치를 부여. 
    tags = compute_weather_tags(weather_summary)
    if "clear" in tags:
        return 1
    else:
        return 0

#강수 여부
def precipitation_ox(weather_summary): #강수 여부 확인 함수
    tags = compute_weather_tags(weather_summary)
    if "rain" in tags or "snow" in tags :
        return 1
    else:
        return 0

#천둥번개 여부
def thunderstorm_ox(weather_summary):
    tags = compute_weather_tags(weather_summary)
    if "thunderstorm" in tags:
        return 1
    else:
        return 0

##햇빛
sunshine_duration_max = 14.75 #한국 하지의 햇빛 길이 가장 긴 날의 일조 시간 은 14시간 46분
sunshine_duration_min = 9.5 #한국 동지의 햇빛 길이 가장 짧은 날의 일조 시간 은 약 9시간 34분

# https://www.mdpi.com/2071-1050/10/6/1822#:~:text=South%20Korea%20is%20located%20between,MJ%20in%20February%20%5B16%5D.
# https://www.bom.gov.au/climate/austmaps/solar-radiation-glossary.shtml
# https://www.sciencedirect.com/science/article/abs/pii/S1364682615300420
shortwave_radiation_sum_max = 30 #한국의 일사량 최대는 대략 25~27로 알려져 있으므로, 약간 높여서 설정 
#https://www.ksesjournal.co.kr/media/sites/kses/2011-031-03/ksest_201106_010/ksest_201106_010.pdf
shortwave_radiation_sum_min = 5.0 #전국 최저 값인 (표3) 제주 1월 값 1.48kWh/m^2/day보다 약간 낮게 설정함

def estimate_sunshine_duration(daylight_duration, weather_summary):
    tags = compute_weather_tags(weather_summary)
    ratio_candidates = []
    if "clear" in tags:
        ratio_candidates.append(0.9)
    if "rain" in tags:
        ratio_candidates.append(0.25)
    if "snow" in tags:
        ratio_candidates.append(0.35)
    if "cloudy" in tags:
        ratio_candidates.append(0.5)
    if "thunderstorm" in tags:
        ratio_candidates.append(0.15)
    
    if not ratio_candidates:
        ratio = 0.7
    else:
        ratio = min(ratio_candidates)

    return round(daylight_duration * ratio, 1)
        

def compute_sunshine_ratio(row): #햇빛 지수를 0~1 사이 값으로 반환하는 함수
    if pd.notna(row.get("sunshine_intensity_label")):
        return (int(row["sunshine_intensity_label"]) - 1) / 4
    sunshine_duration_hours = row.get("sunshine_duration_hours")
    shortwave_radiation_sum = row.get("shortwave_radiation_sum")
    daylight_duration_hours = row.get("daylight_duration_hours")
    if pd.isna(sunshine_duration_hours) or pd.isna(shortwave_radiation_sum):
        return None
    sunshine_duration_ratio = (sunshine_duration_hours - sunshine_duration_min) / (sunshine_duration_max - sunshine_duration_min)
    sunshine_duration_ratio = min(max(sunshine_duration_ratio,0),1)
    sunshine_intensity_ratio = (shortwave_radiation_sum - shortwave_radiation_sum_min) / (shortwave_radiation_sum_max - shortwave_radiation_sum_min)
    sunshine_intensity_ratio = min(max(sunshine_intensity_ratio,0),1)
    if daylight_duration_hours is not None:
        if daylight_duration_hours < 4 or daylight_duration_hours > 20:
            daylight_duration_penalty = 0.2
        elif daylight_duration_hours < 6 or daylight_duration_hours > 18:
            daylight_duration_penalty = 0.1
        else:
            daylight_duration_penalty = 0
    else:
        daylight_duration_penalty = 0
    sunshine_duration_ratio = sunshine_duration_ratio - daylight_duration_penalty
    return (sunshine_duration_ratio + sunshine_intensity_ratio) / 2

def compute_sunshine_index(row): #햇빛 지수를 1~5 사이 값으로 반환하는 함수 
    if pd.notna(row.get("sunshine_intensity_label")):
        return int(row["sunshine_intensity_label"]) #수동 입력 값이 존재한다면, 그냥 그대로 사용.
    ratio = compute_sunshine_ratio(row)
    if ratio is None:
        return None
    return to_five_level(ratio)


##대기질
def pm25_to_level(x): #초미세먼지가 얼마나 나쁜지 1~5의 숫자로 나타내는 함수 
    if pd.isna(x):
        return None
    
    if x<=15:
        return 5
    elif x<=25:
        return 4
    elif x<=35: #3부터는 마스크 착용이 필수라 기분이 많이 나빠짐
        return 3
    elif x<=50:
        return 2
    else:
        return 1

def pm10_to_level(x):
    if pd.isna(x):
        return None
    
    if x<=30:
        return 5
    elif x<=50:
        return 4
    elif x<=80:
        return 3 #초미세먼지와 마찬가지로, 3부터는 마스크 착용이 필수임.
    elif x<=120:
        return 2
    else:
        return 1

def compute_air_quality_index(row):
    pm25_level = pm25_to_level(row.get("pm2_5"))
    pm10_level = pm10_to_level(row.get("pm10"))

    if pm25_level is None or pm10_level is None:
        return None
    return min(pm25_level, pm10_level) #둘 중 더 나쁜 수준을 대기질 수준으로 간주


##기온 : 폭염, 한파에 패널티 부여
def temperature_penalty(temperature): 
    if pd.isna(temperature):
        return 0 #기온 데이터가 없으면 영향도 없음
    
    if 5 <= temperature < 25:
        return 0
    elif -5 <= temperature < 5 or 25 <= temperature < 30: #조금 춥거나 더울 때
        return -1
    elif temperature < -5 or 30 <= temperature: #폭염, 한파 
        return -2
    else:
        return 0

## 습도 : 너무 습하면 패널티 부여 
def humidity_penalty(humidity):
    if pd.isna(humidity):
        return 0

    if humidity < 60:
        return 0
    elif 60 <= humidity < 70:
        return -1
    else:
        return -2

##환경 지수 (모든 요소를 종합적으로 고려, 객관적으로 반영한 지수)
#고려대상 : 공기질, 맑음 여부, 햇빛, 습도, 기온
#숫자가 높을수록 좋은 환경
def compute_environment_index(row):
    sunshine_index = row.get("sunshine_index")
    air_quality_index = row.get("air_quality_index")
    temperature = row.get("temperature_c")
    humidity = row.get("humidity_percent")
    weather_summary = row.get("weather_summary")

    if pd.isna(sunshine_index) or pd.isna(air_quality_index):
        return None
    sunshine_score = (sunshine_index - 1) / 4
    air_quality_score = (air_quality_index - 1) /4
    temperature_score = 1 + (temperature_penalty(temperature) / 2)
    humidity_score = 1 + (humidity_penalty(humidity) / 2)
    clear_score = clear_weather_bonus(weather_summary)

    environment_score = (
        0.30 * air_quality_score +
        0.25 * sunshine_score +
        0.20 * temperature_score +
        0.15 * humidity_score +
        0.10 * clear_score
        )
        
    return 1 + 4 * environment_score


#종합 기분 지수 
def compute_overall_mood_index(row):
    mood = row.get("mood")
    focus = row.get("focus")
    irritability = row.get("irritability")
    depression = row.get("depression")
    if pd.isna(mood) or pd.isna(focus) or pd.isna(irritability) or pd.isna(depression):
        return None
    mood_score = (mood - 1) / 4
    focus_score = (focus - 1) / 4
    irritability_score = (2 - irritability) / 2
    depression_score = (2 - depression) / 2
    overall_mood_score = (
        0.40 * mood_score + 
        0.30 * focus_score + 
        0.15 * irritability_score +
        0.15 * depression_score
        )
    return 1 + 4 * overall_mood_score

#수면 지수
def compute_sleep_score(row):
    duration = row.get("sleep_duration_hours")
    quality = row.get("sleep_quality")
    if pd.isna(duration) or pd.isna(quality):
        return None
    
    # 시간 점수 (8시간 기준)
    duration_score = min(max(duration / 8 , 0), 1)

    # 질 점수 (0~2 -> 0~1로 변환)
    quality_score = quality / 2

    return duration_score * 0.7 + quality_score * 0.3

def compute_sleep_index(row):
    score = compute_sleep_score(row)
    if score is None:
        return None
    return 1 + 4 * score

def compute_sleep_consistency_std(df, target_date, column_name):
    target_date = pd.to_datetime(target_date)
    recent_records = df[
        (pd.to_datetime(df["target_date"]) >= target_date - pd.Timedelta(days=6)) & 
        (pd.to_datetime(df["target_date"]) <= target_date)
    ]
    
    recent_sleep_times = recent_records[column_name].dropna()
    
    if len(recent_sleep_times) < 3: 
        return None
    
    recent_sleep_minutes = []

    for value in recent_sleep_times:
        try: 
            if isinstance(value, dt.time):
                hour = value.hour
                minute = value.minute
            else:
                time_text = str(value).strip()
                hour, minute = map(int, time_text.split(":")[:2])
        except Exception:
            continue

        recent_sleep_minute = hour * 60 + minute
        
        if column_name == "sleep_bed_time" and hour < 12:
            recent_sleep_minute += 24 * 60
        
        recent_sleep_minutes.append(recent_sleep_minute)
    if len(recent_sleep_minutes) < 3:
        return None
        
    return pd.Series(recent_sleep_minutes).std(ddof=0)    

def compute_sleep_consistency_std_index(std_minutes):
    if pd.isna(std_minutes):
        return None
    
    consistency_ratio = 1 - min(max(std_minutes / 120, 0), 1)
    return 1 + 4 * consistency_ratio                 


# 생활 변수(boolean)을 계산 가능하게 바꾸는 함수
def boolean_to_int(value):
    if pd.isna(value):
        return None
    if value is True or value == "True" or value == "true" or value == 1:
        return 1
    if value is False or value == "False" or value == "false" or value == 0:
        return 0
    return None

def calculate_sleep_duration_hours(bed_time, wake_time):
    bed_minutes = bed_time.hour * 60 + bed_time.minute
    wake_minutes = wake_time.hour * 60 + wake_time.minute

    if wake_minutes<=bed_minutes:
        wake_minutes += 24 * 60

    return round((wake_minutes - bed_minutes) / 60, 2)

# ===========================================

st.title(t("app_title"))
st.markdown(t("app_title_sent"))

selected_page = st.segmented_control(
    t('menu'), 
    options=[t('record_menu'), t('statistics_menu'), t('journal_history_menu'), t('settings_menu'), t('user_guide_menu')],
    default=t('record_menu'),
    key="main_page_selector")

# ===========================================
# 날씨와 기분 기록 페이지 
# ==========================================
if selected_page == t("record_menu"):
    ### 날짜 기록 
    #현재 날짜, 시간 기록
    recorded_at = dt.datetime.now() 

    #기록 대상 날짜. 날씨용 시각까지 한꺼번에 처리했다.
    cutoff_hour = 7
    weather_record_hour = 15
    if recorded_at.hour < cutoff_hour: #만약 현재 시간이 오전 7시 이전이라면, 기록 대상 날짜는 어제로 설정    
        target_date = (recorded_at - timedelta(days=1)).date()
        target_hour = weather_record_hour
    elif recorded_at.hour < weather_record_hour:
        target_date = recorded_at.date()
        target_hour = max(0, recorded_at.hour - 1)
    else:
        target_date = recorded_at.date()
        target_hour = weather_record_hour

    current_time_str = recorded_at.strftime("%Y-%m-%d %H:%M") 
    target_date_str = target_date.strftime("%Y-%m-%d")
    
    current_date_only_display = format_date_for_display(recorded_at)
    current_time_only = recorded_at.strftime("%H:%M")
    current_time_str_for_display = (
        f" {current_date_only_display} {current_time_only}"
    )
    target_date_str_for_display=format_date_for_display(target_date_str)
    st.write(f"🕘 {t('current_time')} : {current_time_str_for_display}")
    st.write(f"✅ {t('target_date')} : {target_date_str_for_display}")
    
    # =============================================
    ### 날씨 정보 가져오기
    # =============================================
    weather_url = "https://api.open-meteo.com/v1/forecast"
    air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    weather_code_map = {
        0: t('weather_code_0'),
        1: t('weather_code_1'),
        2: t('weather_code_2'),
        3: t('weather_code_3'),
        45: t('weather_code_45'),
        55: t('weather_code_55'),
        56: t('weather_code_56'),
        57: t('weather_code_57'),
        61: t('weather_code_61'),
        63: t('weather_code_63'),
        65: t('weather_code_65'),
        66: t('weather_code_66'),
        67: t('weather_code_67'),
        71: t('weather_code_71'),
        73: t('weather_code_73'),
        75: t('weather_code_75'),
        77: t('weather_code_77'),
        80: t('weather_code_80'),
        81: t('weather_code_81'),
        82: t('weather_code_82'),
        85: t('weather_code_85'),
        86: t('weather_code_86'),
        95: t('weather_code_95'),
        96: t('weather_code_96'),
        99: t('weather_code_99'),
    }

    # 날씨 정보의 초기 상태 설정
    if "temperature" not in st.session_state:
        st.session_state.temperature = None
    if "humidity" not in st.session_state:
        st.session_state.humidity = None    
    if "sunshine_duration" not in st.session_state:
        st.session_state.sunshine_duration = None 
    if "sunshine_duration_hours" not in st.session_state: #햇빛 지속 시간을 시간 단위로 입력받기 위한 변수
        st.session_state.sunshine_duration_hours = 0.0
    if "daylight_duration" not in st.session_state:
        st.session_state.daylight_duration = None
    if "daylight_duration_hours" not in st.session_state:
        st.session_state.daylight_duration_hours = 0.0
    if "shortwave_radiation_sum" not in st.session_state:
        st.session_state.shortwave_radiation_sum = None
    if "sunshine_intensity_label" not in st.session_state: #햇빛 세기 입력을 위한 변수
        st.session_state.sunshine_intensity_label = None
    if "weather_code" not in st.session_state:
        st.session_state.weather_code = None
    if "weather_summary" not in st.session_state: #weather code에 대응하는 날씨 설명을 저장하기 위한 변수
        st.session_state.weather_summary = None
    if "manual_weather_summary_input" not in st.session_state: #날씨 불러오기를 시도했으나, 날씨 코드 맵에 해당하는 날씨 설명이 없는 경우에 한해, 수동으로 날씨 설명을 입력받기 위한 변수
        st.session_state.manual_weather_summary_input = ""  
    if "weather_reference_time" not in st.session_state:
        st.session_state.weather_reference_time = None

    if "pm2_5" not in st.session_state:
        st.session_state.pm2_5 = None
    if "pm10" not in st.session_state:
        st.session_state.pm10 = None

    if "weather_input_mode" not in st.session_state:
        st.session_state.weather_input_mode = "unset" # unset | auto_pending | manual | awaiting_summary | saved

    #날씨 정보 가져오기 & 수동 입력 버튼 
    st.markdown(f"""
                <div class='section-title'>
                {t('weather_section_title')} 🌦️
                </div>
                """, 
                unsafe_allow_html=True)
    st.write(t('weather_subsection_sent'))

    latitude = st.session_state.latitude
    longitude = st.session_state.longitude
    location_ready = (
        st.session_state.location_mode == "ready" 
        and st.session_state.latitude is not None 
        and st.session_state.longitude is not None
        )

    col1, col2 = st.columns(2)
    with col1: 
        request_weather = st.button(t('auto_weather_button'))
    with col2:
        use_manual_weather = st.button(t('manual_weather_button'))
    
    target_time = f"{target_date_str}T{target_hour:02d}:00"

    if use_manual_weather:
        st.session_state.weather_input_mode = "manual"
        st.session_state.weather_code = None
        st.session_state.manual_weather_summary_input = ""
        st.session_state.shortwave_radiation_sum = None
    if st.session_state.weather_input_mode == "manual":
        st.write(t('manual_weather_input_info'))
        st.session_state.weather_summary = st.selectbox(
            t('manual_today_weather'), 
            [t('clear_sky'), t('cloudy'), t('rain'), t('heavy_rain'), t('snow'), t('heavy_snow'), t('rain_showers'), t('thunderstorm_lightning')]
        )
        st.session_state.temperature = st.number_input(f"{t('temperature')}(°C)", value=20.0, format="%.1f")
        st.session_state.humidity = st.number_input(f"{t('humidity')}(%)", min_value=0, max_value=100, value=50)
        st.session_state.daylight_duration_hours = st.number_input(f"{t('daylight_duration')}({t('hour_unit')})", min_value=0.0, value=0.0, step=0.1, format="%.1f")
        st.session_state.daylight_duration = int(st.session_state.daylight_duration_hours * 3600)
                # 수동 입력 시 daylight duration을 바탕으로 sunshine duration을 추정
        weather_summary = st.session_state.weather_summary
        daylight_duration_hours = st.session_state.daylight_duration_hours
        st.session_state.sunshine_duration_hours = estimate_sunshine_duration(daylight_duration_hours, weather_summary)
        st.session_state.sunshine_duration = int(st.session_state.sunshine_duration_hours * 3600)

        sunshine_intensity_label_map = {
            t('sunshine_intensity_very_weak'): 1,
            t('sunshine_intensity_weak'): 2,
            t('sunshine_intensity_moderate'): 3,
            t('sunshine_intensity_strong'): 4,
            t('sunshine_intensity_very_strong'): 5
        }
        sunshine_intensity_label = st.select_slider(t('sunshine_intensity'), 
                                        options=list(sunshine_intensity_label_map.keys()),
                                        value=t('sunshine_intensity_moderate'))
        st.session_state.sunshine_intensity_label = sunshine_intensity_label_map[sunshine_intensity_label]

        st.session_state.pm2_5 = st.number_input(f"{t('fine_dust')} PM2.5 (µg/m³)", min_value=0.0, value=5.0)
        st.session_state.pm10 = st.number_input(f"{t('fine_dust')} PM10 (µg/m³)", min_value=0.0, value=10.0)
        
        if st.button(t('save_weather_button')):
            st.success(t('weather_saved_info'))
            st.session_state.weather_reference_time = target_date_str
            st.session_state.weather_input_mode = "saved"

    if request_weather:
        st.session_state.weather_input_mode = "auto_pending"
    if st.session_state.weather_input_mode == "auto_pending":
        if not location_ready:
            st.warning(t('set_location_first_info'))
            st.stop()
        #날씨 정보 가져오기 
        selected_region = st.session_state.get("region", "Seoul")
        timezone = region_and_timezone.get(str(selected_region), "Asia/Seoul")
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "past_days": 7,
            "forecast_days": 1,
            "hourly": "temperature_2m,relative_humidity_2m,weather_code",
            "daily": "sunshine_duration,shortwave_radiation_sum,daylight_duration",
            "timezone": timezone,
        }
        weather_data = get_json_with_retry(weather_url, weather_params, t("weather"))
        
        #미세먼지 정보 가져오기 
        air_quality_params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "pm2_5,pm10",
            "timezone": timezone,
            "past_days": 7,
            "forecast_days": 1,
        }
        air_quality_data = get_json_with_retry(air_quality_url, air_quality_params, t("air_quality")) 

        #날씨와 미세먼지 데이터에서 필요한 정보 추출
        weather_times = weather_data["hourly"]["time"]
        temperatures = weather_data["hourly"]["temperature_2m"]
        humidities = weather_data["hourly"]["relative_humidity_2m"]
        weather_codes = weather_data["hourly"]["weather_code"] 

        daily_dates = weather_data["daily"]["time"]
        sunshine_durations = weather_data["daily"]["sunshine_duration"]
        shortwave_radiation_sums = weather_data["daily"]["shortwave_radiation_sum"]
        daylight_durations = weather_data["daily"]["daylight_duration"]

        air_quality_times = air_quality_data["hourly"]["time"]
        pm2_5_values = air_quality_data["hourly"]["pm2_5"]
        pm10_values = air_quality_data["hourly"]["pm10"]

        if target_time in weather_times and target_date_str in daily_dates and target_time in air_quality_times:
            weather_index = weather_times.index(target_time)
            daily_index = daily_dates.index(target_date_str)
            air_quality_index = air_quality_times.index(target_time)

            st.session_state.temperature = temperatures[weather_index]
            st.session_state.humidity = humidities[weather_index]
            st.session_state.sunshine_duration = sunshine_durations[daily_index]
            st.session_state.sunshine_duration_hours = st.session_state.sunshine_duration / 3600
            st.session_state.shortwave_radiation_sum = shortwave_radiation_sums[daily_index]
            st.session_state.daylight_duration = daylight_durations[daily_index]
            st.session_state.daylight_duration_hours = (st.session_state.daylight_duration / 3600)
            st.session_state.sunshine_intensity_label = None
            st.session_state.weather_code = weather_codes[weather_index]

            if st.session_state.weather_code in weather_code_map:  
                st.session_state.weather_summary = weather_code_map[st.session_state.weather_code]
                st.session_state.weather_input_mode = "saved"
            else:
                st.session_state.weather_input_mode = "awaiting_summary"
                st.session_state.weather_summary = ""
                st.session_state.manual_weather_summary_input = ""

            st.session_state.pm2_5 = pm2_5_values[air_quality_index]
            st.session_state.pm10 = pm10_values[air_quality_index]
            
            target_time_display = target_time.split("T")[1]
            st.session_state.weather_reference_time = f"{target_date_str} ({target_time_display})"
            
        else:
            st.warning(t('weather_fail_info'))

    if st.session_state.weather_input_mode == "awaiting_summary":
        st.write(t('manual_weather_summary_info'))
        st.write(t('manual_weather_summary_example'))
        st.session_state.manual_weather_summary_input = st.text_input(t('manual_weather_summary_input_sent'), value=st.session_state.manual_weather_summary_input)
        if st.button(t('manual_weather_summary_save_button')):
            if st.session_state.manual_weather_summary_input.strip() =="":
                st.warning(t('manual_weather_summary_blank_info'))
            else:  
                st.session_state.weather_summary = st.session_state.manual_weather_summary_input.strip()
                st.session_state.weather_input_mode = "saved"
                st.success(t('manual_weather_summary_save_info'))
            
    if st.session_state.weather_input_mode == "saved" and st.session_state.weather_summary not in [None, ""]:
        st.markdown(f"""
                    <div class="subsection-title">
                    {t('today_weather')}
                    </div>
                    """, unsafe_allow_html=True)
        st.write(f"{t('target_time')}: {st.session_state.weather_reference_time}")
        col1, col2 = st.columns(2)
        with col1: 
            st.write(f"{t('weather_summary')}: {st.session_state.weather_summary}")
            st.write(f"{t('temperature')}: {st.session_state.temperature}°C")
            st.write(f"{t('humidity')}: {st.session_state.humidity}%")
            st.write(f"{t('daylight_duration')}: {st.session_state.daylight_duration_hours:.1f} {t('hour_unit')}")
        with col2:
            st.write(f"{t('sunshine_duration')}: {st.session_state.sunshine_duration_hours:.1f} {t('hour_unit')}")

            if st.session_state.sunshine_intensity_label is not None:
                sunshine_display = level_text_map.get(st.session_state.sunshine_intensity_label, "정보 없음")
                st.write(f"{t('sunshine_intensity')}: {sunshine_display}")
            else:
                st.write(f"{t('sunshine_intensity')}: {st.session_state.shortwave_radiation_sum}")

            st.write(f"{t('fine_dust')} PM2.5 : {st.session_state.pm2_5} µg/m³")
            st.write(f"{t('fine_dust')} PM10 : {st.session_state.pm10} µg/m³")

        if st.button(t('edit_weather_summary_button')):
            st.session_state.weather_input_mode = "awaiting_summary"
            st.session_state.manual_weather_summary_input = st.session_state.weather_summary
            st.rerun()        
        
    # ==============================================
    ### 기분 입력
    # ==============================================
    st.markdown(f"""
                <div class="section-title">
                {t('mood_section_title')} 😊
                </div>
                """, unsafe_allow_html=True)
    state_map={
        t('very_bad'): 1,
        t('bad'): 2,
        t('moderate'): 3,
        t('good'): 4,
        t('very_good'): 5
    }
    st.markdown(f"""
                <div class="subsection-title">
                {t('mood_subsection_title')}
                </div>
                """, unsafe_allow_html=True)
    st.write(t('mood_subsection_sent'))
    mood_user_input = st.select_slider("mood", 
                            options=[t('very_bad'), t('bad'), t('moderate'), t('good'), t('very_good')], 
                            value = t('moderate'), 
                            label_visibility="collapsed"
    )
    mood = state_map[mood_user_input]

    st.markdown(f"""
                <div class="subsection-title">
                {t('focus_subsection_title')}🤓
                </div>
                """, unsafe_allow_html=True)
    st.write(t('focus_subsection_sent'))
    focus_user_input = st.select_slider("Focus level", 
                            options=[t('very_bad'), t('bad'), t('moderate'), t('good'), t('very_good')], 
                            value = t('moderate'),
                            label_visibility="collapsed"
    )
    focus = state_map[focus_user_input]

    three_level_state_map = {
        t('no'): 0,
        t('slightly_yes'): 1,
        t('very_yes'): 2
    }
    st.markdown(f"""
                <div class="subsection-title">
                {t('irritability_subsection_title')}😡
                </div>
                """, unsafe_allow_html=True)
    st.write(t('irritability_subsection_sent'))
    irritability_user_input = st.select_slider("Irritability level",
                            options=[t('no'), t('slightly_yes'), t('very_yes')],
                            label_visibility="collapsed"
    ) 
    irritability = three_level_state_map[irritability_user_input]

    st.markdown(f"""
            <div class="subsection-title">
            {t("depression_subsection_title")}😔
            </div>
            """, unsafe_allow_html=True)
    st.write(t("depression_subsection_sent"))
    depression_user_input = st.select_slider("Depression level",
                            options=[t("no"), t("slightly_yes"), t("very_yes")],
                            label_visibility="collapsed"
    )
    depression = three_level_state_map[depression_user_input]

    # =================================================
    # 생활 변수 기록 
    # =================================================
    st.markdown(f"""
                <div class="section-title">
                {t('lifestyle_section_title')}🏃‍➡️
                </div>
                """, unsafe_allow_html=True)
    sleep_quality_map = {
        t('sleep_quality_bad'): 0,
        t('sleep_quality_okay'): 1,
        t('sleep_quality_good'): 2
    }
    st.markdown(f"""
                <div class="subsection-title">
                {t('sleep_subsection_title')} 🛌
                </div>
                """, unsafe_allow_html=True)
    
    default_bed_time_value = time_text_to_time(st.session_state.get("default_bed_time", "23:00"), dt.time(23, 0))
    default_wake_time_value = time_text_to_time(st.session_state.get("default_wake_time", "08:00"), dt.time(8, 0))

    bed_col, wake_col = st.columns(2)
    with bed_col:
        sleep_bed_time = st.time_input(t('bed_time'), value=default_bed_time_value)
    with wake_col:
        sleep_wake_time = st.time_input(t('wake_time'), value=default_wake_time_value)
    sleep_duration_hours = calculate_sleep_duration_hours(sleep_bed_time, sleep_wake_time)
    st.caption(f"{t('sleep_duration')} : {sleep_duration_hours:.1f} {t('hour_unit')}")

    sleep_quality_input = st.select_slider(t('sleep_quality_sent'), options = [t('sleep_quality_bad'), t('sleep_quality_okay'), t('sleep_quality_good')], value = t('sleep_quality_okay'))
    sleep_quality = sleep_quality_map[sleep_quality_input]
    
    st.markdown(f"""
                <div class="subsection-title">
                {t('other_lifestyle_subsection_title')}
                </div>
                """, unsafe_allow_html=True)
    did_exercise = st.checkbox(f"{t('exercise_sent')}💪🏼")
    had_major_stress = st.checkbox(f"{t('major_stress_event_sent')}😰")
    went_outside = st.checkbox(f"{t('went_outside_sent')}☀️")

    st.markdown(f"""
                <div class="subsection-title">
                {t('free_text_subsection_title')} 📝
                </div>
                """, unsafe_allow_html=True)
    st.write(t('free_text_subsection_sent'))
    if "free_text_input" not in st.session_state:
        st.session_state.free_text_input = st.session_state.get("default_free_text", "")
    elif st.session_state.free_text_input == "":
        st.session_state.free_text_input = st.session_state.get("default_free_text", "")
    free_text = st.text_area("free_text", 
                             key="free_text_input",
                             label_visibility="collapsed")
    free_text = free_text.strip()



    # =================================
    #입력된 정보를 저장
    if "final_save_mode" not in st.session_state:
        st.session_state.final_save_mode = "pending"

    if st.session_state.final_save_mode == "pending" or st.session_state.final_save_mode == "editing":
        csv_path = DATA_PATH
        same_date_indices = []
        existing_df = None

        if pl.Path(csv_path).exists():
            existing_df = pd.read_csv(csv_path)
            same_date_indices = existing_df.index[existing_df["target_date"].astype(str) == target_date_str].tolist()
                
        if same_date_indices and st.session_state.final_save_mode != "editing":
            st.warning(t('overwrite_data_info')) 
        
        st.markdown(f"""
            <div class="subsection-title">
            {t('save_record_subsection_title')}
            </div>
            """, unsafe_allow_html=True)
        if st.button(t('submit_button')):
            if st.session_state.weather_input_mode != "saved":
                st.warning(t('save_weather_first_info'))
                st.stop()
            
            #default 문구와 입력값이 동일한 경우 기록 없음으로 간주
            default_free_text = st.session_state.get("default_free_text", "").strip()
            if free_text == default_free_text:
                free_text = ""

            record = {
            "recorded_at": current_time_str,
            "target_date": target_date_str,
            "target_hour": target_hour,
            "region": st.session_state.get("region", "Seoul" ),
            "latitude": st.session_state.get("latitude", 37.5665),
            "longitude": st.session_state.get("longitude", 126.9780),
            "weather_reference_time": st.session_state.weather_reference_time,
            "weather_summary": st.session_state.weather_summary,
            "weather_code": st.session_state.weather_code,
            "temperature_c": st.session_state.temperature,
            "humidity_percent": st.session_state.humidity,
            "sunshine_duration_seconds": st.session_state.sunshine_duration,
            "sunshine_duration_hours": st.session_state.sunshine_duration_hours,
            "daylight_duration_seconds": st.session_state.daylight_duration,
            "daylight_duration_hours": st.session_state.daylight_duration_hours,
            "shortwave_radiation_sum": st.session_state.shortwave_radiation_sum,
            "sunshine_intensity_label": st.session_state.sunshine_intensity_label,
            "pm2_5": st.session_state.pm2_5,
            "pm10": st.session_state.pm10,
            "mood": mood,
            "focus": focus,
            "irritability": irritability,
            "depression": depression,
            "sleep_bed_time": sleep_bed_time.strftime("%H:%M"),
            "sleep_wake_time": sleep_wake_time.strftime("%H:%M"),
            "sleep_duration_hours": sleep_duration_hours,
            "sleep_quality": sleep_quality,
            "did_exercise": did_exercise,
            "had_major_stress": had_major_stress,
            "went_outside": went_outside,
            "free_text": free_text,
    }   
            
            new_row_df = pd.DataFrame([record])

            if pl.Path(csv_path).exists():
                
                #pandas dtype 혼동 예방 
                text_columns = [
                    "recorded_at",
                    "target_date",
                    "region",
                    "weather_reference_time",
                    "weather_summary",
                    "sleep_bed_time",
                    "sleep_wake_time",
                    "free_text"
                ]
                for text_col in text_columns:
                    if text_col in existing_df.columns:
                        existing_df[text_col] = existing_df[text_col].astype("object")
                
                if st.session_state.final_save_mode == "editing":
                    if same_date_indices:
                        target_index_to_update = same_date_indices[-1]
                    else:
                        target_index_to_update = existing_df.index[-1]
                    for col in new_row_df.columns:
                        existing_df.loc[target_index_to_update, col] = new_row_df.iloc[0][col]
                    combined_df = existing_df

                elif same_date_indices:
                    target_index_to_update = same_date_indices[-1]
                    for col in new_row_df.columns:
                        existing_df.loc[target_index_to_update, col] = new_row_df.iloc[0][col]
                    combined_df = existing_df
                else:
                    combined_df = pd.concat([existing_df, new_row_df], ignore_index=True)
            else:
                combined_df = new_row_df

            combined_df.to_csv(csv_path, index=False)
            st.session_state.final_save_mode = "saved"
            st.rerun()

    if st.session_state.final_save_mode == "saved":
        st.success(t('data_saved_info'))
        if st.button(t('modify_data_button')):
            st.session_state.final_save_mode = "editing"
            st.rerun()

    st.markdown("---")
    if st.button(t("exit_app_button")):
        st.info(t("exit_app_info"))
        time.sleep(10)
        os.kill(os.getpid(), signal.SIGTERM)

# ==================================================
# 통계 페이지
# ==================================================
if selected_page == t('statistics_menu'):
    ###통계 내기, 그래프 작성
    st.subheader(t('statistics_big_section_title'))
    csv_path = DATA_PATH
    if not pl.Path(csv_path).exists():
        st.info(t('no_saved_record_info'))
        st.stop()
    else:
        df = pd.read_csv(csv_path) #df = abb. of DataFrame
        df["target_date"] = pd.to_datetime(df["target_date"])
    
    st.write(f"{t('total_saved_record_num')}: {len(df)} {t('day_unit')}")


    #DataFrame 전체에 분석용 지표 열 추가
    df["sunshine_index"] = df.apply(compute_sunshine_index, axis = 1)
    df["sunshine_ratio"] = df.apply(compute_sunshine_ratio, axis = 1)
    df["clear_weather_bonus"] = df["weather_summary"].apply(clear_weather_bonus)
    df["precipitation_ox"] = df["weather_summary"].apply(precipitation_ox)
    df["thunderstorm_ox"] = df["weather_summary"].apply(thunderstorm_ox)
    df["air_quality_index"] = df.apply(compute_air_quality_index, axis = 1)
    df["temperature_penalty"] = df["temperature_c"].apply(temperature_penalty)
    df["humidity_penalty"] = df["humidity_percent"].apply(humidity_penalty)
    df["environment_index"] = df.apply(compute_environment_index, axis = 1)
    df["overall_mood_index"] = df.apply(compute_overall_mood_index, axis = 1)
    df["sleep_index"] = df.apply(compute_sleep_index, axis = 1)
    df["sleep_bed_minute_std_7d"] = df.apply(lambda row: compute_sleep_consistency_std(df, row["target_date"], "sleep_bed_time"), axis=1)
    df["sleep_wake_minute_std_7d"] = df.apply(lambda row: compute_sleep_consistency_std(df, row["target_date"], "sleep_wake_time"), axis=1)
    df["sleep_bed_consistency_index"] = df["sleep_bed_minute_std_7d"].apply(compute_sleep_consistency_std_index)
    df["sleep_wake_consistency_index"] = df["sleep_wake_minute_std_7d"].apply(compute_sleep_consistency_std_index)
    df["overall_sleep_consistency_index"] = df[["sleep_bed_consistency_index", "sleep_wake_consistency_index"]].mean(axis=1)

    sleep_consistency_columns = [
        "sleep_bed_consistency_index",
        "sleep_wake_consistency_index",
        "overall_sleep_consistency_index"
    ]

    for column in sleep_consistency_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        #계산 가능한 값은 숫자로, 계산 불가한 값(None)은 NaN으로 바꿈. 이렇게 해야 통계 돌리는 게 가능해짐.
        #NaN(not a number)은 numpy, pandas의 결측값. type은 float. None은 숫자 계산이 불가하지만, NaN은 모든 연산에 대해 결과값이 NaN인 계산 가능한 결측값임.


    boolean_lifestyle_columns = [
        "did_exercise",
        "had_major_stress",
        "went_outside",
    ]
    for column in boolean_lifestyle_columns:
        if column in df.columns:
            df[column] = df[column].apply(boolean_to_int)

    df["temperature_discomfort"] = -df["temperature_penalty"]
    df["humidity_discomfort"] = -df["humidity_penalty"]



    # ====================================================
    ## 분석을 위한 변수들과 그 분류

    correlation_columns = [ #상관관계 분석이 가능한 변수들의 목록
        "environment_index",
        "overall_mood_index",
        "sunshine_index",
        "air_quality_index",
        "clear_weather_bonus",
        "precipitation_ox",
        "thunderstorm_ox",
        "temperature_discomfort",
        "humidity_discomfort",
        "mood",
        "focus",
        "irritability",
        "depression",
        "sleep_duration_hours",
        "sleep_quality",
        "overall_sleep_consistency_index",
        "sleep_bed_consistency_index",
        "sleep_wake_consistency_index",
        "sleep_index",
        "did_exercise",
        "had_major_stress",
        "went_outside"
    ]


    display_name_map = { #사용자에게 보이는 자연어 
        "environment_index": t('environment_index'),
        "overall_mood_index": t('overall_mood_index'),
        "sunshine_index": t('sunshine_index'),
        "sunshine_ratio": t('sunshine_ratio'),
        "air_quality_index": t('air_quality_index'),
        "clear_weather_bonus": t('clear_weather_bonus'),
        "precipitation_ox": t('precipitation_ox'),
        "thunderstorm_ox": t('thunderstorm_ox'),
        "temperature_discomfort": t('temperature_discomfort'),
        "humidity_discomfort": t('humidity_discomfort'),
        "mood": t('mood'),
        "focus": t('focus'),
        "irritability": t('irritability'),
        "depression": t('depression'),
        "sleep_duration_hours": t('sleep_duration_hours'),
        "sleep_quality" : t('sleep_quality'),
        "overall_sleep_consistency_index": t('overall_sleep_consistency_index'),
        "sleep_bed_consistency_index": t('sleep_bed_consistency_index'),
        "sleep_wake_consistency_index": t('sleep_wake_consistency_index'),
        "sleep_index": t('sleep_index'),
        "did_exercise": t('did_exercise'),
        "had_major_stress": t('had_major_stress'),
        "went_outside": t('went_outside')

    }

    correlation_phrase_map_1 = {
        "environment_index": t('environment_index_corr1'),
        "sunshine_index": t('sunshine_index_corr1'),
        "sunshine_ratio": t('sunshine_ratio_corr1'),
        "air_quality_index": t('air_quality_index_corr1'),
        "clear_weather_bonus": t('clear_weather_bonus_corr1'),
        "precipitation_ox": t('precipitation_ox_corr1'),
        "thunderstorm_ox": t('thunderstorm_ox_corr1'),
        "temperature_discomfort": t('temperature_discomfort_corr1'),
        "humidity_discomfort": t('humidity_discomfort_corr1'),
        "sleep_duration_hours": t('sleep_duration_hours_corr1'),
        "sleep_quality" : t('sleep_quality_corr1'),
        "sleep_index": t('sleep_index_corr1'),
        "overall_sleep_consistency_index": t('overall_sleep_consistency_index_corr1'),
        "sleep_bed_consistency_index": t('sleep_bed_consistency_index_corr1'),
        "sleep_wake_consistency_index": t('sleep_wake_consistency_index_corr1'),
        "did_exercise": t('did_exercise_corr1'),
        "had_major_stress": t('had_major_stress_corr1'),
        "went_outside": t('went_outside_corr1'),
    }

    correlation_phrase_map_2_increase = {
        "overall_mood_index": t('overall_mood_index_corr2_increase'),
        "mood": t('mood_corr2_increase'),
        "focus": t('focus_corr2_increase'),
        "irritability": t('irritability_corr2_increase'),
        "depression": t('depression_corr2_increase'),
        "sleep_duration_hours": t('sleep_duration_hours_corr2_increase'),
        "sleep_quality" : t('sleep_quality_corr2_increase'),
        "overall_sleep_consistency_index": t('overall_sleep_consistency_index_corr2_increase'),
        "sleep_bed_consistency_index": t('sleep_bed_consistency_index_corr2_increase'),
        "sleep_wake_consistency_index": t('sleep_wake_consistency_index_corr2_increase'),
        "sleep_index": t('sleep_index_corr2_increase'),
        "did_exercise": t('did_exercise_corr2_increase'),
        "had_major_stress": t('had_major_stress_corr2_increase'),
        "went_outside": t('went_outside_corr2_increase')

    }

    correlation_phrase_map_2_decrease = {
        "overall_mood_index": t('overall_mood_index_corr2_decrease'),
        "mood": t('mood_corr2_decrease'),
        "focus": t('focus_corr2_decrease'),
        "irritability": t('irritability_corr2_decrease'),
        "depression": t('depression_corr2_decrease'),
        "sleep_duration_hours": t('sleep_duration_hours_corr2_decrease'),
        "sleep_quality" : t('sleep_quality_corr2_decrease'),
        "overall_sleep_consistency_index": t('overall_sleep_consistency_index_corr2_decrease'),
        "sleep_bed_consistency_index": t('sleep_bed_consistency_index_corr2_decrease'),
        "sleep_wake_consistency_index": t('sleep_wake_consistency_index_corr2_decrease'),
        "sleep_index": t('sleep_index_corr2_decrease'),
        "did_exercise": t('did_exercise_corr2_decrease'),
        "had_major_stress": t('had_major_stress_corr2_decrease'),
        "went_outside": t('went_outside_corr2_decrease')

    }


    #자연어 메세지 처리에 활용할 type map
    correlation_columns_type_map = { 
        "environment_index": "scale",
        "overall_mood_index": "scale",
        "sunshine_index": "scale",
        "sunshine_ratio": "scale",
        "air_quality_index": "scale",
        "clear_weather_bonus": "event",
        "precipitation_ox": "event",
        "thunderstorm_ox": "event",
        "temperature_discomfort": "scale",
        "humidity_discomfort": "scale",
        "mood": "scale",
        "focus": "scale",
        "irritability": "scale",
        "depression": "scale",
        "sleep_duration_hours": "scale",
        "sleep_quality": "scale",
        "sleep_index": "scale",
        "overall_sleep_consistency_index": "scale",
        "sleep_bed_consistency_index": "scale",
        "sleep_wake_consistency_index": "scale",
        "did_exercise": "event",
        "had_major_stress": "event",
        "went_outside": "event"
    }

    #변수의 종류를 알려주는 맵
    correlation_columns_group_map = {
        "environment_index": "environment",
        "overall_mood_index": "mood",
        "sunshine_index": "environment",
        "sunshine_ratio": "environment",
        "air_quality_index": "environment",
        "clear_weather_bonus": "environment",
        "precipitation_ox": "environment",
        "thunderstorm_ox": "environment",
        "temperature_discomfort": "environment",
        "humidity_discomfort": "environment",
        "mood": "mood",
        "focus": "mood",
        "irritability": "mood",
        "depression": "mood",
        "sleep_duration_hours": "lifestyle",
        "sleep_quality": "lifestyle",
        "sleep_index": "lifestyle",
        "overall_sleep_consistency_index": "lifestyle",
        "sleep_bed_consistency_index": "lifestyle",
        "sleep_wake_consistency_index": "lifestyle",
        "did_exercise": "lifestyle",
        "had_major_stress": "lifestyle",
        "went_outside": "lifestyle",
    }

    #분석 가능한 변수 종류의 쌍
    allowed_correlation_pairs = {
        frozenset(["environment", "mood"]),
        frozenset(["environment", "lifestyle"]),
        frozenset(["mood", "lifestyle"])
    }

    #분석 가능한 변수 종류의 쌍인지 알려주는 함수 
    def is_allowed_comparison(column1, column2):
        if column1 == column2:
            return False
        group1 = correlation_columns_group_map.get(column1)
        group2 = correlation_columns_group_map.get(column2)
        if group1 is None or group2 is None:
            return False
        return frozenset([group1, group2]) in allowed_correlation_pairs


    available_correlation_columns = [ #형식이 수인 것들만 분석 대상으로 삼음. 이미 숫자로의 변형을 모두 마친 상태이므로, 설계 상 correlation_columns의 모든 변수가 들어간다. 
        column for column in correlation_columns
        if column in df.columns and pd.api.types.is_numeric_dtype(df[column])
    ]

    reverse_display_name_map={ #분석 가능한 것만 가져와서, display name map을 뒤집음. '자연어:변수명' 꼴이 됨.
        display_name: column_name
        for column_name, display_name in display_name_map.items()
        if column_name in available_correlation_columns
    }

    def display_message_parts(message_parts):
        if isinstance(message_parts, list):
            for part in message_parts:
                st.write(part)
        else:
            st.write(message_parts)
    
    # ===================================
    #기본그래프 - 시간에 따른 종합 환경 지수와 기분 지수의 변화 추이 
    st.subheader(t('basic_graph_subsection_title'))
    if "show_environment_index" not in st.session_state:
        st.session_state.show_environment_index = True
    if "show_mood" not in st.session_state:
        st.session_state.show_mood = False
    if "show_focus" not in st.session_state:
        st.session_state.show_focus = False
    if "show_irritability_chart" not in st.session_state:
        st.session_state.show_irritability_chart = False
    if "show_depression_chart" not in st.session_state:
        st.session_state.show_depression_chart = False
    if "smoothen_line_chart" not in st.session_state:
        st.session_state.smoothen_line_chart = True
    if "smooth_line_chart_window" not in st.session_state:
        st.session_state.smooth_line_chart_window = 3

    #그래프로 표시할 변수들의 목록
    line_chart_columns = ["overall_mood_index"]
    if st.session_state.show_environment_index:
        line_chart_columns.append("environment_index")
    if st.session_state.show_mood:
        line_chart_columns.append("mood")
    if st.session_state.show_focus:
        line_chart_columns.append("focus")
    if st.session_state.show_irritability_chart:
        line_chart_columns.append("irritability_chart")
    if st.session_state.show_depression_chart:
        line_chart_columns.append("depression_chart")

    line_chart_df = df.sort_values("target_date").set_index("target_date")

    line_chart_df["irritability_chart"] = line_chart_df["irritability"] * 2.5
    line_chart_df["depression_chart"] = line_chart_df["depression"] * 2.5

    # 그래프 하단에 display될 변수들의 이름의 목록
    line_chart_display_name_map = {
        column: display_name_map.get(column, column) 
        for column in line_chart_columns
    }
    line_chart_display_name_map["irritability_chart"] = t('irritability')
    line_chart_display_name_map["depression_chart"] = t('depression')

    display_line_chart_df = line_chart_df[line_chart_columns].rename(columns=line_chart_display_name_map)
    if st.session_state.smoothen_line_chart and len(display_line_chart_df) >= st.session_state.smooth_line_chart_window:
        display_line_chart_df = display_line_chart_df.rolling(window=st.session_state.smooth_line_chart_window, min_periods=1).mean()

    # 그래프 선 색상 지정
    line_chart_color_map = {
        t('environment_index'): "#6F8A6A",      # muted green
        t('overall_mood_index'): "#8A6A5B",  # muted brown
        t('mood'): "#B07A7A",      # muted rose
        t('focus'): "#6D8196",         # muted blue
        t('irritability'): "#8B6F96",    # muted purple
        t('depression'): "#5A5148"          # dusty gray-purple
    }
    chart_colors = []
    for column in display_line_chart_df.columns:
        chart_colors.append(
            line_chart_color_map.get(column, "#6F8A6A")
        )
    
    # display code
    st.line_chart(display_line_chart_df, color=chart_colors)
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox(t('display_environment_index'), key = "show_environment_index")
        st.checkbox(t('display_overall_mood_index'), key = "show_mood")
        st.checkbox(t('display_focus'), key = "show_focus")
    with col2:
        st.checkbox(t('display_irritability'), key = "show_irritability_chart")
        st.checkbox(t('display_depression'), key = "show_depression_chart")
        st.checkbox(t('smoothen_chart'), key = "smoothen_line_chart")


    # ====================================
    #상관관계
    # ====================================
    st.subheader(t('correlation_subsection_title'))
    if "correlation_mode" not in st.session_state:
        st.session_state.correlation_mode = "pending"

    # 변수에 따른 적절한 메세지 형식을 산출하는 함수 
    def compute_correlation_message(column1, column2):
        message_parts = []
        valid_mask = df[column1].notna() & df[column2].notna()
        #valid_mask는 column1과 column2 모두에 값이 존재하는 행을 나타내는 불리언 시리즈입니다. 상관관계 계산은 두 변수 모두에 유효한 데이터가 있는 행에서만 수행되어야 하므로, valid_mask를 사용하여 이러한 행을 필터링합니다.
        if valid_mask.sum() < 2:
            return [t('not_enough_data_corr_info')]
        
        def correlation_strength_message(correlation_num):
            abs_corr = abs(correlation_num)
            if abs_corr < 0.2:
                return t('no_correlation_sent')
            elif abs_corr < 0.4:
                return t('weak_correlation_sent')
            elif abs_corr < 0.6:
                return t('moderate_correlation_sent')
            elif abs_corr < 0.8:
                return t('strong_correlation_sent')
            else:
                return t('very_strong_correlation_sent')

        def percent_text(value):
            return f"{value * 100 :.1f}%"
        
        column1_type = correlation_columns_type_map[column1]
        column2_type = correlation_columns_type_map[column2]
        column1_name = display_name_map[column1] #선택 란에 나왔던 그 변수의 이름임.
        column2_name = display_name_map[column2]
        column1_phrase = correlation_phrase_map_1.get(column1, column1_name)
        column2_phrase_map = {
            "positive": correlation_phrase_map_2_increase.get(column2, column2_name),
            "negative": correlation_phrase_map_2_decrease.get(column2, column2_name)
        }
        base_kwargs = {
            "column1_name" : column1_name,
            "column2_name" : column2_name,
            "column1_phrase" : column1_phrase,
        }

        if column1_type == "event" and column2_type == "event":
            event_o_mean = df.loc[valid_mask & (df[column1] == 1), column2].mean()
            event_x_mean = df.loc[valid_mask & (df[column1] == 0), column2].mean()
            if pd.isna(event_o_mean) or pd.isna(event_x_mean):
                return [t('not_enough_data_corr_info')]
            selected_column2_phrase = column2_phrase_map.get("positive", column2_name)
            event_o_mean_percent = percent_text(event_o_mean)
            event_x_mean_percent = percent_text(event_x_mean)
            difference = event_o_mean - event_x_mean
            difference_percent_ee = percent_text(abs(difference))
            selected_column2_phrase = column2_phrase_map.get("positive", column2_name)
            selected_column2_phrase_shortened = selected_column2_phrase[:-4].strip()
            common_kwargs = {
                **base_kwargs,
                "event_o_mean_percent": event_o_mean_percent,
                "event_x_mean_percent": event_x_mean_percent,
                "difference_percent_ee": difference_percent_ee,
                "selected_column2_phrase": selected_column2_phrase,
                "selected_column2_phrase_shortened": selected_column2_phrase_shortened,
                }

            message_parts.append(t_sent("event_event_ratio", **common_kwargs))
            if abs(difference) < 0.1:
                message_parts.append(t_sent("event_event_no_relation", **common_kwargs))
            elif difference > 0:
                message_parts.append(t_sent("event_event_positive", **common_kwargs))
            else:
                message_parts.append(t_sent("event_event_negative", **common_kwargs))
        
        elif column1_type == "event" and column2_type == "scale":
            event_o_mean = df.loc[valid_mask & (df[column1] == 1), column2].mean()
            event_x_mean = df.loc[valid_mask & (df[column1] == 0), column2].mean()
            if pd.isna(event_o_mean) or pd.isna(event_x_mean):
                return [t('not_enough_data_corr_info')]
            event_o_mean_percent = percent_text(event_o_mean)
            event_x_mean_percent = percent_text(event_x_mean)
            difference = event_o_mean - event_x_mean
            difference_percent_es = round(abs(difference), 2)
            selected_column2_phrase = column2_phrase_map.get("positive", column2_name)
            selected_column2_phrase_shortened = selected_column2_phrase[:-4].strip()
            common_kwargs = {
                **base_kwargs,
                "event_o_mean": event_o_mean,
                "event_x_mean": event_x_mean,
                "event_o_mean_percent": event_o_mean_percent,
                "event_x_mean_percent": event_x_mean_percent,
                "difference": difference,
                "difference_percent_es": difference_percent_es,
                "selected_column2_phrase": selected_column2_phrase,
                "selected_column2_phrase_shortened": selected_column2_phrase_shortened
            }
            message_parts.append(t_sent("event_scale_ratio", **common_kwargs))
            difference = event_o_mean - event_x_mean
            if abs(difference) < 0.1:
                message_parts.append(t_sent("event_scale_no_relation", **common_kwargs))
            elif difference > 0:
                message_parts.append(t_sent("event_scale_positive", **common_kwargs))
            else:
                message_parts.append(t_sent("event_scale_negative", **common_kwargs))
        
        elif column1_type == "scale" and column2_type == "scale":
            correlation_num = df.loc[valid_mask, column1].corr(df.loc[valid_mask, column2])
            if pd.isna(correlation_num):
                return [t('not_enough_data_corr_info')]
            if correlation_num > 0:
                selected_column2_phrase = column2_phrase_map['positive']
            else:
                selected_column2_phrase = column2_phrase_map['negative']
            strength = correlation_strength_message(correlation_num)
            selected_column2_phrase_shortened = selected_column2_phrase[:-4].strip()
            common_kwargs = {
                **base_kwargs,
                "correlation_num": correlation_num,
                "strength": strength,
                "selected_column2_phrase": selected_column2_phrase,
                "selected_column2_phrase_shortened": selected_column2_phrase_shortened
            }
            message_parts.append(t_sent("scale_scale_corr", **common_kwargs))
            if abs(correlation_num) < 0.2:
                message_parts.append(t_sent("scale_scale_strength", **common_kwargs))
            elif correlation_num > 0:
                message_parts.append(t_sent("scale_scale_positive", **common_kwargs))
            else:
                message_parts.append(t_sent("scale_scale_negative", **common_kwargs))
        
        elif column1_type == "scale" and column2_type == "event":
            correlation_num = df.loc[valid_mask, column1].corr(df.loc[valid_mask, column2])
            if pd.isna(correlation_num):
                return [t('not_enough_data_corr_info')]
            if correlation_num > 0:
                selected_column2_phrase = column2_phrase_map["positive"]
            else:
                selected_column2_phrase = column2_phrase_map["negative"]
            strength = correlation_strength_message(correlation_num)
            selected_column2_phrase_shortened = selected_column2_phrase[:-4].strip()
            common_kwargs = {
                **base_kwargs,
                "selected_column2_phrase": selected_column2_phrase,
                "selected_column2_phrase_shortened": selected_column2_phrase_shortened,
                "correlation_num": correlation_num,
                "strength": strength
            }
            message_parts.append(t_sent("scale_event_corr", **common_kwargs))
            if abs(correlation_num) < 0.2:
                message_parts.append(t_sent("scale_event_strength", **common_kwargs))
            elif correlation_num > 0:
                message_parts.append(t_sent("scale_event_positive", **common_kwargs))
            else:
                message_parts.append(t_sent("scale_event_negative", **common_kwargs))
        return message_parts

    #사용자가 변수 2개를 선택하면, 그에 맞는 메세지를 보여줌. 
    correlation_select_columns = [
        column for column in available_correlation_columns if column in correlation_columns_group_map
    ]
    
    correlation_x_columns = [
        column for column in correlation_select_columns if correlation_columns_group_map.get(column) in ["environment", "lifestyle"]
    ]

    correlation_x_display_names = [
        display_name_map[column] for column in correlation_x_columns
    ]

    if len(correlation_x_columns) < 1:
        st.info(t('no_correlation_variable_info'))
        st.stop()
    else:
        correlation_col1, correlation_col2 = st.columns(2)
        with correlation_col1:
            default_correlation_x_display_name = display_name_map.get("environment_index", correlation_x_display_names[0])
            correlation_x_display_name = st.selectbox(t('first_correlation_variable'), correlation_x_display_names, index=correlation_x_display_names.index(default_correlation_x_display_name) if default_correlation_x_display_name in correlation_x_display_names else 0, key = "correlation_x_selectbox")
            correlation_x_column = reverse_display_name_map[correlation_x_display_name]
            correlation_y_columns = [
                column for column in correlation_select_columns if is_allowed_comparison(correlation_x_column, column)
            ]
            correlation_y_display_names = [
                display_name_map[column] for column in correlation_y_columns
            ]
        with correlation_col2:
            if not correlation_y_display_names:
                correlation_y_display_name = None
                st.info(t('no_second_correlation_variable_info'))
            else:
                default_correlation_y_display_name = display_name_map.get("overall_mood_index", correlation_y_display_names[0])
                correlation_y_display_name = st.selectbox(t('second_correlation_variable'), correlation_y_display_names, index=correlation_y_display_names.index(default_correlation_y_display_name) if default_correlation_y_display_name in correlation_y_display_names else 0, key = "correlation_y_selectbox")
                correlation_y_column = reverse_display_name_map[correlation_y_display_name]
        if correlation_x_display_name and correlation_y_display_name:
            correlation_mode = "ready"
        else:
            correlation_mode = "pending"
        if correlation_mode == "pending":
            st.info(t('both_variables_required_corr_info'))
        if correlation_mode == "ready": 
            if st.button(t('show_correlation_button')):
                st.session_state.correlation_mode = "in_display"
                st.session_state.correlation_x_display_name = correlation_x_display_name
                st.session_state.correlation_y_display_name = correlation_y_display_name
            if st.session_state.correlation_mode == "in_display":
                correlation_x_display_name_to_show = st.session_state.get("correlation_x_display_name", correlation_x_display_name)
                correlation_y_display_name_to_show = st.session_state.get("correlation_y_display_name", correlation_y_display_name)
                correlation_x_column_to_show = reverse_display_name_map.get(correlation_x_display_name_to_show, correlation_x_column)
                correlation_y_column_to_show = reverse_display_name_map.get(correlation_y_display_name_to_show, correlation_y_column)
                valid_mask = df[correlation_x_column_to_show].notna() & df[correlation_y_column_to_show].notna()
                if valid_mask.sum() < 2:
                    st.info(t('not_enough_data_corr_info'))
                else:
                    st.write(f"{t('selected_variables')} : {correlation_x_display_name_to_show} ↔ {correlation_y_display_name_to_show}")
                    if df.loc[valid_mask, correlation_x_column_to_show].nunique() >= 2 and df.loc[valid_mask, correlation_y_column_to_show].nunique() >= 2:
                        selected_correlation = df.loc[valid_mask, correlation_x_column_to_show].corr(df.loc[valid_mask, correlation_y_column_to_show])
                        if pd.notna(selected_correlation):
                            st.write(f"{t('correlation_coefficient')} : {selected_correlation:.3f}")
                    display_message_parts(compute_correlation_message(correlation_x_column_to_show, correlation_y_column_to_show))
        
    # ========================================
    #산점도
    st.subheader(t('scatter_plot_subsection_title'))
    st.write(t('scatter_plot_subsection_sent'))
    if "scatter_chart_mode" not in st.session_state:
        st.session_state.scatter_chart_mode = "pending"

    scatter_columns = [ #변수명
        column for column in available_correlation_columns
        if column in correlation_columns_group_map
    ]
    
    allowed_x_columns = [ #변수명
        column for column in scatter_columns if correlation_columns_group_map.get(column) in ["environment", "lifestyle"]
    ]

    allowed_x_options = [ #자연어
        display_name_map[column]
        for column in allowed_x_columns # : 
        # scatter_options.append(display_name_map[column])
        #최종 저장 형태는 사용자에게 보일 display name이 됨. 
    ]

    if len(allowed_x_options) >= 1:
        col1, col2 = st.columns(2)
        scatter_chart_mode = "pending"
        with col1:
            default_x_display_name = display_name_map.get("environment_index", allowed_x_options[0])
            # get을 사용하는 이유 : 혹시 environment_index 값이 없을까봐
            x_axis_display_name = st.selectbox(t('first_scatter_plot_variable'), allowed_x_options, index=allowed_x_options.index(default_x_display_name) if default_x_display_name in allowed_x_options else 0) #초기값은 종합환경지수가 있으면 그걸로 하고, 없으면 첫번째 값으로 하라
            if x_axis_display_name:
                x_axis_for_filtering = reverse_display_name_map[x_axis_display_name]
                allowed_y_columns = [ #변수명
                column for column in scatter_columns if is_allowed_comparison(x_axis_for_filtering, column)
            ]
                allowed_y_options = [ #자연어
                display_name_map[column] for column in allowed_y_columns
            ]
            else:
                allowed_y_options = []
        with col2:
            if not x_axis_display_name:
                y_axis_display_name = None
                st.info(t('choose_first_variable_info'))
            elif not allowed_y_options:
                y_axis_display_name = None
                st.info(t('no_second_scatter_plot_variable_info'))
                scatter_chart_mode = "blocked"
            else:
                default_y_display_name = display_name_map.get("overall_mood_index", allowed_y_options[0])
                y_axis_display_name = st.selectbox(t('second_scatter_plot_variable'), allowed_y_options, index=allowed_y_options.index(default_y_display_name) if default_y_display_name in allowed_y_options else 0)
            
        if x_axis_display_name and y_axis_display_name:
            scatter_chart_mode = "ready"
        
        if scatter_chart_mode == "pending":
            st.info(t('both_variables_required_scatter_plot_info'))

        if scatter_chart_mode == "ready":
            if st.button(t('show_scatter_plot_button')):
                st.session_state.scatter_chart_mode = "in_display"
            if st.session_state.scatter_chart_mode == "in_display" and x_axis_display_name and y_axis_display_name:
                x_axis = reverse_display_name_map[x_axis_display_name] #사용자가 선택한 display name -> df 상의 변수명 저장 
                y_axis = reverse_display_name_map[y_axis_display_name]
                valid_mask = df[x_axis].notna() & df[y_axis].notna()
                if valid_mask.sum() >= 2:
                    fig, ax = plt.subplots(facecolor="#F7F4EE") #그래프를 그릴 그림판을 가져오는 코드 fig : 전체 그림. ax : 좌표평면
                    ax.set_facecolor("#FCFAF6")
                    #reg은 regression(회귀). 산점도와 추세선(regression line)을 같이 그려주는 함수.
                    #kws는 keyword arguments. alpha는 투명도(0~1 사이 값), s는 size.
                    sns.regplot(
                        data=df.loc[valid_mask],
                        x=x_axis, 
                        y=y_axis, 
                        ax=ax,
                        scatter_kws={
                            "color": "#7A8B6F",
                            "alpha": 0.75,
                            "s": 55
                        },
                        line_kws={
                            "color": "#5A5148",
                            "linewidth": 2
                        }
                        ) #산점도와 추세선을 그리는 코드
                    # data=df.loc[valid_mask] : 값이 들어있는 데이터만 사용해라
                    #ax = ax : 아까 만든 그 좌표평면에 그려라
                    #grid : 좌표평면의 격자선을 추가하는 함수.
                    ax.grid(True, color="#DDD4C7", linewidth=0.8, alpha=0.7)
                    #spine은 그래프를 둘러싼 사각형 테두리 선을 의미함. matplotlib전용 용어.
                    for spine in ax.spines.values():
                        spine.set_color("#CFC5B7")
                    ax.set_xlabel(x_axis_display_name) #사람이 읽기 좋은 변수명으로 display
                    ax.set_ylabel(y_axis_display_name)
                    st.pyplot(fig) #완성된 그래프를 화면에 띄우는 streamlit 함수
                    #상관계수 계산
                    if df.loc[valid_mask, x_axis].nunique() < 2 or df.loc[valid_mask, y_axis].nunique() < 2:
                        st.info(t('correlation_constant_value_warning_info'))
                    else:
                        selected_correlation = df.loc[valid_mask, x_axis].corr(df.loc[valid_mask, y_axis])
                        if pd.isna(selected_correlation):
                            st.write(t('cant_compute_correlation_info'))
                        else:
                            display_message_parts(compute_correlation_message(x_axis, y_axis))
                else: 
                    st.write(t('not_enough_data_info'))
            
# ====================================
# 자유기록 열람
# ====================================
if selected_page == t('journal_history_menu'):
    st.subheader(t('journal_history_section_title'))
    csv_path = DATA_PATH
    
    if not pl.Path(csv_path).exists():
        st.info(t('no_record_info'))
    elif streamlit_calendar is None:
        st.warning(t('install_streamlit_calendar_info'))
        st.code("pip install streamlit-calendar")
    else:
        journal_df = pd.read_csv(csv_path)
        journal_df["target_date"] = pd.to_datetime(journal_df["target_date"]).dt.date
        journal_df = journal_df.sort_values("target_date", ascending=False)

        #자유 열람 칸에서 사용할 파생 지표는 별도 계산 필요.
        journal_df["sunshine_index"] = journal_df.apply(compute_sunshine_index, axis = 1)
        journal_df["air_quality_index"] = journal_df.apply(compute_air_quality_index, axis = 1)
        journal_df["environment_index"] = journal_df.apply(compute_environment_index, axis = 1)
        journal_df["overall_mood_index"] = journal_df.apply(compute_overall_mood_index, axis = 1)
        journal_df["sleep_index"] = journal_df.apply(compute_sleep_index, axis = 1)
        journal_df["sleep_bed_minute_std_7d"] = journal_df.apply(lambda row: compute_sleep_consistency_std(journal_df, row["target_date"], "sleep_bed_time"), axis=1)
        journal_df["sleep_wake_minute_std_7d"] = journal_df.apply(lambda row: compute_sleep_consistency_std(journal_df, row["target_date"], "sleep_wake_time"), axis=1)
        journal_df["sleep_bed_consistency_index"] = journal_df["sleep_bed_minute_std_7d"].apply(compute_sleep_consistency_std_index)
        journal_df["sleep_wake_consistency_index"] = journal_df["sleep_wake_minute_std_7d"].apply(compute_sleep_consistency_std_index)
        journal_df["overall_sleep_consistency_index"] = journal_df[["sleep_bed_consistency_index", "sleep_wake_consistency_index"]].mean(axis=1)

        def calendar_date_to_local_date(value): #JS date 객체를 한국 날짜로 변환하는 방어 코드
            if value is None or str(value).strip() == "":
                return ""
            try:
                parsed_date = pd.to_datetime(value)
                if getattr(parsed_date, "tzinfo", None) is not None: #tz 는 timezone
                    parsed_date = parsed_date.tz_convert("Asia/Seoul")
                return str(parsed_date.date())
            except Exception:
                return str(value)[:10]


        if len(journal_df) == 0:
            st.info(t("no_record_info"))
        else:
            if "selected_journal_date" not in st.session_state:
                st.session_state.selected_journal_date = str(journal_df.iloc[0]["target_date"])
            calendar_events = []
            #캘린더에 표시할 이벤트(박스) 생성. 기록이 있는 날짜마다 이벤트를 추가하는데, 자유 기록이 있는 경우와 없는 경우를 색깔로 구분해서 보여줌.
            for _, row in journal_df.iterrows(): 
                #iterrows는 데이터프레임의 각 행을 반복하는 함수입니다. 각 행은 인덱스와 시리즈로 반환됩니다. 여기서는 _로 index를 무시하고 row로 각 행의 데이터를 담아서 사용합니다.
                date_str = str(row["target_date"])
                has_free_text = pd.notna(row.get("free_text")) and str(row.get("free_text")).strip() != ""
                event_title = t("free_text_o") if has_free_text else t("free_text_x")
                event_color = "#A8BFA3" if has_free_text else "#D8D2C8"
                calendar_events.append({
                    "id": date_str,
                    "title": event_title,
                    "start": date_str,
                    "allDay": True,
                    "backgroundColor": event_color,
                    "borderColor": event_color,
                    "textColor": "#4A443C",
                    "extendedProps": {
                        "target_date": date_str
                    }
                })
            calendar_options = { #캘린더 UI 설정.
                    "initialView": "dayGridMonth", #월간 달력 보기
                    "selectable": True,
                    "editable": False,
                    "locale" : (
                        "ko" if st.session_state.language == "kor"
                        else "en"
                    ),
                    "height": 550,
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,listMonth"
                }
                }
            #custom_css 는 캘린더의 디자인 꾸미기. 볼드체나 폰트 등 설정 가능.
            custom_css = """ 
                .fc-event-title{
                font-weight: 700; 
                }
                .fc-toolbar-title{
                font-size: 1.4rem;
                color: #5C554B;
                font-weight: 600;
                }

                .fc-theme-standard td,
                .fc-theme-standard th {
                    border-color: #ECE7DD;
                    }

                .fc .fc-button {
                    background-color: #F5F1E8;
                    border: 1px solid #D8D1C4;
                    color: #5C554B;
                    box-shadow: none;
                    }
                
                .fc .fc-button:hover {
                    background-color: #EAE3D5;
                    border: 1px solid #CFC6B8;
                    color: #4A443C;
                    }
                .fc .fc-button:focus {
                    box-shadow: none;
                    }
                .fc .fc-button-active {
                    background-color: #DDD3C3 !important;
                    border: 1px solid #C9BDAA !important;
                    color: #4A443C !important;
                    }
                """
            #캘린더 표시. 첫 번째 렌더링이 거의 항상 실패해서, 그냥 자동으로 1번 새로고침 되게 함.
            if "journal_calendar_refresh_count" not in st.session_state:
                st.session_state.journal_calendar_refresh_count = 0
            if "journal_calendar_auto_refreshed" not in st.session_state:
                st.session_state.journal_calendar_auto_refreshed = False

            #streamlit 캘린더는 탭 안에서는 첫 렌더링이 실패하는 오류가 보고되어 있으므로, 1회 자동 새로고침 함.
            if not st.session_state.journal_calendar_auto_refreshed:
                st.session_state.journal_calendar_auto_refreshed = True
                st.session_state.journal_calendar_refresh_count += 1
                st.rerun()

            calendar_placeholder = st.empty()
            with calendar_placeholder:
                calendar_result = streamlit_calendar(
                    events=calendar_events,
                    options=calendar_options,
                    custom_css=custom_css,

                    callbacks=["dateClick", "eventClick"],
                    key=f"journal_calendar_{st.session_state.journal_calendar_refresh_count}", #새로고침되는 캘린더는 모두 다른 객체임.
                )
            if calendar_result is None:
                st.session_state.journal_calendar_refresh_count += 1
                st.rerun()
            if isinstance(calendar_result, dict):
                #st.write(calendar_result)
                if calendar_result.get("callback") == "eventClick": #.get(callback)은 사용자가 무엇을 클릭했는지 알려주는 것임.
                    event = calendar_result.get(
                        "eventClick", 
                        {}
                        ).get("event",{})
                    clicked_date = event.get("id") or event.get("extendedProps", {}).get("target_date") or calendar_date_to_local_date(event.get("start"))
                    #3중안전장치. id -> extendedprops -> timezone 변환 순으로 클릭한 날짜를 가져오는데, 혹시 하나라도 실패할 경우 다음 방법으로 시도.
                    if clicked_date:
                        st.session_state.selected_journal_date = clicked_date
                elif calendar_result.get("callback") == "dateClick":
                    clicked_date = calendar_date_to_local_date(calendar_result.get("dateClick", {}).get("date"))
                    if clicked_date:
                        st.session_state.selected_journal_date = clicked_date
            #calendar reload button
            if st.button(t('reload_calendar_button')):
                st.session_state.journal_calendar_refresh_count += 1
                st.rerun()
            #display journal record of selected date
            selected_date = st.session_state.selected_journal_date
            selected_date_for_display = format_date_for_display(selected_date)
            selected_rows = journal_df[journal_df["target_date"].astype(str) == selected_date] #사용자가 클릭한 날짜와 일치하는 기록만 csv 파일에서 직접 갖고 옴.
            st.markdown("---")
            st.subheader(f"{selected_date_for_display}")
            if len(selected_rows) == 0:
                st.info(t('no_record_on_selected_date_info'))
            else:
                selected_record = selected_rows.iloc[0]
                free_text_value = selected_record.get("free_text")
                has_free_text = pd.notna(free_text_value) and str(free_text_value).strip() != ""
                show_record_tab1, show_record_tab2 = st.tabs([t('summary_and_free_text'), t('details')])
                with show_record_tab1:
                    environmental_index_value = selected_record.get("environment_index")
                    overall_mood_index_value = selected_record.get("overall_mood_index")
                    environmental_index_display = level_to_text(environmental_index_value)
                    overall_mood_index_display = level_to_text(overall_mood_index_value)
                    summary_col1, summary_col2 = st.columns(2)
                    with summary_col1:
                        st.write(f"{t('environment_index')} : {environmental_index_display}")
                    with summary_col2:
                        st.write(f"{t('overall_mood_index')} : {overall_mood_index_display}")
                    if has_free_text:
                        free_text_box = f"""
                        <div style="
                        border: 1px solid #E5DED3;
                        border-radius: 12px;
                        padding: 1.2rem;
                        background-color: #F4F7F2;
                        margin-top: 1rem;
                        margin-bottom: 0.5rem;
                        ">
                        <div style="
                        font-size: 1.05rem;
                        font-weight: 600;
                        color: #5C554B;
                        margin-bottom: 0.8rem;
                        ">
                        {t('free_text')}
                        </div>
                        <div style="
                        font-size: 1rem;
                        line-height: 1.7;
                        color: #4A443C;
                        white-space: pre-wrap;
                        ">
                        {str(free_text_value).strip()}
                        </div>
                        </div>
                        """
                        st.markdown(free_text_box, unsafe_allow_html=True)
                    else:
                        st.info(t('no_free_text_on_selected_date_info'))
                with show_record_tab2:
                    environment_col, mood_col, lifestyle_col = st.columns(3)
                    with environment_col:
                        st.markdown(f"### {t('journal_history_environment_subsection_title')} :sun_behind_small_cloud:")
                        st.write(f"{t('weather_summary')} : {selected_record.get('weather_summary', t('no_record'))}")
                        st.write(f"{t('temperature')} : {selected_record.get('temperature_c', t('no_record'))}°C")
                        st.write(f"{t('humidity')} : {selected_record.get('humidity_percent', t('no_record'))}%")
                        sunshine_index_value = selected_record.get("sunshine_index")
                        sunshine_index_display = level_to_text(sunshine_index_value)
                        st.write(f"{t('sunshine_intensity')} : {sunshine_index_display}")
                        air_quality_index_value = selected_record.get("air_quality_index")
                        air_quality_index_display = level_to_text(air_quality_index_value)
                        st.write(f"{t('air_quality_index')} : {air_quality_index_display}")
                    with mood_col:
                        st.markdown(f"### {t('journal_history_mood_subsection_title')} :brain:")
                        st.write(f"{t('mood')}: {level_to_text(selected_record.get('mood', t('no_record')))}")
                        st.write(f"{t('focus')}: {level_to_text(selected_record.get('focus', t('no_record')))}")
                        st.write(f"{t('irritability')}: {three_level_to_text(selected_record.get('irritability', t('no_record')))}")
                        st.write(f"{t('depression')}: {three_level_to_text(selected_record.get('depression', t('no_record')))}")
                    with lifestyle_col:
                        st.markdown(f"### {t('journal_history_lifestyle_subsection_title')} 🏃")
                        sleep_index_value = selected_record.get("sleep_index")
                        sleep_index_display = level_to_text(sleep_index_value)
                        st.write(f"{t('sleep_index')} : {sleep_index_display}")

                        sleep_consistency_value = selected_record.get("overall_sleep_consistency_index")
                        sleep_consistency_display = level_to_text(sleep_consistency_value)
                        st.write(f"{t('overall_sleep_consistency_index')} : {sleep_consistency_display}")

                        sleep_bed_time_value = selected_record.get("sleep_bed_time")
                        sleep_wake_time_value = selected_record.get("sleep_wake_time")
                        sleep_duration_hours_value = selected_record.get("sleep_duration_hours")
                        if pd.isna(sleep_bed_time_value) or pd.isna(sleep_wake_time_value) or pd.isna(sleep_duration_hours_value):
                            st.write(f"{t('sleep_duration_hours')} : {t('no_data')}")
                        else:
                            sleep_bed_time_str = str(sleep_bed_time_value)
                            sleep_wake_time_str = str(sleep_wake_time_value)
                            sleep_duration_hours_str = f"{float(sleep_duration_hours_value):.1f}"
                            st.write(f"{t('sleep_duration_hours')} : {sleep_bed_time_str} ~ {sleep_wake_time_str}({sleep_duration_hours_str} {t('hour_unit')})")
                        
                        st.write(f"{t('journal_history_did_exercise')} : {ox_to_text(selected_record.get('did_exercise', t('no_record')))}")
                        st.write(f"{t('journal_history_had_major_stress_event')} : {ox_to_text(selected_record.get('had_major_stress', t('no_record')))}")
                        st.write(f"{t('journal_history_went_outside')} : {ox_to_text(selected_record.get('went_outside', t('no_record')))}")


# =========================================
# 설정
# =========================================
if selected_page == t('settings_menu'):

    #Language setting
    st.markdown(f"""
                <div class="section-title">
                {t('language_setting_section_title')} 🌐
                </div>
                """, unsafe_allow_html=True)

    language_display_map = {
        "kor": "한국어",
        "eng": "English"
    }

    reverse_language_display_map = {v: k for k, v in language_display_map.items()}

    selected_language_display_name = st.selectbox(
        "language_setting",
        options=list(language_display_map.values()),
        index=list(language_display_map.values()).index(language_display_map.get(st.session_state.language, "eng")), label_visibility="collapsed")
    
    selected_language = reverse_language_display_map[selected_language_display_name]  

    #Location & region setting
    if "latitude" not in st.session_state:
        st.session_state.latitude = st.session_state.get("latitude", 37.5665)
    if "longitude" not in st.session_state:
        st.session_state.longitude = st.session_state.get("longitude", 126.9780)
    if "location_mode" not in st.session_state:
        st.session_state.location_mode = "unset" # unset | auto_pending | manual | ready 
    if "show_location_success" not in st.session_state:
        st.session_state.show_location_success = False
    if "region" not in st.session_state:
        st.session_state.region = st.session_state.get('region', "Seoul")

    st.markdown(f"""
                <div class="section-title">
                {t('location_setting_section_title')} 📍
                </div>
                """,
                unsafe_allow_html=True)
    st.write(t("location_setting_section_sent"))
    
    #지역 선택
    region_display_map = {
        key: t(f"region_{str(key).lower().replace(' ', '_')}") for key in region_and_timezone
    }
    reverse_region_display_map = {
        display_name: key for key, display_name in region_display_map.items()
    }

    st.markdown(f"""
                <div class="subsection-title">
                {t('select_region')} 
                </div>
                """, unsafe_allow_html=True)
    selected_region_display = st.selectbox(
        "select_region",
        list(region_display_map.values()),
        index=list(region_display_map.values()).index(region_display_map.get(st.session_state.region, "Seoul")),
        label_visibility = "collapsed"
    )
    selected_region = reverse_region_display_map[selected_region_display]
    st.session_state.region = selected_region

    #위도 경도 입력
    st.markdown(f"""
                <div class="subsection-title">
                {t('location_setting')} 
                </div>
                """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        get_current_location = st.button(t('auto_location_button'))
    with col2:
        use_manual_input = st.button(t('manual_location_button'))
    # 수동 입력 버튼을 누르면 수동 모드 켜기
    if use_manual_input:
        st.session_state.location_mode = "manual"
    if get_current_location:
        st.session_state.location_mode = "auto_pending"

    if st.session_state.location_mode == "auto_pending":
        coords = streamlit_js_eval(
            js_expressions="""
            new Promise((resolve) => {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        resolve({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        });
                    },
                    (error) => {
                        resolve({
                            error: error.message
                        });
                    }
                );
            })
            """,
            key="get_location"
        )

        if isinstance(coords, dict) and "latitude" in coords and "longitude" in coords:
            st.session_state.latitude = coords["latitude"]
            st.session_state.longitude = coords["longitude"]
            st.session_state.location_mode = "ready"
            st.session_state.show_location_success = True


        elif isinstance(coords, dict) and "error" in coords:
            st.warning(f"{t('auto_location_fail_info')} [{coords['error']}] {t('use_manual_input_info')}")
            st.session_state.location_mode = "manual"
            st.rerun()
        if st.session_state.show_location_success:
            st.success(f"{t('auto_location_success_info')} {t('latitude')}: {st.session_state.latitude}, {t('longitude')}: {st.session_state.longitude}")
    
    # 수동 입력 모드
    if st.session_state.location_mode == "manual":
        st.write(t('manual_location_sent'))
        st.session_state.latitude = st.number_input(t('latitude'), value=37.5665, format="%.6f")
        st.session_state.longitude = st.number_input(t('longitude'), value=126.9780, format="%.6f")
        if st.button(t('save_location_button')):
            st.session_state.location_mode = "ready"
            st.success(t('save_location_success_info'))
            st.session_state.show_location_success = True
            st.write(f"{t('input_latitude')}: {st.session_state.latitude}")
            st.write(f"{t('input_longitude')}: {st.session_state.longitude}")

    #위치 가져오기의 결과물 
    latitude = st.session_state.latitude
    longitude = st.session_state.longitude

    #Sleep default time setting
    st.markdown(f"""
                <div class="section-title">
                {t('sleep_default_time_setting_section_title')} 🛏️
                </div>
                """, unsafe_allow_html=True)
    st.write(t('sleep_default_time_setting_sent'))
    default_bed_time_setting = time_text_to_time(st.session_state.get("default_bed_time", "23:00"), dt.time(23, 0))
    default_wake_time_setting = time_text_to_time(st.session_state.get("default_wake_time", "07:00"), dt.time(7, 0))

    setting_bed_col, setting_wake_col = st.columns(2)

    with setting_bed_col:
        selected_bed_time = st.time_input(t('default_bed_time_setting'), value=default_bed_time_setting, key="default_bed_time_input")
    with setting_wake_col:
        selected_wake_time = st.time_input(t('default_wake_time_setting'), value=default_wake_time_setting, key="default_wake_time_input")
    
    #Free Text Default text
    st.markdown(f"""
                <div class="section-title">
                {t('default_free_text_setting_section_title')} 🛏️
                </div>
                """, unsafe_allow_html=True)
    st.write(t('default_free_text_setting_sent'))

    #설정 저장값과 입력창 표시값을 분리.
    #default_free_text : 실제 저장값
    #default_free_text_input : 설정 화면 입력창 표시값
    if "default_free_text_input" not in st.session_state:
        st.session_state.default_free_text_input = st.session_state.get("default_free_text", "")
    #elif st.session_state.default_free_text_input == "" or st.session_state.default_free_text_input != st.session_state.get("default_free_text", ""):
        #st.session_state.default_free_text_input = st.session_state.get("default_free_text", "")
    
    default_free_text = st.text_area(
        "default_free_text",
        key="default_free_text_input",
        label_visibility="collapsed"
    )

    # Save Settings
    st.markdown(f"""
                <div class="subsection-title">
                {t('save_settings_subsection_title')}
                </div>
                """, unsafe_allow_html=True)

    if selected_language != st.session_state.get("language", None):
        st.session_state.language = selected_language
        save_settings()
        st.rerun()

    if st.button(t('save_settings_button')):
        st.session_state.default_bed_time = selected_bed_time.strftime("%H:%M")
        st.session_state.default_wake_time = selected_wake_time.strftime("%H:%M")
        st.session_state.latitude = latitude
        st.session_state.longitude = longitude
        st.session_state.region = selected_region
        st.session_state.location_mode = "ready"
        st.session_state.default_free_text = default_free_text
        save_settings()
        st.success(t('successfully_saved_info'))

# ========================================
###사용 가이드
# =========================================
if selected_page == t('user_guide_menu'):

    st.markdown(f"""
            <div class="section-title">
            {t('user_guide_section_title')} 📖
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_general_body'))

    st.markdown(f"""
            <div class="section-title">
            {t('guide_stats_title')} 📈
            </div>
            """, unsafe_allow_html=True)
    st.markdown(f"""
            <div class="subsection-title">
            {t('guide_stats_variable_subsection_title')} 🧮
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_stats_variable_body'))

    st.markdown(f"""
            <div class="subsection-title">
            {t('guide_stats_interpretation_subsection_title')} 🧐
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_stats_interpretation_body'))

    st.markdown(f"""
            <div class="section-title">
            {t('guide_settings_title')} ⚙️
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_settings_body'))
    
    st.markdown(f"""
            <div class="subsection-title">
            {t('guide_default_free_text_example_subtitle')} 
            </div>
            """, unsafe_allow_html=True)
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        st.text_area(
            t('guide_default_free_text_example1_title'),
            value=t('guide_default_free_text_example1'),
            height=220,
            disabled=True,
            key="guide_default_free_text_example1"
        )
    with example_col2:
        st.text_area(
            t('guide_default_free_text_example2_title'),
            value=t('guide_default_free_text_example2'),
            height=220,
            disabled=True,
            key="guide_default_free_text_example2"
        )

    st.markdown(f"""
            <div class="section-title">
            {t('guide_personal_info_title')} 👤
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_personal_info_body'))

    st.markdown(f"""
            <div class="section-title">
            {t('guide_exit_app_title')} 🛠️
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_exit_app_body'))


    st.markdown(f"""
            <div class="section-title">
            {t('guide_developer_title')} 🛠️
            </div>
            """, unsafe_allow_html=True)
    st.markdown(t('guide_developer_body'))









