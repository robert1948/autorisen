#!/bin/bash

echo "🚨 Applying CRITICAL security fixes to Heroku production..."
echo "=========================================================="
echo ""

echo "1. 🔐 Setting new secure SECRET_KEY..."
heroku config:set SECRET_KEY="df%RirYXOS3s#5dUleyka3QH$BUose2Nkj!PvxbSljo$ViB3w#g7@5#XOmZg8RD^" -a capecraft

echo ""
echo "2. 🔗 Fixing API URL (adding www)..."
heroku config:set REACT_APP_API_URL="https://www.cape-control.com/api" -a capecraft

echo ""
echo "3. 🛡️ Setting production environment variables..."
heroku config:set DEBUG=False -a capecraft
heroku config:set ENV=production -a capecraft

echo ""
echo "4. 🌐 Configuring CORS origins..."
heroku config:set CORS_ORIGINS="https://www.cape-control.com,https://cape-control.com,https://capecraft.herokuapp.com" -a capecraft

echo ""
echo "5. 🧹 Cleaning up ALLOWED_HOSTS..."
heroku config:set ALLOWED_HOSTS="capecraft.herokuapp.com,cape-control.com,www.cape-control.com" -a capecraft

echo ""
echo "✅ All fixes applied! Verifying configuration..."
echo ""
heroku config -a capecraft

echo ""
echo "🎯 Next steps:"
echo "- Test the production site: https://www.cape-control.com"
echo "- Check health endpoint: https://www.cape-control.com/api/health"
echo "- Update local .env file"
echo "- Deploy updated code to GitHub"
