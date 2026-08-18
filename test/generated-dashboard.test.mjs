import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  buildDashboardModel,
  freshnessAt,
  generate,
  renderHtml,
  verifyInputs,
} from "../scripts/generate-dashboard.mjs";

const root = new URL("../", import.meta.url).pathname;

async function baseline() {
  const snapshotText = await readFile(new URL("../data/public-portfolio-live.bound.json", import.meta.url), "utf8");
  const manifest = JSON.parse(await readFile(new URL("../data/public-portfolio-live.manifest.json", import.meta.url), "utf8"));
  const portfolio = JSON.parse(await readFile(new URL("../PORTFOLIO.json", import.meta.url), "utf8"));
  const snapshot = JSON.parse(snapshotText);
  return { snapshotText, snapshot, manifest, portfolio };
}

test("committed dashboard is exactly reproducible from the bound snapshot", async () => {
  const output = await generate(root);
  const committedHtml = await readFile(new URL("../docs/index.html", import.meta.url), "utf8");
  const committedJson = await readFile(new URL("../docs/dashboard.json", import.meta.url), "utf8");
  assert.equal(output.html, committedHtml);
  assert.equal(output.json, committedJson);
});

test("counter-proof: a tampered snapshot is rejected by its hash binding", async () => {
  const input = await baseline();
  const tamperedText = input.snapshotText.replace('"status": "STOPPED"', '"status": "RUNNING"');
  const tamperedSnapshot = JSON.parse(tamperedText);
  assert.throws(
    () => verifyInputs({ ...input, snapshotText: tamperedText, snapshot: tamperedSnapshot }),
    /bounded source sha256 does not match manifest|bounded source status does not match manifest/,
  );
});

test("counter-proof: displayed status comes only from the parsed source snapshot", async () => {
  const input = await baseline();
  const { snapshotSha256 } = verifyInputs(input);
  const model = buildDashboardModel({ ...input, snapshotSha256 });
  const html = renderHtml(model);
  assert.equal(model.state.status, input.snapshot.status);
  assert.match(html, new RegExp(`id="source-status">${input.snapshot.status}<`));
  assert.doesNotMatch(html, /id="source-status">RUNNING</);
});

test("counter-proof: read-write snapshots are rejected", async () => {
  const input = await baseline();
  input.snapshot.mode = "READ_WRITE";
  assert.throws(() => verifyInputs(input), /snapshot mode must be READ_ONLY/);
});

test("counter-proof: automatic mutation cannot be enabled", async () => {
  const input = await baseline();
  input.snapshot.automaticMutation = true;
  assert.throws(() => verifyInputs(input), /automaticMutation must be false/);
});

test("freshness flips to STALE immediately after the registry TTL", () => {
  const expiry = "2026-09-17T23:59:59Z";
  assert.equal(freshnessAt(expiry, new Date("2026-09-17T23:59:59Z")), "CURRENT");
  assert.equal(freshnessAt(expiry, new Date("2026-09-18T00:00:00Z")), "STALE");
});
