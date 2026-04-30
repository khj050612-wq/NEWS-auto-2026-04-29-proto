import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict, Counter
import datetime
import re

# 1. [데이터] 전역 변수 설정
ASSOC_LINKS = {
    "대한임상병리사협회": {"url": "http://www.kamt.or.kr/", "icon": "🏠"}, 
    "임상검사정보학회": {"url": "http://www.ksclis.or.kr/", "icon": "💻"}, 
    "대한진단검사의학회": {"url": "https://www.kslm.org/", "icon": "🔬"}
}

# 2. [UI] 스타일 (희진님 요청사항: 파란 박스 + 해시태그 강조 + 건수 연하게 하단 배치)
st.set_page_config(page_title="2026 보건의료 뉴스 스크랩", layout="wide")
st.markdown("""
    <style>
    .count-label { font-size: 0.7rem; color: #999; margin-bottom: -25px; }
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; }
    
    /* 파란 박스 카드 디자인 */
    .keyword-card { 
        background-color: #E3F2FD; 
        border: 1px solid #BBDEFB; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        min-height: 180px; 
        display: flex; 
        flex-direction: column; 
        justify-content: flex-start; 
    }
    .keyword-tag { color: #0D47A1; font-weight: 800; font-size: 1.4rem; margin-bottom: 2px; display: block; }
    .count-num { font-size: 0.8rem; font-weight: 400; color: #78909C; margin-bottom: 10px; display: block; }
    
    /* 박스 내부 근거 데이터 */
    .card-evidence { text-align: left; background-color: rgba(255, 255, 255, 0.5); padding: 8px; border-radius: 8px; font-size: 0.75rem; color: #333; }
    .ev-label { font-weight: bold; color: #1565C0; display: block; margin-top: 2px; }

    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 15px; color: #1a1a1a; }
    .part-label { background-color: #f1f3f5; color: #495057; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 뉴스 데이터 정제 및 근거 추출
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-의원 -이벤트 -개원 -진료개시 -원장 -친절 -체험단 -모집 -맛집"
    if filter_type == "news":
        query_text = f"({query_text}) AND (대학병원 OR 상급종합병원 OR 국책 OR 가이드라인 OR 대형병원)"
    url = f"https://news.google.com/rss/search?q={quote(query_text + ' ' + base_filter)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    
    final = []
    for entry in feed.entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        dt = datetime.datetime(*entry.published_parsed[:6])
        
        # 근거 데이터 추출 (기관, 정부, 기술)
        hospitals = re.findall(r'([가-힣]+병원|[가-힣]+의료원)', clean_t)
        govs = re.findall(r'(식약처|복지부|정부|질병청|심평원|보건소)', clean_t)
        techs = re.findall(r'(AI|디지털|NGS|유전체|로봇|빅데이터|비대면)', clean_t)
        
        final.append({
            "title": clean_t,
            "link": entry.link,
            "dt": dt,
            "hospitals": hospitals,
            "govs": govs,
            "techs": techs,
            "count": 1 # 중복 계산용 초기값
        })
    return final

# --- 4. 메인 화면 ---
st.title("🔬 2026 보건의료 뉴스 스크랩")
tab_news, tab_paper, tab_archive, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🧪 전공 분과", "📓 경험 아카이브", "📅 일정/링크"])

# [TAB 1] 뉴스 분석
with tab_news:
    raw_news = fetch_refined_data("임상병리사 OR 디지털 헬스케어 OR 의료 AI")
    
    # 중복 제거 및 카운트 로직
    grouped = defaultdict(list)
    for n in raw_news:
        grouped[n['title'].replace(" ", "")[:12]].append(n)
    
    news_data = []
    for items in grouped.values():
        items.sort(key=lambda x: x['dt'], reverse=True)
        rep = items[0]
        rep['count'] = len(items)
        news_data.append(rep)
    news_data.sort(key=lambda x: x['dt'], reverse=True)

    st.subheader("🔥 주요 키워드 및 근거 데이터")
    kw_cols = st.columns(5)
    all_titles = [e['title'] for e in news_data]
    top_keywords = Counter([w for w in re.findall(r'[가-힣A-Z]{2,}', " ".join(all_titles)) if w not in ["뉴스", "추진", "강화", "대한", "선정"]]).most_common(5)
    
    for i, (word, count) in enumerate(top_keywords):
        # 해당 키워드 관련 근거 취합
        rel_news = [n for n in news_data if word in n['title']]
        h_list = list(set([h for n in rel_news for h in n['hospitals']]))[:2]
        g_list = list(set([g for n in rel_news for g in n['govs']]))[:1]
        t_list = list(set([t for n in rel_news for t in n['techs']]))[:1]

        with kw_cols[i]:
            st.markdown(f"""
                <div class="keyword-card">
                    <span class="keyword-tag">#{word}</span>
                    <span class="count-num">{count}건의 기사</span>
                    <div class="card-evidence">
                        <span class="ev-label">🏥 주요 병원</span> {", ".join(h_list) if h_list else "상급종합병원"}
                        <span class="ev-label">🏛️ 관련 기관</span> {", ".join(g_list) if g_list else "보건복지부 외"}
                        <span class="ev-label">⚙️ 언급 기술</span> {", ".join(t_list) if t_list else "디지털 헬스케어"}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for e in news_data[:12]:
        badge = f'<span class="news-badge">{e["count"]}건</span>' if e["count"] > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e["title"]} {badge}</div>', unsafe_allow_html=True)
        with st.expander("뉴스 상세 데이터 확인"):
            st.write(f"**발행일:** {e['dt'].strftime('%Y-%m-%d')}")
            st.write(f"**언급 기술:** {', '.join(e['techs']) if e['techs'] else '본문 참조'}")
            st.link_button("뉴스 원문 보기", e['link'])

