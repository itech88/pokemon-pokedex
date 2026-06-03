# Phase 2–5 Enhancement Ideas

This document is the living roadmap for the Pokémon Pokédex platform. Each idea is
elaborated with enough detail to think critically about implementation before writing
a line of code.

**Current status (as of June 2026):**
- Phase 1 ✅ — Full ETL pipeline, DuckDB semantic layer, kids Pokédex, adult analytics
- Phase 2 Idea 1 ✅ — Visual Pokédex (sprites, artwork, animated GIFs, flavor text)
- Phase 2 Idea 2 ✅ — Physical Traits tab (height, weight, catch rate, abilities, locations, type matchups)

---

## Idea 3 — Evolution Chain Trees

### Goal
Show every Pokémon's evolutionary path — from baby form to final evolution, including
all branching variants (Eevee's 8 evolutions, Tyrogue's 3 split paths, regional
variants like Galarian Slowbro). Kids get a visual "family tree"; adults get analytical
queries over chain structure.

### Data requirements

**New API calls:** ~541 — `GET /evolution-chain/{id}` per unique chain URL.
All 541 chain URLs are already known from the cached `pokemon-species__*.json` files
(field: `evolution_chain.url`). No discovery fetch is needed. At 30 concurrent
connections, this takes approximately 20–30 seconds.

**New CSV — `evolution_chains.csv`:**
```
species_id, evolves_into_id, trigger, min_level, min_happiness,
trigger_item, time_of_day, location, held_item, known_move, chain_id
```

One row per directed edge in the evolution graph. A Pokémon with 3 evolutions
(like Tyrogue → Hitmonlee/Hitmonchan/Hitmontop) produces 3 rows with `species_id = 236`.

**New DuckDB objects:**
- `raw_evolution` table — loaded from the CSV above
- `evolution_paths` view — recursive CTE that walks from root to all leaf nodes,
  producing (root_id, intermediate_id, final_id, depth, path_as_string)
- `branching_evolutions` view — filters to chains where a species has >1 evolves_into_id

### Implementation steps

1. **Extract chain URLs** — read all `pokemon-species__*.json` from `.api_cache/`,
   collect unique `evolution_chain.url` values (already present in cache)
2. **Add `fetch_evolution_chains()` coroutine** to `fetch_pokemon_data.py` — reuses
   existing `fetch()` + local JSON caching, so re-runs cost nothing
3. **Parse nested JSON** — PokéAPI evolution chain JSON is a tree:
   `chain.species → chain.evolves_to[] → chain.evolves_to[]`. Walk it recursively,
   flattening each parent→child edge into one CSV row with all trigger conditions
4. **Write `evolution_chains.csv`** from the flattened list
5. **Add to `build_db.py`** — new `raw_evolution` table + `evolution_paths` recursive view
6. **Kids app** — new `render_evolution_tab()` in `app.py`, add "🔗 Evolution" tab
   alongside Overview + Physical Traits. Render each step as an HTML sprite chain
   (`img → arrow → img → arrow → img`) with branch points shown as diverging rows
7. **Adult app** — new `dashboard/pages/8_🔗_Evolution_Chains.py` with
   Plotly `go.Sankey` diagram (all chains simultaneously) + searchable chain viewer

### Complexity: MEDIUM

The fetch and CSV generation are straightforward (the `fetch()` + caching pattern is
already proven). The complexity is in parsing: PokéAPI's evolution JSON is irregular.
Edge cases that need explicit handling:
- **No evolution** (Kangaskhan, all legendaries) → 0 rows in CSV, display "Does not evolve"
- **Multi-branch** (Tyrogue → 3, Eevee → 8, Wurmple → 2 paths)
- **Condition-based** triggers: held item (Slowpoke + King's Rock), location (Leafeon
  in mossy lure), time of day (Espeon/Umbreon), move known (Mime Jr. → Mr. Mime),
  gender (Burmy → Wormadam/Mothim), happiness (Togepi → Togetic)
