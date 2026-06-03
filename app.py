import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))
from db import get_con, TYPE_COLORS, TYPE_ORDER

st.set_page_config(
    page_title="Pokédex",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CDN = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"

# ── Game registry ─────────────────────────────────────────────────────────────
GAMES = {
    1: {"title": "Generation I",    "subtitle": "Red · Blue · Yellow",
        "starters": [1, 4, 7],      "legendary": 150,  "accent": "#C62828"},
    2: {"title": "Generation II",   "subtitle": "Gold · Silver · Crystal",
        "starters": [152, 155, 158], "legendary": 249,  "accent": "#F9A825"},
    3: {"title": "Generation III",  "subtitle": "Ruby · Sapphire · Emerald",
        "starters": [252, 255, 258], "legendary": 384,  "accent": "#2E7D32"},
    4: {"title": "Generation IV",   "subtitle": "Diamond · Pearl · Platinum",
        "starters": [387, 390, 393], "legendary": 483,  "accent": "#1565C0"},
    5: {"title": "Generation V",    "subtitle": "Black · White",
        "starters": [495, 498, 501], "legendary": 643,  "accent": "#37474F"},
    6: {"title": "Generation VI",   "subtitle": "X · Y",
        "starters": [650, 653, 656], "legendary": 716,  "accent": "#4527A0"},
    7: {"title": "Generation VII",  "subtitle": "Sun · Moon",
        "starters": [722, 725, 728], "legendary": 791,  "accent": "#E65100"},
    8: {"title": "Generation VIII", "subtitle": "Sword · Shield",
        "starters": [810, 813, 816], "legendary": 888,  "accent": "#0277BD"},
    9: {"title": "Generation IX",   "subtitle": "Scarlet · Violet",
        "starters": [906, 909, 912], "legendary": 1007, "accent": "#6A1B9A"},
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Game selection cards ── */
.game-card {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    padding: 18px 14px 14px;
    text-align: center;
    margin-bottom: 8px;
    transition: transform 0.18s, box-shadow 0.18s;
    border: 2px solid transparent;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.game-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}
/* Legendary art — absolute-positioned behind everything */
.game-card .cover-art {
    position: absolute;
    right: -12px;
    bottom: -8px;
    width: 160px;
    height: 160px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: bottom right;
    opacity: 0.18;
    pointer-events: none;
}
/* Foreground content sits above the art */
.game-card .card-content {
    position: relative;
    z-index: 1;
    width: 100%;
}
.game-title {
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.03em;
    margin-bottom: 2px;
}
.game-subtitle {
    font-size: 0.75rem;
    color: #ccc;
    margin-bottom: 10px;
}
.game-count {
    display: inline-block;
    background: rgba(0,0,0,0.35);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.75rem;
    color: #ddd;
    margin-top: 8px;
    backdrop-filter: blur(4px);
}
.starter-row { display: flex; justify-content: center; gap: 6px; }
.starter-row img { image-rendering: pixelated; }

/* ── Pokédex detail panel ── */
.type-badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 700;
    margin-right: 6px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}
.stat-row { display: flex; align-items: center; margin-bottom: 5px; }
.stat-label {
    width: 52px; font-weight: 600; color: #aaa; font-size: 0.8rem;
    text-align: right; margin-right: 10px; flex-shrink: 0;
}
.stat-bar-bg {
    flex: 1; background: #2a2a2a; border-radius: 8px;
    height: 12px; overflow: hidden;
}
.stat-bar-fill { height: 100%; border-radius: 8px; }
.stat-val {
    width: 36px; text-align: right; font-size: 0.85rem;
    font-weight: 700; margin-left: 8px; flex-shrink: 0;
}
.flavor-text {
    font-size: 1.05rem; line-height: 1.6; color: #e8e8e8;
    border-left: 4px solid #EE8130;
    padding-left: 14px; margin: 12px 0 18px 0;
}
.physical-stat {
    display: inline-block; background: #1e2128;
    border-radius: 12px; padding: 6px 14px;
    margin-right: 8px; font-size: 0.9rem;
}

/* ── Card grid cells — uniform spreadsheet-style ── */
.poke-cell {
    background: #1a1d23;
    border: 1px solid #2e3038;
    border-radius: 8px;
    padding: 8px 4px 6px;
    text-align: center;
    /* Fixed height so every cell is identical */
    min-height: 148px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    gap: 3px;
    margin-bottom: 2px;
}
.poke-cell.selected {
    border-width: 2px;
    background: #1e2430;
}
/* Fixed-size image box — all sprites same visual footprint */
.poke-img-box {
    width: 68px;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.poke-img-box img {
    max-width: 68px;
    max-height: 68px;
    image-rendering: pixelated;
}
.poke-num  { font-size: 0.62rem; color: #777; font-weight: 600; }
.poke-name { font-size: 0.7rem;  color: #eee; font-weight: 700; line-height: 1.2; }

/* Card buttons — visible on dark background */
div[data-testid="stVerticalBlock"] .stButton button {
    font-size: 0.7rem !important;
    padding: 3px 6px !important;
    border: 1px solid #3e4148 !important;
    background-color: #2a2d35 !important;
    color: #ccc !important;
    border-radius: 6px !important;
    width: 100% !important;
}
div[data-testid="stVerticalBlock"] .stButton button:hover {
    border-color: #EE8130 !important;
    color: #fff !important;
}
/* Primary (selected) card button — accent fill */
div[data-testid="stVerticalBlock"] .stButton button[kind="primary"] {
    background-color: var(--primary-color, #EE8130) !important;
    border-color: transparent !important;
    color: white !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

con = get_con()


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    df = con.sql("SELECT * FROM pokedex_full ORDER BY Number, Name").df()
    df["_len"] = df["Name"].str.len()
    df = (df.sort_values(["Number", "_len"])
            .drop_duplicates(subset=["Number"])
            .drop(columns=["_len"])
            .reset_index(drop=True))
    return df

df_all = load_all()

# Pre-compute count per generation (post-dedup)
GEN_COUNTS = df_all.groupby("Generation").size().to_dict()


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

def gif_url(pokemon_id: int) -> str:
    return f"{CDN}/other/showdown/{pokemon_id}.gif"

def artwork_url(pokemon_id: int) -> str:
    return f"{CDN}/other/official-artwork/{pokemon_id}.png"


# ── Session state defaults ────────────────────────────────────────────────────
if "selected_gen" not in st.session_state:
    st.session_state["selected_gen"] = None
if "selected_number" not in st.session_state:
    st.session_state["selected_number"] = None


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Game selection
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["selected_gen"] is None:

    st.markdown(
        "<h1 style='text-align:center;margin-bottom:4px;'>📖 Pokédex</h1>"
        "<p style='text-align:center;color:#aaa;font-size:1.1rem;margin-bottom:32px;'>"
        "Pick your Pokémon game to get started!</p>",
        unsafe_allow_html=True,
    )

    # 3 columns × 3 rows
    gen_items = list(GAMES.items())
    for row_i in range(3):
        cols = st.columns(3, gap="medium")
        for col_i, col in enumerate(cols):
            gen = row_i * 3 + col_i + 1
            info = GAMES[gen]
            count = GEN_COUNTS.get(gen, 0)
            starters = info["starters"]
            accent = info["accent"]

            starter_imgs = "".join(
                f'<img src="{gif_url(s)}" width="72" style="image-rendering:pixelated;"/>'
                for s in starters
            )

            with col:
                leg_id = info["legendary"]
                art_url = f"{CDN}/other/official-artwork/{leg_id}.png"
                # Gradient: accent colour fading to dark, with legendary art watermark
                gradient = f"linear-gradient(145deg, {accent}33 0%, #0e1117 65%)"
                st.markdown(
                    f'<div class="game-card" style="background:{gradient};border-color:{accent};">'
                    f'<div class="cover-art" style="background-image:url(\'{art_url}\');"></div>'
                    f'<div class="card-content">'
                    f'<div class="game-title" style="color:{accent};">{info["title"]}</div>'
                    f'<div class="game-subtitle">{info["subtitle"]}</div>'
                    f'<div class="starter-row">{starter_imgs}</div>'
                    f'<div class="game-count">✨ {count} new Pokémon</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"Explore {info['title']} →",
                             key=f"gen_{gen}",
                             use_container_width=True):
                    st.session_state["selected_gen"] = gen
                    st.session_state["selected_number"] = None
                    st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Pokédex for selected generation
# ══════════════════════════════════════════════════════════════════════════════
gen = st.session_state["selected_gen"]
info = GAMES[gen]
accent = info["accent"]

# Filter to this generation only, sorted by Pokédex number
df = df_all[df_all["Generation"] == gen].sort_values("Number").reset_index(drop=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("← All Games", use_container_width=True):
        st.session_state["selected_gen"] = None
        st.session_state["selected_number"] = None
        st.rerun()

    st.markdown(
        f'<div style="color:{accent};font-weight:800;font-size:1.1rem;margin:8px 0 2px;">'
        f'{info["title"]}</div>'
        f'<div style="color:#aaa;font-size:0.85rem;margin-bottom:16px;">{info["subtitle"]}</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input("🔍 Search", placeholder="e.g. Charizard")
    show_legendary = st.radio("Show", ["All", "Non-Legendary", "Legendary only"])

    if st.button("🎲 Surprise me!", use_container_width=True):
        st.session_state["selected_number"] = int(df.sample(1).iloc[0]["Number"])
        st.session_state["_scroll_top"] = True
        st.rerun()

# Apply search/legendary filter (generation is already locked)
df_view = df.copy()
if search:
    df_view = df_view[df_view["Name"].str.contains(search, case=False, na=False)]
if show_legendary == "Non-Legendary":
    df_view = df_view[~df_view["Legendary"]]
elif show_legendary == "Legendary only":
    df_view = df_view[df_view["Legendary"]]

if df_view.empty:
    st.warning("No Pokémon match that search. Try something else!")
    st.stop()

# Resolve selected Pokémon (default to first of this gen)
default_num = int(df_view.iloc[0]["Number"])
sel_num = st.session_state.get("selected_number") or default_num
if sel_num not in df_view["Number"].values:
    sel_num = default_num
st.session_state["selected_number"] = sel_num
row = df_view[df_view["Number"] == sel_num].iloc[0]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<h2 style="margin-bottom:4px;">'
    f'<span style="color:{accent};">{info["title"]}</span>'
    f'&nbsp;<span style="color:#888;font-size:1rem;font-weight:400;">{info["subtitle"]}</span>'
    f'</h2>'
    f'<p style="color:#aaa;margin-bottom:16px;">'
    f'#{int(df.iloc[0]["Number"]):04d} – #{int(df.iloc[-1]["Number"]):04d} · '
    f'{len(df_view):,} Pokémon shown</p>',
    unsafe_allow_html=True,
)

# Scroll to top whenever a new Pokémon is selected
if st.session_state.pop("_scroll_top", False):
    components.html(
        "<script>"
        "var el=window.parent.document.querySelector('[data-testid=\"stMain\"]');"
        "if(el)el.scrollTo({top:0,behavior:'smooth'});"
        "</script>",
        height=0,
    )

# ── Detail panel ──────────────────────────────────────────────────────────────
with st.container(border=True):
    art_col, info_col = st.columns([1, 1.7], gap="large")

    with art_col:
        st.image(row["ArtworkURL"], use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:6px;">'
            f'<img src="{row["AnimatedGifURL"]}" width="96" style="image-rendering:pixelated;"/>'
            f'<br><span style="font-size:0.75rem;color:#888;">Battle sprite</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with info_col:
        leg_star = " ⭐" if row["Legendary"] else ""
        st.markdown(
            f'<span style="color:#888;font-size:1.1rem;font-weight:700;">#{int(row["Number"]):04d}</span>'
            f'<span style="color:#888;font-size:0.85rem;"> Gen {gen}{leg_star}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f"## {row['Name']}")

        badges = type_badge(row["Type1"])
        if row["Type2"]:
            badges += type_badge(row["Type2"])
        genus = row.get("Genus", "") or ""
        st.markdown(
            f'<span style="color:#bbb;font-style:italic;font-size:0.95rem;">{genus}</span>'
            f'<br>{badges}',
            unsafe_allow_html=True,
        )

        flavor = row.get("FlavorText", "") or ""
        if flavor:
            st.markdown(
                f'<div class="flavor-text">"{flavor}"</div>',
                unsafe_allow_html=True,
            )

        egg2 = f" / {row['EggGroup2']}" if row.get("EggGroup2") else ""
        st.markdown(
            f'<div style="margin-bottom:14px;">'
            f'<span class="physical-stat">📏 {row["HeightM"]:.1f} m</span>'
            f'<span class="physical-stat">⚖️ {row["WeightKg"]:.1f} kg</span>'
            f'<span class="physical-stat">🥚 {row.get("EggGroup1","")}{egg2}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        bars = "".join([
            stat_bar("HP",    int(row["HP"])),
            stat_bar("ATK",   int(row["Attack"])),
            stat_bar("DEF",   int(row["Defense"])),
            stat_bar("SpATK", int(row["SpAtk"])),
            stat_bar("SpDEF", int(row["SpDef"])),
            stat_bar("SPD",   int(row["Speed"])),
        ])
        tc = stat_color(int(row["TotalStats"]) // 6)
        bars += (f'<div style="margin-top:8px;font-size:0.82rem;color:#aaa;">'
                 f'Total: <strong style="color:{tc}">{int(row["TotalStats"])}</strong></div>')
        st.markdown(bars, unsafe_allow_html=True)

# ── Card grid — uniform spreadsheet cells ─────────────────────────────────────
st.divider()
st.subheader(f"All {len(df_view):,} Pokémon — click any card to explore!")

COLS = 8
for chunk_start in range(0, len(df_view), COLS):
    chunk = df_view.iloc[chunk_start : chunk_start + COLS]
    cols = st.columns(COLS, gap="small")
    for col, (_, r) in zip(cols, chunk.iterrows()):
        with col:
            is_sel = int(r["Number"]) == sel_num
            cell_cls = "poke-cell selected" if is_sel else "poke-cell"
            border_color = accent if is_sel else "#2e3038"

            st.markdown(
                f'<div class="{cell_cls}" style="border-color:{border_color};">'
                f'<div class="poke-img-box">'
                f'<img src="{r["AnimatedGifURL"]}"/>'
                f'</div>'
                f'<div class="poke-num">#{int(r["Number"]):04d}</div>'
                f'<div class="poke-name">{r["Name"]}</div>'
                f'{type_badge(r["Type1"])}'
                f'</div>',
                unsafe_allow_html=True,
            )

            btn_label = "✓ Selected" if is_sel else "View →"
            btn_type  = "primary"    if is_sel else "secondary"
            if st.button(btn_label, key=f"c_{int(r['Number'])}", type=btn_type,
                         use_container_width=True):
                st.session_state["selected_number"] = int(r["Number"])
                st.session_state["_scroll_top"] = True
                st.rerun()