# [TAB 2] 전공 분과
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🧬 분과별 실무 기술")
        sections = {
            "🧪 진단검사 (분자유전/NGS)": "(진단검사의학과 NGS) OR (분자유전)",
            "🧠 생리기능 (심초음파/EEG/TCD)": "(심초음파 검사) OR (뇌파 EEG) OR (신경전도 검사)",
            "🔬 병리 파트 (조직/세포/디지털)": "(디지털병리) OR (면역조직) OR (세포병리)"
        }
        for name, query in sections.items():
            with st.expander(name):
                data = fetch_refined_data(query, filter_type="major")
                for e in data[:5]:
                    st.markdown(f'<span class="part-label">실무</span> {e["title"]}', unsafe_allow_html=True)
                    st.link_button("지침/기술 확인", e['link'])
    with cr:
        st.subheader("🌐 Global Journals")
        data = fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')
        for fp in data[:10]:
            if not re.search('[가-힣]', fp['title']):
                st.markdown(f"📄 {fp['title']}")
                st.link_button("READ", fp['link'])

# [TAB 3] 경험 아카이브
with tab_archive:
    st.subheader("📓 개인 스크랩 & 경험 메모")
    st.info("지식을 채우면서 메모가 필요한 내용을 기록하세요.")
    st.text_area("스크랩 노트", placeholder="이슈의 특징이나 본인의 분석 내용을 기록...", height=300)
    st.button("메모 저장")

# [TAB 4] 수정된 일정/링크 (희진님 요청사항 집중 반영)
with tab_cal:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    st.subheader("🔗 전문 분야별 학회 및 기관")
    
    # 학회 링크 그리드 배치
    c1, c2, c3 = st.columns(3)
    links = list(ASSOC_LINKS.items())
    for i, (name, info) in enumerate(links):
        col = [c1, c2, c3][i % 3]
        col.link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
    
    st.divider()
    
    st.markdown(f"#### ⏰ 하반기 주요 일정 <span class='update-time'>(Last Update: {now})</span>", unsafe_allow_html=True)
    
    col_schedule = st.columns(1)[0]
    with col_schedule:
        st.write("🗓️ **2026 하반기 대학병원 공채 시작** (9월 예정)")
        st.write("🗓️ **제 54회 임상병리사 국가고시** (12월 예정)")
        st.write("🗓️ **주요 분과 학회 추계 학술대회** (10~11월 집중)")
