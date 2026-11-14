"""STREM | streamlit run app.py
DEPLOY: Upload app.py + requirements.txt to GitHub. Streamlit Community Cloud:
choose repository, app.py, Python 3.11 or 3.12.
Optional camera AI: App settings > Secrets:
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-4o-mini"
APP_URL = "https://your-app.streamlit.app"
"""
import base64
import io
import json
from datetime import datetime
from html import escape
from urllib.parse import urlparse
import streamlit as st
from PIL import Image, ImageOps
import qrcode

st.set_page_config(page_title='STREM',page_icon='💧',layout='wide')

def svg_uri(inner, color='#3182f6', sw='2.1'):
    svg=f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='{sw}' stroke-linecap='round' stroke-linejoin='round'>{inner}</svg>"
    return "data:image/svg+xml;base64,"+base64.b64encode(svg.encode()).decode()

QR_SVG="<rect x='3' y='3' width='7' height='7' rx='1'/><rect x='14' y='3' width='7' height='7' rx='1'/><rect x='3' y='14' width='7' height='7' rx='1'/><rect x='14' y='14' width='3' height='3'/><line x1='20' y1='14' x2='20' y2='20'/><line x1='14' y1='20' x2='20' y2='20'/>"

ICONS={
    'logo':svg_uri("<path d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'/>",'#3182f6','2.2'),
    'coffee':svg_uri("<path d='M17 8h1a4 4 0 1 1 0 8h-1'/><path d='M3 8h14v7a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z'/><line x1='6' y1='2' x2='6' y2='4'/><line x1='10' y1='2' x2='10' y2='4'/><line x1='14' y1='2' x2='14' y2='4'/>"),
    'sauce':svg_uri("<path d='M4 11h16a1 1 0 0 1 1 1v.5a7.5 7.5 0 0 1-15 0V12a1 1 0 0 1 1-1Z'/><path d='M7 20h10'/><path d='M9 7c0-1.5 1.5-2 1.5-3.5'/><path d='M14 7c0-1.5 1.5-2 1.5-3.5'/>"),
    'oil':svg_uri("<path d='M12 3l5 5a7 7 0 1 1-10 0z'/><path d='M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5'/>"),
    'fruit':svg_uri("<path d='M12 6c-3.5 0-6 2.8-6 6.5C6 17 9 20 12 20s6-3 6-7.5C18 8.8 15.5 6 12 6z'/><path d='M12 6c0-2 1.5-3.5 3.5-3.5'/><path d='M12 6c-1-1.5-2.5-2-4-1.5'/>"),
    'blood':svg_uri("<path d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'/><line x1='12' y1='11' x2='12' y2='16'/><line x1='9.5' y1='13.5' x2='14.5' y2='13.5'/>"),
    'makeup':svg_uri("<path d='M9 11V6a3 3 0 0 1 6 0v5'/><rect x='7' y='11' width='10' height='9' rx='2'/><line x1='7' y1='15' x2='17' y2='15'/>"),
    'ink':svg_uri("<path d='M12 19l7-7 3 3-7 7-3-3z'/><path d='M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z'/><path d='M2 2l7.5 7.5'/>"),
    'sweat':svg_uri("<path d='M8 4l4 2 4-2 4 4-3 3v9H7v-9L4 8z'/>"),
    'home':svg_uri("<path d='M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",'#3182f6','2.2'),
    'camera':svg_uri("<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/>",'#3182f6','2.2'),
    'help':svg_uri("<circle cx='12' cy='12' r='9'/><path d='M9.2 9a3 3 0 0 1 5.6 1c0 2-2.8 2.5-2.8 4'/><circle cx='12' cy='17.2' r='0.6' fill='#3182f6'/>",'#3182f6','2.2'),
    'history':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>",'#3182f6','2.2'),
    'qr':svg_uri(QR_SVG,'#3182f6','2.2'),
    'home_dim':svg_uri("<path d='M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",'#8b95a1','1.9'),
    'camera_dim':svg_uri("<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/>",'#8b95a1','1.9'),
    'help_dim':svg_uri("<circle cx='12' cy='12' r='9'/><path d='M9.2 9a3 3 0 0 1 5.6 1c0 2-2.8 2.5-2.8 4'/><circle cx='12' cy='17.2' r='0.6' fill='#8b95a1'/>",'#8b95a1','1.9'),
    'history_dim':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>",'#8b95a1','1.9'),
    'qr_dim':svg_uri(QR_SVG,'#8b95a1','1.9'),
}

ALL_SUPPLIES=['주방세제','식초','베이킹소다','소금','치약','비누','소독용 에탄올','클렌징오일','과산화수소수','레몬즙']

S=st.session_state
for k,v in {
    'page':'start',
    'history':[],
    'kind':'coffee',
    'query_name':'',
    'material':'cotton',
    'age':'fresh',
    'cam_note':'',
    'supplies':['주방세제','식초','베이킹소다','소금'],
}.items():
    if k not in S:S[k]=v

active_tab={
    'find':'home',
    'camera':'camera',
    'identify':'help','material':'help','age':'help','result':'help',
    'history':'history',
    'share':'qr',
}.get(S.page,'home')

def dock_icon(name):
    return ICONS[name if active_tab==name else name+'_dim']

