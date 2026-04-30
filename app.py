import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
from datetime import datetime

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="임상병리 전략 마스터", layout="wide")

# 2. 핵심 설정 데이터 (저녁에 구글 시트 연동 시 대체될 부분)
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문", "메디파나"]
ASSOCIATIONS = ["대한임상병리사협회", "대한임상검사정보학회", "대한진단검사의학회", "대한임상미생물검사학회"]

# 3. 데이터 수집 및 정제 함수 (신뢰도/중복/그룹화)
@st.cache_data(ttl=3600)
def fetch_refined_data(keywords, exclude_words="-공무원 -모집 -수당"):
    all_entries = []
    for kw in keywords:
        query = f"{kw} {exclude_words}"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)

    # 중복 그룹화 (제목 앞 15자 기준)
    grouped = defaultdict(list)
    for entry in all_entries:
        key = entry.title[:15]
        grouped[key].append(entry)

    final_list = []
    for key, items in grouped.items():
        # 정렬: 메이저 언론사 우선 -> 최신순
        items.sort(key=lambda x: (
            any(press in x.get('source', {}).get('text', '') for press in MAJOR_PRESS),
            x.published_parsed
        ), reverse=True)
        rep = items[0]
        rep.count = len(items)
        final_list.append(rep)
    return sorted(final_list, key=lambda x: x.published_parsed, reverse=True)

# 4. 전략 및 근거 분석 함수
def analyze_full_strategy(title):
    # 기본값
    topic = "미래 진단 기술 동향"
    evidence = "최신 학술 발표 및 기술 특허 기반"
    
    # 논리적 근거 추출 로직
    if "디지털" in title or "AI" in title:
        topic = "디지털 병리 및 AI 진단 보조"
        evidence = "정부의 디지털 헬스케어 가이드라인 및 대학병원 인프라 도입 확산"
    elif "액체생검" in title or "AACR" in title:
        topic = "액체생검 및 정밀 의료"
        evidence = "글로벌 암 학회(AACR/ASCO) 성과 발표 및 NGS 건강보험 수가 확대 동향"
    elif "간담회" in title or "협력" in title:
        topic = "대학병원 경영 효율화"
        evidence = "필수 의료 확충을 위한 병원 경영진 협의 및 보건복지부 정책 지원"
        
    return {
        "topic": topic,
        "evidence": evidence,
        "tags": f"#{topic.replace(' ', '_')} #실증근거_확보",
        "matching": f"나의 '{MY_EXPERIENCE.split(',')[0]}' 역량을 해당 트렌드에 기여할 포인트로 연결"
    }

# --- 화면 UI 시작 ---
st.title("🔬 임상병리사 커리어 전략 대시보드")
st.markdown(f"**🎯 내 핵심 자소서 소스:** `{MY_EXPERIENCE}`")

# 상단 트렌드 요약 섹션 (최근 1개월 근거 중심)
st.markdown("### 📊 최근 1개월 전략 키워드 & 분석 근거")
t_col1, t_col2, t_col3 = st.columns(3)
with t_col1:
    st.info("**#디지털_병리_전환**")
    st.caption("📜 **근거:** 대학병원 도입 기사 누적 5건 이상 / 정부 표준화 공고")
with t_col2:
    st.info("**#액체생검_현장적용**")
