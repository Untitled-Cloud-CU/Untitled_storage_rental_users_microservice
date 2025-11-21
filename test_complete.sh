#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🧪 COMPLETE Storage Rental Users API Test Suite"
echo "=================================================="

# Test 1: Health Check
echo -e "\n✅ Test 1: Health Check"
curl -s "$BASE_URL/health" | grep -q "healthy" && echo "PASS ✅" || echo "FAIL ❌"

# Test 2-4: Register Users
echo -e "\n✅ Test 2: Register Alice"
ALICE_REG=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Alice","last_name":"Johnson","email":"alice@example.com","password":"AlicePass123","phone":"555-0100"}')
echo $ALICE_REG | grep -q "user_id" && echo "PASS ✅" || echo "FAIL ❌"

echo -e "\n✅ Test 3: Register Bob"
BOB_REG=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Bob","last_name":"Smith","email":"bob@example.com","password":"BobPass123","phone":"555-0200"}')
echo $BOB_REG | grep -q "user_id" && echo "PASS ✅" || echo "FAIL ❌"

echo -e "\n✅ Test 4: Register Carol"
CAROL_REG=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Carol","last_name":"White","email":"carol@example.com","password":"CarolPass123","phone":"555-0300"}')
echo $CAROL_REG | grep -q "user_id" && echo "PASS ✅" || echo "FAIL ❌"

# Test 5-6: Login Tests
echo -e "\n✅ Test 5: Login as Alice"
ALICE_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/users/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"AlicePass123"}')
ALICE_TOKEN=$(echo $ALICE_LOGIN | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo $ALICE_LOGIN | grep -q "token" && echo "PASS ✅ Token: ${ALICE_TOKEN:0:20}..." || echo "FAIL ❌"

echo -e "\n✅ Test 6: Login as Bob"
BOB_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/users/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"bob@example.com","password":"BobPass123"}')
BOB_TOKEN=$(echo $BOB_LOGIN | grep -o '"token":"[^"]*' | cut -d'"' -f4)
echo $BOB_LOGIN | grep -q "token" && echo "PASS ✅ Token: ${BOB_TOKEN:0:20}..." || echo "FAIL ❌"

# Test 7: Get Users
echo -e "\n✅ Test 7: Get All Users"
ALL_USERS=$(curl -s "$BASE_URL/api/v1/users/")
echo $ALL_USERS | grep -q "alice@example.com" && echo "PASS ✅" || echo "FAIL ❌"

# Test 8: Update Own Profile
echo -e "\n✅ Test 8: Alice Updates Own Profile"
UPDATE_ALICE=$(curl -s -X PUT "$BASE_URL/api/v1/users/1" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{"phone":"555-9999"}')
echo $UPDATE_ALICE | grep -q "555-9999" && echo "PASS ✅" || echo "FAIL ❌"

# Test 9: Try to Update Other's Profile
echo -e "\n❌ Test 9: Alice Tries to Update Bob (Should Fail - 403)"
UPDATE_BOB=$(curl -s -X PUT "$BASE_URL/api/v1/users/2" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{"phone":"555-HACKED"}')
echo $UPDATE_BOB | grep -q "Not authorized" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 10: Update Without Token
echo -e "\n❌ Test 10: Update Without Token (Should Fail - 401)"
UPDATE_NO_TOKEN=$(curl -s -X PUT "$BASE_URL/api/v1/users/1" \
  -H 'Content-Type: application/json' \
  -d '{"phone":"555-FAIL"}')
echo $UPDATE_NO_TOKEN | grep -q "detail" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 11: Invalid Token
echo -e "\n❌ Test 11: Update With Invalid Token (Should Fail - 401)"
UPDATE_BAD_TOKEN=$(curl -s -X PUT "$BASE_URL/api/v1/users/1" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer FAKE_TOKEN_123" \
  -d '{"phone":"555-FAIL"}')
echo $UPDATE_BAD_TOKEN | grep -q "Could not validate" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 12: Wrong Password
echo -e "\n❌ Test 12: Login With Wrong Password (Should Fail - 401)"
WRONG_PASS=$(curl -s -X POST "$BASE_URL/api/v1/users/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"WrongPass"}')
echo $WRONG_PASS | grep -q "Incorrect" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 13: Duplicate Email
echo -e "\n❌ Test 13: Register Duplicate Email (Should Fail - 400)"
DUP_EMAIL=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Alice","last_name":"Dup","email":"alice@example.com","password":"Pass123"}')
echo $DUP_EMAIL | grep -q "already registered" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 14: Weak Password (too short)
echo -e "\n❌ Test 14: Register With Weak Password (Should Fail - 422)"
WEAK_PASS=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com","password":"weak"}')
echo $WEAK_PASS | grep -q "detail" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 15: Password Without Digits
echo -e "\n❌ Test 15: Password Without Digits (Should Fail - 422)"
NO_DIGITS=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Test","last_name":"User","email":"test2@example.com","password":"OnlyLetters"}')
echo $NO_DIGITS | grep -q "detail" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 16: Invalid Email Format
echo -e "\n❌ Test 16: Invalid Email Format (Should Fail - 422)"
BAD_EMAIL=$(curl -s -X POST "$BASE_URL/api/v1/users/register" \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Test","last_name":"User","email":"notanemail","password":"Pass123"}')
echo $BAD_EMAIL | grep -q "detail" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 17: Get Non-existent User
echo -e "\n❌ Test 17: Get Non-existent User (Should Fail - 404)"
NOT_FOUND=$(curl -s "$BASE_URL/api/v1/users/999")
echo $NOT_FOUND | grep -q "not found" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 18: Delete Own Account
echo -e "\n✅ Test 18: Carol Deletes Own Account"
CAROL_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/users/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"carol@example.com","password":"CarolPass123"}')
CAROL_TOKEN=$(echo $CAROL_LOGIN | grep -o '"token":"[^"]*' | cut -d'"' -f4)

DELETE_CAROL=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/api/v1/users/3" \
  -H "Authorization: Bearer $CAROL_TOKEN")
echo $DELETE_CAROL | grep -q "204" && echo "PASS ✅" || echo "FAIL ❌"

# Test 19: Try to Delete Other's Account
echo -e "\n❌ Test 19: Bob Tries to Delete Alice (Should Fail - 403)"
DELETE_ALICE=$(curl -s -X DELETE "$BASE_URL/api/v1/users/1" \
  -H "Authorization: Bearer $BOB_TOKEN")
echo $DELETE_ALICE | grep -q "Not authorized" && echo "PASS ✅ (correctly rejected)" || echo "FAIL ❌"

# Test 20: Pagination
echo -e "\n✅ Test 20: Pagination (skip=0, limit=1)"
PAGINATED=$(curl -s "$BASE_URL/api/v1/users/?skip=0&limit=1")
echo $PAGINATED | grep -q "user_id" && echo "PASS ✅" || echo "FAIL ❌"

echo -e "\n\n=================================================="
echo "✅ Testing Complete!"
echo "=================================================="
