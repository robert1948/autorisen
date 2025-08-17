#!/usr/bin/env bash
set -e

# === Directory structure relative to client ===
STATIC_DIR="client/public/static"
MANIFEST_FILE="client/public/static/manifest/site.webmanifest"
S3_BUCKET="s3://lightning-s3/static/website/img"

# === Upload static manifest ===
echo "🚀 Uploading static manifest..."
if [ -f "$MANIFEST_FILE" ]; then
  aws s3 cp "$MANIFEST_FILE" "$S3_BUCKET/site.webmanifest" \
    --content-type "application/manifest+json"
else
  echo "⚠️ Skipped: $MANIFEST_FILE not found."
fi

# Dashboard preview no longer used - replaced with CSS-based hero visual

# === Upload main logo ===
echo "🏷️ Uploading main logo..."
MAIN_LOGO="$STATIC_DIR/capecontrol-logo.png"
if [ -f "$MAIN_LOGO" ]; then
  aws s3 cp "$MAIN_LOGO" "$S3_BUCKET/capecontrol-logo.png" --content-type "image/png"
  echo "📤 $MAIN_LOGO ➜ $S3_BUCKET/capecontrol-logo.png"
else
  echo "⚠️ Skipped: $MAIN_LOGO not found."
fi

# === Upload logo variants ===
echo "🎯 Uploading logo variants..."
for size in 64 128 192 512; do
  LOGO="$STATIC_DIR/logo-${size}x${size}.png"
  if [ -f "$LOGO" ]; then
    echo "📤 $LOGO ➜ $S3_BUCKET/logo-${size}x${size}.png"
    aws s3 cp "$LOGO" "$S3_BUCKET/logo-${size}x${size}.png" --content-type "image/png"
  else
    echo "⚠️ Skipped: $LOGO not found."
  fi
done

# === Upload favicons and icons ===
echo "🌟 Uploading favicons and icons..."
for icon in apple-touch-icon.png favicon-32x32.png favicon-16x16.png android-chrome-192x192.png android-chrome-512x512.png; do
  ICON_PATH="$STATIC_DIR/$icon"
  if [ -f "$ICON_PATH" ]; then
    echo "📤 $ICON_PATH ➜ $S3_BUCKET/$icon"
    aws s3 cp "$ICON_PATH" "$S3_BUCKET/$icon" --content-type "image/png"
  else
    echo "⚠️ Skipped: $ICON_PATH not found."
  fi
done

# === Upload additional images ===
echo "🖼️ Uploading additional images..."
LANDING_IMG="$STATIC_DIR/landing01.png"
if [ -f "$LANDING_IMG" ]; then
  echo "📤 $LANDING_IMG ➜ $S3_BUCKET/landing01.png"
  aws s3 cp "$LANDING_IMG" "$S3_BUCKET/landing01.png" --content-type "image/png"
else
  echo "⚠️ Skipped: $LANDING_IMG not found."
fi

# === Upload main navbar logo ===
echo "🏢 Uploading navbar logo..."
NAVBAR_LOGO="$STATIC_DIR/LogoC.png"
if [ -f "$NAVBAR_LOGO" ]; then
  echo "📤 $NAVBAR_LOGO ➜ $S3_BUCKET/LogoC.png"
  aws s3 cp "$NAVBAR_LOGO" "$S3_BUCKET/LogoC.png" --content-type "image/png"
else
  echo "⚠️ Skipped: $NAVBAR_LOGO not found."
fi

# === Upload white navbar logo ===
echo "🏢 Uploading white navbar logo..."
NAVBAR_LOGO_W="$STATIC_DIR/LogoW.png"
if [ -f "$NAVBAR_LOGO_W" ]; then
  echo "📤 $NAVBAR_LOGO_W ➜ $S3_BUCKET/LogoW.png"
  aws s3 cp "$NAVBAR_LOGO_W" "$S3_BUCKET/LogoW.png" --content-type "image/png"
else
  echo "⚠️ Skipped: $NAVBAR_LOGO_W not found."
fi

# === Upload favicon.ico ===
echo "🔖 Uploading favicon.ico..."
FAVICON_ICO="$STATIC_DIR/favicon.ico"
if [ -f "$FAVICON_ICO" ]; then
  echo "📤 $FAVICON_ICO ➜ $S3_BUCKET/favicon.ico"
  aws s3 cp "$FAVICON_ICO" "$S3_BUCKET/favicon.ico" --content-type "image/x-icon"
else
  echo "⚠️ Skipped: $FAVICON_ICO not found."
fi

echo "✅ All static image assets uploaded with correct headers."

