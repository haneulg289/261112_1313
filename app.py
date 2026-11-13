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
:root{color-scheme:light}
html,body,.stApp{background:#ffffff;color:#182b49;overflow-x:hidden}
header[data-testid="stHeader"],footer,[data-testid="stToolbar"]{display:none!important;height:0!important}
.block-container{max-width:440px;padding:10px 14px 10px!important;margin:0 auto!important}
[data-testid="stVerticalBlock"]{gap:8px!important}
h1{font-size:24px!important;font-weight:800!important;letter-spacing:-0.8px;margin:0 0 2px!important}
h2{font-size:20px!important;margin:0!important}
p,label,[data-testid="stMarkdownContainer"] p{font-size:16px!important;line-height:1.35!important;margin:0!important}

/* Brand Header */
.brand{display:flex;justify-content:space-between;align-items:center;font-size:20px;font-weight:900;letter-spacing:-0.6px;color:#1769ef;padding:2px 2px 4px}
.brand span{font-size:11px;font-weight:700;letter-spacing:1.5px;color:#64748b}

/* Start Splash Card — Clean & Full Mobile Fit */
.splash{background:linear-gradient(155deg,#1769ef 0%,#0b4bb8 100%);color:white;padding:44px 22px;border-radius:26px;text-align:center;box-shadow:0 12px 28px rgba(23,105,239,0.22);margin:6px 0 10px}
.splash-badge{display:inline-block;background:rgba(255,255,255,0.18);padding:5px 12px;border-radius:999px;font-size:12px;font-weight:700;letter-spacing:1.4px;margin-bottom:14px}
.splash h1{color:white!important;font-size:40px!important;font-weight:900!important;margin-bottom:10px!important}
.splash p{color:rgba(255,255,255,0.92)!important;font-size:17px!important;line-height:1.45!important}

/* Naver-style Pill Search Bar */
div[data-testid="stForm"]{border:2.2px solid #1769ef!important;border-radius:999px!important;padding:2px 6px 2px 16px!important;background:#ffffff!important;box-shadow:0 4px 14px rgba(23,105,239,0.09)!important;margin-bottom:2px!important}
div[data-testid="stForm"] [data-testid="stHorizontalBlock"]{align-items:center!important;gap:4px!important;flex-wrap:nowrap!important}
div[data-testid="stForm"] [data-testid="stTextInput"]>div>div{border:none!important;background:transparent!important;box-shadow:none!important}
div[data-testid="stForm"] [data-testid="stTextInput"] input{font-size:16px!important;min-height:38px!important;padding:0!important;color:#182b49!important}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button{border-radius:999px!important;min-height:36px!important;height:36px!important;padding:0 14px!important;background:#eef4ff!important;color:#1769ef!important;border:none!important;font-weight:800!important;font-size:15px!important}

/* Standard Buttons */
.stButton button,.stLinkButton a,.stDownloadButton button{min-height:48px!important;border-radius:16px!important;font-size:17px!important;font-weight:700!important;border:1px solid #e2e8f0!important;background:#f8fafc!important;color:#182b49!important;padding:6px 12px!important}
.stButton button[kind="primary"]{background:#1769ef!important;color:white!important;border:0!important;box-shadow:0 6px 16px rgba(23,105,239,0.22)!important}

/* 2x4 Icon Tile Grid on Find Screen */
.icon-grid-marker + div [data-testid="stHorizontalBlock"],
.icon-grid-marker + div + div [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:6px!important}
.icon-grid-marker + div .stButton button,
.icon-grid-marker + div + div .stButton button{height:72px!important;min-height:72px!important;border-radius:18px!important;background:#ffffff!important;border:1px solid #e6edf5!important;box-shadow:0 3px 10px rgba(15,23,42,0.05)!important;padding:4px 2px!important;white-space:pre-line!important;line-height:1.2!important;font-size:14px!important;font-weight:700!important;color:#1e293b!important}
.icon-grid-marker + div .stButton button p,
.icon-grid-marker + div + div .stButton button p{font-size:13.5px!important;line-height:1.2!important}

/* Single All-at-once Result Card */
.res-box{background:#f8fafc;border:1px solid #dbe5f3;border-radius:20px;padding:14px 16px;margin:2px 0}
.res-tag{display:inline-block;background:#eef4ff;color:#1769ef;font-size:12px;font-weight:800;padding:3px 10px;border-radius:999px;margin-bottom:8px}
.res-step{display:flex;align-items:flex-start;gap:10px;padding:7px 0;border-bottom:1px solid #e8eef7}
.res-step:last-of-type{border-bottom:none}
.res-num{background:#1769ef;color:white;font-size:12px;font-weight:800;width:22px;height:22px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.res-body{font-size:15px;line-height:1.35;color:#1e293b}
.res-body b{color:#0f172a;font-weight:800}
.res-chem{background:#eef4ff;border-radius:12px;padding:8px 11px;margin-top:8px;font-size:13.5px;color:#1e3a8a;font-weight:600;line-height:1.3}
.res-warn{font-size:12.5px;color:#64748b;margin-top:6px;text-align:center}

[data-testid="stCameraInput"]{max-width:270px;margin:0 auto}
@media(max-width:640px){
  [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:6px!important}
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

LABEL={'blood':'피·혈액','oil':'기름·유분','drink':'음료·소스','ink':'잉크·화장품','unknown':'종류 불명'}
ALIASES={'blood':['혈액','피','코피','생리혈'],'oil':['기름','식용유','버터','참기름','올리브유','라면','삼겹살','치킨','마요네즈'],'drink':['김치','커피','라떼','주스','와인','콜라','떡볶이','소스','차','초콜릿','우유','음료','간장','케첩','카레'],'ink':['잉크','볼펜','립스틱','파운데이션','매직','화장품','틴트','사인펜','크레파스']}
CHEM={'blood':'혈액 단백질은 뜨거운 물에 응고되므로 반드시 찬물을 써야 해요.','oil':'친유성 기름 성분은 계면활성제로 유화시켜 물에 씻어내요.','drink':'색소·당분·유분이 섞인 복합 얼룩은 수분 흡수 후 중성세제로 분해해요.','ink':'안료·유분 복합 성분은 임의 용제 사용 시 번질 수 있어 주의해야 해요.','unknown':'성분 미상 얼룩은 화학 반응이나 열 고정 전에 세탁 표시부터 확인해요.'}

def match(text):
    text=text.strip().lower().replace(' ','')
    if not text:return []
    exact=[k for k,words in ALIASES.items() if text in words]
    if exact:return exact
    return list(dict.fromkeys(k for k,words in ALIASES.items() if any(len(w)>1 and w in text for w in words)))

def plan():
    if S.wash!='yes' or S.material!='normal':
        return [('세탁 표시 확인','물·세제를 바르지 말고 세탁 라벨을 먼저 확인하세요.'),('전문 세탁 문의','울·실크 또는 물세탁 불가 의류는 얼룩 원인을 알리고 세탁소에 맡기세요.'),('열·마찰 금지','문지르거나 드라이기·다리미 열을 가하지 마세요.')]
    if S.kind in ['unknown','ink']:
        return [('문지르지 않기','휴지나 물티슈로 문지르면 섬유 깊숙이 번집니다.'),('용제 임의 사용 금지','식초·알코올·표백제를 임의로 쓰지 말고 세탁소에 문의하세요.'),('건조기 사용 금지','열이 가해지면 얼룩이 고착되니 자연 상태를 유지하세요.')]
    if S.kind=='blood':
        return [('찬물로 뒷면 헹구기','얼룩 뒷면에서 찬물을 흘려보내세요. 온수는 단백질을 굳힙니다.'),('액체 세제 전처리','안쪽에 색 번짐 테스트 후 중성 액체 세제를 발라 가볍게 두드리세요.'),('찬물 세탁·자연 건조','얼룩이 빠진 것을 확인한 뒤 세탁하고 건조기 열은 피하세요.')]
    if S.kind=='oil':
        return [('기름기 먼저 흡수','흰 천이나 키친타월로 톡톡 눌러 유분을 흡수하세요.'),('중성세제 전처리','액체 세제를 얼룩에 소량 바르고 손끝으로 살살 두드리세요.'),('표시 온도대로 세탁','세탁 라벨 온도에 맞춰 세탁하고 다림질 전 제거 여부를 확인하세요.')]
    return [('건더기·수분 제거','고형물은 걷어내고 액체는 흰 천으로 눌러 흡수하세요.'),('중성세제 전처리','안쪽 테스트 후 액체 세제를 발라 바깥에서 안쪽으로 두드리세요.'),('세탁 후 자연 건조','세탁 라벨대로 세탁하고 얼룩이 남으면 건조기 사용을 피하세요.')]

st.markdown('<div class="brand">STREM<span>STAIN CARE</span></div>',unsafe_allow_html=True)

if S.page=='start':
    st.markdown('''<div class="splash">
        <div class="splash-badge">FAMILY STAIN HELPER</div>
        <h1>STREM</h1>
        <p>우리 가족 옷 얼룩 해결사<br>성분에 맞는 안전한 세탁 가이드</p>
    </div>''',unsafe_allow_html=True)
    if st.button('앱 시작하기',type='primary',use_container_width=True):go('find')

elif S.page=='find':
    with st.form('search',clear_on_submit=False):
        sc1,sc2=st.columns([3.8,1.3])
        with sc1:
            text=st.text_input('얼룩 검색',placeholder='얼룩 이름을 입력해 주세요.',label_visibility='collapsed')
        with sc2:
            submit=st.form_submit_button('✦ 찾기',use_container_width=True)
    if submit:
        found=match(text)
        if len(found)==1:start(found[0])
        elif found:S.candidates=found;go('candidate')
        else:go('identify')

    st.markdown('<div class="icon-grid-marker"></div>',unsafe_allow_html=True)
    r1=st.columns(4)
    if r1[0].button('☕\n음료·커피',use_container_width=True):start('drink')
    if r1[1].button('🌶️\n김치·소스',use_container_width=True):start('drink')
    if r1[2].button('🍳\n기름·유분',use_container_width=True):start('oil')
    if r1[3].button('🩸\n피·혈액',use_container_width=True):start('blood')

    r2=st.columns(4)
    if r2[0].button('💄\n잉크·화장',use_container_width=True):start('ink')
    if r2[1].button('📷\n카메라 찾기',use_container_width=True):go('camera')
    if r2[2].button('❓\n모르겠어요',use_container_width=True):go('identify')
    if r2[3].button('🔗\nQR·기록',use_container_width=True):go('share')

    if st.button('처음 화면으로',use_container_width=True):go('start')

elif S.page=='camera':
    st.markdown('<h1>📷 카메라로 얼룩 찾기</h1>',unsafe_allow_html=True)
    photo=st.camera_input('촬영',label_visibility='collapsed')
    if photo:
        consent=st.checkbox('AI 얼룩 추정을 위해 사진 전송에 동의합니다')
        if st.button('얼룩 추정하기',type='primary',use_container_width=True,disabled=not consent):
            if not secret('OPENAI_API_KEY'):
                st.warning('AI 키가 없어 질문 선택 화면으로 이동할게요.')
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
                    st.error('추정에 실패했어요. 질문으로 찾기 버튼을 눌러주세요.')
    c1,c2=st.columns(2)
    if c1.button('질문으로 찾기',use_container_width=True):go('identify')
    if c2.button('뒤로가기',use_container_width=True):go('find')

elif S.page=='candidate':
    st.markdown('<h1>어떤 얼룩과 가장 비슷한가요?</h1>',unsafe_allow_html=True)
    for kind in S.candidates:
        if st.button(LABEL[kind],key='cand_'+kind,use_container_width=True):start(kind)
    if st.button('잘 모르겠어요',use_container_width=True):go('identify')

elif S.page=='identify':
    choices('어쩌다 묻었나요?',[('식사·음료 마시다','drink'),('요리·기름 작업 중','oil'),('상처·출혈','blood'),('필기·화장품','ink'),('전혀 모르겠어요','unknown')],'kind','material')
    if st.button('뒤로가기',use_container_width=True):go('find')

elif S.page=='material':
    choices('어떤 옷인가요?',[('일반 면·합성섬유','normal'),('울·실크·가죽·기능성','delicate'),('소재를 잘 몰라요','unknown')],'material','wash')

elif S.page=='wash':
    choices('물세탁 가능한 옷인가요?',[('네, 물세탁 가능해요','yes'),('아니요, 드라이클리닝 전용','no'),('세탁 표시를 안 봤어요','unknown')],'wash','age')

elif S.page=='age':
    choices('얼룩이 언제 묻었나요?',[('방금 묻었어요','fresh'),('시간이 지나 말랐어요','dry'),('이미 세탁·건조했어요','washed')],'age','result')

elif S.page=='result':
    tag=LABEL[S.kind]+' · '+{'fresh':'방금 묻음','dry':'말라붙음','washed':'세탁 후'}[S.age]
    steps_html=''.join(
        f'<div class="res-step"><span class="res-num">{i}</span><div class="res-body"><b>{escape(t)}</b> · {escape(b)}</div></div>'
        for i,(t,b) in enumerate(plan(),1)
    )
    st.markdown(f'''<div class="res-box">
        <div class="res-tag">{escape(tag)} 맞춤 해결법</div>
        {steps_html}
        <div class="res-chem">🧪 <b>화학 원리:</b> {escape(CHEM[S.kind])}</div>
        <div class="res-warn">⚠️ 세제 혼합 금지 · 변색 시 즉시 중단 · 의류 라벨 우선</div>
    </div>''',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    if c1.button('다른 얼룩 찾기',type='primary',use_container_width=True):go('find')
    if c2.button('처음으로',use_container_width=True):go('start')

elif S.page=='share':
    st.markdown('<h1>🔗 QR 공유 · 최근 기록</h1>',unsafe_allow_html=True)
    url=st.text_input('앱 주소',value=secret('APP_URL','https://2611121313-d9pclpfwungek3wl2j9j2s.streamlit.app/'),label_visibility='collapsed')
    parsed=urlparse(url)
    if parsed.scheme=='https' and parsed.netloc:
        buf=io.BytesIO();qrcode.make(url).save(buf,format='PNG')
        c1,c2=st.columns([1,1.5])
        with c1:st.image(buf.getvalue(),width=115)
        with c2:
            st.caption('최근 확인 기록: '+(' / '.join(x['name'] for x in S.history[:3]) if S.history else '없음'))
            st.download_button('QR 이미지 저장',buf.getvalue(),'STREM_QR.png','image/png',use_container_width=True)
    if st.button('찾기 화면으로 돌아가기',type='primary',use_container_width=True):go('find')
