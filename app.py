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

# 2. [UI] 스타일 (병원 비전 키워드 배지 적용)
st.set_page_config(page_title="2026 보건의료 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .count-label { font-size: 0.7rem; color: #999; margin-bottom: -25px; }
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; }
    
    /* 해시태그 카드 */
    .keyword-card { background-color: #f1f3f5; border: 1px solid #dee2e6; padding: 12px; border-radius: 12px; text-align: center; min-height: 100px; display: flex; flex-direction: column; justify-content: center; }
    .count-num { font-size: 1rem; font-weight: 800; color: #495057; margin-bottom: 2px; }
    .keyword-tag { color: #212529; font-weight: bold; font-size: 1.1rem; margin-bottom: 4px; }
    
    /* [수정] 병원 비전 중심 컬러 배지 */
    .kw-pill { padding: 3px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 8px; }
    .pill-tech { background-color: #E3F2FD; color: #1565C0; border: 1px solid #BBDEFB; } /* 첨단지능 */
    .pill-heavy { background-color: #F3E5F5; color: #7B1FA2; border: 1px solid #E1BEE7; } /* 중증고난도 */
    .pill-patient { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; } /* 환자중심 */
    .pill-network { background-color: #FFF3E0; color: #E65100; border: 1px solid #FFE0B2; } /* 케어네트워크 */
    
    .guide-box { background-color: #ffffff; padding: 12px; border: 1px solid #e9ecef; border-left: 5px solid #0D47A1; margin-bottom: 20px; font-size: 0.9rem; }
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 15px; color: #1a1a1a; }
    .part-label { background-color: #f1f3f5; color: #495057; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 병원 비전 키워드 매칭
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
    
    # 비전 매칭 리포트
    report_map = {
        "#첨단지능형": {"kw": "디지털 역량", "desc": "정확한 데이터 관리 및 시스템 적응력"},
        "#중증고난도": {"kw": "전문성", "desc": "정밀 검사 수행 능력 및 오차 분석력"},
        "#환자중심": {"kw": "공감 및 윤리", "desc": "환자 안전을 최우선으로 하는 검사 마인드"},
        "#케어네트워크": {"kw": "협업 능력", "desc": "타 부서와의 원활한 소통 및 유기적 협업"}
    }
    
    pill_html = get_vision_pill(keyword_name)
    category = re.search(r'#(.*?)<', pill_html).group(1)
    match_info = report_map.get(f"#{category}", {"kw": "실무 능력", "desc": "철저한 원칙 준수 및 정확도"})
    
    return {
        "keyword_name": keyword_name,
        "pill": pill_html,
        "topic": f"🏥 병원 비전 연계: {category} 가치 구현을 위한 분석",
        "gov_rule": "2026 상급종합병원 평가 지표 및 환자 안전 기준",
        "my_kw": match_info['kw'],
        "example": f"{keyword_name} 이슈를 고려할 때, {match_info['desc']}를 발휘하여 기여할 수 있음 (추후 내 경험 파일 연동)"
    }

@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-양체험 -원장 -의사 -수의사 -공무원 -모집 -구병원 -에스포항병원"
    if filter_type == "major": base_filter += " -획득 -인증 -수상 -보유"
    url = f"https://news.google.com/rss/search?q={quote(query_text + ' ' + base_filter)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    grouped = defaultdict(list)
    total_raw = len(feed.entries)
    for entry in feed.entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        grouped[clean_t.replace(" ", "")[:12]].append(entry)
    final = []
    for items in grouped.values():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]; rep.count = len(items); rep.dt = datetime.datetime(*rep.published_parsed[:6])
        rep.clean_title = re.sub(r" - .*$", "", rep.title).strip()
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True), total_raw

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

    st.markdown('<div class="guide-box">✨ <b>자소서 팁:</b> 하단의 분석 리포트를 열어 병원의 비전(첨단지능, 환자중심 등)과 자신의 역량을 연결해 보세요.</div>', unsafe_allow_html=True)

    for e in news_data[:12]:
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        report = generate_smart_report(e.clean_title)
        with st.expander(f"🔎 [{report['keyword_name']}] 분석 리포트 & 자소서 매칭확인"):
            st.markdown(f"{report['pill']} **{report['topic']}**", unsafe_allow_html=True)
            st.divider()
            st.markdown("#### 🎯 자소서/면접 전략 매칭")
            match_df = pd.DataFrame({"구분": ["병원 핵심 가치", "연결 역량 키워드", "실전 사례 예시"], "내용": [re.search(r'#(.*?)<', report['pill']).group(1), report['my_kw'], report['example']]})
            st.table(match_df)
            st.caption(f"[뉴스 원문 보기]({e.link}) | {e.dt.strftime('%Y-%m-%d')}")

# (이하 탭 생략 - 기존 병리/생리 탭 그대로 유지)
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🧬 분과별 실무 기술")
        with st.expander("🧪 진단검사 (분자유전/NGS)"):
            data, _ = fetch_refined_data("(진단검사의학과 NGS) OR (분자유전)", filter_type="major")
            for e in data[:5]: st.markdown(f'<span class="part-label">진검</span> {e.clean_title}', unsafe_allow_html=True); st.link_button("기술 확인", e.link)
        with st.expander("🧠 생리기능 (심초음파/EEG/TCD)"):
            data, _ = fetch_refined_data("(심초음파 검사) OR (뇌파 EEG) OR (신경전도 검사)", filter_type="major")
            for e in data[:5]: st.markdown(f'<span class="part-label">생리</span> {e.clean_title}', unsafe_allow_html=True); st.link_button("지침 확인", e.link)
        with st.expander("🔬 병리 파트 (조직/세포/디지털)"):
            data, _ = fetch_refined_data("(디지털병리) OR (면역조직) OR (세포병리)", filter_type="major")
            for e in data[:5]: st.markdown(f'<span class="part-label">병리</span> {e.clean_title}', unsafe_allow_html=True); st.link_button("전문 기술", e.link)
    with cr:
        st.subheader("🌐 Global Journals")
        data, _ = fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')
        for fp in data[:10]:
            if not re.search('[가-힣]', fp.clean_title):
                t = fp.clean_title.replace("Pathology", "**Pathology**").replace("Diagnostic", "**Diagnostic**")
                cols = st.columns([0.8, 0.2])
                cols[0].markdown(f"📄 {t}")
                cols[1].link_button("READ", fp.link)
