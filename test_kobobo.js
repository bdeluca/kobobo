const { chromium } = require('playwright');

async function testKobobo() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Set Kobo viewport
  await page.setViewportSize({ width: 758, height: 1024 });
  
  try {
    // Test 1: Main page screenshot
    console.log('Taking screenshot of main page...');
    await page.goto('http://127.0.0.1:5057', { waitUntil: 'networkidle' });
    await page.screenshot({ path: '/mnt/d/work/kobobo/tmp/main-page.png' });
    console.log('Main page screenshot saved to tmp/main-page.png');
    
    // Test 2: Navigate to series page
    console.log('Navigating to series page...');
    await page.goto('http://127.0.0.1:5057/series', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000); // Wait for any dynamic content
    await page.screenshot({ path: '/mnt/d/work/kobobo/tmp/series-page.png' });
    console.log('Series page screenshot saved to tmp/series-page.png');
    
    // Test 3: Check if books are visible on series page
    const booksVisible = await page.locator('.book-item').count();
    console.log(`Number of visible books on series page: ${booksVisible}`);
    
    // Test 4: Test pagination controls
    console.log('Testing pagination controls...');
    
    // Check if pagination arrows exist
    const upArrow = await page.locator('.pagination-arrow.up');
    const downArrow = await page.locator('.pagination-arrow.down');
    
    const upArrowVisible = await upArrow.isVisible();
    const downArrowVisible = await downArrow.isVisible();
    
    console.log(`Up arrow visible: ${upArrowVisible}`);
    console.log(`Down arrow visible: ${downArrowVisible}`);
    
    // Try clicking down arrow if visible
    if (downArrowVisible) {
      await downArrow.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: '/mnt/d/work/kobobo/tmp/series-page-after-scroll.png' });
      console.log('Screenshot after scrolling saved to tmp/series-page-after-scroll.png');
    }
    
    // Test 5: Check letter groups visibility
    const letterGroups = await page.locator('.letter-group').count();
    const visibleLetterGroups = await page.locator('.letter-group:visible').count();
    console.log(`Total letter groups: ${letterGroups}`);
    console.log(`Visible letter groups: ${visibleLetterGroups}`);
    
    // Take a full page screenshot to see all content
    await page.screenshot({ 
      path: '/mnt/d/work/kobobo/tmp/series-page-full.png',
      fullPage: true 
    });
    console.log('Full page screenshot saved to tmp/series-page-full.png');
    
  } catch (error) {
    console.error('Error during testing:', error);
  } finally {
    await browser.close();
  }
}

testKobobo().catch(console.error);