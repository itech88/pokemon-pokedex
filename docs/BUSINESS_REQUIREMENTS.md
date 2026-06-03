# Business Requirements Document
## Pokémon Visual Pokédex Platform

**Version:** 1.0  
**Date:** June 2026  
**Repos:** `itech88/pokemon-pokedex` (kids) · `itech88/pokemon-analytics` (adult)  
**Status:** Active development — Phase 2 (Physical Traits) complete

---

## Purpose

This document defines the business requirements for the Pokémon Pokédex platform using
Gherkin-style Given/When/Then acceptance criteria. Each requirement is written as a
user story supported by concrete, testable scenarios. These requirements drive feature
development, test design, and architectural decisions.

**Primary audience:** Young Pokémon fans (ages 6–12) who are learning about Pokémon
for the first time — through the kids Pokédex app.

**Secondary audience:** Adult Pokémon enthusiasts who want analytical insights —
through the adult analytics dashboard.

---

## Requirement Groups

| Group | Focus |
|---|---|
| [BR-001](#br-001-game-first-discovery) | Game-first discovery — pick your game before seeing Pokémon |
| [BR-002](#br-002-visual-recognition-before-text) | Visual recognition — animated sprites before names |
| [BR-003](#br-003-kid-friendly-contextual-explanations) | Kid-friendly contextual explanations of stats |
| [BR-004](#br-004-type-battle-information) | Type battle matchup information |
| [BR-005](#br-005-where-to-catch-it) | Wild encounter location data |
| [BR-006](#br-006-data-accuracy--no-false-locations) | Data accuracy — no misleading location data |
| [BR-007](#br-007-smooth-navigation-and-focus-management) | Smooth navigation and scroll-to-focus behaviour |
| [BR-008](#br-008-ability-transparency) | Ability information — what each ability does |
| [BR-009](#br-009-evolution-information) | Evolution chain display — future requirement |
| [BR-010](#br-010-move-and-coverage-information) | Learnset and type coverage — future requirement |
| [BR-011](#br-011-team-builder) | Team builder — future requirement |
| [BR-012](#br-012-data-pipeline-reliability) | Data pipeline reliability — backend requirements |

---

## BR-001: Game-First Discovery

**User story:**
As a young Pokémon fan, I want to choose my favourite Pokémon game before I see any
Pokémon, so that I only encounter the Pokémon that are new and exciting in that game
— not an overwhelming list of all 1,025 Pokémon at once.

**Rationale:** Children associate Pokémon with specific games (e.g., "I play Sword, I
know the Galar Pokémon"). Filtering by game reduces cognitive overload and creates an
emotional connection between the game and its Pokémon. This is the core navigation
model of the kids app.

```gherkin
Feature: BR-001 Game-First Discovery

  Scenario: Home screen presents games, not a Pokémon list
    Given a user opens the Pokédex app for the first time
    When they arrive at the home screen
    Then they should see game selection cards — not a list of Pokémon
    And they should NOT be able to browse Pokémon until they select a game

  Scenario: Nine games are presented, one for each generation
    Given a user is on the home screen
    When they view the game cards
    Then they should see Generation I through Generation IX
    And each card should show recognisable starters for that game
    And each card should show the game titles (e.g., "Red · Blue · Yellow")

  Scenario: The count of new Pokémon is shown on each game card
    Given a user is on the home screen
    When they read a game card
    Then they should see how many new Pokémon that game introduced
    And the count should be accurate (e.g., Generation I = 151, Generation II = 100)

  Scenario: Selecting a game shows ONLY that game's new Pokémon
    Given a user selects Generation II
    When they enter the Pokédex
    Then they should see only Chikorita, Cyndaquil, Totodile and the other 100 Gen II Pokémon
    And they should NOT see Bulbasaur, Pikachu, or any Generation I Pokémon

  Acceptance Criteria:
    - Home screen has no Pokémon grid — only game selection cards
    - Each generation card is clearly labelled with generation number and game title
    - Pokémon count badge is visible on every card
    - Animated starter sprites play on each card
    - Selecting a game filters the Pokédex to only that generation's Pokémon
```

---

## BR-002: Visual Recognition Before Text

**User story:**
As a child who may not be a confident reader, I want to identify Pokémon by their
animated picture before I rely on reading their name, so that I can find my favourite
Pokémon quickly even if I can't spell it yet.

**Rationale:** The target audience includes early readers (ages 6–8) who recognise
Pikachu by sight, not by spelling. Animated battle sprites are more engaging and
distinctive than static images.

```gherkin
Feature: BR-002 Visual Recognition Before Text

  Scenario: Each card in the grid shows an animated Pokémon sprite
    Given a user is browsing the Generation I Pokédex
    When they view the card grid
    Then every card should display an animated GIF of the Pokémon
    And the GIF should play automatically (not require a click to start)

  Scenario: All card sprites are the same visual size
    Given a user is browsing the card grid
    When they compare any two cards
    Then the sprite display area should be exactly the same size on every card
    And small Pokémon (Caterpie) should not appear disproportionately small
    And large Pokémon (Onix) should not overflow the card bounds

  Scenario: Selecting a Pokémon shows large HD artwork
    Given a user clicks on any Pokémon card
    When the detail panel updates
    Then they should see a large, high-resolution official artwork image
    And the artwork should clearly show the Pokémon's design and colours

  Scenario: The animated battle sprite is shown alongside the artwork
    Given a user has selected a Pokémon
    When they view the Overview tab
    Then both the HD artwork AND the animated battle sprite should be visible
    And the battle sprite should be labelled "Battle sprite"

  Scenario: Game selection cards also use animated sprites
    Given a user is on the home screen
    When they view any generation card
    Then the three starter Pokémon should be shown as animated GIFs
    And they should recognise their favourite starters immediately

  Acceptance Criteria:
    - Every card in the grid displays an animated GIF, no static fallback
    - Sprite display area is fixed at 68×68 pixels with CSS max-width/max-height
    - Detail panel shows HD official artwork (official-artwork CDN URL)
    - Animated battle GIF (showdown CDN URL) is visible in Overview tab
    - All images use image-rendering: pixelated for pixel-art aesthetic
```

---

## BR-003: Kid-Friendly Contextual Explanations

**User story:**
As a child, I want confusing numbers (like "0.7 m" or "CaptureRate: 45") explained
in terms I already understand — like familiar objects and animals — so that the
Pokédex teaches me something meaningful, not just raw data.

**Rationale:** A raw height of "1.7 m" means nothing to a 7-year-old. "About as tall
as a grown-up" is immediately understood. This transforms the app from a data dump
into a genuine learning experience.

```gherkin
Feature: BR-003 Kid-Friendly Contextual Explanations

  Scenario: Height is shown with a relatable real-world comparison
    Given a user views the Physical Traits tab for any Pokémon
    When they read the height
    Then they should see both the metric value (e.g., "0.7 m")
    And a friendly comparison (e.g., "about as tall as a 7-year-old 🧒")

  Scenario: Weight is shown with a relatable real-world comparison
    Given a user views the Physical Traits tab for any Pokémon
    When they read the weight
    Then they should see both the metric value (e.g., "6.9 kg")
    And a friendly comparison (e.g., "about as heavy as a big dog 🐕")

  Scenario: Catch difficulty uses star ratings not raw numbers
    Given a user views the Trainer Facts section
    When they read the catch difficulty
    Then they should see a star rating (e.g., "⭐⭐⭐⭐⭐ Very Easy")
    And a percentage (e.g., "17.6% catch chance")
    And a plain-English hint (e.g., "Higher = easier to catch")

  Scenario: Starting happiness uses emoji-labelled descriptions
    Given a user views the Trainer Facts section
    When they read the starting happiness
    Then they should NOT see a raw number like "70"
    But they should see a description like "😐 Neutral — fairly content from the start"
    And the raw score should be shown as secondary information (e.g., "Score: 70/255")

  Scenario: XP reward uses a visual bar with plain-language label
    Given a user views the Trainer Facts section
    When they read the XP reward
    Then they should see a bar showing the XP relative to the maximum
    And a plain label like "low XP", "average XP", or "lots of XP! 🏆"

  Scenario: Growth rate uses icons and plain words
    Given a user views the Trainer Facts section
    When they read the growth rate
    Then they should see an icon (⚡ for fast, 🐢 for slow) and plain words
    And NOT see technical labels like "medium-slow" without explanation

  Scenario: Gender ratio is shown as a visual bar not a raw number
    Given a user views the Body Facts section for a Pokémon with gender
    When they read the gender information
    Then they should see a pink/blue split bar proportional to the ratio
    And clear labels like "♀ 12%" and "♂ 88%"
    And genderless Pokémon should show "⚲ Genderless" instead

  Acceptance Criteria:
    - All heights have a corresponding real-world comparison from HEIGHT_COMPS table
    - All weights have a corresponding real-world comparison from WEIGHT_COMPS table
    - CaptureRate (0–255) is always converted to a star rating + percentage
    - BaseHappiness is always converted to a grumpy/neutral/happy label with emoji
    - Raw numbers are shown as secondary info, never as the primary display
```

---

## BR-004: Type Battle Information

**User story:**
As a young trainer who is learning how Pokémon battles work, I want to know which
types my Pokémon is strong against and weak to, so that I can make smart choices
and win more battles.

**Rationale:** Type matchups are fundamental to Pokémon strategy. A child who knows
"Bulbasaur is weak to Fire" will play better and feel more confident. This bridges
the gap between "I like this Pokémon" and "I understand how it works."

```gherkin
Feature: BR-004 Type Battle Information

  Scenario: Strong-against types are shown with clear visual indicator
    Given a user views the Type Battle Info section for Bulbasaur
    When they read the offensive matchups
    Then they should see "🔴 Strong against:" followed by type badges
    And those badges should include Ground, Rock, and Water

  Scenario: Weak-to types are shown with clear visual indicator
    Given a user views the Type Battle Info section for Bulbasaur
    When they read the defensive matchups
    Then they should see "🔵 Weak to:" followed by type badges
    And those badges should include Flying, Poison, Bug, Fire, and Ice

  Scenario: Resistance types are shown
    Given a user views the Type Battle Info section
    When they read the defensive matchups
    Then they should see "🟡 Resists hits from:" followed by type badges

  Scenario: Immunities are shown when the Pokémon has them
    Given a user views the Type Battle Info section for a Ghost-type Pokémon
    When they read the defensive matchups
    Then they should see "⚫ Immune to (no damage!):" followed by Normal and Fighting

  Scenario: Type badges use the official type colour scheme
    Given a user views any type badge in the app
    When they see a Fire badge
    Then it should be orange (#EE8130)
    And a Water badge should be blue (#6390F0)
    And a Grass badge should be green (#7AC74C)

  Scenario: The section caption explains the context
    Given a user views the Type Battle Info section for Bulbasaur
    When they read the section header
    Then they should see text like "How Bulbasaur's Grass / Poison type performs in battles"

  Acceptance Criteria:
    - StrongAgainst, WeakAgainst, ResistantTo, ImmuneFrom all displayed
    - Data sourced from Types_Attributes.csv joined via pokemon_traits DuckDB view
    - Type badges match the TYPE_COLORS dict (18 colours defined in db.py)
    - Immune section only rendered when ImmuneFrom is non-empty
    - Caption always names the Pokémon and its type(s)
```

---

## BR-005: Where to Catch It

**User story:**
As a player who wants to catch a specific Pokémon, I want to know which game regions
and specific areas I can find it in, so that I know where to look rather than
wandering randomly.

**Rationale:** "Where do I find [Pokémon]?" is one of the most common questions
Pokémon players ask. This replaces a web search with an in-app answer.

```gherkin
Feature: BR-005 Where to Catch It

  Scenario: Wild Pokémon show expandable region sections
    Given a user views the "Where to Find It" section for Rattata
    When they read the location data
    Then they should see expandable sections labelled by region (Kanto, Johto, etc.)
    And each section should list specific area names
    And each area should show an encounter rate percentage

  Scenario: Regions are collapsed by default to avoid overwhelming the user
    Given a user views the "Where to Find It" section for Magikarp
    When the section first loads
    Then the region sections should be collapsed
    And the user should be able to expand each region independently

  Scenario: The number of areas per region is shown on the expander
    Given a user views Rattata's location section
    When they see the Kanto expander
    Then they should see "📍 Kanto (N areas)" where N is the actual count

  Scenario: Encounter rate is shown per area
    Given a user expands a region section
    When they view the area list
    Then each row should show the area name and its encounter rate
    And higher encounter rates should indicate more common spawns

  Scenario: Pokémon not found in the wild show a clear message
    Given a user views the "Where to Find It" section for Bulbasaur
    When the location section loads
    Then they should NOT see any region expanders
    And they should see a message explaining the Pokémon is obtained another way
    (e.g., "This Pokémon can't be found in the wild — it must be obtained another way!")

  Acceptance Criteria:
    - Locations sourced from raw_locations DuckDB table (Pokemon_Locations.csv)
    - Regions are grouped and shown as st.expander widgets
    - Columns displayed: Area Name, Encounter % (renamed from EncounterRate)
    - Empty location set → info box with clear plain-English message
    - Max 3 region columns displayed side by side
```

---

## BR-006: Data Accuracy — No False Locations

**User story:**
As a player who trusts this Pokédex, I expect the location data to be accurate —
a Pokémon that cannot be caught in the wild should never be listed as a wild
encounter, so that I am not sent on a frustrating and impossible search.

**Rationale:** The Charizard bug (June 2026) showed that PokéAPI's raw encounter
data includes gift events and special overworld mechanics that are not true wild
catches. If a child reads "Charizard can be found in Kanto Route 12" and tries
to find it, they will be confused and lose trust in the app.

```gherkin
Feature: BR-006 Data Accuracy — No False Locations

  Scenario: Charizard is never shown as a wild encounter — regression test
    Given the location data has been generated from PokéAPI
    When I check Charizard's (number 6) location rows
    Then there should be exactly 0 rows
    And the Physical Traits tab should show the "not found in the wild" message

  Scenario: Gift-only starter Pokémon have no wild location data
    Given the location data has been generated from PokéAPI
    When I check Bulbasaur (1), Charmander (4), and Squirtle (7)
    Then each should have exactly 0 location rows
    # These are received as gifts from NPCs, not caught in the wild

  Scenario: Evolved starters that cannot be caught have no wild location data
    Given the location data has been generated from PokéAPI
    When I check Venusaur (3), Charizard (6), and Blastoise (9)
    Then each should have exactly 0 location rows

  Scenario: The WILD_METHODS filter excludes known non-wild encounter types
    Given the fetch_pokemon_data.py script runs with the WILD_METHODS filter
    When encounters are processed
    Then "gift" method encounters should be excluded
    And "overworld-flying-special" encounters should be excluded
    And "island-scan" encounters should be excluded
    And "snag" (Colosseum) encounters should be excluded

  Scenario: The WILD_METHODS filter does not over-exclude genuine wild encounters
    Given the fetch_pokemon_data.py script runs with the WILD_METHODS filter
    When encounters are processed
    Then "walk" encounters should be included
    And "cave-spots" encounters (e.g., Drilbur) should be included
    And "horde" encounters (Gen VI) should be included
    And "sos-encounter" encounters (Gen VII) should be included

  Scenario: No Pokémon appears in more than 15 areas all at exactly 100% rate
    # This pattern is a symptom of gift/event data leaking in (original Charizard bug was 25 areas at 100%)
    Given the location data has been generated
    When I check for suspiciously uniform encounter rates
    Then no Pokémon should appear in 15 or more areas where ALL rates are exactly 100%
    Unless it is a known fishing-only species like Magikarp (where 100% old-rod is legitimate)

  Acceptance Criteria:
    - WILD_METHODS constant defines exactly which encounter methods are valid
    - The filter is applied in _process_one() before any encounter row is written
    - test_pokemon_data.py test_10 must pass: Charizard, Venusaur, Blastoise have 0 rows
    - test_pokemon_data.py test_11 must pass: Drilbur, Magikarp, Heracross have >0 rows
    - test_ui.py test_charizard_not_in_wild_locations must pass
    - test_ui.py test_rattata_has_valid_wild_locations must pass
```

---

## BR-007: Smooth Navigation and Focus Management

**User story:**
As a user browsing many Pokémon by clicking cards, I expect the page to immediately
focus on the Pokémon I selected — showing me the detail panel at the top of the
screen — so that I do not have to manually scroll up after every selection.

**Rationale:** Without automatic scroll-to-top, a user who clicks a card while scrolled
500px into the grid will see the card update but still be looking at the grid, not
the detail panel. This creates a broken user experience, especially for children who
may not instinctively know to scroll up.

```gherkin
Feature: BR-007 Smooth Navigation and Focus Management

  Scenario: Clicking a card scrolls to the top of the page
    Given a user has scrolled 2,000 pixels into the Pokémon card grid
    When they click any "View →" card button
    Then the page should scroll to the top within 1 second
    And the scrollTop position of the main content area should be less than 150 pixels
    And the Pokémon detail panel should be fully visible

  Scenario: The scroll happens reliably on repeated clicks
    Given a user clicks Pokémon card A (page scrolls to top)
    And then scrolls back down 2,000 pixels
    When they click Pokémon card B
    Then the page should scroll to the top again
    And the behaviour should be identical regardless of how many times it is repeated

  Scenario: Surprise me button also scrolls to the top
    Given a user has scrolled 2,000 pixels into the card grid
    When they click "🎲 Surprise me!" in the sidebar
    Then the page should scroll to the top within 1 second
    And the selected Pokémon's detail panel should be visible

  Scenario: The scroll is instant, not animated
    Given a user clicks a card while scrolled down
    When the scroll happens
    Then the page should jump immediately to the top (instant scroll)
    And NOT use a slow smooth animation that could be interrupted by DOM rendering

  Scenario: Navigating between generations resets the scroll position
    Given a user is scrolled down in Generation I
    When they click "← All Games" and then select Generation II
    Then they should start at the top of the Generation II Pokédex
    And not be mid-page from the previous generation

  Technical implementation notes:
    - scroll target: [data-testid="stMain"] (confirmed via DOM inspection)
    - scroll method: .scrollTop = 0 (instant, not .scrollTo({behavior:'smooth'}))
    - cache-busting: unique comment /* N */ in JS prevents Streamlit iframe caching
    - retry strategy: fire at 0ms, 200ms, 500ms to catch post-render DOM reflows

  Acceptance Criteria:
    - test_ui.py test_card_click_scrolls_to_top must pass (scrollTop < 150px)
    - test_ui.py test_surprise_me_scrolls_to_top must pass (scrollTop < 150px)
    - Scroll must work consistently across repeated card clicks (no stale iframe)
```

---

## BR-008: Ability Transparency

**User story:**
As a young trainer, I want to know what each of my Pokémon's abilities does in plain
English, so that I can understand its strengths and use it effectively in battles.

**Status:** Partially implemented (ability names and hidden ability badge shown).
Effect text requires Phase 2 Idea 5 (307 new API fetches for ability detail endpoints).

```gherkin
Feature: BR-008 Ability Transparency

  Scenario: Regular abilities are clearly identified — IMPLEMENTED
    Given a user views the Physical Traits tab for Bulbasaur
    When they view the Abilities section
    Then they should see "Overgrow" displayed as a clearly styled badge
    And the badge should be visually distinct (green colour)

  Scenario: Hidden abilities are marked as special — IMPLEMENTED
    Given a user views the Physical Traits tab for Bulbasaur
    When they view the Abilities section
    Then they should see "✨ Chlorophyll (Hidden)" in a gold/yellow badge
    And it should be clear that hidden abilities are harder to obtain

  Scenario: Each ability shows a one-sentence plain-English effect — FUTURE (Idea 5)
    Given Idea 5 (ability_detail.csv) has been implemented
    When a user views the Abilities section for Bulbasaur
    Then below "Overgrow" they should see text like:
      "Powers up Grass-type moves when the Pokémon's HP is low"
    And below "Chlorophyll" they should see:
      "Boosts the Pokémon's Speed stat in harsh sunlight"

  Scenario: The Abilities section has an explanatory caption — IMPLEMENTED
    Given a user views the Abilities section
    When they read the header area
    Then they should see text explaining what abilities are
    (e.g., "Abilities are special powers that help Pokémon in battle!")

  Acceptance Criteria (current):
    - Ability names displayed as styled HTML span badges
    - Regular abilities: green (#2E7D32) background, white text
    - Hidden ability: gold (#F9A825) background, dark text, "✨ (Hidden)" suffix
    - Section caption always shown
  Acceptance Criteria (Idea 5):
    - ability_detail.csv loaded into raw_ability_detail DuckDB table
    - Effect text shown as small italic text below each ability badge
    - Effect text truncated to one sentence maximum
```

---

## BR-009: Evolution Information *(Future — Idea 3)*

**User story:**
As a young Pokémon fan, I want to see how my Pokémon evolves — what it turns into,
and what I need to do to make it evolve — so that I can plan ahead and raise my
Pokémon to its final, strongest form.

**Status:** Not yet implemented. Requires ~541 new API fetches. See [IDEAS.md](IDEAS.md#idea-3--evolution-chain-trees).

```gherkin
Feature: BR-009 Evolution Information (Future)

  Scenario: Pokémon that evolve show their full evolution chain
    Given Idea 3 has been implemented
    And a user has selected Bulbasaur
    When they click the "🔗 Evolution" tab
    Then they should see: Bulbasaur → Ivysaur → Venusaur
    And each step should show the Pokémon's animated sprite
    And the evolution trigger should be shown (e.g., "Level 16")

  Scenario: Branching evolutions show all paths
    Given Idea 3 has been implemented
    And a user has selected Eevee
    When they view the Evolution tab
    Then they should see all 8 evolution options (Vaporeon, Jolteon, Flareon, etc.)
    And the trigger for each branch should be displayed (Water Stone, Thunder Stone, etc.)

  Scenario: Condition-based evolutions show their conditions
    Given Idea 3 has been implemented
    And a user has selected Togepi
    When they view the Evolution tab
    Then they should see "Togetic" as the next evolution
    And the condition should read "High friendship" or "Happiness"

  Scenario: Pokémon with no evolution show a clear message
    Given Idea 3 has been implemented
    And a user has selected Mewtwo
    When they view the Evolution tab
    Then they should see "Does not evolve"
    And no evolution arrows or sprites should be shown

  Acceptance Criteria (Idea 3):
    - evolution_chains.csv generated with all fields
    - DuckDB view evolution_paths walks chains recursively
    - Kids app: HTML sprite chain with connecting arrows
    - No Mega Evolution forms shown (battle-only, filtered out)
```

---

## BR-010: Move and Coverage Information *(Future — Idea 4)*

**User story:**
As a trainer planning my team, I want to know what moves my Pokémon can learn and
what types those moves can hit, so that I can build a team with good type coverage.

**Status:** Not yet implemented. Learnset extraction requires 0 new fetches; move
detail requires ~900 fetches. See [IDEAS.md](IDEAS.md#idea-4--learnset--move-coverage-explorer).

```gherkin
Feature: BR-010 Move and Coverage Information (Future)

  Scenario: Level-up moves are shown in a simple table
    Given Idea 4 has been implemented
    And a user has selected Pikachu
    When they view the "⚡ Moves" tab
    Then they should see a table of moves Pikachu learns by levelling up
    And each row should show: Level, Move Name, Type badge, Power, Accuracy

  Scenario: TM moves are shown as type-coloured badges
    Given Idea 4 has been implemented
    When a user views the Moves tab
    Then TM/HM moves should be displayed as compact badges grouped by type

  Scenario: Type coverage is shown for the Pokémon's moveset
    Given Idea 4 has been implemented
    When a user views the Moves tab
    Then they should see which defending types this Pokémon can hit super-effectively
    And which defending types it cannot cover effectively

  Acceptance Criteria (Idea 4):
    - pokemon_moves.csv extracted from cache (0 network, ~80k rows)
    - moves.csv fetched from API (~900 calls, ~900 rows)
    - Kids: level-up table + TM badge grid + coverage summary
    - Adult: full learnset browser + reverse lookup (which Pokémon learn this move?)
```

---

## BR-011: Team Builder *(Future — Idea 6)*

**User story:**
As a player building my team, I want to select up to 6 Pokémon and see at a glance
which types my team covers and which types threaten it, so that I can build a
well-balanced team without doing the maths myself.

**Status:** Not yet implemented. Requires zero new data. See [IDEAS.md](IDEAS.md#idea-6--team-builder--type-coverage-advisor).

```gherkin
Feature: BR-011 Team Builder (Future)

  Scenario: User can select up to 6 Pokémon for their team
    Given Idea 6 has been implemented
    When a user opens the Team Builder page
    Then they should be able to search for and add up to 6 Pokémon
    And adding a 7th should either replace a slot or show a warning

  Scenario: Offensive type coverage is shown as a coloured grid
    Given a user has built a team of 6 Pokémon
    When they view the coverage summary
    Then they should see all 18 defending types
    And green cells indicate the team can hit that type super-effectively
    And grey cells indicate neutral coverage
    And red cells indicate no team member hits that type super-effectively

  Scenario: Defensive weaknesses are highlighted
    Given a user has built a team
    When they view the weakness summary
    Then they should see which attacking types threaten 2 or more team members
    And these should be highlighted as a priority to address

  Acceptance Criteria (Idea 6):
    - Zero new API calls or CSVs needed
    - DuckDB query uses existing type_matchup_matrix view
    - Dual-type defensive product correctly calculated (min of both type multipliers)
    - Team state managed in Streamlit session state
```

---

## BR-012: Data Pipeline Reliability

**User story:**
As the developer maintaining this platform, I need the data pipeline to be reliable,
testable, and self-healing, so that any change to the upstream PokéAPI or my ETL
scripts can be caught before it reaches users.

```gherkin
Feature: BR-012 Data Pipeline Reliability

  Scenario: Re-running the ETL scripts is safe (idempotent)
    Given the CSVs and DuckDB already exist
    When a developer runs fetch_pokemon_data.py again
    Then the existing CSVs should be overwritten with fresh (but identical) data
    And the DuckDB should be rebuilt correctly from the new CSVs

  Scenario: The ETL is fast on repeated runs due to local caching
    Given the .api_cache/ directory is populated from a previous run
    When a developer runs fetch_pokemon_data.py
    Then the script should complete in under 30 seconds
    And it should make zero network calls to PokéAPI

  Scenario: All 51 backend unit tests pass before a CSV is committed
    Given a developer has regenerated the CSVs
    When they run python -m pytest test_pokemon_data.py
    Then all 51 tests should pass
    And any failure should block the commit

  Scenario: All 8 smoke tests pass before a dashboard change is committed
    Given a developer has changed a dashboard page
    When they run python -m pytest test_dashboard_smoke.py
    Then all 8 smoke tests should pass
    And any Streamlit exception should block the commit

  Scenario: All 10 E2E tests pass before any Pokédex change is committed
    Given a developer has changed the kids Pokédex app or its data
    When they run python -m pytest test_ui.py
    Then all 10 Playwright tests should pass
    And the Charizard and Rattata location tests must pass specifically

  Scenario: The DuckDB auto-builds from CSVs on first launch
    Given the pokemon.duckdb file does not exist
    When a user launches the Streamlit app for the first time
    Then the app should build the database automatically
    And the user should not see any error messages
    And the build should complete before the first page renders

  Acceptance Criteria:
    - test_pokemon_data.py: 51 passing (validates all 6 CSVs)
    - test_dashboard_smoke.py: 8 passing (adult dashboard pages)
    - test_ui.py: 10 passing (kids Pokédex E2E)
    - All tests run without network access (cache-based)
    - db.py get_con() auto-builds DuckDB if file absent
    - Both repos have requirements.txt with pinned dependency versions
```

---

## Pre-Commit Checklist

Before every `git push` to either repository, the following must pass:

```
pokemon-analytics/  (adult analytics)
  □ python -m pytest test_pokemon_data.py -q      → 51 passed
  □ python -m pytest test_dashboard_smoke.py -q   → 8 passed
  □ python build_db.py                            → no errors

pokemon-pokedex/  (kids Pokédex)
  □ python -m pytest test_ui.py -q                → 10 passed
  □ Verify docs/ is up to date if architecture changed
```

Any test failure is a hard block. No exceptions.

---

## Glossary

| Term | Definition |
|---|---|
| Base form | A Pokémon's canonical form (e.g., Charizard), as opposed to Mega, Gigantamax, or regional variant forms |
| WILD_METHODS | The allowlist of 35 PokéAPI encounter method names that represent genuine wild Pokémon encounters (defined in fetch_pokemon_data.py) |
| Semantic layer | The DuckDB views that transform raw CSV data into business-ready queries — analogous to a Microsoft Fabric semantic model |
| Generation | One of 9 main Pokémon game generations, each introducing a set of new Pokémon and regions |
| Session state | Streamlit's in-memory key-value store that persists between page reruns within a single browser session |
| DuckDB-WASM | WebAssembly build of DuckDB that runs entirely in the browser — the target architecture for the free-form pivot upgrade path |
