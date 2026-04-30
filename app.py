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

# 2. [UI] 페이지 설정 및 스타일 (희진님 커스텀 스타일 복구)
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    /* 1. 딥 레드 배지 스타일 */
    .news-badge {
        background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block;
    }
    /* 2. 파란색 키워드 해시태그 카드 */
    .keyword-card {
        background-color: #E3F2FD; border: 1px solid #BBDEFB; padding: 12px;
        border-radius: 10px; text-align: center; margin-bottom: 10px;
    }
    .keyword-tag { color: #1565C0; font-weight: bold; font-size: 1.1rem; }
    .keyword-basis { color: #64B5F6; font-size: 0.8rem; margin-top: 5px; }
    
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 10px; }
    hr { margin: 8px 0px; border: 0; border-top: 1px solid #f0f0f0; }
    .part-label { background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 및 분석
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-양체험 -원장 -의사 -수의사 -공무원 -모집 -구병원 -에스포항병원"
    if filter_type == "major":
        base_filter += " -획득 -인증 -수상 -보유 -기념"
    
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
    return sorted(final, key=lambda x: x.dt, reverse=True)

def generate_smart_report(title):
    subject_match = re.search(r"['‘\"“](.*?)['’\"”]", title)
    subject = subject_match.group(1) if subject_match else "보건의료 이슈"
    
    mapping = {"디지털": "데이터 무결성", "AI": "분석 정확도", "NGS": "정밀 분석 역량", "자동화": "시스템 관리 능력"}
    my_kw = "실무 적응력"
    for k, v in mapping.items():
        if k in title: my_kw = v; break
            
    return {"subject": subject, "my_kw": my_kw, "example": "관련 실습 당시 오차율을 줄였던 사례"}

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")

tab_news, tab_paper, tab_archive, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🧪 전공 분과", "📓 경험 아카이브", "📅 일정/링크"])

# [탭 1] 의료 뉴스 분석
with tab_news:
    news_data = fetch_refined_data("임상병리사 OR 디지털 헬스케어 OR 의료 AI")
    
    # [복구 2] 현재 분석된 총 뉴스 건수 요약
    st.markdown(f"### 📊 오늘은 총 **{len(news_data)}건**의 트렌드가 분석되었습니다.")
    
    # [복구 3] 파란색 해시태그 키워드 카드 (TOP 5)
    st.subheader("🔥 지금 화제인 키워드")
    kw_cols = st.columns(5)
    all_titles = [e.clean_title for e in news_data]
    words = Counter([w for w in re.findall(r'[가-힣A-Z]{2,}', " ".join(all_titles)) if w not in ["뉴스", "추진", "강화"]]).most_common(5)
    
    for i, (word, count) in enumerate(words):
        with kw_cols[i]:
            st.markdown(f"""
            <div class="keyword-card">
                <div class="keyword-tag">#{word}</div>
                <div class="keyword-basis">{count}개의 관련 기사</div>
            </div>
            """, unsafe_allow_html=True)
    st.divider()
    
    for e in news_data[:12]:
        # [복구 1] 제목 옆 딥 레드 배지 고정
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        
        with st.expander("🔎 분석 리포트 & 자소서 매칭 확인"):
            report = generate_smart_report(e.clean_title)
            
            # [추가] 뉴스 키워드 - 나의 키워드 매칭 표
            st.markdown("#### 🎯 자소서/면접 공략 매칭 테이블")
            match_df = pd.DataFrame({
                "구분": ["뉴스 키워드", "나의 키워드", "사례 예시"],
                "내용": [report['subject'], report['my_kw'], report['example']]
            })
            st.table(match_df)
            
            st.caption(f"발행일: {e.dt.strftime('%Y-%m-%d')} | [뉴스 원문 보기]({e.link})")

# [탭 2] 전공 분과 (독립된 병리 파트 포함)
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🧬 분과별 실무 기술")
        with st.expander("🧪 진단검사 (분자유전/NGS)"):
            for e in fetch_refined_data("(진단검사의학과 NGS) OR (분자유전)", filter_type="major")[:5]:
                st.markdown(f'<span class="part-label">진검</span> {e.clean_title}', unsafe_allow_html=True)
                st.link_button("기술 확인", e.link)
        with st.expander("🔬 병리 파트 (조직/세포/디지털)"):
            for e in fetch_refined_data("(디지털병리) OR (면역조직화학) OR (동결절편)", filter_type="major")[:5]:
                st.markdown(f'<span class="part-label">병리</span> {e.clean_title}', unsafe_allow_html=True)
                st.link_button("전문 기술 확인", e.link)

    with cr:
        st.subheader("🌐 Global Journals")
        for fp in fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')[:8]:
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 **{fp.clean_title}**"); st.link_button("Read", fp.link); st.markdown("<hr>", unsafe_allow_html=True)

# [탭 3] 경험 아카이브
with tab_archive:
    st.subheader("📓 희진님의 실무 경험 기록")
    if 'my_notes' not in st.session_state: st.session_state.my_notes = []
    with st.form("archive_form", clear_on_submit=True):
        cat = st.selectbox("구분", ["🩸 실습", "📜 자소서", "💬 면접", "🔬 공부"])
        txt = st.text_area("메모를 남겨주세요.")
        if st.form_submit_button("저장") and txt:
            st.session_state.my_notes.insert(0, {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "type": cat, "content": txt})
    for n in st.session_state.my_notes:
        st.info(f"{n['date']} [{n['type']}] {n['content']}")

# [탭 4] 일정
with tab_cal:
    st.success("🎯 제54회 임상병리사 국가고시: 2026-12-13")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
