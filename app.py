"""LIkeFit — streamlit run app.py"""
import time
import io
import base64
from datetime import datetime
from html import escape
import streamlit as st
import streamlit.components.v1 as components
try:
    import qrcode
except ImportError:
    qrcode=None

st.set_page_config(page_title='LIkeFit',page_icon='💙',layout='centered')
st.markdown('''<style>
.stApp{background:#f4f6f9;color:#172b45;color-scheme:light}.block-container{max-width:540px;padding:1.4rem 1rem 5rem}h1,h2,h3{letter-spacing:-.05em;color:#162b47}h1{font-size:30px!important}h3{font-size:20px!important}
[data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"]{display:none}.stAppDeployButton{display:none}
.card{background:#fff;border:1px solid #e8edf4;border-radius:20px;padding:22px;margin:14px 0;color:#1d3452}.muted{font-size:13px;color:#6a7e96}.card h3{margin:0 0 10px}.card p{margin:8px 0;line-height:1.65}.blue{background:#176bee;color:white;border:0}.blue h1,.blue h3{color:white!important}.blue .muted{color:#dfebff}.hero{padding:32px 25px;background:radial-gradient(circle at 95% 0%,#5b9aff,transparent 50%),linear-gradient(140deg,#1046b6,#1875ef);min-height:290px;display:flex;flex-direction:column;justify-content:space-between}.hero h1{font-size:43px!important;color:white;margin:14px 0}.features{display:flex;gap:7px;flex-wrap:wrap}.features span{background:#ffffff24;border:1px solid #ffffff40;padding:10px 12px;border-radius:12px;font-size:13px}.step{display:flex;gap:13px;padding:12px 0;border-bottom:1px solid #eef2f7}.step:last-child{border:0}.step b{color:#176bee}.brand{font-size:22px;font-weight:850;letter-spacing:-1px}.section{margin-top:26px;font-size:12px;font-weight:700;color:#7c8ba0;letter-spacing:1px}
.stButton>button,.stFormSubmitButton>button{min-height:48px;border-radius:13px;font-weight:700}.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:#176bee;border:0;color:white}div[data-testid="stForm"]{border:0;background:white;border-radius:20px;padding:18px}div[role="radiogroup"]{gap:5px;flex-wrap:wrap}div[role="radiogroup"] label{background:white;border:1px solid #e3eaf4;border-radius:12px;padding:10px 8px!important;margin:0!important}div[role="radiogroup"] label p{font-size:13px!important}[data-testid="stCheckbox"]{padding:8px 0}input,select{font-size:16px!important}footer{display:none}

.block-container{padding-top:.7rem;padding-bottom:1rem}.card{padding:15px;margin:9px 0}.hero{min-height:330px;padding:28px 22px}.card p{margin:5px 0;line-height:1.45}.stElementContainer{margin-bottom:0}[data-testid="stVerticalBlock"]{gap:.55rem}[data-testid="stCheckbox"]{padding:2px 0}[data-testid="stCameraInput"] video{max-height:42dvh;object-fit:contain}[data-testid="stSegmentedControl"]{width:100%}[data-testid="stSegmentedControl"] button{flex:1;font-size:12px;padding:7px!important;min-height:40px}

/* Mobile readability and equal-width navigation */
html,body,[data-testid="stAppViewContainer"]{font-size:18px}
.block-container{max-width:600px;padding-left:14px;padding-right:14px}
h1{font-size:36px!important}h2{font-size:29px!important}h3{font-size:25px!important}
.brand{font-size:29px}.card p{font-size:20px;line-height:1.5}.muted{font-size:17px}.features span{font-size:17px}.hero h1{font-size:49px!important}
[data-testid="stWidgetLabel"] p,[data-testid="stCheckbox"] p,[data-testid="stSelectbox"] p{font-size:19px!important}
[data-testid="stCaptionContainer"] p{font-size:17px!important}
.stButton>button,.stFormSubmitButton>button{min-height:54px}.stButton>button p,.stFormSubmitButton>button p{font-size:20px!important}
[data-testid="stSegmentedControl"]{width:100%!important;max-width:100%!important}
[data-testid="stSegmentedControl"] [role="radiogroup"], [data-testid="stSegmentedControl"] [data-baseweb="button-group"]{display:flex!important;width:100%!important;gap:3px!important;flex-wrap:nowrap!important}
[data-testid="stSegmentedControl"] button{flex:1 1 0!important;min-width:0!important;padding:10px 2px!important;min-height:56px!important;border-radius:12px!important}
[data-testid="stSegmentedControl"] button p,[data-testid="stSegmentedControl"] button span{font-size:17px!important;font-weight:750!important;white-space:nowrap}
</style>''',unsafe_allow_html=True)
for k,v in {'check_step':0,'started':False,'people':['나'],'records':[],'result':{},'active':None,'done_steps':[]}.items():
    if k not in st.session_state:st.session_state[k]=v

