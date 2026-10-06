---
name: Culinary Blog
description: A warm, calm recipe site on paper-toned surfaces with one tomato-red action and herb-green accents.
colors:
  tomato-red: "#b82a17"
  tomato-red-deep: "#9a2212"
  herb-green: "#2f6b3f"
  herb-green-deep: "#255735"
  paper: "#fafaf6"
  card-white: "#ffffff"
  ink: "#1f2a22"
  ink-muted: "#55615a"
  sage-mist: "#e6f0e4"
  oat: "#f0f1e8"
  linen: "#eef1e6"
  hairline: "#dfe3d8"
  control-edge: "#8a9486"
  error-red: "#b42318"
  error-tint: "#fbe9e5"
  tint-1: "#e9d8b8"
  tint-2: "#f0dda8"
  tint-3: "#f2c9a8"
  tint-4: "#e5cfc0"
  tint-5: "#cfe0c4"
  tint-6: "#d8dcc0"
  tint-7: "#e8c5c0"
  tint-8: "#c9dcd5"
typography:
  hero:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "56px"
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: "-0.01em"
  page:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "44px"
    fontWeight: 700
    lineHeight: 1.1
  section:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "34px"
    fontWeight: 600
    lineHeight: 1.15
  card-title:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.25
  lede:
    fontFamily: "Be Vietnam Pro, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.6
  body:
    fontFamily: "Be Vietnam Pro, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
  label:
    fontFamily: "Be Vietnam Pro, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 500
  meta:
    fontFamily: "Be Vietnam Pro, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
rounded:
  sm: "4px"
  md: "8px"
  lg: "10px"
  xl: "12px"
  full: "999px"
components:
  button-primary:
    backgroundColor: "{colors.tomato-red}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.md}"
    height: "44px"
    padding: "0 18px"
  button-primary-hover:
    backgroundColor: "{colors.tomato-red-deep}"
  button-herb:
    backgroundColor: "{colors.herb-green}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.md}"
    height: "44px"
    padding: "0 18px"
  button-herb-hover:
    backgroundColor: "{colors.herb-green-deep}"
  button-outline:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "44px"
    padding: "0 18px"
  button-secondary:
    backgroundColor: "{colors.sage-mist}"
    textColor: "{colors.herb-green}"
    rounded: "{rounded.md}"
    height: "44px"
    padding: "0 18px"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "44px"
    padding: "0 12px"
  badge:
    backgroundColor: "{colors.sage-mist}"
    textColor: "{colors.herb-green}"
    rounded: "{rounded.full}"
    height: "24px"
    padding: "0 10px"
  card:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xl}"
    padding: "16px"
---

# Design System: Culinary Blog

## Overview

**Creative North Star: "The Family Recipe Card"**

A well-loved printed recipe card, translated to screen: warm paper underneath, a serif title that feels written rather than set, calm structure, and a single tomato-red action. The food and its tinted placeholders supply the colour; the interface stays quiet so a cook can scan, choose and start cooking.

The mood is warm, calm and practical. Surfaces are flat and separated by hairlines, copy is Vietnamese with full diacritics, and nothing competes with the recipe. It rejects glossy food-magazine drama and loud app chrome.

