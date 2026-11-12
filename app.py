"""LIkeFit. Run: streamlit run app.py. Browser-side photo analysis. Session-only records."""
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

DISCLAIMER = '자세 습관 참고용 · 의료 진단이 아닙니다.'


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
    st.caption('기록은 현재 세션에만 저장됩니다. 종료 전 백업하세요.')
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
    st.subheader('사진으로 자세 확인')
    st.caption('사진은 브라우저에서 처리됩니다. 처음에는 모델 로딩 시간이 필요해요.')
    agreed=st.checkbox('촬영 대상의 동의를 받았습니다.')
    if agreed:
        components.html('<style>body{margin:0;font:15px system-ui;color:#163353}button,.pick{background:#176deb;color:white;border:0;border-radius:12px;padding:13px 18px;cursor:pointer;display:inline-block}select{padding:10px;border:1px solid #cee0f5;border-radius:10px;margin:8px}canvas{max-width:100%;max-height:520px;object-fit:contain;display:block;margin:14px auto;border-radius:15px}#status{padding:12px;background:#eaf2ff;border-radius:12px;margin:12px 0}.result{padding:12px;background:#f2f7ff;border-radius:12px;white-space:pre-line}small{display:block;color:#506786;margin:10px 0}a{color:#176deb}input[type=file]{max-width:100%;margin:10px 0}</style>\n<label>촬영 방향 <select id="view"><option value="front">정면</option><option value="left">왼쪽 옆면</option><option value="right">오른쪽 옆면</option></select></label>\n<small>옆면: 귀와 어깨만 보여도 분석합니다. 정면: 양쪽 어깨가 보이게 찍어주세요.</small>\n<input id="file" type="file" accept="image/jpeg,image/png,image/webp">\n<small>사진은 브라우저 안에서 분석됩니다. 분석 모델을 불러오려면 인터넷이 필요합니다.</small>\n<button id="run" disabled>사진을 먼저 선택하세요</button>\n<button id="clear" style="background:#e1ebfa;color:#163353">지우기</button>\n<div id="status" role="status">사진을 선택하면 미리보기가 나타납니다.</div>\n<canvas id="canvas"></canvas><div id="result" class="result" hidden></div>\n<a id="download" hidden download="LIkeFit_photo.json">관찰값 다운로드</a>\n<small>자세 참고용이며 의료 진단이 아닙니다. 촬영 각도에 따라 값이 달라집니다.</small>\n<script type="module">\nconst $=id=>document.getElementById(id),canvas=$(\'canvas\'),ctx=canvas.getContext(\'2d\');\nlet image=null,detector=null,engine=null,busy=false,downloadURL=null,version=0;\nconst status=t=>$(\'status\').textContent=t;\nfunction resetOutput(){ $(\'result\').hidden=true;$(\'download\').hidden=true;if(downloadURL){URL.revokeObjectURL(downloadURL);downloadURL=null;} }\n$(\'file\').onchange=async()=>{const f=$(\'file\').files[0],v=++version;image=null;resetOutput();$(\'run\').disabled=true;if(!f)return;\n if(f.size>10*1024*1024){status(\'10MB 이하 사진을 선택하세요.\');return;}\n try{const bmp=await createImageBitmap(f);if(v!==version){bmp.close();return;}if(bmp.width*bmp.height>30000000){bmp.close();throw Error(\'size\');}\n const s=Math.min(1,1400/Math.max(bmp.width,bmp.height));canvas.width=Math.round(bmp.width*s);canvas.height=Math.round(bmp.height*s);ctx.drawImage(bmp,0,0,canvas.width,canvas.height);bmp.close();image=ctx.getImageData(0,0,canvas.width,canvas.height);$(\'run\').disabled=false;$(\'run\').textContent=\'사진 분석\';status(\'준비됐어요. 사진 분석을 눌러주세요.\');}catch(e){status(\'사진을 열지 못했습니다. JPG 또는 PNG로 다시 선택하세요.\');}};\n$(\'view\').onchange=()=>{resetOutput();if(image)ctx.putImageData(image,0,0);};\n$(\'clear\').onclick=()=>{version++;image=null;canvas.width=0;canvas.height=0;$(\'file\').value=\'\';$(\'run\').disabled=true;resetOutput();status(\'사진을 지웠습니다.\');};\nasync function load(){if(detector)return detector;\n status(\'첫 실행: 분석 모델을 불러오는 중…\');\n engine=await import(\'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs\');\n const files=await engine.FilesetResolver.forVisionTasks(\'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm\');\n detector=await engine.PoseLandmarker.createFromOptions(files,{baseOptions:{modelAssetPath:\'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task\',delegate:\'CPU\'},runningMode:\'IMAGE\',numPoses:2,minPoseDetectionConfidence:.6,minPosePresenceConfidence:.6});return detector;}\n$(\'run\').onclick=async()=>{if(!image||busy)return;busy=true;$(\'run\').disabled=true;$(\'file\').disabled=true;$(\'view\').disabled=true;const v=version;resetOutput();\n try{const model=await load();if(v!==version||!image)return;ctx.putImageData(image,0,0);status(\'관절 위치 확인 중…\');\n await new Promise(r=>setTimeout(r,30));const result=model.detect(canvas);if(v!==version)return;\n if(result.landmarks.length!==1){status(result.landmarks.length?\'한 사람만 보이는 사진을 사용하세요.\':\'관절을 찾지 못했어요. 어깨가 잘 보이는 밝은 사진으로 다시 시도하세요.\');return;}\n const lm=result.landmarks[0],view=$(\'view\').value,ids=view===\'front\'?[11,12]:view===\'left\'?[7,11]:[8,12];\n if(ids.some(i=>(lm[i].visibility??0)<.45||lm[i].x<0||lm[i].x>1||lm[i].y<0||lm[i].y>1)){status(\'정면은 양쪽 어깨, 옆면은 선택한 쪽 귀와 어깨가 필요해요. 얼굴만 나온 사진이나 가려진 사진은 분석할 수 없습니다.\');return;}\n const xy=i=>[lm[i].x*canvas.width,lm[i].y*canvas.height];\n const angle=(a,b)=>{const p=xy(a),q=xy(b);return +(Math.atan2(Math.abs(q[1]-p[1]),Math.max(Math.abs(q[0]-p[0]),1e-9))*180/Math.PI).toFixed(1);};\n const edges=[[11,12],[11,23],[12,24],[23,24],[11,13],[13,15],[12,14],[14,16],[23,25],[25,27],[24,26],[26,28]];\n ctx.strokeStyle=\'#2586ff\';ctx.lineWidth=3;for(const [a,b]of edges){if((lm[a].visibility??0)<.65||(lm[b].visibility??0)<.65)continue;ctx.beginPath();ctx.moveTo(...xy(a));ctx.lineTo(...xy(b));ctx.stroke();}\n for(const i of ids){ctx.fillStyle=\'#29ddff\';ctx.beginPath();ctx.arc(...xy(i),6,0,Math.PI*2);ctx.fill();}\n const metrics=view===\'front\'?{\'화면상 어깨선 기울기\':angle(11,12)}:{\'화면상 귀–어깨선 각도\':view===\'left\'?angle(11,7):angle(12,8)};\n if(view===\'front\'&&[23,24].every(i=>(lm[i].visibility??0)>=.65&&lm[i].x>=0&&lm[i].x<=1&&lm[i].y>=0&&lm[i].y<=1))metrics[\'화면상 골반선 기울기\']=angle(23,24);\n $(\'result\').textContent=Object.entries(metrics).map(([k,v])=>k+\': \'+v+\'°\').join(\'\\n\')+\'\\n\\n\'+(view===\'front\'?\'척추측만증 판정값이 아닙니다.\':\'경추각(CVA) 또는 거북목 판정값이 아닙니다.\');$(\'result\').hidden=false;\n downloadURL=URL.createObjectURL(new Blob([JSON.stringify({time:new Date().toISOString(),view,metrics},null,2)],{type:\'application/json\'}));$(\'download\').href=downloadURL;$(\'download\').hidden=false;status(\'완료 · 점이 실제 관절과 맞는지 확인하세요.\');\n }catch(e){status(\'분석 모델을 불러오지 못했어요. 인터넷 연결을 확인하거나 다른 브라우저에서 열어주세요.\');console.error(e);}\n finally{busy=false;$(\'run\').disabled=!image;$(\'file\').disabled=false;$(\'view\').disabled=false;}\n};window.addEventListener(\'pagehide\',()=>{if(detector)detector.close();});\n</script>',height=1000,scrolling=True)
    st.caption('사진 관찰값은 다운로드로 보관하세요. 가족 기록에 자동 저장되지는 않습니다.')

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
        st.caption('좌우 드래그로 회전 · 교육용 모형이며 사용자 신체나 척추측만증을 재현한 것이 아닙니다.')

with tabs[3]:
    st.subheader('짧게 움직이고, 다시 일상으로')
    st.warning('통증·저림·어지럼이 있으면 중단하세요.')
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
    with st.expander('배포 안내'):
        st.write('GitHub에 app.py와 requirements.txt 업로드 → Streamlit에서 저장소 연결 → app.py 배포')
        st.caption('사진 분석에는 서버 MediaPipe 설치가 필요 없습니다. 브라우저가 외부 모델을 불러옵니다.')

    st.caption(DISCLAIMER)

st.divider()
st.caption('LIkeFit · Stay comfortable. Move often. Together. | 사진은 진단이 아닌 관찰, 변화는 기록이 아닌 일상에서.')
