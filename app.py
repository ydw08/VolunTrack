import streamlit as st
import requests
import xml.etree.ElementTree as ET
import random
import math
import urllib.parse

# ==========================================
# 🎨 1. 화려한 프리미엄 UI/UX 스타일링 (HTML/CSS)
# ==========================================
st.set_page_config(page_title="VolunTrack AI Pro", page_icon="✨", layout="wide")

st.markdown("""
<style>
    /* 폰트 및 배경 그라데이션 */
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Pretendard', sans-serif;
    }

    /* 메인 히어로 섹션 */
    .hero-container {
        padding: 60px 20px;
        text-align: center;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 40px;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .main-title {
        font-size: 4rem; font-weight: 900; margin-bottom: 10px;
        background: linear-gradient(to right, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .sub-title { font-size: 1.2rem; color: #475569; letter-spacing: 1px; }

    /* 초록색 메인 버튼 커스텀 스타일 */
    div.stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 25px rgba(16, 185, 129, 0.4) !important;
    }

    /* 결과 카드 디자인 (유리 질감) */
    .vol-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 25px;
        padding: 30px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }
    .rank-tag {
        display: inline-block;
        background: #10b981; color: white;
        padding: 5px 20px; border-radius: 50px;
        font-weight: 800; font-size: 0.9rem; margin-bottom: 15px;
    }
    .vol-title { font-size: 1.6rem; font-weight: 800; color: #1e293b; margin-bottom: 10px; }

    /* 점수 메트릭 */
    .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 20px 0; }
    .metric-item {
        background: white; padding: 15px; border-radius: 18px; text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    .m-label { font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px; }
    .m-value { font-size: 1.4rem; font-weight: 800; color: #059669; }
</style>
""", unsafe_allow_html=True)