def card(title,body,blue=False):
    st.markdown(f'<section class="card {"blue" if blue else ""}"><h3>{escape(title)}</h3>{body}</section>',unsafe_allow_html=True)
def record(kind,detail):
    st.session_state.records.append({'person':person,'kind':kind,'detail':detail,'time':datetime.now().strftime('%m.%d %H:%M')})
SOURCE='https://www.nhs.uk/live-well/exercise/sitting-exercises/'
if not st.session_state.started:
    st.markdown('''<div class="card blue hero"><div><div class="muted">FAMILY POSTURE CARE</div><h1>LIkeFit</h1><p>오늘의 자세를 확인하고<br>가족과 함께 바르게 움직여요.</p></div><div class="features"><span>사진 확인</span><span>습관 체크</span><span>맞춤 루틴</span></div></div>''',unsafe_allow_html=True)
    if st.button('시작',type='primary',use_container_width=True):st.session_state.started=True;st.rerun()
    st.stop()

st.markdown('<div class="brand">LIkeFit <span style="color:#1973ed">●</span></div>',unsafe_allow_html=True)
person=st.selectbox('가족 선택',st.session_state.people,key='selected_person')
page=st.segmented_control('메뉴',['홈','사진 분석','체크','루틴','가족'],default='홈',label_visibility='collapsed') or '홈'

if page=='홈':
    card(f'{person}의 오늘', '<p>어깨는 편하게, 발은 바닥에.<br>오래 같은 자세였다면 잠깐 움직여요.</p>',True)
    mine=[r for r in st.session_state.records if r['person']==person]
    count=sum(r['kind']=='루틴' for r in mine)
    card('이번 세션',f'<p>습관 체크 <b>{sum(r["kind"]=="체크" for r in mine)}회</b>　·　완료 루틴 <b>{count}회</b></p>')

