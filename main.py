import streamlit as st
import time
import random
import math

st.set_page_config(
    page_title="거지 탈출 RPG",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 게임 데이터
# ============================================================

STAGES = [
    {
        "name": "시골 탈출",
        "place": "시골",
        "goal": 1_000_000,
        "desc": "시골에서 돈을 모아 도시로 탈출하자",
        "emoji": "🌾",
    },
    {
        "name": "길거리 탈출",
        "place": "길거리 인도",
        "goal": 5_000_000,
        "desc": "길거리에서 돈을 모아 서울역으로 가자",
        "emoji": "🚶",
    },
    {
        "name": "서울역 탈출",
        "place": "서울역",
        "goal": 50_000_000,
        "desc": "서울역을 벗어날 만큼 돈을 모으자",
        "emoji": "🚉",
    },
    {
        "name": "반지하 탈출",
        "place": "반지하",
        "goal": 250_000_000,
        "desc": "반지하 생활에서 탈출하자",
        "emoji": "🏠",
    },
    {
        "name": "1층집 탈출",
        "place": "지방 도시의 아파트",
        "goal": 1_250_000_000,
        "desc": "12억 5천만 원을 모으면 최종 탈출!",
        "emoji": "🏢",
    },
]

SHOP_ITEMS = [
    {
        "name": "손재주",
        "desc": "클릭당 수입 +1,000원",
        "type": "money",
    },
    {
        "name": "두 손",
        "desc": "한 번 클릭할 때 1회 추가 클릭",
        "type": "click",
    },
    {
        "name": "돈 냄새",
        "desc": "클릭당 수입 +1,000원",
        "type": "money",
    },
    {
        "name": "빠른 손",
        "desc": "한 번 클릭할 때 1회 추가 클릭",
        "type": "click",
    },
]

# ============================================================
# 상태 초기화
# ============================================================

def init_game():
    if "money" not in st.session_state:
        st.session_state.money = 0

    if "stage" not in st.session_state:
        st.session_state.stage = 0

    if "click_power" not in st.session_state:
        st.session_state.click_power = 1_000

    if "extra_clicks" not in st.session_state:
        st.session_state.extra_clicks = 0

    if "shop_levels" not in st.session_state:
        st.session_state.shop_levels = [0, 0, 0, 0]

    if "floating_texts" not in st.session_state:
        st.session_state.floating_texts = []

    if "sound" not in st.session_state:
        st.session_state.sound = False

    if "clear" not in st.session_state:
        st.session_state.clear = False

    if "notice" not in st.session_state:
        st.session_state.notice = ""

    if "last_click" not in st.session_state:
        st.session_state.last_click = 0


def reset_game():
    st.session_state.money = 0
    st.session_state.stage = 0
    st.session_state.click_power = 1_000
    st.session_state.extra_clicks = 0
    st.session_state.shop_levels = [0, 0, 0, 0]
    st.session_state.floating_texts = []
    st.session_state.sound = False
    st.session_state.clear = False
    st.session_state.notice = ""
    st.session_state.last_click = 0


init_game()

# ============================================================
# 계산
# ============================================================

def money_text(value):
    return f"{value:,}원"


def upgrade_cost(level):
    return int(1000 * (1.5 ** level))


def current_click_income():
    return st.session_state.click_power * (1 + st.session_state.extra_clicks)


def buy_upgrade(index):
    level = st.session_state.shop_levels[index]
    cost = upgrade_cost(level)

    if st.session_state.money < cost:
        st.session_state.notice = "돈이 부족합니다"
        return

    st.session_state.money -= cost
    st.session_state.shop_levels[index] += 1

    item_type = SHOP_ITEMS[index]["type"]

    if item_type == "money":
        st.session_state.click_power += 1_000
    else:
        st.session_state.extra_clicks += 1

    st.session_state.notice = f"{SHOP_ITEMS[index]['name']} 업그레이드 완료!"


def perform_click():
    # 클릭 1회 + 추가 클릭 능력
    income = current_click_income()
    st.session_state.money += income

    # +금액 표시
    st.session_state.floating_texts.append(
        {
            "text": f"+{money_text(income)}",
            "time": time.time(),
        }
    )

    # 효과음 활성화
    st.session_state.sound = True
    st.session_state.last_click = time.time()

    # 스테이지 클리어 체크
    current_goal = STAGES[st.session_state.stage]["goal"]

    if st.session_state.money >= current_goal:
        if st.session_state.stage < len(STAGES) - 1:
            st.session_state.stage += 1
            st.session_state.notice = (
                f"STAGE CLEAR!  {STAGES[st.session_state.stage]['name']}"
            )
        else:
            st.session_state.clear = True
            st.session_state.notice = "최종 탈출 성공!"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Nunito:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Jua', 'Nunito', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 20% 10%, rgba(255,255,255,.45) 0 3%, transparent 4%),
        linear-gradient(#f5e7c8, #e8d2a8);
}

.block-container {
    max-width: 720px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.game-title {
    text-align: center;
    font-size: 3.1rem;
    font-weight: 900;
    color: #3b3025;
    text-shadow: 3px 3px 0 #fff5dc;
    margin-bottom: 0;
}

.game-subtitle {
    text-align: center;
    color: #756451;
    font-size: 1.05rem;
    margin-bottom: 1.2rem;
}

.location-card {
    border: 4px solid #44372b;
    border-radius: 22px;
    padding: 18px;
    background: rgba(255,250,238,.92);
    box-shadow: 6px 6px 0 #44372b;
    margin-bottom: 18px;
}

.location-name {
    text-align: center;
    font-size: 1.9rem;
    font-weight: 900;
    color: #44372b;
}

.location-desc {
    text-align: center;
    color: #766653;
    margin-top: 4px;
}

.money-card {
    background: #fff9e9;
    border: 4px solid #44372b;
    border-radius: 22px;
    padding: 20px;
    text-align: center;
    box-shadow: 6px 6px 0 #44372b;
    margin-bottom: 14px;
}

.money-label {
    color: #776752;
    font-size: 1rem;
}

.money-value {
    color: #3b3025;
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -1px;
}

.stat-row {
    display: flex;
    gap: 10px;
    margin: 12px 0;
}

.stat {
    flex: 1;
    background: #fff9e9;
    border: 2px solid #554536;
    border-radius: 14px;
    padding: 10px;
    text-align: center;
}

.stat-title {
    font-size: .85rem;
    color: #806f5c;
}

.stat-value {
    font-size: 1.15rem;
    font-weight: 900;
    color: #3d3025;
}

.click-area {
    background: #d5b98c;
    border: 4px solid #44372b;
    border-radius: 26px;
    padding: 20px;
    box-shadow: 7px 7px 0 #44372b;
    margin: 20px 0;
}

.click-guide {
    text-align: center;
    color: #5f4f3d;
    margin-bottom: 10px;
    font-size: 1rem;
}

.floating {
    text-align: center;
    min-height: 45px;
    font-size: 2rem;
    font-weight: 900;
    color: #b46a10;
    animation: fadeUp 1s ease-out forwards;
}

@keyframes fadeUp {
    0% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-35px); }
}

