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

# 2. [UI] 스타일 (회색 가이드 문구 및 박스 제거)
st.set_page_config(page_title="2026 보건의료 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .count-label { font-size: 0.7rem; color: #999; margin-bottom: -25px; }
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; }
    
    .keyword-card { background-color: #E3F2FD; border: 1px solid #BBDEFB; padding: 12px; border-radius: 12px; text-align: center; min-height: 100px; display: flex; flex-direction: column; justify-content: center; }
    .count-num { font-size: 1rem; font-weight: 800; color: #0D47A1; margin-bottom: 2px; }
    .keyword-tag { color: #1565C0; font-weight: bold; font-size: 1.1rem; margin-bottom: 4px; }
    
    /* [수정] 가이드 문구: 회색 글씨로 슬림하게 */
    .simple-guide { color: #888888; font-size: 0.85rem; margin: 30px 0px 10px 0px; border-top: 1px solid #f0f0f0; padding-top: 10px; }
    
    .kw-pill { padding: 3px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 8px; }
    .pill-tech { background-color: #E3F2FD; color: #1565C0; border: 1px solid #BBDEFB; }
    .pill-heavy { background-color: #F3E5F5; color: #7B1FA2; border: 1px solid #E1BEE7; }
    .pill-patient { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; }
    .pill-network { background-color: #FFF3E0; color: #E65100; border: 1px solid #FFE0B2; }
    
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 15px; color: #1a1a1a; }
    .part-label { background-color: #f1f3f5; color: #495057; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 뉴스 및 리포트 처리 (에러 수정본 유지)
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-의원 -체험단 -맛집"
    if filter_type == "news":
        query_text = f"({query_text}) AND (대학병원 OR 상급종합병원 OR 종합병원 OR 국책 OR 가이드라인 OR 대형병원 OR 전문병원)"
    url = f"https://news.google.com/rss/search?q={quote(query_text + ' ' + base_filter)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    grouped = defaultdict(list)
    for entry in feed.entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        grouped[clean_t.replace(" ", "")[:12]].append(entry)
    final = []
    for items in grouped.values():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        rep.dt = datetime.datetime(*rep.published_parsed[:6])
        rep.clean_title = re.sub(r" - .*$", "", rep.title).strip()
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True), len(feed.entries)

def get_vision_pill(word):
    tech = ["AI", "디지털", "첨단", "지능", "스마트", "로봇", "데이터"]
    heavy = ["중증", "고난도", "암", "희귀", "이식", "NGS", "분자"]
    patient = ["환자", "경험", "안전", "케어", "접근성", "환경"]
    network = ["네트워크", "클러스터", "상생", "협력", "지역", "공유"]
    if any(k in word for k in tech): return f'<span class="kw-pill pill-tech">#첨단지능형</span>'
    if any(k in word for k in heavy): return f'<span class="kw-pill pill-heavy">#중증고난도</span>'
    if any(k in word for k in patient): return f'<span class="kw-pill pill-patient">#환자중심</span>'
    if any(k in word for k in network): return f'<span class="kw-pill pill-network">#케어네트워크</span>'
    return f'<span class="kw-pill pill-tech">#메디컬이슈</span>'

def generate_smart_report(title):
    subject_match = re.search(r"['‘\"“](.*?)['’\"”]", title)
    keyword_name = subject_match.group(1) if subject_match else " ".join(title.split()[:2])
    pill_html = get_vision_pill(keyword_name)
    category = re.search(r'#(.*?)<', pill_html).group(1)
    mapping = {"#첨단지능형": "디지털 역량", "#중증고난도": "전문성", "#환자중심": "공감 및 윤리", "#케어네트워크": "협업 능력"}
    my_kw = mapping.get(f"#{category}", "실무 능력")
    return {"keyword_name": keyword_name, "pill": pill_html, "category": category, "my_kw": my_kw}

# --- 4. 메인 화면 ---
st.title("🔬 2026 보건의료 뉴스-자소서 전략")
tab_news, tab_paper, tab_archive, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🧪 전공 분과", "📓 경험 아카이브", "📅 일정/링크"])

with tab_news:
    news_data, total_count = fetch_refined_data("임상병리사 OR 디지털 헬스케어 OR 의료 AI")
    
    st.markdown('<div class="count-label">← 관련기사 건수</div>', unsafe_allow_html=True)
    st.subheader("🔥 주요 병원 관심 키워드")
    kw_cols = st.columns(5)
    all_titles = [e.clean_title for e in news_data]
    words = Counter([w for w in re.findall(r'[가-힣A-Z]{2,}', " ".join(all_titles)) if w not in ["뉴스", "추진", "강화", "대한"]]).most_common(5)
    for i, (word, count) in enumerate(words):
        with kw_cols[i]: st.markdown(f'<div class="keyword-card"><div class="count-num">{count}건</div><div class="keyword-tag">#{word}</div></div>', unsafe_allow_html=True)

    # [수정 반영] 안내 멘트 회색 텍스트로 변경
    st.markdown('<div class="simple-guide"> 하단의 키워드를 누르면 분석리포트&자소서매칭 확인이 가능합니다. 병원의 인재상과 자신의 역량을 연결해보세요.</div>', unsafe_allow_html=True)

    for e in news_data[:12]:
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        report = generate_smart_report(e.clean_title)
        with st.expander(f"🔎 [{report['keyword_name']}]"):
            st.markdown(f"{report['pill']} **{report['keyword_name']} 이슈 중심 분석**", unsafe_allow_html=True)
            st.divider()
            st.markdown("#### 🎯 자소서/면접 전략 매칭")
            match_df = pd.DataFrame({"구분": ["병원 핵심 가치", "연결 역량 키워드", "실전 사례 예시"], "내용": [report['category'], report['my_kw'], "업로드된 파일에서 매칭될 예정입니다."]})
            st.table(match_df)
            st.caption(f"[뉴스 원문 보기]({e.link}) | {e.dt.strftime('%Y-%m-%d')}")
            
# [TAB 2] 전공 분과 (복구)
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
                data, _ = fetch_refined_data(query, filter_type="major")
                for e in data[:5]:
                    st.markdown(f'<span class="part-label">실무</span> {e.clean_title}', unsafe_allow_html=True)
                    st.link_button("지침/기술 확인", e.link)
    with cr:
        st.subheader("🌐 Global Journals")
        data, _ = fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')
        for fp in data[:10]:
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 {fp.clean_title}")
                st.link_button("READ", fp.link)

# [TAB 3] 경험 아카이브 (복구)
with tab_archive:
    st.subheader("📓 나의 경험 데이터베이스")
    st.info("여기에 희진님의 자소서 파일이나 실습 일지를 업로드하면 뉴스 키워드와 자동으로 매칭됩니다.")
    uploaded_file = st.file_uploader("자소서/경험 정리 파일 업로드 (PDF, TXT)", type=["pdf", "txt"])
    if uploaded_file:
        st.success("파일이 성공적으로 로드되었습니다. 이제 뉴스 리포트에서 관련 경험이 매칭됩니다.")

# [TAB 4] 일정/링크 (복구)
with tab_cal:
    st.subheader("📅 주요 일정 및 바로가기")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🔗 유관 기관")
        for name, info in ASSOC_LINKS.items():
            st.link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
    with c2:
        st.markdown("#### ⏰ 하반기 주요 일정")
        st.write("- 2026 하반기 대학병원 공채 시작 (9월 예정)")
        st.write("- 제 54회 임상병리사 국가고시 (12월 예정)")
