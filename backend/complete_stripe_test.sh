#!/bin/bash
# Complete Stripe Integration Test
echo "🚀 Starting Complete Stripe Integration Test..."

echo "📋 Step 1: Testing environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
    if grep -q "STRIPE_SECRET_KEY=sk_test_" .env; then
        echo "✅ Stripe secret key configured"
    else
        echo "❌ Stripe secret key missing or invalid"
    fi
    
    if grep -q "STRIPE_PUBLISHABLE_KEY=pk_test_" .env; then
        echo "✅ Stripe publishable key configured"
    else
        echo "❌ Stripe publishable key missing or invalid"
    fi
    
    if grep -q "STRIPE_WEBHOOK_SECRET=whsec_" .env; then
        echo "✅ Stripe webhook secret configured"
    else
        echo "⚠️  Stripe webhook secret needs to be updated"
        echo "   Copy the webhook secret from your Stripe Dashboard"
    fi
else
    echo "❌ .env file not found"
fi

echo ""
echo "📋 Step 2: Testing Stripe routes import..."
python3 -c "
try:
    from app.routes.stripe_routes import router
    print('✅ Stripe routes imported successfully')
    print(f'✅ {len(router.routes)} routes available')
except Exception as e:
    print(f'❌ Stripe routes import failed: {e}')
"

echo ""
echo "📋 Step 3: Starting FastAPI server..."
echo "🌐 Server will be available at: http://localhost:8000"
echo "📋 API Documentation: http://localhost:8000/docs"
echo "🔗 Webhook endpoint: http://localhost:8000/api/stripe/webhook"
echo ""
echo "⏯️  Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
