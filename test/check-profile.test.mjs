import assert from "node:assert/strict";
import test from "node:test";
import { validatePortfolio, validateWorkflowText } from "../scripts/check-profile.mjs";

const architecture = () => ({
  state: "PREPARED_CONCRETE_SIX",
  implementationState: "LOCAL_ONLY",
  githubMigrationState: "NOT_APPLIED",
  transitionalTargetCount: 18,
  publicSourceRepositoryCount: 112,
  finalEntityCount: 8,
  productRepositoryCount: 6,
  supportRepositoryCount: 2,
  activeRepositoryCount: 8,
  privateRepositoryCount: 1,
  connectedRepositoryCount: 9,
  governanceRepository: ".github",
  governanceCommit: "a".repeat(40),
  governanceCommitState: "LOCAL_ONLY",
  activationRequiresHumanApproval: true,
  deletionAuthorized: false
});

const expectedFeatured = [
  "automation-control-plane",
  "shipcheck",
  "repo-doctor",
  "promptops",
  "rag-lab",
  "proofgate",
];

const project = (repository, index) => ({
  area: `area-${index}`,
  repository,
  url: `https://github.com/vigilanty0x/${repository}`,
  canonical: true,
  maturity: "prototype",
  headSha: "a".repeat(40),
  treeSha: "b".repeat(40),
  verification: "PASS",
  verificationScope: "REMOTE_MAIN_BASELINE",
  consolidationState: "LOCAL_PREPARATION",
  evidenceReference: "synthetic exact-SHA verification evidence",
  release: null
});

const portfolio = () => ({
  schemaVersion: 2,
  architecture: architecture(),
  featured: expectedFeatured.map((repository, index) => project(repository, index))
});

test("accepts six canonical entries bound to the locally prepared 8-public/9-connected architecture", () => {
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

test("counter-proof: an arbitrary canonical repository cannot replace an umbrella project", () => {
  const candidate = portfolio();
  candidate.featured[0].repository = "apprentice-ai";
  candidate.featured[0].url = "https://github.com/vigilanty0x/apprentice-ai";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "featured-project-set"));
});

test("counter-proof: final entity count drift is rejected", () => {
  const candidate = portfolio();
  candidate.architecture.finalEntityCount = 9;
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "final-entity-count"));
});

test("counter-proof: local preparation cannot claim GitHub migration", () => {
  const candidate = portfolio();
  candidate.architecture.githubMigrationState = "APPLIED";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "github-migration-state"));
});

test("counter-proof: the prepared governance commit cannot masquerade as public main", () => {
  const candidate = portfolio();
  candidate.architecture.governanceCommitState = "PUBLIC_MAIN";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "governance-commit-state"));
});

test("counter-proof: connected target remains eight public plus one private aggregate", () => {
  const candidate = portfolio();
  candidate.architecture.connectedRepositoryCount = 8;
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "connected-repository-count"));
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "connected-repository-arithmetic"));
});

test("counter-proof: deletion is never authorized by profile metadata", () => {
  const candidate = portfolio();
  candidate.architecture.deletionAuthorized = true;
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "deletion-authorization"));
});

test("counter-proof: baseline verification cannot masquerade as completed consolidation", () => {
  const candidate = portfolio();
  candidate.featured[0].consolidationState = "MIGRATED";
  assert.ok(validatePortfolio(candidate).some((finding) => finding.rule === "consolidation-state"));
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