elif page=='사진 분석':
    st.caption('정면: 양쪽 어깨 · 옆면: 귀와 어깨')
    if not st.session_state.get('captured_photo'):
        shot=st.camera_input('본인 또는 동의받은 가족을 촬영하세요',key='camera_shot')
        if shot:
            st.session_state.captured_photo=shot.getvalue();st.rerun()
    else:
        components.html('<style>body{margin:0;font:19px system-ui;color:#163353}button,.pick{background:#176deb;color:white;border:0;border-radius:12px;padding:14px 18px;font-size:19px;cursor:pointer;display:inline-block}select{padding:10px;border:1px solid #cee0f5;border-radius:10px;margin:8px}canvas{max-width:100%;max-height:160px;object-fit:contain;display:block;margin:8px auto;border-radius:15px}#status{padding:12px;background:#eaf2ff;border-radius:12px;margin:12px 0}.result{padding:12px;background:#f2f7ff;border-radius:12px;white-space:pre-line}small{display:block;color:#506786;margin:10px 0}a{color:#176deb}input[type=file]{max-width:100%;margin:10px 0}</style>\n<label>촬영 방향 <select id="view"><option value="front">정면</option><option value="left">왼쪽 옆면</option><option value="right">오른쪽 옆면</option></select></label>\n<small>귀·어깨가 보이는 상체 사진도 가능해요.</small>\n<button id="run" disabled>분석 준비 중</button><div id="status" role="status">촬영한 사진을 확인하세요.</div>\n<canvas id="canvas"></canvas><div id="result" class="result" hidden></div>\n\n<small>자세 가이드 · 촬영 각도에 따라 달라져요.</small>\n<script type="module">\nconst $=id=>document.getElementById(id),canvas=$(\'canvas\'),ctx=canvas.getContext(\'2d\');\nlet image=null,detector=null,engine=null,busy=false,version=0;\nconst status=t=>$(\'status\').textContent=t;\nfunction resetOutput(){ $(\'result\').hidden=true;}\nconst captured=new Image();\ncaptured.onload=()=>{const scale=Math.min(1,1200/Math.max(captured.width,captured.height));canvas.width=Math.round(captured.width*scale);canvas.height=Math.round(captured.height*scale);ctx.drawImage(captured,0,0,canvas.width,canvas.height);image=ctx.getImageData(0,0,canvas.width,canvas.height);$(\'run\').disabled=false;$(\'run\').textContent=\'분석\';};\ncaptured.src=\'data:image/jpeg;base64,CAPTURE_DATA\';\n$(\'view\').onchange=()=>{resetOutput();if(image)ctx.putImageData(image,0,0);};\nasync function load(){if(detector)return detector;\n status(\'첫 실행: 분석 모델을 불러오는 중…\');\n engine=await import(\'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs\');\n const files=await engine.FilesetResolver.forVisionTasks(\'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm\');\n detector=await engine.PoseLandmarker.createFromOptions(files,{baseOptions:{modelAssetPath:\'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task\',delegate:\'CPU\'},runningMode:\'IMAGE\',numPoses:2,minPoseDetectionConfidence:.6,minPosePresenceConfidence:.6});return detector;}\n$(\'run\').onclick=async()=>{if(!image||busy)return;busy=true;$(\'run\').disabled=true;$(\'view\').disabled=true;const v=version;resetOutput();\n try{const model=await load();if(v!==version||!image)return;ctx.putImageData(image,0,0);status(\'관절 위치 확인 중…\');\n await new Promise(r=>setTimeout(r,30));const result=model.detect(canvas);if(v!==version)return;\n if(result.landmarks.length!==1){status(result.landmarks.length?\'한 사람만 보이는 사진을 사용하세요.\':\'관절을 찾지 못했어요. 어깨가 잘 보이는 밝은 사진으로 다시 시도하세요.\');return;}\n const lm=result.landmarks[0],view=$(\'view\').value,ids=view===\'front\'?[11,12]:view===\'left\'?[7,11]:[8,12];\n if(ids.some(i=>(lm[i].visibility??0)<.45||lm[i].x<0||lm[i].x>1||lm[i].y<0||lm[i].y>1)){status(\'정면은 양쪽 어깨, 옆면은 선택한 쪽 귀와 어깨가 필요해요. 얼굴만 나온 사진이나 가려진 사진은 분석할 수 없습니다.\');return;}\n const xy=i=>[lm[i].x*canvas.width,lm[i].y*canvas.height];\n const angle=(a,b)=>{const p=xy(a),q=xy(b);return +(Math.atan2(Math.abs(q[1]-p[1]),Math.max(Math.abs(q[0]-p[0]),1e-9))*180/Math.PI).toFixed(1);};\n const edges=[[11,12],[11,23],[12,24],[23,24],[11,13],[13,15],[12,14],[14,16],[23,25],[25,27],[24,26],[26,28]];\n ctx.strokeStyle=\'#2586ff\';ctx.lineWidth=3;for(const [a,b]of edges){if((lm[a].visibility??0)<.65||(lm[b].visibility??0)<.65)continue;ctx.beginPath();ctx.moveTo(...xy(a));ctx.lineTo(...xy(b));ctx.stroke();}\n for(const i of ids){ctx.fillStyle=\'#29ddff\';ctx.beginPath();ctx.arc(...xy(i),6,0,Math.PI*2);ctx.fill();}\n const metrics=view===\'front\'?{\'화면상 어깨선 기울기\':angle(11,12)}:{\'화면상 귀–어깨선 각도\':view===\'left\'?angle(11,7):angle(12,8)};\n if(view===\'front\'&&[23,24].every(i=>(lm[i].visibility??0)>=.65&&lm[i].x>=0&&lm[i].x<=1&&lm[i].y>=0&&lm[i].y<=1))metrics[\'화면상 골반선 기울기\']=angle(23,24);\n const tips=[];\n if(view===\'front\'){\n const diff=(lm[11].y-lm[12].y)*canvas.height;\n tips.push(Math.abs(diff)<1?\'사진상 양쪽 어깨 높이가 비슷해요.\':(diff<0?\'사진상 왼쪽 어깨가 더 높아 보여요.\':\'사진상 오른쪽 어깨가 더 높아 보여요.\'));\n tips.push(\'바로잡기: 양발을 나란히 두고, 어깨 힘을 빼고 10초 유지하세요.\');\n if(metrics[\'화면상 골반선 기울기\']!==undefined)tips.push(\'골반: 양쪽 발에 체중을 고르게 실어보세요.\');\n }else{\n tips.push(\'사진상 귀–어깨 정렬을 확인했어요.\');\n tips.push(\'바로잡기: 시선은 정면, 턱은 가볍게 뒤로. 어깨를 내리고 5초 × 5회.\');\n tips.push(\'화면을 눈높이로 올려보세요.\');\n }\n $(\'result\').textContent=tips.join(\'\\n\')+\'\\n\'+Object.entries(metrics).map(([k,v])=>k.replace(\'화면상 \',\'\')+\': \'+v+\'°\').join(\'\\n\');$(\'result\').hidden=false;\n\nstatus(\'완료 · 관절 위치를 확인하세요.\');\n }catch(e){status(\'분석 모델을 불러오지 못했어요. 인터넷 연결을 확인하거나 다른 브라우저에서 열어주세요.\');console.error(e);}\n finally{busy=false;$(\'run\').disabled=!image;$(\'view\').disabled=false;}\n};window.addEventListener(\'pagehide\',()=>{if(detector)detector.close();});\n</script>'.replace('CAPTURE_DATA',base64.b64encode(st.session_state.captured_photo).decode()),height=490,scrolling=False)
        if st.button('다시 촬영',use_container_width=True):
            st.session_state.pop('captured_photo',None);st.rerun()

