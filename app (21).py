"""LIkeFit — 가족 자세 습관 코치.
배포: GitHub 저장소 루트에 app.py / requirements.txt 업로드 → Streamlit
Community Cloud에서 저장소와 app.py 선택 → Advanced settings Python 3.11 선택.
실행: streamlit run app.py
QR 탭에 배포된 https://...streamlit.app 주소를 입력하세요. QR은 설치가 아닌 웹 접속입니다.
저장: 가족/기록은 현재 세션에만 저장됩니다. JSON 백업/복원 지원, 로그인/서버 DB 없음.
사진은 서버 메모리에서 분석하며 앱 코드에서 파일·DB로 저장하지 않습니다.
운영 서비스에는 별도 개인정보 고지, 접근 제어, 보관 정책 검토가 필요합니다.
"""
import io
import json
import math
import time
import uuid
from datetime import datetime
from urllib.parse import urlparse

import numpy as np
try:
    import qrcode
except ImportError:
    qrcode = None
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps, ImageDraw

st.set_page_config(page_title='LIkeFit | 가족 자세 습관 코치', page_icon='💙', layout='wide')
st.markdown('''<style>
.stApp{background:#f3f7fd;color:#163353} .block-container{max-width:1160px;padding-top:2rem}
h1,h2,h3{color:#103b70;letter-spacing:-.04em} .eyebrow{color:#2376ec;font-weight:800;letter-spacing:.18em;font-size:12px}
.hero{padding:38px;border-radius:28px;background:#103b70;color:white;margin:12px 0 24px;position:relative;overflow:hidden}
.hero h1{color:white;font-size:clamp(36px,6vw,68px);line-height:1.08;margin:15px 0}.hero p{color:#d4e8ff;max-width:620px;font-size:17px}
.hero .eyebrow{color:#8dc6ff}.pill{display:inline-block;padding:6px 12px;border:1px solid #5895d3;border-radius:30px;font-size:12px;color:#cce4ff}
.note{background:#e4efff;border-left:4px solid #287bea;padding:16px 20px;border-radius:0 16px 16px 0;margin:12px 0;color:#234d7b}
[data-testid="stMetric"]{background:white;border:1px solid #dfebfb;padding:18px;border-radius:18px}
.stButton>button[kind="primary"]{background:#1c70e8;border:0;border-radius:12px;min-height:46px}
[data-testid="stSidebar"]{background:#e8f0fc} div[data-testid="stTabs"] button{font-weight:700}
footer{visibility:hidden} @media(max-width:640px){.hero{padding:24px}.block-container{padding-top:1rem}}
</style>''', unsafe_allow_html=True)

for key, default in {'started':False,'people':['나'],'records':[], 'timer_end':0.0}.items():
    if key not in st.session_state:
        st.session_state[key] = default

DISCLAIMER = 'LIkeFit은 자세 습관 참고 도구이며 의료기기가 아닙니다. 거북목·척추측만증의 진단, 치료 또는 교정 효과를 판정하지 않습니다.'


