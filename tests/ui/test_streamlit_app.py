"""Automated browser QA for the GAMESTATE Streamlit app, per the
project's testing requirements: every page loads, navigation works,
filters work, no console errors, no horizontal overflow, the intro
renders and both Enter and Skip work.

Run with: python -m pytest tests/ui/ -v
Requires: pip install playwright && python -m playwright install chromium
"""
import pytest

PAGES = [
    ("Global_Search", "Global Search"),
    ("League_Table", "League Table"),
    ("League_Trends", "League Trends"),
    ("Team_Explorer", "Team Explorer"),
    ("Head_to_Head", "Head-to-Head"),
    ("Match_Explorer", "Match Explorer"),
    ("Player_Explorer", "Player Explorer"),
    ("European_Performance", "European Performance"),
    ("Methodology", "Methodology"),
    ("About", "About GAMESTATE"),
]

# Streamlit's own frontend issues a couple of internal polling requests
# (_stcore/health, _stcore/host-config) that 404 as a known, harmless
# quirk when a page is loaded directly at a sub-path (rather than
# navigated to client-side from "/") - confirmed by inspecting the
# actual failed request URLs during development. That's Streamlit's own
# plumbing, not an application bug, so it's filtered out here; anything
# else 4xx/5xx or a genuine console/page error still fails the test.
BENIGN_URL_SNIPPETS = ["_stcore/", "favicon"]


# Chrome's console API doesn't include the failed URL in a "Failed to
# load resource" message text (only the generic message) - the real
# URL only shows up via the "response" event below. So this generic
# console message is always redundant with an 'http' entry we already
# capture with full URL context, and is dropped here rather than
# false-failing on every _stcore/ 404 with no way to tell it apart
# from a real one by text alone.
GENERIC_RESOURCE_ERROR = "Failed to load resource: the server responded with a status of"


def _collect_errors(page):
    """Returns a list that accumulates (source, detail) tuples for real
    console errors, uncaught page errors, and failed HTTP responses -
    call this BEFORE page.goto() so early requests are captured."""
    errors = []

    def on_console(msg):
        if msg.type == "error" and not msg.text.startswith(GENERIC_RESOURCE_ERROR):
            errors.append(("console", msg.text))

    page.on("console", on_console)
    page.on("pageerror", lambda exc: errors.append(("pageerror", str(exc))))
    page.on("response", lambda r: errors.append(("http", f"{r.status} {r.url}")) if r.status >= 400 else None)
    return errors


def _real_errors(errors):
    return [(src, detail) for src, detail in errors if not any(s in detail for s in BENIGN_URL_SNIPPETS)]


def _no_horizontal_overflow(page) -> bool:
    return page.evaluate(
        "document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2"
    )


# ---------------------------------------------------------------- Home / intro

def test_home_intro_renders(page, streamlit_server):
    page.goto(streamlit_server, wait_until="load")
    page.wait_for_selector("text=ENTER", timeout=15000)
    assert page.get_by_text("ENTER").is_visible()
    assert page.get_by_text("Skip Intro").is_visible()
    # the cinematic wordmark renders inside the isolated iframe
    frame = page.frame_locator("iframe").first
    frame.locator("text=GAMESTATE").wait_for(timeout=10000)


def test_home_enter_button_reveals_dashboard(page, streamlit_server):
    page.goto(streamlit_server, wait_until="load")
    page.wait_for_selector("text=ENTER", timeout=15000)
    page.get_by_text("ENTER", exact=True).click()
    # hero-only text: the sidebar wordmark "GAMESTATE" is visible during the intro too
    page.wait_for_selector("text=EXPLORE THE GAME", timeout=15000)
    assert page.get_by_text("SEASONS", exact=True).is_visible()
    assert page.get_by_text("MATCHES", exact=True).is_visible()


def test_home_skip_intro_reveals_dashboard(page, streamlit_server):
    page.goto(streamlit_server, wait_until="load")
    page.wait_for_selector("text=Skip Intro", timeout=15000)
    page.get_by_text("Skip Intro", exact=True).click()
    page.wait_for_selector("text=EXPLORE THE GAME", timeout=15000)
    assert page.get_by_text("CLUBS", exact=True).is_visible()