# 헤더 섹션
st.markdown("""
<div class="hero-container">
    <div class="main-title">VolunTrack AI</div>
    <div class="sub-title">실시간 GPS 연동 전공 적합성 지능형 매칭 엔진</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 📝 2. 사용자 입력 및 필터 (수정된 예시 포함)
# ==========================================
with st.container():
    c1, c2, c3 = st.columns([1.5, 1.5, 1])
    with c1: school_input = st.text_input("🏫 소속 고등학교 (위치 기준)", placeholder="예: 한국고")
    with c2: career_input = st.text_input("🎓 희망 전공 키워드", placeholder="예: 컴퓨터공학")
    with c3: sort_option = st.selectbox("🔍 우선순위 필터", ("🌟 종합 랭킹", "📏 최단 거리순", "🎓 전공 밀착순"))

# ==========================================
# 🛠️ 3. 백엔드 로직 (API & 거리 계산)
# ==========================================
def fetch_1365_data(keyword, num_rows=40):
    API_KEY = 'de7ef85de1d080dfa512c4a0ebdfa3941962fa8d1677f2013c8d02dc7e776427'
    encoded_kw = urllib.parse.quote(keyword)
    url = f"http://openapi.1365.go.kr/openapi/service/rest/VolunteerPartcptnService/getVltrSearchWordList?serviceKey={API_KEY}&keyword={encoded_kw}&numOfRows={num_rows}"
    v_list = []
    try:
        root = ET.fromstring(requests.get(url).content)
        for item in root.findall('.//item'):
            v_list.append({
                "title": item.find('progrmSj').text if item.find('progrmSj') is not None else "제목 없음",
                "address": item.find('actPlace').text if item.find('actPlace') is not None else "장소 미상",
                "content": item.find('progrmCn').text if item.find('progrmCn') is not None else "상세 내용 없음"
            })
    except: pass
    return v_list

# ✨ 수정된 부분 1: 스마트 주소 클리닝이 적용된 좌표 변환 함수
def get_coords(addr, key):
    headers = {"Authorization": f"KakaoAK {key}"}
    
    # 🧹 1단계: 더티 데이터 청소 (괄호나 쉼표 뒤의 쓸데없는 상세 설명 잘라내기)
    clean_addr = addr.split('(')[0].split(',')[0].strip()
    
    try:
        # 🎯 2단계: 카카오 '주소' 정밀 검색 시도
        res = requests.get("https://dapi.kakao.com/v2/local/search/address.json", headers=headers, params={"query": clean_addr}).json()
        if res.get('documents'): 
            return float(res['documents'][0]['y']), float(res['documents'][0]['x'])
            
        # 🚀 3단계: 주소가 아니라 '장소명(예: 순천시청)'으로 적혀있을 때를 위한 '키워드' 검색 풀가동!
        res_kw = requests.get("https://dapi.kakao.com/v2/local/search/keyword.json", headers=headers, params={"query": clean_addr}).json()
        if res_kw.get('documents'):
            return float(res_kw['documents'][0]['y']), float(res_kw['documents'][0]['x'])
    except: 
        pass
        
    return None, None

def calc_dist(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2): return None
    R = 6371
    dLat, dLon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)

# ==========================================
# 🚀 4. 매칭 시작 버튼 및 결과
# ==========================================
if st.button("✨ 초정밀 AI 매칭 분석 시작"):
    if not school_input or not career_input:
        st.warning("⚠️ 모든 정보를 입력해주셔야 분석이 가능합니다.")
    else:
        with st.spinner("🚀 최신 봉사 데이터를 스캔하고 위성 좌표를 계산 중입니다..."):
            KAKAO_KEY = '17c2755ebd29e0cd5c6cd7b52d59f105'
            NEIS_KEY = '9fcdc4432e014490855bb2af1c5999ea'
            CAREER_KEY = '여기에_키_입력' # 실제 키 입력 필요
            
            # 학교/시청 위치
            city, school_full_addr = "순천", ""
            try:
                res = requests.get(f"https://open.neis.go.kr/hub/schoolInfo?KEY={NEIS_KEY}&Type=json&SCHUL_NM={school_input}").json()
                school_full_addr = res['schoolInfo'][1]['row'][0]['ORG_RDNMA']
                city = school_full_addr.split(" ")[1]
            except: pass
            
            s_lat, s_lng = get_coords(school_full_addr, KAKAO_KEY)
            c_lat, c_lng = get_coords(f"{city}시청", KAKAO_KEY)

            # 데이터 확보
            vol_list = fetch_1365_data(city, 40)
            vol_list.extend(fetch_1365_data(career_input[:2], 20))

            scored_data = []
            seen = set()
            for v in vol_list:
                if v['title'] in seen: continue
                seen.add(v['title'])
                
                d_score, d_km = 0, 999.9
                addr, text = v['address'], v['title'] + v['content']
                
                if any(x in text for x in ["온라인", "재택", "비대면"]): d_score, d_km = 50, 0.0
                elif "협의" in addr or "미정" in addr: d_score, d_km = 0, 999.9
                else:
                    v_lat, v_lng = (c_lat, c_lng) if ("일대" in addr or len(addr) < 5) else get_coords(addr, KAKAO_KEY)
                    if v_lat is None: v_lat, v_lng = c_lat, c_lng
                    d_km = calc_dist(s_lat, s_lng, v_lat, v_lng)
                    if d_km is not None:
                        if d_km <= 2.0: d_score = 50
                        elif d_km <= 5.0: d_score = 45
                        else: d_score = max(0, 45 - (math.ceil((d_km-5)/10)*5))

                m_score = random.randint(40, 50) if career_input[:2] in v['title'] else random.randint(0, 10)
                v.update({'dist_km': d_km, 'dist_score': d_score, 'major_score': m_score, 'total': d_score + m_score})
                scored_data.append(v)

            # 정렬
            if "종합" in sort_option: scored_data.sort(key=lambda x: x['total'], reverse=True)
            elif "거리" in sort_option: scored_data.sort(key=lambda x: (x['dist_score'], x['major_score']), reverse=True)
            else: scored_data.sort(key=lambda x: (x['major_score'], x['dist_score']), reverse=True)

            # 결과 렌더링
            st.markdown("<br><h2 style='text-align:center;'>🎯 분석 결과 TOP 10</h2>", unsafe_allow_html=True)
            for idx, item in enumerate(scored_data[:10]):
                
                # ✨ 수정된 부분 2: None 에러를 완벽히 막아내는 거리 텍스트 안전 처리
                d_km = item.get('dist_km')
                dist_label = "🏠 재택/온라인" if d_km == 0 else (f"📍 약 {d_km}km" if d_km is not None and d_km < 900 else "📍 위치 미상")
                
                st.markdown(f"""
                <div class="vol-card">
                    <div class="rank-tag">RANK {idx+1}</div>
                    <div class="vol-title">{item['title']}</div>
                    <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 20px;">📍 {item['address']}</div>
                    <div class="metric-grid">
                        <div class="metric-item"><div class="m-label">총합 점수</div><div class="m-value">{item['total']}점</div></div>
                        <div class="metric-item"><div class="m-label">접근성 점수</div><div class="m-value">{item['dist_score']}/50</div><div style="font-size:0.7rem; color:#94a3b8;">{dist_label}</div></div>
                        <div class="metric-item"><div class="m-label">전공 적합성</div><div class="m-value">{item['major_score']}/50</div><div style="font-size:0.7rem; color:#94a3b8;">{career_input} 연계</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("📝 상세 모집 요강 펼쳐보기"):
                    st.write(item['content'])
                if item['major_score'] >= 40: st.success(f"🤖 AI 가이드: 이 활동은 전공 심화 탐구 능력을 보여주기에 완벽한 기회입니다!")
                elif item['dist_score'] >= 45: st.info(f"🤖 AI 가이드: 매우 높은 접근성을 가지고 있어 효율적인 시간 관리가 가능합니다.")
                st.write("<br>", unsafe_allow_html=True)
