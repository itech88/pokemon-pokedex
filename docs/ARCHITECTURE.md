# Solution Architecture

## Overview

The Pokémon platform is a two-repo analytics ecosystem built around a shared
PokéAPI data pipeline. One repo serves kids learning about Pokémon; the other
serves adult analytics. Both read from the same set of source-of-truth CSVs,
build their own DuckDB semantic layer, and expose their data via Streamlit
web applications.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  itech88/pokemon-analytics          │   itech88/pokemon-pokedex             │
│  Adult analytical dashboard         │   Kid-friendly Visual Pokédex         │
│  7 Streamlit pages                  │   3-screen Streamlit app              │
│  12 DuckDB views + 6 raw tables     │   3 DuckDB views + 5 raw tables       │
│  51 unit tests + 8 smoke tests      │   10 Playwright E2E tests             │
└─────────────────────────────────────────────────────────────────────────────┘
                       ▲ both read from shared CSVs
```

---

## Solution Architecture Diagram

```mermaid
graph TB
  subgraph EXT["External Sources"]
    API["PokéAPI\npokeapi.co/api/v2\nfree · rate-limited"]
    CDN["Sprite CDN\nraw.githubusercontent.com\nPokeAPI/sprites"]
  end

  subgraph ETL["ETL Layer  —  pokemon-analytics repo"]
    FETCH["fetch_pokemon_data.py\nasync aiohttp · 30 concurrent\nWILD_METHODS filter\ncaches responses in .api_cache/"]
    EXTRACT["extract_pokedex_data.py\nreads .api_cache/ only\nno network calls"]
    CACHE[".api_cache/\n5,318 JSON files\n~100 MB uncompressed"]
    BUILD["build_db.py\n6 raw tables\n12 semantic views\nidempotent"]
    DB_A["pokemon.duckdb  (adult)\n~3.5 MB"]
  end

  subgraph CSV["CSVs  —  source of truth  —  committed to both repos"]
    C1["pokemon_data.csv\n1,351 rows\n12 cols"]
    C2["pokedex_data.csv\n1,026 rows\n17 cols"]
    C3["Pokemon_Abilities.csv\n2,575 rows\n3 cols"]
    C4["Pokemon_Locations.csv\n8,467 rows\n4 cols"]
    C5["Types_Attributes.csv\n18 rows · 5 cols"]
    C6["Type_effectiveness.csv\n120 rows · 3 cols"]
  end

  subgraph ADULT["Adult Analytics  —  pokemon-analytics"]
    DA["dashboard/app.py\nHome · 5 KPI metrics"]
    P1["📊 Stats by Type"]
    P2["📈 Power Creep"]
    P3["⚔️ Type Effectiveness"]
    P4["🏆 Pokémon Explorer"]
    P5["🗺️ Regions"]
    P6["🌟 Legendary"]
    P7["📖 Visual Pokédex"]
    V_A["12 Semantic Views\nstat_summary_by_type\ntype_matchup_matrix\ntop_pokemon_by_stat\nregion_encounter_summary\nlegendary_vs_normal\ndual_type_distribution\npokemon_full_dex\n+ 5 more"]
  end

  subgraph KIDS["Kids Pokédex  —  pokemon-pokedex"]
    APP["app.py\n3 screens"]
    S1["Screen 1: Game Selection\n9 generation cards\nstarter sprites + legendary art"]
    S2["Screen 2: Generation Pokédex\nOverview tab + Physical Traits tab\n8-col card grid"]
    S3["Session state management\nselected_gen · selected_number\n_scroll_top · _scroll_n"]
    DB_K["pokemon.duckdb  (kids)\nauto-built on first launch"]
    V_K["3 Views\npokedex_full\npokemon_traits\npokemon_base"]
  end

  subgraph TESTS["Test Layer"]
    T1["test_pokemon_data.py\n51 unit tests\nvalidates all 6 CSVs"]
    T2["test_dashboard_smoke.py\n8 Streamlit AppTest\nheadless, no browser"]
    T3["test_ui.py\n10 Playwright E2E\nheadless Chromium"]
  end

  API -->|"GET /pokemon\nGET /evolution-chain\netc."| FETCH
  FETCH -->|"cache miss"| CACHE
  CACHE -->|"cache hit"| FETCH
  FETCH --> C1 & C3 & C4 & C5 & C6
  CACHE --> EXTRACT --> C2
  C1 & C2 & C3 & C4 & C5 & C6 --> BUILD --> DB_A --> V_A
  DA & P1 & P2 & P3 & P4 & P5 & P6 & P7 --- V_A
  C1 & C2 & C3 & C4 & C5 --> DB_K --> V_K --> APP
  APP --> S1 & S2 & S3
  CDN -->|"sprite URLs\nconstrucred from id"| APP
  T1 -.->|validates| C1 & C4
  T2 -.->|smoke| P1 & P2 & P3 & P4 & P5 & P6 & P7
  T3 -.->|E2E| S1 & S2
