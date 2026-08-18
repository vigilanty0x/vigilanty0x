#!/usr/bin/env node

import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const SNAPSHOT_PATH = "data/public-portfolio-live.bound.json";
const MANIFEST_PATH = "data/public-portfolio-live.manifest.json";
const PORTFOLIO_PATH = "PORTFOLIO.json";
const HTML_PATH = "docs/index.html";
const JSON_PATH = "docs/dashboard.json";

function sha256(text) {
  return createHash("sha256").update(text).digest("hex");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function freshnessAt(expiresAt, now = new Date()) {
  const expiry = Date.parse(expiresAt);
  if (!Number.isFinite(expiry)) throw new Error("invalid expiresAt");
  return now.getTime() > expiry ? "STALE" : "CURRENT";
}

export function verifyInputs({ snapshotText, snapshot, manifest, portfolio }) {
  const errors = [];
  if (manifest?.schemaVersion !== 1) errors.push("manifest schemaVersion must be 1");
  if (manifest?.source?.repository !== ".github") errors.push("manifest source repository must be .github");
  if (!/^[0-9a-f]{40}$/.test(manifest?.source?.headSha ?? "")) errors.push("manifest source headSha must be exact");
  if (!Number.isInteger(manifest?.source?.workflowRunId) || manifest.source.workflowRunId <= 0) errors.push("manifest workflowRunId invalid");
  if (!Number.isInteger(manifest?.source?.artifactId) || manifest.source.artifactId <= 0) errors.push("manifest artifactId invalid");
  if (!/^sha256:[0-9a-f]{64}$/.test(manifest?.source?.artifactDigest ?? "")) errors.push("manifest artifactDigest invalid");

  const actualSnapshotSha = sha256(snapshotText);
  if (manifest?.boundedSource?.sha256 !== actualSnapshotSha) errors.push("bounded source sha256 does not match manifest");
  if (manifest?.boundedSource?.generatedAt !== snapshot?.generatedAt) errors.push("bounded source generatedAt does not match manifest");
  if (manifest?.boundedSource?.expiresAt !== snapshot?.registry?.expiresAt) errors.push("bounded source expiresAt does not match manifest");
  if (manifest?.boundedSource?.status !== snapshot?.status) errors.push("bounded source status does not match manifest");

  if (snapshot?.schemaVersion !== 1) errors.push("snapshot schemaVersion must be 1");
  if (snapshot?.mode !== "READ_ONLY") errors.push("snapshot mode must be READ_ONLY");
  if (snapshot?.automaticMutation !== false) errors.push("snapshot automaticMutation must be false");
  if (snapshot?.policy?.autoClose !== false || snapshot?.policy?.autoMerge !== false) errors.push("snapshot mutation policy must remain false");
  if (snapshot?.registry?.owner !== "vigilanty0x") errors.push("snapshot owner mismatch");
  if (snapshot?.upstreamSnapshotSha256 !== manifest?.source?.upstreamSnapshotSha256) errors.push("upstream snapshot sha256 does not match manifest");
  if (snapshot?.summary?.publicRepositoryCount !== manifest?.policy?.expectedPublicRepositoryCount) errors.push("public repository count does not match manifest policy");
  if (snapshot?.summary?.expectedPublicRepositoryCount !== manifest?.policy?.expectedPublicRepositoryCount) errors.push("expected public repository count does not match manifest policy");

  if (portfolio?.schemaVersion !== 2 || portfolio?.owner !== "vigilanty0x") errors.push("portfolio contract mismatch");
  if (portfolio?.architecture?.transitionalTargetCount !== snapshot?.registry?.expectedTargetCount) errors.push("portfolio transitional targets disagree with live registry");
  if (!Array.isArray(portfolio?.featured) || portfolio.featured.length !== 6) errors.push("portfolio must expose six featured canonical projects");

  if (errors.length) throw new Error(errors.join(" | "));
  return { snapshotSha256: actualSnapshotSha };
}

export function buildDashboardModel({ snapshot, manifest, portfolio, snapshotSha256 }) {
  const s = snapshot.summary;
  return {
    schemaVersion: 1,
    source: {
      repository: manifest.source.repository,
      workflowRunId: manifest.source.workflowRunId,
      headSha: manifest.source.headSha,
      artifactId: manifest.source.artifactId,
      artifactDigest: manifest.source.artifactDigest,
      boundedSourceSha256: snapshotSha256,
      upstreamSnapshotSha256: manifest.source.upstreamSnapshotSha256,
      generatedAt: snapshot.generatedAt,
      expiresAt: snapshot.registry.expiresAt,
      mode: snapshot.mode,
    },
    state: {
      status: snapshot.status,
      stopReasons: snapshot.stopReasons,
      freezeActive: snapshot.policy.freezeActive,
      publicRepositories: s.publicRepositoryCount,
      expectedPublicRepositories: s.expectedPublicRepositoryCount,
      openPullRequests: s.openPullRequestCount,
      drafts: s.draftPullRequestCount,
      overSla: s.overSlaCount,
      failingCi: s.failingCiCount,
      pendingCi: s.pendingCiCount,
      mergeConflicts: s.mergeConflictCount,
      activeConsolidations: s.activeConsolidationTargetCount,
      maxOpenPullRequests: snapshot.policy.maxOpenPullRequests,
      maxActiveConsolidations: snapshot.policy.maxActiveConsolidations,
      categoryCounts: s.categoryCounts,
      activeConsolidationTargets: s.activeConsolidationTargets,
    },
    portfolio: {
      finalEntityCount: portfolio.architecture.finalEntityCount,
      activeRepositoryCount: portfolio.architecture.activeRepositoryCount,
      featured: portfolio.featured.map(({ repository, url, maturity, verification }) => ({ repository, url, maturity, verification })),
    },
  };
}

export function renderDashboardJson(model) {
  return `${JSON.stringify(model, null, 2)}\n`;
}

export function renderHtml(model) {
  const state = model.state;
  const source = model.source;
  const statusClass = state.status === "STOPPED" ? "stopped" : "other";
  const metrics = [
    ["Public repos", `${state.publicRepositories}/${state.expectedPublicRepositories}`],
    ["Open PRs", state.openPullRequests],
    ["Drafts", state.drafts],
    ["Over SLA", state.overSla],
    ["Failing CI", state.failingCi],
    ["Pending CI", state.pendingCi],
    ["Merge conflicts", state.mergeConflicts],
    ["Active consolidations", `${state.activeConsolidations}/${state.maxActiveConsolidations}`],
  ];
  const categories = Object.entries(state.categoryCounts)
    .map(([name, value]) => `<li><span>${escapeHtml(name)}</span><strong>${escapeHtml(value)}</strong></li>`)
    .join("\n            ");
  const reasons = state.stopReasons.length
    ? state.stopReasons.map((reason) => `<li><strong>${escapeHtml(reason.code)}</strong><span>${escapeHtml(reason.message)}</span></li>`).join("\n            ")
    : "<li><strong>NONE</strong><span>No stop reason was recorded in this source snapshot.</span></li>";
  const targets = state.activeConsolidationTargets
    .map((target) => `<li>${escapeHtml(target)}</li>`)
    .join("\n            ");
  const featured = model.portfolio.featured
    .map((project) => `<article><h3><a href="${escapeHtml(project.url)}">${escapeHtml(project.repository)}</a></h3><p>${escapeHtml(project.maturity)} · evidence ${escapeHtml(project.verification)}</p></article>`)
    .join("\n          ");
  const metricCards = metrics
    .map(([label, value]) => `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`)
    .join("\n          ");

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Evidence-first live public GitHub portfolio dashboard for vigilanty0x.">
  <title>vigilanty0x — public portfolio evidence</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #071018; color: #f5f8fb; }
    a { color: inherit; }
    main { width: min(76rem, calc(100% - 2rem)); margin: auto; padding: 4rem 0 5rem; }
    .eyebrow { margin: 0 0 1rem; color: #9fb2c3; font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; }
    h1 { max-width: 16ch; margin: 0; font-size: clamp(2.8rem, 7vw, 6rem); line-height: .96; letter-spacing: -.055em; }
    .lede { max-width: 68ch; color: #bdccd6; font-size: 1.12rem; line-height: 1.65; }
    .status { display: inline-flex; align-items: center; gap: .6rem; margin-top: 1.2rem; padding: .55rem .9rem; border: 1px solid #4b5963; border-radius: 999px; font-weight: 800; letter-spacing: .08em; }
    .status.stopped { border-color: #7d5149; background: #201412; }
    .freshness { display: inline-flex; margin-left: .6rem; padding: .55rem .9rem; border: 1px solid #2b4657; border-radius: 999px; color: #c7d5df; }
    .freshness[data-state="STALE"] { border-color: #866940; background: #211b12; color: #f0d7a4; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); gap: .8rem; margin-top: 2rem; }
    .metric { padding: 1rem; border: 1px solid #263c4b; border-radius: .9rem; background: #0b1822; }
    .metric span { display: block; color: #9fb2c3; font-size: .8rem; }
    .metric strong { display: block; margin-top: .25rem; font-size: 1.6rem; letter-spacing: -.03em; }
    section { margin-top: 3.2rem; }
    section h2 { margin-bottom: .7rem; }
    .reason-list, .categories, .targets { list-style: none; padding: 0; margin: 1rem 0 0; }
    .reason-list li { display: grid; grid-template-columns: minmax(12rem, .4fr) 1fr; gap: 1rem; padding: .9rem 0; border-top: 1px solid #233845; }
    .reason-list span { color: #adbdc8; }
    .categories { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: .7rem; }
    .categories li { display: flex; justify-content: space-between; padding: .8rem 1rem; border: 1px solid #263c4b; border-radius: .8rem; background: #0b1822; }
    .targets { display: flex; flex-wrap: wrap; gap: .5rem; }
    .targets li { padding: .45rem .7rem; border: 1px solid #294252; border-radius: 999px; color: #bdccd6; }
    .projects { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: .8rem; }
    article { padding: 1rem; border: 1px solid #263c4b; border-radius: .9rem; background: #0b1822; }
    article h3, article p { margin: 0; }
    article p { margin-top: .5rem; color: #9fb2c3; }
    .source { padding: 1rem; border: 1px solid #263c4b; border-radius: .9rem; background: #09151e; color: #aebfcb; line-height: 1.7; overflow-wrap: anywhere; }
    .warning { color: #f0d7a4; }
    footer { margin-top: 3.5rem; padding-top: 1.4rem; border-top: 1px solid #263c4b; color: #8fa4b3; line-height: 1.6; }
    @media (max-width: 650px) { .reason-list li { grid-template-columns: 1fr; gap: .3rem; } .freshness { margin: .6rem 0 0; } }
  </style>
</head>
<body data-expires-at="${escapeHtml(source.expiresAt)}">
  <!-- generated: scripts/generate-dashboard.mjs -->
  <!-- bounded-source-sha256:${escapeHtml(source.boundedSourceSha256)} upstream-snapshot-sha256:${escapeHtml(source.upstreamSnapshotSha256)} -->
  <!-- source-head:${escapeHtml(source.headSha)} run:${escapeHtml(source.workflowRunId)} artifact:${escapeHtml(source.artifactId)} -->
  <main>
    <p class="eyebrow">vigilanty0x / generated public portfolio evidence</p>
    <h1>Evidence before confidence.</h1>
    <p class="lede">This page is generated from a read-only GitHub portfolio snapshot. The visible program status and metrics are not hand-edited.</p>
    <div class="status ${statusClass}" id="source-status">${escapeHtml(state.status)}</div>
    <div class="freshness" id="freshness" data-state="CURRENT">CURRENT UNTIL ${escapeHtml(source.expiresAt)}</div>

    <div class="metrics">
          ${metricCards}
    </div>

    <section aria-labelledby="stop-reasons">
      <h2 id="stop-reasons">Stop-the-line reasons</h2>
      <ul class="reason-list">
            ${reasons}
      </ul>
    </section>

    <section aria-labelledby="categories">
      <h2 id="categories">Open PR categories</h2>
      <ul class="categories">
            ${categories}
      </ul>
    </section>

    <section aria-labelledby="consolidations">
      <h2 id="consolidations">Active consolidation targets</h2>
      <p class="lede">Policy capacity is ${escapeHtml(state.maxActiveConsolidations)}. The source snapshot records ${escapeHtml(state.activeConsolidations)} active targets.</p>
      <ul class="targets">
            ${targets}
      </ul>
    </section>

    <section aria-labelledby="portfolio">
      <h2 id="portfolio">Prepared final portfolio</h2>
      <p class="lede">${escapeHtml(model.portfolio.finalEntityCount)} final entities / ${escapeHtml(model.portfolio.activeRepositoryCount)} active repositories are prepared. Activation remains human-gated; this live dashboard does not convert that prepared topology into a completed migration.</p>
      <div class="projects">
          ${featured}
      </div>
    </section>

    <section aria-labelledby="source">
      <h2 id="source">Source evidence</h2>
      <div class="source">
        <strong>Mode:</strong> ${escapeHtml(source.mode)}<br>
        <strong>Generated:</strong> ${escapeHtml(source.generatedAt)}<br>
        <strong>Expires:</strong> ${escapeHtml(source.expiresAt)}<br>
        <strong>Source head:</strong> <code>${escapeHtml(source.headSha)}</code><br>
        <strong>Workflow run:</strong> ${escapeHtml(source.workflowRunId)}<br>
        <strong>Artifact:</strong> ${escapeHtml(source.artifactId)} · <code>${escapeHtml(source.artifactDigest)}</code><br>
        <strong>Upstream snapshot SHA-256:</strong> <code>${escapeHtml(source.upstreamSnapshotSha256)}</code><br>
        <strong>Bounded source SHA-256:</strong> <code>${escapeHtml(source.boundedSourceSha256)}</code>
      </div>
      <p class="warning" id="stale-warning" hidden>This evidence is past its registry TTL. Treat the page as historical until a newer verified snapshot is committed.</p>
    </section>

    <footer>Generated from bounded public evidence. No hosted-service SLA, source archive authorization, release authorization, or automatic repository mutation is implied.</footer>
  </main>
  <script>
    (() => {
      const expiresAt = document.body.dataset.expiresAt;
      const stale = Number.isFinite(Date.parse(expiresAt)) && Date.now() > Date.parse(expiresAt);
      if (!stale) return;
      const freshness = document.getElementById("freshness");
      freshness.dataset.state = "STALE";
      freshness.textContent = "STALE — EXPIRED " + expiresAt;
      document.getElementById("stale-warning").hidden = false;
    })();
  </script>
</body>
</html>
`;
}

export async function loadInputs(rootPath = ".") {
  const root = resolve(rootPath);
  const [snapshotText, manifestText, portfolioText] = await Promise.all([
    readFile(resolve(root, SNAPSHOT_PATH), "utf8"),
    readFile(resolve(root, MANIFEST_PATH), "utf8"),
    readFile(resolve(root, PORTFOLIO_PATH), "utf8"),
  ]);
  const snapshot = JSON.parse(snapshotText);
  const manifest = JSON.parse(manifestText);
  const portfolio = JSON.parse(portfolioText);
  const { snapshotSha256 } = verifyInputs({ snapshotText, snapshot, manifest, portfolio });
  return { snapshotText, snapshot, manifest, portfolio, snapshotSha256 };
}

export async function generate(rootPath = ".") {
  const inputs = await loadInputs(rootPath);
  const model = buildDashboardModel(inputs);
  return { model, html: renderHtml(model), json: renderDashboardJson(model) };
}

async function main() {
  const args = process.argv.slice(2);
  const rootFlag = args.indexOf("--root");
  const root = rootFlag >= 0 ? args[rootFlag + 1] : ".";
  const check = args.includes("--check");
  const requireCurrent = args.includes("--require-current");
  const output = await generate(root);
  if (requireCurrent && freshnessAt(output.model.source.expiresAt) !== "CURRENT") {
    throw new Error(`source evidence expired at ${output.model.source.expiresAt}`);
  }
  const htmlPath = resolve(root, HTML_PATH);
  const jsonPath = resolve(root, JSON_PATH);
  if (check) {
    const [existingHtml, existingJson] = await Promise.all([readFile(htmlPath, "utf8"), readFile(jsonPath, "utf8")]);
    const mismatches = [];
    if (existingHtml !== output.html) mismatches.push(HTML_PATH);
    if (existingJson !== output.json) mismatches.push(JSON_PATH);
    if (mismatches.length) throw new Error(`generated dashboard drift: ${mismatches.join(", ")}`);
    process.stdout.write(`PASS: generated dashboard matches source snapshot ${output.model.source.upstreamSnapshotSha256}\n`);
    return;
  }
  await Promise.all([writeFile(htmlPath, output.html, "utf8"), writeFile(jsonPath, output.json, "utf8")]);
  process.stdout.write(`generated ${HTML_PATH} and ${JSON_PATH}\n`);
}

if (process.argv[1]?.endsWith("generate-dashboard.mjs")) {
  main().catch((error) => {
    console.error(`BLOCKED: ${error.message}`);
    process.exitCode = 2;
  });
}
