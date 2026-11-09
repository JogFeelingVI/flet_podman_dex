# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-11-03 00:04:17
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-11-03 00:05:21
# @File    : default.py
# @Time    : 2026/11/03 08:04:23
# @Author  : ---
name: Nocturne Romance
colors:
  surface: '#14121b'
  surface-dim: '#14121b'
  surface-bright: '#3b3842'
  surface-container-lowest: '#0f0d16'
  surface-container-low: '#1c1a24'
  surface-container: '#211e28'
  surface-container-high: '#2b2933'
  surface-container-highest: '#36333e'
  on-surface: '#e6e0ee'
  on-surface-variant: '#e5bdc0'
  inverse-surface: '#e6e0ee'
  inverse-on-surface: '#322f39'
  outline: '#ac888b'
  outline-variant: '#5c3f42'
  surface-tint: '#ffb2ba'
  primary: '#ffb2ba'
  on-primary: '#670020'
  primary-container: '#ff4f73'
  on-primary-container: '#5a001b'
  inverse-primary: '#bd0042'
  secondary: '#d0bcff'
  on-secondary: '#3c0091'
  secondary-container: '#571bc1'
  on-secondary-container: '#c4abff'
  tertiary: '#ffb1c0'
  on-tertiary: '#660029'
  tertiary-container: '#e96486'
  on-tertiary-container: '#5a0023'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffd9dc'
  primary-fixed-dim: '#ffb2ba'
  on-primary-fixed: '#400011'
  on-primary-fixed-variant: '#910030'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#ffd9df'
  tertiary-fixed-dim: '#ffb1c0'
  on-tertiary-fixed: '#3f0016'
  on-tertiary-fixed-variant: '#88183e'
  background: '#14121b'
  on-background: '#e6e0ee'
  surface-variant: '#36333e'
typography:
  headline-xl:
    fontFamily: Sora
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Sora
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Sora
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Sora
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  title-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-sm: 0.75rem
  gutter-lg: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style
The design system establishes an intimate, cinematic atmosphere tailored for premium romantic storytelling and entertainment streaming. The visual identity merges the luxury of midnight theater spaces with the passionate warmth of romantic drama, evoking intrigue, emotional resonance, and escapism.

The design movement combines **Dark Cinema Ergonomics** with **Sensory Glassmorphism**:
- **Atmospheric Depth:** Deep obsidian and midnight violet canvases recede into the distance, letting rich video key art and romantic narratives take center stage.
- **Luminescent Translucency:** Frosted glass surfaces with subtle inner borders diffuse underlying artwork, evoking velvet night textures and cinematic light spill.
- **Electric Passion:** Vibrant rose-coral accents act as focal beacons, commanding immediate emotional engagement without visual fatigue.
- **Sleek Modernity:** Precise, high-legibility geometric typography creates an elevated, editorial tone fitting for prestige dramas, reality romance, and episodic storytelling.

## Colors
The palette is calibrated for immersive low-light consumption, prioritizing OLED power efficiency and high dynamic contrast for video thumbnails and posters.

### Palette Architecture
- **Primary (`#FF3366` - Vivid Rose Coral):** Represents desire, emotion, and vital action. Used strictly for hero CTAs, playback scrubber playheads, match percentages, and critical interactive active states.
- **Secondary (`#8B5CF6` - Soft Violet Glow):** Conveys midnight mystery and enchantment. Deployed for subtle linear gradient overlays, premium badges, and secondary highlight states.
- **Tertiary (`#FF7597` - Blushed Orchid):** Used for micro-interactions, favorites/like toggles, and delicate romantic tag elements.
- **Neutral Base (`#0D0B14` - Midnight Obsidian):** The deep root canvas. Absorbs excess screen glare and delivers near-infinite contrast against bright video art.

