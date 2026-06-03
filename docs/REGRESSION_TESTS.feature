# Pokémon Pokédex — Regression Test Suite
# Gherkin / Behaviour-Driven Development specification
#
# This file is the BDD contract for the pokemon-pokedex application.
# Every scenario maps to an automated test in test_ui.py (Playwright E2E)
# or test_pokemon_data.py (Python unit tests in the pokemon-analytics repo).
# All scenarios in this file MUST pass before any GitHub commit is pushed.
#
# Run backend tests:  python -m pytest test_pokemon_data.py -v         (in pokemon-analytics/)
# Run UI tests:       python -m pytest test_ui.py -v                   (in pokemon-pokedex/)
# Run all:            python -m pytest test_pokemon_data.py test_dashboard_smoke.py test_ui.py -v

# ============================================================================
# FEATURE: Game Selection Landing Screen
# ============================================================================

Feature: Game Selection Landing Screen
  As a young Pokémon fan
  I want to see all Pokémon games on the home screen
  So that I can pick the game I know and love before seeing any Pokémon

  Background:
    Given the Pokédex application is running
    And I am on the home screen

  Scenario: Landing page displays all nine game generations
    When I view the landing page
    Then I should see exactly 9 game selection cards
    And each card should have an "Explore Generation" button

  Scenario: Each game card shows the correct generation title
    When I view the landing page
    Then I should see "Generation I" on one card
    And "Generation II" on another card
    And "Generation III" through "Generation IX" on the remaining cards

  Scenario: Each game card shows the game subtitle
    When I view the Generation I card
    Then I should see the subtitle "Red · Blue · Yellow"

  Scenario: Each game card displays the number of new Pokémon introduced
    When I view any game card
    Then I should see a badge containing "new Pokémon"
    And the count should be greater than zero

  Scenario: Each game card shows three starter Pokémon animated sprites
    When I view the Generation I card
    Then I should see animated GIF images of Bulbasaur, Charmander, and Squirtle

  Scenario: Each game card has a legendary Pokémon background watermark
    When I view the Generation I card
    Then the card background should incorporate Mewtwo's official artwork

  Scenario: Clicking a generation card navigates to that generation's Pokédex
    When I click the "Explore Generation I →" button
    Then I should see the heading "Generation I"
    And I should see Pokémon numbered "#0001" in the card grid

  Scenario: Clicking Generation II card shows only Generation II Pokémon
    When I click the "Explore Generation II →" button
    Then I should see Pokémon starting from "#0152" (Chikorita)
    And I should not see "#0001" (Bulbasaur) in the grid


# ============================================================================
# FEATURE: Generation Pokédex Navigation
# ============================================================================

Feature: Generation Pokédex Navigation
  As a young Pokémon fan
  I want to browse only the Pokémon introduced in my chosen game
  So that the list isn't overwhelming and I can find my favourites

  Background:
    Given the Pokédex application is running
    And I have selected "Generation I"

  Scenario: Pokédex shows only Pokémon introduced in the selected generation
    When I view the Generation I Pokédex
    Then the card grid should show exactly 151 Pokémon
    And all Pokémon should have Generation 1 in their data
    And no Pokémon from later generations should appear

  Scenario: Pokémon are displayed in ascending Pokédex number order
    When I view the Generation I Pokédex
    Then the first card should show "#0001 Bulbasaur"
    And each subsequent card should have a higher Pokédex number

  Scenario: The generation header shows the correct Pokédex number range
    When I view the Generation I Pokédex
    Then I should see "#0001 – #0151" in the page header

  Scenario: Back button returns to game selection screen
    When I click the "← All Games" sidebar button
    Then I should see the game selection screen
    And I should see 9 "Explore Generation" buttons

  Scenario: Surprise me button selects a random Pokémon
    When I click the "🎲 Surprise me!" sidebar button
    Then the detail panel should update to show a different Pokémon
    And the page should scroll to the top

  Scenario: Search by name filters the card grid
    When I type "Char" in the search box
    Then the card grid should show only Charmander, Charmeleon, and Charizard

  Scenario: Legendary filter shows only legendary Pokémon
    When I select "Legendary only" from the Show filter
    Then the card grid should show Mewtwo and Mew
    And should not show Bulbasaur or Pikachu


