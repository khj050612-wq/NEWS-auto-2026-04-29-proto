@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-양체험 -원장 -의사 -수의사 -공무원 -모집 -구병원 -에스포항병원"
    if filter_type == "major": base_filter += " -획득 -인증 -수상 -보유"
    url = f"https://news.google.com/rss/search?q={quote(query_text + ' ' + base_filter)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    grouped = defaultdict(list)
    total_raw = len(feed.entries)
    
    for entry in feed.entries:
        # 제목에서 신문사 이름 제거 등 전처리
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        grouped[clean_t.replace(" ", "")[:12]].append(entry)
        
    final = []
    for items in grouped.values():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        rep.dt = datetime.datetime(*rep.published_parsed[:6])
        # [수정 포인트] 에러 발생 지점 복구: 원본 제목에서 불필요한 부분만 제거
        rep.clean_title = re.sub(r" - .*$", "", rep.title).strip()
        final.append(rep)
        
    return sorted(final, key=lambda x: x.dt, reverse=True), total_raw
