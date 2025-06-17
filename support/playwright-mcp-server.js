#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { chromium } from 'playwright';

const server = new Server(
  {
    name: 'kobobo-playwright',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

let browser = null;
let page = null;

// Tool to take a screenshot of the Kobobo interface
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'screenshot_kobobo',
        description: 'Take a screenshot of the Kobobo web interface',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'URL to screenshot (defaults to http://localhost:5057)',
              default: 'http://localhost:5057'
            },
            width: {
              type: 'number',
              description: 'Viewport width',
              default: 1280
            },
            height: {
              type: 'number', 
              description: 'Viewport height',
              default: 720
            },
            fullPage: {
              type: 'boolean',
              description: 'Take full page screenshot',
              default: false
            }
          }
        }
      },
      {
        name: 'navigate_kobobo',
        description: 'Navigate to a specific page and take screenshot',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to navigate to (e.g., /series, /authors, /debug/series)'
            },
            waitFor: {
              type: 'string',
              description: 'CSS selector to wait for before screenshot'
            }
          },
          required: ['path']
        }
      },
      {
        name: 'inspect_element',
        description: 'Inspect a specific element and return its properties',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'URL to navigate to',
              default: 'http://localhost:5057'
            },
            selector: {
              type: 'string',
              description: 'CSS selector of element to inspect'
            }
          },
          required: ['selector']
        }
      }
    ]
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (!browser) {
    browser = await chromium.launch({ headless: true });
  }
  
  if (!page) {
    page = await browser.newPage();
  }

  try {
    switch (request.params.name) {
      case 'screenshot_kobobo':
        const { url = 'http://localhost:5057', width = 1280, height = 720, fullPage = false } = request.params.arguments || {};
        
        await page.setViewportSize({ width, height });
        await page.goto(url, { waitUntil: 'networkidle' });
        
        const screenshot = await page.screenshot({ 
          fullPage,
          type: 'png'
        });
        
        return {
          content: [
            {
              type: 'image',
              data: screenshot.toString('base64'),
              mimeType: 'image/png'
            },
            {
              type: 'text',
              text: `Screenshot taken of ${url} at ${width}x${height}${fullPage ? ' (full page)' : ''}`
            }
          ]
        };

      case 'navigate_kobobo':
        const { path, waitFor } = request.params.arguments || {};
        const baseUrl = 'http://localhost:5057';
        const fullUrl = `${baseUrl}${path}`;
        
        await page.setViewportSize({ width: 1280, height: 720 });
        await page.goto(fullUrl, { waitUntil: 'networkidle' });
        
        if (waitFor) {
          await page.waitForSelector(waitFor, { timeout: 5000 });
        }
        
        const navScreenshot = await page.screenshot({ 
          fullPage: true,
          type: 'png'
        });
        
        return {
          content: [
            {
              type: 'image',
              data: navScreenshot.toString('base64'),
              mimeType: 'image/png'
            },
            {
              type: 'text',
              text: `Navigated to ${fullUrl}${waitFor ? ` and waited for ${waitFor}` : ''}`
            }
          ]
        };

      case 'inspect_element':
        const { url: inspectUrl = 'http://localhost:5057', selector } = request.params.arguments || {};
        
        await page.goto(inspectUrl, { waitUntil: 'networkidle' });
        
        const element = await page.locator(selector).first();
        const isVisible = await element.isVisible();
        const boundingBox = await element.boundingBox();
        const textContent = await element.textContent();
        const innerHTML = await element.innerHTML();
        
        return {
          content: [
            {
              type: 'text',
              text: `Element inspection for selector: ${selector}\n` +
                    `Visible: ${isVisible}\n` +
                    `Bounding box: ${JSON.stringify(boundingBox)}\n` +
                    `Text content: ${textContent}\n` +
                    `Inner HTML: ${innerHTML}`
            }
          ]
        };

      default:
        throw new Error(`Unknown tool: ${request.params.name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

// Cleanup on exit
process.on('SIGINT', async () => {
  if (browser) {
    await browser.close();
  }
  process.exit(0);
});

async function runServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Kobobo Playwright MCP server running on stdio');
}

runServer().catch(console.error);