import streamlit as st
import pandas as pd
import heapq

st.set_page_config(
    page_title="DIGIMON CYBER SLEUTH",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. UI/CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Pretendard:wght@400;600;700&display=swap');

    /* Streamlit 상단 흰색 바 / 헤더 숨기기 및 기본 패딩 제거 */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 900px; /* 고해상도 모니터에서도 가독성을 위해 정돈된 폭 제공 */
    }

    /* 전체 앱 배경 */
    .stApp, [data-testid="stSidebar"] {
        background-color: #060913 !important;
        color: #f1f5f9;
        font-family: 'Pretendard', -apple-system, sans-serif;
    }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
        background-color: #0a0f1d !important;
    }

    /* 메인 타이틀 헤더 */
    .hero-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.7) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        border-radius: 14px;
        padding: 20px 28px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        
    }
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 1.6rem;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Selectbox 위 라벨 글자색 및 폰트 변경 */
    div[data-testid="stSelectbox"] label p {
        color: #94a3b8 !important; /* 밝은 슬레이트 블루/그레이 */
        font-weight: 700 !important;
    }

    /* Metric 소제목 글자색 */
    div[data-testid="stMarkdownContainer"] p {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    /* Metric 메인 값 글자색 */
    div[data-testid="stMetricValue"] div {
        color: #38bdf8 !important; /* 사이버틱한 네온 블루 */
        font-family: 'Orbitron', sans-serif !important;
    }
    /* 카드 노드 기본 스타일 */
    .step-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 14px 18px;
        position: relative;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    .step-card-evo {
        border-left: 5px solid #10b981 !important;
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.05) 0%, #0f172a 100%);
    }
    .step-card-dev {
        border-left: 5px solid #3b82f6 !important;
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, #0f172a 100%);
    }
    .step-card-start {
        border-left: 5px solid #38bdf8 !important;
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.08) 0%, #111827 100%);
    }

    /* 타이틀 및 가독성 최적화 */
    .digimon-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        margin-right: 8px;
    }
    .step-label {
        color: #94a3b8; /* 가독성을 위한 명도 업 */
        font-size: 0.82rem;
        font-family: 'Orbitron', monospace;
        font-weight: 600;
    }

    /* 요구조건 태그 */
    .req-container {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
    }
    .req-chip {
        background: #182235;
        border: 1px solid #283854;
        color: #38bdf8;
        font-family: 'Orbitron', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 5px;
    }
    .req-chip-extra {
        background: #31131d;
        border-color: #881337;
        color: #fda4af;
    }

    /* 세대 및 속성 배지 */
    .badge {
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        display: inline-block;
        vertical-align: middle;
    }
    .badge-stage { background: #334155; color: #f1f5f9; }
    .badge-attr { background: #1e1b4b; color: #c7d2fe; border: 1px solid rgba(165, 180, 252, 0.2); }

    /* 연결 커넥터 (기존 화살표 대체) */
    .path-connector {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 24px;
        position: relative;
    }
    .path-line {
        position: absolute;
        width: 2px;
        height: 100%;
        background: linear-gradient(180deg, rgba(56, 189, 248, 0.4) 0%, rgba(129, 140, 248, 0.1) 100%);
    }
    .path-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #38bdf8;
        box-shadow: 0 0 8px #38bdf8;
        z-index: 1;
    }

    /* Streamlit 기본 버튼 스타일 개선 */
    .stButton>button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 6px 12px !important;
        transition: all 0.2s !important;
    }
    .stButton>button:hover {
        background-color: #ef4444 !important;
        color: #ffffff !important;
        border-color: #f87171 !important;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
    }
    
    /* Selectbox 가독성 최적화 */
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Session State
if 'blocked_list' not in st.session_state:
    st.session_state.blocked_list = []

def safe_int(val):
    if pd.isna(val) or val is None: return 0
    val_str = str(val).replace('%', '').strip()
    try: return int(float(val_str))
    except ValueError: return 0

