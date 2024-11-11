from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats,
    get_leaderboard,
)

######################################################
#
#    Fixtures and Utilities
#
######################################################


def normalize_whitespace(sql_query: str) -> str:
    """Utility function to normalize whitespace in SQL queries for comparison."""
    return re.sub(r"\s+", " ", sql_query).strip()


# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch(
        "meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection
    )

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Create and Delete Tests
#
######################################################


def test_create_meal(mock_cursor):
    """Test creating a new meal in the database."""

    create_meal(meal="Pasta", cuisine="Italian", price=10.00, difficulty="MED")

    expected_query = normalize_whitespace(
        """
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """
    )

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert (
        actual_query == expected_query
    ), "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Pasta", "Italian", 10.00, "MED")
    assert (
        actual_arguments == expected_arguments
    ), f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_meal_duplicate(mock_cursor):
    """Test creating a duplicate meal (should raise an error)."""

    mock_cursor.execute.side_effect = sqlite3.IntegrityError(
        "UNIQUE constraint failed: meals.meal"
    )

    with pytest.raises(ValueError, match="Meal with name 'Pasta' already exists"):
        create_meal(meal="Pasta", cuisine="Italian", price=10.00, difficulty="MED")


def test_create_meal_invalid_price():
    """Test creating a meal with an invalid price (e.g., negative price)."""

    with pytest.raises(
        ValueError, match="Invalid price: -10.0. Price must be a positive number."
    ):
        create_meal(meal="Pizza", cuisine="Italian", price=-10.00, difficulty="MED")


def test_create_meal_invalid_difficulty():
    """Test creating a meal with an invalid difficulty."""

    with pytest.raises(
        ValueError,
        match="Invalid difficulty level: MEDIUM. Must be 'LOW', 'MED', or 'HIGH'.",
    ):
        create_meal(meal="Burger", cuisine="American", price=15.00, difficulty="MEDIUM")


def test_delete_meal(mock_cursor):
    """Test soft deleting a meal by meal ID."""

    mock_cursor.fetchone.return_value = [False]

    delete_meal(1)

    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace(
        "UPDATE meals SET deleted = TRUE WHERE id = ?"
    )

    actual_select_sql = normalize_whitespace(
        mock_cursor.execute.call_args_list[0][0][0]
    )
    actual_update_sql = normalize_whitespace(
        mock_cursor.execute.call_args_list[1][0][0]
    )

    assert (
        actual_select_sql == expected_select_sql
    ), "The SELECT query did not match the expected structure."
    assert (
        actual_update_sql == expected_update_sql
    ), "The UPDATE query did not match the expected structure."

    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert (
        actual_select_args == expected_select_args
    ), f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert (
        actual_update_args == expected_update_args
    ), f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_delete_meal_bad_id(mock_cursor):
    """Test deleting a non-existent meal."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)


def test_delete_meal_already_deleted(mock_cursor):
    """Test deleting a meal that is already marked as deleted."""

    mock_cursor.fetchone.return_value = [True]

    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)


def test_clear_meals(mock_cursor, mocker):
    """Test clearing all meals."""

    mocker.patch.dict(
        "os.environ", {"SQL_CREATE_TABLE_PATH": "sql/create_meal_table.sql"}
    )
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data="CREATE TABLE meals ...")
    )

    clear_meals()

    mock_open.assert_called_once_with("sql/create_meal_table.sql", "r")
    mock_cursor.executescript.assert_called_once()


def test_get_meal_by_id_success(mock_cursor):
    """Test retrieving a meal by ID successfully."""
    mock_cursor.fetchone.return_value = (
        1,
        "Pasta",
        "Italian",
        10.0,
        "MED",
        False,
        0,
        0,
    )

    meal = get_meal_by_id(1)

    expected_meal = Meal(
        id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED"
    )
    assert meal == expected_meal, f"Expected {expected_meal}, got {meal}"

    mock_cursor.execute.assert_called_once_with(
        "SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?",
        (1,),
    )


def test_get_meal_by_id_not_found(mock_cursor):
    """Test getting a meal by ID that does not exist."""

    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)


def test_get_meal_by_name_success(mock_cursor):
    """Test retrieving a meal by name successfully."""
    mock_cursor.fetchone.return_value = (
        1,
        "Pasta",
        "Italian",
        10.0,
        "MED",
        False,
        0,
        0,
    )

    meal = get_meal_by_name("Pasta")

    expected_meal = Meal(
        id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED"
    )
    assert meal == expected_meal, f"Expected {expected_meal}, got {meal}"


def test_get_meal_by_name_not_found(mock_cursor):
    """Test getting a meal by name that does not exist."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Meal with name Pizza not found"):
        get_meal_by_name("Pizza")


