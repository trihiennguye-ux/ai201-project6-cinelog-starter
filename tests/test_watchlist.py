import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    AlreadyInWatchlistError,
)
from services.collection_service import FilmNotFoundError


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """Adding a film_id that doesn't exist should raise FilmNotFoundError."""
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


def test_remove_from_watchlist_deletes_existing_entry(app, sample_user, sample_film):
    """Removing a film from the watchlist should delete the entry from storage."""
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        removed_entry = remove_from_watchlist(user_id=sample_user, film_id=sample_film)

        assert removed_entry is not None
        assert removed_entry.user_id == sample_user
        assert removed_entry.film_id == sample_film

        remaining = db.session.query(WatchlistEntry).filter_by(
            user_id=sample_user, film_id=sample_film
        ).first()
        assert remaining is None


def test_remove_from_watchlist_missing_entry_raises(app, sample_user, sample_film):
    """Removing a film that is not on the watchlist should raise an error."""
    with app.app_context():
        with pytest.raises(AlreadyInWatchlistError):
            remove_from_watchlist(user_id=sample_user, film_id=sample_film)