# ============================================================================
# FEATURE: Pokédex Card Grid
# ============================================================================

Feature: Pokédex Card Grid
  As a user browsing Pokémon
  I want a clear, uniform visual grid I can click to select a Pokémon
  So that navigation is intuitive and I always know which one I have selected

  Background:
    Given the Pokédex application is running
    And I have selected "Generation I"

  Scenario: Card grid shows 8 Pokémon per row
    When I view the Generation I card grid
    Then the cards should be arranged in rows of 8

  Scenario: Each card shows the animated battle sprite
    When I view any card in the grid
    Then it should display an animated GIF of the Pokémon

  Scenario: Each card shows the Pokédex number
    When I view the Bulbasaur card
    Then it should display "#0001"

  Scenario: Each card shows the Pokémon name
    When I view the Bulbasaur card
    Then it should display "Bulbasaur"

  Scenario: Each card shows the primary type as a coloured badge
    When I view the Bulbasaur card
    Then it should display a green "Grass" type badge

  Scenario: All card cells are the same height
    When I view the card grid
    Then every card cell should have the same fixed height
    And sprite images should fit within a uniform 68×68 pixel box

  Scenario: Unselected cards show a "View →" button
    When no card is selected
    Then all card buttons should read "View →"

  Scenario: Clicking a card updates the detail panel
    When I click the "View →" button on the Charmander card
    Then the detail panel heading should change to "Charmander"
    And Charmander's artwork should be displayed

  Scenario: The selected card shows a highlighted accent border
    When I click the Charmander card
    Then the Charmander card should have a visible coloured border
    And all other cards should have no accent border

  Scenario: The selected card button changes to "✓ Selected"
    When I click the Charmander card
    Then the button on Charmander's card should read "✓ Selected"
    And the button should be filled with the accent colour

  Scenario: Clicking a card scrolls the page to the top
    Given I have scrolled deep into the card grid
    When I click any "View →" card button
    Then the page should scroll to the top within 1 second
    And the scrollTop position should be less than 150 pixels

  Scenario: Surprise me button also scrolls to the top
    Given I have scrolled deep into the card grid
    When I click the "🎲 Surprise me!" button
    Then the page should scroll to the top within 1 second
    And the scrollTop position should be less than 150 pixels


# ============================================================================
# FEATURE: Pokémon Overview Tab
# ============================================================================

Feature: Pokémon Overview Tab
  As a young Pokémon fan
  I want to see my Pokémon's picture, description, and stats clearly
  So that I can learn about them in an engaging way

  Background:
    Given the Pokédex application is running
    And I have selected "Generation I"
    And I have selected Bulbasaur

  Scenario: Detail panel shows the official HD artwork
    When I view the Overview tab
    Then I should see a high-resolution official artwork image of Bulbasaur
    And the image should load from the PokéAPI sprite CDN

  Scenario: Detail panel shows the animated battle sprite
    When I view the Overview tab
    Then I should see an animated GIF of Bulbasaur in battle pose
    And the sprite should be labelled "Battle sprite"

  Scenario: Pokédex number and generation are displayed
    When I view the Overview tab
    Then I should see "#0001" and "Gen 1" in the header area

  Scenario: Flavour text is displayed in a styled quote block
    When I view the Overview tab
    Then I should see Bulbasaur's Pokédex flavour text
    And it should be displayed in a quote block with an orange left border

  Scenario: Type badges are displayed in type-specific colours
    When I view the Overview tab
    Then I should see a green "Grass" badge
    And a purple "Poison" badge
    And dual-type Pokémon should show both badges

  Scenario: Genus is shown in italic text
    When I view the Overview tab
    Then I should see "Seed Pokémon" in italic text below the name

  Scenario: Base stat bars are rendered for all six stats
    When I view the Overview tab
    Then I should see stat bars for HP, ATK, DEF, SpATK, SpDEF, and SPD
    And each bar should be proportional to the stat value (max 255)
    And the Total stat should be shown at the bottom

  Scenario: Legendary Pokémon are marked with a star
    Given I have selected Mewtwo
    When I view the Overview tab
    Then I should see a "⭐" symbol next to the generation label


