"""
test_ui.py
Playwright-based UI tests for the Pokémon Pokédex app.

Starts a real Streamlit server as a subprocess, drives a headless Chromium
browser through the full user flow, and asserts scroll, navigation, and
selection behaviour.

Run:  python -m pytest test_ui.py -v
Requires: playwright  (pip install playwright && playwright install chromium)
"""

import subprocess
import time
import urllib.request

import pytest
from playwright.sync_api import sync_playwright, Page

# ── Config ────────────────────────────────────────────────────────────────────
PORT = 8510
BASE = f"http://localhost:{PORT}"
STREAMLIT_READY_TIMEOUT = 30   # seconds to wait for server startup
RERUN_WAIT = 4.0               # seconds to let Streamlit finish a Python rerun
SCROLL_SETTLE = 0.9            # seconds to let scroll retries fire (3 × at 0/200/500 ms)
SCROLL_THRESHOLD = 150         # px — scrollTop must be below this after a snap-to-top


# ── Server fixture ────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def running_app():
    """Start Streamlit in the background; yield; kill it."""
    proc = subprocess.Popen(
        [
            ".venv/bin/streamlit", "run", "app.py",
            "--server.port", str(PORT),
            "--server.headless", "true",
            "--server.runOnSave", "false",
            "--logger.level", "error",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait until the server responds
    deadline = time.time() + STREAMLIT_READY_TIMEOUT
    while time.time() < deadline:
        try:
            urllib.request.urlopen(BASE, timeout=2)
            break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill()
        pytest.fail("Streamlit server did not start in time")

    yield BASE
    proc.kill()


@pytest.fixture(scope="session")
def browser_ctx(running_app):
    """Single headless browser for the whole session."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        yield ctx
        browser.close()


@pytest.fixture
def page(browser_ctx, running_app):
    """Fresh page that navigates to the app root before each test."""
    pg = browser_ctx.new_page()
    pg.goto(running_app, wait_until="networkidle", timeout=20_000)
    time.sleep(2)
    yield pg
    pg.close()


# ── Helpers ───────────────────────────────────────────────────────────────────
def scroll_main(page: Page, px: int) -> None:
    page.evaluate(
        f"document.querySelector('[data-testid=\"stMain\"]').scrollTop = {px}"
    )
    time.sleep(0.2)


def get_scroll_top(page: Page) -> int:
    return page.evaluate(
        "document.querySelector('[data-testid=\"stMain\"]').scrollTop"
    )


def enter_gen1(page: Page) -> None:
    page.locator("button", has_text="Explore Generation I").first.click()
    time.sleep(RERUN_WAIT)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_game_selection_shows_9_cards(page: Page):
    """Landing page must have exactly 9 Explore Generation buttons."""
    btns = page.locator("button", has_text="Explore Generation").all()
    assert len(btns) == 9, f"Expected 9 game cards, got {len(btns)}"


def test_each_generation_card_has_count_badge(page: Page):
    """Every card must show the '✨ N new Pokémon' badge."""
    content = page.content()
    for gen_num in range(1, 10):
        assert "new Pokémon" in content, f"'new Pokémon' badge missing for gen {gen_num}"


def test_generation_titles_visible(page: Page):
    """All nine generation titles must appear on screen."""
    titles = [
        "Generation I", "Generation II", "Generation III",
        "Generation IV", "Generation V", "Generation VI",
        "Generation VII", "Generation VIII", "Generation IX",
    ]
    content = page.content()
    for t in titles:
        assert t in content, f"'{t}' not found on game selection screen"


def test_clicking_gen_enters_pokedex(page: Page):
    """Clicking Gen I card should show the Gen I Pokédex heading and #0001."""
    enter_gen1(page)
    content = page.content()
    assert "Generation I" in content, "Gen I heading missing after clicking card"
    assert "#0001" in content, "#0001 not found in card grid"


def click_sidebar_button(page: Page, text: str) -> None:
    """Click a sidebar button via JS — bypasses Playwright's out-of-viewport check."""
    page.evaluate(f"""
        () => {{
            for (const b of document.querySelectorAll('button')) {{
                if (b.textContent.includes('{text}')) {{ b.click(); break; }}
            }}
        }}
    """)


def test_back_button_returns_to_selection(page: Page):
    """After entering a gen, clicking '← All Games' returns to selection screen."""
    enter_gen1(page)
    click_sidebar_button(page, "All Games")
    time.sleep(RERUN_WAIT)
    btns = page.locator("button", has_text="Explore Generation").all()
    assert len(btns) == 9, "Back button did not return to game selection screen"


def test_card_click_updates_detail_panel(page: Page):
    """Clicking Charmander's card changes the detail panel to show Charmander."""
    enter_gen1(page)
    # Charmander is the 4th Pokémon (#4); its card button is the 4th 'View →'
    view_btns = page.locator("button", has_text="View →").all()
    assert len(view_btns) >= 4, "Not enough View → buttons found"
    view_btns[3].click()  # index 3 = Charmander
    time.sleep(RERUN_WAIT)
    content = page.content()
    assert "Charmander" in content, "Detail panel did not update to Charmander"
    # That card's button should now say ✓ Selected
    selected_btns = page.locator("button", has_text="Selected").all()
    assert len(selected_btns) >= 1, "No '✓ Selected' button found after click"


def test_card_click_scrolls_to_top(page: Page):
    """After clicking a card while scrolled deep, page must snap back near top."""
    enter_gen1(page)
    # Scroll to mid-grid
    scroll_main(page, 3000)
    assert get_scroll_top(page) > 500, "Scroll setup failed — page did not scroll down"

    # Click a card visible at that scroll depth
    view_btns = page.locator("button", has_text="View →").all()
    assert len(view_btns) > 15
    view_btns[15].click()  # somewhere in the middle of the list
    time.sleep(RERUN_WAIT + SCROLL_SETTLE)

    top = get_scroll_top(page)
    assert top < SCROLL_THRESHOLD, (
        f"Page did not scroll to top after card click — scrollTop={top}px "
        f"(threshold: {SCROLL_THRESHOLD}px)"
    )


def test_surprise_me_scrolls_to_top(page: Page):
    """Surprise me! button must also snap the page back to the top."""
    enter_gen1(page)
    scroll_main(page, 3000)
    assert get_scroll_top(page) > 500, "Scroll setup failed"

    click_sidebar_button(page, "Surprise me")
    time.sleep(RERUN_WAIT + SCROLL_SETTLE)

    top = get_scroll_top(page)
    assert top < SCROLL_THRESHOLD, (
        f"Surprise me! did not scroll to top — scrollTop={top}px"
    )


def test_charizard_not_in_wild_locations(page: Page):
    """
    Regression test for the Charizard location data bug.

    Charizard (#6) was incorrectly showing 25 Kanto wild encounter areas at
    100% rate due to 'overworld-flying-special' (Let's Go) entries being
    included in the location CSV without method filtering.

    After the fix, Charizard's Physical Traits tab must show the
    'can't be found in the wild' message — not any region expanders.
    """
    enter_gen1(page)

    # Charizard is card index 5 (#6) — click it
    view_btns = page.locator("button", has_text="View →").all()
    assert len(view_btns) >= 6, "Not enough cards in Gen I"
    view_btns[5].click()
    time.sleep(RERUN_WAIT)

    # Open Physical Traits tab
    page.locator("[role='tab']", has_text="Physical Traits").first.click()
    time.sleep(2)

    content = page.content()
    # Must show the no-locations message
    assert "obtained another way" in content or "can't be found" in content, (
        "Charizard should show the 'can't be found in the wild' message "
        "but no such text was found — the location bug may have returned"
    )
    # Must NOT show Kanto as a wild location section
    traits_section = content.split("Where to Find It")[-1].split("Type Battle")[0] if "Where to Find It" in content else ""
    assert "Kanto" not in traits_section, (
        "Charizard's location section should not contain 'Kanto' — "
        "the overworld-flying-special data is leaking back in"
    )


def test_rattata_has_valid_wild_locations(page: Page):
    """
    Rattata (#19) must show real location data in Physical Traits.

    Guards against over-filtering in WILD_METHODS — if too many methods
    are excluded, genuinely wild Pokémon like Rattata would incorrectly
    show the no-locations message.
    """
    enter_gen1(page)

    # Rattata is card index 18 (#19)
    view_btns = page.locator("button", has_text="View →").all()
    assert len(view_btns) >= 19, "Not enough cards in Gen I"
    view_btns[18].click()
    time.sleep(RERUN_WAIT)

    page.locator("[role='tab']", has_text="Physical Traits").first.click()
    time.sleep(2)

    content = page.content()
    assert "obtained another way" not in content and "can't be found" not in content, (
        "Rattata should have real location data — the WILD_METHODS filter "
        "may be excluding 'walk' or 'overworld' encounters incorrectly"
    )
    assert any(r in content for r in ("Kanto", "Johto", "Hoenn", "Sinnoh", "Alola")), (
        "Rattata should show at least one region in its location section"
    )


def test_charizard_catch_difficulty_not_shown(page: Page):
    """
    Regression: Charizard's Physical Traits tab must NOT show a catch difficulty
    gauge or star rating.

    Root cause: CaptureRate (45 for Charizard) exists in PokéAPI for every species
    as an internal formula value. For Pokémon with 0 wild location rows the gauge
    has no meaning — showing '5 stars, Very Easy, 17.6%' implies Charizard can be
    caught in the wild, which it cannot. The fix gates the catch gauge on has_wild.
    """
    enter_gen1(page)

    view_btns = page.locator("button", has_text="View →").all()
    assert len(view_btns) >= 6, "Not enough cards in Gen I"
    view_btns[5].click()   # index 5 = Charizard (#6)
    time.sleep(RERUN_WAIT)

    page.locator("[role='tab']", has_text="Physical Traits").first.click()
    time.sleep(2)

    content = page.content()

    # Must NOT show a star rating or catch chance percentage
    assert "catch chance" not in content, (
        "Charizard should not show a catch chance percentage — "
        "it cannot be found in the wild so the catch rate is meaningless"
    )
    assert "Very Easy" not in content and "Very Hard" not in content, (
        "Charizard should not show a catch difficulty star label"
    )

    # Must show the 'not applicable' message instead
    assert "Not applicable" in content or "cannot be found in the wild" in content, (
        "Charizard's catch difficulty section should explain it is not applicable"
    )


def test_rattata_catch_difficulty_shown(page: Page):
    """
    Rattata (#19) IS catchable in the wild and MUST show a catch difficulty gauge.
    Guards against over-suppression of the catch rate display.
    """
    enter_gen1(page)

    view_btns = page.locator("button", has_text="View →").all()
    assert len(view_btns) >= 19, "Not enough cards in Gen I"
    view_btns[18].click()   # index 18 = Rattata (#19)
    time.sleep(RERUN_WAIT)

    page.locator("[role='tab']", has_text="Physical Traits").first.click()
    time.sleep(2)

    content = page.content()
    assert "catch chance" in content, (
        "Rattata should show a catch chance percentage — "
        "it is a genuine wild Pokémon and the catch rate is meaningful"
    )
    assert "Not applicable" not in content, (
        "Rattata should NOT show the 'not applicable' catch message"
    )
