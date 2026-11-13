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
    'menu':svg_uri("<line x1='4' y1='7' x2='20' y2='7'/><line x1='4' y1='12' x2='20' y2='12'/><line x1='4' y1='17' x2='20' y2='17'/>"),
    'home_dim':svg_uri("<path d='M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",'#8b95a1','1.8'),
    'camera_dim':svg_uri("<path d='M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z'/><circle cx='12' cy='13' r='4'/>",'#8b95a1','1.8'),
    'help_dim':svg_uri("<circle cx='12' cy='12' r='9'/><path d='M9.2 9a3 3 0 0 1 5.6 1c0 2-2.8 2.5-2.8 4'/><circle cx='12' cy='17.2' r='0.6' fill='#8b95a1'/>",'#8b95a1','1.8'),
    'history_dim':svg_uri("<circle cx='12' cy='12' r='9'/><polyline points='12 7 12 12 15.5 14'/>",'#8b95a1','1.8'),
    'menu_dim':svg_uri("<line x1='4' y1='7' x2='20' y2='7'/><line x1='4' y1='12' x2='20' y2='12'/><line x1='4' y1='17' x2='20' y2='17'/>",'#8b95a1','1.8'),
}

S=st.session_state
for k,v in {'page':'start','history':[],'kind':'unknown','material':None,'wash':None,'age':None,'candidates':[]}.items():
    if k not in S:S[k]=v

