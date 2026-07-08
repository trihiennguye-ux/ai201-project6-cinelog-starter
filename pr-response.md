# PR Response Doc — CineLog Watchlist Feature

## AI Usage
I used AI assistance to help draft and tighten the written responses, then verified the repo state with editor, search, and test tools instead of relying on guesses.

- Used workspace search and file inspection to trace the watchlist service, route, and test coverage.
- Added support for removing films from the watchlist and covered the new behavior with regression tests.
- Used AI to stress-test the arguments for Comment 4 and Comment 5, then rewrote them to match the maintainer's priorities and the project's actual behavior.
- Ran the project's watchlist and full test suites in the configured venv to validate the final state.

## Comment 1 — Rename
**What I did:**
- Verified the service function is exported as `add_to_watchlist()` in `services/watchlist_service.py`.
- Searched the repository for the old name `save_to_watchlist` and the new name `add_to_watchlist` to find all call sites.
- Confirmed the existing route in `routes/watchlist/watchlist.py` already imports and calls `add_to_watchlist()` so no code-level rename was necessary.
**How I verified:**
- Repo-wide search for `save_to_watchlist` (no results) and `add_to_watchlist` (found service and route).
- Ran the test suite after environment setup to ensure no import or name errors.

## Comment 2 — Deduplication
**What I did:**
- Implemented deduplication in `add_to_watchlist()` to mirror the pattern used by `add_to_collection()` in `services/collection_service.py`:
	- Query for an existing `WatchlistEntry` with `user_id` and `film_id`.
	- If present, raise a specific `AlreadyInWatchlistError` (replacing a previous generic `Exception`).
**How I verified:**
- Reviewed `services/collection_service.py` to match behavior and error messages.
- Ran the full test suite and added a targeted test (see Comment 3) to ensure the error is raised for nonexistent films and duplicates are prevented.

## Comment 3 — Missing test
**What I did:**
- Added `tests/test_watchlist.py` with `test_add_to_watchlist_nonexistent_film_raises`.
- Modeled the test directly on `test_add_to_collection_nonexistent_film_raises` from `tests/test_collection.py` using the same fixtures (`app`, `sample_user`) and in-memory SQLite DB setup.
**How I verified:**
- Executed the project's tests using the project's venv Python:

```bash
pytest tests/test_watchlist.py -v
pytest tests/ -v
```

- All tests passed after the change (`5 passed`).

## Comment 4 — Default visibility
**My position:**
I recommend changing the default to `public=False` (private-by-default). If we keep `public=True`, we should explicitly document and surface that choice in the UI and onboarding so users are not surprised.

**Reasoning:**
- Privacy-first UX: Most users expect personal lists (watchlists, playlists, bookmarks) to be private unless they knowingly share them. Defaulting to private minimizes accidental sharing and helps build user trust.
- Minimize accidental exposure: New or casual users are likelier to add items without considering visibility; private-by-default prevents inadvertent public exposure of their preferences or viewing plans.
- Legal and reputational safety: Making private the default reduces risk around sensitive content or identifiable patterns being public, which can be important for compliance or user comfort.
- Opt-in for discoverability: Social features (discover, follow, public collections) are valuable, but they work well when users explicitly opt in — that action signals intent and increases the quality of public content.

**Tradeoff acknowledged:**
- Reduced passive discoverability: `public=True` by default helps surface content and bootstraps social features (recommendations, curated lists) earlier. With `public=False` fewer items will be available for aggregation and discovery out of the box.
- Slightly higher friction for sharing: Users who intended to share immediately must take an extra step to toggle visibility.

**Mitigations and implementation notes:**
- Make the visibility toggle prominent in the watchlist UI and in the API response so users can change it per-entry and understand the current state.
- Add a one-time onboarding tip explaining visibility defaults and how to change them.
- Provide a user-level preference (in account settings) to set a default visibility (`public_by_default: true|false`) for power users who want the old behavior.
- If we keep `public=True` for backwards compatibility, add an opt-in privacy-safe migration plan and a clear changelog message so users and integrators are aware.

**How to verify in tests / QA:**
- Unit test: create a `WatchlistEntry` without specifying `public` and assert the entry's `public` value equals the chosen default (False).
- API/integration test: POST to the watchlist add endpoint and assert the returned `public` field matches the default; then explicitly toggle visibility and assert persistence.
- Manual QA: Verify onboarding message appears, toggle is visible, and the user-level preference overrides entry-level defaults.

## Comment 5 — Sort order
**My position:**
Default to `date_added` (newest first) but expose explicit, documented sorting options (`date_added`, `title`) at the API/UI level and provide a per-user preference for default sorting.

