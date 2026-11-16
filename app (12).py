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
import time
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
SPARK_SVG="<circle cx='11' cy='11' r='6.5'/><line x1='20' y1='20' x2='15.8' y2='15.8'/><line x1='11' y1='8' x2='11' y2='14'/><line x1='8' y1='11' x2='14' y2='11'/>"

ICONS={
    'logo':svg_uri("<path d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'/>",'#3182f6','2.2'),
    'search':svg_uri("<circle cx='11' cy='11' r='7'/><line x1='20' y1='20' x2='16.2' y2='16.2'/>",'#3182f6','2.3'),
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
    'identify':svg_uri(SPARK_SVG,'#3182f6','2.2'),
    'history':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>",'#3182f6','2.2'),
    'qr':svg_uri(QR_SVG,'#3182f6','2.2'),
    'home_dim':svg_uri("<path d='M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",'#8b95a1','1.9'),
    'camera_dim':svg_uri("<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/>",'#8b95a1','1.9'),
    'identify_dim':svg_uri(SPARK_SVG,'#8b95a1','1.9'),
    'history_dim':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>",'#8b95a1','1.9'),
    'qr_dim':svg_uri(QR_SVG,'#8b95a1','1.9'),
}

ALL_SUPPLIES=['주방세제','베이킹소다','과산화수소','식초','클렌징오일','소독에탄올','소금','치약','비누']

S=st.session_state
for k,v in {
    'page':'start',
    'history':[],
    'kind':'coffee',
    'query_name':'',
    'material':'cotton',
    'age':'fresh',
    'supplies':['주방세제','베이킹소다','식초','소금'],
}.items():
    if k not in S:S[k]=v

S.supplies = [('소독에탄올' if x=='소독용 에탄올' else ('과산화수소' if x=='과산화수소수' else x)) for x in S.supplies]
S.supplies = [x for x in S.supplies if x in ALL_SUPPLIES]

