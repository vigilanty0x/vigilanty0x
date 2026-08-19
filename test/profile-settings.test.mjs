import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const settings = JSON.parse(fs.readFileSync("profile-settings.json", "utf8"));
const workflow = fs.readFileSync(".github/workflows/profile-settings.yml", "utf8");
const script = fs.readFileSync("scripts/apply-profile-settings.py", "utf8");

const expectedPins = [
  "apprentice-ai",
  "repo-doctor",
  "proofgate",
  "ai-assistance-manifest",
  "model-router",
  "local-ai-stack",
];
const transitional = new Set([
  "repo-doctor-ai",
  "safe-merge-gate",
  "shipcheck-release-gate",
  "agent-dashboard",
  "agent-handoff",
  "agent-worktrees",
]);
const topicPattern = /^[a-z0-9](?:[a-z0-9-]{0,48}[a-z0-9])?$/;

test("profile settings contract is bounded to the verified public owner", () => {
  assert.equal(settings.schemaVersion, 1);
  assert.equal(settings.owner, "vigilanty0x");
  assert.equal(settings.issueGate, 4);
  assert.equal(settings.pages.repository, "vigilanty0x");
  assert.equal(settings.pages.buildType, "workflow");
  assert.equal(settings.profile.website, settings.pages.expectedUrl);
  assert.ok(settings.profile.website.startsWith("https://vigilanty0x.github.io/"));
});

test("exact six canonical pins are required and transitional identities are excluded", () => {
  assert.deepEqual(settings.pins, expectedPins);
  assert.equal(settings.pins.length, 6);
  for (const repo of settings.pins) assert.equal(transitional.has(repo), false);
});

test("topic contract is valid, bounded, and includes each pinned repository", () => {
  assert.ok(settings.topics.vigilanty0x);
  assert.ok(settings.topics["portfolio-kit"]);
  for (const repo of expectedPins) assert.ok(settings.topics[repo], `missing topics for ${repo}`);
  for (const [repo, topics] of Object.entries(settings.topics)) {
    assert.ok(topics.length > 0 && topics.length <= 20, `invalid topic count for ${repo}`);
    assert.equal(new Set(topics).size, topics.length, `duplicate topic for ${repo}`);
    for (const topic of topics) assert.match(topic, topicPattern);
  }
});

test("issue-comment trigger is owner-only and bound to the dedicated final-gate issue", () => {
  assert.match(workflow, /issue_comment:/);
  assert.match(workflow, /github\.event\.issue\.number == 4/);
  assert.match(workflow, /github\.event\.comment\.body == '\/apply-profile-settings'/);
  assert.match(workflow, /github\.event\.comment\.user\.login == 'vigilanty0x'/);
  assert.doesNotMatch(workflow, /pull_request_target:/);
});

test("privileged token is scoped only to environment variables on local Python steps", () => {
  const tokenRefs = [...workflow.matchAll(/PROFILE_ADMIN_TOKEN/g)].length;
  assert.equal(tokenRefs, 4);
  const secretLines = workflow.split(/\r?\n/).filter((line) => line.includes("secrets.PROFILE_ADMIN_TOKEN"));
  assert.equal(secretLines.length, 2);
  for (const line of secretLines) {
    assert.match(line, /^\s+PROFILE_ADMIN_TOKEN:\s+\$\{\{ secrets\.PROFILE_ADMIN_TOKEN \}\}$/);
  }
  assert.match(script, /tokenValueIncluded/);
  assert.doesNotMatch(script, /print\(token/);
});

test("applier preserves existing topics and verifier requires the exact pins", () => {
  assert.match(script, /set\(existing\) \| set\(required\)/);
  assert.match(script, /actual_pins != config\["pins"\]/);
  assert.match(script, /has_pages/);
  assert.match(script, /build_type/);
  assert.match(script, /PROFILE_ADMIN_TOKEN is not configured/);
});