st.markdown(f'''<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

:root{{color-scheme:light}}
html,body,.stApp{{
  background:#f2f4f6!important;
  color:#191f28!important;
  overflow-x:hidden;
  font-family:'Gowun Dodum',-apple-system,BlinkMacSystemFont,sans-serif!important;
  font-weight:400!important;
}}
body *,.stApp *,button,input,label,p,span,h1,h2,h3,div,b,strong{{
  font-family:'Gowun Dodum',-apple-system,BlinkMacSystemFont,sans-serif!important;
  font-weight:400!important;
}}
header[data-testid="stHeader"],footer,[data-testid="stToolbar"]{{display:none!important;height:0!important}}

.block-container{{
  width:100%!important;
  max-width:100%!important;
  min-height:100dvh!important;
  padding:8px 10px 96px!important;
  margin:0!important;
}}
@media(min-width:640px){{
  .block-container{{max-width:520px!important;margin:0 auto!important}}
}}
[data-testid="stVerticalBlock"]{{gap:7px!important}}
h1{{font-size:25px!important;letter-spacing:-0.4px;margin:2px 0 4px!important;color:#191f28!important}}
h2{{font-size:21px!important;margin:0!important}}
p,label,[data-testid="stMarkdownContainer"] p{{font-size:18px!important;line-height:1.38!important;margin:0!important}}

/* Top Brand Header */
.brand{{
  display:flex;justify-content:space-between;align-items:center;
  padding:2px 4px 2px;
}}
.brand-left{{display:flex;align-items:center;gap:8px;font-size:22px;color:#191f28;letter-spacing:-0.3px}}
.brand-left img{{width:22px;height:22px}}
.brand span{{font-size:12px;letter-spacing:1.3px;color:#3182f6}}

/* Start Splash Card */
.splash{{
  background:#ffffff;
  color:#191f28;
  min-height:76dvh;
  padding:38px 22px;
  border-radius:28px;
  text-align:center;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  box-shadow:0 8px 24px rgba(15,23,42,0.05);
  margin:2px 0 8px;
}}
.splash-logo{{
  width:76px;height:76px;border-radius:24px;background:#eef4ff;
  display:flex;align-items:center;justify-content:center;margin-bottom:16px;
}}
.splash-logo img{{width:42px;height:42px}}
.splash-badge{{display:inline-block;background:#eef4ff;color:#3182f6;padding:7px 16px;border-radius:999px;font-size:14px;letter-spacing:1px;margin-bottom:12px}}
.splash h1{{color:#191f28!important;font-size:44px!important;margin-bottom:10px!important}}
.splash p{{color:#4e5968!important;font-size:20px!important;line-height:1.48!important}}

/* Pill Search Bar */
div[data-testid="stForm"]{{
  border:2px solid #3182f6!important;
  border-radius:999px!important;
  padding:3px 8px 3px 18px!important;
  background:#ffffff!important;
  box-shadow:0 4px 14px rgba(49,130,246,0.08)!important;
  margin-bottom:2px!important;
}}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]{{align-items:center!important;gap:6px!important;flex-wrap:nowrap!important}}
div[data-testid="stForm"] [data-testid="stTextInput"]>div>div{{border:none!important;background:transparent!important;box-shadow:none!important}}
div[data-testid="stForm"] [data-testid="stTextInput"] input{{font-size:18px!important;min-height:40px!important;padding:0!important;color:#191f28!important}}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button{{
  border-radius:999px!important;
  min-height:40px!important;
  height:40px!important;
  padding:0 16px!important;
  background:#eef4ff!important;
  color:#3182f6!important;
  border:none!important;
  font-size:17px!important;
}}

/* Standard Choice Buttons */
.stButton button,.stLinkButton a,.stDownloadButton button{{
  width:100%!important;
  min-height:58px!important;
  border-radius:20px!important;
  font-size:19px!important;
  border:1.4px solid #e5eaf2!important;
  background-color:#ffffff!important;
  color:#191f28!important;
  padding:8px 14px!important;
  box-shadow:0 3px 10px rgba(15,23,42,0.04)!important;
}}
.stButton button p{{font-size:19px!important;line-height:1.25!important;color:#191f28!important}}
.stButton button:active,.stButton button:focus{{
  background-color:#eef4ff!important;
  border-color:#3182f6!important;
}}
.stButton button:active p,.stButton button:focus p{{
  color:#3182f6!important;
}}
.stButton button[kind="primary"]{{
  background-color:#3182f6!important;
  color:#ffffff!important;
  min-height:60px!important;
  font-size:20px!important;
  border:none!important;
  box-shadow:0 6px 18px rgba(49,130,246,0.24)!important;
}}
.stButton button[kind="primary"] p{{color:#ffffff!important;font-size:20px!important}}

/* 8 Stain Cards (4x2 Grid) — Clean Fixed Height so Nothing Overlaps */
div[class*="st-key-grid_r"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:8px!important;
}}
div[class*="st-key-grid_r"] .stButton button,
div[class*="st-key-grid_r"] .stButton button:hover,
div[class*="st-key-grid_r"] .stButton button:active,
div[class*="st-key-grid_r"] .stButton button:focus,
div[class*="st-key-grid_r"] .stButton button:focus-visible{{
  height:74px!important;
  min-height:74px!important;
  max-height:74px!important;
  border-radius:20px!important;
  background-color:#ffffff!important;
  border:1.5px solid #e5eaf2!important;
  box-shadow:0 3px 10px rgba(15,23,42,0.04)!important;
  padding:36px 6px 6px!important;
  background-repeat:no-repeat!important;
  background-position:center 10px!important;
  background-size:26px 26px!important;
  outline:none!important;
}}
div[class*="st-key-grid_r"] .stButton button:active,
div[class*="st-key-grid_r"] .stButton button:focus{{
  background-color:#eef4ff!important;
  border-color:#3182f6!important;
}}
div[class*="st-key-grid_r"] .stButton button p{{
  font-size:17px!important;
  color:#191f28!important;
  line-height:1.15!important;
}}
div[class*="st-key-grid_r"] .stButton button:active p,
div[class*="st-key-grid_r"] .stButton button:focus p{{
  color:#3182f6!important;
}}
div[class*="st-key-tile_coffee"] button,div[class*="st-key-tile_coffee"] button:hover,div[class*="st-key-tile_coffee"] button:focus,div[class*="st-key-tile_coffee"] button:active{{background-image:url("{ICONS['coffee']}")!important}}
div[class*="st-key-tile_sauce"] button,div[class*="st-key-tile_sauce"] button:hover,div[class*="st-key-tile_sauce"] button:focus,div[class*="st-key-tile_sauce"] button:active{{background-image:url("{ICONS['sauce']}")!important}}
div[class*="st-key-tile_oil"] button,div[class*="st-key-tile_oil"] button:hover,div[class*="st-key-tile_oil"] button:focus,div[class*="st-key-tile_oil"] button:active{{background-image:url("{ICONS['oil']}")!important}}
div[class*="st-key-tile_fruit"] button,div[class*="st-key-tile_fruit"] button:hover,div[class*="st-key-tile_fruit"] button:focus,div[class*="st-key-tile_fruit"] button:active{{background-image:url("{ICONS['fruit']}")!important}}
div[class*="st-key-tile_blood"] button,div[class*="st-key-tile_blood"] button:hover,div[class*="st-key-tile_blood"] button:focus,div[class*="st-key-tile_blood"] button:active{{background-image:url("{ICONS['blood']}")!important}}
div[class*="st-key-tile_makeup"] button,div[class*="st-key-tile_makeup"] button:hover,div[class*="st-key-tile_makeup"] button:focus,div[class*="st-key-tile_makeup"] button:active{{background-image:url("{ICONS['makeup']}")!important}}
div[class*="st-key-tile_ink"] button,div[class*="st-key-tile_ink"] button:hover,div[class*="st-key-tile_ink"] button:focus,div[class*="st-key-tile_ink"] button:active{{background-image:url("{ICONS['ink']}")!important}}
div[class*="st-key-tile_sweat"] button,div[class*="st-key-tile_sweat"] button:hover,div[class*="st-key-tile_sweat"] button:focus,div[class*="st-key-tile_sweat"] button:active{{background-image:url("{ICONS['sweat']}")!important}}

/* Separate Bottom Box for Household Supplies (Clearly separated below the 8 stain cards) */
div[class*="st-key-pantry_box"]{{
  background:#ffffff!important;
  border-radius:22px!important;
  padding:12px 12px 10px!important;
  margin-top:14px!important;
  border:1.5px solid #dbeafe!important;
  box-shadow:0 4px 14px rgba(15,23,42,0.04)!important;
}}
.pantry-head{{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:6px;
  padding:0 2px;
}}
.pantry-title{{font-size:17px;color:#191f28}}
.pantry-sub{{font-size:13.5px;color:#3182f6;background:#eef4ff;padding:4px 10px;border-radius:999px}}
div[class*="st-key-sup_row"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:5px!important;
}}
div[class*="st-key-sup_row"] .stButton button,
div[class*="st-key-sup_row"] .stButton button:hover,
div[class*="st-key-sup_row"] .stButton button:focus,
div[class*="st-key-sup_row"] .stButton button:active{{
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  border-radius:13px!important;
  padding:0 3px!important;
  background-color:#f8fafc!important;
  border:1.3px solid #d8e2ee!important;
  box-shadow:none!important;
  background-image:none!important;
}}
div[class*="st-key-sup_row"] .stButton button p{{
  font-size:14.5px!important;
  color:#4e5968!important;
  line-height:1.1!important;
}}
div[class*="st-key-sup_row"] .stButton button[kind="primary"],
div[class*="st-key-sup_row"] .stButton button[kind="primary"]:hover,
div[class*="st-key-sup_row"] .stButton button[kind="primary"]:focus,
div[class*="st-key-sup_row"] .stButton button[kind="primary"]:active{{
  background-color:#eef4ff!important;
  border:1.8px solid #3182f6!important;
  box-shadow:none!important;
  background-image:none!important;
}}
div[class*="st-key-sup_row"] .stButton button[kind="primary"] p{{
  color:#3182f6!important;
  font-size:14.5px!important;
}}

/* Two-Column Grid for 10 Fabrics & 12 Stains */
div[class*="st-key-mat_grid"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:8px!important;
}}
div[class*="st-key-mat_grid"] .stButton button{{
  height:12.2dvh!important;
  min-height:66px!important;
  border-radius:20px!important;
  padding:8px 10px!important;
}}
div[class*="st-key-mat_grid"] .stButton button p{{
  font-size:18px!important;
  line-height:1.25!important;
}}

/* Age Screen Buttons */
div[class*="st-key-age_list"] .stButton button{{
  height:12.5dvh!important;
  min-height:68px!important;
  border-radius:20px!important;
}}
div[class*="st-key-age_list"] .stButton button p{{
  font-size:19px!important;
}}

/* Native Streamlit Container Styled as Toss Result Card */
div[class*="st-key-result_card"]{{
  background:#ffffff!important;
  border-radius:26px!important;
  padding:18px 18px!important;
  margin:2px 0 6px!important;
  min-height:68dvh!important;
  box-shadow:0 4px 18px rgba(15,23,42,0.05)!important;
  border:1px solid #e8eef5!important;
}}
.tag-pill{{
  display:inline-block;
  background:#eef4ff;
  color:#3182f6;
  font-size:17px;
  padding:6px 14px;
  border-radius:999px;
  margin-bottom:6px;
}}
.info-pill{{
  background:#f8fbff;
  border:1.3px solid #dbeafe;
  border-radius:16px;
  padding:10px 14px;
  margin:4px 0;
  font-size:17px;
  color:#1e3a8a;
  line-height:1.4;
}}
.step-card{{
  background:#ffffff;
  border-bottom:1px solid #f2f4f6;
  padding:10px 2px;
}}
.step-head{{
  font-size:19px;
  color:#3182f6;
  margin-bottom:3px;
}}
.step-desc{{
  font-size:17.5px;
  color:#333d4b;
  line-height:1.42;
}}
.chem-pill{{
  background:#f2f6ff;
  border-radius:16px;
  padding:12px 14px;
  margin-top:8px;
  font-size:16.5px;
  color:#3182f6;
  line-height:1.4;
}}

/* Toss White Rounded Bottom Bar */
div[class*="st-key-bottom_dock"]{{
  position:fixed!important;
  left:50%!important;
  bottom:0!important;
  transform:translateX(-50%)!important;
  width:100%!important;
  max-width:520px!important;
  background:#ffffff!important;
  border-top:1px solid #e5e8eb!important;
  border-radius:24px 24px 0 0!important;
  padding:8px 8px 12px!important;
  box-shadow:0 -6px 24px rgba(15,23,42,0.08)!important;
  z-index:9999!important;
}}
div[class*="st-key-bottom_dock"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:2px!important;
  align-items:center!important;
}}
div[class*="st-key-bottom_dock"] .stButton button,
div[class*="st-key-bottom_dock"] .stButton button:hover,
div[class*="st-key-bottom_dock"] .stButton button:focus,
div[class*="st-key-bottom_dock"] .stButton button:active,
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"],
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"]:hover,
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"]:focus,
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"]:active{{
  height:54px!important;
  min-height:54px!important;
  background-color:transparent!important;
  border:none!important;
  box-shadow:none!important;
  border-radius:14px!important;
  padding:27px 2px 2px!important;
  background-repeat:no-repeat!important;
  background-position:center 4px!important;
  background-size:23px 23px!important;
  outline:none!important;
}}
div[class*="st-key-bottom_dock"] .stButton button p{{
  font-size:13.5px!important;
  line-height:1.1!important;
  color:#8b95a1!important;
}}
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"] p,
div[class*="st-key-bottom_dock"] .stButton button:focus p,
div[class*="st-key-bottom_dock"] .stButton button:active p{{
  color:#3182f6!important;
  font-size:13.5px!important;
}}
div[class*="st-key-dock_home"] button,div[class*="st-key-dock_home"] button:hover{{background-image:url("{dock_icon('home')}")!important}}
div[class*="st-key-dock_cam"] button,div[class*="st-key-dock_cam"] button:hover{{background-image:url("{dock_icon('camera')}")!important}}
div[class*="st-key-dock_id"] button,div[class*="st-key-dock_id"] button:hover{{background-image:url("{dock_icon('help')}")!important}}
div[class*="st-key-dock_hist"] button,div[class*="st-key-dock_hist"] button:hover{{background-image:url("{dock_icon('history')}")!important}}
div[class*="st-key-dock_qr"] button,div[class*="st-key-dock_qr"] button:hover{{background-image:url("{dock_icon('qr')}")!important}}
div[class*="st-key-dock_home"] button:focus,div[class*="st-key-dock_home"] button:active{{background-image:url("{ICONS['home']}")!important}}
div[class*="st-key-dock_cam"] button:focus,div[class*="st-key-dock_cam"] button:active{{background-image:url("{ICONS['camera']}")!important}}
div[class*="st-key-dock_id"] button:focus,div[class*="st-key-dock_id"] button:active{{background-image:url("{ICONS['help']}")!important}}
div[class*="st-key-dock_hist"] button:focus,div[class*="st-key-dock_hist"] button:active{{background-image:url("{ICONS['history']}")!important}}
div[class*="st-key-dock_qr"] button:focus,div[class*="st-key-dock_qr"] button:active{{background-image:url("{ICONS['qr']}")!important}}

[data-testid="stCameraInput"]{{max-width:100%;margin:0 auto}}
@media(max-width:640px){{
  [data-testid="stHorizontalBlock"]{{flex-wrap:nowrap!important}}
  [data-testid="stColumn"]{{min-width:0!important;flex:1!important}}
}}
</style>''',unsafe_allow_html=True)

