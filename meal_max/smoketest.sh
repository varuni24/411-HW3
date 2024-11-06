#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

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
# Kitchen Management
#
##########################################################

create_kitchen_item() {
  name=$1
  category=$2
  price=$3
  quantity=$4

  echo "Adding kitchen item ($name, $category, $price) to the catalog..."
  curl -s -X POST "$BASE_URL/create-item" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"category\":\"$category\", \"price\":$price, \"quantity\":$quantity}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Item added successfully."
  else
    echo "Failed to add item."
    exit 1
  fi
}

delete_kitchen_item_by_id() {
  item_id=$1

  echo "Deleting kitchen item ID ($item_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-item/$item_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Item deleted successfully ID ($item_id)."
  else
    echo "Failed to delete item ID ($item_id)."
    exit 1
  fi
}

get_all_kitchen_items() {
  echo "Getting all kitchen items in the catalog..."
  response=$(curl -s -X GET "$BASE_URL/get-all-items")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All items retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Items JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get items."
    exit 1
  fi
}

get_kitchen_item_by_id() {
  item_id=$1

  echo "Getting kitchen item by ID ($item_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-item-by-id/$item_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Item retrieved successfully by ID ($item_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Item JSON (ID $item_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get item by ID ($item_id)."
    exit 1
  fi
}

get_kitchen_item_by_name() {
  name=$1

  echo "Getting kitchen item by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-item-by-name?name=$(echo $name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Item retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Item JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get item by name."
    exit 1
  fi
}

get_random_kitchen_item() {
  echo "Getting a random kitchen item..."
  response=$(curl -s -X GET "$BASE_URL/get-random-item")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random item retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Item JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get a random item."
    exit 1
  fi
}


############################################################
#
# Kitchen Inventory Management
#
############################################################

update_item_quantity() {
  item_id=$1
  quantity=$2

  echo "Updating item quantity for item ID $item_id to $quantity..."
  response=$(curl -s -X PUT "$BASE_URL/update-item-quantity/$item_id" \
    -H "Content-Type: application/json" \
    -d "{\"quantity\":$quantity}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Item quantity updated successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Updated Item JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to update item quantity."
    exit 1
  fi
}

clear_inventory() {
  echo "Clearing inventory..."
  response=$(curl -s -X POST "$BASE_URL/clear-inventory")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Inventory cleared successfully."
  else
    echo "Failed to clear inventory."
    exit 1
  fi
}


############################################################
#
# Order Management
#
############################################################

create_order() {
  item_id=$1
  quantity=$2

  echo "Creating order for item ID $item_id with quantity $quantity..."
  response=$(curl -s -X POST "$BASE_URL/create-order" \
    -H "Content-Type: application/json" \
    -d "{\"item_id\":$item_id, \"quantity\":$quantity}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Order created successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Order JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to create order."
    exit 1
  fi
}

get_order_by_id() {
  order_id=$1

  echo "Getting order by ID ($order_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-order-by-id/$order_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Order retrieved successfully by ID ($order_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Order JSON (ID $order_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get order by ID ($order_id)."
    exit 1
  fi
}

##########################################################
#
# BattleModel
#
##########################################################


test_battle_model_init() {
  echo "Testing BattleModel initialization..."
  response=$(curl -s -X POST "$BASE_URL/init-battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "BattleModel initialized successfully."
  else
    echo "Failed to initialize BattleModel."
    exit 1
  fi
}


test_battle_model_battle() {
  echo "Testing BattleModel battle..."
  response=$(curl -s -X POST "$BASE_URL/start-battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle completed successfully."
  else
    echo "Battle test failed."
    exit 1
  fi
}


test_battle_model_clear_combatants() {
  echo "Testing BattleModel clear_combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

# Function calls to check the health and database connection
check_health
check_db

# Run the kitchen item tests
create_kitchen_item "Wisk" "Appliances" 50.99 10
create_kitchen_item "Blender" "Appliances" 30.99 20
get_all_kitchen_items
get_kitchen_item_by_id 1
get_kitchen_item_by_name "Blender"
update_item_quantity 1 15
delete_kitchen_item_by_id 1

# Run the order tests
create_order 1 2
get_order_by_id 1

# Run the tests for BattleModel
test_battle_model_init
test_battle_model_battle
test_battle_model_clear_combatants


# Clearing inventory
clear_inventory
