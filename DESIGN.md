---
name: Attendance
description: A clear Vietnamese employee work register.
colors:
  ink: "#16372f"
  accent: "#176348"
  paper: "#f5f7f4"
  line: "#dce4dc"
  muted: "#596b61"
  danger: "#a12835"
  white: "#fff"
  accent-hover: "#104b36"
  focus: "#b37e1b"
  intro: "#163e32"
  intro-text: "#f4f2df"
  checkin: "#e7eddf"
  navigation-active: "#e6eee3"
  secondary: "#e9eee5"
  secondary-hover: "#dce6d5"
  field-line: "#bac8bf"
  badge-open: "#e6efdf"
  badge-open-text: "#285436"
  badge-closed: "#eff1ec"
  badge-closed-text: "#52614f"
  badge-off: "#faece9"
  badge-off-text: "#983c31"
typography:
  display:
    fontFamily: "BeVietnamPro, sans-serif"
    fontSize: "clamp(40px, 4.2vw, 66px)"
    fontWeight: 600
    lineHeight: 1.12
    letterSpacing: "-.03em"
  headline:
    fontFamily: "Segoe UI, Arial, sans-serif"
    fontSize: "32px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-.025em"
  title:
    fontFamily: "Segoe UI, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 650
    lineHeight: 1.4
  body:
    fontFamily: "Segoe UI, Arial, sans-serif"
    fontSize: "15px"
    lineHeight: 1.6
  label:
    fontFamily: "Segoe UI, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 600
rounded:
  badge: "5px"
  field: "6px"
  button: "7px"
  container: "8px"
  checkin: "12px"
spacing:
  field-gap: "7px"
  action-gap: "10px"
  filter-gap: "14px"
  grid-gap: "18px"
  section-gap: "20px"
  form-padding: "26px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.white}"
    rounded: "{rounded.button}"
    padding: "11px 19px"
  button-primary-hover:
    backgroundColor: "{colors.accent-hover}"
  button-secondary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: "11px 19px"
  button-secondary-hover:
    backgroundColor: "{colors.secondary-hover}"
  field:
    backgroundColor: "{colors.white}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "10px 12px"
  checkin-panel:
    backgroundColor: "{colors.checkin}"
    rounded: "{rounded.checkin}"
    padding: "32px 36px"
  badge-open:
    backgroundColor: "{colors.badge-open}"
    textColor: "{colors.badge-open-text}"
    rounded: "{rounded.badge}"
    padding: "4px 9px"
---

# Design System: Attendance

## Overview

**Creative North Star: "The Employee Work Register"**

This code-led operational interface puts one shift action beside a prominent clock and readable records. Forest green, soft paper, white tables and restrained corners support repeated daytime use. The login heading supplies the Vietnamese typographic identity; operational screens use familiar system text.

This document records the implemented system in `app/public/style.css`, `index.html` and `app.js`, with direction from `docs/surface-attendance.md`. It describes actual behavior rather than proposing new components.

**Key Characteristics:**
- A pale attendance field anchors the current action.
- Tables preserve legibility through local horizontal scrolling.
- Text labels accompany every operational status.
- No decorative raster product assets; evidence screenshots must be real captures.

## Colors

### Primary

Forest accent identifies primary actions and editable row actions. Its darker hover sibling provides feedback. Deep intro green and warm intro text establish the login surface. Gold is reserved for the wordmark dot and visible keyboard focus.

### Neutral

Ink carries main text; muted green-gray supports metadata. Paper surrounds white navigation, forms and tables. Line and field-line distinguish container boundaries and input outlines. Pale checkin green marks the attendance action area, while navigation-active marks the selected destination.

### Semantic

Open shifts use green badges, completed shifts neutral badges, and disabled employee accounts pale red badges. Danger marks destructive row actions and error text. Success notices use a pale green field; error notices use pale red. Status text remains present alongside color.

## Typography

The self-hosted BeVietnamPro semibold face is used only for the login headline, with a sans-serif fallback and `font-display: swap`. Segoe UI, Arial, sans-serif carries the rest of the interface. No external font request is required.

Desktop page headings use the headline role; section headings use title. The login form heading is 28px. Labels are 13px/600, table headings 12px/600, table cells 13px, badges 11px and footer metadata 11–12px. Body line height is 1.6. The clock uses 54px/600, tabular numerals and a 1.25 line height; tables also use tabular numerals. The wordmark is 27px/750 with tight tracking.