elif page=='체크':
    stage=st.session_state.check_step
    if stage==0:
        st.subheader('생활 습관')
        with st.form('habits'):
            neck=st.checkbox('고개를 앞으로 내밀어요')
            shoulder=st.checkbox('어깨가 말리거나 힘이 들어가요')
            lean=st.checkbox('한쪽으로 기대요')
            legs=st.checkbox('다리를 자주 꼬아요')
            symptoms=st.checkbox('통증·저림 또는 최근 부상이 있어요')
            if st.form_submit_button('다음 · 앉는 시간',type='primary',use_container_width=True):
                st.session_state.habits=[neck,shoulder,lean,legs,symptoms];st.session_state.check_step=1;st.rerun()
    elif stage==1:
        st.subheader('앉는 시간')
        duration=st.select_slider('한 번에 얼마나 앉아 있나요?',options=['30분 미만','30~60분','1~2시간','2시간 이상'])
        if st.button('가이드 보기',type='primary',use_container_width=True):
            neck,shoulder,lean,legs,symptoms=st.session_state.habits
            items=[]
            if neck:items.append(('화면','화면을 눈높이에 맞추고 글자를 키워요.'))
            if shoulder:items.append(('어깨','힘을 빼고 가슴 열기 루틴을 해보세요.'))
            if lean:items.append(('균형','양발을 지지하고 한쪽에 오래 기대지 않아요.'))
            if legs:items.append(('다리','다리를 풀고, 발이 뜨면 발 받침을 써요.'))
            if duration!='30분 미만':items.append(('휴식','잠깐 일어나 편안하게 움직여요.'))
            if not items:items=[('유지','편안하게 앉고 자주 자세를 바꿔요.')]
            st.session_state.result[person]={'items':items,'symptoms':symptoms}
            record('체크',duration);st.session_state.check_step=2;st.rerun()
        if st.button('이전',use_container_width=True):st.session_state.check_step=0;st.rerun()
    else:
        result=st.session_state.result.get(person)
        if result:
            body='<p>통증·저림이 있으면 운동 전 의료진에게 확인하세요.</p>' if result['symptoms'] else ''
            for title,text in result['items']:body+=f'<p><b>{escape(title)}</b> · {escape(text)}</p>'
            card('오늘의 실천',body)
        if st.button('다시 체크',use_container_width=True):st.session_state.check_step=0;st.rerun()