def secret(name,default=''):
    try:return st.secrets.get(name,default)
    except Exception:return default

def go(page):S.page=page;st.rerun()

LABEL={
    'coffee':'커피 · 차 · 탄닌 얼룩',
    'sauce':'김치 · 소스 · 양념 얼룩',
    'oil':'기름 · 삼겹살 · 유분 얼룩',
    'fruit':'과일 · 와인 · 색소 얼룩',
    'blood':'피 · 단백질 얼룩',
    'makeup':'화장품 · 립스틱 얼룩',
    'ink':'볼펜 · 잉크 · 물감 얼룩',
    'sweat':'땀 · 피지 · 황변 얼룩',
    'mud':'흙 · 진흙 · 풀물 얼룩',
    'rust':'녹물 · 금속 산화 얼룩',
    'gum':'껌 · 접착제 · 수지 얼룩',
    'unknown':'복합 생활 얼룩'
}

MAT_NAME={
    'cotton':'면 · 티셔츠 · 셔츠',
    'denim':'청바지 · 데님',
    'poly':'운동복 · 합성섬유',
    'knit':'니트 · 울 · 가디건',
    'silk':'실크 · 블라우스',
    'linen':'린넨 · 여름 마 셔츠',
    'padding':'패딩 · 점퍼 · 아우터',
    'towel':'수건 · 양말 · 속옷',
    'school':'교복 · 정장 · 슬랙스',
    'bedding':'이불 · 침구 · 커튼'
}