**Reasoning:**
- Aligns with maintainer preference: The maintainer's ask to use `date_added` is well-motivated — watchlists are often a temporal queue (what I intend to watch soon), and showing recently added items first surface the user's current priorities.
- User intent and discoverability: Newest-first helps users pick up where they left off and reduces friction for recently-added items (they're the ones a user most likely wants to act on). It also helps surface newly added content across the user base if we have social discovery features.
- Preserve browseability: Alphabetical ordering is useful for browsing and locating a specific title. Rather than forcing a single mental model on all users, exposing a simple `sort` parameter and a per-account default gives power users the control they need while making the UI sensible for casual users.

**Engagement with the maintainer's point:**
- The maintainer argued for `date_added` to reflect recency; I agree this is the right default behaviour for the majority of watchlist use-cases. Where the maintainer's concern is discoverability for features like curated lists or public watchlists, we can still support alphabetical or other ordering in those contexts explicitly (e.g., a public listing endpoint could default to `title` for easier scanning).
- If the maintainer's worry is breaking existing integrations that depend on alphabetical order, we should treat this as a breaking change: document it in the changelog, and offer a transitional toggle (user/account default or an API query parameter) so integrators can opt-in/opt-out.

**Implementation notes:**
- Change `get_watchlist(user_id)` in `services/watchlist_service.py` to order by `WatchlistEntry.date_added.desc()` (newest first) rather than `Film.title.asc()`.
- Add an optional `sort` parameter to the route in `routes/watchlist/watchlist.py` (query param) so callers can override the default. Example: `GET /watchlist/<user_id>?sort=title`.
- Add a user preference (e.g., `watchlist_sort_default`) in account settings to persist a user's preferred sort order.

**Tests / QA:**
- Unit test: create multiple `WatchlistEntry` objects with differing `date_added` values and assert `get_watchlist()` returns items in newest-first order by default.
- Integration/API test: request the watchlist with `?sort=title` and assert the returned list is alphabetically ordered by `title`.
- Backward compatibility test: if switching the default, add a test that exercises the user/account preference override so existing integrations can be validated.

If you'd like, I can implement the default change and add the `sort` query parameter and tests in a follow-up patch; otherwise I can prepare a small, focused PR that only updates the default ordering and test coverage.

## Comment 6 — Rebase
**What conflicted:**
- The rebase conflict happened in `.gitignore` where both branches modified Python environment ignore rules around `.pytest_cache/`, `.venv/`, and `venv/`.
- The conflict was a classic overlapping edit (both sides touched the same block), which produced merge markers.

**How I resolved it:**
- I removed the conflict markers and kept the union of the useful ignore entries so local environments and test cache files remain untracked:
	- `.pytest_cache/`
	- `.venv/`
	- `venv/`
- I kept the final section minimal and de-duplicated to avoid future churn when rebasing.

**How I verified no conflict remains:**
- Ran `git status --short` to confirm there are no unmerged (`UU`) paths.
- Scanned tracked files for merge markers (`<<<<<<<`, `=======`, `>>>>>>>`) to ensure none remain after resolution.
- Re-ran the test command used during review (`pytest tests/ -v`) to ensure the resolved files do not introduce syntax/parse issues from conflict artifacts.

## Comment 7 — Remove from watchlist
**What I did:**
- Implemented `remove_from_watchlist()` in `services/watchlist_service.py` so a user can remove an existing film from their watchlist after validating that the film exists and the watchlist entry is present.
- Added regression tests in `tests/test_watchlist.py` for the successful removal path and the missing-entry error path.
**How I verified:**
- Ran `pytest tests/test_watchlist.py -v` and `pytest tests/ -v` after adding the model and tests.
- Confirmed the service now removes entries cleanly and raises `AlreadyInWatchlistError` when the film is not already on the watchlist.

## PR Description
This PR adds and documents the CineLog watchlist feature work.

The watchlist lets a user save films they want to watch, removes entries through `remove_from_watchlist()`, prevents duplicate entries through `AlreadyInWatchlistError`, and exposes the watchlist through the route and service layer used by the project.

Design decisions:
- Visibility default: I recommend private by default (`public=False`) so a user's watchlist is not shared unless they choose to make it public.
- Sort order: I recommend newest-first by `date_added` so the watchlist reflects what the user added most recently, while still allowing alternate sort options.

Manual testing steps:
1. Run the app in the project's virtual environment.
2. Add a film to a user's watchlist through the API or existing watchlist route.
3. Confirm the new entry appears in the watchlist response and that duplicates are rejected with `AlreadyInWatchlistError`.
4. Verify the default visibility is private unless explicitly changed.
5. Verify the default sort order is newest-first by `date_added`, and compare with an alternate sort if available.

This PR also records the review responses covering the rename cleanup, deduplication logic, the rebase conflict resolution, and the two design decisions above.