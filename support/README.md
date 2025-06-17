# Kobobo Playwright MCP Support

This directory contains Playwright MCP (Model Context Protocol) setup for visually testing and debugging the Kobobo web interface.

## Setup

1. Install dependencies:
   ```bash
   cd support
   npm install
   npm run install-browsers
   ```

2. Make sure Kobobo is running:
   ```bash
   # From project root
   ./bin/run.sh
   ```

3. Configure MCP in your Claude Desktop settings to use this server.

## Available Tools

### `screenshot_kobobo`
Take a screenshot of the Kobobo web interface optimized for e-reader testing.

**Parameters:**
- `url` (optional): URL to screenshot (default: http://localhost:5057)
- `width` (optional): Viewport width (default: 758 - Kobo Glo width)
- `height` (optional): Viewport height (default: 1024 - Kobo Glo height)
- `ereader` (optional): E-reader preset (kobo-glo, kobo-clara-hd, kindle-paperwhite, kobo-aura, kobo-sage, kobo-elipsa)
- `fullPage` (optional): Take full page screenshot (default: false)

### `navigate_kobobo`
Navigate to a specific page and take a screenshot.

**Parameters:**
- `path` (required): Path to navigate to (e.g., `/series`, `/authors`, `/debug/series`)
- `waitFor` (optional): CSS selector to wait for before screenshot

### `inspect_element`
Inspect a specific element and return its properties.

**Parameters:**
- `url` (optional): URL to navigate to (default: http://localhost:5057)
- `selector` (required): CSS selector of element to inspect

### `test_ereader_compatibility`
Test Kobobo interface across multiple e-reader devices and orientations.

**Parameters:**
- `path` (optional): Path to test (default: /)
- `devices` (optional): Array of e-reader devices to test (default: ['kobo-glo', 'kobo-clara-hd', 'kindle-paperwhite'])
- `orientations` (optional): Array of orientations to test (default: ['portrait', 'landscape'])

## Usage Examples

```javascript
// Take a screenshot using Kobo Glo dimensions (default)
screenshot_kobobo()

// Test with specific e-reader device
screenshot_kobobo({ ereader: "kobo-clara-hd" })

// Navigate to series page with e-reader viewport
navigate_kobobo({ path: "/series" })

// Test interface across multiple e-readers
test_ereader_compatibility({ path: "/series" })

// Test specific devices and orientations
test_ereader_compatibility({ 
  path: "/authors",
  devices: ["kobo-glo", "kindle-paperwhite"],
  orientations: ["portrait"]
})

// Inspect touch targets for e-reader compatibility
inspect_element({ selector: ".nav-button" })

// Debug with high-DPI e-reader
screenshot_kobobo({ 
  ereader: "kobo-clara-hd", 
  path: "/debug/series", 
  fullPage: true 
})
```

## E-Reader Testing

This MCP server is optimized for testing e-reader compatibility with the following devices:

| Device | Resolution | Common Use |
|--------|------------|------------|
| kobo-glo | 758×1024 | Primary target (most common) |
| kobo-clara-hd | 1264×1680 | High-DPI testing |
| kindle-paperwhite | 758×1024 | Kindle compatibility |
| kobo-aura | 758×1024 | Alternative standard |
| kobo-sage | 1440×1920 | Large screen testing |
| kobo-elipsa | 1404×1872 | Large screen testing |

**Recommendation**: Always test with `kobo-glo` (758×1024) as the primary target, then verify with higher resolution devices.

## Claude Desktop Configuration

Add this to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "kobobo-playwright": {
      "command": "node",
      "args": ["playwright-mcp-server.js"],
      "cwd": "/path/to/kobobo/support"
    }
  }
}
```