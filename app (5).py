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
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@700&family=Jua&display=swap');

:root{color-scheme:light}
html,body,.stApp{
  background:#ffffff;
  color:#182b49;
  overflow-x:hidden;
  font-family:'Jua',sans-serif!important;
}
body *, .stApp *, button, input, label, p, span, h1, h2, h3, div{
  font-family:'Jua',sans-serif!important;
}
header[data-testid="stHeader"],footer,[data-testid="stToolbar"]{display:none!important;height:0!important}
.block-container{
  max-width:480px!important;
  min-height:100dvh!important;
  padding:14px 16px 104px!important;
  margin:0 auto!important;
  display:flex!important;
  flex-direction:column!important;
  justify-content:space-between!important;
}
[data-testid="stVerticalBlock"]{gap:12px!important}
h1{font-size:30px!important;font-weight:400!important;letter-spacing:-0.4px;margin:2px 0 6px!important;color:#0f172a!important}
h2{font-size:23px!important;font-weight:400!important;margin:0!important}
p,label,[data-testid="stMarkdownContainer"] p{font-size:20px!important;line-height:1.4!important;margin:0!important}

/* Brand Header */
.brand{display:flex;justify-content:space-between;align-items:center;font-size:26px;color:#1769ef;padding:2px 2px 4px}
.brand span{font-size:13px;letter-spacing:1.4px;color:#64748b}

/* Start Splash Card — Fills Mobile Screen */
.splash{
  background:linear-gradient(155deg,#1769ef 0%,#0b4bb8 100%);
  color:white;
  min-height:66dvh;
  padding:38px 24px;
  border-radius:32px;
  text-align:center;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  box-shadow:0 16px 34px rgba(23,105,239,0.24);
  margin:4px 0 12px;
}
.splash-badge{display:inline-block;background:rgba(255,255,255,0.22);padding:7px 16px;border-radius:999px;font-size:15px;letter-spacing:1.2px;margin-bottom:18px}
.splash h1{color:white!important;font-size:52px!important;margin-bottom:12px!important}
.splash p{color:rgba(255,255,255,0.95)!important;font-size:22px!important;line-height:1.45!important}

/* Pill Search Bar */
div[data-testid="stForm"]{
  border:3px solid #1769ef!important;
  border-radius:999px!important;
  padding:6px 8px 6px 20px!important;
  background:#ffffff!important;
  box-shadow:0 8px 22px rgba(23,105,239,0.12)!important;
  margin-bottom:4px!important;
}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]{align-items:center!important;gap:6px!important;flex-wrap:nowrap!important}
div[data-testid="stForm"] [data-testid="stTextInput"]>div>div{border:none!important;background:transparent!important;box-shadow:none!important}
div[data-testid="stForm"] [data-testid="stTextInput"] input{font-size:21px!important;min-height:46px!important;padding:0!important;color:#0f172a!important}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button{
  border-radius:999px!important;
  min-height:46px!important;
  height:46px!important;
  padding:0 16px!important;
  background:#1769ef!important;
  color:#ffffff!important;
  border:none!important;
  font-size:20px!important;
}

/* Standard Choice Buttons */
.stButton button,.stLinkButton a,.stDownloadButton button{
  min-height:64px!important;
  border-radius:22px!important;
  font-size:22px!important;
  border:2px solid #dbe5f3!important;
  background:#f8fafc!important;
  color:#0f172a!important;
  padding:10px 14px!important;
}
.stButton button p{font-size:22px!important;line-height:1.25!important}
.stButton button[kind="primary"]{
  background:#1769ef!important;
  color:white!important;
  border:0!important;
  min-height:66px!important;
  font-size:24px!important;
  box-shadow:0 8px 20px rgba(23,105,239,0.26)!important;
}
.stButton button[kind="primary"] p{color:white!important;font-size:24px!important}

/* Big 2x2 Stain Tile Grid */
.stain-grid-marker + div [data-testid="stHorizontalBlock"],
.stain-grid-marker + div + div [data-testid="stHorizontalBlock"]{
  flex-wrap:nowrap!important;
  gap:12px!important;
}
.stain-grid-marker + div .stButton button,
.stain-grid-marker + div + div .stButton button{
  height:142px!important;
  min-height:142px!important;
  border-radius:28px!important;
  background:#f8fafc!important;
  border:2px solid #e2ecf7!important;
  box-shadow:0 6px 16px rgba(15,23,42,0.06)!important;
  padding:10px 6px!important;
  white-space:pre-line!important;
}
.stain-grid-marker + div .stButton button p,
.stain-grid-marker + div + div .stButton button p{
  font-size:25px!important;
  line-height:1.35!important;
  color:#0f172a!important;
}

/* Toss-style Rounded Bottom Sheet Navigation Bar (Dark, Icon + Label) */
div[class*="st-key-bottom_dock"]{
  position:fixed!important;
  left:50%!important;
  bottom:0!important;
  transform:translateX(-50%)!important;
  width:100%!important;
  max-width:480px!important;
  background:#17171c!important;
  border-top:1px solid #2c2c35!important;
  border-radius:26px 26px 0 0!important;
  padding:8px 10px 14px!important;
  box-shadow:0 -8px 28px rgba(0,0,0,0.22)!important;
  z-index:9999!important;
}
div[class*="st-key-bottom_dock"] [data-testid="stHorizontalBlock"]{
  flex-wrap:nowrap!important;
  gap:2px!important;
  align-items:center!important;
}
div[class*="st-key-bottom_dock"] .stButton button{
  height:58px!important;
  min-height:58px!important;
  background:transparent!important;
  border:none!important;
  box-shadow:none!important;
  border-radius:16px!important;
  padding:4px 2px!important;
  white-space:pre-line!important;
}
div[class*="st-key-bottom_dock"] .stButton button p{
  font-size:15px!important;
  line-height:1.25!important;
  color:#8b95a1!important;
}
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"]{
  background:transparent!important;
  box-shadow:none!important;
}
div[class*="st-key-bottom_dock"] .stButton button[kind="primary"] p{
  color:#ffffff!important;
  font-size:15.5px!important;
}

/* Single All-at-once Result Card */
.res-box{background:#f8fafc;border:2px solid #dbe5f3;border-radius:26px;padding:18px 18px;margin:4px 0}
.res-tag{display:inline-block;background:#1769ef;color:#ffffff;font-size:16px;padding:5px 14px;border-radius:999px;margin-bottom:12px}
.res-step{display:flex;align-items:flex-start;gap:12px;padding:10px 0;border-bottom:1.5px solid #e6eef8}
.res-step:last-of-type{border-bottom:none}
.res-num{background:#1769ef;color:white;font-size:17px;width:28px;height:28px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}
.res-body{font-size:20px;line-height:1.4;color:#1e293b}
.res-body b{color:#0f172a;font-size:21px;font-weight:400}
.res-chem{background:#eef4ff;border-radius:16px;padding:12px 14px;margin-top:10px;font-size:18px;color:#1e3a8a;line-height:1.35}
.res-warn{font-size:16px;color:#64748b;margin-top:8px;text-align:center}

[data-testid="stCameraInput"]{max-width:300px;margin:0 auto}
@media(max-width:640px){
  [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important}
  [data-testid="stColumn"]{min-width:0!important;flex:1!important}
}
</style>''',unsafe_allow_html=True)

S=st.session_state
for k,v in {'page':'start','history':[],'kind':'unknown','material':None,'wash':None,'age':None,'candidates':[]}.items():
    if k not in S:S[k]=v

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
        if d1.button('🏠\n홈',key='dock_home',use_container_width=True,type='primary' if S.page=='find' else 'secondary'):go('find')
        if d2.button('📷\n카메라',key='dock_cam',use_container_width=True,type='primary' if S.page=='camera' else 'secondary'):go('camera')
        if d3.button('❓\n얼룩찾기',key='dock_id',use_container_width=True,type='primary' if S.page in ['identify','material','wash','age','result'] else 'secondary'):go('identify')
        if d4.button('🕘\n기록',key='dock_hist',use_container_width=True,type='primary' if S.page=='history' else 'secondary'):go('history')
        if d5.button('☰\n전체·QR',key='dock_share',use_container_width=True,type='primary' if S.page=='share' else 'secondary'):go('share')

LABEL={'blood':'피·혈액','oil':'기름·유분','drink':'음료·소스','ink':'잉크·화장품','unknown':'종류 불명'}
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

st.markdown('<div class="brand">STREM<span>STAIN CARE</span></div>',unsafe_allow_html=True)

if S.page=='start':
    st.markdown('''<div class="splash">
        <div class="splash-badge">FAMILY STAIN CARE</div>
        <h1>STREM</h1>
        <p>우리 가족 옷 얼룩 해결사<br>성분에 맞는 화학 세탁 가이드</p>
    </div>''',unsafe_allow_html=True)
    if st.button('앱 시작하기',type='primary',use_container_width=True):go('find')

elif S.page=='find':
    with st.form('search',clear_on_submit=False):
        sc1,sc2=st.columns([3.7,1.2])
        with sc1:
            text=st.text_input('얼룩 검색',placeholder='커피, 김치, 볼펜…',label_visibility='collapsed')
        with sc2:
            submit=st.form_submit_button('🔍',use_container_width=True)
    if submit:
        found=match(text)
        if len(found)==1:start(found[0])
        elif found:S.candidates=found;go('candidate')
        else:go('identify')

    st.markdown('<div class="stain-grid-marker"></div>',unsafe_allow_html=True)
    r1=st.columns(2)
    if r1[0].button('☕\n음료 · 소스',use_container_width=True):start('drink')
    if r1[1].button('🍳\n기름 · 유분',use_container_width=True):start('oil')

    r2=st.columns(2)
    if r2[0].button('🩸\n피 · 혈액',use_container_width=True):start('blood')
    if r2[1].button('💄\n잉크 · 화장',use_container_width=True):start('ink')

    bottom_dock()

elif S.page=='camera':
    st.markdown('<h1>📷 얼룩 촬영</h1>',unsafe_allow_html=True)
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
    choices('어쩌다 묻었나요?',[('☕ 식사 · 음료','drink'),('🍳 요리 · 기름','oil'),('🩸 상처 · 출혈','blood'),('💄 필기 · 화장품','ink'),('❓ 잘 모르겠어요','unknown')],'kind','material')
    bottom_dock()

elif S.page=='material':
    choices('어떤 소재인가요?',[('👕 면 · 합성섬유','normal'),('🧣 울 · 실크 · 가죽','delicate'),('❓ 소재를 몰라요','unknown')],'material','wash')
    bottom_dock()

elif S.page=='wash':
    choices('물세탁 가능한가요?',[('⭕ 물세탁 가능','yes'),('🚫 드라이 전용','no'),('❓ 라벨 안 봤어요','unknown')],'wash','age')
    bottom_dock()

elif S.page=='age':
    choices('언제 묻었나요?',[('💧 방금 묻었어요','fresh'),('⏳ 말라붙었어요','dry'),('🧺 이미 세탁했어요','washed')],'age','result')
    bottom_dock()

elif S.page=='result':
    tag=LABEL[S.kind]+' · '+{'fresh':'방금 묻음','dry':'말라붙음','washed':'세탁 후'}[S.age]
    steps_html=''.join(
        f'<div class="res-step"><span class="res-num">{i}</span><div class="res-body"><b>{escape(t)}</b><br>{escape(b)}</div></div>'
        for i,(t,b) in enumerate(plan(),1)
    )
    st.markdown(f'''<div class="res-box">
        <div class="res-tag">{escape(tag)} 해결법</div>
        {steps_html}
        <div class="res-chem">🧪 {escape(CHEM[S.kind])}</div>
        <div class="res-warn">⚠️ 세제 혼합 금지 · 의류 라벨 우선</div>
    </div>''',unsafe_allow_html=True)
    bottom_dock()

elif S.page=='history':
    st.markdown('<h1>🕘 최근 기록</h1>',unsafe_allow_html=True)
    if S.history:
        items_html=''.join(
            f'<div class="res-step"><span class="res-num">{i}</span><div class="res-body"><b>{escape(x["name"])}</b> · {escape(x["time"])}</div></div>'
            for i,x in enumerate(S.history[:4],1)
        )
        st.markdown(f'<div class="res-box">{items_html}</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="res-box"><div class="res-body"><b>아직 기록이 없어요.</b></div></div>',unsafe_allow_html=True)
    bottom_dock()

elif S.page=='share':
    st.markdown('<h1>🔗 QR · 전체</h1>',unsafe_allow_html=True)
    url=st.text_input('앱 주소',value=secret('APP_URL','https://2611121313-d9pclpfwungek3wl2j9j2s.streamlit.app/'),label_visibility='collapsed')
    parsed=urlparse(url)
    if parsed.scheme=='https' and parsed.netloc:
        buf=io.BytesIO();qrcode.make(url).save(buf,format='PNG')
        c1,c2=st.columns([1,1.3])
        with c1:st.image(buf.getvalue(),width=130)
        with c2:
            st.download_button('📥 QR 저장',buf.getvalue(),'STREM_QR.png','image/png',use_container_width=True)
            if st.button('처음 화면으로',use_container_width=True):go('start')
    bottom_dock()