active_tab={
    'find':'home','material':'home','age':'home','result':'home',
    'camera':'camera',
    'identify':'identify',
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
  padding:16px 14px calc(130px + env(safe-area-inset-bottom, 0px))!important;
  margin:0!important;
}}
@media(min-width:640px){{
  .block-container{{max-width:520px!important;margin:0 auto!important}}
}}
[data-testid="stVerticalBlock"]{{gap:8px!important}}
h1{{font-size:22px!important;letter-spacing:-0.4px;margin:4px 0 8px!important;color:#191f28!important}}
h2{{font-size:19px!important;margin:0!important}}
p,label,[data-testid="stMarkdownContainer"] p{{font-size:16.5px!important;line-height:1.35!important;margin:0!important}}

/* Top Brand Header — Clear Gap Between STREM and Search Bar */
.brand{{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:6px 4px 14px!important;
  margin-bottom:8px!important;
}}
.brand-left{{display:flex;align-items:center;gap:8px;font-size:22px;color:#191f28;letter-spacing:-0.3px}}
.brand-left img{{width:22px;height:22px}}

/* Animated Intro Screen — ONLY Icon and Name Move & Enter Automatically */
@keyframes stremPop {{
  0% {{opacity:0;transform:translateY(26px) scale(0.84)}}
  55% {{opacity:1;transform:translateY(-6px) scale(1.04)}}
  100% {{opacity:1;transform:translateY(0) scale(1)}}
}}
@keyframes stremPulse {{
  0%,100% {{box-shadow:0 12px 32px rgba(49,130,246,0.14)}}
  50% {{box-shadow:0 16px 42px rgba(49,130,246,0.28)}}
}}
.splash-auto{{
  min-height:86dvh;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  text-align:center;
}}
.splash-logo-anim{{
  width:92px;
  height:92px;
  border-radius:30px;
  background:#ffffff;
  display:flex;
  align-items:center;
  justify-content:center;
  margin-bottom:18px;
  animation:stremPop 0.9s cubic-bezier(0.22,1,0.36,1) forwards, stremPulse 1.6s ease-in-out infinite;
}}
.splash-logo-anim img{{width:48px;height:48px}}
.splash-name-anim{{
  font-size:44px!important;
  color:#191f28!important;
  letter-spacing:1.5px;
  opacity:0;
  animation:stremPop 0.85s cubic-bezier(0.22,1,0.36,1) 0.15s forwards;
}}

/* Pill Search Bar with Compact Magnifying Glass Icon Button */
div[data-testid="stForm"]{{
  border:2px solid #3182f6!important;
  border-radius:999px!important;
  padding:2px 6px 2px 16px!important;
  background:#ffffff!important;
  box-shadow:0 4px 12px rgba(49,130,246,0.08)!important;
  margin-top:8px!important;
  margin-bottom:14px!important;
}}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]{{
  align-items:center!important;
  gap:4px!important;
  flex-wrap:nowrap!important;
}}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:first-child{{
  flex:1 1 auto!important;
  min-width:0!important;
}}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]:last-child{{
  flex:0 0 40px!important;
  width:40px!important;
  max-width:40px!important;
}}
div[data-testid="stForm"] [data-testid="stTextInput"]>div>div{{border:none!important;background:transparent!important;box-shadow:none!important}}
div[data-testid="stForm"] [data-testid="stTextInput"] input{{font-size:16.5px!important;min-height:36px!important;padding:0!important;color:#191f28!important}}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button,
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:focus,
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:active{{
  border-radius:999px!important;
  width:36px!important;
  min-width:36px!important;
  max-width:36px!important;
  min-height:36px!important;
  height:36px!important;
  padding:0!important;
  background-color:#eef4ff!important;
  background-image:url("{ICONS['search']}")!important;
  background-repeat:no-repeat!important;
  background-position:center center!important;
  background-size:18px 18px!important;
  border:none!important;
  box-shadow:none!important;
}}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button p{{
  font-size:0!important;
  color:transparent!important;
}}

/* Standard Choice Buttons */
.stButton button,.stLinkButton a,.stDownloadButton button{{
  width:100%!important;
  min-height:52px!important;
  border-radius:18px!important;
  font-size:17.5px!important;
  border:1.4px solid #e5eaf2!important;
  background-color:#ffffff!important;
  color:#191f28!important;
  padding:6px 10px!important;
  box-shadow:0 2px 8px rgba(15,23,42,0.04)!important;
}}
.stButton button p,.stDownloadButton button p{{
  font-size:17px!important;
  line-height:1.2!important;
  color:#191f28!important;
  white-space:nowrap!important;
  overflow:visible!important;
}}
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
  min-height:52px!important;
  font-size:18.5px!important;
  border:none!important;
  box-shadow:0 6px 16px rgba(49,130,246,0.24)!important;
}}
.stButton button[kind="primary"] p{{color:#ffffff!important;font-size:18.5px!important}}

/* 8 Stain Cards (4x2 Grid) */
div[class*="st-key-grid_r"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:8px!important;
}}
div[class*="st-key-grid_r"] .stButton button,
div[class*="st-key-grid_r"] .stButton button:hover,
div[class*="st-key-grid_r"] .stButton button:active,
div[class*="st-key-grid_r"] .stButton button:focus,
div[class*="st-key-grid_r"] .stButton button:focus-visible{{
  height:64px!important;
  min-height:64px!important;
  max-height:64px!important;
  border-radius:18px!important;
  background-color:#ffffff!important;
  border:1.5px solid #e5eaf2!important;
  box-shadow:0 2px 8px rgba(15,23,42,0.04)!important;
  padding:30px 6px 4px!important;
  background-repeat:no-repeat!important;
  background-position:center 8px!important;
  background-size:22px 22px!important;
  outline:none!important;
}}
div[class*="st-key-grid_r"] .stButton button:active,
div[class*="st-key-grid_r"] .stButton button:focus{{
  background-color:#eef4ff!important;
  border-color:#3182f6!important;
}}
div[class*="st-key-grid_r"] .stButton button p{{
  font-size:16.5px!important;
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

/* Pantry Box: Clear Separation Between "보유 용품" Label and the Supply Buttons Below */
div[class*="st-key-pantry_box"]{{
  background:#ffffff!important;
  border-radius:22px!important;
  padding:16px 14px 16px!important;
  margin-top:14px!important;
  margin-bottom:28px!important;
  border:1.5px solid #e5eaf2!important;
  box-shadow:0 4px 14px rgba(15,23,42,0.04)!important;
}}
div[class*="st-key-pantry_box"] [data-testid="stVerticalBlock"]{{
  gap:10px!important;
}}
.pantry-label{{
  font-size:17.5px;
  color:#191f28;
  padding:0 4px 12px;
  margin-bottom:8px;
  border-bottom:1.5px solid #edf1f7;
  display:block;
}}
div[class*="st-key-sup_row1"]{{
  margin-top:6px!important;
}}
div[class*="st-key-sup_row"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:8px!important;
}}
div[class*="st-key-sup_row"] .stButton button,
div[class*="st-key-sup_row"] .stButton button:hover,
div[class*="st-key-sup_row"] .stButton button:focus,
div[class*="st-key-sup_row"] .stButton button:active{{
  min-height:42px!important;
  height:42px!important;
  max-height:42px!important;
  border-radius:13px!important;
  padding:0 6px!important;
  background-color:#f8fafc!important;
  border:1.3px solid #d8e2ee!important;
  box-shadow:none!important;
  background-image:none!important;
}}
div[class*="st-key-sup_row"] .stButton button p{{
  font-size:15.5px!important;
  color:#8b95a1!important;
  line-height:1.15!important;
  white-space:nowrap!important;
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
  font-size:15.5px!important;
  white-space:nowrap!important;
}}

/* Quick Stain Finder (빠른 얼룩 찾기) — Larger, Readable Cards with ≤2 Words */
div[class*="st-key-id_grid"]{{
  margin-top:4px!important;
  margin-bottom:28px!important;
}}
div[class*="st-key-id_grid"] [data-testid="stVerticalBlock"]{{
  gap:10px!important;
}}
div[class*="st-key-id_grid"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:10px!important;
}}
div[class*="st-key-id_grid"] .stButton button{{
  height:68px!important;
  min-height:68px!important;
  max-height:68px!important;
  border-radius:20px!important;
  padding:8px 10px!important;
  border:1.6px solid #dce5f2!important;
  box-shadow:0 4px 12px rgba(15,23,42,0.05)!important;
}}
div[class*="st-key-id_grid"] .stButton button p{{
  font-size:18.5px!important;
  line-height:1.2!important;
  color:#191f28!important;
  white-space:nowrap!important;
}}

/* Material Page (5 rows x 2 cols) — Larger Cards */
div[class*="st-key-mat_grid_fab"]{{
  margin-bottom:26px!important;
}}
div[class*="st-key-mat_grid_fab"] [data-testid="stVerticalBlock"]{{
  gap:10px!important;
}}
div[class*="st-key-mat_grid_fab"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:10px!important;
}}
div[class*="st-key-mat_grid_fab"] .stButton button{{
  height:66px!important;
  min-height:66px!important;
  max-height:66px!important;
  border-radius:20px!important;
  padding:8px 10px!important;
}}
div[class*="st-key-mat_grid_fab"] .stButton button p{{
  font-size:18px!important;
  line-height:1.2!important;
  white-space:nowrap!important;
}}

/* Age Screen Buttons (5 rows) — Larger & Concise */
div[class*="st-key-age_list"]{{
  margin-bottom:26px!important;
}}
div[class*="st-key-age_list"] [data-testid="stVerticalBlock"]{{
  gap:10px!important;
}}
div[class*="st-key-age_list"] .stButton button{{
  height:64px!important;
  min-height:64px!important;
  max-height:64px!important;
  border-radius:20px!important;
}}
div[class*="st-key-age_list"] .stButton button p{{
  font-size:18.5px!important;
}}

/* Clean, Well-Organized Toss Result Card */
div[class*="st-key-result_card"]{{
  background:#ffffff!important;
  border-radius:26px!important;
  padding:20px 18px!important;
  margin:6px 0 12px!important;
  box-shadow:0 6px 20px rgba(15,23,42,0.05)!important;
  border:1px solid #e8eef5!important;
}}
.sec-label{{
  font-size:14.5px;
  color:#8b95a1;
  margin-bottom:6px;
}}
.sup-chip-wrap{{
  display:flex;
  flex-wrap:wrap;
  gap:6px;
  margin-bottom:12px;
  padding-bottom:12px;
  border-bottom:1px solid #f2f4f6;
}}
.sup-chip-on{{
  background:#3182f6;
  color:#ffffff;
  padding:6px 13px;
  border-radius:999px;
  font-size:15.5px;
  box-shadow:0 3px 10px rgba(49,130,246,0.25);
}}
.sup-chip-off{{
  background:#f2f4f6;
  color:#b0b8c1;
  padding:6px 12px;
  border-radius:999px;
  font-size:14.5px;
}}
.step-card{{
  background:#f8fafc;
  border-radius:18px;
  padding:12px 14px;
  margin-bottom:8px;
}}
.step-head{{
  font-size:18px;
  color:#191f28;
  margin-bottom:3px;
}}
.step-num{{
  color:#3182f6;
  margin-right:6px;
}}
.step-desc{{
  font-size:16px;
  color:#4e5968;
  line-height:1.4;
}}

/* Centered QR Card & Centered Action Buttons */
.qr-center-box{{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  text-align:center;
  padding:6px 0 12px;
}}
.qr-center-box img{{
  width:180px;
  height:180px;
  border-radius:16px;
  margin:8px auto 6px;
  display:block;
}}
div[class*="st-key-qr_actions"]{{
  max-width:300px!important;
  margin:0 auto!important;
}}
div[class*="st-key-qr_actions"] [data-testid="stVerticalBlock"]{{
  gap:10px!important;
  align-items:center!important;
}}
div[class*="st-key-qr_actions"] .stDownloadButton,
div[class*="st-key-qr_actions"] .stButton{{
  width:100%!important;
}}
div[class*="st-key-qr_actions"] .stDownloadButton button,
div[class*="st-key-qr_actions"] .stButton button{{
  height:54px!important;
  min-height:54px!important;
  border-radius:16px!important;
}}

/* Toss White Rounded Bottom Bar (5 Tabs: 홈 · 카메라 · 얼룩찾기 · 기록 · QR) */
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
  padding:7px 8px calc(10px + env(safe-area-inset-bottom, 0px))!important;
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
  height:50px!important;
  min-height:50px!important;
  background-color:transparent!important;
  border:none!important;
  box-shadow:none!important;
  border-radius:14px!important;
  padding:25px 2px 2px!important;
  background-repeat:no-repeat!important;
  background-position:center 4px!important;
  background-size:21px 21px!important;
  outline:none!important;
}}
div[class*="st-key-bottom_dock"] .stButton button p{{
  font-size:12.5px!important;
  line-height:1.1!important;
  color:#8b95a1!important;
}}
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"] p,
div[class*="st-key-bottom_dock"] .stButton button:focus p,
div[class*="st-key-bottom_dock"] .stButton button:active p{{
  color:#3182f6!important;
  font-size:12.5px!important;
}}
div[class*="st-key-dock_home"] button,div[class*="st-key-dock_home"] button:hover{{background-image:url("{dock_icon('home')}")!important}}
div[class*="st-key-dock_cam"] button,div[class*="st-key-dock_cam"] button:hover{{background-image:url("{dock_icon('camera')}")!important}}
div[class*="st-key-dock_id"] button,div[class*="st-key-dock_id"] button:hover{{background-image:url("{dock_icon('identify')}")!important}}
div[class*="st-key-dock_hist"] button,div[class*="st-key-dock_hist"] button:hover{{background-image:url("{dock_icon('history')}")!important}}
div[class*="st-key-dock_qr"] button,div[class*="st-key-dock_qr"] button:hover{{background-image:url("{dock_icon('qr')}")!important}}
div[class*="st-key-dock_home"] button:focus,div[class*="st-key-dock_home"] button:active{{background-image:url("{ICONS['home']}")!important}}
div[class*="st-key-dock_cam"] button:focus,div[class*="st-key-dock_cam"] button:active{{background-image:url("{ICONS['camera']}")!important}}
div[class*="st-key-dock_id"] button:focus,div[class*="st-key-dock_id"] button:active{{background-image:url("{ICONS['identify']}")!important}}
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
    'coffee':'커피 · 차',
    'sauce':'김치 · 소스',
    'oil':'기름 · 삼겹살',
    'fruit':'과일 · 와인',
    'blood':'피 · 혈액',
    'makeup':'화장품 · 립스틱',
    'ink':'볼펜 · 잉크',
    'sweat':'땀 · 누런때',
    'mud':'흙 · 진흙',
    'rust':'녹물 · 금속',
    'gum':'껌 · 접착제',
    'unknown':'생활 얼룩'
}

