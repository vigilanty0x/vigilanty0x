#!/usr/bin/env node

import { createHash } from "node:crypto";
import { readdir, readFile, stat } from "node:fs/promises";
import { join, relative, resolve } from "node:path";

const FORBIDDEN_TOKEN_DIGESTS = new Set(["003cc88d6e2eb5d4e5a02df093ee97f3a638d82599ba2f7770aae5a66c951ade"]);
const REQUIRED = ["README.md", "PORTFOLIO.json", "LICENSE", "CONTRIBUTING.md", "SECURITY.md"];
const ALLOWED_MATURITY = new Set(["prototype", "preview", "stable"]);
const ALLOWED_VERIFICATION = new Set(["PASS", "BLOCKED", "FAIL"]);
const SKIP = new Set([".git", "node_modules", "dist", "coverage"]);
const digest = (value) => createHash("sha256").update(value.toUpperCase()).digest("hex");

async function walk(root, directory = root) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (SKIP.has(entry.name)) continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) result.push(...await walk(root, path));
    else if (entry.isFile() && (await stat(path)).size <= 2_000_000) result.push(path);
  }
  return result;
}

export function validatePortfolio(portfolio) {
  const findings = [];
  if (portfolio?.schemaVersion !== 1) findings.push({ rule: "schema-version" });
  if (!Array.isArray(portfolio?.featured) || portfolio.featured.length !== 6) {
    findings.push({ rule: "featured-count" });
    return findings;
  }
  const names = new Set();
  for (const [index, project] of portfolio.featured.entries()) {
    const path = `PORTFOLIO.json#/featured/${index}`;
    if (!/^[a-z0-9][a-z0-9-]+$/.test(project.repository ?? "")) findings.push({ rule: "repository-name", path });
    if (names.has(project.repository)) findings.push({ rule: "duplicate-repository", path });
    names.add(project.repository);
    if (project.url !== `https://github.com/vigilanty0x/${project.repository}`) findings.push({ rule: "repository-url", path });
    if (!ALLOWED_MATURITY.has(project.maturity)) findings.push({ rule: "maturity", path });
    if (!ALLOWED_VERIFICATION.has(project.verification)) findings.push({ rule: "verification", path });
    if (!/^[0-9a-f]{40}$/.test(project.headSha ?? "") || !/^[0-9a-f]{40}$/.test(project.treeSha ?? "")) findings.push({ rule: "git-sha", path });
    if (project.verification === "BLOCKED" && !project.blockedReason) findings.push({ rule: "blocked-reason", path });
    if (project.maturity === "stable" && (!project.release?.tag || !/^[0-9a-f]{64}$/.test(project.release?.artifactSha256 ?? ""))) {
      findings.push({ rule: "stable-without-release-proof", path });
    }
  }
  return findings;
}

export async function check(rootPath) {
  const root = resolve(rootPath);
  const findings = [];
  for (const required of REQUIRED) {
    try { await stat(join(root, required)); } catch { findings.push({ rule: "required-file", path: required }); }
  }
  try {
    findings.push(...validatePortfolio(JSON.parse(await readFile(join(root, "PORTFOLIO.json"), "utf8"))));
  } catch {
    findings.push({ rule: "portfolio-json", path: "PORTFOLIO.json" });
  }
  for (const path of await walk(root)) {
    let content;
    try { content = await readFile(path, "utf8"); } catch { continue; }
    const file = relative(root, path).replaceAll("\\", "/");
    for (const match of content.matchAll(/[A-Za-z0-9_-]{3,}/g)) {
      if (FORBIDDEN_TOKEN_DIGESTS.has(digest(match[0]))) findings.push({ rule: "public-boundary", path: file, line: content.slice(0, match.index).split(/\r?\n/).length });
    }
    if (/^\.github\/workflows\/.*\.ya?ml$/i.test(file)) {
      if (!/^permissions\s*:/m.test(content)) findings.push({ rule: "workflow-permissions", path: file });
      for (const [index, line] of content.split(/\r?\n/).entries()) {
        const use = /^\s*(?:-\s*)?uses:\s*([^\s#]+)/.exec(line)?.[1];
        if (!use || use.startsWith("./") || /\$\{\{/.test(use)) continue;
        const reference = use.slice(use.lastIndexOf("@") + 1);
        if (!/^[0-9a-f]{40}$/i.test(reference)) findings.push({ rule: "mutable-action", path: file, line: index + 1 });
      }
    }
  }
  findings.sort((a, b) => (a.path ?? "").localeCompare(b.path ?? "") || (a.line ?? 0) - (b.line ?? 0) || a.rule.localeCompare(b.rule));
  return { status: findings.length ? "FAIL" : "PASS", findingCount: findings.length, findings, valuesIncluded: false };
}

const rootIndex = process.argv.indexOf("--root");
if (process.argv[1]?.endsWith("check-profile.mjs")) {
  const report = await check(rootIndex >= 0 ? process.argv[rootIndex + 1] : ".");
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
  if (report.status !== "PASS") process.exitCode = 1;
}