def skeleton(mode='중립 자세', height=410):
    """Real rotatable 3D illustration, not inferred anatomy or medical simulation."""
    pts = np.array([[0,0,1.85],[0,0,1.55],[-.30,0,1.48],[.30,0,1.48],
                    [-.43,0,1.12],[.43,0,1.12],[-.46,0,.84],[.46,0,.84],
                    [0,0,1.04],[-.20,0,.98],[.20,0,.98],[-.20,0,.52],[.20,0,.52],
                    [-.20,.03,.06],[.20,.03,.06]], dtype=float)
    if mode == '고개 앞으로':
        pts[0,1] = .36
        pts[1,1] = .16
    elif mode == '한쪽으로 기울기':
        pts[:9,0] += np.linspace(.24,.08,9)
        pts[2,2] += .10
        pts[3,2] -= .10
    elif mode == '다리 꼬기':
        pts[11] = [.15,.25,.57]
        pts[13] = [.37,.18,.15]
    edges=[(0,1),(1,2),(1,3),(2,4),(4,6),(3,5),(5,7),(1,8),(8,9),(8,10),(9,11),(10,12),(11,13),(12,14)]
    # Browser canvas projects the 3D coordinates; no Plotly or external script needed.
    page = """<style>body{margin:0;background:#edf5ff;font-family:sans-serif}canvas{width:100%;touch-action:none;display:block;border-radius:24px}p{text-align:center;color:#326197;font-size:13px}</style>
    <canvas id="body" aria-label="회전 가능한 교육용 3D 자세 모형"></canvas><p>손가락이나 마우스로 좌우로 드래그하여 회전하세요</p>
    <script>
    const pts=POINTS,edges=EDGES,c=document.getElementById('body'),ctx=c.getContext('2d');
    let angle=.45,last=null;
    function draw(){const w=Math.max(240,c.clientWidth),h=HEIGHT-45,dpr=window.devicePixelRatio||1;
      c.width=w*dpr;c.height=h*dpr;c.style.height=h+'px';ctx.scale(dpr,dpr);
      const scale=Math.min(w/2.5,h/2.4);
      const pp=pts.map(p=>{const x=p[0]*Math.cos(angle)+p[1]*Math.sin(angle),y=-p[0]*Math.sin(angle)+p[1]*Math.cos(angle);
      const perspective=4/(4+y);return [w/2+x*scale*perspective,h/2-(p[2]-1)*scale*perspective,perspective];});
      ctx.fillStyle='#d7e7fc';ctx.beginPath();ctx.ellipse(w/2,h-18,scale*.7,12,0,0,Math.PI*2);ctx.fill();
      ctx.lineCap='round';for(const [a,b] of edges){ctx.strokeStyle='#247bea';ctx.lineWidth=14;ctx.beginPath();ctx.moveTo(pp[a][0],pp[a][1]);ctx.lineTo(pp[b][0],pp[b][1]);ctx.stroke();}
      pp.forEach((p,i)=>{const r=(i===0?21:7)*p[2],g=ctx.createRadialGradient(p[0]-r/3,p[1]-r/3,1,p[0],p[1],r);g.addColorStop(0,'#d5f2ff');g.addColorStop(1,'#3b93f3');ctx.fillStyle=g;ctx.beginPath();ctx.arc(p[0],p[1],r,0,Math.PI*2);ctx.fill();});
    }
    c.addEventListener('pointerdown',e=>{last=e.clientX;c.setPointerCapture(e.pointerId)});
    c.addEventListener('pointermove',e=>{if(last!==null){angle+=(e.clientX-last)*.012;last=e.clientX;draw()}});
    c.addEventListener('pointerup',()=>last=null);c.addEventListener('pointercancel',()=>last=null);
    window.addEventListener('resize',draw);draw();</script>"""
    components.html(page.replace('POINTS',json.dumps(pts.tolist())).replace('EDGES',json.dumps(edges)).replace('HEIGHT',str(height)),height=height)


def save_record(person, kind, details):
    st.session_state.records.append({'id':str(uuid.uuid4()), 'person':person,
        'time':datetime.now().astimezone().isoformat(timespec='seconds'), 'kind':kind,'details':details})


def tilt(a,b):
    d=np.asarray(b)-np.asarray(a)
    return round(math.degrees(math.atan2(abs(d[1]),max(abs(d[0]),1e-9))),1)