**Key Characteristics:**
- Paper-toned background (#fafaf6) with white cards and 1px sage hairlines.
- Serif headings (Fraunces) over a humanist sans (Be Vietnam Pro) for UI and body text.
- One tomato-red primary action per view; herb green for brand, links, focus and secondary emphasis.
- Light theme only; no dark mode.
- 44px minimum touch targets on controls.

## Colors

A warm neutral ground, one hot accent, one cool-green companion, and eight food-toned placeholder tints.

### Primary
- **Tomato Red** (#b82a17): the primary call to action, link hover on card titles, and the single hot note on a screen. Deepens to **Tomato Red Deep** (#9a2212) on hover.

### Secondary
- **Herb Green** (#2f6b3f): brand accent, secondary buttons (`herb`), count badges, the focus ring, and text on **Sage Mist** (#e6f0e4) surfaces. Hover **Herb Green Deep** (#255735).

### Neutral
- **Paper** (#fafaf6): page and control background.
- **Card White** (#ffffff): cards and popovers.
- **Ink** (#1f2a22): body and heading text, a green-tinted near-black.
- **Ink Muted** (#55615a): metadata, placeholders, inactive nav.
- **Oat** (#f0f1e8) and **Linen** (#eef1e6): muted and hover surfaces.
- **Hairline** (#dfe3d8): card, header and divider borders.
- **Control Edge** (#8a9486): input and outline-button borders, darker than hairlines so controls remain identifiable.
- **Error Red** (#b42318) on **Error Tint** (#fbe9e5): invalid fields and destructive actions.

### Placeholder Tints
- **Tints 1-8** (#e9d8b8, #f0dda8, #f2c9a8, #e5cfc0, #cfe0c4, #d8dcc0, #e8c5c0, #c9dcd5): backgrounds for recipes without a thumbnail, chosen by a stable hash of the slug so the grid never reshuffles.

### Named Rules
**The One Hot Note Rule.** Tomato red marks the one primary action on a view. Reaching for it as decoration dilutes the action.
**The Food Is The Colour Rule.** Interface chrome stays neutral and green; saturated colour belongs to recipe imagery and placeholder tints.

## Typography

**Display Font:** Fraunces (with Georgia, serif), weights 600 and 700
**Body Font:** Be Vietnam Pro (with system-ui, sans-serif), weights 400 to 700, Latin and Vietnamese subsets

**Character:** A soft, slightly old-style serif for titles paired with a clean humanist sans that handles Vietnamese diacritics well. Headings use the serif automatically (h1-h4); everything else is sans.

### Hierarchy
- **Hero** (700, 56px, 1.08, -0.01em): home hero only.
- **Page** (700, 44px, 1.1): page titles such as a recipe name.
- **Section** (600, 34px, 1.15): section headings.
- **Card Title** (600, 20px, 1.25): recipe card titles.
- **Lede** (400, 18px, 1.6): introductory paragraphs.
- **Body** (400, 14px): default UI and reading text.
- **Label** (500, 14px): buttons, nav links, form labels.
- **Meta** (600, 12px): badges and counts.

### Named Rules
**The Diacritics Rule.** Every size must be checked with Vietnamese text; line heights are set to clear stacked diacritics, so never tighten them for aesthetics.

## Layout

Content sits in a centred container capped at 1200px with 16px side padding on mobile and 32px from tablet up. Breakpoints are 768px (`sm`) and 1200px (`lg`); designs are drawn at 1440, 820 and 390. The header is 64px tall with the main nav appearing from `lg`, search from `md`, and a mobile menu below. Recipe grids size by container width (about 1, 2-3 and 4 columns) rather than by viewport. Spacing follows a 4/8px rhythm.

## Elevation & Depth

Flat by default. Depth comes from 1px hairline borders on white cards over the paper background, not from shadows.

### Shadow Vocabulary
- **Card** (`box-shadow: 0 1px 2px rgb(0 0 0 / 0.05)`): barely-there contact shadow on cards.
- **Card Hover** (`box-shadow: 0 4px 12px rgb(0 0 0 / 0.08)`): the only lift, on hover of an interactive card.
- **Tab** (`box-shadow: 0 1px 2px rgb(0 0 0 / 0.08)`): the selected tab.

### Named Rules
**The Hairline First Rule.** Separate with a border before reaching for a shadow; shadows only respond to interaction.

## Shapes

Gently curved, never pill-shaped except for tags. Controls use an 8px radius, cards 12px, small elements 4px, and badges are fully rounded (999px). Images fill their card top edge, clipped by the card radius, with a bottom hairline. Placeholder images are 4:3.

## Components

### Buttons
- **Shape:** 8px radius, 44px tall (36px small, 44px square icon), 18px horizontal padding, 14px medium text.
- **Primary:** Tomato Red with white text; hover Tomato Red Deep.
- **Herb:** Herb Green with white text; hover Herb Green Deep.
- **Outline:** Paper background, Control Edge border; hover Linen.
- **Secondary:** Sage Mist with Herb Green text.
- **Ghost / Link:** Ghost shows Linen on hover; link is red text with underline on hover.
- **Destructive:** Error Red with white text.
- **Disabled:** 50% opacity, no pointer events.

### Chips and Badges
- **Style:** 24px tall, fully rounded, 12px semibold text.
- **Variants:** secondary (Sage Mist), outline (white with Control Edge), archived (Oat, muted text), overlay (Paper with hairline, sits over images), count (Herb Green).

### Cards / Containers
- **Corner Style:** 12px.
- **Background:** Card White on Paper.
- **Shadow Strategy:** Card at rest, Card Hover on interaction.
- **Border:** 1px Hairline.
- **Internal Padding:** 16px; meta row uses 16px horizontal gaps with 16px icons.

### Inputs / Fields
- **Style:** Paper background, 1px Control Edge border, 8px radius, 44px height, 12px padding, muted placeholder.
- **Focus:** global 2px Herb Green outline with 2px offset.
- **Error / Disabled:** error sets an Error Red border; disabled uses Oat background, Hairline border and muted text.

### Navigation
- **Style:** 64px header on Paper with a hairline bottom border. Links are 44px tall, 8px radius, 14px medium muted text; hover shows Linen background and Ink text. Below `lg` the links collapse into a mobile menu.

### Recipe Card (signature)
A linked white card: 4:3 image or tinted placeholder with a bowl icon, an overlay category badge top left, a serif title that turns Tomato Red on hover, then time and difficulty with small icons and an optional "Bởi {author}" line.

## Do's and Don'ts

### Do:
- **Do** use token classes (`bg-primary`, `text-muted-foreground`, `border-border`), never raw hex.
- **Do** keep one primary tomato-red button per view.
- **Do** give every interactive element a visible focus ring and a 44px target.
- **Do** write all copy in Vietnamese with diacritics, and test long titles.
- **Do** provide loading (skeleton), empty and error states for each screen.
- **Do** keep the placeholder tint stable per recipe.

### Don't:
- **Don't** add gradients, glassmorphism, heavy shadows or a dark theme.
- **Don't** introduce another accent hue or font family.
- **Don't** use red for decoration or for non-primary actions.
- **Don't** imply comments, ratings, bookmarks or other out-of-scope social features.
- **Don't** invent testimonials, user counts or chef profiles.
