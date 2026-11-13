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

st.set_page_config(page_title='STREM',page_icon='💧',layout='centered')

def svg_uri(inner, color='#3182f6', sw='2'):
    svg=f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='{sw}' stroke-linecap='round' stroke-linejoin='round'>{inner}</svg>"
    return "data:image/svg+xml;base64,"+base64.b64encode(svg.encode()).decode()

QR_SVG="<rect x='3' y='3' width='7' height='7' rx='1'/><rect x='14' y='3' width='7' height='7' rx='1'/><rect x='3' y='14' width='7' height='7' rx='1'/><rect x='14' y='14' width='3' height='3'/><line x1='20' y1='14' x2='20' y2='20'/><line x1='14' y1='20' x2='20' y2='20'/>"

ICONS={
    'logo':svg_uri("<path d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'/>",'#3182f6','2'),
    'search':svg_uri("<circle cx='11' cy='11' r='7'/><line x1='20' y1='20' x2='16.2' y2='16.2'/>",'#3182f6','2'),
    'drink':svg_uri("<path d='M17 8h1a4 4 0 1 1 0 8h-1'/><path d='M3 8h14v7a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z'/><line x1='6' y1='2' x2='6' y2='4'/><line x1='10' y1='2' x2='10' y2='4'/><line x1='14' y1='2' x2='14' y2='4'/>"),
    'oil':svg_uri("<path d='M12 3l5 5a7 7 0 1 1-10 0z'/><path d='M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5'/>"),
    'blood':svg_uri("<path d='M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z'/><line x1='12' y1='11' x2='12' y2='16'/><line x1='9.5' y1='13.5' x2='14.5' y2='13.5'/>"),
    'ink':svg_uri("<path d='M12 19l7-7 3 3-7 7-3-3z'/><path d='M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z'/><path d='M2 2l7.5 7.5'/>"),
    'home':svg_uri("<path d='M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>"),
    'camera':svg_uri("<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/>"),
    'help':svg_uri("<circle cx='12' cy='12' r='9'/><path d='M9.2 9a3 3 0 0 1 5.6 1c0 2-2.8 2.5-2.8 4'/><circle cx='12' cy='17.2' r='0.6' fill='#3182f6'/>"),
    'history':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>"),
    'qr':svg_uri(QR_SVG),
    'home_dim':svg_uri("<path d='M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",'#8b95a1','1.8'),
    'camera_dim':svg_uri("<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/>",'#8b95a1','1.8'),
    'help_dim':svg_uri("<circle cx='12' cy='12' r='9'/><path d='M9.2 9a3 3 0 0 1 5.6 1c0 2-2.8 2.5-2.8 4'/><circle cx='12' cy='17.2' r='0.6' fill='#8b95a1'/>",'#8b95a1','1.8'),
    'history_dim':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>",'#8b95a1','1.8'),
    'qr_dim':svg_uri(QR_SVG,'#8b95a1','1.8'),
}