MAT_NAME={
    'cotton':'면 · 티셔츠',
    'denim':'청바지 · 데님',
    'poly':'운동복 · 합성섬유',
    'knit':'니트 · 가디건',
    'silk':'실크 · 블라우스',
    'linen':'린넨 · 셔츠',
    'padding':'패딩 · 점퍼',
    'towel':'수건 · 양말',
    'school':'교복 · 정장',
    'bedding':'이불 · 침구'
}

QUICK_STAINS=[
    ('음식·양념','sauce'),
    ('음료','coffee'),
    ('기름·유분','oil'),
    ('혈액·체액','blood'),
    ('과일·색소','fruit'),
    ('화장품','makeup'),
    ('필기구·물감','ink'),
    ('땀·찌든때','sweat'),
    ('흙·식물','mud'),
    ('녹·금속','rust'),
    ('껌·접착제','gum'),
    ('기타·모름','unknown'),
]

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
        return k
    if secret('OPENAI_API_KEY'):
        try:
            from openai import OpenAI
            client=OpenAI(api_key=secret('OPENAI_API_KEY'),timeout=12,max_retries=0)
            response=client.chat.completions.create(
                model=secret('OPENAI_MODEL','gpt-4o-mini'),
                max_tokens=60,
                response_format={'type':'json_object'},
                messages=[
                    {'role':'system','content':'Classify any stain keyword into one ID: "coffee","sauce","oil","fruit","blood","makeup","ink","sweat","mud","rust","gum","unknown". Return JSON {"kind":"..."}.'},
                    {'role':'user','content':text}
                ]
            )
            data=json.loads(response.choices[0].message.content)
            ai_k=data.get('kind','unknown')
            if ai_k in LABEL:
                return ai_k
        except Exception:
            pass
    return 'unknown'

