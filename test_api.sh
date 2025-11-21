#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🧪 Storage Rental Users API - Test Suite"
echo "=========================================="

# Test 1: Health Check
echo -e "\n✅ Test 1: Health Check"
curl -s "$BASE_URL/health"

# Test 2: Register Alice
echo -e "\n\n✅ Test 2: Register Alice"
curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Alice","last_name":"Johnson","email":"alice@example.com","password":"AlicePass123","phone":"555-0100"}'

# Test 3: Register Bob
echo -e "\n\n✅ Test 3: Register Bob"
curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Bob","last_name":"Smith","email":"bob@example.com","password":"BobPass123","phone":"555-0200"}'

# Test 4: Get All Users
echo -e "\n\n✅ Test 4: Get All Users"
curl -s "$BASE_URL/api/v1/users/"

# Test 5: Login as Alice
echo -e "\n\n✅ Test 5: Login as Alice"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/users/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"AlicePass123"}')
echo $LOGIN_RESPONSE

# Extract token
ALICE_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo -e "\nToken received: ${ALICE_TOKEN:0:20}..."

# Test 6: Update Alice's Info (should work)
echo -e "\n✅ Test 6: Update Alice's Info (Should Work)"
curl -s -X PUT "$BASE_URL/api/v1/users/1" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{"phone":"555-9999","city":"Portland"}'

# Test 7: Try to Update Bob (should fail)
echo -e "\n\n❌ Test 7: Try to Update Bob with Alice's Token (Should Fail)"
curl -s -X PUT "$BASE_URL/api/v1/users/2" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{"phone":"555-HACKED"}'

# Test 8: Wrong password (should fail)
echo -e "\n\n❌ Test 8: Login with Wrong Password (Should Fail)"
curl -s -X POST "$BASE_URL/api/v1/users/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"WrongPassword"}'

echo -e "\n\n✅ All tests complete!"
echo "========================================"
