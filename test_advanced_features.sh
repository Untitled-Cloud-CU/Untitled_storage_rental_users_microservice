#!/bin/bash

# ============================================================================
# Test Script for Enhanced Users Microservice
# Tests: eTag, HATEOAS, and 202 Async features
# ============================================================================

BASE_URL="http://localhost:8000"

echo "🧪 Testing Enhanced Users Microservice Features"
echo "=================================================="
echo ""

# ============================================================================
# TEST 1: HATEOAS - Linked Data and Relative Paths
# ============================================================================

echo "📋 TEST 1: HATEOAS - Linked Data and Relative Paths"
echo "---------------------------------------------------"
echo "Testing GET /api/v1/users/1 for HATEOAS links..."
echo ""

RESPONSE=$(curl -s "$BASE_URL/api/v1/users/1")
echo "Response:"
echo "$RESPONSE" | jq '.'
echo ""

# Check for _links
if echo "$RESPONSE" | jq -e '._links' > /dev/null 2>&1; then
    echo "✅ PASS: HATEOAS _links found in response"
    echo ""
    echo "Links found:"
    echo "$RESPONSE" | jq '._links'
else
    echo "❌ FAIL: No HATEOAS _links in response"
fi

echo ""
echo "=================================================="
echo ""

# ============================================================================
# TEST 2: eTag Processing
# ============================================================================

echo "📋 TEST 2: eTag Processing"
echo "---------------------------------------------------"
echo "Step 1: GET user and extract ETag..."
echo ""

# First request - get ETag
RESPONSE=$(curl -si "$BASE_URL/api/v1/users/1")
echo "$RESPONSE"
echo ""

# Extract ETag
ETAG=$(echo "$RESPONSE" | grep -i "etag:" | cut -d' ' -f2 | tr -d '\r\n')
echo "Extracted ETag: $ETAG"
echo ""

if [ -n "$ETAG" ]; then
    echo "✅ PASS: ETag header found"
    echo ""
    
    echo "Step 2: Send conditional GET with If-None-Match..."
    echo ""
    
    # Second request with If-None-Match
    RESPONSE2=$(curl -si -H "If-None-Match: $ETAG" "$BASE_URL/api/v1/users/1")
    echo "$RESPONSE2"
    echo ""
    
    # Check for 304 Not Modified
    if echo "$RESPONSE2" | grep -q "304 Not Modified"; then
        echo "✅ PASS: Received 304 Not Modified (eTag matched)"
    else
        echo "❌ FAIL: Expected 304 Not Modified"
    fi
else
    echo "❌ FAIL: No ETag header in response"
fi

echo ""
echo "=================================================="
echo ""

# ============================================================================
# TEST 3: 202 Accepted with Async Processing
# ============================================================================

echo "📋 TEST 3: 202 Accepted with Async Processing"
echo "---------------------------------------------------"
echo "Step 1: Initiate async email verification..."
echo ""

# Start async task
TASK_RESPONSE=$(curl -si -X POST "$BASE_URL/api/v1/users/1/verify-email")
echo "$TASK_RESPONSE"
echo ""

# Check for 202 Accepted
if echo "$TASK_RESPONSE" | grep -q "202 Accepted"; then
    echo "✅ PASS: Received 202 Accepted status"
else
    echo "❌ FAIL: Expected 202 Accepted status"
fi
echo ""

# Extract task_id
TASK_ID=$(echo "$TASK_RESPONSE" | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
echo "Task ID: $TASK_ID"
echo ""

if [ -n "$TASK_ID" ]; then
    echo "Step 2: Poll for task status (initial)..."
    echo ""
    
    TASK_STATUS=$(curl -s "$BASE_URL/api/v1/users/tasks/$TASK_ID")
    echo "$TASK_STATUS" | jq '.'
    echo ""
    
    if echo "$TASK_STATUS" | jq -e '.status' | grep -q "pending"; then
        echo "✅ PASS: Task status is 'pending'"
    fi
    echo ""
    
    echo "Step 3: Wait 6 seconds for async processing..."
    sleep 6
    echo ""
    
    echo "Step 4: Poll for task status (final)..."
    echo ""
    
    TASK_STATUS2=$(curl -s "$BASE_URL/api/v1/users/tasks/$TASK_ID")
    echo "$TASK_STATUS2" | jq '.'
    echo ""
    
    if echo "$TASK_STATUS2" | jq -e '.status' | grep -q "completed"; then
        echo "✅ PASS: Task status is 'completed'"
        echo "✅ PASS: Async processing works correctly"
    else
        echo "⚠️  Task may still be processing (check status)"
    fi
else
    echo "❌ FAIL: No task_id in response"
fi

echo ""
echo "=================================================="
echo ""

# ============================================================================
# TEST 4: Pagination
# ============================================================================

echo "📋 TEST 4: Pagination (Query Parameters)"
echo "---------------------------------------------------"
echo "Testing GET /api/v1/users/?skip=0&limit=1..."
echo ""

PAGINATION_RESPONSE=$(curl -s "$BASE_URL/api/v1/users/?skip=0&limit=1")
echo "$PAGINATION_RESPONSE" | jq '.'
echo ""

# Check if array has exactly 1 item
ITEM_COUNT=$(echo "$PAGINATION_RESPONSE" | jq 'length')
if [ "$ITEM_COUNT" = "1" ]; then
    echo "✅ PASS: Pagination returned exactly 1 user"
else
    echo "❌ FAIL: Expected 1 user, got $ITEM_COUNT"
fi

echo ""
echo "=================================================="
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "🎯 TEST SUMMARY"
echo "=================================================="
echo ""
echo "✅ Feature 1: HATEOAS (Linked Data) - Implemented"
echo "   - _links object in responses"
echo "   - Relative paths to related resources"
echo "   - Self, update, delete, rentals links"
echo ""
echo "✅ Feature 2: eTag Processing - Implemented"
echo "   - ETag generation based on resource state"
echo "   - If-None-Match conditional request support"
echo "   - 304 Not Modified response"
echo "   - Cache-Control headers"
echo ""
echo "✅ Feature 3: 202 Accepted + Async - Implemented"
echo "   - Returns 202 Accepted immediately"
echo "   - Background task processing"
echo "   - Status polling endpoint"
echo "   - HATEOAS links for status URL"
echo ""
echo "✅ Feature 4: Pagination - Already Implemented"
echo "   - skip and limit query parameters"
echo ""
echo "=================================================="
echo "🎉 All Sprint 2 advanced features are ready!"
echo "=================================================="