def analyze_photo(data, view, side):
    # Lazy import: self check and routines still work if vision cannot initialize.
    import mediapipe as mp
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
    if im.width*im.height>30_000_000:
        raise ValueError('사진 해상도가 너무 큽니다. 휴대폰에서 크기를 줄여 다시 올려주세요.')
    im.thumbnail((1600,1600))
    arr=np.asarray(im)
    with mp.solutions.pose.Pose(static_image_mode=True, model_complexity=1,
                               min_detection_confidence=.6,enable_segmentation=False) as pose:
        result=pose.process(arr)
    if not result.pose_landmarks:
        return im, None, '사람의 관절을 찾지 못했습니다. 전신이 보이는 밝은 사진으로 다시 촬영하세요.'
    lm=result.pose_landmarks.landmark
    indices=[11,12,23,24] if view=='정면' else ([7,11,23] if side=='왼쪽' else [8,12,24])
    if any(lm[i].visibility<.65 or not(0<=lm[i].x<=1 and 0<=lm[i].y<=1) for i in indices):
        return im,None,'필요한 귀·어깨·골반 관절이 가려졌거나 프레임 밖에 있습니다. 촬영 안내에 맞춰 다시 촬영하세요.'
    xy=lambda i:(lm[i].x*im.width,lm[i].y*im.height)
    draw=ImageDraw.Draw(im)
    for a,b in mp.solutions.pose.POSE_CONNECTIONS:
        if lm[a].visibility>.65 and lm[b].visibility>.65:
            draw.line([xy(a),xy(b)],fill='#2586ff',width=max(2,im.width//300))
    for i in indices:
        x,y=xy(i); r=max(4,im.width//180)
        draw.ellipse((x-r,y-r,x+r,y+r),fill='#72edff',outline='#164c89',width=2)
    if view=='정면':
        metrics={'화면상 어깨선 기울기 (°)':tilt(xy(11),xy(12)), '화면상 골반선 기울기 (°)':tilt(xy(23),xy(24))}
        note='카메라 기울기·옷·회전에 따라 달라지는 2D 관찰값입니다. 좌우 차이는 척추측만증 판정 근거가 아닙니다.'
    else:
        ear, shoulder=(7,11) if side=='왼쪽' else (8,12)
        a,b=xy(shoulder),xy(ear)
        metrics={'화면상 귀–어깨선 각도 (°)':tilt(a,b)}
        note='사진의 수평선과 귀–어깨선 사이 각도입니다. 경추각(CVA)이 아니며 거북목 진단·정상 기준과 비교하지 않습니다.'
    return im,metrics,note


with st.sidebar:
    st.markdown('## LIkeFit 💙')
    st.caption('작은 자세 습관, 함께 쌓는 변화')
    person=st.selectbox('현재 가족 프로필',st.session_state.people)
    with st.expander('가족 추가'):
        name=st.text_input('이름 대신 별명을 권장합니다',max_chars=20)
        if st.button('프로필 추가'):
            name=name.strip()
            if name and name not in st.session_state.people and len(st.session_state.people)<12:
                st.session_state.people.append(name); st.rerun()
            else: st.warning('중복되지 않는 별명을 입력하세요. 최대 12명까지 가능합니다.')
    st.info('기록은 이 브라우저의 현재 세션에만 남습니다. 종료 전 기록 탭에서 백업하세요. 다른 휴대폰과 자동 공유되지 않습니다.')
    st.caption(DISCLAIMER)

if not st.session_state.started:
    st.markdown('''<section class="hero"><span class="pill">FAMILY POSTURE COMPANION</span>
    <h1>바른 자세보다 먼저,<br>나를 알아가는 시간.</h1><p>우리 가족의 일상에 가볍게 스며드는 자세 습관 코치, LIkeFit.</p>
    <div class="eyebrow">CHECK · MOVE · TOGETHER</div></section>''',unsafe_allow_html=True)
    a,b=st.columns([1,1])
    with a:
        st.subheader('사진 한 장, 오늘의 습관 체크')
        st.write('관절 위치를 확인하고, 나에게 맞는 짧은 움직임을 선택하세요. 복잡한 장비 없이 휴대폰으로 시작할 수 있어요.')
        st.markdown('**01** 사진 또는 자가 체크  →  **02** 습관 가이드  →  **03** 짧은 루틴')
        if st.button('LIkeFit 시작하기 →',type='primary',use_container_width=True):
            st.session_state.started=True; st.rerun()
        st.caption('사진 촬영은 선택입니다. 사진 없이도 모든 생활 습관 루틴을 이용할 수 있습니다.')
    with b: skeleton()
    st.warning(DISCLAIMER)
    st.stop()

st.markdown('<div class="eyebrow">YOUR EVERYDAY ALIGNMENT</div>',unsafe_allow_html=True)
st.title('오늘도, 가볍게 LIkeFit')
my=[r for r in st.session_state.records if r['person']==person]
a,b,c=st.columns(3)
a.metric('현재 프로필',person)
b.metric('완료한 루틴',sum(r['kind']=='루틴' for r in my))
c.metric('체크 기록',sum(r['kind'] in ['사진 관찰','자가 체크'] for r in my))
tabs=st.tabs(['📷 사진 체크','☑️ 자가 체크','🧍 3D 가이드','⏱️ 데일리 루틴','💙 가족 기록','🔗 QR · 사용 안내'])

with tabs[0]:
    st.subheader('내 자세를 눈으로 확인하기')
    st.caption('실시간·백그라운드 감시가 아닌, 사용자가 촬영한 한 장의 사진 분석입니다. 한 장으로 평소 자세를 알 수는 없습니다.')
    with st.expander('좋은 촬영 방법 · 개인정보',expanded=True):
        st.write('• 다른 사람이 없는 밝은 곳에서 몸에 붙는 옷을 입고 촬영하세요.\n• 카메라를 수평으로 고정하고 머리·어깨·골반이 모두 보이도록 2–3m 떨어지세요.\n• 정면은 몸을 비틀지 말고, 옆면은 선택한 쪽 귀와 어깨가 카메라를 향하게 하세요.\n• 아이 사진은 보호자 동의 아래 사용하세요. 사진은 서버로 전송되어 메모리에서 처리됩니다.\n• 분석용 사진은 앱 코드에서 디스크·DB에 저장하지 않지만, 실행 중 화면/세션 메모리에 남을 수 있습니다.')
    consent=st.checkbox('촬영 대상의 동의를 받았고 사진 처리 안내를 확인했습니다.')
    view=st.radio('촬영 방향',['정면','옆면'],horizontal=True)
    side=st.radio('카메라에 보이는 쪽',['왼쪽','오른쪽'],horizontal=True,disabled=view=='정면')
    source=st.radio('사진 입력',['파일 업로드','카메라 촬영'],horizontal=True)
    image=st.file_uploader('JPG / PNG · 최대 10MB',type=['jpg','jpeg','png']) if source=='파일 업로드' else st.camera_input('자세 사진 촬영')
    st.caption('카메라는 HTTPS와 브라우저 권한이 필요합니다. 혼자 촬영하기 어렵다면 휴대폰 기본 카메라의 타이머로 촬영 후 업로드하세요.')
    if st.button('관절 위치 분석',type='primary',disabled=not(consent and image is not None)):
        if image.size>10*1024*1024:
            st.error('10MB 이하 사진을 사용하세요.')
        else:
            try:
                with st.spinner('사진에서 관절 위치를 찾고 있어요…'):
                    overlay,metrics,note=analyze_photo(image.getvalue(),view,side)
                st.session_state['analysis']={'image':overlay,'metrics':metrics,'note':note,'person':person,'token':str(uuid.uuid4())}
            except Exception as e:
                st.error('사진 분석을 실행하지 못했습니다. 배포 Python 3.11과 의존성 설치를 확인하거나 다른 사진을 사용하세요. 자가 체크는 계속 사용할 수 있습니다.')
                with st.expander('오류 상세'): st.code(str(e)[:700])
    res=st.session_state.get('analysis')
    if res and res['person']==person:
        left,right=st.columns([1.2,1])
        with left: st.image(res['image'],caption='최근 분석 사진 · 관절 추정 오버레이',use_container_width=True)
        with right:
            st.info(res['note'])
            if res['metrics']:
                for label,val in res['metrics'].items(): st.metric(label,val)
                st.write('점이 실제 관절과 다르면 이 값을 사용하지 말고 재촬영하세요. 수치의 증감이 건강 개선을 의미하지는 않습니다.')
                if st.button('관찰값만 기록',key='savephoto',disabled=res.get('saved',False)):
                    save_record(person,'사진 관찰',res['metrics']);res['saved']=True;st.success('사진 없이 관찰값만 기록했습니다.')
            else: st.warning('분석 불가: 자가 체크를 이용하거나 다시 촬영하세요.')
        if st.button('분석 사진 지우기'):
            del st.session_state['analysis'];st.rerun()

with tabs[1]:
    st.subheader('지금의 몸과 생활 습관을 확인해요')
    st.caption('질병 위험 점수가 아닌, 본인이 체크한 습관에 따른 안내입니다.')
    with st.form('self_check'):
        neck=st.checkbox('화면을 볼 때 고개가 앞으로 나오는 편이에요')
        uneven=st.checkbox('앉을 때 한쪽으로 기대거나 좌우가 다르게 느껴져요')
        legs=st.checkbox('다리를 자주 꼬고 오래 앉아 있어요')
        sitting=st.select_slider('한 번에 앉아 있는 시간',options=['30분 미만','30–60분','1–2시간','2시간 이상'])
        pain=st.checkbox('현재 통증·저림 또는 최근 부상이 있어요')
        submitted=st.form_submit_button('맞춤 습관 가이드 보기',type='primary')
    if submitted:
        details={'고개 앞으로':neck,'한쪽 기대기':uneven,'다리 꼬기':legs,'앉는 시간':sitting,'증상 있음':pain}
        save_record(person,'자가 체크',details)
        st.session_state['self_result']={'person':person,'details':details}
    check=st.session_state.get('self_result')
    if check and check['person']==person:
        d=check['details']
        if d['증상 있음']:
            st.warning('통증·저림·최근 부상이 있으면 운동을 시작하기 전 의료진과 상담하세요. 증상이 생기는 동작은 중단하세요.')
        if d['고개 앞으로']: st.info('화면 높이를 편한 시선에 맞추고 팔을 지지하세요. 목을 억지로 뒤로 꺾지 마세요.')
        if d['한쪽 기대기']: st.info('발을 바닥에 지지하고 한쪽 팔걸이에 오래 기대지 않도록 자세를 바꿔보세요. 지속되는 비대칭은 의료진 평가를 권합니다.')
        if d['다리 꼬기']: st.info('두 발이 편히 닿도록 의자 높이를 조절하고, 다리를 꼬고 있음을 알아차리면 풀어주세요.')
        st.success('완벽한 자세를 고정하기보다, 편안한 범위에서 자주 자세를 바꾸는 습관을 만들어보세요.')

with tabs[2]:
    st.subheader('돌려보면서 이해하는 자세 가이드')
    mode=st.selectbox('비교할 생활 자세',['중립 자세','고개 앞으로','한쪽으로 기울기','다리 꼬기'])
    l,r=st.columns([1.3,1])
    with l: skeleton(mode)
    with r:
        st.markdown('### 몸을 고정하지 말고,\n### 편안하게 바꿔주세요.')
        st.write({'중립 자세':'귀·어깨·골반이 편안히 놓이게 하고, 발은 바닥이나 발 받침에 지지하세요.',
                  '고개 앞으로':'작은 화면을 보려고 목을 내밀기보다 화면을 가까이 가져오거나 글자 크기를 키워보세요.',
                  '한쪽으로 기울기':'몸을 한쪽으로 기대는 시간이 길어지지 않도록 자리와 팔 지지를 조절해보세요.',
                  '다리 꼬기':'두 발을 편히 지지하고, 오래 앉아 있었다면 잠깐 일어나 움직여보세요.'}[mode])
        st.caption('좌우 드래그: 회전. 교육용 단순 3D 모형이며 사진 속 사용자 신체를 재구성한 것이 아닙니다. 한쪽 기울기 그림은 척추측만증을 표현하지 않습니다.')

with tabs[3]:
    st.subheader('짧게 움직이고, 다시 일상으로')
    st.warning('통증·저림·어지럼이 있으면 즉시 중단하세요. 강한 목 돌리기, 강제로 누르기, 척추를 비트는 교정 동작은 제공하지 않습니다.')
    routines={'화면 휴식 · 60초':(60,['화면에서 시선을 떼고 먼 곳을 편안히 바라보세요.','어깨의 힘을 풀고 천천히 호흡하세요.','화면 높이와 팔 지지를 다시 확인하세요.']),
              '어깨 힘 빼기 · 60초':(60,['허리를 억지로 세우지 말고 편하게 앉으세요.','통증 없는 범위에서 어깨를 살짝 올렸다가 내려놓으세요.','목을 꺾지 말고 자연스럽게 호흡하세요.']),
              '앉기 리셋 · 90초':(90,['다리를 풀고 양발을 바닥에 편히 놓으세요.','안전하다면 천천히 일어나 잠깐 걸으세요.','앉은 뒤 등을 편히 지지하고 작업을 재개하세요.'])}
    routine=st.selectbox('오늘의 루틴',list(routines),disabled=bool(st.session_state.get('active_routine')))
    seconds,steps=routines[routine]
    for i,step in enumerate(steps,1): st.write(f'{i}. {step}')
    safe=st.checkbox('지금 통증·저림·어지럼이 없으며 안전하게 움직일 수 있어요.')
    a,b=st.columns(2)
    if a.button('타이머 시작',type='primary',disabled=not safe or bool(st.session_state.get('active_routine'))):
        st.session_state.timer_end=time.time()+seconds
        st.session_state.active_routine={'person':person,'name':routine,'seconds':seconds}
        st.rerun()
    if b.button('중단 / 초기화'):
        st.session_state.timer_end=0
        st.session_state.pop('active_routine',None);st.rerun()

    @st.fragment(run_every=1)
    def timer():
        active=st.session_state.get('active_routine')
        if not active: return
        remaining=max(0,math.ceil(st.session_state.timer_end-time.time()))
        st.metric(f"{active['person']} · {active['name']}",f'{remaining//60:02d}:{remaining%60:02d}')
        st.progress(min(1.,max(0.,1-remaining/active['seconds'])))
        if remaining==0:
            st.success('시간이 끝났어요. 실제로 루틴을 수행했다면 완료를 눌러주세요.')
            if st.button('완료 기록하기',key='finish'):
                save_record(active['person'],'루틴',{'이름':active['name'],'초':active['seconds']})
                st.session_state.pop('active_routine',None);st.session_state.timer_end=0;st.rerun()
    timer()
    st.markdown('#### 작업 중 쉬는 시간 알림')
    minutes=st.slider('페이지가 열려 있는 동안 알림 간격(분)',10,60,30,step=5)
    if st.checkbox('이 페이지에서 휴식 알림 켜기'):
        components.html('''<div style="font-family:sans-serif;color:#2862a1;padding:12px;background:#e6efff;border-radius:12px">
        <b id="label">휴식 알림 작동 중</b><div id="clock"></div></div><script>
        const gap=MINUTES*60; let next=Date.now()+gap*1000;
        setInterval(()=>{let n=Math.max(0,Math.ceil((next-Date.now())/1000));
        document.getElementById('clock').textContent='다음 알림까지 '+Math.floor(n/60)+'분 '+n%60+'초';
        if(n===0){document.getElementById('label').textContent='💙 잠깐 자세를 바꾸고 편하게 움직여보세요!';next=Date.now()+gap*1000;}},1000);
        </script>'''.replace('MINUTES',str(minutes)),height=90)
        st.caption('탭이 닫히거나 휴대폰이 잠기면 알림을 보장할 수 없습니다. 푸시·백그라운드 알림이 아니며 페이지 재실행 시 간격이 초기화됩니다.')

with tabs[4]:
    st.subheader('가족의 작은 실천 모아보기')
    st.caption('같은 세션의 프로필 기록만 표시합니다. 가족을 점수로 비교하거나 진단 순위를 매기지 않습니다.')
    for p in st.session_state.people:
        records=[r for r in st.session_state.records if r['person']==p]
        with st.expander(f'{p} · {len(records)}개 기록',expanded=p==person):
            if not records: st.write('아직 기록이 없어요. 첫 체크를 시작해보세요.')
            for rec in reversed(records[-30:]):
                st.write(f"**{rec['kind']}** · {rec['time']}")
                st.json(rec['details'],expanded=False)
    backup={'version':1,'people':st.session_state.people,'records':st.session_state.records}
    st.download_button('전체 기록 JSON 백업',json.dumps(backup,ensure_ascii=False,indent=2),file_name='likefit_backup.json',mime='application/json')
    st.caption('백업에는 별명과 건강 관련 자가 응답이 포함됩니다. 안전한 장소에 보관하고 공개 GitHub에 올리지 마세요.')
    restore=st.file_uploader('LIkeFit 백업 복원 (기존 기록은 유지)',type=['json'])
    if st.button('백업 가져오기',disabled=restore is None):
        try:
            if restore.size>2_000_000: raise ValueError('2MB 이하 백업만 지원합니다.')
            obj=json.loads(restore.getvalue())
            if not isinstance(obj,dict) or obj.get('version')!=1: raise ValueError('지원하지 않는 백업 형식입니다.')
            people=obj.get('people'); rows=obj.get('records')
            if not isinstance(people,list) or not 1<=len(people)<=12 or any(not isinstance(p,str) or not p.strip() or len(p)>20 for p in people): raise ValueError('프로필 형식 오류')
            if not isinstance(rows,list) or len(rows)>5000: raise ValueError('최대 5,000개 기록까지 복원할 수 있습니다.')
            merged=list(dict.fromkeys(st.session_state.people+people))
            if len(merged)>12: raise ValueError('복원 후 가족이 12명을 초과합니다.')
            for row in rows:
                if not isinstance(row,dict) or not all(k in row for k in ['id','person','time','kind','details']): raise ValueError('기록 형식 오류')
                if not all(isinstance(row[k],str) for k in ['id','person','time','kind']): raise ValueError('기록 값 오류')
                if row['person'] not in people or row['kind'] not in ['사진 관찰','자가 체크','루틴'] or not isinstance(row['details'],dict): raise ValueError('잘못된 기록입니다.')
                datetime.fromisoformat(row['time'])
            known={r['id'] for r in st.session_state.records}
            additions=[]
            for row in rows:
                if row['id'] not in known: additions.append(row);known.add(row['id'])
            st.session_state.people=merged;st.session_state.records.extend(additions)
            st.success(f'{len(additions)}개 기록을 복원했습니다. 다른 탭으로 이동하면 반영됩니다.')
        except Exception as e: st.error(f'복원하지 못했습니다: {e}')
    with st.expander('현재 프로필 기록 삭제'):
        confirm=st.checkbox('현재 프로필의 기록을 모두 삭제합니다. 되돌릴 수 없습니다.')
        if st.button('기록 삭제',disabled=not confirm):
            st.session_state.records=[r for r in st.session_state.records if r['person']!=person]
            if st.session_state.get('analysis',{}).get('person')==person: st.session_state.pop('analysis',None)
            if st.session_state.get('self_result',{}).get('person')==person: st.session_state.pop('self_result',None)
            st.rerun()

with tabs[5]:
    st.subheader('QR로 가족의 휴대폰에서 열기')
    address=st.text_input('배포 완료된 앱의 공개 HTTPS 주소',placeholder='https://your-likefit.streamlit.app')
    if address:
        parsed=urlparse(address.strip())
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.hostname in ['localhost','127.0.0.1']:
            st.warning('휴대폰에서 접속 가능한 공개 HTTPS 주소를 입력하세요.')
        else:
            if qrcode is None:
                st.info('QR 생성 패키지가 설치되지 않았습니다. 아래 주소를 복사해서 가족에게 보내주세요. 다른 기능은 계속 사용할 수 있습니다.')
                st.code(address.strip())
            else:
                qr=qrcode.make(address.strip());buf=io.BytesIO();qr.save(buf,format='PNG')
                st.image(buf.getvalue(),width=240,caption='휴대폰 기본 카메라로 스캔하세요')
                st.download_button('QR 이미지 다운로드',buf.getvalue(),file_name='LIkeFit_QR.png',mime='image/png')
                st.caption('QR은 이 주소를 여는 링크입니다. 앱을 자동 설치하거나 서로의 기록을 공유하지 않습니다.')
    with st.expander('GitHub → Streamlit 배포 순서',expanded=True):
        st.markdown('''1. GitHub 새 저장소 루트에 **app.py**와 **requirements.txt** 두 파일을 올립니다.
2. Streamlit Community Cloud에서 **Create app**으로 GitHub 저장소를 연결합니다.
3. Main file path를 `app.py`, Advanced settings의 Python을 **3.11**로 선택합니다.
4. Deploy 후 공개 앱 주소를 위에 입력하여 QR을 다운로드합니다.
5. 휴대폰에서 QR을 스캔하고 카메라 권한을 허용합니다. iPhone/Android에서 사진 업로드도 사용할 수 있습니다.

**파일명 주의:** 자동 의존성 설치에는 복수형 `requirements.txt`가 필요합니다.

**분석 설치 오류:** Python 3.11을 확인하고 의존성을 설치한 뒤 앱을 재부팅하세요. 이 앱은 MediaPipe 0.10.21의 Pose API를 사용하므로 임의로 최신 버전으로 변경하면 호환되지 않을 수 있습니다.

**OpenCV / libGL 오류:** 호스팅 이미지에 시스템 그래픽 라이브러리가 없으면 설치 문제가 생길 수 있습니다. 이 경우 자가 체크를 이용하고, 별도 시스템 패키지 설정이 가능한 호스팅에서 배포하세요. 두 파일만으로 모든 호스팅 환경의 시스템 패키지를 보장하지는 않습니다.

**사진 인식 한계:** 넉넉한 구도, 수평 카메라, 한 사람 촬영이 필요합니다. 헐렁한 옷·가림·반사·체형에 따라 실패할 수 있습니다. 다리 꼬기 자동 판정은 제공하지 않습니다. 자가 체크로 기록하세요.

**의료 상담:** 지속되는 통증·저림, 눈에 띄는 비대칭, 성장기 척추 변형이 걱정되면 의료진에게 평가받으세요. 심하거나 갑자기 발생한 증상은 신속히 진료받으세요.''')
    st.caption(DISCLAIMER)

st.divider()
st.caption('LIkeFit · Stay comfortable. Move often. Together. | 사진은 진단이 아닌 관찰, 변화는 기록이 아닌 일상에서.')
