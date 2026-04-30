import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict, Counter
import datetime
import re

# 1. [UI] 설정: 스크랩북 스타일 (해시태그 강조형)
st.set_page_config(page_title="2026 보건의료 뉴스 스크랩", layout="wide")
st.markdown("""
    <style>
    .count-label { font-size: 0.7rem; color: #999; margin-bottom: -25px; }
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; }
    
    /* 해시태그 카드: 태그를 가장 크게, 건수는 아주 작게 */
    .keyword-card { background-color: #ffffff; border: 1px solid #E3F2FD; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .keyword-tag { color: #0D47A1; font-weight: 800; font-size: 1.3rem; margin-bottom: 2px; }
    .count-num { font-size: 0.8rem; font-weight: 400; color: #9e9e9e; }
    
    /* 안내 문구: 회색으로 은은하게 */
    .simple-guide { color: #888888; font-size: 0.85rem; margin: 30px 0px 10px 0px; border-top: 1px solid #f0f0f0; padding-top: 10px; }
    
    .kw-pill { padding: 3px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 8px; }
    .pill-tech { background-color: #E3F2FD; color: #1565C0; border: 1px solid #BBDEFB; }
    .pill-heavy { background-color: #F3E5F5; color: #7B1FA2; border: 1px solid #E1BEE7; }
    .pill-patient { background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; }
    .pill-network { background-color: #FFF3E0; color: #E65100; border: 1px solid #FFE0B2; }
    
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 15px; color: #1a1a1a; }
    
    /* 근거 데이터 박스 */
    .evidence-box { background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-top: 10px; border-left: 5px solid #0D47A1; }
    .ev-title { font-size: 0.85rem; font-weight: bold; color: #1a1a1a; margin-bottom: 8px; }
    .ev-content { font-size: 0.85rem; color: #444; line-height: 1.6; }
    
    .part-label { background-color: #f1f3f5; color: #495057; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. [로직] 뉴스 데이터 필터링 및 근거 추출
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    # 불필요한 홍보물 및 소음 제거
    base_filter = "-의원 -이벤트 -개원 -진료개시 -원장 -친절 -체험단 -모집 -맛집 -양체험"
    if filter_type == "news":
        query_text = f"({query_text}) AND (대학병원 OR 상급종합병원 OR 국책 OR 가이드라인 OR 대형병원)"
    
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
        
        # 근거 데이터 추출 (기관, 기술, 정책 등)
        hospitals = re.findall(r'([가-힣]+병원|[가-힣]+의료원)', rep.clean_title)
        govs = re.findall(r'(식약처|복지부|정부|질병청|심평원|보건소|원주시|서울시)', rep.clean_title)
        techs = re.findall(r'(AI|디지털|NGS|유전체|로봇|플랫폼|트윈|헬스케어|빅데이터)', rep.clean_title)
        policies = re.findall(r'(가이드라인|제정|선정|구축|실증|혁신|추진)', rep.clean_title)
        
        rep.evidence = {
            "기관": ", ".join(set(hospitals + govs)) if (hospitals + govs) else "본문 내 주요 병원/기관 참조",
            "기술": ", ".join(set(techs)) if techs else "보건의료 서비스",
            "이슈": ", ".join(set(policies)) if policies else "최신 트렌드"
        }
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True)

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

# --- 3. 메인 화면 ---
st.title("🔬 2026 보건의료 뉴스 스크랩")
tab_news, tab_paper, tab_archive = st.tabs(["🗞️ 의료 뉴스 분석", "🧪 전공/심화 지식", "📓 개인 메모"])

# [TAB 1] 뉴스 분석
with tab_news:
    news_data = fetch_refined_data("임상병리사 OR 디지털 헬스케어 OR 의료 AI")
    st.markdown('<div class="count-label">← 관련기사 건수</div>', unsafe_allow_html=True)
    st.subheader("🔥 오늘의 핵심 보건의료 키워드")
    
    # 상단 해시태그 카드 (태그 강조)
    kw_cols = st.columns(5)
    all_titles = [e.clean_title for e in news_data]
    words = Counter([w for w in re.findall(r'[가-힣A-Z]{2,}', " ".join(all_titles)) if w not in ["뉴스", "추진", "강화", "대한", "구축", "선정"]]).most_common(5)
    for i, (word, count) in enumerate(words):
        with kw_cols[i]:
            st.markdown(f"""
                <div class="keyword-card">
                    <div class="keyword-tag">#{word}</div>
                    <div class="count-num">{count}건의 기사</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="simple-guide">... 하단의 키워드를 누르면 이슈 분석과 근거 데이터를 확인할 수 있습니다.</div>', unsafe_allow_html=True)

    for e in news_data[:15]:
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        
        # 키워드 및 필 추출
        subject_match = re.search(r"['‘\"“](.*?)['’\"”]", e.clean_title)
        kw_name = subject_match.group(1) if subject_match else " ".join(e.clean_title.split()[:2])
        pill_html = get_vision_pill(kw_name)
        
        with st.expander(f"🔎 [{kw_name}] 이슈 분석 & 근거 데이터"):
            st.markdown(f"{pill_html} **이슈 요약**", unsafe_allow_html=True)
            
            # 근거 데이터 박스 (병원, 기관, 기술명 등)
            st.markdown(f"""
                <div class="evidence-box">
                    <div class="ev-title">📊 뉴스 언급 데이터 (Fact)</div>
                    <div class="ev-content">
                        <b>📍 관련 기관/병원:</b> {e.evidence['기관']}<br>
                        <b>⚙️ 언급된 기술명:</b> {e.evidence['기술']}<br>
                        <b>📑 이슈 카테고리:</b> {e.evidence['이슈']}<br>
                        <hr style="margin: 10px 0; border: 0; border-top: 1px solid #ddd;">
                        <b>📝 리포트:</b> {e.clean_title}은(는) 2026년 보건의료 트렌드인 {e.evidence['기술']} 중심의 변화를 보여줍니다.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            st.caption(f"[뉴스 원문 읽기]({e.link}) | 발행: {e.dt.strftime('%Y-%m-%d')}")

# [TAB 2] 전공 분과
with tab_paper:
    st.subheader("🧪 분과별 심화 스크랩")
    cl, cr = st.columns(2)
    with cl:
        sections = {
            "🧪 진단검사 (분자유전/NGS)": "진단검사의학과 NGS OR 분자유전",
            "🧠 생리기능 (심초음파/EEG)": "심초음파 OR 뇌파 EEG",
            "🔬 병리 (디지털/조직)": "디지털병리 OR 면역조직"
        }
        for name, query in sections.items():
            with st.expander(name):
                data = fetch_refined_data(query, filter_type="major")
                for e in data[:5]:
                    st.markdown(f'<span class="part-label">실무</span> {e.clean_title}', unsafe_allow_html=True)
                    st.link_button("원문 보기", e.link)
    with cr:
        st.subheader("🌐 Global Journal 스크랩")
        data = fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')
        for fp in data[:10]:
            if not re.search('[가-힣]', fp.clean_title):
                st.write(f"🌍 {fp.clean_title}")
                st.link_button("View Article", fp.link)

# [TAB 3] 개인 메모
with tab_archive:
    st.subheader("📓 개인 스크랩 메모")
    st.info("지식을 채우면서 기억해야 할 핵심 내용을 메모하세요.")
    st.text_area("스크랩 노트", placeholder="이슈의 특징이나 본인의 분석 내용을 기록...", height=400)
    st.button("메모 저장")
