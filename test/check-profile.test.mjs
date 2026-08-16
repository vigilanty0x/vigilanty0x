import assert from "node:assert/strict";
import test from "node:test";
import { validatePortfolio } from "../scripts/check-profile.mjs";

const project = (index) => ({
  area: `area-${index}`,
  repository: `repo-${index}`,
  url: `https://github.com/vigilanty0x/repo-${index}`,
  maturity: "prototype",
  headSha: "a".repeat(40),
  treeSha: "b".repeat(40),
  verification: "PASS",
  release: null
});

test("accepts exactly six factual prototype entries", () => {
  const findings = validatePortfolio({ schemaVersion: 1, featured: Array.from({ length: 6 }, (_, index) => project(index)) });
  assert.deepEqual(findings, []);
});

test("rejects a stable claim without release and artifact proof", () => {
  const featured = Array.from({ length: 6 }, (_, index) => project(index));
  featured[0].maturity = "stable";
  assert.ok(validatePortfolio({ schemaVersion: 1, featured }).some((finding) => finding.rule === "stable-without-release-proof"));
});

test("requires a reason for every blocked verification", () => {
  const featured = Array.from({ length: 6 }, (_, index) => project(index));
  featured[0].verification = "BLOCKED";
  assert.ok(validatePortfolio({ schemaVersion: 1, featured }).some((finding) => finding.rule === "blocked-reason"));
});