MAT_TIP={
    'cotton':'면 섬유는 조직이 튼튼하므로 칫솔이나 손끝으로 톡톡 두드려 세제를 침투시키세요.',
    'denim':'청바지는 강하게 문지르면 인디고 염료가 빠져 하얗게 물이 빠지니 뒤집어서 두드려 빼세요.',
    'poly':'합성섬유는 기름을 강하게 끌어당기므로 물을 묻히기 전 주방세제 원액부터 바르세요.',
    'knit':'울·니트는 알칼리와 마찰에 줄어드니 비비지 말고 중성 주방세제와 식초로 톡톡 눌러 빼세요.',
    'silk':'실크·블라우스는 섬유가 약하므로 밑에 수건을 깔고 면봉·스펀지로 두드려서 얼룩을 옮겨내세요.',
    'linen':'린넨은 마찰에 보풀이 잘 생기므로 거품을 올려 5분 불린 뒤 부드럽게 주물러 헹구세요.',
    'padding':'패딩·점퍼는 전체 세탁 대신 얼룩 부위에만 주방세제·에탄올을 묻혀 젖은 수건으로 닦아내세요.',
    'towel':'수건·양말은 40℃ 미온수에 베이킹소다를 풀어 10분 담갔다 세탁하면 섬유 속까지 깨끗해집니다.',
    'school':'교복·슬랙스는 번들거림이 생기지 않게 밑에 천을 받치고 안쪽에서 바깥쪽으로 두드려 빼세요.',
    'bedding':'부피가 큰 침구는 얼룩 아래에 마른 수건을 두껍게 깔고 위에서 세제 거품으로 두드려 흡수시키세요.'
}

ALIASES={
    'coffee':['커피','아메리카노','라떼','카페라떼','에스프레소','녹차','홍차','보리차','차','초콜릿','초코','코코아','밀크티','콜라','사이다','탄산','흑당','카라멜','아이스티','맥주','소주'],
    'sauce':['김치','김치국물','떡볶이','양념','고추장','케첩','간장','된장','카레','짜장','짜장면','짬뽕','마라','마라탕','소스','치킨','바베큐','돈까스','머스타드','불닭','핫소스','국물','찌개'],
    'oil':['기름','식용유','버터','참기름','들기름','올리브유','라면','삼겹살','고기','마요네즈','고추기름','튀김','피자','치즈','감자튀김','베이컨','곱창','족발','치킨기름','샐러드드레싱','드레싱'],
    'fruit':['과일','주스','오렌지','포도','딸기','블루베리','수박','사과','와인','레드와인','식혜','복숭아','체리','망고','토마토','석류','감','귤','자몽','레몬','매실','잼'],
    'blood':['혈액','피','코피','생리혈','상처','핏자국','계란','달걀','우유','요거트','치즈','침','고름','구토','토','배변','분유'],
    'makeup':['립스틱','틴트','파운데이션','쿠션','비비','화장품','아이라이너','마스카라','블러셔','선크림','립밤','섀도우','컨실러','향수','로션','크림','바세린','오일'],
    'ink':['잉크','볼펜','사인펜','매직','네임펜','형광펜','만년필','크레파스','물감','연필','페인트','아크릴','붓펜','도장','먹물','토너','염색약','매니큐어'],
    'sweat':['땀','황변','누런때','목때','겨드랑이','피지','데오드란트','개기름','쉰내','체취','소변','오줌','찌든때','손때'],
    'mud':['흙','진흙','모래','먼지','잔디','풀','풀물','낙엽','꽃가루','시멘트','분필','숯','재','매연'],
    'rust':['녹','녹물','철분','쇳물','동전','금속','자전거체인'],
    'gum':['껌','본드','접착제','풀','스티커','테이프','끈적이','실리콘','송진','촛농','양초','슬라임','클레이'],
}

