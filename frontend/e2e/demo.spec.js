import { test, expect } from '@playwright/test';

test('CALIBRA E2E Demo Flow', async ({ page }) => {
  // 1. Navigate to the App
  await page.goto('/');
  await expect(page.locator('text=CALIBRA')).toBeVisible();

  // 2. Go to Instrument Profile
  await page.click('text=Instruments');
  await expect(page.locator('h1')).toHaveText('Instrument Profile');

  // 3. Create Profile & Generate Plan
  await page.click('button:has-text("Validate Profile & Generate Test Plan")');

  // 4. Verify we are in the Test Workspace
  await expect(page).toHaveURL(/\/workspace\?sessionId=\d+/);
  await expect(page.locator('h1')).toContainText('Test Workspace');

  // 5. Test PASS Scenario
  await page.fill('input[name="load"]', '10'); // Assuming you add name attributes
  // For the demo we use a simplified selection strategy
  const inputs = await page.locator('.form-input');
  await inputs.nth(0).fill('10');
  await inputs.nth(1).fill('10.008');
  
  await page.click('button:has-text("Validate & Calculate")');
  await expect(page.locator('text=PASS')).toBeVisible();

  // 6. Test Evidence Graph
  await page.click('button:has-text("WHY?")');
  await expect(page.locator('text=Evidence Chain')).toBeVisible();

  // 7. Test FAIL Scenario
  await page.click('button:has-text("Load Failing Demo Data")');
  await page.click('button:has-text("Validate & Calculate")');
  await expect(page.locator('text=FAIL')).toBeVisible();
});
