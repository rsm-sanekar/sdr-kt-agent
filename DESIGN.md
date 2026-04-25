# Design System — SDR KT Agent

## Philosophy
Flat design. Light theme. No shadows, no gradients, no blur, no depth tricks.
Visual hierarchy through color, scale, and typography only.
Think bold poster design — every section is a graphic composition.

## Colors
- Background: #FFFFFF
- Foreground: #111827 (Gray 900)
- Primary: #3B82F6 (Blue 500) — action color
- Secondary: #10B981 (Emerald 500) — supporting accent
- Accent: #F59E0B (Amber 500) — highlights, badges
- Muted: #F3F4F6 (Gray 100) — secondary backgrounds
- Border: #E5E7EB (Gray 200) — used sparingly

## Typography
- Font: Outfit (Google Fonts)
- Headings: font-weight 700-800, tracking-tight (-0.02em)
- Body: font-weight 400, normal spacing
- Labels/Buttons: font-weight 500-600, uppercase + tracking-wider

## Radius
- Cards and containers: rounded-lg (8px)
- Buttons: rounded-md (6px)
- Tags/pills: rounded-full only

## Shadows and Effects
- NO box shadows on any element ever
- NO backdrop blur
- NO gradients on buttons or cards
- Background decoration only: large geometric shapes, low opacity,
  absolutely positioned

## Buttons
Primary:
- bg-blue-500 text-white rounded-md h-14
- hover:bg-blue-600 hover:scale-105 transition-all duration-200
- No shadow

Secondary:
- bg-gray-100 text-gray-900 rounded-md
- hover:bg-gray-200 hover:scale-105

Outline:
- border-4 border-blue-500 text-blue-500 bg-transparent
- hover:bg-blue-500 hover:text-white (fill effect)

## Cards
- Solid background (white, or color tint: bg-blue-50, bg-emerald-50)
- No shadow, no border
- Padding p-6 or p-8
- rounded-lg
- hover:scale-[1.02] transition-all duration-200

## Inputs
- Normal: bg-gray-100 rounded-md, no border
- Focus: bg-white border-2 border-blue-500, no glow

## Approval Checkpoint Card (appears on every app page)
- bg-gray-50 border-2 border-gray-200 rounded-lg p-6
- Three buttons: Approve (primary), Edit (secondary), Reject (border-4 border-red-500 text-red-500)
- Approved state: bg-emerald-50 border-emerald-500
- Edited state: bg-amber-50 border-amber-500
- Show metadata: generation time, model used

## Layout
- Max width: max-w-7xl
- Grid: 12-column, strict alignment
- Spacing: multiples of 4 (Tailwind default)

## Page Structure

### Homepage (/)
1. Navbar — logo left, nav links center, CTA right
2. Hero — bold headline, subtext, 2 CTA buttons, geometric decoration
3. Problem — 4 pain point stats from baseline metrics
4. How it works — 4 feature cards with icons
5. KB loop — explain self-improving system visually
6. Footer

### App pages (/tutor, /preboarding, /offboarding, /coaching, /dashboard)
- Top navbar (not sidebar)
- Page title + subtitle
- Two-column layout: input left, AI output right
- ApprovalCard always at bottom

## Icons
- Library: lucide-react
- Style: stroke-width 2px
- Treatment: inside solid colored circle (bg-blue-500 text-white,
  h-12 w-12 rounded-full)
- Hover: group-hover:scale-110 transition-transform duration-200

## Section Alternating Backgrounds
- White → Gray 100 → Blue 500 (with white text) → White
- Sharp transitions, no gradients between sections
- Large geometric shapes (circles, squares) absolutely positioned
  at low opacity for visual interest

## Anti-patterns — never do these
- No box shadows
- No backdrop blur
- No dark backgrounds (this is a light theme)
- No colorful gradients
- No sidebar navigation on app pages
- No rounded pills on buttons
- No Material Design floating cards