- **Mega evolutions** — listed in PokéAPI but are battle-only, not true evolutions;
  these should be excluded from the chain CSV

### Risks
- Mega/Gigantamax forms appearing in chain data — need an explicit exclusion list
- Some chains reference Pokémon numbers above 1025 (future DLC) — guard with a max-number filter
- Recursive CTE performance in DuckDB — test with the Eevee chain (depth 2, 9 nodes)

### Which repo
Both. Evolution sub-tab in `pokemon-pokedex`, full chart page in `pokemon-analytics`.

---

## Idea 4 — Learnset / Move Coverage Explorer

### Goal
Answer "What moves can Pikachu learn?" and "What types can Charizard hit
super-effectively with its moveset?" — unlocking competitive team-building analysis.

### Data requirements

**Learnset data (0 new fetches):**
Move names + learn methods are already stored in every `pokemon__*.json` in `.api_cache/`:
```json
poke["moves"] = [
  {
    "move": {"name": "thunder-punch"},
    "version_group_details": [
      {"level_learned_at": 0, "move_learn_method": {"name": "machine"}, "version_group": {"name": "scarlet-violet"}}
    ]
  }
]
```
A new script `extract_learnsets.py` can write `pokemon_moves.csv` with zero network calls.

**New CSV — `pokemon_moves.csv`:**
```
species_id, move_name, learn_method, min_level, version_group
```
~50,000–80,000 rows (average 60 moves per Pokémon × 1,025 species).
Filter to a single, current version group (e.g., `scarlet-violet`) to control size.

**Move detail data (~900 new fetches):**
`GET /move/{id}` for each distinct move. At 30 concurrency: ~30 seconds.

**New CSV — `moves.csv`:**
```
move_id, name, type, power, accuracy, pp, damage_class, effect_short, priority
```
~900 rows.

**New DuckDB views:**
- `pokemon_learnset` — joins `pokemon_moves` → `moves` for full details per species
- `move_type_coverage` — 3-way join: `pokemon_moves` → `moves` → `type_effectiveness`
  — answers "what defending types does this Pokémon's moveset hit super-effectively?"
- `best_coverage_moves_by_type` — for each type, which TMs give the broadest coverage?

### Implementation steps

1. Write `extract_learnsets.py` — reads `pokemon__*.json`, filters to latest version
   group, writes `pokemon_moves.csv` (no network)
2. Add `fetch_move_details()` coroutine to `fetch_pokemon_data.py` (or standalone script)
3. Write `moves.csv`
4. Add `raw_moves`, `raw_pokemon_moves` tables + `pokemon_learnset`, `move_type_coverage`
   views to `build_db.py`
5. **Kids app** — "⚡ Moves" sub-tab: level-up moves shown as a compact table
   (sorted by level), TM/HM moves as colour-coded type badges
6. **Adult app** — `9_⚡_Learnsets.py`: dual search (by Pokémon → what moves?
   and by move → which Pokémon learn it?), coverage heatmap

### Complexity: MEDIUM-HIGH

The data extraction is mechanical. The challenge is query design: computing
"what types can this team super-effectively cover" requires joining across
three tables with multiplier logic. Version-group filtering is also nuanced —
decide upfront whether to store all historical moves or only current-gen.

### Risks
- `pokemon_moves.csv` without version filtering could exceed 500k rows — always filter
- Moves with null `power` (status moves) must be handled gracefully in coverage queries
- The 3-way coverage join is expensive on 80k rows × 18 types; consider materialising
  as a table rather than a view

### Which repo
Both. Simplified move list in `pokemon-pokedex`, full learnset + coverage analysis in
`pokemon-analytics`.

---

## Idea 5 — Ability Insights & Hidden Ability Rarity

### Goal
Tell kids what each ability actually does ("Overgrow boosts Grass moves when HP is low")
and show adults which hidden abilities are rarest and which types cluster around them.

### Data requirements

**New API calls:** ~307 — `GET /ability/{id}` for each distinct ability.
At 30 concurrency: ~10–15 seconds. Fully cacheable.

