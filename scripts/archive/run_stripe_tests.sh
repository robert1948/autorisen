#!/bin/bash
# Stripe Testing Suite for CapeControl
# Run comprehensive tests for Stripe integration

echo "🧪 CapeControl Stripe Testing Suite"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if requests is available
if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠️  Installing requests module..."
    pip3 install requests
fi

echo ""
echo "🚀 Running Tests..."
echo ""

# 1. Quick API test
echo "1️⃣  Quick API Test"
echo "----------------"
python3 quick_stripe_test.py
quick_result=$?

echo ""

# 2. Comprehensive test
echo "2️⃣  Comprehensive Integration Test"
echo "-------------------------------"
python3 stripe_comprehensive_test.py
comprehensive_result=$?

echo ""

# 3. Manual testing guidance
echo "3️⃣  Manual Testing"
echo "----------------"
echo "📋 Manual testing checklist available in:"
echo "   STRIPE_MANUAL_TESTING_CHECKLIST.md"
echo ""
echo "🔗 Key URLs to test manually:"
echo "   • Pricing: https://cape-control.com/api/payment/pricing"
echo "   • Subscribe: https://cape-control.com/subscribe"
echo "   • Credits: https://cape-control.com/credits"
echo ""

# 4. Advanced testing with auth
echo "4️⃣  Advanced Testing (Optional)"
echo "-----------------------------"
echo "For authenticated testing, run:"
echo "   python3 test_stripe_integration.py --token YOUR_JWT_TOKEN"
echo ""

# Summary
echo "="*50
echo "📊 Testing Summary"
echo "="*50

if [ $quick_result -eq 0 ]; then
    echo "✅ Quick Test: PASSED"
else
    echo "❌ Quick Test: FAILED"
fi

if [ $comprehensive_result -eq 0 ]; then
    echo "✅ Comprehensive Test: PASSED"
else
    echo "❌ Comprehensive Test: FAILED"
fi

echo ""
echo "📚 Additional Resources:"
echo "   • STRIPE_TESTING_GUIDE.md - Complete testing documentation"
echo "   • STRIPE_MANUAL_TESTING_CHECKLIST.md - Manual testing steps"
echo "   • Stripe Dashboard: https://dashboard.stripe.com/test"
echo ""

# Exit with appropriate code
if [ $quick_result -eq 0 ] && [ $comprehensive_result -eq 0 ]; then
    echo "🎉 All automated tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Check the output above for details."
    exit 1
fi