def test_home_no_console_errors_or_overflow(page, streamlit_server):
    errors = _collect_errors(page)
    page.goto(streamlit_server, wait_until="load")
    page.wait_for_selector("text=Skip Intro", timeout=15000)
    page.get_by_text("Skip Intro", exact=True).click()
    page.wait_for_selector("text=EXPLORE THE GAME", timeout=15000)
    page.wait_for_timeout(500)
    assert _real_errors(errors) == [], f"Console errors on Home: {_real_errors(errors)}"
    assert _no_horizontal_overflow(page)


# ---------------------------------------------------------------- Every page loads

@pytest.mark.parametrize("slug,heading", PAGES)
def test_page_loads_with_expected_heading(page, streamlit_server, slug, heading):
    page.goto(f"{streamlit_server}/{slug}", wait_until="load")
    title = page.get_by_role("heading", name=heading).first
    title.wait_for(timeout=15000)
    assert title.is_visible()


@pytest.mark.parametrize("slug,heading", PAGES)
def test_page_no_console_errors(page, streamlit_server, slug, heading):
    errors = _collect_errors(page)
    page.goto(f"{streamlit_server}/{slug}", wait_until="load")
    page.get_by_role("heading", name=heading).first.wait_for(timeout=15000)
    page.wait_for_timeout(500)
    assert _real_errors(errors) == [], f"Console errors on {slug}: {_real_errors(errors)}"


@pytest.mark.parametrize("slug,heading", PAGES)
def test_page_no_horizontal_overflow(page, streamlit_server, slug, heading):
    page.goto(f"{streamlit_server}/{slug}", wait_until="load")
    page.get_by_role("heading", name=heading).first.wait_for(timeout=15000)
    assert _no_horizontal_overflow(page), f"{slug} has horizontal overflow at 1440px width"


# ---------------------------------------------------------------- Navigation

def test_sidebar_navigation_between_pages(page, streamlit_server):
    page.goto(streamlit_server, wait_until="load")
    page.wait_for_selector("text=Skip Intro", timeout=15000)
    page.get_by_text("Skip Intro", exact=True).click()
    page.wait_for_selector("text=EXPLORE THE GAME", timeout=15000)

    sidebar = page.locator('section[data-testid="stSidebar"]')
    sidebar.get_by_role("link", name="Standings").click()
    page.wait_for_url("**/League_Table*", timeout=15000)
    page.get_by_role("heading", name="League Table").first.wait_for(timeout=15000)

    sidebar.get_by_role("link", name="Head-to-Head").click()
    page.wait_for_url("**/Head_to_Head*", timeout=15000)
    page.get_by_role("heading", name="Head-to-Head").first.wait_for(timeout=15000)


# ---------------------------------------------------------------- Filters actually work

def test_league_table_season_filter_changes_standings(page, streamlit_server):
    page.goto(f"{streamlit_server}/League_Table", wait_until="load")
    # The standings table (st.dataframe) renders into a canvas-based grid
    # (glide-data-grid) whose JS is lazy-loaded - waiting for its
    # container element, not a fixed timeout, is what actually
    # guarantees its text is readable afterward.
    page.wait_for_selector('[data-testid="stDataFrame"]', timeout=20000)
    page.wait_for_timeout(500)

    combo = page.get_by_role("combobox", name="Season")
    combo.click()
    page.wait_for_timeout(300)
    page.get_by_role("option", name="2015/16", exact=True).click()
    page.wait_for_selector('[data-testid="stDataFrame"]', timeout=20000)
    page.wait_for_timeout(1000)

    body_text = page.inner_text("body")
    # Real, independently known fact: Leicester City won the league in
    # 2015/16 - this confirms the filter actually re-queries real data,
    # not just changes a label.
    leicester_idx = body_text.find("Leicester City")
    arsenal_idx = body_text.find("Arsenal")
    assert leicester_idx != -1 and arsenal_idx != -1
    assert leicester_idx < arsenal_idx, "Leicester City should be above Arsenal in the 2015/16 table"