def test_update_meal_stats_win(mock_cursor):
    """Test updating the meal stats for a win."""

    mock_cursor.fetchone.return_value = (False,)

    update_meal_stats(1, "win")

    mock_cursor.execute.assert_any_call("SELECT deleted FROM meals WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call(
        "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,)
    )


def test_update_meal_stats_invalid_result(mock_cursor):
    """Test updating meal stats with an invalid result."""

    mock_cursor.fetchone.return_value = [False]

    with pytest.raises(
        ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."
    ):
        update_meal_stats(1, "draw")


def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test updating meal stats for a meal that has been deleted."""

    mock_cursor.fetchone.return_value = (True,)

    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")


######################################################
#
#    Leaderboard Tests
#
######################################################


def test_get_leaderboard_sort_by_wins(mock_cursor):
    """Test retrieving the leaderboard sorted by wins."""
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 10.0, "MED", 10, 8, 0.8),
        (2, "Sushi", "Japanese", 12.0, "LOW", 12, 9, 0.75),
        (3, "Burger", "American", 8.0, "HIGH", 15, 5, 0.33),
    ]

    leaderboard = get_leaderboard(sort_by="wins")

    expected_leaderboard = [
        {
            "id": 1,
            "meal": "Pasta",
            "cuisine": "Italian",
            "price": 10.0,
            "difficulty": "MED",
            "battles": 10,
            "wins": 8,
            "win_pct": 80.0,
        },
        {
            "id": 2,
            "meal": "Sushi",
            "cuisine": "Japanese",
            "price": 12.0,
            "difficulty": "LOW",
            "battles": 12,
            "wins": 9,
            "win_pct": 75.0,
        },
        {
            "id": 3,
            "meal": "Burger",
            "cuisine": "American",
            "price": 8.0,
            "difficulty": "HIGH",
            "battles": 15,
            "wins": 5,
            "win_pct": 33.0,
        },
    ]

    assert (
        leaderboard == expected_leaderboard
    ), f"Expected {expected_leaderboard}, got {leaderboard}"


def test_get_leaderboard_sort_by_win_pct(mock_cursor):
    """Test retrieving the leaderboard sorted by win percentage."""
    mock_cursor.fetchall.return_value = [
        (1, "Pasta", "Italian", 10.0, "MED", 10, 8, 0.8),
        (2, "Sushi", "Japanese", 12.0, "LOW", 12, 9, 0.75),
        (3, "Burger", "American", 8.0, "HIGH", 15, 5, 0.33),
    ]

    leaderboard = get_leaderboard(sort_by="win_pct")

    expected_leaderboard = [
        {
            "id": 1,
            "meal": "Pasta",
            "cuisine": "Italian",
            "price": 10.0,
            "difficulty": "MED",
            "battles": 10,
            "wins": 8,
            "win_pct": 80.0,
        },
        {
            "id": 2,
            "meal": "Sushi",
            "cuisine": "Japanese",
            "price": 12.0,
            "difficulty": "LOW",
            "battles": 12,
            "wins": 9,
            "win_pct": 75.0,
        },
        {
            "id": 3,
            "meal": "Burger",
            "cuisine": "American",
            "price": 8.0,
            "difficulty": "HIGH",
            "battles": 15,
            "wins": 5,
            "win_pct": 33.0,
        },
    ]

    assert (
        leaderboard == expected_leaderboard
    ), f"Expected {expected_leaderboard}, got {leaderboard}"


def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test retrieving the leaderboard with an invalid sort_by parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_param"):
        get_leaderboard(sort_by="invalid_param")