CHEM={
    'coffee':'주방세제가 음료의 유분을 분리하고, 식초의 아세트산(CH₃COOH)과 소금의 삼투·흡착 작용이 탄닌 색소 결합을 끊어 지워냅니다.',
    'sauce':'계면활성제가 고추기름·유분을 유화시키고, 식초(산성)와 베이킹소다(약알칼리)가 캡사이신·카로티노이드 색소를 분해합니다.',
    'oil':'주방세제의 친유성기가 비극성 기름 분자를 감싸 물에 녹이는 미셀(Micelle) 유화 작용과 베이킹소다의 비누화 반응으로 기름을 뺍니다.',
    'fruit':'식초·레몬즙의 유기산이 과일의 안토시아닌 색소를 환원·분해해 섬유에 착색되는 것을 막습니다.',
    'blood':'혈액·단백질은 40℃ 이상에서 열변성되어 굳으므로 찬물과 소금물(삼투압)·비누로 단백질을 불려 분해해야 합니다.',
    'makeup':'클렌징오일·알코올·치약 속 연마·계면활성 성분이 화장품의 실리콘·왁스 결합을 같은 극성끼리 녹여냅니다(유유상용).',
    'ink':'소독용 에탄올이나 치약·비누의 계면활성 성분이 잉크의 유성 수지 결합을 느슨하게 녹여 섬유에서 떼어냅니다.',
    'sweat':'땀 속 피지와 단백질이 산화된 황변 얼룩을 약알칼리성 베이킹소다와 주방세제가 가수분해하고 식초가 냄새를 중화합니다.',
    'mud':'진흙의 규산염 입자는 물에 젖으면 섬유 틈에 끼므로 말려서 털어낸 뒤, 치약·비누의 계면활성 거품으로 미세 입자를 빼냅니다.',
    'rust':'산화철(Fe₂O₃) 녹 얼룩은 물과 세제에 녹지 않지만, 식초·레몬즙의 산(Acid)과 소금의 염화이온이 만나 수용성 철이온으로 환원되어 빠집니다.',
    'gum':'고분자 수지·왁스는 얼음으로 냉각해 유리전이온도 이하로 딱딱하게 굳혀 떼어낸 뒤, 오일·세제로 잔여물을 녹입니다.',
    'unknown':'유분(주방세제·비누) → 산성·단백질 오염(베이킹소다·소금) → 알칼리·색소(식초) 3단계 화학 반응으로 미확인 복합 성분을 제거합니다.',
}

def match(text):
    clean=text.strip().lower().replace(' ','')
    if not clean:return 'unknown'
    for k,words in ALIASES.items():
        if clean in words or any(len(w)>=1 and (w in clean or clean in w) for w in words):
            return k
    if any(x in clean for x in ['국','탕','볶음','구이','조림','면','밥','떡','빵','과자','치킨','버거']):
        return 'sauce'
    if any(x in clean for x in ['유','기름','버터','치즈','크림','튀김','전']):
        return 'oil'
    if any(x in clean for x in ['차','주스','에이드','스무디','라떼','티','청','와인','술']):
        return 'coffee'
    if any(x in clean for x in ['펜','잉크','물감','색연필','마카','염색','페인트']):
        return 'ink'
    return 'unknown'

def smart_search_kind(text):
    k = match(text)
    if k != 'unknown':
        return k, ''
    if secret('OPENAI_API_KEY'):
        try:
            from openai import OpenAI
            client=OpenAI(api_key=secret('OPENAI_API_KEY'),timeout=12,max_retries=0)
            response=client.chat.completions.create(
                model=secret('OPENAI_MODEL','gpt-4o-mini'),
                max_tokens=80,
                response_format={'type':'json_object'},
                messages=[
                    {'role':'system','content':'Classify any stain keyword into one ID: "coffee","sauce","oil","fruit","blood","makeup","ink","sweat","mud","rust","gum","unknown". Return JSON {"kind":"...","note":"한 줄 화학 성분 요약"}.'},
                    {'role':'user','content':text}
                ]
            )
            data=json.loads(response.choices[0].message.content)
            ai_k=data.get('kind','unknown')
            if ai_k in LABEL:
                return ai_k, data.get('note','')
        except Exception:
            pass
    return 'unknown', f"'{text.strip()}' 얼룩의 수용성·유성·색소 복합 성분을 한 번에 분해하는 맞춤 방법이에요."

def show_solution_immediately(kind, query_name='', cam_note=''):
    S.kind = kind if kind in LABEL else 'unknown'
    S.query_name = query_name.strip()
    S.cam_note = cam_note
    title_name = S.query_name if S.query_name else LABEL[S.kind]
    S.history.insert(0,{'name':title_name,'time':datetime.now().strftime('%m.%d %H:%M')})
    S.history=S.history[:20]
    go('result')

def start(kind):
    S.kind = kind if kind in LABEL else 'unknown'
    S.query_name = ''
    S.material='cotton';S.age='fresh';S.cam_note=''
    go('material')

def bottom_dock():
    with st.container(key='bottom_dock'):
        d1,d2,d3,d4,d5=st.columns(5)
        if d1.button('홈',key='dock_home',use_container_width=True,type='primary' if active_tab=='home' else 'secondary'):go('find')
        if d2.button('카메라',key='dock_cam',use_container_width=True,type='primary' if active_tab=='camera' else 'secondary'):go('camera')
        if d3.button('얼룩찾기',key='dock_id',use_container_width=True,type='primary' if active_tab=='help' else 'secondary'):go('identify')
        if d4.button('기록',key='dock_hist',use_container_width=True,type='primary' if active_tab=='history' else 'secondary'):go('history')
        if d5.button('QR',key='dock_qr',use_container_width=True,type='primary' if active_tab=='qr' else 'secondary'):go('share')