# ============================================================================
# FEATURE: Physical Traits Tab
# ============================================================================

Feature: Physical Traits Tab
  As a young Pokémon fan
  I want to understand my Pokémon's physical characteristics and trainer facts
  So that I can learn about the Pokémon in a context I understand

  Background:
    Given the Pokédex application is running
    And I have selected "Generation I"
    And I have selected Bulbasaur
    And I have clicked the "🏋️ Physical Traits" tab

  # ── Body Facts ──────────────────────────────────────────────────────────────

  Scenario: Height is shown with a real-world comparison
    When I view the Body Facts section
    Then I should see Bulbasaur's height as "0.7 m"
    And I should see a comparison like "about as tall as a 7-year-old"

  Scenario: Weight is shown with a real-world comparison
    When I view the Body Facts section
    Then I should see Bulbasaur's weight as "6.9 kg"
    And I should see a comparison like "about as heavy as a big dog"

  Scenario: Body colour is shown as a coloured pill badge
    When I view the Body Facts section
    Then I should see a green coloured badge labelled "Green"

  Scenario: Body shape is displayed
    When I view the Body Facts section
    Then I should see "Body shape: Quadruped"

  Scenario: Gender ratio is shown as a split colour bar
    When I view the Body Facts section
    Then I should see a pink/blue split bar
    And I should see "♀ 12%" and "♂ 88%"

  Scenario: Genderless Pokémon display the genderless symbol
    Given I have selected Mewtwo
    When I view the Body Facts section
    Then I should see "⚲ Genderless"
    And I should not see a gender split bar

  # ── Trainer Facts ───────────────────────────────────────────────────────────

  Scenario: Catch difficulty is shown as a star rating and percentage for wild Pokémon
    When I view the Trainer Facts section for Rattata (a genuinely wild Pokémon)
    Then I should see a catch difficulty gauge bar
    And I should see a star rating like "⭐⭐⭐⭐⭐ Very Easy"
    And I should see a catch percentage like "100% catch chance"

  Scenario: Very hard to catch wild Pokémon show low catch difficulty
    Given I have selected a Pokémon that is both wild AND hard to catch
    When I view the Trainer Facts section
    Then I should see "💀 Very Hard" or a 1-star rating
    And the gauge bar should be very short

  Scenario: Catch difficulty is HIDDEN for non-wild Pokémon — regression for Charizard catch-rate bug
    # Root cause: CaptureRate exists in PokéAPI for ALL Pokémon (it's an internal game
    # formula value). Charizard has CaptureRate=45 (17.6%) even though it cannot be
    # caught in the wild. Showing this implied it was catchable. Fix: gate the catch
    # difficulty gauge on has_wild (WildLocations > 0 in raw_locations).
    Given I have selected Charizard (which has 0 wild encounter locations)
    When I view the Trainer Facts section
    Then I should NOT see any catch percentage or star rating
    And I should see a message like "Not applicable — this Pokémon cannot be found in the wild"

  Scenario: Bulbasaur and other gift-only starters also hide catch difficulty
    Given I have selected Bulbasaur (which is received as a gift, never wild)
    When I view the Trainer Facts section
    Then I should NOT see a catch difficulty gauge
    And I should see the "not applicable" message

  Scenario: Starting happiness is shown with an emoji label
    When I view the Trainer Facts section
    Then I should see "😐 Neutral — fairly content from the start"
    And the score should be shown as "70/255"

  Scenario: XP reward bar is displayed
    When I view the Trainer Facts section
    Then I should see a purple XP bar
    And I should see "64 XP" with a label like "low XP"

  Scenario: Growth rate is displayed with an icon
    When I view the Trainer Facts section
    Then I should see "🐾 Medium Slow" or equivalent growth rate label

  Scenario: Egg groups are displayed
    When I view the Trainer Facts section
    Then I should see "Monster / Plant" as the egg groups

  # ── Abilities ───────────────────────────────────────────────────────────────

  Scenario: Regular abilities are shown as green badges
    When I view the Abilities section
    Then I should see "Overgrow" in a green badge

  Scenario: Hidden ability is shown with a gold badge and label
    When I view the Abilities section
    Then I should see "✨ Chlorophyll (Hidden)" in a gold/yellow badge

  Scenario: The abilities section has an explanatory caption
    When I view the Abilities section
    Then I should see text like "Abilities are special powers that help Pokémon in battle"

  # ── Where to Find It ────────────────────────────────────────────────────────

  Scenario: Wild location regions are shown as expandable sections
    Given I have selected Rattata
    When I view the "Where to Find It" section
    Then I should see expandable region sections (Kanto, Johto, etc.)
    And each section should list area names and encounter rates

  Scenario: Gift-only Pokémon display a special "not found in wild" message
    Given I have selected Bulbasaur
    When I view the "Where to Find It" section
    Then I should see a message containing "can't be found in the wild" or "obtained another way"
    And I should not see any region expanders

  Scenario: Charizard is not shown as a wild encounter — regression test
    Given I have selected Charizard
    When I view the "Where to Find It" section
    Then I should see the "not found in the wild" message
    And "Kanto" should not appear in the location section

  # ── Type Battle Info ────────────────────────────────────────────────────────

  Scenario: Type strengths are shown as coloured type badges
    When I view the Type Battle Info section
    Then I should see "🔴 Strong against:" followed by Ground, Rock, and Water badges

  Scenario: Type weaknesses are shown as coloured type badges
    When I view the Type Battle Info section
    Then I should see "🔵 Weak to:" followed by Flying, Poison, Bug, Fire, and Ice badges

  Scenario: Type resistances are shown
    When I view the Type Battle Info section
    Then I should see "🟡 Resists hits from:" followed by Ground, Water, Grass, and Electric badges

  Scenario: Type immunities are shown when applicable
    Given I have selected Gastly (Ghost type)
    When I view the Type Battle Info section
    Then I should see "⚫ Immune to (no damage!):" followed by Normal and Fighting badges

  Scenario: Battle info caption names the Pokémon and its type
    When I view the Type Battle Info section
    Then I should see text like "How Bulbasaur's Grass / Poison type performs in battles"


