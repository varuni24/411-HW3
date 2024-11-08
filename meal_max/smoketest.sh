#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

clear_meal_catalog() {
  echo "Clearing the meal catalog..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal catalog cleared successfully."
  else
    echo "Failed to clear meal catalog."
    echo "Response from server: $response"
    exit 1
  fi
}

create_meal() {
  meal_name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal_name, Cuisine: $cuisine) to the catalog..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal_name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    echo "Response from server: $response"
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    echo "Response from server: $response"
    exit 1
  fi
}

get_all_meals() {
  echo "Retrieving all meals in the catalog..."
  response=$(curl -s -X GET "$BASE_URL/get-all-meals")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meals."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Retrieving meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve meal by ID ($meal_id)."
    echo "Response from server: $response"
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1
  echo "Retrieving meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name: $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve meal by name ($meal_name)."
    echo "Response from server: $response"
    exit 1
  fi
}


############################################################
#
# Combatant Management
#
############################################################

prep_combatant() {
  local meal_name="$1"
  echo "Preparing combatant: $meal_name..."
  
  prep_data="{\"meal\": \"$meal_name\"}"
  
  response=$(curl -s -X POST -H "Content-Type: application/json" -d "$prep_data" "$BASE_URL/prep-combatant")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Prep Combatant JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to prepare combatant."
    echo "Response: $response" 
    exit 1
  fi
}


get_combatants() {
  echo "Retrieving all combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve combatants."
    echo "Response from server: $response"
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing all combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    echo "Response from server: $response"
    exit 1
  fi
}


############################################################
#
# Battle Management
#
############################################################

initiate_battle() {
  echo "Initiating a battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle completed successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initiate battle."
    echo "Response from server: $response"
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

get_leaderboard() {
  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    echo "Response from server: $response"
    exit 1
  fi
}


check_health
check_db

clear_meal_catalog

create_meal "Pho" "Vietnamese" 10.99 "MED"
create_meal "Curry" "Indian" 7.99 "LOW"
create_meal "Burger" "American" 15.99 "HIGH"

delete_meal_by_id 1

get_meal_by_id 2
get_meal_by_name "Curry"

prep_combatant "Curry"
prep_combatant "Burger"

get_combatants

initiate_battle

clear_combatants

get_leaderboard

echo "All tests completed successfully!"
