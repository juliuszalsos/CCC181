# Week 3: Accessibility check

Tested in Chrome with Lighthouse (Accessibility and Mobile, "Analyze page load") at about 378 px wide, running locally with `flask --app app run --debug`. Date: 2026-10-27.

## 9a. Lighthouse

| Screen | URL | Performance | Accessibility | Best Practices | SEO |
|---|---|---|---|---|---|
| Join | `/join` | 99 | **100** | 100 | 90 |
| My place | `/queue/5` | 99 | **100** | 100 | 90 |
| Staff | `/staff` | 99 | **100** | 100 | 90 |

Screenshots of the final scores:

![Lighthouse score for Join](lighthouse-join.png)
![Lighthouse score for My place](lighthouse-my-place.png)
![Lighthouse score for Staff](lighthouse-staff.png)

**Issues and fixes:** Accessibility scored 100 on every screen, so no failing audits were left to fix.

**What is left:** SEO is 90 on every screen. This is outside the accessibility goal. The likely cause is that the pages have no `<meta name="description">`, which I am leaving for a later week.

## 9b. Keyboard only

Done with the mouse put away, using Tab, Shift+Tab, Enter, Space and the arrow keys.

**Join the queue from the home page**
1. First Tab: the "Skip to main content" link appears.
2. Tab through Join queue, My place, then the home page's Join the queue button, and press Enter.
3. On the form, Tab through Full name, Email, Service (arrow keys choose the option) and the submit button. Enter submits.
4. The My place page opens with the success message.

**Staff dashboard: filter, call, serve**
1. Open Staff access from the footer with Tab and Enter.
2. Tab to the Filter by service dropdown, choose a service with the arrow keys, Tab to Apply and press Enter.
3. Tab to Call next and press Enter. The ticket becomes Called.
4. Tab to Serve and press Enter. The ticket becomes Served.

**Results**
- Every link, field and button could be reached and used with the keyboard.
- The skip link appears on the first Tab.
- The focus position is visible at each step (3 px blue outline from `:focus-visible` in `style.css`).
- Nothing failed, so no fixes were needed.

## 9c. Manual checklist

| Check | Join | My place | Staff |
|---|---|---|---|
| Every input has a visible label | ✅ | ✅ | ✅ |
| Error messages say what to do, in text | ✅ | ✅ | ✅ |
| Status is shown in words, not only color | n/a | ✅ | ✅ |
| Text and buttons are readable at 375 px with no sideways page scroll | ✅ | ✅ | ✅ |
| Buttons are at least about 44 × 44 px on a phone | ✅ | ✅ | ✅ |
| Page has one `<h1>` and headings in order | ✅ | ✅ | ✅ |
| `<html lang="en">` is set | ✅ | ✅ | ✅ |

Notes:
- **Labels:** Join uses `<label for>` on name, email and service. My place has no inputs on the ticket page, and the lookup page labels its "Ticket number" field. Staff labels the service filter.
- **Error messages:** Join shows a message under each field, such as "Enter a valid email address, like juan@example.com." The lookup page says "We couldn't find that ticket number. Check your ticket and try again." Staff actions show text flash messages.
- **Status in words:** badges say Waiting, Called, Served or Cancelled, and My place adds a text headline such as "You're next!". Join has no status, so it is n/a.
- **375 px:** the staff table is replaced by stacked cards on phones, so nothing scrolls sideways.
- **44 px:** `.btn` has `min-height: 44px`, large buttons are 56 px, and the nav pills are 44 px. The footer "Staff access" link has extra padding so it also reaches 44 px.
- **Headings:** each page has one `<h1>` (Join the queue, My place in line, Manage queue). Staff then uses `<h2>` for its cards and tables.
- **Language:** `<html lang="en">` is in `base.html`, so every page has it.