# ============================================================================
# FEATURE: Location Data Accuracy
# ============================================================================

Feature: Location Data Accuracy
  As a player using this Pokédex to find Pokémon in the wild
  I want location data to be accurate
  So that I am not misled about where to find a Pokémon

  Scenario: Charizard has no wild encounter locations — regression for overworld-flying-special bug
    Given I query the location data for Pokémon number 6 (Charizard)
    Then the location table should return 0 rows
    And the Physical Traits tab should show the "not in the wild" message

  Scenario: Rattata has genuine wild encounter locations
    Given I query the location data for Pokémon number 19 (Rattata)
    Then the location table should return more than 0 rows
    And at least one row should have a region of "Kanto" or "Johto" or "Alola"
    And encounter rates should vary (not all the same value)

  Scenario: Gift-only base starter Pokémon have zero wild location rows
    Given I query the location data for Pokémon numbers 1, 4, and 7
    Then each should return exactly 0 location rows
    # Bulbasaur, Charmander, and Squirtle are received as gifts in the games

  Scenario: Fully evolved starter Pokémon have zero wild location rows
    Given I query the location data for Pokémon numbers 3, 6, and 9
    Then each should return exactly 0 location rows
    # Venusaur, Charizard, and Blastoise cannot be caught in the wild

  Scenario: Intermediate evolved forms may have location data via Friend Safari
    Given I query the location data for Pokémon number 2 (Ivysaur)
    Then the location table may return rows from the Kalos "Friend Safari"
    # Ivysaur IS catchable in Generation VI Friend Safari — this is correct

  Scenario: Pokémon with cave-spots encounters have location data
    Given I query the location data for Pokémon number 529 (Drilbur)
    Then the location table should return more than 0 rows
    # Drilbur is found via cave-spots (dust cloud) encounters in Gen V

  Scenario: All encounter rates in the location data are between 1 and 100
    Given I load the full Pokemon_Locations.csv file
    Then no row should have an EncounterRate less than 1
    And no row should have an EncounterRate greater than 100


# ============================================================================
# FEATURE: Backend Data Integrity
# ============================================================================

