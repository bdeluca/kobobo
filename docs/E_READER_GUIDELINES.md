# E-Reader Design Guidelines for Kobobo

## Overview

This document outlines design and development guidelines for ensuring Kobobo works optimally on e-reader devices, particularly Kobo and Kindle devices with their limited browsers and e-ink display characteristics.

## E-Reader Constraints & Limitations

### Browser Capabilities
- **JavaScript**: Limited or disabled on most e-readers
- **CSS**: Basic CSS support only, avoid modern features
- **HTML**: Stick to standard HTML elements
- **Network**: Slow and limited bandwidth
- **Processing**: Limited CPU/memory compared to tablets/phones

### E-Ink Display Characteristics
- **Refresh Rate**: Slow refresh, minimize page changes
- **Colors**: Grayscale only (16 levels typically)
- **Contrast**: High contrast needed for readability
- **Ghosting**: Previous content may remain faintly visible

## Design Principles

### 1. Simplicity First
- Use simple, linear layouts
- Minimize complex CSS styling
- Avoid animations and transitions
- Use basic table-based layouts when needed

### 2. Touch-Friendly Interface
- **Minimum touch target size**: 44px × 44px
- **Spacing**: At least 8px between interactive elements
- **Clear boundaries**: Visual indication of clickable areas
- **Large buttons**: Prefer larger buttons over small links

### 3. Typography & Readability
- **Font sizes**: Minimum 14px, prefer 16px+ for body text
- **Font families**: Stick to web-safe fonts (Arial, serif)
- **Line height**: 1.4-1.6 for optimal reading
- **Contrast**: Dark text on light backgrounds
- **Text length**: Keep line lengths reasonable (45-75 characters)

### 4. Layout Guidelines
- **Single column**: Avoid complex multi-column layouts
- **Progressive disclosure**: Show essential info first
- **Consistent navigation**: Same navigation pattern throughout
- **Breadcrumbs**: Help users understand their location

## Viewport Specifications

### Common E-Reader Resolutions

| Device | Portrait | Landscape | Notes |
|--------|----------|-----------|-------|
| Kobo Glo | 758×1024 | 1024×758 | Most common |
| Kobo Clara HD | 1264×1680 | 1680×1264 | High DPI |
| Kindle Paperwhite | 758×1024 | 1024×758 | Standard |
| Kobo Aura | 758×1024 | 1024×758 | Standard |
| Kobo Sage | 1440×1920 | 1920×1440 | Large screen |
| Kobo Elipsa | 1404×1872 | 1872×1404 | Large screen |

### Primary Target
**Kobo Glo (758×1024)** should be the primary design target as it represents the most common e-reader resolution.

## HTML/CSS Best Practices

### ✅ DO Use
- Basic HTML tags: `div`, `p`, `h1-h6`, `table`, `img`, `a`
- Simple CSS properties: `margin`, `padding`, `border`, `background-color`
- Table-based layouts for complex layouts
- Inline styles when needed for critical styling
- High contrast colors
- Large, clear fonts

### ❌ AVOID
- JavaScript (may not work)
- CSS Grid or Flexbox (limited support)
- CSS animations and transitions
- Small fonts (< 14px)
- `:hover` effects (no mouse on touch devices)
- Complex nested layouts
- Background images for critical content
- Fixed positioning (can cause issues)

## Navigation Patterns

### 1. Main Navigation
- Use large, clearly labeled buttons
- Arrange in simple grid pattern
- Provide visual feedback for active state

### 2. List Navigation
- Alphabetical indices for large lists
- Pagination for long lists
- Clear "Back" navigation

### 3. Book Browsing
- Grid layout with large cover images
- Essential info only (title, author)
- Clear download/view buttons

## Testing Checklist

### Basic Functionality
- [ ] All pages load within 5 seconds
- [ ] Touch targets are at least 44px
- [ ] Text is readable at default zoom
- [ ] Navigation works without JavaScript
- [ ] Images load and display correctly

### E-Reader Specific
- [ ] Test on Kobo Glo resolution (758×1024)
- [ ] Test in both portrait and landscape
- [ ] Verify high contrast readability
- [ ] Check touch responsiveness
- [ ] Validate with slow network simulation

### Accessibility
- [ ] Proper heading hierarchy (h1, h2, h3)
- [ ] Alt text for all images
- [ ] Clear focus indicators
- [ ] Logical tab order

## Performance Guidelines

### Loading Speed
- **Target**: Pages should load in under 3 seconds on slow connections
- **Images**: Optimize cover images (JPEG, max 150KB each)
- **CSS**: Minimize and inline critical CSS
- **Requests**: Minimize HTTP requests

### Bandwidth Considerations
- Use compressed images
- Minimize external resources
- Implement efficient caching headers
- Consider lazy loading for image grids

## Implementation Notes

### CSS Reset/Base
```css
/* E-reader friendly base styles */
body {
    font-family: Arial, sans-serif;
    font-size: 16px;
    line-height: 1.5;
    margin: 0;
    padding: 8px;
    color: #000;
    background: #fff;
}

/* Touch-friendly buttons */
.button {
    display: block;
    min-height: 44px;
    min-width: 44px;
    padding: 12px 16px;
    margin: 8px 0;
    border: 2px solid #000;
    background: #fff;
    color: #000;
    text-decoration: none;
    text-align: center;
}

.button:active {
    background: #f0f0f0;
}
```

### JavaScript Alternatives
- Use server-side rendering instead of client-side dynamic content
- Implement search as full page reloads
- Use form submissions instead of AJAX
- Provide static fallbacks for dynamic features

## Testing Tools

Use the Playwright MCP tools to test across different e-reader resolutions:

```javascript
// Test main page across all e-readers
test_ereader_compatibility({ path: "/" })

// Test specific device
screenshot_kobobo({ ereader: "kobo-glo", path: "/series" })

// Test landscape orientation
screenshot_kobobo({ 
  ereader: "kobo-clara-hd", 
  width: 1680, 
  height: 1264 
})
```

## Common Issues & Solutions

### Issue: Touch targets too small
**Solution**: Ensure all clickable elements are at least 44×44px

### Issue: Text too small to read
**Solution**: Use minimum 14px font size, prefer 16px+

### Issue: Complex layouts break
**Solution**: Simplify to single-column, linear layouts

### Issue: Slow page loads
**Solution**: Optimize images, minimize HTTP requests

### Issue: Navigation confusing
**Solution**: Implement clear breadcrumbs and consistent back buttons

## References

- [Kobo Developer Guidelines](https://www.kobo.com/developer)
- [E-Ink Display Characteristics](https://developer.amazon.com/docs/kindle/design-guidelines.html)
- [Touch Target Sizing (Apple HIG)](https://developer.apple.com/design/human-interface-guidelines/buttons)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)