**New CSV — `ability_detail.csv`:**
```
ability_id, name, effect_short, flavor_text, generation_introduced
```
307 rows.

**Existing data reused:**
`Pokemon_Abilities.csv` (2,575 rows) already maps `Number → AbilityName → IsHidden`.
Join `ability_detail` ON `name` to enrich with effect text — no new join table needed.

**New DuckDB objects:**
- `raw_ability_detail` table
- `abilities_enriched` view — `Pokemon_Abilities JOIN ability_detail JOIN pokemon_base`
  → one row per (Pokémon, ability) with effect text, type, and generation

### Implementation steps

1. Add `fetch_ability_details()` coroutine to `fetch_pokemon_data.py` or write
   `extract_ability_details.py` (reads from cache if already fetched, else fetches)
2. Write `ability_detail.csv`
3. Add `raw_ability_detail` table + `abilities_enriched` view to `build_db.py` in
   both repos
4. **Kids app** — expand the Abilities section on the Physical Traits tab: render
   each ability badge with a tooltip-style one-sentence effect below it
5. **Adult app** — new `8_⚡_Abilities.py`:
   - Searchable ability browser (all 307 abilities with effect text + which Pokémon have it)
   - Hidden ability rarity chart (how many Pokémon have each hidden ability?)
   - Ability × Type heatmap (does Intimidate cluster around Dark/Normal types?)
   - "Defensive Ability Wall" — rank abilities by how many common super-effective
     hits they negate (Levitate, Flash Fire, Volt Absorb, etc.)

### Complexity: LOW-MEDIUM

This is the most self-contained of the remaining ideas. The fetch, CSV, and enriched
view are all straightforward. The adult analytics page is the most interesting design
challenge — especially the ability-type affinity heatmap.

### Risks
- Ability effect text in PokéAPI occasionally contains HTML entities or game-specific
  jargon — may need a light cleaning pass before display
- Some abilities have changed effect between generations (pre-Gen 6 Intimidate had
  different mechanics) — use `flavor_text` for in-game text, not `effect`

### Which repo
Both. Effect text in kids' Physical Traits tab; full analytical page in adult analytics.

---

## Idea 6 — Team Builder / Type Coverage Advisor

### Goal
Select up to 6 Pokémon, instantly see: (1) what types your team's moves cover
super-effectively, (2) what types your team is collectively weak to. The "team
synergy check" every trainer does mentally, automated.

### Data requirements

**Zero new API calls, zero new CSVs.**
Everything needed already exists in DuckDB:
- `type_matchup_matrix` view — full 18×18 offense multipliers
- `pokemon_base` view — types per Pokémon
- With Idea 4 done: `move_type_coverage` — what types each Pokémon can hit SE

Without Idea 4, a simplified version uses only type-based coverage (a Fire-type
Pokémon is assumed to always have a Fire move that can hit Grass/Bug/Steel/Ice).

**New session state:** `st.session_state["team"] = []` (list of ≤6 Pokédex numbers)

**New DuckDB query (inline, not a view):**
```sql
-- Offensive coverage: what can this team hit SE?
SELECT DISTINCT tm.DefendingType
FROM type_matchup_matrix tm
WHERE tm.AttackingType IN (<team_types>)
  AND tm.Multiplier = 2.0

-- Defensive weakness: what threatens this team?
SELECT tm.AttackingType, COUNT(*) AS members_weak
FROM type_matchup_matrix tm
WHERE tm.DefendingType IN (<team_types>)
  AND tm.Multiplier = 2.0
GROUP BY tm.AttackingType
ORDER BY members_weak DESC
```

### Implementation steps

1. **Adult app only** — new `10_🛡️_Team_Builder.py`
2. Multiselect widget: pick up to 6 Pokémon from `pokemon_base` (searchable)
3. For each selected Pokémon: display small sprite, name, type badges
4. Coverage heatmap: 18 type cells, colour-coded (green=covered SE, grey=neutral,
   orange=resisted, red=team has a member weak to this)