.shop-title {
    font-size: 1.8rem;
    color: #44372b;
    font-weight: 900;
    margin-top: 20px;
}

.shop-card {
    background: #fff9e9;
    border: 3px solid #554536;
    border-radius: 17px;
    padding: 13px;
    margin: 8px 0;
}

.shop-name {
    font-size: 1.25rem;
    font-weight: 900;
    color: #3e3024;
}

.shop-desc {
    color: #756451;
    font-size: .95rem;
}

.clear-box {
    background: #fff2a8;
    border: 5px solid #44372b;
    border-radius: 25px;
    padding: 30px;
    text-align: center;
    font-size: 2rem;
    font-weight: 900;
    box-shadow: 7px 7px 0 #44372b;
    margin: 20px 0;
}

.notice {
    text-align: center;
    font-size: 1.15rem;
    font-weight: 900;
    color: #a55708;
    min-height: 30px;
    margin: 8px 0;
}

div.stButton > button {
    border: 3px solid #44372b;
    border-radius: 15px;
    font-family: 'Jua', sans-serif;
    font-weight: 900;
    background: #fff9e9;
    color: #3e3024;
    min-height: 48px;
}

div.stButton > button:hover {
    border-color: #2e241c;
    color: #2e241c;
}

.click-button button {
    min-height: 135px !important;
    font-size: 2rem !important;
    background: #f7c65d !important;
    box-shadow: 5px 5px 0 #44372b;
}

.click-button button:active {
    transform: translate(4px, 4px);
    box-shadow: 1px 1px 0 #44372b;
}