Feature: Backend Data Integrity
  As a developer maintaining this platform
  I want the CSV source data to be complete and valid
  So that the UI always has correct information to display

  # ── pokemon_data.csv ────────────────────────────────────────────────────────

  Scenario: All 1,025 base-form species are present
    Given I load pokemon_data.csv
    Then there should be at least 1,025 unique Pokédex numbers
    And species numbers 1 through 1025 should all be present

  Scenario: No Pokémon has a null primary type
    Given I load pokemon_data.csv
    Then every row should have a non-null Type1 value
    And every Type1 value should be one of the 18 valid Pokémon types

  Scenario: All secondary types are valid or empty
    Given I load pokemon_data.csv
    Then every non-null Type2 value should be one of the 18 valid Pokémon types

  Scenario: All generations are in the range 1 to 9
    Given I load pokemon_data.csv
    Then every Generation value should be between 1 and 9 inclusive

  Scenario: All stat values are positive integers
    Given I load pokemon_data.csv
    Then every HP, Attack, Defense, SpAtk, SpDef, and Speed value should be greater than 0

  Scenario: Known legendaries are correctly flagged
    Given I load pokemon_data.csv
    Then Mewtwo (number 150) should have Legendary = TRUE
    And Mew (number 151) should have Legendary = TRUE
    And Pikachu (number 25) should have Legendary = FALSE

  # ── Pokemon_Abilities.csv ───────────────────────────────────────────────────

  Scenario: All ability numbers exist in the main Pokémon dataset
    Given I load Pokemon_Abilities.csv and pokemon_data.csv
    Then every Number in Pokemon_Abilities.csv should exist in pokemon_data.csv

  Scenario: IsHidden is a boolean value
    Given I load Pokemon_Abilities.csv
    Then every IsHidden value should be either True or False

  Scenario: No exact duplicate ability rows exist
    Given I load Pokemon_Abilities.csv
    Then no two rows should have identical Number, AbilityName, and IsHidden values

  # ── Pokemon_Locations.csv ───────────────────────────────────────────────────

  Scenario: All location numbers exist in the main Pokémon dataset
    Given I load Pokemon_Locations.csv and pokemon_data.csv
    Then every Number in Pokemon_Locations.csv should exist in pokemon_data.csv

  Scenario: All region names are from the known set
    Given I load Pokemon_Locations.csv
    Then every Region should be one of: Kanto, Johto, Hoenn, Sinnoh, Unova,
      Kalos, Alola, Galar, Paldea, Hisui, Orre, Unknown

  Scenario: No duplicate area rows exist per Pokémon
    Given I load Pokemon_Locations.csv
    Then no two rows should have the same Number, Region, and AreaName combination

  Scenario: Area names are human-readable strings
    Given I load Pokemon_Locations.csv
    Then no AreaName should consist entirely of digits

  Scenario: Known wild Pokémon are present in the location data
    Given I load Pokemon_Locations.csv
    Then Pidgey (number 16) should have at least one location row
    And Rattata (number 19) should have at least one location row
    And Zubat (number 41) should have at least one location row
    And Magikarp (number 129) should have at least one location row

  Scenario: Non-standard wild methods are not over-filtered
    Given I load Pokemon_Locations.csv
    Then Drilbur (number 529) should have at least one location row
    # Drilbur is only found via cave-spots — verifies WILD_METHODS is not too restrictive
    And Heracross (number 214) should have at least one location row
    # Heracross is found via headbutt trees

  # ── Type_effectiveness.csv ──────────────────────────────────────────────────

  Scenario: All multiplier values are valid
    Given I load Type_effectiveness.csv
    Then every Multiplier value should be 0.0, 0.5, or 2.0

  Scenario: Known super-effective matchups are correct
    Given I load Type_effectiveness.csv
    Then Fire attacking Grass should have Multiplier = 2.0
    And Water attacking Fire should have Multiplier = 2.0
    And Normal attacking Ghost should have Multiplier = 0.0

  Scenario: The 18×18 matchup matrix has the correct number of non-neutral entries
    Given I load Type_effectiveness.csv
    Then there should be exactly 120 rows
    # Only non-neutral multipliers (0.0 and 0.5 and 2.0) are stored;
    # neutral (1.0) entries are omitted and inferred by the type_matchup_matrix view