def show_solution_immediately(kind, query_name=''):
    S.kind = kind if kind in LABEL else 'unknown'
    S.query_name = query_name.strip()
    title_name = S.query_name if S.query_name else LABEL[S.kind]
    if S.get('history_order') != 'oldest_first':
        S.history = list(reversed(S.history))
        S.history_order = 'oldest_first'
    S.history.append({'name':title_name,'time':datetime.now().strftime('%m.%d %H:%M')})
    go('result')

def start(kind):
    S.kind = kind if kind in LABEL else 'unknown'
    S.query_name = ''
    S.material='cotton';S.age='fresh'
    go('material')

def bottom_dock():
    with st.container(key='bottom_dock'):
        d1,d2,d3,d4,d5=st.columns(5)
        if d1.button('홈',key='dock_home',use_container_width=True,type='primary' if active_tab=='home' else 'secondary'):go('find')
        if d2.button('카메라',key='dock_cam',use_container_width=True,type='primary' if active_tab=='camera' else 'secondary'):go('camera')
        if d3.button('얼룩찾기',key='dock_id',use_container_width=True,type='primary' if active_tab=='identify' else 'secondary'):go('identify')
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
                max_tokens=80,
                response_format={'type':'json_object'},
                messages=[
                    {'role':'system','content':'Classify the clothing stain into one ID: "coffee", "sauce", "oil", "fruit", "blood", "makeup", "ink", "sweat", "mud", "rust", "gum". Return JSON {"kind":"..."}.'},
                    {'role':'user','content':[{'type':'text','text':'얼룩 종류를 판별해 주세요.'},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()}}]}
                ]
            )
            data=json.loads(response.choices[0].message.content)
            k=data.get('kind','sauce')
            if k in LABEL:
                return k
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
        return 'blood'
    if bright<85 or abs(r-b)>34:
        return 'ink'
    if r>g>b and (r-b)>24:
        return 'sauce'
    return 'oil'

