import random
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from db import get_con, TYPE_COLORS, TYPE_ORDER

st.set_page_config(
    page_title="Pokédex",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.type-badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-right: 6px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}
.stat-row {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
}
.stat-label {
    width: 52px;
    font-weight: 600;
    color: #aaa;
    font-size: 0.8rem;
    text-align: right;
    margin-right: 10px;
    flex-shrink: 0;
}
.stat-bar-bg {
    flex: 1;
    background: #2a2a2a;
    border-radius: 8px;
    height: 12px;
    overflow: hidden;
}
.stat-bar-fill {
    height: 100%;
    border-radius: 8px;
}
.stat-val {
    width: 36px;
    text-align: right;
    font-size: 0.85rem;
    font-weight: 700;
    margin-left: 8px;
    flex-shrink: 0;
}
.flavor-text {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #e8e8e8;
    border-left: 4px solid #EE8130;
    padding-left: 14px;
    margin: 12px 0 20px 0;
}
.physical-stat {
    display: inline-block;
    background: #1e2128;
    border-radius: 12px;
    padding: 7px 16px;
    margin-right: 10px;
    font-size: 0.95rem;
}
.pokedex-number {
    color: #888;
    font-size: 1.1rem;
    font-weight: 700;
}
.genus-text {
    color: #bbb;
    font-style: italic;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

con = get_con()


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    df = con.sql("""
        SELECT * FROM pokedex_full ORDER BY Number, Name
    """).df()
    df["_namelen"] = df["Name"].str.len()
    df = (df.sort_values(["Number", "_namelen"])
            .drop_duplicates(subset=["Number"])
            .drop(columns=["_namelen"])
            .reset_index(drop=True))
    return df

df_all = load_all()


# ── Helpers ───────────────────────────────────────────────────────────────────
def type_badge(t: str) -> str:
    c = TYPE_COLORS.get(t, "#888")
    return f'<span class="type-badge" style="background:{c};">{t}</span>'


def stat_color(v: int) -> str:
    if v >= 100: return "#5bde7a"
    if v >= 70:  return "#f7d02c"
    if v >= 45:  return "#EE8130"
    return "#C22E28"


def stat_bar(label: str, val: int) -> str:
    pct = min(int(val / 255 * 100), 100)
    c = stat_color(val)
    return (
        f'<div class="stat-row">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{c};"></div></div>'
        f'<div class="stat-val" style="color:{c};">{val}</div>'
        f'</div>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png", width=40)
    st.title("Pokédex")
    st.caption("Find your favourite Pokémon!")

    search = st.text_input("🔍 Search by name", placeholder="e.g. Pikachu")

    type_filter = st.multiselect("Type", TYPE_ORDER, default=TYPE_ORDER)
    gen_filter  = st.multiselect("Generation", list(range(1, 10)), default=list(range(1, 10)))

    st.divider()
    if st.button("🎲 Surprise me!", use_container_width=True):
        pool = df_all if df_all.empty else df_all
        st.session_state["selected_number"] = int(pool.sample(1).iloc[0]["Number"])

# ── Filter ────────────────────────────────────────────────────────────────────
df = df_all.copy()
if search:
    df = df[df["Name"].str.contains(search, case=False, na=False)]
if type_filter:
    df = df[df["Type1"].isin(type_filter)]
if gen_filter:
    df = df[df["Generation"].isin(gen_filter)]

if df.empty:
    st.warning("No Pokémon match those filters. Try broadening your search!")
    st.stop()

# Resolve selected Pokémon
default_num = int(df.iloc[0]["Number"])
sel_num = int(st.session_state.get("selected_number", default_num))
if sel_num not in df["Number"].values:
    sel_num = default_num
    st.session_state["selected_number"] = sel_num

row = df[df["Number"] == sel_num].iloc[0]

# ── Detail panel ──────────────────────────────────────────────────────────────
st.markdown(f"## 📖 Pokédex &nbsp; <span style='color:#888;font-size:1rem;'>Showing {len(df):,} Pokémon</span>",
            unsafe_allow_html=True)

with st.container(border=True):
    art_col, info_col = st.columns([1, 1.7], gap="large")

    with art_col:
        st.image(row["ArtworkURL"], use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:6px;">'
            f'<img src="{row["AnimatedGifURL"]}" width="100" style="image-rendering:pixelated;"/>'
            f'<br><span style="font-size:0.75rem;color:#888;">Battle sprite</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with info_col:
        leg = " ⭐" if row["Legendary"] else ""
        st.markdown(
            f'<span class="pokedex-number">#{int(row["Number"]):04d}</span>'
            f'<span style="color:#888;font-size:0.9rem;"> Gen {int(row["Generation"])}{leg}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"## {row['Name']}")
        badges = type_badge(row["Type1"])
        if row["Type2"]:
            badges += type_badge(row["Type2"])
        st.markdown(
            f'<span class="genus-text">{row["Genus"]}</span><br>{badges}',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="flavor-text">"{row["FlavorText"]}"</div>',
            unsafe_allow_html=True,
        )

        egg2 = f" / {row['EggGroup2']}" if row["EggGroup2"] else ""
        st.markdown(
            f'<div>'
            f'<span class="physical-stat">📏 {row["HeightM"]:.1f} m</span>'
            f'<span class="physical-stat">⚖️ {row["WeightKg"]:.1f} kg</span>'
            f'<span class="physical-stat">🥚 {row["EggGroup1"]}{egg2}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        bars = "".join([
            stat_bar("HP",    int(row["HP"])),
            stat_bar("ATK",   int(row["Attack"])),
            stat_bar("DEF",   int(row["Defense"])),
            stat_bar("SpATK", int(row["SpAtk"])),
            stat_bar("SpDEF", int(row["SpDef"])),
            stat_bar("SPD",   int(row["Speed"])),
        ])
        total_c = stat_color(int(row["TotalStats"]) // 6)
        bars += f'<div style="margin-top:8px;font-size:0.82rem;color:#aaa;">Total: <strong style="color:{total_c}">{int(row["TotalStats"])}</strong></div>'
        st.markdown(bars, unsafe_allow_html=True)

# ── Card grid ────────────────────────────────────────────────────────────────
st.divider()
st.subheader("All Pokémon — click any card!")

COLS = 8
chunks = [df.iloc[i:i+COLS] for i in range(0, len(df), COLS)]
for chunk in chunks:
    cols = st.columns(COLS)
    for col, (_, r) in zip(cols, chunk.iterrows()):
        with col:
            is_sel = int(r["Number"]) == sel_num
            border = "2px solid #EE8130" if is_sel else "2px solid transparent"
            bg     = "#1e2128" if is_sel else "transparent"
            st.markdown(
                f'<div style="border:{border};border-radius:10px;padding:4px;'
                f'background:{bg};text-align:center;">'
                f'<img src="{r["AnimatedGifURL"]}" width="60" style="image-rendering:pixelated;"/>'
                f'<br><span style="font-size:0.68rem;font-weight:600;">{r["Name"]}</span><br>'
                f'{type_badge(r["Type1"])}'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("", key=f"c_{int(r['Number'])}", help=r["Name"], width="stretch"):
                st.session_state["selected_number"] = int(r["Number"])
                st.rerun()
