# Data Flow

## Overview

This document traces data movement at two levels:
1. **Build-time ETL flow** — from PokéAPI to committed CSVs to DuckDB
2. **Runtime user flow** — from a browser click to rendered HTML

---

## Build-Time ETL Flow

The following sequence shows what happens when you run `python fetch_pokemon_data.py`
on a cold system (no cache), then `python build_db.py`, then launch the app.

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant Script as fetch_pokemon_data.py
  participant Cache as .api_cache/ (disk)
  participant API as PokéAPI
  participant CSV as CSV files (disk)
  participant Extract as extract_pokedex_data.py
  participant Build as build_db.py
  participant DB as pokemon.duckdb

  Dev->>Script: python fetch_pokemon_data.py

  Script->>API: GET /pokemon?limit=10000
  API-->>Script: 1,350 entries (name + URL)

  loop For each Pokémon (30 concurrent)
    Script->>Cache: check pokemon__{id}.json
    alt Cache miss
      Script->>API: GET /pokemon/{id}
      API-->>Script: stats, types, moves, sprites, encounter URL
      Script->>Cache: write pokemon__{id}.json
    else Cache hit
      Cache-->>Script: JSON (instant, no network)
    end

    Script->>Cache: check pokemon-species__{id}.json
    alt Cache miss
      Script->>API: GET /pokemon-species/{id}
      API-->>Script: generation, legendary, egg groups, flavor text
      Script->>Cache: write pokemon-species__{id}.json
    end

    Script->>Cache: check pokemon__{id}__encounters.json
    alt Cache miss
      Script->>API: GET /pokemon/{id}/encounters
      API-->>Script: location_area list with version_details
      Script->>Cache: write encounters JSON
    end

    Note over Script: Apply WILD_METHODS filter<br/>Exclude: gift, island-scan,<br/>overworld-flying-special, etc.
  end

  Script->>CSV: write pokemon_data.csv (1,351 rows)
  Script->>CSV: write Pokemon_Abilities.csv (2,575 rows)
  Script->>CSV: write Pokemon_Locations.csv (8,467 rows — filtered)
  Script->>CSV: write Types_Attributes.csv (18 rows)
  Script->>CSV: write Type_effectiveness.csv (120 rows)

  Dev->>Extract: python extract_pokedex_data.py
  Extract->>Cache: read pokemon__{id}.json + pokemon-species__{id}.json
  Note over Extract: Zero network calls<br/>Extracts: height, weight, sprites,<br/>flavor text, capture rate,<br/>gender rate, egg groups, etc.
  Extract->>CSV: write pokedex_data.csv (1,026 rows)

  Dev->>Build: python build_db.py
  Build->>CSV: read_csv_auto() × 6
  Build->>DB: CREATE TABLE raw_pokemon, raw_abilities, raw_locations,<br/>raw_type_attrs, raw_type_eff, raw_pokedex
  Build->>DB: CREATE VIEW pokemon_full, pokemon_base,<br/>stat_summary_by_type, type_matchup_matrix, …(12 total)
  Build->>DB: CHECKPOINT
  DB-->>Dev: "pokemon.duckdb built successfully. 6 tables, 12 views."
```

---

## Runtime User Interaction Flow (Kids App)

The following shows what happens when a user clicks a Pokémon card while scrolled
deep in the grid — the most complex interaction path in the app.

```mermaid
sequenceDiagram
  participant User as Browser (User)
  participant ST as Streamlit Server (Python)
  participant SS as Session State
  participant DB as DuckDB (in-process)
  participant CDN as Sprite CDN (GitHub)
  participant JS as Browser JS Engine

  User->>ST: Click "View →" button on Charmander card

  ST->>SS: selected_number = 4
  ST->>SS: _scroll_top = True
  ST->>ST: st.rerun() — full Python re-execution

  Note over ST: Script re-runs from top

  ST->>SS: read selected_gen (e.g., 1)
  ST->>SS: read selected_number (4 = Charmander)
  ST->>SS: pop _scroll_top → True
  ST->>SS: get _scroll_n = N; set _scroll_n = N+1

  ST->>ST: components.html("<script>/* N+1 */\nfunction _s(){...}\n_s();\nsetTimeout(_s,200);\nsetTimeout(_s,500);\n</script>", height=0)
  Note over ST: Unique comment /* N+1 */ forces<br/>new iframe — script always re-executes

  ST->>DB: SELECT * FROM pokedex_full\nWHERE Generation = 1\nORDER BY Number, Name
  DB-->>ST: 151 rows (Gen I Pokémon)

  ST->>DB: SELECT * FROM pokedex_full\nWHERE Number = 4
  DB-->>ST: 1 row (Charmander detail)

  ST->>ST: render_detail(row=Charmander, tab=Overview)
  ST->>CDN: <img src="…/official-artwork/4.png">
  CDN-->>User: HD artwork PNG

  ST->>CDN: <img src="…/showdown/4.gif">
  CDN-->>User: Animated battle GIF

  ST->>ST: render card grid (151 cards, 8 per row)
  Note over ST: Card #4 (Charmander) renders with:<br/>border: accent colour<br/>button: "✓ Selected" (primary type)

  ST-->>User: Full page HTML + CSS delivered to browser

  User->>JS: Iframe loads (the scroll component)
  JS->>JS: _s() fires immediately → stMain.scrollTop = 0
  JS->>JS: setTimeout(_s, 200ms) → scrollTop = 0 (catches reflow)
  JS->>JS: setTimeout(_s, 500ms) → scrollTop = 0 (final guard)

  User->>User: Page snapped to top; Charmander detail visible