# 3. 데이터 로딩
@st.cache_data
def load_all_data():
    df_evo = pd.read_csv('Digivolutions.xls', sep=';').dropna(subset=['Digivolves from', 'Digivolves to'])
    df_digimon = pd.read_csv('Digimon.xls', sep=';')
    df_req = pd.read_csv('Digivolution Requirements.xls', sep=';')
    
    stage_map = dict(zip(df_digimon['Digimon'], df_digimon['Stage']))
    attr_map = dict(zip(df_digimon['Digimon'], df_digimon['Attribute']))
    
    req_map = {}
    for _, row in df_req.iterrows():
        digimon_name = str(row['Digimon']).strip()
        req_map[digimon_name] = {
            'Level': safe_int(row.get('Level')),
            'HP': safe_int(row.get('HP')),
            'SP': safe_int(row.get('SP')),
            'ATK': safe_int(row.get('ATK')),
            'DEF': safe_int(row.get('DEF')),
            'INT': safe_int(row.get('INT')),
            'SPD': safe_int(row.get('SPD')),
            'ABI': safe_int(row.get('ABI')),
            'CAM': safe_int(row.get('CAM')),
            'Extra': str(row.get('Extra Condition')).strip() if pd.notna(row.get('Extra Condition')) and str(row.get('Extra Condition')).strip() != 'nan' else None
        }
    
    g_undirected = {}
    digimon_set = set()
    
    for _, row in df_evo.iterrows():
        src = str(row['Digivolves from']).strip()
        dst = str(row['Digivolves to']).strip()
        digimon_set.update([src, dst])
        
        if src not in g_undirected: g_undirected[src] = []
        if dst not in g_undirected: g_undirected[dst] = []
        
        g_undirected[src].append((dst, 'Evolve'))
        g_undirected[dst].append((src, 'Devolve'))
        
    return sorted(list(digimon_set)), stage_map, attr_map, req_map, g_undirected

digimon_list, stage_map, attr_map, req_map, g_undirected = load_all_data()

STAGE_WEIGHTS = {
    'Baby': 1, 'In-Training': 1, 'Rookie': 2, 'Champion': 4,
    'Ultimate': 7, 'Mega': 12, 'Ultra': 20, 'Armor': 5
}

def find_optimal_path(graph, start, target, stage_map, blocked_devolve_set=set()):
    pq = [(0, start, [(start, 'Start', 0)])]
    visited = {}
    
    while pq:
        cost, curr, path = heapq.heappop(pq)
        
        if curr in visited and visited[curr] <= cost:
            continue
        visited[curr] = cost
        
        if curr == target:
            return cost, path
            
        for nxt, move_type in graph.get(curr, []):
            if move_type == 'Devolve' and nxt in blocked_devolve_set:
                continue
                
            edge_cost = 1 if move_type == 'Devolve' else STAGE_WEIGHTS.get(stage_map.get(nxt, 'Rookie'), 4)
            new_cost = cost + edge_cost
            
            if nxt not in visited or new_cost < visited[nxt]:
                heapq.heappush(pq, (new_cost, nxt, path + [(nxt, move_type, edge_cost)]))
                
    return None, None

def ban_digimon(mon_name):
    if mon_name not in st.session_state.blocked_list:
        st.session_state.blocked_list.append(mon_name)

def unban_digimon(mon_name):
    if mon_name in st.session_state.blocked_list:
        st.session_state.blocked_list.remove(mon_name)

def reset_blocked():
    st.session_state.blocked_list = []

# --- 사이드바 ---
st.sidebar.markdown("<h3 style='color:#38bdf8; font-family:Orbitron; font-size:1.1rem;'>🚫 UNDISCOVERED</h3>", unsafe_allow_html=True)
if st.session_state.blocked_list:
    for b_mon in list(st.session_state.blocked_list):
        sb1, sb2 = st.sidebar.columns([3, 2])
        with sb1:
            st.markdown(f"<div style='padding-top:6px; color:#cbd5e1; font-size:0.88rem;'>• {b_mon}</div>", unsafe_allow_html=True)
        with sb2:
            st.button("🟢 Unban", key=f"unban_sb_{b_mon}", on_click=unban_digimon, args=(b_mon,))
    st.sidebar.markdown("---")
    st.sidebar.button("🔄 Reset All Banned", on_click=reset_blocked, use_container_width=True)
else:
    st.sidebar.info("No Digimon banned.\nClick [🚫 BAN] on devolution steps to auto-reroute!")

