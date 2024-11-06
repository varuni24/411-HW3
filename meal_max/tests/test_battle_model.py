import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal
from unittest.mock import patch, Mock


@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()


@pytest.fixture
def sample_meal1():
    return Meal(id=1, meal="Meal 1", cuisine="Cuisine A", price=10.0, difficulty="MED")


@pytest.fixture
def sample_meal2():
    return Meal(id=2, meal="Meal 2", cuisine="Cuisine B", price=15.0, difficulty="LOW")


@pytest.fixture
def sample_meal3():
    return Meal(id=3, meal="Meal 3", cuisine="Cuisine C", price=20.0, difficulty="HIGH")


##################################################
# Prep Combatants Test Cases
##################################################


def test_prep_combatant_success(battle_model, sample_meal1):
    """Test adding a single combatant successfully."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Meal 1"


def test_prep_combatant_full_list(
    battle_model, sample_meal1, sample_meal2, sample_meal3
):
    """Test error when trying to add more than two combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with pytest.raises(
        ValueError, match="Combatant list is full, cannot add more combatants."
    ):
        battle_model.prep_combatant(sample_meal3)


##################################################
# Clear Combatants Test Cases
##################################################


def test_clear_combatants(battle_model, sample_meal1, sample_meal2):
    """Test clearing all combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    assert len(battle_model.combatants) == 2
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


def test_clear_empty_combatants(battle_model):
    """Test clearing an already empty combatants list."""
    assert len(battle_model.combatants) == 0
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0


##################################################
# Battle Functionality Test Cases
##################################################


def test_battle_success(battle_model, sample_meal1, sample_meal2):
    """Test a successful battle between two meals."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with patch("meal_max.models.battle_model.get_random", return_value=0.1), patch(
        "meal_max.models.battle_model.update_meal_stats"
    ) as mock_update_stats:
        winner = battle_model.battle()
        assert winner in [
            "Meal 1",
            "Meal 2",
        ], f"Expected 'Meal 1' or 'Meal 2' to win, got {winner}"
        assert len(battle_model.combatants) == 1
        mock_update_stats.assert_any_call(sample_meal1.id, "win")
        mock_update_stats.assert_any_call(sample_meal2.id, "loss")


def test_battle_random_tie(battle_model, sample_meal1, sample_meal2):
    """Test a battle where the random value prevents a clear winner."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    with patch("meal_max.models.battle_model.get_random", return_value=0.9), patch(
        "meal_max.models.battle_model.update_meal_stats"
    ) as mock_update_stats:
        winner = battle_model.battle()
        assert winner in [
            "Meal 1",
            "Meal 2",
        ], f"Expected 'Meal 1' or 'Meal 2' to win, got {winner}"
        assert len(battle_model.combatants) == 1
        mock_update_stats.assert_called()


def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test battle initiation with fewer than two combatants raises an error."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(
        ValueError, match="Two combatants must be prepped for a battle."
    ):
        battle_model.battle()


##################################################
# Battle Score Calculation Test Cases
##################################################


def test_get_battle_score(battle_model, sample_meal1):
    """Test calculating the battle score of a combatant."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (
        sample_meal1.price * len(sample_meal1.cuisine)
    ) - 2  # MED difficulty modifier is 2
    assert score == expected_score, f"Expected score {expected_score}, got {score}"


def test_get_battle_score_high_difficulty(battle_model, sample_meal3):
    """Test calculating the battle score of a HIGH difficulty combatant."""
    score = battle_model.get_battle_score(sample_meal3)
    expected_score = (
        sample_meal3.price * len(sample_meal3.cuisine)
    ) - 1  # HIGH difficulty modifier is 1
    assert score == expected_score, f"Expected score {expected_score}, got {score}"


def test_get_battle_score_low_difficulty(battle_model, sample_meal2):
    """Test calculating the battle score of a LOW difficulty combatant."""
    score = battle_model.get_battle_score(sample_meal2)
    expected_score = (
        sample_meal2.price * len(sample_meal2.cuisine)
    ) - 3  # LOW difficulty modifier is 3
    assert score == expected_score, f"Expected score {expected_score}, got {score}"


##################################################
# Get Combatants Test Cases
##################################################


def test_get_combatants_empty(battle_model):
    """Test retrieving combatants when none are present."""
    combatants = battle_model.get_combatants()
    assert len(combatants) == 0


def test_get_combatants_with_entries(battle_model, sample_meal1, sample_meal2):
    """Test retrieving combatants when two are present."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Meal 1"
    assert combatants[1].meal == "Meal 2"
