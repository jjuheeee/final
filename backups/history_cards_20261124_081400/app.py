import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
from uuid import uuid4

st.set_page_config(
    page_title="DBD LAB",
    page_icon="💀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 커스텀 디자인 적용
css_path = Path("assets/style.css")

if css_path.exists():
    st.markdown(
        "<style>" + css_path.read_text(encoding="utf-8") + "</style>",
        unsafe_allow_html=True
    )

# 기본 데이터 불러오기
DATA = Path("data")

survivors = pd.read_csv(DATA / "survivors.csv")["name"].tolist()
killers = pd.read_csv(DATA / "killers.csv")["name"].tolist()
maps = pd.read_csv(DATA / "maps.csv")["name"].tolist()
perks = pd.read_csv(DATA / "perks.csv")

# 경기 기록 저장 파일
with st.sidebar:
    dataset = st.selectbox(
        "데이터 모드",
        ["내 경기 기록", "발표용 가상 데이터"]
    )

MATCH_FILE = DATA / (
    "demo_matches.csv"
    if dataset == "발표용 가상 데이터"
    else "matches.csv"
)

if dataset == "발표용 가상 데이터":
    st.warning(
        "DEMO MODE | 발표용 가상 경기 데이터를 표시하고 있습니다."
    )

columns = [
    "id", "date", "time", "mode", "character",
    "opponent", "map", "perks", "result",
    "chase", "generators", "rescues", "kills",
    "hooks", "party", "condition", "memo"
]

if not MATCH_FILE.exists():
    pd.DataFrame(columns=columns).to_csv(
        MATCH_FILE, index=False, encoding="utf-8-sig"
    )

matches = pd.read_csv(MATCH_FILE)

# 사이드바
with st.sidebar:
    st.title("💀 DBD LAB")
    st.caption("DEAD BY DAYLIGHT ANALYTICS")
    st.divider()

    mode = st.segmented_control(
        "플레이 유형",
        ["생존자", "살인마"],
        default="생존자",
        selection_mode="single",
        key="play_mode"
    ) or "생존자"

    st.divider()
    st.caption("MENU")

    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "홈"

    menu_items = [
        ("홈", ":material/dashboard:"),
        ("경기 기록", ":material/edit_note:"),
        ("경기 내역", ":material/history:"),
        ("플레이 패턴 분석", ":material/monitoring:"),
        ("캐릭터 및 퍽 분석", ":material/groups:"),
        ("맞춤형 리포트", ":material/assignment:")
    ]

    for name, icon in menu_items:
        if st.button(
            name,
            icon=icon,
            key=f"nav_{name}",
            width="stretch",
            type="primary" if st.session_state.selected_menu == name else "secondary"
        ):
            st.session_state.selected_menu = name
            st.rerun()

    menu = st.session_state.selected_menu


filtered = matches[matches["mode"] == mode].copy()




def character_picker(options, key, role, label, show_grid=False):
    state_key = f"{key}_selected"
    open_key = f"{key}_open"

    if st.session_state.get(state_key) not in options:
        st.session_state[state_key] = options[0]

    if open_key not in st.session_state:
        st.session_state[open_key] = False

    current = st.session_state[state_key]

    if not show_grid:
        st.markdown("""
        <style>
        div[class*="st-key-charcard_"] {
            background: rgba(24,24,28,0.88);
            border: 1px solid #38383d;
            border-radius: 5px;
            padding: 6px;
            transition: all 0.2s ease;
        }

        div[class*="st-key-charcard_"]:hover {
            border-color: #d62828;
            box-shadow: 0 0 14px #8b202066;
            background: #30191d;
        }

        div[class*="st-key-charcard_selected_"] {
            border: 1px solid #e53935;
            background: #35191d;
            box-shadow: 0 0 12px #c6282855;
        }

        div[class*="st-key-charcard_"] button {
            min-height: 48px;
            padding: 4px;
            white-space: normal;
        }

        div[class*="st-key-charcard_"] button p {
            font-size: 12px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.subheader(label)

        with st.container(border=True):
            a, b = st.columns([1, 2])

            with a:
                image = Path("assets/characters") / f"{current}.png"

                if image.exists():
                    st.image(str(image), width=120)
                else:
                    st.caption("NO IMAGE")

            with b:
                st.caption(
                    "SELECTED SURVIVOR"
                    if role == "생존자"
                    else "SELECTED KILLER"
                )

                st.subheader(current)

                if st.button(
                    "목록 닫기"
                    if st.session_state[open_key]
                    else f"{role} 변경",
                    key=f"{key}_toggle",
                    width="stretch"
                ):
                    st.session_state[open_key] = not st.session_state[open_key]
                    st.rerun()

    if show_grid and st.session_state[open_key]:
        st.divider()
        st.subheader(f"{role} 선택")

        search = st.text_input(
            f"{role} 검색",
            placeholder="캐릭터 이름을 입력하세요",
            key=f"{key}_search"
        )

        visible = [
            name for name in options
            if search.replace(" ", "").lower()
            in name.replace(" ", "").lower()
        ]

        if not visible:
            st.info("검색 결과가 없습니다.")

        for i in range(0, len(visible), 8):
            cols = st.columns(8)

            for col, name in zip(cols, visible[i:i+8]):
                with col:
                    selected = current == name

                    prefix = (
                        "charcard_selected_"
                        if selected else "charcard_"
                    )

                    with st.container(
                        key=f"{prefix}{key}_{options.index(name)}"
                    ):
                        image = Path("assets/characters") / f"{name}.png"

                        if image.exists():
                            st.image(str(image), width="stretch")
                        else:
                            st.caption("NO IMAGE")

                        if st.button(
                            name,
                            key=f"{key}_pick_{name}",
                            width="stretch",
                            type="primary" if selected else "secondary"
                        ):
                            st.session_state[state_key] = name
                            st.session_state[open_key] = False
                            st.rerun()

    return st.session_state[state_key]




def map_picker(key):

    import base64
    import html

    maps_data = pd.read_csv(
        "data/maps_clean.csv",
        keep_default_na=False
    )

    maps_data = maps_data.sort_values(
        ["realm", "name"]
    )

    selected_key = f"{key}_selected"
    opened_key = f"{key}_opened"

    if selected_key not in st.session_state:
        st.session_state[selected_key] = ""

    if opened_key not in st.session_state:
        st.session_state[opened_key] = False

    def render_map(path):
        if path and Path(path).is_file():
            encoded = base64.b64encode(
                Path(path).read_bytes()
            ).decode("utf-8")

            st.markdown(
                f'<img src="data:image/png;base64,{encoded}" '
                'style="width:100%;aspect-ratio:16/9;'
                'object-fit:cover;display:block;'
                'margin:auto;border-radius:6px;">',
                unsafe_allow_html=True
            )

    st.markdown("""
    <style>
    div[class*="st-key-mapcard_"] {
        background: #19171e;
        border: 1px solid #39323f;
        border-radius: 8px;
        padding: 10px;
        transition: 0.2s ease;
    }

    div[class*="st-key-mapcard_"]:hover {
        border-color: #a578dc;
        box-shadow: 0 0 15px #8054aa55;
    }

    div[class*="st-key-mapcard_selected_"] {
        background: #332143;
        border: 1px solid #bd8cff;
    }

    div[class*="st-key-mapcard_selected_"] button {
        background: #67408c !important;
        border-color: #b78cdb !important;
    }

    div[class*="st-key-mapcard_"] button {
        min-height: 60px;
    }

    div[class*="st-key-mapcard_"] p {
        text-align: center;
        word-break: keep-all;
    }

    div[class*="st-key-map_selected_"] {
        background: #21192b;
        border: 1px solid #59436e;
        border-radius: 8px;
        padding: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("플레이 맵")

    selected = st.session_state[selected_key]

    found = maps_data[
        maps_data["map_id"] == selected
    ]

    with st.container(key=f"map_selected_{key}"):

        if not found.empty:

            row = found.iloc[0]

            a, b = st.columns([1, 2])

            with a:
                render_map(row["image"])

            with b:
                st.caption("SELECTED MAP")
                st.markdown(
                    f"### {row['name']}"
                )
                st.caption(row["realm"])

        elif selected == "기타":
            st.write("기타")

        else:
            st.caption("아직 선택된 맵이 없습니다.")

        if st.button(
            "맵 선택 목록 닫기"
            if st.session_state[opened_key]
            else "＋ 맵 선택하기",
            key=f"{key}_toggle",
            width="stretch"
        ):
            st.session_state[opened_key] = (
                not st.session_state[opened_key]
            )
            st.rerun()

    if st.session_state[opened_key]:

        a, b = st.columns([1, 2])

        with a:
            realm = st.selectbox(
                "지역 선택",
                ["전체 지역"] +
                sorted(maps_data["realm"].unique()),
                key=f"{key}_realm",
                on_change=lambda: st.session_state.update({f"{key}_page": 0})
            )

        with b:
            search = st.text_input(
                "맵 검색",
                placeholder="지역 또는 맵 이름 입력",
                key=f"{key}_search",
                on_change=lambda: st.session_state.update({f"{key}_page": 0})
            )

        visible = maps_data.copy()

        if realm != "전체 지역":
            visible = visible[
                visible["realm"] == realm
            ]

        if search:
            term = search.replace(" ", "").lower()

            visible = visible[
                visible["name"].str.replace(
                    " ", ""
                ).str.lower().str.contains(
                    term, regex=False
                ) |
                visible["realm"].str.replace(
                    " ", ""
                ).str.lower().str.contains(
                    term, regex=False
                )
            ]

        st.caption(f"{len(visible)} MAPS")

        if visible.empty:
            st.info("검색 결과가 없습니다.")


        page_size = 16
        page_key = f"{key}_page"

        records = visible.to_dict("records")
        pages = max(1, (len(records)+page_size-1)//page_size)

        page = min(
            st.session_state.get(page_key, 0),
            pages-1
        )

        st.session_state[page_key] = page

        prev, center, nxt = st.columns([1, 2, 1])

        with prev:
            if st.button(
                "◀ 이전",
                key=f"{key}_prev",
                disabled=page == 0,
                width="stretch"
            ):
                st.session_state[page_key] -= 1
                st.rerun()

        with center:
            st.markdown(
                f'<div style="text-align:center;padding:10px;">'
                f'{page+1} / {pages} PAGE</div>',
                unsafe_allow_html=True
            )

        with nxt:
            if st.button(
                "다음 ▶",
                key=f"{key}_next",
                disabled=page >= pages-1,
                width="stretch"
            ):
                st.session_state[page_key] += 1
                st.rerun()

        records = records[
            page*page_size:(page+1)*page_size
        ]

        for start in range(0, len(records), 4):

            cols = st.columns(4)

            for col, row in zip(
                cols, records[start:start+4]
            ):

                active = selected == row["map_id"]

                prefix = (
                    "mapcard_selected_"
                    if active
                    else "mapcard_"
                )

                with col:
                    with st.container(
                        key=f"{prefix}{key}_{row['map_id']}"
                    ):

                        render_map(row["image"])

                        region_name = html.escape(
                            row["realm"]
                        )

                        st.markdown(
                            f'<div style="text-align:center;'
                            f'font-size:12px;color:#b99bdb;'
                            f'min-height:20px;">'
                            f'{region_name}</div>',
                            unsafe_allow_html=True
                        )

                        if st.button(
                            row["name"],
                            key=f"{key}_pick_{row['map_id']}",
                            help=row["description"] or None,
                            type="primary" if active else "secondary",
                            width="stretch"
                        ):
                            st.session_state[selected_key] = row["map_id"]
                            st.session_state[opened_key] = False
                            st.rerun()

        if st.button(
            "기타 맵",
            key=f"{key}_other",
            width="stretch"
        ):
            st.session_state[selected_key] = "기타"
            st.session_state[opened_key] = False
            st.rerun()

    if selected == "기타":
        return "기타"

    if not found.empty:
        return found.iloc[0]["name"]

    return ""

def perk_picker(perks, role, key):

    import base64

    def render_perk(path, size):
        encoded = base64.b64encode(
            Path(path).read_bytes()
        ).decode("utf-8")

        st.markdown(
            f'<div style="display:flex;justify-content:center;align-items:center;width:100%;">'
            f'<img src="data:image/png;base64,{encoded}" '
            f'style="width:{size}px;max-width:100%;height:auto;display:block;margin:0 auto;">'
            f'</div>',
            unsafe_allow_html=True
        )

    data = perks[perks["role"] == role].copy()
    data = data.drop_duplicates("name")

    options = data["name"].tolist()
    images = dict(zip(data["name"], data["styled_image"]))
    descriptions = dict(zip(data["name"], data["clean_description"]))

    state = f"{key}_selected"
    opened = f"{key}_open"
    page_key = f"{key}_page"

    if state not in st.session_state:
        st.session_state[state] = []

    if opened not in st.session_state:
        st.session_state[opened] = False

    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    selected = [
        x for x in st.session_state[state]
        if x in options
    ]

    st.session_state[state] = selected

    st.markdown("""
    <style>
    div[class*="st-key-perkslot_"] {
        background: rgba(32,24,42,0.85);
        border: 1px solid #554068;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }

    div[class*="st-key-perkcard_"] {
        background: #19171e;
        border: 1px solid #39323f;
        border-radius: 6px;
        padding: 8px;
        transition: 0.2s ease;
    }

    div[class*="st-key-perkcard_"]:hover {
        border-color: #a578dc;
        box-shadow: 0 0 15px #8054aa55;
    }

    div[class*="st-key-perkcard_selected_"] {
        background: #332143;
        border: 1px solid #bd8cff;
        box-shadow: 0 0 12px #8054aa88;
    }

    div[class*="st-key-perkcard_"] button {
        min-height: 45px;
        padding: 4px;
    }

    div[class*="st-key-perkcard_"] button p {
        font-size: 12px;
    }
    
    div[class*="st-key-perk_add_"] button {
        min-height: 110px !important;
        background: transparent !important;
        border: 1px dashed #70558c !important;
        border-radius: 8px !important;
        color: #b99bdb !important;
        transition: all 0.2s ease;
    }

    div[class*="st-key-perk_add_"] button p {
        font-size: 38px !important;
        font-weight: 300 !important;
        color: #b99bdb !important;
    }

    div[class*="st-key-perk_add_"] button:hover {
        background: #352345 !important;
        border-color: #bd8cff !important;
        box-shadow: 0 0 18px #8054aa66;
    }

    div[class*="st-key-perkslot_"] p {
        text-align: center;
    }

    div[class*="st-key-perkslot_"] img {
        margin: auto;
    }


    div[class*="st-key-perkslot_"] {
        min-height: 245px !important;
    }

    div[class*="st-key-perkslot_"] p {
        text-align: center !important;
    }

    div[class*="st-key-perk_add_"] button {
        min-height: 180px !important;
    }

    div[class*="st-key-perkcard_selected_"] button {
        background: #67408c !important;
        border-color: #b78cdb !important;
        color: white !important;
    }

    div[class*="st-key-perkcard_"] button {
        min-height: 48px !important;
    }

    div[class*="st-key-perkcard_"] button p {
        text-align: center !important;
        word-break: keep-all !important;
    }
</style>
    """, unsafe_allow_html=True)

    st.subheader("사용한 퍽")
    st.caption(f"{len(selected)} / 4 SELECTED")

    cols = st.columns(4)

    for i, col in enumerate(cols):
        with col:
            with st.container(key=f"perkslot_{key}_{i}"):
                if i < len(selected):
                    name = selected[i]
                    path = Path(str(images.get(name, "")))

                    if path.is_file():
                        render_perk(path, 140)

                    st.write(name)

                    if st.button(
                        "선택 해제",
                        key=f"{key}_remove_{i}",
                        width="stretch"
                    ):
                        st.session_state[state].remove(name)
                        st.rerun()

                else:
                    if st.button(
                        "＋",
                        key=f"perk_add_{key}_{i}",
                        width="stretch",
                        help="퍽 선택 목록 열기"
                    ):
                        st.session_state[opened] = True
                        st.rerun()

                    st.caption(f"퍽 추가 {i+1}")

    if st.session_state[opened]:
        if st.button(
            "퍽 선택 목록 닫기",
            key=f"{key}_toggle",
            width="stretch"
        ):
            st.session_state[opened] = False
            st.rerun()

    if st.session_state[opened]:
        search = st.text_input(
            "퍽 검색",
            placeholder="퍽 이름을 입력하세요",
            key=f"{key}_search"
        )

        visible = [
            name for name in options
            if search.replace(" ", "").lower()
            in name.replace(" ", "").lower()
        ]

        page_size = 24
        pages = max(1, (len(visible)+page_size-1)//page_size)

        page = min(st.session_state[page_key], pages-1)
        st.session_state[page_key] = page

        a, b, c = st.columns([1, 2, 1])

        with a:
            if st.button(
                "이전",
                key=f"{key}_prev",
                disabled=page == 0,
                width="stretch"
            ):
                st.session_state[page_key] -= 1
                st.rerun()

        with b:
            st.markdown(
                f"<center>{page+1} / {pages} PAGE</center>",
                unsafe_allow_html=True
            )

        with c:
            if st.button(
                "다음",
                key=f"{key}_next",
                disabled=page >= pages-1,
                width="stretch"
            ):
                st.session_state[page_key] += 1
                st.rerun()

        visible = visible[
            page*page_size:(page+1)*page_size
        ]

        if not visible:
            st.info("검색 결과가 없습니다.")

        for start in range(0, len(visible), 8):
            cols = st.columns(8)

            for col, name in zip(cols, visible[start:start+8]):
                with col:
                    active = name in selected

                    prefix = (
                        "perkcard_selected_"
                        if active else "perkcard_"
                    )

                    with st.container(
                        key=f"{prefix}{key}_{options.index(name)}"
                    ):
                        path = Path(str(images.get(name, "")))

                        if path.is_file():
                            render_perk(path, 100)
                        else:
                            st.caption("NO IMAGE")

                        if st.button(
                            name, help=descriptions.get(name, ""),
                            key=f"{key}_pick_{name}",
                            type="primary" if active else "secondary",
                            disabled=len(selected)>=4 and not active,
                            width="stretch"
                        ):
                            if active:
                                st.session_state[state].remove(name)
                            else:
                                st.session_state[state].append(name)

                            if len(st.session_state[state]) == 4:
                                st.session_state[opened] = False

                            st.rerun()

    return st.session_state[state].copy()


# 홈 화면
if menu == "홈":
    st.markdown(
        """
        <div class="dbd-hero">
            <div class="dbd-hero-label">
                DEAD BY DAYLIGHT · PERSONAL ANALYTICS
            </div>
            <div class="dbd-hero-title">DBD LAB</div>
            <div class="dbd-hero-description">
                안개 속에서 살아남은 모든 순간을 기록하다.
            </div>
            <div class="dbd-hero-line"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()
    st.subheader(f"{mode} 플레이 대시보드")

    col1, col2, col3, col4 = st.columns(4)

    total = len(filtered)
    col1.metric("전체 경기", f"{total}회")

    main_character = (
        filtered["character"].mode().iloc[0]
        if total else "-"
    )

    if mode == "생존자":
        valid = filtered[
            filtered["result"] != "연결 종료"
        ]

        escape_rate = (
            (valid["result"] == "탈출").mean() * 100
            if len(valid) else 0
        )

        chase_avg = filtered["chase"].mean() if total else 0

        col2.metric("탈출률", f"{escape_rate:.1f}%")
        col3.metric("평균 추격 시간", f"{chase_avg:.0f}초")
        col4.metric("주력 생존자", main_character)

    else:
        kill_avg = filtered["kills"].mean() if total else 0

        four_k = (
            (filtered["kills"] == 4).mean() * 100
            if total else 0
        )

        col2.metric("평균 처치 수", f"{kill_avg:.1f}명")
        col3.metric("4킬 달성률", f"{four_k:.1f}%")
        col4.metric("주력 살인마", main_character)

    st.divider()

    if total == 0:
        st.info("경기 기록을 추가하면 분석 결과가 표시됩니다.")
    else:
        st.subheader("최근 경기 기록")
        st.dataframe(
            filtered.tail(5).iloc[::-1][
                ["date", "character", "map", "result"]
            ].rename(columns={
                "date": "날짜",
                "character": "캐릭터",
                "map": "맵",
                "result": "경기 결과"
            }),
            hide_index=True,
            use_container_width=True
        )

# 경기 기록
elif menu == "경기 기록":
    st.title("경기 기록하기")
    st.caption("NEW MATCH RECORD")
    st.divider()

    if mode == "생존자":
        left, right = st.columns(2)

        with left:
            picked_survivor = character_picker(
                survivors,
                "record_survivor",
                "생존자",
                "플레이 생존자"
            )

        with right:
            picked_killer = character_picker(
                killers,
                f"record_{mode}",
                "살인마",
                "상대 살인마"
            )

        picked_survivor = character_picker(
            survivors,
            "record_survivor",
            "생존자",
            "플레이 생존자",
            show_grid=True
        )

    else:
        picked_killer = character_picker(
            killers,
            f"record_{mode}",
            "살인마",
            "플레이 살인마"
        )

    picked_killer = character_picker(
        killers,
        f"record_{mode}",
        "살인마",
        "살인마 선택",
        show_grid=True
    )

    st.divider()

    selected_perks = perk_picker(
        perks,
        mode,
        f"record_perks_{mode}"
    )

    st.divider()

    selected_map = map_picker(f"record_map_{mode}")

    with st.form(f"match_form_{mode}"):

        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("플레이 날짜")
        with col2:
            time = st.time_input("플레이 시간")

        col1, col2 = st.columns(2)

        opponent = ""
        chase = 0
        generators = 0
        rescues = 0
        kills = 0
        hooks = 0
        party = "-"

        if mode == "생존자":
            with col1:
                character = picked_survivor
                st.write("플레이 생존자:", character)
            with col2:
                opponent = picked_killer
                st.write("상대 살인마:", opponent)
        else:
            character = picked_killer
            st.write("플레이 살인마:", character)


        perk_options = perks[
            perks["role"] == mode
        ]["name"].tolist()

        st.caption("선택한 퍽: " + (" / ".join(selected_perks) or "없음"))

        st.divider()
        st.subheader("경기 결과")

        if mode == "생존자":

            result = st.radio(
                "경기 결과",
                ["탈출", "희생", "사망", "연결 종료"],
                horizontal=True
            )

            party = st.radio(
                "파티 유형",
                ["솔큐", "2인큐", "3인큐", "4인큐"],
                horizontal=True
            )

            col1, col2, col3 = st.columns(3)

            chase = col1.number_input(
                "총 추격 시간 (초)",
                min_value=0, step=10
            )

            generator_count = col2.number_input(
                "발전기 수리 개수",
                min_value=0.0,
                value=0.0,
                step=0.5,
                format="%.2f",
                help="발전기 한 개 분량은 1.0, 절반은 0.5입니다."
            )

            generators = int(round(generator_count * 100))

            rescues = col3.number_input(
                "구조 횟수",
                min_value=0, step=1
            )

        else:

            kills = st.slider(
                "처치한 생존자 수", 0, 4, 0
            )

            hooks = st.number_input(
                "갈고리 횟수",
                min_value=0, max_value=12, step=1
            )

            result = f"{kills}킬"

        condition = st.select_slider(
            "플레이 컨디션",
            options=[
                "매우 나쁨", "나쁨", "보통",
                "좋음", "매우 좋음"
            ],
            value="보통"
        )

        memo = st.text_area(
            "경기 메모",
            placeholder="아쉬웠던 점이나 잘했던 점을 기록하세요."
        )

        submitted = st.form_submit_button(
            "경기 기록 저장",
            use_container_width=True,
            type="primary"
        )

    if submitted:

        new_match = {
            "id": str(uuid4()),
            "date": str(date),
            "time": str(time),
            "mode": mode,
            "character": character,
            "opponent": opponent,
            "map": selected_map or "기타",
            "perks": " | ".join(selected_perks),
            "result": result,
            "chase": chase,
            "generators": generators,
            "rescues": rescues,
            "kills": kills,
            "hooks": hooks,
            "party": party,
            "condition": condition,
            "memo": memo
        }

        pd.DataFrame([new_match]).to_csv(
            MATCH_FILE,
            mode="a",
            header=False,
            index=False,
            encoding="utf-8"
        )

        st.success("경기 기록이 저장되었습니다!")

# 경기 내역
elif menu == "경기 내역":
    st.title("나의 경기 내역")
    st.caption("MATCH HISTORY")
    if "notice" in st.session_state:
        st.success(st.session_state.pop("notice"))
    st.divider()

    if filtered.empty:
        st.info("아직 저장된 경기 기록이 없습니다.")
    else:
        st.metric("저장된 경기", f"{len(filtered)}회")

        display = filtered.drop(columns=["id"]).copy()

        display["generators"] = (
            pd.to_numeric(
                display["generators"],
                errors="coerce"
            ).fillna(0) / 100
        ).round(2)

        display = display.rename(columns={
            "date": "날짜",
            "time": "시간",
            "mode": "플레이 유형",
            "character": "캐릭터",
            "opponent": "상대 살인마",
            "map": "맵",
            "perks": "사용 퍽",
            "result": "결과",
            "chase": "추격 시간",
            "generators": "발전기 수리 개수",
            "rescues": "구조 횟수",
            "kills": "처치 수",
            "hooks": "갈고리 횟수",
            "party": "파티 유형",
            "condition": "컨디션",
            "memo": "메모"
        })

        st.dataframe(
            display.iloc[::-1],
            hide_index=True,
            use_container_width=True
        )

        st.divider()
        st.subheader("경기 기록 관리")

        records = filtered.iloc[::-1].set_index("id")

        selected_id = st.selectbox(
            "수정하거나 삭제할 경기 선택",
            records.index.tolist(),
            format_func=lambda x: (
                f"{records.loc[x, 'date']} | "
                f"{records.loc[x, 'time']} | "
                f"{records.loc[x, 'character']} | "
                f"{records.loc[x, 'result']}"
            )
        )

        selected = records.loc[selected_id]

        edit_tab, delete_tab = st.tabs(
            ["기록 수정", "기록 삭제"]
        )

        with edit_tab:
            with st.form(f"edit_{selected_id}"):

                edit_date = st.date_input(
                    "경기 날짜",
                    value=pd.to_datetime(
                        selected["date"]
                    ).date()
                )

                edit_time = st.time_input(
                    "경기 시간",
                    value=pd.to_datetime(
                        str(selected["time"])
                    ).time()
                )

                character_options = (
                    survivors if mode == "생존자"
                    else killers
                )

                character_options = list(dict.fromkeys(
                    character_options + [selected["character"]]
                ))

                edit_character = st.selectbox(
                    "캐릭터",
                    character_options,
                    index=character_options.index(
                        selected["character"]
                    )
                )

                map_options = list(dict.fromkeys(
                    maps + [selected["map"]]
                ))

                edit_map = st.selectbox(
                    "맵",
                    map_options,
                    index=map_options.index(selected["map"])
                )

                perk_options = perks[
                    perks["role"] == mode
                ]["name"].tolist()

                current_perks = (
                    str(selected["perks"]).split(" | ")
                    if pd.notna(selected["perks"])
                    else []
                )

                perk_options = list(dict.fromkeys(
                    perk_options + current_perks
                ))

                edit_perks = st.multiselect(
                    "사용한 퍽",
                    perk_options,
                    default=current_perks,
                    max_selections=4
                )

                updates = {}

                if mode == "생존자":

                    opponent_options = list(dict.fromkeys(
                        killers + [selected["opponent"]]
                    ))

                    edit_opponent = st.selectbox(
                        "상대 살인마",
                        opponent_options,
                        index=opponent_options.index(
                            selected["opponent"]
                        )
                    )

                    results = [
                        "탈출", "희생", "사망", "연결 종료"
                    ]

                    edit_result = st.radio(
                        "경기 결과",
                        results,
                        index=results.index(selected["result"]),
                        horizontal=True
                    )

                    parties = [
                        "솔큐", "2인큐", "3인큐", "4인큐"
                    ]

                    edit_party = st.radio(
                        "파티 유형",
                        parties,
                        index=parties.index(selected["party"]),
                        horizontal=True
                    )

                    c1, c2, c3 = st.columns(3)

                    edit_chase = c1.number_input(
                        "추격 시간 (초)",
                        min_value=0,
                        value=int(selected["chase"])
                    )

                    edit_generator_count = c2.number_input(
                        "발전기 수리 개수",
                        min_value=0.0,
                        value=float(selected["generators"]) / 100,
                        step=0.5,
                        format="%.2f",
                        help="발전기 한 개 분량은 1.0, 절반은 0.5입니다."
                    )

                    edit_generators = int(
                        round(edit_generator_count * 100)
                    )

                    edit_rescues = c3.number_input(
                        "구조 횟수",
                        min_value=0,
                        value=int(selected["rescues"])
                    )

                    updates.update({
                        "opponent": edit_opponent,
                        "result": edit_result,
                        "party": edit_party,
                        "chase": edit_chase,
                        "generators": edit_generators,
                        "rescues": edit_rescues
                    })

                else:
                    edit_kills = st.slider(
                        "처치 수", 0, 4,
                        int(selected["kills"])
                    )

                    edit_hooks = st.number_input(
                        "갈고리 횟수",
                        min_value=0,
                        max_value=12,
                        value=int(selected["hooks"])
                    )

                    updates.update({
                        "kills": edit_kills,
                        "hooks": edit_hooks,
                        "result": f"{edit_kills}킬"
                    })

                conditions = [
                    "매우 나쁨", "나쁨", "보통",
                    "좋음", "매우 좋음"
                ]

                edit_condition = st.select_slider(
                    "플레이 컨디션",
                    options=conditions,
                    value=selected["condition"]
                )

                edit_memo = st.text_area(
                    "경기 메모",
                    value=str(selected["memo"])
                    if pd.notna(selected["memo"]) else ""
                )

                save_edit = st.form_submit_button(
                    "수정 내용 저장",
                    type="primary",
                    use_container_width=True
                )

            if save_edit:
                updates.update({
                    "date": str(edit_date),
                    "time": str(edit_time),
                    "character": edit_character,
                    "map": edit_map,
                    "perks": " | ".join(edit_perks),
                    "condition": edit_condition,
                    "memo": edit_memo
                })

                for key, value in updates.items():
                    matches[key] = matches[key].astype(object)
                    matches.loc[
                        matches["id"] == selected_id, key
                    ] = value

                matches.to_csv(
                    MATCH_FILE,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.session_state["notice"] = "경기 기록이 수정되었습니다."
                st.rerun()

        with delete_tab:
            st.warning(
                "삭제한 경기 기록은 복구할 수 없습니다."
            )

            confirm = st.checkbox(
                "선택한 경기 기록을 삭제하겠습니다.",
                key=f"confirm_{selected_id}"
            )

            if st.button(
                "경기 기록 삭제",
                disabled=not confirm,
                type="primary"
            ):
                matches = matches[
                    matches["id"] != selected_id
                ]

                matches.to_csv(
                    MATCH_FILE,
                    index=False,
                    encoding="utf-8-sig"
                )

                st.session_state["notice"] = "경기 기록이 삭제되었습니다."
                st.rerun()

        st.divider()

        st.download_button(
            "경기 기록 CSV 다운로드",
            data=filtered.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="dbd_matches.csv",
            mime="text/csv"
        )

elif menu == "플레이 패턴 분석":
    st.title("플레이 패턴 분석")
    st.caption("PLAY PATTERN ANALYTICS")
    st.divider()

    if filtered.empty:
        st.info("경기 기록을 먼저 추가해주세요.")

    else:
        df = filtered.copy()

        if mode == "생존자":
            df = df[df["result"] != "연결 종료"].copy()
            df["score"] = (
                df["result"] == "탈출"
            ).astype(int) * 100
            metric = "탈출률 (%)"
            upper = 100
        else:
            df["score"] = df["kills"]
            metric = "평균 처치 수"
            upper = 4

        if df.empty:
            st.info("분석 가능한 완료 경기가 없습니다.")
            st.stop()

        df["datetime"] = pd.to_datetime(
            df["date"].astype(str) + " " +
            df["time"].astype(str),
            errors="coerce"
        )

        df = df.sort_values("datetime")

        df["hour"] = df["datetime"].dt.hour

        def time_group(hour):
            if pd.isna(hour):
                return "미기록"
            if hour < 6:
                return "새벽 (00~06시)"
            elif hour < 12:
                return "오전 (06~12시)"
            elif hour < 18:
                return "오후 (12~18시)"
            else:
                return "저녁 (18~24시)"

        df["시간대"] = df["hour"].apply(time_group)

        weekdays = [
            "월요일", "화요일", "수요일",
            "목요일", "금요일", "토요일", "일요일"
        ]

        df["요일"] = df["datetime"].dt.dayofweek.map(
            dict(enumerate(weekdays))
        )

        st.metric("분석 대상 경기", f"{len(df)}회")

        if len(df) < 10:
            st.warning(
                "아직 경기 데이터가 부족합니다. "
                "현재 결과는 참고용으로 확인해주세요."
            )

        def draw_chart(column, title, order=None):

            summary = df.groupby(column).agg(
                성과=("score", "mean"),
                경기수=("score", "count")
            ).reset_index()

            summary["성과"] = summary["성과"].round(1)

            fig = px.bar(
                summary,
                x=column,
                y="성과",
                text="성과",
                color="성과",
                color_continuous_scale=[
                    "#592326", "#C62828", "#FF7373"
                ],
                hover_data=["경기수"],
                labels={"성과": metric},
                category_orders={
                    column: order
                } if order else {}
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#101012",
                plot_bgcolor="#101012",
                coloraxis_showscale=False,
                height=350,
                margin=dict(l=20, r=20, t=20, b=20)
            )

            fig.update_yaxes(range=[0, upper * 1.15])

            fig.update_traces(
                textposition="outside"
            )

            st.subheader(title)
            st.plotly_chart(
                fig,
                use_container_width=True
            )

        col1, col2 = st.columns(2)

        with col1:
            draw_chart(
                "시간대",
                "시간대별 플레이 성과",
                [
                    "새벽 (00~06시)",
                    "오전 (06~12시)",
                    "오후 (12~18시)",
                    "저녁 (18~24시)"
                ]
            )

        with col2:
            draw_chart(
                "요일",
                "요일별 플레이 성과",
                weekdays
            )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            draw_chart(
                "condition",
                "컨디션별 플레이 성과",
                [
                    "매우 나쁨", "나쁨", "보통",
                    "좋음", "매우 좋음"
                ]
            )

        with col2:
            if mode == "생존자":
                draw_chart(
                    "party",
                    "솔큐 및 다인큐 성과 비교",
                    ["솔큐", "2인큐", "3인큐", "4인큐"]
                )
            else:
                draw_chart(
                    "character",
                    "살인마별 평균 처치 수"
                )

        st.divider()
        st.subheader("최근 경기 성과 변화")

        recent = df.tail(30).copy()
        recent["경기"] = range(1, len(recent) + 1)

        recent["이동평균"] = recent["score"].rolling(
            5, min_periods=1
        ).mean()

        fig = px.line(
            recent,
            x="경기",
            y=["score", "이동평균"],
            markers=True,
            color_discrete_sequence=[
                "#C62828", "#E8B66A"
            ],
            labels={
                "value": metric,
                "variable": "구분"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#101012",
            plot_bgcolor="#101012",
            height=380
        )

        fig.update_yaxes(range=[0, upper * 1.1])

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            "이동평균은 최근 최대 5경기의 평균 성과입니다."
        )

        if mode == "생존자":
            st.divider()
            draw_chart(
                "opponent",
                "상대 살인마별 탈출률"
            )

elif menu == "캐릭터 및 퍽 분석":
    st.title("캐릭터 및 퍽 분석")
    st.caption("CHARACTER & PERK ANALYTICS")
    st.divider()

    df = filtered.copy()

    if mode == "생존자":
        df = df[df["result"] != "연결 종료"].copy()
        df["score"] = (
            df["result"] == "탈출"
        ).astype(int) * 100
        metric = "탈출률 (%)"
        upper = 100
    else:
        df["score"] = df["kills"]
        metric = "평균 처치 수"
        upper = 4

    if df.empty:
        st.info("분석할 경기 기록이 없습니다.")
        st.stop()

    st.metric("분석 대상 경기", f"{len(df)}회")

    if len(df) < 10:
        st.warning("경기 데이터가 부족하여 분석 결과는 참고용입니다.")

    min_games = st.slider(
        "최소 사용 경기 수",
        1, max(2, min(20, len(df))), 1
    )

    def analyze(data, column):
        summary = data.groupby(column).agg(
            경기수=("score", "count"),
            성과=("score", "mean")
        ).reset_index()

        summary = summary[
            summary["경기수"] >= min_games
        ].copy()

        summary["성과"] = summary["성과"].round(1)

        return summary.sort_values(
            ["성과", "경기수"],
            ascending=False
        )

    def chart(data, column, title, value, limit=None):

        st.subheader(title)

        if data.empty:
            st.info("조건에 해당하는 데이터가 없습니다.")
            return

        display = data.nlargest(15, value).sort_values(value)

        fig = px.bar(
            display,
            x=value,
            y=column,
            orientation="h",
            text=value,
            color_discrete_sequence=["#C62828"],
            hover_data=["경기수"],
            labels={
                "성과": metric,
                "character": "캐릭터",
                "map": "맵",
                "perk": "퍽",
                "build": "퍽 조합"
            }
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#101012",
            plot_bgcolor="#101012",
            height=max(320, len(display) * 42),
            margin=dict(l=20, r=40, t=20, b=20)
        )

        fig.update_traces(textposition="outside")

        if limit:
            fig.update_xaxes(range=[0, limit * 1.15])

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    tab1, tab2, tab3, tab4 = st.tabs([
        "캐릭터 분석",
        "퍽 분석",
        "퍽 조합 분석",
        "맵 분석"
    ])

    with tab1:

        character_stats = analyze(df, "character")

        c1, c2 = st.columns(2)

        with c1:
            chart(
                character_stats,
                "character",
                "캐릭터별 사용 횟수",
                "경기수"
            )

        with c2:
            chart(
                character_stats,
                "character",
                "캐릭터별 플레이 성과",
                "성과",
                upper
            )

        if mode == "생존자":
            extra = df.groupby("character").agg(
                평균추격시간=("chase", "mean"),
                평균발전기수리개수=("generators", lambda x: x.mean() / 100),
                평균구조횟수=("rescues", "mean")
            ).reset_index()
        else:
            extra = df.groupby("character").agg(
                평균갈고리횟수=("hooks", "mean"),
                평균처치수=("kills", "mean")
            ).reset_index()

        result_table = character_stats.merge(
            extra, on="character"
        ).round(1)

        st.subheader("캐릭터별 상세 통계")

        st.dataframe(
            result_table.rename(columns={
                "character": "캐릭터",
                "성과": metric
            }),
            hide_index=True,
            use_container_width=True
        )

    with tab2:

        perk_df = df.copy()

        perk_df["perk"] = (
            perk_df["perks"]
            .fillna("")
            .str.split(" | ", regex=False)
        )

        perk_df = perk_df.explode("perk")
        perk_df = perk_df[perk_df["perk"] != ""]

        perk_stats = analyze(perk_df, "perk")

        c1, c2 = st.columns(2)

        with c1:
            chart(
                perk_stats,
                "perk",
                "퍽별 사용 횟수",
                "경기수"
            )

        with c2:
            chart(
                perk_stats,
                "perk",
                "퍽별 플레이 성과",
                "성과",
                upper
            )

        st.subheader("퍽별 상세 통계")

        st.dataframe(
            perk_stats.rename(columns={
                "perk": "퍽 이름",
                "성과": metric
            }),
            hide_index=True,
            use_container_width=True
        )

        st.caption(
            "퍽별 성과는 해당 퍽을 사용한 경기의 평균이며, "
            "퍽 자체의 효과를 의미하지는 않습니다."
        )

    with tab3:

        build_df = df.copy()

        build_df["build"] = (
            build_df["perks"]
            .fillna("")
            .apply(
                lambda x: " + ".join(
                    sorted(x.split(" | "))
                ) if x else "퍽 미사용"
            )
        )

        build_stats = analyze(build_df, "build")

        chart(
            build_stats,
            "build",
            "퍽 조합별 플레이 성과",
            "성과",
            upper
        )

        st.dataframe(
            build_stats.rename(columns={
                "build": "퍽 조합",
                "성과": metric
            }),
            hide_index=True,
            use_container_width=True
        )

    with tab4:

        map_stats = analyze(df, "map")

        chart(
            map_stats,
            "map",
            "맵별 플레이 성과",
            "성과",
            upper
        )

        st.dataframe(
            map_stats.rename(columns={
                "map": "맵",
                "성과": metric
            }),
            hide_index=True,
            use_container_width=True
        )

elif menu == "맞춤형 리포트":
    st.title("맞춤형 플레이 리포트")
    st.caption("PERSONAL PERFORMANCE REPORT")
    st.divider()

    df = filtered.copy()

    if mode == "생존자":
        df = df[df["result"] != "연결 종료"].copy()
        df["score"] = (
            df["result"] == "탈출"
        ).astype(int) * 100
        unit = "%"
    else:
        df["score"] = df["kills"]
        unit = "명"

    if df.empty:
        st.info("경기 기록을 먼저 추가해주세요.")
        st.stop()

    total = len(df)
    avg = df["score"].mean()

    st.metric("분석 대상 경기", f"{total}회")

    st.progress(min(total / 30, 1.0))

    st.caption(
        f"권장 분석 데이터 확보량: {min(total, 30)}/30경기"
    )

    if total < 10:
        st.warning(
            "아직 데이터가 부족합니다. "
            "현재는 기초 통계만 제공하며 "
            "10경기 이상부터 맞춤 분석을 제공합니다."
        )

    st.divider()
    st.subheader("01. 나의 플레이 프로필")

    if mode == "생존자":

        chase = df["chase"].mean()
        gen = df["generators"].mean()
        rescue = df["rescues"].mean()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("탈출률", f"{avg:.1f}%")
        c2.metric("평균 추격", f"{chase:.0f}초")
        c3.metric("평균 발전기", f"{gen / 100:.2f}개")
        c4.metric("평균 구조", f"{rescue:.1f}회")

        if total >= 10:

            scores = {
                "어그로 중심형": chase / 120,
                "발전기 중심형": gen / 150,
                "팀 지원형": rescue / 2
            }

            style = max(scores, key=scores.get)

            st.success(f"나의 플레이 유형: {style}")

            descriptions = {
                "어그로 중심형":
                    "살인마의 시간을 소모시키는 플레이에 집중하는 유형입니다.",
                "발전기 중심형":
                    "발전기 수리를 통해 팀의 목표 달성에 기여하는 유형입니다.",
                "팀 지원형":
                    "구조와 팀원 지원에 집중하는 유형입니다."
            }

            st.write(descriptions[style])

            st.caption(
                "플레이 유형은 프로젝트에서 설정한 "
                "자체 기준에 따른 분류입니다."
            )

    else:

        hooks = df["hooks"].mean()
        four_k = (df["kills"] == 4).mean() * 100

        c1, c2, c3 = st.columns(3)

        c1.metric("평균 처치 수", f"{avg:.1f}명")
        c2.metric("평균 갈고리", f"{hooks:.1f}회")
        c3.metric("4킬 달성률", f"{four_k:.1f}%")

    st.divider()

    if total < 10:
        st.info(
            "경기 기록을 더 추가하면 강점, 개선 방향, "
            "추천 퍽 조합을 확인할 수 있습니다."
        )
        st.stop()

    st.subheader("02. 강점 및 개선 방향")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 강점")

        if mode == "생존자":

            if chase >= 120:
                st.success("평균 추격 시간이 긴 편입니다.")

            if gen >= 150:
                st.success("발전기 수리 기여도가 높습니다.")

            if rescue >= 2:
                st.success("팀원 구조에 적극적으로 참여합니다.")

            if avg >= 50:
                st.success("기록된 경기의 절반 이상에서 탈출했습니다.")

            if chase < 120 and gen < 150 and rescue < 2 and avg < 50:
                st.info("아직 뚜렷한 강점 기준에 도달하지 않았습니다.")

        else:

            if avg >= 3:
                st.success("평균 3명 이상을 처치하고 있습니다.")

            if hooks >= 8:
                st.success("갈고리 횟수가 높은 편입니다.")

            if avg < 3 and hooks < 8:
                st.info("추가 기록을 통해 강점을 확인해보세요.")

    with c2:
        st.markdown("#### 개선 방향")

        if mode == "생존자":

            if chase < 120:
                st.info("판자와 창틀 위치를 파악하고 추격 동선을 연습해보세요.")

            if gen < 150:
                st.info("추격받지 않는 시간에 발전기 수리에 집중해보세요.")

            if rescue < 2:
                st.info("안전한 구조 기회와 팀원의 상황을 확인해보세요.")

            if avg < 50:
                st.info("실패한 경기의 상대 살인마와 맵을 비교해보세요.")

            if chase >= 120 and gen >= 150 and rescue >= 2 and avg >= 50:
                st.success("현재 플레이 패턴을 유지하며 추가 기록을 쌓아보세요.")

        else:

            if avg < 2:
                st.info("발전기 견제와 추격 대상 변경을 연습해보세요.")

            if hooks < 8:
                st.info("지나치게 긴 추격을 줄이는 전략을 연습해보세요.")

            if avg >= 2 and hooks >= 8:
                st.success("현재 전략을 유지하며 맵별 성과를 비교해보세요.")

    st.caption(
        "강점과 개선 방향은 공식 게임 평균이 아닌 "
        "프로젝트 자체 분석 기준입니다."
    )

    st.divider()
    st.subheader("03. 추천 플레이 시간대")

    df["hour"] = pd.to_numeric(
        df["time"].astype(str).str[:2],
        errors="coerce"
    )

    def period(hour):
        if pd.isna(hour):
            return "미기록"
        if hour < 6:
            return "새벽"
        if hour < 12:
            return "오전"
        if hour < 18:
            return "오후"
        return "저녁"

    df["시간대"] = df["hour"].apply(period)

    time_stats = df.groupby("시간대").agg(
        경기수=("score", "count"),
        성과=("score", "mean")
    )

    time_stats = time_stats[
        (time_stats["경기수"] >= 5) &
        (time_stats.index != "미기록")
    ]

    if not time_stats.empty:

        best = time_stats["성과"].idxmax()
        value = time_stats.loc[best, "성과"]

        st.success(
            f"기록상 가장 성과가 좋은 시간대: "
            f"{best} ({value:.1f}{unit})"
        )

        st.dataframe(
            time_stats.round(1),
            use_container_width=True
        )

    else:
        st.info("시간대별로 최소 5경기 이상의 기록이 필요합니다.")

    st.divider()
    st.subheader("04. 추천 퍽 조합")

    df["build"] = df["perks"].fillna("").apply(
        lambda x: " + ".join(
            sorted(x.split(" | "))
        ) if x else ""
    )

    build_stats = df[df["build"] != ""].groupby(
        "build"
    ).agg(
        경기수=("score", "count"),
        성과=("score", "mean")
    )

    build_stats = build_stats[
        build_stats["경기수"] >= 3
    ].sort_values(
        ["성과", "경기수"],
        ascending=False
    )

    if not build_stats.empty:

        best_build = build_stats.index[0]
        best_score = build_stats.iloc[0]["성과"]

        st.success("개인 기록 기반 추천 퍽 조합")

        for perk in best_build.split(" + "):
            st.markdown(f"**{perk}**")

        st.metric(
            "해당 조합의 평균 성과",
            f"{best_score:.1f}{unit}"
        )

        st.caption(
            "기존에 사용한 조합 중 성과가 가장 높은 조합입니다. "
            "퍽의 인과적 효과를 의미하지 않습니다."
        )

    else:
        st.info("동일한 퍽 조합으로 최소 3경기 이상 플레이해주세요.")

    st.divider()

    if mode == "생존자":

        st.subheader("05. 상대하기 어려운 살인마")

        opponent_stats = df.groupby("opponent").agg(
            경기수=("score", "count"),
            탈출률=("score", "mean")
        )

        opponent_stats = opponent_stats[
            opponent_stats["경기수"] >= 3
        ].sort_values("탈출률")

        if not opponent_stats.empty:

            hardest = opponent_stats.index[0]
            rate = opponent_stats.iloc[0]["탈출률"]

            st.warning(
                f"기록상 탈출률이 가장 낮은 살인마: "
                f"{hardest} ({rate:.1f}%)"
            )

            st.write(
                f"{hardest} 상대 경기의 추격 동선과 "
                "경기 메모를 복기해보세요."
            )

            st.dataframe(
                opponent_stats.round(1),
                use_container_width=True
            )

        else:
            st.info("동일한 살인마를 상대했던 기록이 3경기 이상 필요합니다.")

    else:

        st.subheader("05. 나에게 잘 맞는 살인마")

        killer_stats = df.groupby("character").agg(
            경기수=("score", "count"),
            평균처치수=("score", "mean")
        )

        killer_stats = killer_stats[
            killer_stats["경기수"] >= 3
        ].sort_values("평균처치수", ascending=False)

        if not killer_stats.empty:

            best_killer = killer_stats.index[0]

            st.success(
                f"기록상 가장 성과가 좋은 살인마: {best_killer}"
            )

            st.dataframe(
                killer_stats.round(1),
                use_container_width=True
            )

        else:
            st.info("살인마별 최소 3경기 이상의 기록이 필요합니다.")

    st.divider()

    st.caption(
        "본 리포트는 사용자가 입력한 경기 데이터를 "
        "기반으로 생성된 규칙 기반 분석 결과입니다."
    )

else:
    st.title(menu)
    st.info("개발 예정인 기능입니다.")