.stProgress > div > div > div > div {
    border-radius: 20px;
}

hr {
    border-color: #8f7b62;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 상단
# ============================================================

st.markdown('<div class="game-title">거지 탈출 RPG</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="game-subtitle">클릭해서 돈을 모으고 더 나은 곳으로 탈출하자</div>',
    unsafe_allow_html=True,
)

stage = STAGES[st.session_state.stage]

st.markdown(
    f"""
<div class="location-card">
    <div class="location-name">
        {stage['emoji']} STAGE {st.session_state.stage + 1} · {stage['name']}
    </div>
    <div class="location-desc">
        현재 장소: {stage['place']}<br>
        {stage['desc']}
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 돈
# ============================================================

st.markdown(
    f"""
<div class="money-card">
    <div class="money-label">현재 보유 금액</div>
    <div class="money-value">{money_text(st.session_state.money)}</div>
</div>
""",
    unsafe_allow_html=True,
)

progress = min(st.session_state.money / stage["goal"], 1.0)
st.progress(
    progress,
    text=f"목표 {money_text(stage['goal'])} · {progress * 100:.1f}%",
)

# ============================================================
# 능력치
# ============================================================

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"""
<div class="stat">
    <div class="stat-title">클릭당 수입</div>
    <div class="stat-value">{money_text(st.session_state.click_power)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
<div class="stat">
    <div class="stat-title">실제 클릭 횟수</div>
    <div class="stat-value">{1 + st.session_state.extra_clicks}회</div>
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# 클릭 영역
# ============================================================

st.markdown('<div class="click-area">', unsafe_allow_html=True)

# 최근 +금액을 보여주고 1초 후 사라지는 느낌
recent = st.session_state.floating_texts[-1:] if st.session_state.floating_texts else []

if recent:
    item = recent[0]
    if time.time() - item["time"] < 1.0:
        st.markdown(
            f'<div class="floating">{item["text"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="floating">&nbsp;</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="floating">&nbsp;</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="click-guide">아래 버튼을 눌러 돈을 벌자</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="click-button">', unsafe_allow_html=True)

if st.button(
    f"돈 벌기\n+{money_text(current_click_income())}",
    use_container_width=True,
):
    perform_click()
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 효과음
# 브라우저에서 Web Audio API를 이용해 짧은 동전 느낌의 음을 생성
# ============================================================

if st.session_state.sound:
    st.components.v1.html(
        """
        <script>
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            const ctx = new AudioContext();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "sine";
            osc.frequency.setValueAtTime(900, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(
                1450, ctx.currentTime + 0.07
            );

            gain.gain.setValueAtTime(0.0001, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(
                0.12, ctx.currentTime + 0.01
            );
            gain.gain.exponentialRampToValueAtTime(
                0.0001, ctx.currentTime + 0.18
            );

            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.2);
        }
        </script>
        """,
        height=0,
    )
    st.session_state.sound = False

# ============================================================
# 안내
# ============================================================

if st.session_state.notice:
    st.markdown(
        f'<div class="notice">{st.session_state.notice}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# 상점
# ============================================================

st.markdown('<div class="shop-title">상점</div>', unsafe_allow_html=True)

for i, item in enumerate(SHOP_ITEMS):
    level = st.session_state.shop_levels[i]
    cost = upgrade_cost(level)

    st.markdown(
        f"""
<div class="shop-card">
    <div class="shop-name">{item['name']} · Lv.{level}</div>
    <div class="shop-desc">{item['desc']}</div>
    <div class="shop-desc">
        다음 업그레이드 비용: <b>{money_text(cost)}</b>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button(
        f"{item['name']} 업그레이드 · {money_text(cost)}",
        key=f"shop_{i}",
        use_container_width=True,
    ):
        buy_upgrade(i)
        st.rerun()

# ============================================================
# 최종 클리어
# ============================================================

if st.session_state.clear:
    st.markdown(
        """
<div class="clear-box">
    최종 탈출 성공!<br>
    12억 5천만 원을 모았습니다<br>
    <span style="font-size:1rem;">이제 진짜 탈출이다</span>
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# 초기화
# ============================================================

st.divider()

if st.button("게임 초기화", use_container_width=True):
    reset_game()
    st.rerun()

st.caption(
    "업그레이드 비용은 1,000원부터 시작하며 업그레이드할 때마다 50%씩 증가합니다"
)
