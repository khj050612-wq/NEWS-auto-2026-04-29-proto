import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="임상병리 성장 기록장", layout="wide")

# 1. 임시 데이터 저장소 초기화 (뉴스 바구니 & 사고 기록장)
if 'news_basket' not in st.session_state:
    st.session_state.news_basket = []
if 'thought_history' not in st.session_state:
    st.session_state.thought_history = []

st.title("🏥 임상병리사 김희진의 성장 기록 시스템")
st.caption("뉴스를 통해 변화하는 나의 사고 과정을 기록하고 추출합니다.")

# --- 상단 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["📰 최신 뉴스 분석", "📝 나의 사고 기록장", "📈 사고 변화 타임라인"])

# [탭 1] 뉴스 분석 (이전과 동일하지만 '사고 기록' 연동 추가)
with tab1:
    st.subheader("국내외 보건의료 이슈")
    # (뉴스 수집 로직은 생략 - 이전 코드를 그대로 사용한다고 가정)
    # 기사 하나가 있다고 가정할 때:
    sample_title = "AI 기반 디지털 병리 진단 시스템 도입 확산"
    with st.expander(f"📌 {sample_title}"):
        st.write("🔗 [기사 링크](https://example.com)")
        
        # 내 생각 입력 칸
        my_insight = st.text_area("이 뉴스를 보고 든 현재의 생각은?", key="insight_input")
        
        if st.button("내 관점으로 스크랩"):
            new_thought = {
                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "주제": sample_title,
                "내용": my_insight
            }
            st.session_state.thought_history.append(new_thought)
            st.toast("사고 기록 완료!")

# [탭 2] 나의 사고 기록장 (그동안 쓴 글 모아보기)
with tab2:
    st.subheader("📔 내가 남긴 관점들")
    if st.session_state.thought_history:
        for i, entry in enumerate(reversed(st.session_state.thought_history)):
            st.info(f"**{entry['날짜']}** - {entry['주제']}")
            st.write(f"💬 {entry['내용']}")
    else:
        st.write("아직 기록된 생각이 없습니다.")

# [탭 3] 사고 변화 타임라인 (사고 발전 과정 추출)
with tab3:
    st.subheader("📈 나의 사고 발전 과정")
    if len(st.session_state.thought_history) >= 2:
        st.write("이전의 생각과 현재의 생각이 어떻게 달라졌는지 비교해 보세요.")
        
        df_thought = pd.DataFrame(st.session_state.thought_history)
        st.table(df_thought) # 표 형태로 한눈에 보기
        
        # 사고 추출 요약 (나중에 AI가 이 부분을 분석하게 됩니다)
        st.success("✨ **성장 포인트 추출**")
        st.write("- **초기:** 뉴스 정보를 수집하는 것에 집중함")
        st.write("- **현재:** 해당 기술이 임상 현장에 미칠 실질적 영향을 분석하기 시작함")
    else:
        st.write("사고 변화를 분석하려면 최소 2개 이상의 기록이 필요합니다.")