elif page=='루틴':
    routines={
    '목 회전': [('준비',15,'바퀴 없는 의자에 앉아 양발을 바닥에 놓고, 어깨 힘을 빼요.')]+[(f'{i+1}회 · {side}',10,f'고개를 {side}으로 편안한 범위까지만 돌려 5초 유지한 뒤 정면으로 돌아와요.') for i in range(3) for side in ['왼쪽','오른쪽']],
    '가슴 열기': [('준비',15,'안정된 의자에 앉아 등받이에서 등을 살짝 떼요.')]+[(f'{i+1}/5회',15,'어깨를 뒤·아래로 가볍게 내리고 팔을 옆으로 열어요. 가슴을 편안하게 열어 5~10초 유지 후 쉬어요.') for i in range(5)],
    '발목 움직이기': [('준비',15,'의자 옆을 잡고 안정되게 앉아요.')]+[(f'{side} · {i+1}/2세트',25,f'{side} 다리를 편안히 펴 발을 바닥에서 살짝 들어요. 발끝을 앞으로 뻗었다 몸쪽으로 당기기를 5회 해요. 힘들면 내려놓고 쉬어요.') for side in ['왼쪽','오른쪽'] for i in range(2)]}
    active=st.session_state.active
    choice=st.selectbox('동작 선택',list(routines),disabled=active is not None)
    steps=routines[choice]
    card(choice,'<p>'+{'목 회전':'좌우 각 3회 · 방향마다 5초','가슴 열기':'5~10초 유지 × 5회','발목 움직이기':'양발 각각 5회 × 2세트'}[choice]+'</p><p class="muted">통증·저림·어지럼이 생기면 중단하세요.</p>')
    safe=st.checkbox('통증 없이 안전하게 움직일 수 있어요',disabled=active is not None)
    if st.button('루틴 시작',type='primary',use_container_width=True,disabled=not safe or active is not None):
        st.session_state.active={'name':choice,'person':person,'index':0,'end':time.time()+steps[0][1]};st.rerun()
    if active and active['person']!=person:
        st.info(f'{active["person"]}의 루틴이 진행 중이에요. 해당 가족으로 전환해주세요.')
    elif active:
        current=routines[active['name']];idx=active['index'];title,secs,text=current[idx]
        card(f'{idx+1}/{len(current)} · {title}',f'<p>{escape(text)}</p>',True)
        @st.fragment(run_every=1)
        def clock():
            left=max(0,int(st.session_state.active['end']-time.time()+.999))
            st.metric('남은 시간',f'{left//60:02d}:{left%60:02d}')
            st.progress(min(1.,max(0.,1-left/secs)))
            if left==0:st.caption('동작을 마쳤다면 아래 버튼을 눌러주세요.')
        clock()
        if st.button('다음 동작' if idx<len(current)-1 else '완료 기록',type='primary',use_container_width=True):
            if time.time()<active['end']:st.warning('타이머가 끝난 뒤 눌러주세요. 힘들면 중단하세요.')
            elif idx<len(current)-1:
                active['index']+=1;active['end']=time.time()+current[active['index']][1];st.rerun()
            else:
                record('루틴',active['name']);st.session_state.active=None;st.session_state['completed_notice']=True;st.rerun()
        if st.button('중단',use_container_width=True):st.session_state.active=None;st.rerun()
    if st.session_state.pop('completed_notice',False):card('완료','<p>오늘의 움직임을 기록했어요.</p>')

elif page=='가족':
    family_page=st.segmented_control('가족 메뉴',['설정','기록','공유'],default='설정',label_visibility='collapsed') or '설정'
    if family_page=='설정':
        with st.form('family',clear_on_submit=True):
            name=st.text_input('가족 별명',max_chars=16,placeholder='예: 엄마, 아빠, 민준')
            add=st.form_submit_button('가족 추가',type='primary',use_container_width=True)
        if add:
            name=name.strip()
            if not name or name in st.session_state.people:st.warning('겹치지 않는 별명을 입력해주세요.')
            elif len(st.session_state.people)>=12:st.warning('가족은 최대 12명까지 추가할 수 있어요.')
            else:st.session_state.people.append(name);st.rerun()
        st.caption('추가한 가족은 화면 위 ‘가족 선택’에서 바꿀 수 있어요.')
        card('우리 가족','<p>'+ ' · '.join(escape(x) for x in st.session_state.people)+'</p>')
    elif family_page=='기록':
        st.markdown(f'### {escape(person)}의 기록')
        mine=[r for r in st.session_state.records if r['person']==person]
        history_page=st.number_input('기록 페이지',min_value=1,max_value=max(1,(len(mine)+1)//2),step=1)
        if not mine:card('첫 실천을 기다려요','<p>체크나 루틴을 완료하면 여기에 보여요.</p>')
        for r in list(reversed(mine))[(history_page-1)*2:history_page*2]:card(r['kind'],f'<p>{escape(r["detail"])}</p><span class="muted">{escape(r["time"])}</span>')
        st.caption('가족·기록은 현재 접속 세션에만 보관돼요. 다른 휴대폰과 동기화되지 않아요.')
    else:
        st.markdown('### 가족에게 공유')
        address='https://2611121313-d9pclpfwungek3wl2j9j2s.streamlit.app/'
        st.link_button('앱 링크',address,use_container_width=True)
        if qrcode:
            buf=io.BytesIO();qrcode.make(address).save(buf,format='PNG');st.image(buf.getvalue(),width=180)