def has_sup(name):
    return name in S.supplies

def build_custom_plan():
    k = S.kind if S.kind in LABEL else 'unknown'
    q = S.query_name if S.query_name else LABEL[k]

    surf = '주방세제' if has_sup('주방세제') else ('비누' if has_sup('비누') else ('치약' if has_sup('치약') else '주방세제'))
    acid = '식초'
    alkali = '베이킹소다' if has_sup('베이킹소다') else ('소금' if has_sup('소금') else ('치약' if has_sup('치약') else '베이킹소다'))
    solvent = '소독에탄올' if has_sup('소독에탄올') else ('클렌징오일' if has_sup('클렌징오일') else ('치약' if has_sup('치약') else '소독에탄올'))

    if k=='coffee':
        needed = [surf, acid] + (['소금'] if has_sup('소금') else [])
        steps=[
            (f'{surf}로 가볍게 두드리기',f'얼룩에 {surf}를 묻혀 손끝으로 톡톡 두드려 유분과 당분을 먼저 빼냅니다.'),
            (f'물 헹굼 후 {acid} 적시기',f'물로 가볍게 헹군 뒤 {acid}를 몇 방울 적셔 남은 갈색 자국을 뺍니다.'),
            ('미온수로 헹구기','거품과 얼룩이 남지 않도록 물로 깨끗이 헹굽니다.')
        ]
    elif k=='sauce':
        needed = [surf, alkali]
        steps=[
            (f'마른 얼룩에 {surf} 바르기',f'물을 묻히기 전 {surf} 원액을 발라 양념 기름기를 먼저 녹입니다.'),
            (f'{alkali} 풀어 가볍게 문지르기',f'미온수에 {alkali}를 조금 풀어 남은 붉은 양념 자국을 빼냅니다.'),
            ('미온수 헹굼 후 건조','따뜻한 물로 헹군 뒤 말리면 자국이 깔끔히 사라집니다.')
        ]
    elif k=='oil':
        needed = [surf, alkali]
        steps=[
            (f'물기 없이 {surf} 바르기',f'마른 상태에서 {surf}를 바로 발라 기름기를 먼저 감싸 분리합니다.'),
            (f'{alkali} 뿌리고 따뜻한 물로 문지르기',f'{alkali}를 살짝 뿌린 뒤 미온수로 굳은 기름을 녹여냅니다.'),
            ('따뜻한 물로 충분히 헹구기','기름기가 다시 남지 않도록 온수로 깨끗이 헹궈냅니다.')
        ]
    elif k=='fruit':
        needed = [acid, surf]
        steps=[
            (f'{acid} 먼저 적시기',f'과일·와인 자국에 {acid}를 몇 방울 적셔 색이 배는 것을 막습니다.'),
            (f'물 헹굼 후 {surf}로 두드리기',f'가볍게 헹군 뒤 {surf} 거품으로 남은 얼룩을 빼냅니다.'),
            ('찬물로 깨끗이 헹구기','단 성분이 남지 않도록 찬물로 헹궈 마무리합니다.')
        ]
    elif k=='blood':
        oxy = '과산화수소' if has_sup('과산화수소') else ('소금' if has_sup('소금') else alkali)
        needed = [surf, oxy]
        steps=[
            (f'찬물 + {surf}로 불리기',f'반드시 찬물로 적신 뒤 {surf}를 묻혀 핏자국을 불려냅니다.'),
            (f'{oxy}로 남은 핏기 빼기',f'찬물로 한 번 헹군 뒤 {oxy}를 사용해 스며든 흔적을 지워냅니다.'),
            ('찬물로 헹구기','더운물을 쓰지 말고 찬물로 깨끗이 씻어냅니다.')
        ]
    elif k=='makeup':
        oil_remover = '클렌징오일' if has_sup('클렌징오일') else ('소독에탄올' if has_sup('소독에탄올') else surf)
        needed = [oil_remover, surf]
        steps=[
            (f'{oil_remover}로 화장품 녹이기',f'마른 상태에서 {oil_remover}를 발라 화장품 유분을 먼저 녹입니다.'),
            (f'{surf}로 2차 거품 세척',f'녹아 나온 색소 기름기를 {surf} 거품으로 한 번 더 잡아 빼냅니다.'),
            ('따뜻한 물로 헹구기','남은 유분기가 없도록 미온수로 헹궈 마무리합니다.')
        ]
    elif k=='ink':
        needed = [solvent, surf]
        steps=[
            (f'{solvent}로 톡톡 두드리기',f'옷 밑에 휴지를 깔고 {solvent}를 묻혀 두드려 잉크를 휴지 쪽으로 빼냅니다.'),
            (f'{surf}로 남은 자국 씻기',f'느슨해진 잉크 자국을 {surf} 거품으로 감싸 지워냅니다.'),
            ('미온수로 헹구기','잉크가 번지지 않는지 확인하고 물로 깨끗이 헹굽니다.')
        ]
    elif k=='sweat':
        needed = [surf, alkali]
        steps=[
            (f'{surf}로 목·겨드랑이 문지르기',f'누렇게 변한 부위에 {surf}를 발라 피지 기름기를 먼저 녹입니다.'),
            (f'{alkali} 푼 온수에 10분 담그기',f'{alkali}를 푼 따뜻한 물에 담가 누런 때를 빼냅니다.'),
            ('미온수로 충분히 헹구기','세제 성분이 남지 않도록 깨끗한 물로 헹궈 마무리합니다.')
        ]
    elif k=='mud':
        brush = '비누' if has_sup('비누') else ('치약' if has_sup('치약') else surf)
        needed = [brush, alkali]
        steps=[
            ('마른 상태에서 흙 먼저 털기','젖은 채로 문지르지 말고 마른 흙가루를 먼저 털어냅니다.'),
            (f'{brush} + {alkali}로 거품 세척',f'{brush}와 {alkali}로 섬유 틈새의 진흙·풀물을 빼냅니다.'),
            ('미온수로 헹구기','입자가 남지 않도록 물로 깨끗이 헹궈냅니다.')
        ]
    elif k=='rust':
        needed = [acid] + (['소금'] if has_sup('소금') else []) + [surf]
        steps=[
            (f'{acid} 적셔 10분 불리기',f'녹물 위에 {acid}를 적셔 녹 자국을 천천히 불립니다.'),
            (f'물 헹굼 후 {surf}로 닦아내기',f'물로 먼저 헹군 뒤 {surf} 거품으로 두드려 빼냅니다.'),
            ('찬물로 충분히 헹구기','성분이 남지 않도록 물로 깨끗이 헹굽니다.')
        ]
    elif k=='gum':
        needed = [solvent, surf]
        steps=[
            ('얼음으로 굳혀서 떼어내기','얼음을 비닐에 넣어 2분간 대어 딱딱하게 굳힌 뒤 먼저 떼어냅니다.'),
            (f'{solvent}로 끈적임 녹이기',f'남은 자국에 {solvent}를 묻혀 살살 녹여냅니다.'),
            (f'{surf}로 세척 후 헹구기',f'{surf} 거품으로 닦아낸 뒤 미온수로 깨끗이 헹굽니다.')
        ]
    else:
        needed = [surf, alkali]
        steps=[
            (f'찬물로 가볍게 두드리기',f"'{q}' 얼룩이 번지지 않게 찬물과 휴지로 표면을 먼저 눌러 닦아냅니다."),
            (f'{surf} 거품으로 부분 세척',f'{surf}를 소량 묻혀 손끝으로 가볍게 두드려 자국을 빼냅니다.'),
            ('깨끗한 물로 충분히 헹구기','확인되지 않은 얼룩은 강한 약품을 섞지 말고 물로 충분히 헹궈 마무리합니다.')
        ]
    return list(dict.fromkeys(needed)), steps