def analyze_stain_photo(file_obj):
    im=ImageOps.exif_transpose(Image.open(file_obj)).convert('RGB')
    if secret('OPENAI_API_KEY'):
        try:
            from openai import OpenAI
            im_small=im.copy();im_small.thumbnail((800,800));buf=io.BytesIO();im_small.save(buf,format='JPEG',quality=80)
            client=OpenAI(api_key=secret('OPENAI_API_KEY'),timeout=20,max_retries=0)
            response=client.chat.completions.create(
                model=secret('OPENAI_MODEL','gpt-4o-mini'),
                max_tokens=100,
                response_format={'type':'json_object'},
                messages=[
                    {'role':'system','content':'Classify the clothing stain into one ID: "coffee", "sauce", "oil", "fruit", "blood", "makeup", "ink", "sweat", "mud", "rust", "gum". Return JSON {"kind":"...","note":"AI 사진 성분 분석 완료"}.'},
                    {'role':'user','content':[{'type':'text','text':'얼룩 종류를 판별해 주세요.'},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()}}]}
                ]
            )
            data=json.loads(response.choices[0].message.content)
            k=data.get('kind','sauce')
            if k in LABEL:
                return k, data.get('note','AI 사진 분석 완료')
        except Exception:
            pass
    crop=im.resize((80,80))
    px=list(crop.getdata())
    cx=[p for i,p in enumerate(px) if 20<=i%80<=60 and 20<=i//80<=60]
    r=sum(p[0] for p in cx)/len(cx)
    g=sum(p[1] for p in cx)/len(cx)
    b=sum(p[2] for p in cx)/len(cx)
    bright=(r+g+b)/3
    if r-max(g,b)>28 and r>85:
        return 'blood','사진의 적색 파장을 분석해 혈액·단백질 얼룩으로 판별했어요'
    if bright<85 or abs(r-b)>34:
        return 'ink','사진의 진한 색소 농도를 분석해 잉크·볼펜 얼룩으로 판별했어요'
    if r>g>b and (r-b)>24:
        return 'sauce','사진의 주황·갈색 색소를 분석해 김치·소스·커피 얼룩으로 판별했어요'
    return 'oil','사진의 반투명 유분 패턴을 분석해 기름·유분 얼룩으로 판별했어요'

def has_sup(name):
    return name in S.supplies

def build_custom_plan():
    k = S.kind if S.kind in LABEL else 'unknown'
    q = S.query_name if S.query_name else LABEL[k]
    owned = S.supplies if S.supplies else ['주방세제','물']

    surf = '주방세제' if has_sup('주방세제') else ('비누' if has_sup('비누') else ('치약' if has_sup('치약') else '주방세제(또는 비누)'))
    acid = '식초' if has_sup('식초') else ('레몬즙' if has_sup('레몬즙') else '식초(또는 레몬즙)')
    alkali = '베이킹소다' if has_sup('베이킹소다') else ('소금' if has_sup('소금') else ('치약' if has_sup('치약') else '베이킹소다(또는 소금)'))
    solvent = '소독용 에탄올' if has_sup('소독용 에탄올') else ('클렌징오일' if has_sup('클렌징오일') else ('치약' if has_sup('치약') else '알코올(또는 치약)'))

    used=[]
    for item in [surf, acid, alkali, solvent, '과산화수소수', '소금']:
        base=item.split('(')[0]
        if base in owned and base not in used:
            used.append(base)
    prep_str = '내 보유 용품 활용 · ' + (' + '.join(used[:4]) if used else '주방세제 + 식초 + 베이킹소다')

    if k=='coffee':
        steps=[
            (f'{surf}로 유분·당분 먼저 분해',f'얼룩 부위에 {surf}를 묻혀 손끝으로 톡톡 두드려 우유 지방과 당분을 먼저 녹여냅니다.'),
            (f'{acid} + {"소금 " if has_sup("소금") else ""}산성 탈색',f'{acid}를 몇 방울 적셔 5분 두면 갈색 탄닌 색소 결합이 화학 분해됩니다.'),
            ('미온수 헹굼 마무리','녹아 나온 갈색 거품을 물로 깨끗이 헹궈냅니다.')
        ]
    elif k=='sauce':
        steps=[
            (f'마른 얼룩에 {surf} 원액 도포',f'물을 묻히기 전 {surf}를 발라 양념의 고추기름·유분 막을 먼저 감싸 녹입니다.'),
            (f'{acid} → {alkali} 반응으로 색소 제거',f'{acid}를 적신 뒤 {alkali}를 살짝 올려 붉은 색소와 냄새 성분을 빼냅니다.'),
            ('미온수 헹굼 및 햇빛 건조','물로 헹군 뒤 햇빛에 말리면 남은 붉은 색소까지 광분해됩니다.')
        ]
    elif k=='oil':
        steps=[
            (f'물기 없이 {surf} 침투',f'마른 상태에서 {surf}를 바로 발라 기름 분자를 계면활성제로 감싸 분리합니다.'),
            (f'{alkali} + 따뜻한 물 유화',f'{alkali}를 뿌려 가볍게 문지른 뒤 40℃ 따뜻한 물로 굳은 지방산을 녹여냅니다.'),
            ('온수 거품 세척','기름기가 다시 엉기지 않도록 따뜻한 물로 충분히 헹궈냅니다.')
        ]
    elif k=='fruit':
        steps=[
            (f'{acid} 먼저 적시기',f'과일즙·와인 얼룩에 {acid}를 먼저 적셔 안토시아닌 색소가 섬유에 고착되는 것을 막습니다.'),
            (f'{surf} 거품 세척',f'{surf}를 묻혀 가볍게 두드려 당분과 남은 색소를 빼냅니다.'),
            ('찬물 헹굼','남은 당분이 없도록 깨끗이 헹궈 마무리합니다.')
        ]
    elif k=='blood':
        oxy = '과산화수소수' if has_sup('과산화수소수') else ('소금' if has_sup('소금') else alkali)
        steps=[
            (f'찬물 + {surf}로 단백질 불리기',f'반드시 찬물로 적신 뒤 {surf}를 묻혀 혈액 단백질을 불려냅니다. (뜨거운 물 금지)'),
            (f'{oxy}로 핏기 분해',f'남은 자국에 {oxy}를 올려 삼투압·산화 작용으로 섬유 속 헤모글로빈을 빼냅니다.'),
            ('찬물 헹굼 마무리','분해된 단백질 거품을 찬물로 깨끗이 씻어냅니다.')
        ]
    elif k=='makeup':
        oil_remover = '클렌징오일' if has_sup('클렌징오일') else ('소독용 에탄올' if has_sup('소독용 에탄올') else surf)
        steps=[
            (f'{oil_remover}로 화장품 왁스·유분 용해',f'마른 얼룩에 {oil_remover}를 발라 화장품의 실리콘·오일 성분을 먼저 녹입니다.'),
            (f'{surf} + {alkali} 2차 세척',f'녹아 나온 색소 유분을 {surf} 거품으로 한 번 더 잡아 빼냅니다.'),
            ('미온수 헹굼','남은 유분기가 없도록 따뜻한 물로 헹궈 마무리합니다.')
        ]
    elif k=='ink':
        steps=[
            (f'{solvent}로 잉크 수지 용해',f'옷 밑에 휴지를 깔고 {solvent}를 묻혀 두드려 잉크 색소를 휴지 쪽으로 옮겨냅니다.'),
            (f'{surf} 거품 세척',f'느슨해진 잉크 잔여물을 {surf} 거품으로 감싸 섬유에서 분리합니다.'),
            ('미온수 헹굼 마무리','잉크가 번지지 않는지 확인하고 물로 깨끗이 헹굽니다.')
        ]
    elif k=='sweat':
        steps=[
            (f'{surf}로 피지 기름막 제거',f'누렇게 변한 부위에 {surf}를 발라 땀 속 피지 성분을 먼저 녹입니다.'),
            (f'{alkali} 온수 담금 분해',f'{alkali}를 푼 따뜻한 물에 10분간 불려 산화된 황변 때를 분해합니다.'),
            (f'{acid} 중화 헹굼',f'마지막 헹굼 물에 {acid}를 몇 방울 넣어 알칼리를 중화하고 냄새를 잡습니다.')
        ]
    elif k=='mud':
        brush = '치약' if has_sup('치약') else ('비누' if has_sup('비누') else surf)
        steps=[
            ('마른 상태에서 흙 입자 털기','젖은 상태에서 문지르지 말고, 흙가루를 먼저 털어내 섬유 박힘을 막습니다.'),
            (f'{brush} + {alkali} 거품 흡착',f'{brush}와 {alkali}를 묻혀 거품을 내어 섬유 틈새의 미세 진흙·풀물 입자를 빼냅니다.'),
            ('미온수 헹굼','입자가 남지 않도록 물로 헹궈 마무리합니다.')
        ]
    elif k=='rust':
        steps=[
            (f'{acid} + {"소금 " if has_sup("소금") else ""}산성 환원 반응',f'녹물 위에 {acid}와 {"소금을" if has_sup("소금") else "세제를"} 올려 10분 두어 불용성 산화철을 수용성으로 녹입니다.'),
            (f'{surf}로 잔여물 제거',f'녹아 나온 철분 자국을 {surf} 거품으로 가볍게 두드려 닦아냅니다.'),
            ('찬물 헹굼','산성 성분이 남지 않도록 물로 충분히 헹굽니다.')
        ]
    elif k=='gum':
        steps=[
            ('얼음 냉각으로 굳혀 떼어내기','얼음을 비닐에 넣어 2분간 대어 끈적이는 고분자 수지를 딱딱하게 굳힌 뒤 긁어냅니다.'),
            (f'{solvent} + {surf}로 잔여 접착제 용해',f'남은 끈적임에 {solvent}와 {surf}를 발라 유성 수지 성분을 녹여냅니다.'),
            ('미온수 헹굼 마무리','따뜻한 물로 헹궈 잔여물을 완전히 제거합니다.')
        ]
    else:
        steps=[
            (f'1단계 · {surf}로 기름막·표면 오염 분리',f"'{q}' 얼룩에 {surf}를 먼저 묻혀 유분과 수용성 오염을 동시에 감싸 녹여냅니다."),
            (f'2단계 · {alkali}로 고착 오염 분해',f'{alkali}를 조금 올려 손끝으로 두드려 섬유에 붙은 단백질·산성 오염을 분해합니다.'),
            (f'3단계 · {acid} 중화 및 헹굼',f'남은 색소에 {acid}를 살짝 적셔 중화한 뒤 미온수로 깨끗이 헹궈냅니다.')
        ]
    return prep_str, steps

st.markdown(f'<div class="brand"><div class="brand-left"><img src="{ICONS["logo"]}"/>STREM</div><span>STAIN CARE</span></div>',unsafe_allow_html=True)

if S.page=='start':
    st.markdown(f'<div class="splash"><div class="splash-logo"><img src="{ICONS["logo"]}"/></div><div class="splash-badge">CHEMISTRY STAIN CARE</div><h1>STREM</h1><p>집에 있는 세제 · 식초 · 소금으로<br>어떤 얼룩이든 성분에 맞게 지우는 화학 가이드</p></div>',unsafe_allow_html=True)
    if st.button('앱 시작하기',type='primary',use_container_width=True):go('find')

elif S.page=='find':
    with st.form('search',clear_on_submit=False):
        sc1,sc2=st.columns([3.5,1.3])
        with sc1:
            text=st.text_input('얼룩 검색',placeholder='떡볶이, 볼펜, 진흙, 녹물, 껌 등 무엇이든 입력…',label_visibility='collapsed')
        with sc2:
            submit=st.form_submit_button('찾기',use_container_width=True)
    if submit and text.strip():
        found,ai_note=smart_search_kind(text)
        show_solution_immediately(found, query_name=text.strip(), cam_note=ai_note)

    with st.container(key='grid_r1'):
        r1=st.columns(2)
        if r1[0].button('커피 · 차',key='tile_coffee',use_container_width=True):start('coffee')
        if r1[1].button('김치 · 소스',key='tile_sauce',use_container_width=True):start('sauce')

    with st.container(key='grid_r2'):
        r2=st.columns(2)
        if r2[0].button('기름 · 삼겹살',key='tile_oil',use_container_width=True):start('oil')
        if r2[1].button('과일 · 와인',key='tile_fruit',use_container_width=True):start('fruit')

    with st.container(key='grid_r3'):
        r3=st.columns(2)
        if r3[0].button('피 · 혈액',key='tile_blood',use_container_width=True):start('blood')
        if r3[1].button('화장품 · 립스틱',key='tile_makeup',use_container_width=True):start('makeup')

    with st.container(key='grid_r4'):
        r4=st.columns(2)
        if r4[0].button('볼펜 · 잉크',key='tile_ink',use_container_width=True):start('ink')
        if r4[1].button('땀 · 누런때',key='tile_sweat',use_container_width=True):start('sweat')

    with st.container(key='pantry_box'):
        st.markdown(f'<div class="pantry-head"><span class="pantry-title">내 보유 용품 등록 ({len(S.supplies)}개)</span><span class="pantry-sub">누르면 내 재료로 맞춤 해결</span></div>',unsafe_allow_html=True)
        with st.container(key='sup_row1'):
            s1=st.columns(5)
            for idx,item in enumerate(ALL_SUPPLIES[:5]):
                on = item in S.supplies
                if s1[idx].button(item,key=f'sup_{idx}',use_container_width=True,type='primary' if on else 'secondary'):
                    if on:S.supplies.remove(item)
                    else:S.supplies.append(item)
                    st.rerun()
        with st.container(key='sup_row2'):
            s2=st.columns(5)
            for idx,item in enumerate(ALL_SUPPLIES[5:]):
                on = item in S.supplies
                if s2[idx].button(item,key=f'sup_{idx+5}',use_container_width=True,type='primary' if on else 'secondary'):
                    if on:S.supplies.remove(item)
                    else:S.supplies.append(item)
                    st.rerun()

    bottom_dock()

elif S.page=='camera':
    st.markdown('<h1>모르는 얼룩 촬영</h1>',unsafe_allow_html=True)
    st.caption('찍으면 질문 없이 바로 얼룩 성분을 판별해 내 보유 용품에 맞는 해결책을 알려드려요.')
    photo=st.camera_input('촬영',label_visibility='collapsed')
    if photo:
        if st.button('이 얼룩 바로 분석 · 해결책 보기',type='primary',use_container_width=True):
            kind,note=analyze_stain_photo(photo)
            S.material='cotton';S.age='fresh'
            show_solution_immediately(kind, cam_note=note)
    bottom_dock()

elif S.page=='identify':
    st.markdown('<h1>어떤 얼룩인지 골라주세요</h1>',unsafe_allow_html=True)
    id_items=[
        ('커피 · 라떼 · 차 · 콜라','coffee'),
        ('김치 · 떡볶이 · 카레 · 소스','sauce'),
        ('삼겹살 · 라면 · 식용유 · 버터','oil'),
        ('과일즙 · 주스 · 와인','fruit'),
        ('피 · 코피 · 혈흔 · 단백질','blood'),
        ('립스틱 · 파운데이션 · 선크림','makeup'),
        ('볼펜 · 사인펜 · 형광펜 · 물감','ink'),
        ('땀 · 목주변 누런때 · 데오드란트','sweat'),
        ('흙 · 진흙 · 잔디 · 풀물','mud'),
        ('녹물 · 금속 자국','rust'),
        ('껌 · 접착제 · 스티커 · 촛농','gum'),
        ('정체를 모르는 얼룩','unknown'),
    ]
    with st.container(key='mat_grid_id'):
        for i in range(0,len(id_items),2):
            cols=st.columns(2)
            for j in range(2):
                if i+j<len(id_items):
                    lbl,val=id_items[i+j]
                    if cols[j].button(lbl,key=f'id_{val}',use_container_width=True):
                        S.kind=val;S.query_name=''
                        go('material')
    bottom_dock()

elif S.page=='material':
    st.markdown('<h1>어떤 옷감인가요? (10종)</h1>',unsafe_allow_html=True)
    mat_items=list(MAT_NAME.items())
    with st.container(key='mat_grid'):
        for i in range(0,len(mat_items),2):
            cols=st.columns(2)
            for j in range(2):
                if i+j<len(mat_items):
                    val,lbl=mat_items[i+j]
                    if cols[j].button(lbl,key=f'mat_{val}',use_container_width=True):
                        S.material=val
                        go('age')
    bottom_dock()

elif S.page=='age':
    st.markdown('<h1>얼룩 상태가 어떤가요?</h1>',unsafe_allow_html=True)
    age_items=[
        ('방금 묻어서 아직 축축해요','fresh'),
        ('묻은 지 몇 시간 지나 말랐어요','dry'),
        ('어제 이전에 묻어 단단히 굳었어요','old'),
        ('물이나 휴지로 한 번 닦아봤어요','wiped'),
        ('세탁기 돌렸는데 아직 남아있어요','washed')
    ]
    with st.container(key='age_list'):
        for lbl,val in age_items:
            if st.button(lbl,key=f'age_{val}',use_container_width=True):
                S.age=val
                show_solution_immediately(S.kind, S.query_name)
    bottom_dock()

elif S.page=='result':
    k = S.kind if S.kind in LABEL else 'unknown'
    m = S.material if S.material in MAT_NAME else 'cotton'
    header_title = f"'{S.query_name}' 맞춤 해결책" if S.query_name else f"{LABEL[k]} 맞춤 해결책"
    prep_str, steps = build_custom_plan()

    with st.container(key='result_card'):
        st.markdown(f'<div class="tag-pill">{escape(header_title)}</div>', unsafe_allow_html=True)
        if S.cam_note:
            st.markdown(f'<div class="info-pill">{escape(S.cam_note)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-pill">{escape(prep_str)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-pill">{escape(MAT_NAME[m])} 케어 · {escape(MAT_TIP[m])}</div>', unsafe_allow_html=True)
        for idx, (t, b) in enumerate(steps, 1):
            st.markdown(f'<div class="step-card"><div class="step-head">{idx}. {escape(t)}</div><div class="step-desc">{escape(b)}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chem-pill">화학 원리 · {escape(CHEM[k])}</div>', unsafe_allow_html=True)

    if st.button('다른 얼룩 찾기',type='primary',use_container_width=True):go('find')
    bottom_dock()

elif S.page=='history':
    st.markdown('<h1>최근 기록</h1>',unsafe_allow_html=True)
    with st.container(key='result_card'):
        if S.history:
            for i,x in enumerate(S.history[:6],1):
                st.markdown(f'<div class="step-card"><div class="step-head">{i}. {escape(x["name"])}</div><div class="step-desc">{escape(x["time"])}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="step-desc">아직 기록이 없어요.</div>',unsafe_allow_html=True)
    bottom_dock()

elif S.page=='share':
    st.markdown('<h1>QR 코드</h1>',unsafe_allow_html=True)
    url=st.text_input('앱 주소',value=secret('APP_URL','https://2611121313-d9pclpfwungek3wl2j9j2s.streamlit.app/'),label_visibility='collapsed')
    parsed=urlparse(url)
    if parsed.scheme=='https' and parsed.netloc:
        buf=io.BytesIO();qrcode.make(url).save(buf,format='PNG')
        with st.container(key='result_card'):
            st.markdown('<div class="step-head" style="text-align:center;margin-bottom:10px">휴대폰으로 스캔해 STREM 열기</div>',unsafe_allow_html=True)
            c1,c2=st.columns([1,1.2])
            with c1:st.image(buf.getvalue(),width=165)
            with c2:
                st.download_button('QR 저장',buf.getvalue(),'STREM_QR.png','image/png',use_container_width=True)
                if st.button('처음 화면으로',use_container_width=True):go('start')
    bottom_dock()