def test_head_to_head_shows_real_data_for_selected_teams(page, streamlit_server):
    page.goto(f"{streamlit_server}/Head_to_Head", wait_until="load")
    page.wait_for_selector('[data-testid="stSelectbox"]', timeout=15000)
    page.wait_for_timeout(500)
    page.wait_for_selector("text=MEETINGS", timeout=15000)

    body_text = page.inner_text("body")
    assert "MEETINGS" in body_text
    assert "WINS" in body_text.upper() or "DRAWS" in body_text.upper()


# ---------------------------------------------------------------- Global Search

def test_search_finds_team_and_navigates_to_team_explorer(page, streamlit_server):
    page.goto(f"{streamlit_server}/Global_Search", wait_until="load")
    page.wait_for_selector('input[aria-label="Search"], input[placeholder*="Arsenal"]', timeout=15000)
    search_box = page.locator('input[placeholder*="Arsenal"]')
    search_box.fill("arsenal")
    search_box.press("Enter")  # this widget shows "Press Enter to apply" - fill() alone doesn't commit it
    page.wait_for_timeout(600)

    body_text = page.inner_text("body")
    assert "Arsenal" in body_text
    assert "result" in body_text.lower()

    page.get_by_role("button", name="View →").first.click()
    # Every page's sidebar always shows a "Team Explorer" link, including
    # Global Search itself - waiting for that text matches instantly and
    # races the actual navigation. Wait for the URL to actually change instead.
    page.wait_for_url("**/Team_Explorer*", timeout=15000)
    assert "team=Arsenal" in page.url

    # The team name itself lives inside the selectbox's <input> value,
    # which isn't part of inner_text() - "Arsenal" only appears as real
    # rendered text once the season-journey chart's subheader renders,
    # so wait for that rather than the selection alone.
    page.wait_for_selector("text=season journey", timeout=15000)
    combo = page.get_by_role("combobox", name="Select a team")
    assert combo.input_value() == "Arsenal"


def test_search_finds_player_and_navigates_to_player_explorer(page, streamlit_server):
    page.goto(f"{streamlit_server}/Global_Search", wait_until="load")
    page.wait_for_selector('input[placeholder*="Arsenal"]', timeout=15000)
    search_box = page.locator('input[placeholder*="Arsenal"]')
    search_box.fill("haaland")
    search_box.press("Enter")
    page.wait_for_timeout(600)

    body_text = page.inner_text("body")
    assert "Haaland" in body_text

    page.get_by_role("button", name="View →").first.click()
    page.wait_for_url("**/Player_Explorer*", timeout=15000)
    assert "player=" in page.url


def test_search_no_results_shows_message(page, streamlit_server):
    page.goto(f"{streamlit_server}/Global_Search", wait_until="load")
    page.wait_for_selector('input[placeholder*="Arsenal"]', timeout=15000)
    search_box = page.locator('input[placeholder*="Arsenal"]')
    search_box.fill("zzzznotarealquery")
    search_box.press("Enter")
    page.wait_for_timeout(600)
    body_text = page.inner_text("body")
    assert "No teams, clubs, players or seasons found" in body_text


def test_european_performance_club_selector_changes_data(page, streamlit_server):
    page.goto(f"{streamlit_server}/European_Performance", wait_until="load")
    page.wait_for_selector('[data-testid="stSelectbox"]', timeout=15000)
    page.wait_for_timeout(500)

    combo = page.get_by_role("combobox", name="Select a club")
    combo.click()
    page.wait_for_timeout(300)
    page.get_by_role("option", name="Leicester City", exact=True).click()
    page.wait_for_timeout(1200)

    body_text = page.inner_text("body")
    # Leicester City's real, only Champions League campaign in range
    # reached the Quarterfinal (2016/17) - confirms real data, not a stub.
    assert "Quarterfinal" in body_text