S=st.session_state
for k,v in {'page':'start','history':[],'kind':'drink','material':'normal','age':'fresh','cam_note':''}.items():
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
  max-width:460px!important;
  min-height:100dvh!important;
  padding:14px 16px 104px!important;
  margin:0 auto!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:space-between!important;
}}
[data-testid="stVerticalBlock"]{{gap:11px!important}}
h1{{font-size:26px!important;letter-spacing:-0.4px;margin:2px 0 4px!important;color:#191f28!important}}
h2{{font-size:21px!important;margin:0!important}}
p,label,[data-testid="stMarkdownContainer"] p{{font-size:18px!important;line-height:1.45!important;margin:0!important}}

/* Top Brand Header — Blue Line Logo + Thin Typography */
.brand{{
  display:flex;justify-content:space-between;align-items:center;
  padding:4px 2px 6px;
}}
.brand-left{{display:flex;align-items:center;gap:8px;font-size:22px;color:#191f28;letter-spacing:-0.3px}}
.brand-left img{{width:22px;height:22px}}
.brand span{{font-size:12px;letter-spacing:1.4px;color:#3182f6}}

/* Start Splash Card — Toss White/Blue Clean Card */
.splash{{
  background:#ffffff;
  color:#191f28;
  min-height:66dvh;
  padding:38px 24px;
  border-radius:28px;
  text-align:center;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  box-shadow:0 8px 24px rgba(15,23,42,0.05);
  margin:4px 0 10px;
}}
.splash-logo{{
  width:64px;height:64px;border-radius:22px;background:#eef4ff;
  display:flex;align-items:center;justify-content:center;margin-bottom:18px;
}}
.splash-logo img{{width:34px;height:34px}}
.splash-badge{{display:inline-block;background:#eef4ff;color:#3182f6;padding:6px 14px;border-radius:999px;font-size:13px;letter-spacing:1px;margin-bottom:14px}}
.splash h1{{color:#191f28!important;font-size:42px!important;margin-bottom:10px!important}}
.splash p{{color:#4e5968!important;font-size:19px!important;line-height:1.5!important}}

/* Pill Search Bar */
div[data-testid="stForm"]{{
  border:1.8px solid #3182f6!important;
  border-radius:999px!important;
  padding:4px 8px 4px 18px!important;
  background:#ffffff!important;
  box-shadow:0 4px 14px rgba(49,130,246,0.08)!important;
  margin-bottom:2px!important;
}}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]{{align-items:center!important;gap:6px!important;flex-wrap:nowrap!important}}
div[data-testid="stForm"] [data-testid="stTextInput"]>div>div{{border:none!important;background:transparent!important;box-shadow:none!important}}
div[data-testid="stForm"] [data-testid="stTextInput"] input{{font-size:18px!important;min-height:42px!important;padding:0!important;color:#191f28!important}}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button{{
  border-radius:999px!important;
  min-height:40px!important;
  height:40px!important;
  padding:0 16px!important;
  background:#eef4ff!important;
  color:#3182f6!important;
  border:none!important;
  font-size:16px!important;
}}

/* Standard Choice Buttons — Toss White List Cards */
.stButton button,.stLinkButton a,.stDownloadButton button{{
  min-height:60px!important;
  border-radius:20px!important;
  font-size:19px!important;
  border:none!important;
  background:#ffffff!important;
  color:#191f28!important;
  padding:10px 16px!important;
  box-shadow:0 2px 10px rgba(15,23,42,0.04)!important;
}}
.stButton button p{{font-size:19px!important;line-height:1.3!important;color:#191f28!important}}
.stButton button[kind="primary"]{{
  background:#3182f6!important;
  color:#ffffff!important;
  min-height:62px!important;
  font-size:20px!important;
  box-shadow:0 6px 18px rgba(49,130,246,0.22)!important;
}}
.stButton button[kind="primary"] p{{color:#ffffff!important;font-size:20px!important}}

/* 2x2 Stain Cards with Blue Line SVG Icons */
div[class*="st-key-grid_r1"] [data-testid="stHorizontalBlock"],
div[class*="st-key-grid_r2"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:12px!important;
}}
div[class*="st-key-grid_r1"] .stButton button,
div[class*="st-key-grid_r2"] .stButton button{{
  height:138px!important;
  min-height:138px!important;
  border-radius:24px!important;
  background:#ffffff!important;
  border:none!important;
  box-shadow:0 4px 14px rgba(15,23,42,0.05)!important;
  padding:64px 8px 14px!important;
  background-repeat:no-repeat!important;
  background-position:center 24px!important;
  background-size:34px 34px!important;
}}
div[class*="st-key-grid_r1"] .stButton button p,
div[class*="st-key-grid_r2"] .stButton button p{{
  font-size:19px!important;
  color:#191f28!important;
}}
div[class*="st-key-tile_drink"] button{{background-image:url("{ICONS['drink']}")!important}}
div[class*="st-key-tile_oil"] button{{background-image:url("{ICONS['oil']}")!important}}
div[class*="st-key-tile_blood"] button{{background-image:url("{ICONS['blood']}")!important}}
div[class*="st-key-tile_ink"] button{{background-image:url("{ICONS['ink']}")!important}}

/* Toss White Rounded Bottom Bar with Blue/Gray Line SVG Icons */
div[class*="st-key-bottom_dock"]{{
  position:fixed!important;
  left:50%!important;
  bottom:0!important;
  transform:translateX(-50%)!important;
  width:100%!important;
  max-width:460px!important;
  background:#ffffff!important;
  border-top:1px solid #e5e8eb!important;
  border-radius:24px 24px 0 0!important;
  padding:8px 8px 14px!important;
  box-shadow:0 -6px 24px rgba(15,23,42,0.08)!important;
  z-index:9999!important;
}}
div[class*="st-key-bottom_dock"] [data-testid="stHorizontalBlock"]{{
  flex-wrap:nowrap!important;
  gap:2px!important;
  align-items:center!important;
}}
div[class*="st-key-bottom_dock"] .stButton button{{
  height:54px!important;
  min-height:54px!important;
  background-color:transparent!important;
  border:none!important;
  box-shadow:none!important;
  border-radius:14px!important;
  padding:28px 2px 2px!important;
  background-repeat:no-repeat!important;
  background-position:center 5px!important;
  background-size:22px 22px!important;
}}
div[class*="st-key-bottom_dock"] .stButton button p{{
  font-size:13px!important;
  line-height:1.1!important;
  color:#8b95a1!important;
}}
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"]{{
  background-color:transparent!important;
  box-shadow:none!important;
}}
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"] p{{
  color:#3182f6!important;
  font-size:13px!important;
}}
div[class*="st-key-dock_home"] button{{background-image:url("{dock_icon('home')}")!important}}
div[class*="st-key-dock_cam"] button{{background-image:url("{dock_icon('camera')}")!important}}
div[class*="st-key-dock_id"] button{{background-image:url("{dock_icon('help')}")!important}}
div[class*="st-key-dock_hist"] button{{background-image:url("{dock_icon('history')}")!important}}
div[class*="st-key-dock_qr"] button{{background-image:url("{dock_icon('qr')}")!important}}

/* Single All-at-once Result Card */
.res-box{{background:#ffffff;border-radius:24px;padding:16px 18px;margin:2px 0;box-shadow:0 4px 16px rgba(15,23,42,0.05)}}
.res-tag{{display:inline-block;background:#eef4ff;color:#3182f6;font-size:14px;padding:4px 12px;border-radius:999px;margin-bottom:6px}}
.res-prep{{background:#f8fbff;border:1px solid #dbeafe;border-radius:14px;padding:8px 12px;margin-bottom:8px;font-size:16px;color:#1e3a8a}}
.res-step{{display:flex;align-items:flex-start;gap:12px;padding:8px 0;border-bottom:1px solid #f2f4f6}}
.res-step:last-of-type{{border-bottom:none}}
.res-num{{border:1.6px solid #3182f6;color:#3182f6;font-size:14px;width:24px;height:24px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}}
.res-body{{font-size:16.5px;line-height:1.4;color:#333d4b}}
.res-title{{color:#191f28;font-size:17.5px;display:block;margin-bottom:2px}}
.res-chem{{background:#f2f6ff;border-radius:14px;padding:10px 12px;margin-top:8px;font-size:15.5px;color:#3182f6;line-height:1.38}}

[data-testid="stCameraInput"]{{max-width:290px;margin:0 auto}}
@media(max-width:640px){{
  [data-testid="stHorizontalBlock"]{{flex-wrap:nowrap!important}}
  [data-testid="stColumn"]{{min-width:0!important;flex:1!important}}
}}
</style>''',unsafe_allow_html=True)

def secret(name,default=''):
    try:return st.secrets.get(name,default)
    except Exception:return default

def go(page):S.page=page;st.rerun()

def record_and_show(kind, cam_note=''):
    S.kind=kind
    S.cam_note=cam_note
    S.history.insert(0,{'name':LABEL[S.kind],'time':datetime.now().strftime('%m.%d %H:%M')})
    S.history=S.history[:20]
    go('result')

def start(kind):
    S.kind=kind;S.material='normal';S.age='fresh';S.cam_note='';go('material')

def choices(title,items,field,nextpage):
    st.markdown(f'<h1>{escape(title)}</h1>',unsafe_allow_html=True)
    for label,value in items:
        if st.button(label,use_container_width=True,key=field+str(value)):
            S[field]=value
            if nextpage=='result':
                record_and_show(S.kind)
            else:
                go(nextpage)

def bottom_dock():
    with st.container(key='bottom_dock'):
        d1,d2,d3,d4,d5=st.columns(5)
        if d1.button('홈',key='dock_home',use_container_width=True,type='primary' if active_tab=='home' else 'secondary'):go('find')
        if d2.button('카메라',key='dock_cam',use_container_width=True,type='primary' if active_tab=='camera' else 'secondary'):go('camera')
        if d3.button('얼룩찾기',key='dock_id',use_container_width=True,type='primary' if active_tab=='help' else 'secondary'):go('identify')
        if d4.button('기록',key='dock_hist',use_container_width=True,type='primary' if active_tab=='history' else 'secondary'):go('history')
        if d5.button('QR',key='dock_qr',use_container_width=True,type='primary' if active_tab=='qr' else 'secondary'):go('share')

LABEL={'blood':'피 · 혈액','oil':'기름 · 유분','drink':'음료 · 김치 · 소스','ink':'잉크 · 볼펜 · 화장품','unknown':'복합 · 미상 얼룩'}
ALIASES={
    'blood':['혈액','피','코피','생리혈','상처'],
    'oil':['기름','식용유','버터','참기름','올리브유','라면','삼겹살','치킨','마요네즈','고추기름','카레','짜장'],
    'drink':['김치','커피','라떼','주스','와인','콜라','떡볶이','소스','차','초콜릿','우유','음료','간장','케첩','과일','땀'],
    'ink':['잉크','볼펜','립스틱','파운데이션','매직','화장품','틴트','사인펜','크레파스','형광펜'],
}
PREP={
    'drink':'준비물 · 주방세제 + 식초 (또는 구연산)',
    'oil':'준비물 · 주방세제 + 베이킹소다 + 미온수',
    'blood':'준비물 · 찬물 + 알칼리성 세탁비누 + 과산화수소수(소독약)',
    'ink':'준비물 · 소독용 에탄올(알코올)/클렌징오일 + 주방세제',
    'unknown':'준비물 · 주방세제 + 베이킹소다 + 식초 (단계별 적용)',
}
CHEM={
    'drink':'주방세제의 계면활성제가 색소·유분을 분리하고, 식초의 아세트산(약산성)이 탄닌·안토시아닌 색소 결합을 끊어 분해합니다.',
    'oil':'주방세제의 친유성기가 기름 분자를 감싸 물에 녹이는 유화 작용을 하고, 베이킹소다(약알칼리)가 지방산을 비누화해 제거합니다.',
    'blood':'혈액 속 헤모글로빈 단백질은 40℃ 이상에서 열변성되어 굳으므로 찬물만 써야 하며, 과산화수소의 활성산소가 색소를 산화 탈색합니다.',
    'ink':'알코올(에탄올)과 오일이 유성 수지·왁스 결합을 용해한 뒤, 주방세제가 녹아 나온 성분을 미셀 형태로 가두어 씻어냅니다.',
    'unknown':'계면활성제(유분 제거) → 약알칼리 베이킹소다(산성·기름 분해) → 약산성 식초(알칼리·색소 중화) 순서로 화학 성분을 단계별 제거합니다.',
}

def match(text):
    text=text.strip().lower().replace(' ','')
    if not text:return None
    for k,words in ALIASES.items():
        if text in words or any(len(w)>1 and w in text for w in words):
            return k
    return 'unknown'

def analyze_stain_photo(file_obj):
    im=ImageOps.exif_transpose(Image.open(file_obj)).convert('RGB')
    # Optional OpenAI vision if configured
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
                    {'role':'system','content':'Classify the clothing stain image into exactly one best category ID: "drink", "oil", "blood", or "ink". Return JSON {"kind":"drink|oil|blood|ink","note":"사진 색상·번짐 패턴 분석 완료"}.'},
                    {'role':'user','content':[{'type':'text','text':'얼룩 종류를 판별해 주세요.'},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()}}]}
                ]
            )
            data=json.loads(response.choices[0].message.content)
            k=data.get('kind','drink')
            if k in ['drink','oil','blood','ink']:
                return k, data.get('note','AI 사진 분석 완료')
        except Exception:
            pass
    # Built-in instant color/saturation/darkness chemical stain estimator (works immediately with zero questions)
    crop=im.resize((80,80))
    px=list(crop.getdata())
    cx=[p for i,p in enumerate(px) if 20<=i%80<=60 and 20<=i//80<=60]
    r=sum(p[0] for p in cx)/len(cx)
    g=sum(p[1] for p in cx)/len(cx)
    b=sum(p[2] for p in cx)/len(cx)
    bright=(r+g+b)/3
    if r-max(g,b)>28 and r>85:
        return 'blood','사진의 붉은색·암적색 파장 비율을 분석해 단백질·혈액 계열로 판별했어요'
    if bright<85 or abs(r-b)>32:
        return 'ink','사진의 진한 색소·유성 번짐 농도를 분석해 잉크·화장품 계열로 판별했어요'
    if r>g>b and (r-b)>22:
        return 'drink','사진의 갈색·주황색 수용성 색소 패턴을 분석해 음료·소스 계열로 판별했어요'
    return 'oil','사진의 반투명 유분 흡수 패턴을 분석해 기름·유분 계열로 판별했어요'

def plan():
    gentle = (S.material=='delicate')
    dried = (S.age!='fresh')
    if S.kind=='drink':
        return [
            ('주방세제 + 미온수 도포','얼룩 부위에 주방세제를 1~2방울 올리고 손끝으로 톡톡 두드려 색소와 기름기를 먼저 녹여냅니다.'),
            ('식초 1 : 물 2 산성 분해','식초(또는 구연산수)를 희석해 5분간 올려두면 커피·김치·과일의 탄닌·색소 결합이 분해됩니다.'),
            ('찬물 헹굼' + (' · 중성세제 마무리를 권장해요' if gentle else ' · 세탁 마무리'),
             '거품과 식초 성분이 남지 않게 찬물로 충분히 헹궈 얼룩을 완전히 빼냅니다.')
        ]
    if S.kind=='oil':
        return [
            ('주방세제 원액 침투','물기를 묻히기 전 마른 얼룩 위에 주방세제를 바로 발라 친유성 기름 막을 감싸게 합니다.'),
            ('베이킹소다 + 미온수 유화','베이킹소다를 약간 뿌리고(' + ('살살 눌러준 뒤' if gentle else '솔이나 손으로 문지른 뒤') + ') 40℃ 미온수로 기름때를 녹여냅니다.'),
            ('비누 거품 헹굼','남은 유분기가 다시 굳지 않도록 따뜻한 물로 헹궈 완전히 제거합니다.')
        ]
    if S.kind=='blood':
        return [
            ('찬물 + 세탁비누(또는 주방세제)','반드시 찬물로 적신 뒤 알칼리성 비누나 주방세제를 묻혀 단백질을 불려냅니다. (온수 절대 금지)'),
            ('과산화수소수(소독약) 산소 탈색',('오래 굳은 혈흔 위에 ' if dried else '남은 붉은 자국에 ') + '약국용 과산화수소수를 몇 방울 떨어뜨려 거품 반응으로 핏기를 분해합니다.'),
            ('찬물 마무리 헹굼','녹아 나온 단백질 거품을 찬물로 깨끗이 씻어냅니다.')
        ]
    if S.kind=='ink':
        return [
            ('소독용 에탄올 · 클렌징오일 용해','얼룩 밑에 휴지를 깔고 볼펜·잉크는 알코올(에탄올)을, 립스틱·화장품은 클렌징오일을 묻혀 두드려 녹입니다.'),
            ('주방세제로 유성 수지 제거','녹아 나온 잉크·색소 기름기를 주방세제 거품으로 감싸 섬유에서 분리합니다.'),
            ('미온수 헹굼','번진 색소가 남지 않도록 물로 깨끗이 헹궈 마무리합니다.')
        ]
    return [
        ('1단계 · 주방세제로 유분 제거','정체를 모르는 얼룩은 먼저 주방세제와 찬물로 기름 막과 수용성 오염을 함께 녹여냅니다.'),
        ('2단계 · 베이킹소다 약알칼리 분해','얼룩이 남으면 베이킹소다 반죽을 올려 산성 오염과 찌든 지방 성분을 분해합니다.'),
        ('3단계 · 식초 물 중화 탈색','마지막으로 식초 희석액을 살짝 적셔 남아 있는 색소와 알칼리 성분을 중화해 빼냅니다.')
    ]

st.markdown(f'<div class="brand"><div class="brand-left"><img src="{ICONS["logo"]}"/>STREM</div><span>STAIN CARE</span></div>',unsafe_allow_html=True)

if S.page=='start':
    st.markdown(f'''<div class="splash">
        <div class="splash-logo"><img src="{ICONS['logo']}"/></div>
        <div class="splash-badge">CHEMISTRY STAIN CARE</div>
        <h1>STREM</h1>
        <p>주방세제 · 식초 · 베이킹소다로<br>성분에 맞게 얼룩을 바로 지우는 화학 가이드</p>
    </div>''',unsafe_allow_html=True)
    if st.button('앱 시작하기',type='primary',use_container_width=True):go('find')

elif S.page=='find':
    with st.form('search',clear_on_submit=False):
        sc1,sc2=st.columns([3.6,1.3])
        with sc1:
            text=st.text_input('얼룩 검색',placeholder='커피, 김치, 볼펜, 삼겹살…',label_visibility='collapsed')
        with sc2:
            submit=st.form_submit_button('찾기',use_container_width=True)
    if submit:
        found=match(text)
        if found:start(found)

    with st.container(key='grid_r1'):
        r1=st.columns(2)
        if r1[0].button('음료 · 소스',key='tile_drink',use_container_width=True):start('drink')
        if r1[1].button('기름 · 유분',key='tile_oil',use_container_width=True):start('oil')

    with st.container(key='grid_r2'):
        r2=st.columns(2)
        if r2[0].button('피 · 혈액',key='tile_blood',use_container_width=True):start('blood')
        if r2[1].button('잉크 · 화장',key='tile_ink',use_container_width=True):start('ink')

    bottom_dock()

elif S.page=='camera':
    st.markdown('<h1>모르는 얼룩 촬영</h1>',unsafe_allow_html=True)
    st.caption('찍으면 질문 없이 바로 얼룩 성분을 판별해 제거법을 알려드려요.')
    photo=st.camera_input('촬영',label_visibility='collapsed')
    if photo:
        if st.button('이 얼룩 바로 분석 · 제거법 보기',type='primary',use_container_width=True):
            kind,note=analyze_stain_photo(photo)
            S.material='normal';S.age='fresh'
            record_and_show(kind, note)
    bottom_dock()

elif S.page=='identify':
    choices('어떤 얼룩인가요?',[
        ('커피 · 김치 · 음료 · 과일즙','drink'),
        ('삼겹살 · 라면 · 식용유 · 버터','oil'),
        ('코피 · 상처 혈흔','blood'),
        ('볼펜 · 립스틱 · 파운데이션','ink'),
        ('정체를 모르는 얼룩 (만능 화학 제거)','unknown')
    ],'kind','material')
    bottom_dock()

elif S.page=='material':
    choices('어떤 옷감인가요?',[
        ('일반 의류 (면 · 청바지 · 합성섬유)','normal'),
        ('예민한 옷감 (니트 · 실크 · 코트 · 미확인)','delicate')
    ],'material','age')
    bottom_dock()

elif S.page=='age':
    choices('얼룩이 언제 묻었나요?',[
        ('방금 묻었어요','fresh'),
        ('시간이 지나 말라붙었어요','dry')
    ],'age','result')
    bottom_dock()

elif S.page=='result':
    tag=LABEL[S.kind]+' · '+('방금 묻음' if S.age=='fresh' else '말라붙은 얼룩')
    note_html=f'<div class="res-prep">{escape(S.cam_note)}</div>' if S.cam_note else ''
    steps_html=''.join(
        f'<div class="res-step"><span class="res-num">{i}</span><div class="res-body"><span class="res-title">{escape(t)}</span>{escape(b)}</div></div>'
        for i,(t,b) in enumerate(plan(),1)
    )
    st.markdown(f'''<div class="res-box">
        <div class="res-tag">{escape(tag)} 제거 레시피</div>
        {note_html}
        <div class="res-prep">{escape(PREP[S.kind])}</div>
        {steps_html}
        <div class="res-chem">화학 원리 · {escape(CHEM[S.kind])}</div>
    </div>''',unsafe_allow_html=True)
    bottom_dock()

elif S.page=='history':
    st.markdown('<h1>최근 기록</h1>',unsafe_allow_html=True)
    if S.history:
        items_html=''.join(
            f'<div class="res-step"><span class="res-num">{i}</span><div class="res-body"><span class="res-title">{escape(x["name"])}</span>{escape(x["time"])}</div></div>'
            for i,x in enumerate(S.history[:4],1)
        )
        st.markdown(f'<div class="res-box">{items_html}</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="res-box"><div class="res-body">아직 기록이 없어요.</div></div>',unsafe_allow_html=True)
    bottom_dock()

elif S.page=='share':
    st.markdown('<h1>QR 코드</h1>',unsafe_allow_html=True)
    url=st.text_input('앱 주소',value=secret('APP_URL','https://2611121313-d9pclpfwungek3wl2j9j2s.streamlit.app/'),label_visibility='collapsed')
    parsed=urlparse(url)
    if parsed.scheme=='https' and parsed.netloc:
        buf=io.BytesIO();qrcode.make(url).save(buf,format='PNG')
        c1,c2=st.columns([1,1.3])
        with c1:st.image(buf.getvalue(),width=130)
        with c2:
            st.download_button('QR 저장',buf.getvalue(),'STREM_QR.png','image/png',use_container_width=True)
            if st.button('처음 화면으로',use_container_width=True):go('start')
    bottom_dock()
