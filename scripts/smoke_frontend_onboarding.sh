#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://dev.cape-control.com}"
EMAIL="${EMAIL:-tester@example.com}"
PASSWORD="${PASSWORD:-changeme}"

echo "▶ CSRF probe…"
# Keep cookies between calls
COOKIE_JAR="$(mktemp)"
TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -f "$COOKIE_JAR"
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

CSRF_JSON="$(curl -fsSL -c "$COOKIE_JAR" -H "Accept: application/json" \
  "$BASE_URL/api/auth/csrf")"

TOKEN="$(printf '%s' "$CSRF_JSON" | jq -r '.csrf // .csrf_token // .token // empty')"
if [[ -z "$TOKEN" ]]; then
  echo "❌ No CSRF token in JSON body"; exit 1
fi
echo "   CSRF token: ${#TOKEN} chars"

echo "▶ Login…"
LOGIN_PAYLOAD="$(jq -n --arg email "$EMAIL" --arg password "$PASSWORD" '{email:$email,password:$password}')"
LOGIN_BODY="$TMP_DIR/login.json"
LOGIN_CODE="$(curl -s -o "$LOGIN_BODY" -w "%{http_code}" -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $TOKEN" \
  -d "$LOGIN_PAYLOAD" \
  "$BASE_URL/api/auth/login")"

if [[ "$LOGIN_CODE" != "200" && "$LOGIN_CODE" != "204" ]]; then
  echo "❌ Login failed: HTTP $LOGIN_CODE"; cat "$LOGIN_BODY"; exit 1
fi
echo "   Login OK (HTTP $LOGIN_CODE)"

# Capture bearer for subsequent probes
ACCESS_TOKEN="$(jq -r '.access_token // empty' "$LOGIN_BODY" 2>/dev/null || true)"
if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "❌ Login response missing access_token"; cat "$LOGIN_BODY"; exit 1
fi

echo "▶ Who am I…"
/usr/bin/env bash -lc '
  set -euo pipefail
' >/dev/null 2>&1

ME_BODY="$TMP_DIR/me.json"
ME_CODE="$(curl -s -o "$ME_BODY" -w "%{http_code}" -b "$COOKIE_JAR" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  "$BASE_URL/api/auth/me" || true)"

if [[ "$ME_CODE" == "404" ]]; then
  # Fallback if your route is different
  ME_CODE="$(curl -s -o "$ME_BODY" -w "%{http_code}" -b "$COOKIE_JAR" \
    -H "Accept: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    "$BASE_URL/api/me" || true)"
fi

if [[ "$ME_CODE" != "200" ]]; then
  echo "❌ /me probe failed: HTTP $ME_CODE"; cat "$ME_BODY"; exit 1
fi
echo "   /me OK (HTTP $ME_CODE)"

echo "▶ Onboarding status…"
ONB_BODY="$TMP_DIR/onb.json"
ONB_CODE="$(curl -s -o "$ONB_BODY" -w "%{http_code}" -b "$COOKIE_JAR" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  "$BASE_URL/api/onboarding/status" || true)"

if [[ "$ONB_CODE" != "200" && "$ONB_CODE" != "404" ]]; then
  echo "❌ Onboarding status failed: HTTP $ONB_CODE"; cat "$ONB_BODY"; exit 1
fi
if [[ "$ONB_CODE" == "404" ]]; then
  echo "   (Note) Onboarding endpoint not present; skipping."
else
  echo "   Onboarding status OK (HTTP $ONB_CODE)"
fi

echo "✅ Staging smoke passed."
