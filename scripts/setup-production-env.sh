#!/bin/bash

# Production Environment Setup Script for Heroku
# Run this script to configure all required environment variables

APP_NAME="capecraft"

echo "🔧 Setting up production environment variables for $APP_NAME..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first."
    exit 1
fi

# Generate secure random keys
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)

echo "🔐 Generated secure keys..."

# Set critical environment variables
heroku config:set ENVIRONMENT="production" -a $APP_NAME
heroku config:set DEBUG="False" -a $APP_NAME
heroku config:set SECRET_KEY="$SECRET_KEY" -a $APP_NAME
heroku config:set JWT_SECRET_KEY="$JWT_SECRET_KEY" -a $APP_NAME
heroku config:set SESSION_SECRET="$SESSION_SECRET" -a $APP_NAME

# Set CORS and security
heroku config:set CORS_ORIGINS="https://www.cape-control.com,https://cape-control.com" -a $APP_NAME
heroku config:set ALLOWED_HOSTS="www.cape-control.com,cape-control.com" -a $APP_NAME
heroku config:set FRONTEND_ORIGIN="https://www.cape-control.com" -a $APP_NAME

# Set API configuration
heroku config:set API_BASE_URL="https://www.cape-control.com/api" -a $APP_NAME

# Set S3 configuration (you'll need to provide these)
echo "⚠️  Please set the following S3 variables manually:"
echo "heroku config:set AWS_ACCESS_KEY_ID=\"your-aws-access-key\" -a $APP_NAME"
echo "heroku config:set AWS_SECRET_ACCESS_KEY=\"your-aws-secret-key\" -a $APP_NAME"
echo "heroku config:set AWS_STORAGE_BUCKET_NAME=\"lightning-s3\" -a $APP_NAME"
echo "heroku config:set AWS_S3_REGION_NAME=\"us-east-1\" -a $APP_NAME"

# Set email configuration (you'll need to provide these)
echo "📧 Please set the following email variables manually:"
echo "heroku config:set SMTP_SERVER=\"smtp.gmail.com\" -a $APP_NAME"
echo "heroku config:set SMTP_PORT=\"587\" -a $APP_NAME"
echo "heroku config:set SMTP_USE_TLS=\"true\" -a $APP_NAME"
echo "heroku config:set SMTP_USERNAME=\"your-email@cape-control.com\" -a $APP_NAME"
echo "heroku config:set SMTP_PASSWORD=\"your-email-password\" -a $APP_NAME"
echo "heroku config:set FROM_EMAIL=\"noreply@cape-control.com\" -a $APP_NAME"

# Check if PostgreSQL add-on is installed
if heroku addons:info heroku-postgresql -a $APP_NAME &> /dev/null; then
    echo "✅ PostgreSQL add-on is already installed"
else
    echo "📊 Installing PostgreSQL add-on..."
    heroku addons:create heroku-postgresql:essential-0 -a $APP_NAME
fi

echo "✅ Basic production environment setup complete!"
echo ""
echo "🔍 Current configuration:"
heroku config -a $APP_NAME

echo ""
echo "🚀 Next steps:"
echo "1. Set your AWS S3 credentials"
echo "2. Set your email service credentials"
echo "3. Deploy your application"
echo "4. Test the production environment"
echo ""
echo "📝 Security checklist:"
echo "- [ ] SECRET_KEY is unique and secure"
echo "- [ ] DEBUG is False"
echo "- [ ] PostgreSQL is configured"
echo "- [ ] CORS origins are production domains only"
echo "- [ ] All sensitive credentials are set"