### Surface System
- **Base Canvas:** `#0D0B14`
- **Surface Elevation 1 (Card/Sheet):** `#161224` (or `rgba(22, 18, 36, 0.72)` when paired with backdrop blur)
- **Surface Elevation 2 (Floating Popover/Navbar):** `rgba(32, 25, 53, 0.85)`
- **Glass Border Stroke:** `rgba(255, 255, 255, 0.08)` to `rgba(255, 51, 102, 0.20)` for active states
- **Text & Foreground:**
  - High Contrast (Primary Typography): `#FFFFFF`
  - Medium Contrast (Subtext & Meta): `rgba(255, 255, 255, 0.70)`
  - Low Contrast (Dividers & Inactive): `rgba(255, 255, 255, 0.38)`

## Typography
The typographic pair unites **Sora** and **Plus Jakarta Sans** to balance editorial romance with effortless mobile legibility.

- **Headline Hierarchy (Sora):** Sora brings a geometric yet curvilinear personality that injects modern tech-forward romance into series titles, hero billboards, and screen headings. Its open apertures remain distinct over varied backdrop imagery.
- **Content Hierarchy (Plus Jakarta Sans):** Warm, soft, and balanced, Plus Jakarta Sans handles episode synopses, cast directories, meta tags, and interactive labels without causing visual fatigue during prolonged nocturnal reading.
- **Contrast & Legibility Guidelines:** 
  - All body text over media backgrounds must be accompanied by a directional dark vignette (`rgba(13, 11, 20, 0.90)` to `transparent`).
  - Small labels (such as "4K Ultra HD", "Season 1", or "Top 10") must use `label-sm` with all-caps styling and letter spacing of `0.04em` for crisp rendering across all screen densities.

## Layout & Spacing
The layout follows a fluid-first mobile architecture engineered around edge-to-edge media cards, horizontal carousels, and persistent thumb-zone navigation.

### Mobile Grid & Carousels
- **Mobile (< 768px):** 4-column layout with `1rem` screen margins and `0.75rem` column gutters. Horizontal carousels break canvas bounds, bleeding to the screen edge with a `1rem` trailing snap offset to reveal upcoming content.
- **Tablet (768px - 1024px):** 8-column layout with `1.5rem` margins and `1rem` gutters. Poster grids adapt to 3–4 items per row.
- **Desktop / Large Tablet Landscape (> 1024px):** 12-column layout with `2.5rem` margins and `1.5rem` gutters. Content containers are capped at `1440px` max-width.

### Spacing Cadence
- Use `space-xs` (4px) and `space-sm` (8px) for tightly coupled metadata tags, star ratings, and badge padding.
- Use `space-md` (16px) for standard component interior padding and vertically stacked form elements.
- Use `space-lg` (24px) for spacing between distinct carousel rows and modular card blocks.
- Use `space-xl` (32px) for major vertical section divisions and modal top-padding.

## Elevation & Depth
Depth is established through translucent atmospheric layers, frosted glass backdrops, and colored chromatic glows rather than standard black drop shadows.

### Glassmorphism & Blur Tokens
- **Ambient Frosted Glass:** Background fill of `rgba(22, 18, 36, 0.65)` layered with `backdrop-filter: blur(16px)` and a continuous hairline stroke of `rgba(255, 255, 255, 0.08)`.
- **Raised Glass (Overlays & Sheets):** Background fill of `rgba(32, 25, 53, 0.85)` with `backdrop-filter: blur(24px)` and a subtle directional light border (`border-top: 1px solid rgba(255, 255, 255, 0.15)`).

### Luminescent Glows
- **Primary Action Glow:** On hero buttons and playback triggers, cast an ambient drop shadow tinted with primary color: `0px 8px 24px rgba(255, 51, 102, 0.35)`.
- **Violet Ambient Halos:** Selected video cards and active tab icons emit a diffused violet aura: `0px 4px 20px rgba(139, 92, 246, 0.25)`.
- **Bottom Navigation Dock:** Uses a persistent elevated frost (`rgba(13, 11, 20, 0.88)` with `blur(20px)`) that subtly dissolves content scrolling beneath it.

