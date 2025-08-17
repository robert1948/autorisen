#!/bin/bash

echo "🚀 Testing CapeControl Enhanced Authentication System"
echo "======================================================"

# Test health endpoint
echo "📊 1. Testing Health Endpoint..."
HEALTH=$(curl -s https://www.cape-control.com/api/health)
echo "$HEALTH" | head -3
echo ""

# Test enhanced registration
echo "🧪 2. Testing Enhanced Registration..."
REGISTER_RESPONSE=$(curl -s -X POST https://www.cape-control.com/api/enhanced/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!",
    "firstName": "Test",
    "lastName": "User",
    "role": "customer"
  }')

echo "Registration Response:"
echo "$REGISTER_RESPONSE" | head -5
echo ""

# Test enhanced login
echo "🔐 3. Testing Enhanced Login..."
LOGIN_RESPONSE=$(curl -s -X POST https://www.cape-control.com/api/enhanced/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!"
  }')

echo "Login Response:"
echo "$LOGIN_RESPONSE" | head -5
echo ""

# Extract access token if successful
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$ACCESS_TOKEN" ]; then
    echo "✅ JWT Token extracted successfully"
    echo "Token: ${ACCESS_TOKEN:0:50}..."
    echo ""
    
    # Test protected endpoint
    echo "🛡️  4. Testing Protected Endpoint (/me)..."
    ME_RESPONSE=$(curl -s -X GET https://www.cape-control.com/api/enhanced/me \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    
    echo "User Profile Response:"
    echo "$ME_RESPONSE" | head -3
    echo ""
else
    echo "❌ No access token found in login response"
fi

# Test developer endpoints
echo "💰 5. Testing Developer Earnings Endpoint..."
DEV_RESPONSE=$(curl -s -X GET https://www.cape-control.com/api/enhanced/developer/earnings \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "Developer Earnings Response:"
echo "$DEV_RESPONSE" | head -3
echo ""

echo "🎉 Enhanced Authentication Testing Complete!"
