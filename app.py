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

# 2. [UI] 스타일 (희진님 맞춤형 레이아웃)
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    /* 관련기사 문구 구석탱이 배치 */
    .count-label { font-size: 0.7rem; color: #999; margin-bottom: -25px; }
    
    .news-badge {
        background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block;
    }
    
    /* 해시태그 카드 (숫자만 깔끔하게) */
    .keyword-card {
        background-color: #E3F2FD; border: 1px solid #BBDEFB; padding: 12px;
        border-radius: 12px; text-align: center; min-height: 100px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .count-num { font-size: 1rem; font-weight: 800; color: #0D47A1; margin-bottom: 2px; }
    .keyword-tag { color: #1565C0; font-weight: bold; font-size: 1.1rem; margin-bottom: 4px; }
    .keyword-basis { color: #1E88E5; font-size: 0.8rem; font-weight: 500; line-height: 1.3; word-break: keep-all; }
    
    .summary-text { font-size: 0.85rem; color: #666; margin: 10px 0px; }
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 12px; }
    .part-label { background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    
    /* 글로벌 저널 가독성 (행간 압축) */
    .journal-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; border-bottom: 1px solid #f9f9f9; }
    .journal-title { font-size: 0.85rem; color: #333; flex: 1; margin-right: 10px; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 처리 함수들
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

def generate_smart_report(title):
    subject_match = re.search(r"['‘\"“](.*?)['’\"”]", title)
    keyword_name = subject_match.group(1) if subject_match else " ".join(title.split()[:2])
    mapping = {"디지털": "데이터 무결성", "AI": "분석 정확도", "NGS": "정밀 분석 역량", "심초음파": "검사 전문성"}
    my_kw = "실무 적응력"
    for k, v in mapping.items():
        if k in title: my_kw = v; break
    return {
        "keyword_name": keyword_name,
        "topic": f"🔥 {keyword_name} 도입에 따른 검사 환경의 변화",
        "gov_rule": "2026 보건의료 품질관리 가이드라인",
        "my_kw": my_kw,
        "example": f"{keyword_name} 관련 실습 시 정확한 분석 절차를 준수한 사례 (추후 파일 연동 가능)"
    }

def get_basis_text(word):
    bases = {"디지털": "병리/검사실 디지털 전환 가속화", "AI": "인공지능 판독 보조 솔루션 도입 확대", "NGS": "유전체 분석 기반 정밀의료 확산", "임상병리사": "전문성 강화 논의", "검사": "POCT 및 스마트 검사 지침 강화"}
    return bases.get(word, "최신 의료 기술 도입 대응 필요")

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")

tab_news, tab_paper, tab_archive, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🧪 전공 분과", "📓 경험 아카이브", "📅 일정/링크"])

# [탭 1] 의료 뉴스 분석
with tab_news:
    news_data, total_count = fetch_refined_data("임상병리사 OR 디지털 헬스케어 OR 의료 AI")
    
    # "관련기사" 문구 구석탱이 배치
    st.markdown('<div class="count-label">← 관련기사 건수</div>', unsafe_allow_html=True)
    st.subheader("🔥 지금 화제인 키워드")
    
    kw_cols = st.columns(5)
    all_titles = [e.clean_title for e in news_data]
    words = Counter([w for w in re.findall(r'[가-힣A-Z]{2,}', " ".join(all_titles)) if w not in ["뉴스", "추진", "강화", "대한"]]).most_common(5)
    
    for i, (word, count) in enumerate(words):
        with kw_cols[i]:
            basis = get_basis_text(word)
            st.markdown(f"""
            <div class="keyword-card">
                <div class="count-num">{count}건</div>
                <div class="keyword-tag">#{word}</div>
                <div class="keyword-basis">{basis}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="summary-text">📊 분석 결과: 총 {total_count}건 중 {len(news_data)}개의 핵심 이슈 선별</div>', unsafe_allow_html=True)
    
    for e in news_data[:12]:
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        with st.expander("🔎 분석 리포트 & 자소서 매칭 확인"):
            report = generate_smart_report(e.clean_title)
            st.success(f"**📌 분석 주제**: {report['topic']}")
            st.info(f"**📜 관련 근거**: {report['gov_rule']}")
            st.divider()
            st.markdown("#### 🎯 자소서/면접 전략 매칭")
            match_df = pd.DataFrame({"구분": ["뉴스 핵심 이름", "연결 역량 키워드", "실전 사례 예시"], "내용": [report['keyword_name'], report['my_kw'], report['example']]})
            st.table(match_df)
            st.caption(f"[뉴스 원문 보기]({e.link}) | {e.dt.strftime('%Y-%m-%d')}")

# [탭 2] 전공 분과 (진검/생리/병리)
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🧬 분과별 실무 기술")
        with st.expander("🧪 진단검사 (분자유전/NGS)"):
            data, _ = fetch_refined_data("(진단검사의학과 NGS) OR (분자유전)", filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">진검</span> {e.clean_title}', unsafe_allow_html=True)
                st.link_button("기술 확인", e.link)
        with st.expander("🧠 생리기능 (심초음파/EEG/TCD)"):
            data, _ = fetch_refined_data("(심초음파 검사) OR (뇌파 EEG) OR (신경전도 검사)", filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">생리</span> {e.clean_title}', unsafe_allow_html=True)
                st.link_button("지침 확인", e.link)
        with st.expander("🔬 병리 파트 (조직/세포/디지털)"):
            data, _ = fetch_refined_data("(디지털병리) OR (면역조직) OR (세포병리)", filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">병리</span> {e.clean_title}', unsafe_allow_html=True)
                st.link_button("전문 기술", e.link)
    with cr:
        st.subheader("🌐 Global Journals")
        data, _ = fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')
        for fp in data[:10]:
            if not re.search('[가-힣]', fp.clean_title):
                # 제목 내 강조 단어 굵게 처리
                t = fp.clean_title.replace("Pathology", "**Pathology**").replace("Diagnostic", "**Diagnostic**").replace("Clinical", "**Clinical**")
                cols = st.columns([0.8, 0.2])
                cols[0].markdown(f"📄 {t}")
                cols[1].link_button("READ", fp.link)

# [탭 3] 경험 아카이브
with tab_archive:
    st.subheader("📓 희진님의 실무 경험 기록")
    if 'my_notes' not in st.session_state: st.session_state.my_notes = []
    with st.form("archive_form", clear_on_submit=True):
        cat = st.selectbox("카테고리", ["🩸 실습", "📜 자소서", "💬 면접", "🔬 공부"])
        txt = st.text_area("경험 메모 (여기에 적은 내용이 나중에 자소서 매칭에 활용됩니다)"); sub = st.form_submit_button("저장")
        if sub and txt: st.session_state.my_notes.insert(0, {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "type": cat, "content": txt})
    for n in st.session_state.my_notes: st.info(f"{n['date']} [{n['type']}] {n['content']}")

# [탭 4] 일정
with tab_cal:
    st.success("🎯 제54회 임상병리사 국가고시: 2026-12-13")
    l_cols = st.columns(3)
    for i, (name, info) in enumerate(ASSOC_LINKS.items()): l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