if S.page=='start':
    st.markdown(f'<div class="splash-auto"><div class="splash-logo-anim"><img src="{ICONS["logo"]}"/></div><div class="splash-name-anim">STREM</div></div>',unsafe_allow_html=True)
    time.sleep(1.35)
    go('find')

st.markdown(f'<div class="brand"><div class="brand-left"><img src="{ICONS["logo"]}"/>STREM</div></div>',unsafe_allow_html=True)

if S.page=='find':
    with st.form('search',clear_on_submit=False):
        sc1,sc2=st.columns([7.5,1])
        with sc1:
            text=st.text_input('얼룩 검색',placeholder='묻은 얼룩을 입력해주세요',label_visibility='collapsed')
        with sc2:
            submit=st.form_submit_button(' ',use_container_width=True)
    if submit and text.strip():
        found=smart_search_kind(text)
        show_solution_immediately(found, query_name=text.strip())

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
        st.markdown('<span class="pantry-label">보유 용품</span>',unsafe_allow_html=True)
        for row_idx in range(3):
            with st.container(key=f'sup_row{row_idx+1}'):
                cols=st.columns(3)
                for col_idx in range(3):
                    item_idx = row_idx*3 + col_idx
                    item = ALL_SUPPLIES[item_idx]
                    on = item in S.supplies
                    if cols[col_idx].button(item,key=f'sup_{item_idx}',use_container_width=True,type='primary' if on else 'secondary'):
                        if on:S.supplies.remove(item)
                        else:S.supplies.append(item)
                        st.rerun()

    bottom_dock()