## Layout

Desktop workspace uses a 240px navigation rail and a flexible `minmax(0,1fr)` content column. Main content has 42px horizontal padding. Heading spacing is 38px above and 30px below. The attendance panel places the clock and a 280px-wide form side by side with a 40px gap. Editable forms use two equal columns with an 18px gap.

At viewport widths up to 1000px, the rail becomes 200px, content padding 24px, attendance-panel padding 26px and gap 22px; the clock becomes 44px and the authenticated-session indicator is hidden.

At widths up to 700px, the rail becomes a top navigation surface. Navigation scrolls horizontally within itself; the sidebar identity block disappears and header logout appears. Content padding becomes 18px. The header wraps, page heading becomes 26px, attendance panel stacks with a full-width form and a 46px clock, filters wrap and editable forms become one column. Tables keep nowrap cells inside their scroll container. Footer items stack.

Login uses a 1.05fr/1fr split with a full-height intro and a centered form capped at 390px. At 700px it becomes one column: the intro has a 250px minimum height, 28px padding and a 36px headline; supplementary intro copy and footer are hidden. Login form padding becomes 36px 28px.

## Elevation & Depth

No box shadows are used. Depth comes from paper/white/pale-green tonal fields, fine borders and spacing. The attendance panel is the strongest tonal container; tables and admin forms remain quiet white surfaces.

## Shapes

Use the observed radius roles in the frontmatter: field, button, container, attendance panel and badge. Borders are generally 1px. The brand dot, live indicator and avatar are circles. Avoid introducing pills or floating card shadows into this register.

## Components

### Buttons and focus

Primary and secondary buttons have a 44px minimum height and 600 weight. Row actions use transparent backgrounds, 12px text and a 36px minimum height; destructive actions use danger text. Text actions are transparent, muted and underline on hover. Disabled buttons use 0.55 opacity and a wait cursor. Do not infer an additional loading spinner.

Buttons, links, inputs and selects share a 3px gold `:focus-visible` outline with 3px offset. Background transitions run for 0.15s ease-out only when reduced motion is not requested. Notices reveal through a 0.2s clip animation under the same preference; reduced-motion users receive immediate state changes.

### Fields and inline forms

Inputs and selects use white backgrounds, field-line borders, 44px minimum height and visible labels. Helpers use muted regular-weight text. Native required, email, pattern, length and date/time controls supply validation. Admin forms open inline above tables; cancel hides them. Saving successfully hides the form; API errors appear in the shared notice.

### Navigation

Default destinations are muted on transparent backgrounds. Hover adds a pale field; the selected destination uses pale green with stronger ink and weight. Admin destinations are hidden for employees. Page switches update the breadcrumb, selected button and visible section, and hide the previous notice.

### Attendance field

The live clock and dates use Asia/Ho_Chi_Minh. An open shift selects its actual shift ID, disables selection, replaces Vào ca with Ra ca and shows the shift name and arrival time. With no shifts, selection and check-in are disabled and explanatory copy appears; admins also receive a direct add-shift action. Empty daily records explain how to start; empty history explains that no record matches the date range.

### Tables, badges and notices

Tables use muted headings on a lightly tinted white header, 15px 18px cell padding (13px on mobile), fine row separators and no final-row border. Employee names sit above muted codes. Badge labels distinguish open, completed and inactive states. Unavailable times use an em dash. Shared notices use `role="status"`; login errors use `role="alert"`. The shared notice remains until navigation or another notice replaces it. Browser-native confirmation is used before deleting a shift or disabling an employee.

## Do's and Don'ts

### Do:
- **Do** preserve Vietnamese labels, explicit status text and tabular time values.
- **Do** keep the primary action in the attendance field and admin editing in its own destination.
- **Do** retain local table/navigation overflow and the visible keyboard outline.
- **Do** use the CSS source as authority if implementation changes after this snapshot.

### Don't:
- **Don't** add decorative raster imagery, fabricated evidence or unsupported production claims.
- **Don't** use color alone to communicate attendance or account status.
- **Don't** introduce shadows or a second decorative typeface into operational screens.
- **Don't** describe unimplemented skeletons, tooltips or modal components as existing system behavior.
