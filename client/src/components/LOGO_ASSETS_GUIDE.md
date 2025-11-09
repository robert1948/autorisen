# CapeControl Logo Assets Guide

This document explains how to use the various logo sizes and favicon assets created from the original LogoW.png.

## Available Assets

### Favicon Files

- `favicon.ico` - Multi-size ICO file for legacy browsers (16x16, 32x32, 48x48)
- `icons/favicon-16x16.png` - Standard browser tab icon
- `icons/favicon-32x32.png` - High-DPI browser tab icon
- `icons/favicon-48x48.png` - Larger favicon for some contexts

### App Icons

- `icons/apple-touch-icon.png` - 180x180 for iOS home screen
- `icons/android-chrome-192x192.png` - Android Chrome icon
- `icons/android-chrome-512x512.png` - Large Android Chrome icon for PWA

### Logo Variants

- `LogoW.png` - Original 1024x1024 logo (use for default/high-quality contexts)
- `icons/logo-64x64.png` - Small UI components, navigation bars
- `icons/logo-128x128.png` - Medium UI components, card headers
- `icons/logo-256x256.png` - Large UI components, modal headers
- `icons/logo-512x512.png` - Hero sections, splash screens

## Using the Logo Component

The `Logo` component automatically selects the appropriate image size:

```tsx
import Logo from '../components/Logo';

// Default size (uses original LogoW.png)
<Logo />

// Small size (64x64) - for navigation, compact UI
<Logo size="small" />

// Medium size (128x128) - for cards, modals
<Logo size="medium" />

// Large size (256x256) - for hero sections
<Logo size="large" />

// Custom styling
<Logo size="medium" className="my-custom-class" />
```text
## Favicon Implementation

The following HTML meta tags are included in `index.html`:

```html
<!-- Favicon and Icons -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="/icons/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/icons/favicon-48x48.png">

<!-- Apple Touch Icon -->
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">

<!-- Android Chrome Icons -->
<link rel="icon" type="image/png" sizes="192x192" href="/icons/android-chrome-192x192.png">
<link rel="icon" type="image/png" sizes="512x512" href="/icons/android-chrome-512x512.png">

<!-- Web App Manifest -->
<link rel="manifest" href="/site.webmanifest">
```text
## PWA Manifest

The `site.webmanifest` file provides metadata for Progressive Web App installation:

```json
{
  "name": "CapeControl",
  "short_name": "CapeControl",
  "description": "CapeControl authentication and management platform",
  "theme_color": "#007BFF",
  "background_color": "#0f1720"
}
```text
## Best Practices

### When to Use Each Size
- **Small (64x64)**: Navigation bars, inline icons, compact layouts
- **Medium (128x128)**: Card headers, modal headers, medium-sized components
- **Large (256x256)**: Hero sections, splash screens, prominent branding
- **Default (1024x1024)**: High-quality displays, print, maximum resolution needs

### Performance Considerations
- The Logo component automatically serves optimized sizes
- Smaller images load faster and use less bandwidth
- Original high-resolution image is only served when maximum quality is needed

### Responsive Behavior
- CSS automatically scales down logos on mobile devices
- Use appropriate size prop to avoid serving oversized images
- Consider using `srcset` for advanced responsive image loading

## CSS Classes

Additional CSS classes are available for custom styling:

```css
.cc-logo--small   /* 48x48px */
.cc-logo--medium  /* 64x64px */
.cc-logo--large   /* 128x128px */
```text
## File Structure

```text
public/
├── favicon.ico
├── LogoW.png (original)
├── site.webmanifest
└── icons/
    ├── favicon-16x16.png
    ├── favicon-32x32.png
    ├── favicon-48x48.png
    ├── apple-touch-icon.png
    ├── android-chrome-192x192.png
    ├── android-chrome-512x512.png
    ├── logo-64x64.png
    ├── logo-128x128.png
    ├── logo-256x256.png
    └── logo-512x512.png
```text
