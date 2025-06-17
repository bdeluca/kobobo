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

// E-reader viewport presets for testing
const E_READER_VIEWPORTS = {
  'kobo-glo': { width: 758, height: 1024 },
  'kobo-clara-hd': { width: 1264, height: 1680 },
  'kindle-paperwhite': { width: 758, height: 1024 },
  'kobo-aura': { width: 758, height: 1024 },
  'kobo-sage': { width: 1440, height: 1920 },
  'kobo-elipsa': { width: 1404, height: 1872 }
};

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
              description: 'Viewport width (defaults to Kobo Glo: 758)',
              default: 758
            },
            height: {
              type: 'number', 
              description: 'Viewport height (defaults to Kobo Glo: 1024)',
              default: 1024
            },
            ereader: {
              type: 'string',
              description: 'E-reader preset (kobo-glo, kobo-clara-hd, kindle-paperwhite, kobo-aura, kobo-sage, kobo-elipsa)',
              enum: ['kobo-glo', 'kobo-clara-hd', 'kindle-paperwhite', 'kobo-aura', 'kobo-sage', 'kobo-elipsa']
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
      },
      {
        name: 'test_ereader_compatibility',
        description: 'Test Kobobo interface across multiple e-reader devices and orientations',
        inputSchema: {
          type: 'object',
          properties: {
            path: {
              type: 'string',
              description: 'Path to test (e.g., /, /series, /authors)',
              default: '/'
            },
            devices: {
              type: 'array',
              description: 'E-reader devices to test (default: all)',
              items: {
                type: 'string',
                enum: ['kobo-glo', 'kobo-clara-hd', 'kindle-paperwhite', 'kobo-aura', 'kobo-sage', 'kobo-elipsa']
              }
            },
            orientations: {
              type: 'array',
              description: 'Orientations to test (default: [portrait, landscape])',
              items: {
                type: 'string',
                enum: ['portrait', 'landscape']
              }
            }
          }
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
        const { url = 'http://localhost:5057', width = 758, height = 1024, fullPage = false, ereader } = request.params.arguments || {};
        
        // Use e-reader preset if specified, otherwise use provided dimensions
        let viewport = { width, height };
        if (ereader && E_READER_VIEWPORTS[ereader]) {
          viewport = E_READER_VIEWPORTS[ereader];
        }
        
        await page.setViewportSize(viewport);
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
              text: `Screenshot taken of ${url} at ${viewport.width}x${viewport.height}${ereader ? ` (${ereader})` : ''}${fullPage ? ' (full page)' : ''}`
            }
          ]
        };

      case 'navigate_kobobo':
        const { path, waitFor } = request.params.arguments || {};
        const baseUrl = 'http://localhost:5057';
        const fullUrl = `${baseUrl}${path}`;
        
        await page.setViewportSize({ width: 758, height: 1024 });
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

      case 'test_ereader_compatibility':
        const { 
          path: testPath = '/', 
          devices = ['kobo-glo', 'kobo-clara-hd', 'kindle-paperwhite'], 
          orientations = ['portrait', 'landscape'] 
        } = request.params.arguments || {};
        
        const baseTestUrl = 'http://localhost:5057';
        const fullTestUrl = `${baseTestUrl}${testPath}`;
        const screenshots = [];
        let summary = `E-reader compatibility test for ${testPath}\n\n`;
        
        for (const deviceName of devices) {
          const deviceViewport = E_READER_VIEWPORTS[deviceName];
          if (!deviceViewport) continue;
          
          for (const orientation of orientations) {
            const viewport = orientation === 'landscape' 
              ? { width: deviceViewport.height, height: deviceViewport.width }
              : deviceViewport;
              
            await page.setViewportSize(viewport);
            await page.goto(fullTestUrl, { waitUntil: 'networkidle' });
            
            const screenshot = await page.screenshot({ 
              fullPage: true,
              type: 'png'
            });
            
            screenshots.push({
              type: 'image',
              data: screenshot.toString('base64'),
              mimeType: 'image/png'
            });
            
            summary += `✓ ${deviceName} (${orientation}): ${viewport.width}x${viewport.height}\n`;
          }
        }
        
        return {
          content: [
            {
              type: 'text',
              text: summary + `\nGenerated ${screenshots.length} screenshots across ${devices.length} devices and ${orientations.length} orientations.`
            },
            ...screenshots
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