## Shapes
The shape language uses `roundedness: 2` (base radius of `0.5rem` / 8px) to establish a sleek, modern contour that feels polished, friendly, and touch-ergonomic.

- **Poster & Video Cards:** 12px (`0.75rem`) to 16px (`1rem`) border radius, preserving rectangular cinematic framing while softening edge tension.
- **Buttons & Interactive Tags:** Pill silhouettes (`9999px` radius) are reserved for primary action buttons, category filter chips, and live status badges to ensure quick tap-target recognition.
- **Modals & Bottom Drawers:** 24px (`1.5rem`) top corner radii, providing an organic, curtain-like pull-up appearance on mobile interfaces.

## Components

### Buttons
- **Primary ("Watch Now", "Resume"):** Full pill (`rounded-full`), solid `#FF3366` background, `#FFFFFF` bold text (`label-lg`), with `box-shadow: 0 8px 24px rgba(255, 51, 102, 0.35)`. Press state reduces opacity to 0.9 and scales to `0.98`.
- **Secondary ("Trailer", "Details"):** Frosted glass pill, `rgba(255, 255, 255, 0.08)` fill, `1px solid rgba(255, 255, 255, 0.18)`, `#FFFFFF` text. On tap, surface lightens to `rgba(255, 255, 255, 0.16)`.
- **Icon Actions (Like, Add to Watchlist, Share):** 44x44px circular glass buttons (`rounded-full`) with centered monochrome iconography that shifts to `#FF3366` when toggled.

### Video Poster & Banner Cards
- **Standard Episode / Show Card:** Aspect ratio 2:3 (vertical poster) or 16:9 (episode thumb). Features a 12px border radius, high-density image cover, and a linear gradient shadow (`rgba(13, 11, 20, 0.85)` at bottom to `transparent` at top) displaying title and match metadata.
- **Glass Metadata Card:** Overlaid glass container with 8px radius, `rgba(22, 18, 36, 0.70)` fill, displaying episode runtime and progress bar.
- **Progress Bar:** 4px height track in `rgba(255, 255, 255, 0.20)`, active track filled with `#FF3366` and subtle glow.

### Chips & Filter Tags
- **Category Filter Chips (e.g., "Slow Burn", "K-Drama", "Rom-Com"):** 32px height, pill shape. Inactive: `rgba(255, 255, 255, 0.06)` background with `rgba(255, 255, 255, 0.7)` text. Active: Linear gradient from `#FF3366` to `#8B5CF6` with `#FFFFFF` text and zero outer border.

### Input Fields & Search Bars
- **Search Bar:** 48px height, rounded to 16px, background `rgba(22, 18, 36, 0.80)`, 1px border `rgba(255, 255, 255, 0.10)`. Focused state transitions border to `#8B5CF6` with a soft 3px outer glow `rgba(139, 92, 246, 0.20)`. Placeholder text in `rgba(255, 255, 255, 0.40)`.
- **Form Inputs:** Labels rendered in `label-md` with `rgba(255, 255, 255, 0.8)`. Error states introduce a vibrant crimson border `#FF4D4D` with helper text below.

### Lists & Episode Directory
- **Episode Row:** Horizontal flex layout with 16:9 thumbnail preview (with duration chip anchored bottom-right), title, episode number, and synopsis. Separated by `1px solid rgba(255, 255, 255, 0.05)`. Active/playing row highlighted with `rgba(255, 51, 102, 0.08)` surface tint and rose icon marker.

### Checkboxes & Toggle Switches
- **Toggles (Autoplay, Subtitles):** 28px height by 48px width pill track. Inactive: `#201935`. Active: `#FF3366`. Circular thumb (22px) in `#FFFFFF` with smooth ease-in-out transition.
# @Email   : glifelse@gmail.com
# @Desc    : 请在此处输入文件描述

