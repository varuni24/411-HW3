import unittest
import sqlite3
from meal_max.models.kitchen_model import(
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)


class TestMealModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = sqlite3.connect(":memory:")
        cls.create_table()

    @classmethod
    def create_table(cls):
        cls.connection.execute("""
            CREATE TABLE meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal TEXT NOT NULL UNIQUE,
                cuisine TEXT NOT NULL,
                price REAL NOT NULL,
                difficulty TEXT NOT NULL CHECK (difficulty IN ('LOW', 'MED', 'HIGH')),
                deleted BOOLEAN NOT NULL DEFAULT FALSE,
                battles INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0
            )
        """)

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        self.clear_database()

    def clear_database(self):
        self.connection.execute("DELETE FROM meals")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_create_meal_valid(self):
        """Test creating a meal successfully."""
        create_meal("Sushi", "Japanese", 20.00, "HIGH")
        meal = get_meal_by_name("Sushi")
        self.assertEqual(meal.meal, "Sushi")
        self.assertEqual(meal.cuisine, "Japanese")
        self.assertEqual(meal.price, 20.00)
        self.assertEqual(meal.difficulty, "HIGH")

    def test_create_meal_invalid_price(self):
        """Test creating a meal with invalid price."""
        with self.assertRaises(ValueError) as context:
            create_meal("Pizza", "Italian", -10.00, "MED")
        self.assertEqual(str(context.exception), "Invalid price: -10.0. Price must be a positive number.")

    def test_create_meal_invalid_difficulty(self):
        """Test creating a meal with an invalid difficulty."""
        with self.assertRaises(ValueError) as context:
            create_meal("Burger", "British", 10.00, "MEDIUM")
        self.assertEqual(str(context.exception), "Invalid difficulty level: MEDIUM. Must be 'LOW', 'MED', or 'HIGH'.")

    def test_create_meal_duplicate(self):
        """Test creating a duplicate meal."""
        create_meal("Sushi", "Japanese", 20.00, "HIGH")
        with self.assertRaises(ValueError) as context:
            create_meal("Sushi", "Japanese", 20.00, "HIGH")
        self.assertEqual(str(context.exception), "Meal with name Sushi already exists")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_clear_meals_empty(self):
        """Test clearing meals when no meals exist."""
        clear_meals()
        #how to check any error?

    def test_clear_meals(self):
        """Test deleting all meals successfully."""
        create_meal("Burrito", "Mexican", 8.00, "LOW")
        clear_meals()
        with self.assertRaises(ValueError) as context:
            get_meal_by_name("Burrito")
        self.assertEqual(str(context.exception), "Meal with name Burrito not found")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_delete_meal_success(self):
        """Test deleting a meal successfully."""
        create_meal("Spagetti", "Italian", 19.00, "MED")
        meal = get_meal_by_name("Spagetti")
        delete_meal(meal.id)
        with self.assertRaises(ValueError) as context:
            get_meal_by_id(meal.id)
        self.assertEqual(str(context.exception), f"Meal with ID {meal.id} has been deleted")

    def test_delete_nonexistent_meal(self):
        """Test deleting a non-existent meal."""
        with self.assertRaises(ValueError) as context:
            delete_meal(1000000000000000)
        self.assertEqual(str(context.exception), "Meal with ID 1000000000000000 not found")

    def test_delete_deleted(self):
        """Test deleting an already deleted meal."""
        create_meal("Spagetti", "Italian", 19.00, "MED")
        meal = get_meal_by_name("Spagetti")
        delete_meal(meal.id)
        with self.assertRaises(ValueError) as context:
            delete_meal(meal.id)
        self.assertEqual(str(context.exception), f"Meal with ID {meal.id} has been deleted")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_get_leaderboard(self):
        """Test retrieving leaderboard successfully."""
        create_meal("Pasta", "Italian", 5.00, "LOW")
        meal = get_meal_by_name("Pasta")
        update_meal_stats(meal.id, "win")
        leaderboard = get_leaderboard("wins")
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['meal'], "Pasta")
        self.assertEqual(leaderboard[0]['wins'], meal.id)

    def test_get_leaderboard_empty(self):
        """Test leaderboard where no meals exist."""
        leaderboard = get_leaderboard("wins")
        self.assertEqual(leaderboard, [])

    def test_get_leaderboard_invalid_sort(self):
        """Test retrieving leaderboard with invalid sort by."""
        with self.assertRaises(ValueError) as context:
            get_leaderboard("loss")
        self.assertEqual(str(context.exception), "Invalid sort_by parameter: loss")



    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_get_meal_by_id_success(self):
        """Test retrieving a meal by ID successfully."""
        create_meal("Tacos", "Mexican", 8.00, "LOW")
        meal = get_meal_by_name("Tacos")
        self.assertEqual(meal.meal, "Tacos")
        self.assertEqual(meal.cuisine, "Mexican")
        self.assertEqual(meal.price, 8.00)
        self.assertEqual(meal.difficulty, "LOW")

    def test_get_meal_by_id_deleted(self):
        """Test getting a meal by ID that has already been deleted."""
        create_meal("Chole Bature", "Indian", 13.00, "MED")
        meal = get_meal_by_name("Chole Bature")
        delete_meal(meal.id)

        with self.assertRaises(ValueError) as context:
            get_meal_by_id(meal.id)
        self.assertEqual(str(context.exception), "Meal with ID {meal_id} has been deleted")


    def test_get_meal_by_id_not_found(self):
        """Test getting a meal by ID that does not exist."""
        with self.assertRaises(ValueError) as context:
            get_meal_by_id(91286389)
        self.assertEqual(str(context.exception), "Meal with ID 91286389 not found")

    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_get_meal_by_name_success(self):
        """Test retrieving a meal by name successfully."""
        create_meal("Pasta", "Italian", 8.00, "LOW")
        meal = get_meal_by_name("Pasta")
        self.assertEqual(meal.meal, "Pasta")
        self.assertEqual(meal.cuisine, "Italian")

    def test_get_meal_by_name_not_found(self):
        """Test getting a meal by name that does not exist."""
        with self.assertRaises(ValueError) as context:
            get_meal_by_name("ASDFGHKL")
        self.assertEqual(str(context.exception), "Meal with name ASDFGHKL not found")

    def test_get_meal_by_name_deleted(self):
        """Test getting a meal by name that has been deleted"""
        create_meal("Butter Chicken", "Indian", 20.00, "MED")
        meal = get_meal_by_name("Butter Chicken")
        self.assertIsNotNone(meal)
        delete_meal(meal.id)

        with self.assertRaises(ValueError) as context:
            get_meal_by_name("Butter Chicken")
        self.assertEqual(str(context.exception), f"Meal with name Butter Chicken has been deleted")


    #---------------------------------------------------------------------------------------------------------------------------------------

    def test_update_meal_stats_win_success(self):
        """Test updating meal stats successfully for a win."""
        create_meal("Sushi", "Japanese", 20.00, "HIGH")
        meal = get_meal_by_name("Sushi")
        update_meal_stats(meal.id, "win")
        updated_meal = get_meal_by_id(meal.id)
        self.assertEqual(updated_meal.battles, 1)
        self.assertEqual(updated_meal.wins, 1)

    def test_update_meal_stats_loss_success(self):
        """Test updating meal stats successfully for a loss."""
        create_meal("Ramen", "Japanese", 15.00, "MED")
        meal = get_meal_by_name("Ramen")
        update_meal_stats(meal.id, "loss")
        updated_meal = get_meal_by_id(meal.id)
        self.assertEqual(updated_meal.battles, 1)
        self.assertEqual(updated_meal.wins, 0)

    def test_update_meal_stats_invalid_result(self):
        """Test updating meal stats with invalid result."""
        create_meal("Taco", "Mexican", 10.00, "LOW")
        meal = get_meal_by_name("Taco")
        with self.assertRaises(ValueError) as context:
            update_meal_stats(meal.id, "tie")
        self.assertEqual(str(context.exception), "Invalid result: tie. Expected 'win' or 'loss'.")

    def test_update_meal_stats_deleted_meal(self):
        """Test updating meal stats for a meal that is deleted."""
        create_meal("Pasta", "Italian", 14.00, "MED")
        meal = get_meal_by_name("Pasta")
        delete_meal(meal.id)

        with self.assertRaises(ValueError) as context:
            update_meal_stats(meal.id, "win")
        self.assertEqual(str(context.exception), f"Meal with ID {meal.id} has been deleted")

    def test_update_meal_stats_nonexistent_meal(self):
        """Test updating meal stats for non-existent meal."""
        with self.assertRaises(ValueError) as context:
            update_meal_stats(834838, "win")
        self.assertEqual(str(context.exception), "Meal with ID 834838 not found")

    def test_update_meal_stats_multiple_updates(self):
        """Test multiple updates to same meal."""
        create_meal("Mac&Cheese", "American", 6.00, "LOW")
        meal = get_meal_by_name("Mac&Cheese")

        update_meal_stats(meal.id, "win")
        update_meal_stats(meal.id, "loss")
        update_meal_stats(meal.id, "win")
        update_meal_stats(meal.id, "loss")

        updated_meal = get_meal_by_id(meal.id)
        self.assertEqual(updated_meal.battles, 4)
        self.assertEqual(updated_meal.wins, 2)

    #---------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