```

---

## Layers

### External Sources

| Source | What we use | Rate limit |
|---|---|---|
| PokéAPI `pokeapi.co/api/v2` | Pokémon stats, species, encounters, types, abilities, evolution chains | Soft limit; respected via local cache |
| GitHub Sprite CDN `raw.githubusercontent.com/PokeAPI/sprites` | Official artwork PNGs, animated battle GIFs | No limit; CDN-served |

The `.api_cache/` directory stores every API response as a JSON file keyed by endpoint
URL. Re-running the ETL scripts costs zero network calls for already-fetched data.

### ETL Layer (`pokemon-analytics` repo)

Three Python scripts produce the six source CSVs:

| Script | Input | Output | Network calls |
|---|---|---|---|
| `fetch_pokemon_data.py` | PokéAPI (cached) | 5 CSVs | 0 if cache warm; ~5,318 on cold start |
| `extract_pokedex_data.py` | `.api_cache/` only | `pokedex_data.csv` | 0 always |
| `build_db.py` | 6 CSVs | `pokemon.duckdb` | 0 |

`fetch_pokemon_data.py` is the only script that ever touches the network. It uses
`asyncio` + `aiohttp` with 30 concurrent connections and an exponential-backoff retry
strategy. The `WILD_METHODS` allowlist (35 encounter methods) ensures only genuine
wild encounters appear in `Pokemon_Locations.csv`.

### Data Layer (CSVs)

The six CSVs are committed to both repos and serve as the **single source of truth**.
They are regenerated by re-running `fetch_pokemon_data.py` + `extract_pokedex_data.py`,
then synced to the kids repo with a `cp` command.

**Why CSVs instead of a shared database?**
- Simple to version-control and diff
- Any developer can open them in Excel/Numbers to inspect data
- Each repo builds its own DuckDB from them — no shared mutable state
- CSVs can be exported to Parquet for the future DuckDB-WASM upgrade

### Application Layer

Both applications use the same stack but with different emphases:

| Aspect | Adult (`pokemon-analytics`) | Kids (`pokemon-pokedex`) |
|---|---|---|
| Framework | Streamlit 1.58 | Streamlit 1.58 |
| DB connection | `read_only=True`, `@st.cache_resource` | `read_only=True`, `@st.cache_resource` |
| Session state | Minimal (filter state per page) | Rich (`selected_gen`, `selected_number`, scroll flags) |
| Data volume per query | Aggregated views (18–1,026 rows) | Single-Pokémon lookups (1–100 rows) |
| Scroll management | Standard Streamlit | Custom JS via `st.components.v1.html` with cache-bust counter |
| Image loading | Plotly charts (no external images) | CDN sprites via `st.image()` and raw `<img>` tags |

### Semantic Layer (DuckDB Views)

DuckDB sits between the CSVs and the UI. All business logic lives in SQL views
rather than Python, which means:
- The same views can be queried from notebooks, the dashboard, and future WASM clients
- Adding a new field means adding it to the view — the UI picks it up automatically
- Views are cheap to rebuild (sub-second for this dataset size)

**Adult repo views (12):**
`pokemon_full`, `pokemon_base`, `pokemon_full_dex`, `pokemon_with_abilities`,
`pokemon_with_locations`, `type_matchup_matrix`, `stat_summary_by_type`,
`stat_summary_by_generation`, `legendary_vs_normal`, `top_pokemon_by_stat`,
`region_encounter_summary`, `dual_type_distribution`

**Kids repo views (3):**
`pokemon_base`, `pokedex_full`, `pokemon_traits`

### Test Layer

| Test file | What it validates | When to run |
|---|---|---|
| `test_pokemon_data.py` | CSV data integrity against `.api_cache/` — types, encounter rates, no gift-only Pokémon in wild locations | After any ETL run or CSV change |
| `test_dashboard_smoke.py` | All 7 adult dashboard pages render without Python exception | Before every commit to `pokemon-analytics` |
| `test_ui.py` | Full browser automation — game selection, generation navigation, card clicks, scroll behaviour, location accuracy | Before every commit to `pokemon-pokedex` |

---

## Future Architecture: DuckDB-WASM + React

See [IDEAS.md](IDEAS.md#architecture-upgrade--duckdb-wasm--react) for the full
upgrade path. The key architectural difference: CSVs → Parquet → hosted statically →
queried in-browser by DuckDB-WASM. The Python ETL layer is unchanged; only the
presentation layer moves from Streamlit (server-rendered) to React (client-rendered).