active_tab={
    'find':'home',
    'camera':'camera',
    'identify':'help','material':'help','wash':'help','age':'help','result':'help','candidate':'help',
    'history':'history',
    'share':'menu',
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

/* Pill Search Bar — Clean White Card with Blue Border & Line Icon */
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
div[class*="st-key-dock_share"] button{{background-image:url("{dock_icon('menu')}")!important}}

/* Single All-at-once Result Card — Clean Toss White Card */
.res-box{{background:#ffffff;border-radius:24px;padding:18px 18px;margin:4px 0;box-shadow:0 4px 16px rgba(15,23,42,0.05)}}
.res-tag{{display:inline-block;background:#eef4ff;color:#3182f6;font-size:14px;padding:5px 12px;border-radius:999px;margin-bottom:10px}}
.res-step{{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1px solid #f2f4f6}}
.res-step:last-of-type{{border-bottom:none}}
.res-num{{border:1.6px solid #3182f6;color:#3182f6;font-size:14px;width:24px;height:24px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}}
.res-body{{font-size:17px;line-height:1.45;color:#333d4b}}
.res-title{{color:#191f28;font-size:18px;display:block;margin-bottom:2px}}
.res-chem{{background:#f8fbff;border:1px solid #dbeafe;border-radius:16px;padding:11px 14px;margin-top:10px;font-size:16px;color:#3182f6;line-height:1.4}}
.res-warn{{font-size:14px;color:#8b95a1;margin-top:8px;text-align:center}}

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
def start(kind):
    S.kind=kind;S.material=None;S.wash=None;S.age=None;go('material')
def choices(title,items,field,nextpage):
    st.markdown(f'<h1>{escape(title)}</h1>',unsafe_allow_html=True)
    for label,value in items:
        if st.button(label,use_container_width=True,key=field+str(value)):
            S[field]=value
            if nextpage=='result':
                S.history.insert(0,{'name':LABEL[S.kind],'time':datetime.now().strftime('%m.%d %H:%M')})
                S.history=S.history[:20]
            go(nextpage)

def bottom_dock():
    with st.container(key='bottom_dock'):
        d1,d2,d3,d4,d5=st.columns(5)
        if d1.button('홈',key='dock_home',use_container_width=True,type='primary' if active_tab=='home' else 'secondary'):go('find')
        if d2.button('카메라',key='dock_cam',use_container_width=True,type='primary' if active_tab=='camera' else 'secondary'):go('camera')
        if d3.button('얼룩찾기',key='dock_id',use_container_width=True,type='primary' if active_tab=='help' else 'secondary'):go('identify')
        if d4.button('기록',key='dock_hist',use_container_width=True,type='primary' if active_tab=='history' else 'secondary'):go('history')
        if d5.button('전체',key='dock_share',use_container_width=True,type='primary' if active_tab=='menu' else 'secondary'):go('share')

LABEL={'blood':'피 · 혈액','oil':'기름 · 유분','drink':'음료 · 소스','ink':'잉크 · 화장품','unknown':'종류 불명'}
ALIASES={'blood':['혈액','피','코피','생리혈'],'oil':['기름','식용유','버터','참기름','올리브유','라면','삼겹살','치킨','마요네즈'],'drink':['김치','커피','라떼','주스','와인','콜라','떡볶이','소스','차','초콜릿','우유','음료','간장','케첩','카레'],'ink':['잉크','볼펜','립스틱','파운데이션','매직','화장품','틴트','사인펜','크레파스']}
CHEM={'blood':'혈액 단백질은 온수에 굳으므로 찬물을 써야 해요.','oil':'기름 성분은 계면활성제로 유화시켜 물에 씻어내요.','drink':'색소·당분 복합 얼룩은 수분 흡수 후 중성세제로 분해해요.','ink':'안료·유분 얼룩은 임의 용제 사용 시 번질 수 있어요.','unknown':'모르는 얼룩은 열 고정 전에 세탁 표시부터 확인해요.'}

def match(text):
    text=text.strip().lower().replace(' ','')
    if not text:return []
    exact=[k for k,words in ALIASES.items() if text in words]
    if exact:return exact
    return list(dict.fromkeys(k for k,words in ALIASES.items() if any(len(w)>1 and w in text for w in words)))

def plan():
    if S.wash!='yes' or S.material!='normal':
        return [('세탁 표시 확인','물·세제를 바르지 말고 라벨을 확인하세요.'),('전문 세탁소 문의','울·실크·드라이 전용은 세탁소에 맡기세요.'),('열·마찰 금지','문지르거나 다리미 열을 가하지 마세요.')]
    if S.kind in ['unknown','ink']:
        return [('문지르지 않기','문지르면 섬유 깊숙이 번집니다.'),('용제 임의 사용 금지','식초·알코올 대신 세탁소에 문의하세요.'),('건조기 사용 금지','열이 닿으면 얼룩이 굳어버립니다.')]
    if S.kind=='blood':
        return [('찬물로 뒷면 헹구기','얼룩 뒷면에서 찬물을 흘려보내세요.'),('중성세제 두드리기','액체 세제를 발라 가볍게 두드리세요.'),('찬물 세탁·자연 건조','얼룩 제거 확인 후 자연 건조하세요.')]
    if S.kind=='oil':
        return [('기름기 먼저 흡수','흰 천으로 눌러 유분을 흡수하세요.'),('중성세제 전처리','액체 세제를 바르고 살살 두드리세요.'),('라벨 온도대로 세탁','표시 온도에 맞춰 세탁하세요.')]
    return [('건더기·수분 흡수','흰 천으로 톡톡 눌러 흡수하세요.'),('중성세제 전처리','액체 세제를 발라 안쪽으로 두드리세요.'),('세탁 후 자연 건조','얼룩이 남으면 건조기를 쓰지 마세요.')]

st.markdown(f'<div class="brand"><div class="brand-left"><img src="{ICONS["logo"]}"/>STREM</div><span>STAIN CARE</span></div>',unsafe_allow_html=True)

if S.page=='start':
    st.markdown(f'''<div class="splash">
        <div class="splash-logo"><img src="{ICONS['logo']}"/></div>
        <div class="splash-badge">FAMILY STAIN CARE</div>
        <h1>STREM</h1>
        <p>우리 가족 옷 얼룩 해결사<br>성분에 맞는 화학 세탁 가이드</p>
    </div>''',unsafe_allow_html=True)
    if st.button('앱 시작하기',type='primary',use_container_width=True):go('find')

elif S.page=='find':
    with st.form('search',clear_on_submit=False):
        sc1,sc2=st.columns([3.6,1.3])
        with sc1:
            text=st.text_input('얼룩 검색',placeholder='커피, 김치, 볼펜…',label_visibility='collapsed')
        with sc2:
            submit=st.form_submit_button('찾기',use_container_width=True)
    if submit:
        found=match(text)
        if len(found)==1:start(found[0])
        elif found:S.candidates=found;go('candidate')
        else:go('identify')

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
    st.markdown('<h1>얼룩 촬영</h1>',unsafe_allow_html=True)
    photo=st.camera_input('촬영',label_visibility='collapsed')
    if photo:
        consent=st.checkbox('AI 추정을 위해 사진 전송에 동의합니다')
        if st.button('얼룩 확인하기',type='primary',use_container_width=True,disabled=not consent):
            if not secret('OPENAI_API_KEY'):
                go('identify')
            else:
                try:
                    from openai import OpenAI
                    im=ImageOps.exif_transpose(Image.open(photo)).convert('RGB');im.thumbnail((800,800));buf=io.BytesIO();im.save(buf,format='JPEG',quality=80)
                    client=OpenAI(api_key=secret('OPENAI_API_KEY'),timeout=25,max_retries=0)
                    response=client.chat.completions.create(model=secret('OPENAI_MODEL','gpt-4o-mini'),max_tokens=150,response_format={'type':'json_object'},messages=[{'role':'system','content':'Return JSON {"candidates":[...]} with 1-3 IDs from: blood, oil, drink, ink, unknown.'},{'role':'user','content':[{'type':'text','text':'의류 얼룩 후보를 골라주세요.'},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()}}]}])
                    raw=json.loads(response.choices[0].message.content).get('candidates',[])
                    S.candidates=list(dict.fromkeys(x for x in raw if isinstance(x,str) and x in LABEL))[:3] or ['unknown'];go('candidate')
                except Exception:
                    go('identify')
    bottom_dock()

elif S.page=='candidate':
    st.markdown('<h1>가장 가까운 얼룩은?</h1>',unsafe_allow_html=True)
    for kind in S.candidates:
        if st.button(LABEL[kind],key='cand_'+kind,use_container_width=True):start(kind)
    if st.button('잘 모르겠어요',use_container_width=True):go('identify')
    bottom_dock()

elif S.page=='identify':
    choices('어쩌다 묻었나요?',[('식사 · 음료','drink'),('요리 · 기름','oil'),('상처 · 출혈','blood'),('필기 · 화장품','ink'),('잘 모르겠어요','unknown')],'kind','material')
    bottom_dock()

elif S.page=='material':
    choices('어떤 소재인가요?',[('면 · 합성섬유','normal'),('울 · 실크 · 가죽','delicate'),('소재를 몰라요','unknown')],'material','wash')
    bottom_dock()

elif S.page=='wash':
    choices('물세탁 가능한가요?',[('물세탁 가능','yes'),('드라이 전용','no'),('라벨 안 봤어요','unknown')],'wash','age')
    bottom_dock()

elif S.page=='age':
    choices('언제 묻었나요?',[('방금 묻었어요','fresh'),('말라붙었어요','dry'),('이미 세탁했어요','washed')],'age','result')
    bottom_dock()

elif S.page=='result':
    tag=LABEL[S.kind]+' · '+{'fresh':'방금 묻음','dry':'말라붙음','washed':'세탁 후'}[S.age]
    steps_html=''.join(
        f'<div class="res-step"><span class="res-num">{i}</span><div class="res-body"><span class="res-title">{escape(t)}</span>{escape(b)}</div></div>'
        for i,(t,b) in enumerate(plan(),1)
    )
    st.markdown(f'''<div class="res-box">
        <div class="res-tag">{escape(tag)} 해결법</div>
        {steps_html}
        <div class="res-chem">화학 원리 · {escape(CHEM[S.kind])}</div>
        <div class="res-warn">세제 혼합 금지 · 의류 라벨 우선</div>
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
    st.markdown('<h1>QR · 전체</h1>',unsafe_allow_html=True)
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
