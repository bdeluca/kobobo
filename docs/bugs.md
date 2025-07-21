# Known Bugs in Kobobo

## Pagination Issues

### 1. Empty Book List Edge Case
**Location**: `src/blueprints/books.py:33-34`
**Description**: When `total_books = 0`, `total_pages` becomes 0, but then `page` is set to 0 which is invalid (pages should start at 1).
**Impact**: Could cause errors when there are no books in the library.
**Fix**: Use `max(1, (total_books + books_per_page - 1) // books_per_page)` to ensure `total_pages` is at least 1.

### 2. Disabled Pagination Arrow Styling
**Location**: `src/static/pagination.css:49-60`
**Description**: Disabled arrows have `cursor: not-allowed` but are using `<div>` elements instead of links.
**Impact**: Inconsistent UX - cursor suggests interactivity when there is none.
**Fix**: Add `pointer-events: none` to the `.pagination-arrow.disabled` CSS rule.

### 3. Page Indicator Positioning
**Location**: `src/static/pagination.css:66`
**Description**: Page indicator is positioned at `bottom: 90px` with comment "Above alphabet navigation", but no alphabet navigation exists in the books template.
**Impact**: Potentially incorrect positioning on the page.
**Note**: May be leftover from another view or future feature.

## Recent Commit History Issues

The recent commits show a pattern of back-and-forth changes around pagination:
- Multiple attempts to implement pagination (JavaScript vs server-side)
- Reverts and re-implementations
- Switching between bottom pagination and side arrows
- Jinja2 template compatibility issues (min function not available)

This suggests the pagination feature needs a more stable implementation that works reliably on Kobo devices.