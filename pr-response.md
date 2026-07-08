# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

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
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->