elif S.page=='identify':
    st.markdown('<h1>빠른 얼룩 찾기</h1>',unsafe_allow_html=True)
    with st.container(key='id_grid'):
        for i in range(0,len(QUICK_STAINS),2):
            cols=st.columns(2)
            for j in range(2):
                if i+j<len(QUICK_STAINS):
                    lbl,k_val=QUICK_STAINS[i+j]
                    if cols[j].button(lbl,key=f'qid_{i+j}',use_container_width=True):
                        show_solution_immediately(k_val, query_name=lbl)
    bottom_dock()

elif S.page=='camera':
    st.markdown('<h1>모르는 얼룩 촬영</h1>',unsafe_allow_html=True)
    photo=st.camera_input('촬영',label_visibility='collapsed')
    if photo:
        if st.button('이 얼룩 바로 지우기',type='primary',use_container_width=True):
            kind=analyze_stain_photo(photo)
            S.material='cotton';S.age='fresh'
            show_solution_immediately(kind)
    bottom_dock()

elif S.page=='material':
    st.markdown('<h1>옷감 선택</h1>',unsafe_allow_html=True)
    mat_items=list(MAT_NAME.items())
    with st.container(key='mat_grid_fab'):
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
    st.markdown('<h1>얼룩 상태</h1>',unsafe_allow_html=True)
    age_items=[
        ('방금 묻음','fresh'),
        ('조금 마름','dry'),
        ('오래 굳음','old'),
        ('물로 닦음','wiped'),
        ('세탁 후 남음','washed')
    ]
    with st.container(key='age_list'):
        for lbl,val in age_items:
            if st.button(lbl,key=f'age_{val}',use_container_width=True):
                S.age=val
                show_solution_immediately(S.kind, S.query_name)
    bottom_dock()

