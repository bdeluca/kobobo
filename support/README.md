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
Take a screenshot of the Kobobo web interface.

**Parameters:**
- `url` (optional): URL to screenshot (default: http://localhost:5057)
- `width` (optional): Viewport width (default: 1280)
- `height` (optional): Viewport height (default: 720)
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

## Usage Examples

```javascript
// Take a screenshot of the main page
screenshot_kobobo()

// Navigate to series page and screenshot
navigate_kobobo({ path: "/series" })

// Take a full page screenshot of authors page
navigate_kobobo({ path: "/authors", fullPage: true })

// Inspect the first book item
inspect_element({ selector: ".book-item" })

// Debug series data
navigate_kobobo({ path: "/debug/series" })
```

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