# --- 메인 헤더 ---
st.markdown("""
<div class="hero-banner">
    <div>
        <div class="hero-title">DIGIMON CYBER SLEUTH</div>
        <div style="color:#94a3b8; font-size:0.82rem; margin-top:4px;">Effort-Weighted Shortest Path Solver</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 검색 입력 컨트롤
c1, c2 = st.columns(2)
with c1:
    start_mon = st.selectbox("🎯 START DIGIMON", digimon_list, index=digimon_list.index("Keramon") if "Keramon" in digimon_list else 0)
with c2:
    target_mon = st.selectbox("🏁 TARGET DIGIMON", digimon_list, index=digimon_list.index("Angewomon") if "Angewomon" in digimon_list else 1)

if start_mon == target_mon:
    st.warning("Start and Target Digimon are identical.")
else:
    blocked_set = set(st.session_state.blocked_list)
    cost_opt, path_opt = find_optimal_path(g_undirected, start_mon, target_mon, stage_map, blocked_set)
    
    if path_opt:
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        # 요약 메트릭
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Total Steps", f"{len(path_opt)-1} Steps")
        with m2:
            st.metric("Effort Cost Score", f"{cost_opt} Pts")
            
        st.markdown("<hr style='border-color:rgba(56, 189, 248, 0.15); margin:16px 0 24px 0;'>", unsafe_allow_html=True)
        
        # 슬림 세로 타임라인 렌더링
        for idx, (mon, move, c) in enumerate(path_opt):
            stg = stage_map.get(mon, 'Unknown')
            attr = attr_map.get(mon, 'Neutral')
            
            # 커넥터 라인 (화살표 대체)
            if idx > 0:
                st.markdown("""
                <div class="path-connector">
                    <div class="path-line"></div>
                    <div class="path-dot"></div>
                </div>
                """, unsafe_allow_html=True)
            
            # 노드 카드 렌더링
            if idx == 0:
                st.markdown(f"""
                <div class="step-card step-card-start">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="color:#38bdf8; font-family:'Orbitron'; font-size:0.7rem; font-weight:800; letter-spacing:1px;">STARTING POINT</span>
                            <div style="margin-top:2px;">
                                <span class="digimon-title">{mon}</span>
                                <span class="badge badge-stage">{stg}</span>
                                <span class="badge badge-attr">{attr}</span>
                            </div>
                        </div>
                        <span class="step-label">STEP 0</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                card_col, btn_col = st.columns([6, 1])
                
                with card_col:
                    badge_label = "▲ EVOLVE" if move == "Evolve" else "▼ DEVOLVE"
                    badge_color = "#10b981" if move == "Evolve" else "#60a5fa"
                    card_type = "step-card-evo" if move == "Evolve" else "step-card-dev"
                    
                    # 스탯 태그
                    req_chips = ""
                    if move == "Evolve":
                        req = req_map.get(mon, {})
                        items = []
                        if req.get('Level', 0) > 0: items.append(f"LV {req['Level']}")
                        if req.get('HP', 0) > 0: items.append(f"HP {req['HP']}")
                        if req.get('SP', 0) > 0: items.append(f"SP {req['SP']}")
                        if req.get('ATK', 0) > 0: items.append(f"ATK {req['ATK']}")
                        if req.get('DEF', 0) > 0: items.append(f"DEF {req['DEF']}")
                        if req.get('INT', 0) > 0: items.append(f"INT {req['INT']}")
                        if req.get('SPD', 0) > 0: items.append(f"SPD {req['SPD']}")
                        if req.get('ABI', 0) > 0: items.append(f"ABI {req['ABI']}")
                        if req.get('CAM', 0) > 0: items.append(f"CAM {req['CAM']}%")
                        
                        chips = "".join([f'<span class="req-chip">{i}</span>' for i in items])
                        if req.get('Extra'):
                            chips += f'<span class="req-chip req-chip-extra">★ {req["Extra"]}</span>'
                        if chips:
                            req_chips = f'<div class="req-container">{chips}</div>'
                    
                    st.markdown(f"""
                    <div class="step-card {card_type}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="color:{badge_color}; font-family:'Orbitron'; font-size:0.72rem; font-weight:800; margin-right:8px;">{badge_label}</span>
                                <span class="digimon-title">{mon}</span>
                                <span class="badge badge-stage">{stg}</span>
                                <span class="badge badge-attr">{attr}</span>
                            </div>
                            <span class="step-label">STEP {idx} <span style="color:#64748b; font-size:0.75rem;">(+{c} Pts)</span></span>
                        </div>
                        {req_chips}
                    </div>
                    """, unsafe_allow_html=True)
                
                with btn_col:
                    if move == "Devolve":
                        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                        st.button("🚫 BAN", key=f"ban_{mon}_{idx}", on_click=ban_digimon, args=(mon,), use_container_width=True)
    else:
        st.error("❌ No path found with current devolution restrictions. Try unbanning some Digimon from the sidebar!")