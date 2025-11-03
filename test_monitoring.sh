#!/bin/bash

# Social Mode Monitoring Test Script

echo "🧪 Testing Social Mode Monitoring System"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
SERVER_URL="http://localhost:7030"
TEST_USERNAME="testagent"
TEST_PASSWORD="test123"

# Check if server is running
echo "📡 Checking if server is running..."
if ! curl -s "${SERVER_URL}" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running on ${SERVER_URL}${NC}"
    echo "Please start the server with: yarn dev:server"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test 1: API Login
echo "🔐 Test 1: API Login"
echo "--------------------"
LOGIN_RESPONSE=$(curl -s -X POST "${SERVER_URL}/api/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${TEST_USERNAME}\",\"password\":\"${TEST_PASSWORD}\"}")

if echo "$LOGIN_RESPONSE" | grep -q "success"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
    echo -e "${GREEN}✅ API login successful${NC}"
    echo "Token: ${TOKEN:0:20}..."
    echo ""
else
    echo -e "${RED}❌ API login failed${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test 2: Move agent
echo "🚶 Test 2: Move Agent via API"
echo "------------------------------"
MOVE_RESPONSE=$(curl -s -X POST "${SERVER_URL}/api/move" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"x":25,"y":25}')

if echo "$MOVE_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ Agent moved to (25, 25)${NC}"
    echo ""
else
    echo -e "${RED}❌ Move failed${NC}"
    echo "Response: $MOVE_RESPONSE"
fi

# Test 3: Get player status
echo "📊 Test 3: Get Player Status"
echo "-----------------------------"
STATUS_RESPONSE=$(curl -s -X GET "${SERVER_URL}/api/player" \
  -H "Authorization: Bearer ${TOKEN}")

if echo "$STATUS_RESPONSE" | grep -q "username"; then
    echo -e "${GREEN}✅ Got player status${NC}"
    echo "$STATUS_RESPONSE" | jq '.'
    echo ""
else
    echo -e "${YELLOW}⚠️  Status endpoint may not exist${NC}"
    echo ""
fi

# Test 4: Instructions for Web UI
echo "🌐 Test 4: Web UI Observer (Manual Test)"
echo "------------------------------------------"
echo "Now test the Web UI observer:"
echo ""
echo -e "${YELLOW}1. Open browser: ${SERVER_URL}${NC}"
echo -e "${YELLOW}2. Login with:${NC}"
echo "   Username: ${TEST_USERNAME}"
echo "   Password: ${TEST_PASSWORD}"
echo ""
echo -e "${GREEN}Expected result:${NC}"
echo "  ✅ You should login successfully as an observer"
echo "  ✅ You should see the agent at position (25, 25)"
echo "  ✅ You should be able to control the agent from Web UI"
echo ""
echo -e "${YELLOW}3. In another terminal, move the agent:${NC}"
echo "   curl -X POST ${SERVER_URL}/api/move \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -H \"Authorization: Bearer ${TOKEN}\" \\"
echo "     -d '{\"x\":30,\"y\":30}'"
echo ""
echo -e "${GREEN}Expected result:${NC}"
echo "  ✅ Web UI should see the agent move to (30, 30) in real-time"
echo ""

# Test 5: Multiple observers
echo "👥 Test 5: Multiple Observers (Manual Test)"
echo "--------------------------------------------"
echo "Test multiple observers:"
echo ""
echo -e "${YELLOW}1. Keep the first browser window open${NC}"
echo -e "${YELLOW}2. Open a second browser window (or different browser)${NC}"
echo -e "${YELLOW}3. Login again with the same credentials${NC}"
echo ""
echo -e "${GREEN}Expected result:${NC}"
echo "  ✅ Both windows should show the same agent"
echo "  ✅ Moving in one window updates the other"
echo "  ✅ Server logs should show: 'Observer added for player: ${TEST_USERNAME}'"
echo ""

# Final instructions
echo "📝 Server Logs to Check"
echo "-----------------------"
echo "Look for these messages in server logs:"
echo "  - Web UI observer connected for player: ${TEST_USERNAME}"
echo "  - Observer added for player: ${TEST_USERNAME}"
echo "  - Observer removed for player: ${TEST_USERNAME}"
echo ""

echo "🎉 API tests complete!"
echo "Now perform the manual Web UI tests described above."
echo ""
echo "To clean up, you can logout the agent:"
echo "  curl -X POST ${SERVER_URL}/api/logout \\"
echo "    -H \"Authorization: Bearer ${TOKEN}\""