elif S.page=='result':
    needed, steps = build_custom_plan()
    display_pool = list(dict.fromkeys(needed + S.supplies))[:6]
    chips_html = ''.join(
        f'<span class="{"sup-chip-on" if item in needed else "sup-chip-off"}">{escape(item)}</span>'
        for item in display_pool
    )

    with st.container(key='result_card'):
        st.markdown('<div class="sec-label">필요한 준비물</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sup-chip-wrap">{chips_html}</div>', unsafe_allow_html=True)
        for idx, (t, b) in enumerate(steps, 1):
            st.markdown(f'<div class="step-card"><div class="step-head"><span class="step-num">{idx}</span>{escape(t)}</div><div class="step-desc">{escape(b)}</div></div>', unsafe_allow_html=True)

    if st.button('다른 얼룩 찾기',type='primary',use_container_width=True):go('find')
    bottom_dock()

elif S.page=='history':
    if S.get('history_order') != 'oldest_first':
        S.history = list(reversed(S.history))
        S.history_order = 'oldest_first'
    st.markdown('<h1>최근 기록</h1>',unsafe_allow_html=True)
    with st.container(key='result_card'):
        if S.history:
            for i,x in enumerate(S.history,1):
                st.markdown(f'<div class="step-card"><div class="step-head"><span class="step-num">{i}</span>{escape(x["name"])}</div><div class="step-desc">{escape(x["time"])}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="step-desc">아직 기록이 없어요.</div>',unsafe_allow_html=True)
    bottom_dock()

elif S.page=='share':
    st.markdown('<h1>QR 코드</h1>',unsafe_allow_html=True)
    url=st.text_input('앱 주소',value=secret('APP_URL','https://2611121313-d9pclpfwungek3wl2j9j2s.streamlit.app/'),label_visibility='collapsed')
    parsed=urlparse(url)
    if parsed.scheme=='https' and parsed.netloc:
        buf=io.BytesIO();qrcode.make(url).save(buf,format='PNG')
        qr_b64=base64.b64encode(buf.getvalue()).decode()
        with st.container(key='result_card'):
            st.markdown(f'<div class="qr-center-box"><div class="step-head">휴대폰으로 스캔해 STREM 열기</div><img src="data:image/png;base64,{qr_b64}" alt="QR"/></div>',unsafe_allow_html=True)
            with st.container(key='qr_actions'):
                st.download_button('QR 저장',buf.getvalue(),'STREM_QR.png','image/png',use_container_width=True)
                if st.button('처음 화면',type='primary',use_container_width=True):go('start')
    bottom_dock()
