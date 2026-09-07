import { chromium } from "playwright";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import path from "node:path";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const url = "file://" + path.join(root, "dist/index.html");
const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROMIUM_PATH
    ? { executablePath: process.env.CHROMIUM_PATH }
    : {}),
  args: ["--no-sandbox"],
});
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
page.setDefaultTimeout(8000);
const errors = [],
  external = [];
page.on("pageerror", (e) => errors.push(e.message));
page.on("request", (r) => {
  if (/^https?:/.test(r.url())) external.push(r.url());
});
try {
  await page.goto(url);
  assert.match(
    await page.locator(".pdf-page").innerText(),
    /No measured vibration/,
  );
  await page.getByRole("button", { name: "Code", exact: true }).click();
  assert.match(
    await page.locator(".editor-body").innerText(),
    /validate_reading/,
  );
  await page.getByRole("button", { name: "Chat", exact: true }).click();
  await page.locator(".composer textarea").fill("A test instruction");
  await page.getByRole("button", { name: "Send simulated message" }).click();
  assert.match(
    await page.locator(".chat-layout").innerText(),
    /not a response generated/,
  );
  await page
    .getByRole("button", { name: "View participants and roles" })
    .click();
  await page.getByRole("button", { name: "Hand off to Aditya" }).click();
  await page.getByRole("button", { name: "Close panel", exact: true }).click();
  assert.equal(await page.locator(".composer textarea").isDisabled(), true);
  await page
    .getByRole("button", { name: "View participants and roles" })
    .click();
  await page.locator("#identity").selectOption("aditya");
  await page.getByRole("button", { name: "Close panel", exact: true }).click();
  assert.equal(await page.locator(".composer textarea").isEnabled(), true);
  await page.goto(url + "?mode=agent");
  await page.getByRole("button", { name: "Run demo workflow" }).click();
  await page.getByText("Waiting for reviewer", { exact: true }).waitFor();
  await page.getByRole("button", { name: "Open review", exact: true }).click();
  assert.equal(
    await page.getByRole("button", { name: "Approve v1" }).isDisabled(),
    true,
  );
  await page.getByRole("button", { name: "Close panel", exact: true }).click();
  await page
    .getByRole("button", { name: "View participants and roles" })
    .click();
  await page.locator("#identity").selectOption("pallavi");
  await page.getByRole("button", { name: "Close panel", exact: true }).click();
  await page.getByRole("button", { name: "Open review", exact: true }).click();
  assert.match(
    await page.locator(".review-preview").innerText(),
    /No measured value/,
  );
  await page.getByRole("button", { name: "Approve v1" }).click();
  await page.getByRole("button", { name: "Close panel", exact: true }).click();
  const d = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download note", exact: true })
    .click();
  assert.equal((await d).suggestedFilename(), "P204-inspection-brief.md");
  await page.goto(url + "?mode=code&panel=review&identity=pallavi");
  await page
    .getByRole("button", { name: "Request changes", exact: true })
    .click();
  assert.equal(await page.locator(".form-error").count(), 1);
  await page
    .locator("#review-reason")
    .fill("Add a test for empty asset names.");
  await page
    .getByRole("button", { name: "Request changes", exact: true })
    .click();
  assert.match(
    await page.locator(".status-chip").innerText(),
    /Changes requested/,
  );
  await page.keyboard.press("Escape");
  assert.equal(await page.locator("dialog").count(), 0);
  for (const mode of ["chat", "documents", "code", "agent"]) {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(url + "?mode=" + mode);
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
      "mobile overflow: " + mode,
    );
  }
  for (const panel of ["people", "sources", "activity", "logs", "outputs"]) {
    await page.goto(url + "?panel=" + panel);
    assert.equal(await page.locator("dialog").isVisible(), true);
    await page.keyboard.press("Escape");
    assert.equal(await page.locator("dialog").count(), 0);
  }
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  console.log(
    "PASS: modes, local input, handoff/read-only states, simulated agent review gate, exact-note view, download, changes validation, drawers/Escape, four mobile layouts, no JS errors, no external requests.",
  );
  console.log(
    "These are UI prototype tests, not backend permission, model or multiplayer tests.",
  );
} finally {
  await browser.close();
}
