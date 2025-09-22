# from backend/ directory
# if you have python-dotenv installed (requirements include it), you can do:
export $(grep -v '^#' .env.development | xargs)

# Alternatively, explicitly source if file is plain shell-style:
set -o allexport; source .env.development; set +o allexport

# Ensure these are set (optional check)
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo "REDIS_URL=$REDIS_URL"