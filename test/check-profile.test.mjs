import assert from "node:assert/strict";
import test from "node:test";
import { validatePortfolio, validateWorkflowText } from "../scripts/check-profile.mjs";

const architecture = () => ({
  state: "PREPARED_FINAL_TOPOLOGY",
  transitionalTargetCount: 18,
  finalEntityCount: 16,
  activeRepositoryCount: 17,
  governanceRepository: ".github",
  governanceCommit: "a".repeat(40),
  activationRequiresHumanApproval: true
});

const project = (index) => ({
  area: `area-${index}`,
  repository: `repo-${index}`,
  url: `https://github.com/vigilanty0x/repo-${index}`,
  canonical: true,
  maturity: "prototype",
  headSha: "a".repeat(40),
  treeSha: "b".repeat(40),
  verification: "PASS",
  evidenceReference: "synthetic exact-SHA verification evidence",
  release: null
});

const portfolio = () => ({
  schemaVersion: 2,
  architecture: architecture(),
  featured: Array.from({ length: 6 }, (_, index) => project(index))
});

test("accepts six canonical entries bound to the prepared 16/17 architecture", () => {
  assert.deepEqual(validatePortfolio(portfolio()), []);
});

test("rejects a stable claim without release and artifact proof", () => {
  const candidate = portfolio();
  candidate.featured[0].maturity = "stable";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "stable-without-release-proof"));
});

test("requires a reason for every blocked verification", () => {
  const candidate = portfolio();
  candidate.featured[0].verification = "BLOCKED";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "blocked-reason"));
});

test("counter-proof: a transitional repository cannot return to the featured six", () => {
  const candidate = portfolio();
  candidate.featured[0].repository = "agent-dashboard";
  candidate.featured[0].url = "https://github.com/vigilanty0x/agent-dashboard";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "transitional-featured-identity"));
});

test("counter-proof: final entity count drift is rejected", () => {
  const candidate = portfolio();
  candidate.architecture.finalEntityCount = 17;
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "final-entity-count"));
});

test("counter-proof: final activation cannot lose its human gate", () => {
  const candidate = portfolio();
  candidate.architecture.activationRequiresHumanApproval = false;
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "human-activation-gate"));
});

test("counter-proof: mutable runner aliases are rejected", () => {
  const workflow = "permissions:\n  contents: read\njobs:\n  verify:\n    runs-on: ubuntu-latest\n";
  assert.ok(validateWorkflowText(".github/workflows/ci.yml", workflow).some((finding) => finding.rule === "mutable-runner"));
});

test("counter-proof: mutable action references are rejected", () => {
  const workflow = "permissions:\n  contents: read\njobs:\n  verify:\n    runs-on: ubuntu-24.04\n    steps:\n      - uses: actions/checkout@v4\n";
  assert.ok(validateWorkflowText(".github/workflows/ci.yml", workflow).some((finding) => finding.rule === "mutable-action"));
});