```

---

## Runtime Flow: Physical Traits Tab

When a user clicks the "🏋️ Physical Traits" tab (after a Pokémon is selected):

```mermaid
sequenceDiagram
  participant User as Browser
  participant ST as Streamlit
  participant DB as DuckDB

  User->>ST: Click "Physical Traits" tab

  Note over ST: Tab change is handled client-side<br/>by Streamlit's tab widget —<br/>no full rerun unless state changes

  ST->>DB: SELECT StrongAgainst, WeakAgainst, ResistantTo, ImmuneFrom\nFROM pokemon_traits WHERE Number = {sel_num}
  DB-->>ST: 1 row (type attributes via LEFT JOIN raw_type_attrs)

  ST->>DB: SELECT AbilityName, IsHidden\nFROM raw_abilities WHERE Number = {sel_num}\nORDER BY IsHidden
  DB-->>ST: 1–3 rows (abilities for this Pokémon)

  ST->>DB: SELECT Region, AreaName, EncounterRate\nFROM raw_locations WHERE Number = {sel_num}\nORDER BY Region, EncounterRate DESC
  DB-->>ST: 0–N rows (wild encounter areas, or empty for gift-only)

  ST->>ST: render Body Facts section\n(height comparison, weight comparison, gender bar)
  ST->>ST: render Trainer Facts section\n(catch difficulty gauge, XP bar, happiness label, growth rate)
  ST->>ST: render Abilities section\n(green badges for normal, gold badge for hidden)

  alt Pokémon has 0 location rows
    ST->>ST: render "can't be found in the wild" info box
  else Pokémon has locations
    ST->>ST: render expandable region sections
  end

  ST->>ST: render Type Battle Info section\n(type badges from semicolon-delimited strings)
  ST-->>User: Physical Traits tab content rendered
```

---

## WILD_METHODS Filter — How It Works

This filter is the fix for the Charizard location bug (June 2026). It runs during
CSV generation in `fetch_pokemon_data.py`.

```
PokéAPI encounter response structure:
[
  {
    "location_area": {"url": "…/location-area/123/"},
    "version_details": [
      {
        "max_chance": 100,
        "encounter_details": [
          {
            "chance": 100,
            "method": {"name": "overworld-flying-special"},  ← CHECK THIS FIELD
            "min_level": 3,
            "max_level": 56
          }
        ]
      }
    ]
  }
]

Filter logic:
  Keep encounter IF any(
    ed["method"]["name"] IN WILD_METHODS
    for vd in version_details
    for ed in vd["encounter_details"]
  )

WILD_METHODS includes:  walk, overworld, dark-grass, cave-spots, surf,
                        old-rod, good-rod, super-rod, horde, honey-tree,
                        sos-encounter, headbutt-*, …(35 total)

WILD_METHODS excludes:  gift, island-scan, overworld-flying-special,
                        overworld-special, snag, npc-trade, gift-egg, …
```

**Result:** Charizard's 25 Kanto "overworld-flying-special" entries → filtered out → 0 rows.
Rattata's "walk" entries → kept → 73 rows across multiple regions.

---

## Sprite URL Construction

Sprite URLs are derived deterministically from a Pokémon's `id` field — no API call needed.

```
Official HD artwork (PNG, transparent background):
  https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/
  pokemon/other/official-artwork/{id}.png

Animated battle sprite (GIF, pixel-art style):
  https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/
  pokemon/other/showdown/{id}.gif

Shiny animated sprite:
  https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/
  pokemon/other/showdown/shiny/{id}.gif
```

**Important:** The `id` here is the Pokémon's internal API identifier, which equals
the species Pokédex number for all base forms (1–1025). Regional variants and alternate
forms have IDs above 10000 and are excluded from the kids app by the `IsForm = false`
filter in `pokemon_base`.

---

## pokedex_full De-duplication — The Farfetch'd Galar Case

`pokemon_data.csv` has an edge case: "Farfetchd Galar" (number 83) appears without
parentheses in its name because the display-name formatter dropped the apostrophe
during slug normalization. This means `IsForm = false` matches two rows for species 83
instead of one.

The `load_all()` function in `app.py` applies a secondary de-duplication:

```python
df["_namelen"] = df["Name"].str.len()
df = (df.sort_values(["Number", "_namelen"])
        .drop_duplicates(subset=["Number"])   # keep shortest name = canonical
        .drop(columns=["_namelen"]))
```

This is a display-layer workaround. The correct fix is in `fetch_pokemon_data.py`'s
`_display_name()` function — ensuring Galarian forms always produce names with
parentheses. Tracked for a future cleanup pass.