5. Weakness summary table: which attacking types threaten the most team members?
6. Optional (requires Idea 4): toggle between "type-only coverage" and
   "actual move coverage" based on learnset data

### Complexity: LOW

All data is in place. This is purely UI + DuckDB query work. The main design challenge
is the dual-type composite matchup: a Water/Flying Pokémon defending against Electric
takes ×2 from Electric (both types share the weakness) — handle by taking the
product of both type multipliers.

### Risks
- Dual-type defensive product can produce ×4 weak (very common) — highlight visually
- The "type-only" assumption (Fire Pokémon always has a Fire move) is wrong for some
  Pokémon (Slugma that only knows Normal moves) — caveat prominently

### Which repo
Adult (`pokemon-analytics`) as the primary home. A simplified "type match"
widget could appear in `pokemon-pokedex` Physical Traits tab (BR-004).

---

## Architecture Upgrade — DuckDB-WASM + React

### Goal
Achieve the original Microsoft Fabric inspiration: a true free-form pivot / semantic
layer experience where users drag dimensions, apply cross-filters, and get instant
responses — without a page reload.

### Why the current stack hits its ceiling
Streamlit re-executes the entire Python script on every user interaction. For a
pre-defined report (fixed charts, fixed filters), this is acceptable. For a
free-form pivot where users pick arbitrary dimensions and slices simultaneously,
each interaction takes 1–3 seconds for Python rerun + DuckDB query + Streamlit
re-render. Cross-filter (clicking one chart to filter all others) is not natively
supported in Streamlit.

### What DuckDB-WASM enables
DuckDB compiled to WebAssembly runs entirely inside the browser. The full query
engine — including JOINs, window functions, GROUP BYs — executes client-side with
no server round-trip. Queries on the Pokémon dataset (≤50k rows) return in
< 50ms in-browser, enabling true interactive pivoting.

### High-level implementation path

1. **Build step** — convert all DuckDB views to Parquet files:
   ```bash
   python3 -c "
   import duckdb
   con = duckdb.connect('pokemon.duckdb', read_only=True)
   for view in ['pokemon_base', 'type_matchup_matrix', 'stat_summary_by_type', ...]:
       con.execute(f\"COPY {view} TO 'public/{view}.parquet' (FORMAT PARQUET)\")
   "
   ```
2. **Static hosting** — Parquet files go in `public/` and are served via GitHub Pages
   (the repo already has a public GitHub URL)
3. **React bootstrap** — `npm create vite@latest pokemon-wasm -- --template react`
   with `@duckdb/duckdb-wasm` dependency
4. **DuckDB initialisation in-browser:**
   ```javascript
   const duckdb = await createDuckDb();
   await duckdb.registerFileURL('pokemon_base.parquet', '/pokemon_base.parquet');
   const result = await duckdb.query('SELECT * FROM read_parquet(...)');
   ```
5. **Component library** — Recharts (simpler) or D3 (more control) for the charts;
   React state management for cross-filter (Redux or Zustand)
6. **Port each page** — Stats by Type, Type Effectiveness, Pokemon Explorer each
   become a React component with DuckDB SQL queries replacing DuckDB Python calls

### Decision criteria for the upgrade

| Factor | Stay with Streamlit | Upgrade to WASM + React |
|---|---|---|
| Interaction latency | 1–3s per filter change | < 50ms |
| Cross-filtering | Not supported natively | Native |
| Free-form pivot | Fixed reports only | Full drag-and-drop |
| Development speed | Very fast | Slower (full JS stack) |
| Deployment | Streamlit Community Cloud (free) | GitHub Pages (free) |
| Maintenance | Python only | Python (ETL) + JavaScript (UI) |

**Recommendation:** Build Ideas 3, 4, 5, 6 in Streamlit first to validate the full
feature set and data model. Then evaluate the WASM upgrade once analytics requirements
are stable. The Parquet export step (above) is the bridge — Parquet files work with
both DuckDB-Python (current) and DuckDB-WASM (future).
