#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { basename } from "node:path";

const ADAPTIVE_CONTENT_TYPE = "application/vnd.microsoft.card.adaptive";
const VALID_TARGETS = new Set(["auto", "card", "bot", "webhook", "graph"]);

const issues = [];

function usage(exitCode = 0) {
  const out = exitCode === 0 ? console.log : console.error;
  out(`Usage: node check-teams-card.mjs [--target auto|card|bot|webhook|graph] payload.json

Targets:
  card     Raw Adaptive Card JSON
  bot      Bot Framework/Teams SDK activity or attachment
  webhook  Workflows webhook message wrapper (same shape as retired Incoming Webhooks)
  graph    Microsoft Graph chatMessage payload
  auto     Infer target from payload shape

Exit codes: 0 = no errors (warnings allowed), 1 = errors or invalid JSON, 2 = usage error.
`);
  process.exit(exitCode);
}

function add(severity, path, message) {
  issues.push({ severity, path, message });
}

function error(path, message) {
  add("ERROR", path, message);
}

function warn(path, message) {
  add("WARN", path, message);
}

function info(path, message) {
  add("INFO", path, message);
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function parseArgs(argv) {
  let target = "auto";
  let file = null;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") usage(0);
    if (arg === "--target") {
      target = argv[i + 1];
      i += 1;
      continue;
    }
    if (arg.startsWith("--target=")) {
      target = arg.slice("--target=".length);
      continue;
    }
    if (arg.startsWith("-")) usage(2);
    file = arg;
  }

  if (!VALID_TARGETS.has(target)) {
    console.error(`Invalid target: ${target}`);
    usage(2);
  }
  if (!file) usage(2);

  return { target, file };
}

function readJson(file) {
  const text = readFileSync(file, "utf8");
  try {
    return JSON.parse(text);
  } catch (err) {
    console.error(`Invalid JSON in ${file}: ${err.message}`);
    process.exit(1);
  }
}

function parseVersion(version) {
  if (typeof version !== "string") return null;
  const match = version.match(/^(\d+)\.(\d+)$/);
  if (!match) return null;
  return { major: Number(match[1]), minor: Number(match[2]), raw: version };
}

function compareVersion(a, b) {
  const pa = parseVersion(a);
  const pb = parseVersion(b);
  if (!pa || !pb) return 0;
  if (pa.major !== pb.major) return pa.major - pb.major;
  return pa.minor - pb.minor;
}

function versionLt(version, minimum) {
  return compareVersion(version, minimum) < 0;
}

function versionGt(version, maximum) {
  return compareVersion(version, maximum) > 0;
}

function inferTarget(payload) {
  if (isObject(payload) && payload.type === "AdaptiveCard") return "card";
  if (isObject(payload) && isObject(payload.body) && Array.isArray(payload.attachments)) return "graph";
  if (isObject(payload) && payload.type === "message" && Array.isArray(payload.attachments)) return "webhook";
  if (isObject(payload) && payload.contentType === ADAPTIVE_CONTENT_TYPE) return "bot";
  return "card";
}

function parseCardContent(content, path, graphMode = false) {
  if (typeof content === "string") {
    try {
      const parsed = JSON.parse(content);
      if (!isObject(parsed)) {
        error(path, "Stringified card content must parse to a JSON object.");
        return null;
      }
      return parsed;
    } catch (err) {
      error(path, `Card content is not valid JSON: ${err.message}`);
      return null;
    }
  }
  if (isObject(content)) {
    if (graphMode) {
      warn(path, "Graph adaptive card attachment content is commonly expected as stringified JSON; verify your SDK/API path accepts an object.");
    }
    return content;
  }
  error(path, "Adaptive Card attachment content must be an object or stringified JSON object.");
  return null;
}

function cardsFromAttachment(attachment, path, graphMode = false) {
  if (!isObject(attachment)) {
    error(path, "Attachment must be an object.");
    return [];
  }
  if (attachment.contentType !== ADAPTIVE_CONTENT_TYPE) {
    return [];
  }
  const card = parseCardContent(attachment.content, `${path}.content`, graphMode);
  return card ? [{ card, path: `${path}.content` }] : [];
}

function collectCards(payload, target) {
  const cards = [];

  if (target === "card") {
    cards.push({ card: payload, path: "$" });
    return cards;
  }

  if (target === "bot") {
    if (payload?.contentType === ADAPTIVE_CONTENT_TYPE) {
      cards.push(...cardsFromAttachment(payload, "$"));
      return cards;
    }
    if (!Array.isArray(payload?.attachments)) {
      error("$", "Bot target expects an activity with attachments[] or an Adaptive Card attachment.");
      return cards;
    }
    payload.attachments.forEach((attachment, index) => {
      cards.push(...cardsFromAttachment(attachment, `$.attachments[${index}]`));
    });
    if (cards.length === 0) error("$.attachments", "No Adaptive Card attachments found.");
    return cards;
  }

  if (target === "webhook") {
    if (payload?.type !== "message") {
      error("$.type", 'Webhook/Workflows payload must have top-level type "message".');
    }
    if (!Array.isArray(payload?.attachments)) {
      error("$.attachments", "Webhook/Workflows payload must include attachments[].");
      return cards;
    }
    payload.attachments.forEach((attachment, index) => {
      cards.push(...cardsFromAttachment(attachment, `$.attachments[${index}]`));
    });
    if (cards.length === 0) error("$.attachments", "No Adaptive Card attachments found.");
    return cards;
  }

  if (target === "graph") {
    validateGraphWrapper(payload);
    if (!Array.isArray(payload?.attachments)) return cards;
    payload.attachments.forEach((attachment, index) => {
      cards.push(...cardsFromAttachment(attachment, `$.attachments[${index}]`, true));
    });
    return cards;
  }

  return cards;
}

function extractAttachmentIds(html) {
  if (typeof html !== "string") return [];
  const ids = [];
  const pattern = /<attachment\b[^>]*\bid=["']([^"']+)["'][^>]*>(?:<\/attachment>)?/gi;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    ids.push(match[1]);
  }
  return ids;
}

function validateGraphWrapper(payload) {
  if (!isObject(payload)) {
    error("$", "Graph target expects a chatMessage object.");
    return;
  }
  if (!isObject(payload.body)) {
    error("$.body", "Graph chatMessage requires body.");
    return;
  }
  if (payload.body.contentType !== "html" && Array.isArray(payload.attachments) && payload.attachments.length > 0) {
    error("$.body.contentType", 'Graph messages with attachments should use body.contentType "html".');
  }
  const placeholders = extractAttachmentIds(payload.body.content);
  const attachments = Array.isArray(payload.attachments) ? payload.attachments : [];
  const attachmentIds = new Set(attachments.map((a) => a?.id).filter(Boolean));

  if (attachments.length > 0 && placeholders.length === 0) {
    error("$.body.content", 'Graph messages with attachments need an <attachment id="..."></attachment> placeholder.');
  }

  placeholders.forEach((id) => {
    if (!attachmentIds.has(id)) {
      error("$.body.content", `Attachment placeholder id "${id}" has no matching attachments[].id.`);
    }
  });

  attachments.forEach((attachment, index) => {
    if (attachment?.contentType === ADAPTIVE_CONTENT_TYPE && !attachment.id) {
      error(`$.attachments[${index}].id`, "Graph Adaptive Card attachment must have an id matching a body placeholder.");
    }
    if (attachment?.id && !placeholders.includes(attachment.id)) {
      warn(`$.attachments[${index}].id`, `Attachment id "${attachment.id}" is not referenced in body.content.`);
    }
  });
}

function traverse(value, path, visitor) {
  if (Array.isArray(value)) {
    value.forEach((item, index) => traverse(item, `${path}[${index}]`, visitor));
    return;
  }
  if (!isObject(value)) return;
  visitor(value, path);
  for (const [key, child] of Object.entries(value)) {
    if (isObject(child) || Array.isArray(child)) {
      traverse(child, `${path}.${key}`, visitor);
    }
  }
}

function collectMentionTexts(card) {
  const texts = [];
  traverse(card, "$", (node) => {
    if (typeof node.text === "string") texts.push(...extractAtMentions(node.text));
    if (Array.isArray(node.facts)) {
      for (const fact of node.facts) {
        if (typeof fact?.title === "string") texts.push(...extractAtMentions(fact.title));
        if (typeof fact?.value === "string") texts.push(...extractAtMentions(fact.value));
      }
    }
  });
  return [...new Set(texts)];
}

function extractAtMentions(text) {
  const mentions = [];
  const pattern = /<at>.*?<\/at>/g;
  let match;
  while ((match = pattern.exec(text)) !== null) {
    mentions.push(match[0]);
  }
  return mentions;
}

function validateMentionMetadata(card, path, target) {
  const visibleMentions = collectMentionTexts(card);
  const entities = card?.msteams?.entities;

  if (visibleMentions.length === 0) return;

  if (!Array.isArray(entities)) {
    warn(path, "Card contains <at>...</at> mention text but has no root msteams.entities metadata.");
    return;
  }

  const entityTexts = new Set(entities.map((entity) => entity?.text).filter(Boolean));
  visibleMentions.forEach((mentionText) => {
    if (!entityTexts.has(mentionText)) {
      warn(path, `Mention text ${mentionText} has no matching msteams.entities entry.`);
    }
  });

  entities.forEach((entity, index) => {
    if (entity?.type !== "mention") {
      warn(`${path}.msteams.entities[${index}]`, 'Mention entity type should be "mention".');
    }
    if (!visibleMentions.includes(entity?.text)) {
      warn(`${path}.msteams.entities[${index}].text`, "Mention entity text is not present in card text.");
    }
    if (target === "webhook" && entity?.mentioned?.id?.startsWith?.("28:")) {
      warn(`${path}.msteams.entities[${index}].mentioned.id`, "Incoming Webhook Adaptive Cards support user mentions, not bot mentions.");
    }
  });
}

function validateMarkdown(text, path) {
  if (typeof text !== "string") return;
  if (/^#{1,6}\s/m.test(text)) warn(path, "Adaptive Card TextBlock Markdown does not support headings; use TextBlock size/weight/style.");
  if (/!\[[^\]]*]\([^)]+\)/.test(text)) warn(path, "Adaptive Card TextBlock Markdown does not support images; use Image element.");
  if (/```/.test(text)) warn(path, "Adaptive Card TextBlock Markdown does not support code fences; use CodeBlock where supported.");
  if (/^\s*>/m.test(text)) warn(path, "Adaptive Card TextBlock Markdown does not support blockquotes.");
  if (/^\s*\|.*\|\s*$/m.test(text)) warn(path, "Adaptive Card TextBlock Markdown does not support tables; use Table or FactSet.");
  if (/<\/?(strong|b|em|i|a|p|br|ul|ol|li|code|pre|blockquote)\b/i.test(text)) {
    warn(path, "Adaptive Card text does not support HTML; use Markdown or card elements.");
  }
}

function validateCard(card, path, target) {
  if (!isObject(card)) {
    error(path, "Card must be a JSON object.");
    return;
  }
  if (card.type !== "AdaptiveCard") {
    error(`${path}.type`, 'Card type must be "AdaptiveCard".');
  }
  if (!card.$schema) {
    info(`${path}.$schema`, "Add the Adaptive Card schema URL to help tooling validate the card.");
  }
  if (!card.version) {
    error(`${path}.version`, "Card version is required.");
  } else {
    const parsed = parseVersion(card.version);
    if (!parsed) {
      error(`${path}.version`, 'Card version should be a string like "1.2".');
    } else {
      if (versionGt(card.version, "1.5")) {
        error(`${path}.version`, "Teams platform documentation supports Adaptive Card features v1.5 or earlier.");
      }
      if (versionGt(card.version, "1.2")) {
        warn(`${path}.version`, "Versions later than 1.2 can have limited or inconsistent Teams mobile behavior; verify target clients.");
      }
    }
  }

  if (!card.fallbackText) {
    warn(`${path}.fallbackText`, "Add fallbackText with a concise summary for unsupported clients and accessibility.");
  }
  if (!Array.isArray(card.body) && !Array.isArray(card.actions)) {
    error(path, "Card should include body[] and/or actions[].");
  }
  if (card.msteams?.width === "Full") {
    info(`${path}.msteams.width`, "Full-width card still needs narrow/mobile testing.");
  }
  if (card.refresh && target !== "bot") {
    warn(`${path}.refresh`, "Refresh requires Universal Actions bot invoke handling; verify this transport has a bot backend.");
  }
  if (card.authentication && target !== "bot") {
    warn(`${path}.authentication`, "Adaptive Card authentication/SSO requires a supported bot-backed flow.");
  }

  validateMentionMetadata(card, path, target);

  traverse(card, path, (node, nodePath) => {
    validateElement(node, nodePath, card.version, target);
  });
}

function validateElement(node, path, version, target) {
  if (typeof node.type !== "string") return;

  if (node.type === "TextBlock") {
    validateMarkdown(node.text, `${path}.text`);
    if (typeof node.text === "string" && node.text.length > 80 && node.wrap !== true) {
      warn(`${path}.wrap`, "Long TextBlock content should set wrap: true.");
    }
  }

  if (node.type === "FactSet" && Array.isArray(node.facts)) {
    node.facts.forEach((fact, index) => {
      validateMarkdown(fact?.title, `${path}.facts[${index}].title`);
      validateMarkdown(fact?.value, `${path}.facts[${index}].value`);
    });
  }

  if (node.type === "Image" && !node.altText) {
    warn(`${path}.altText`, "Images should include altText.");
  }

  if (node.type === "ColumnSet" && Array.isArray(node.columns)) {
    if (node.columns.length > 3) {
      warn(`${path}.columns`, "ColumnSet with more than three columns is risky in Teams mobile and side panels.");
    }
    node.columns.forEach((column, index) => {
      if (typeof column?.width === "number") {
        warn(`${path}.columns[${index}].width`, "Avoid fixed numeric column widths for Teams; prefer auto/stretch/weighted layout.");
      }
    });
  }

  if (node.type === "Table" && version && versionLt(version, "1.5")) {
    error(path, "Table requires a newer Adaptive Card version; use version 1.5 or replace with FactSet/containers.");
  }

  if (node.type === "CodeBlock") {
    if (version && versionLt(version, "1.5")) {
      error(path, "CodeBlock requires a newer Adaptive Card version; use version 1.5 or link to code/logs.");
    }
    if (!node.language) warn(`${path}.language`, "CodeBlock should include a language such as Json, TypeScript, Python, or PlainText.");
    if (!node.codeSnippet) error(`${path}.codeSnippet`, "CodeBlock requires codeSnippet.");
    info(path, "CodeBlock renders only in Teams web and desktop clients; mobile users need fallbackText or a link.");
  }

  if (node.type?.startsWith("Chart.") || node.type === "Icon" || node.type === "CompoundButton") {
    if (version && versionLt(version, "1.5")) {
      error(path, `${node.type} requires Adaptive Card version 1.5 in Teams.`);
    }
    if (!node.fallback) {
      info(`${path}.fallback`, `${node.type} is capability-gated; consider a fallback element for hosts that cannot render it.`);
    }
  }

  if (node.type?.startsWith("Input.")) {
    if (version && !versionLt(version, "1.3") && !node.label) {
      warn(`${path}.label`, "Inputs in v1.3+ cards should use label for accessibility.");
    }
    if (target === "webhook" || target === "graph") {
      warn(path, "Input elements require a bot-backed submit/execute flow; this transport is usually notification-only.");
    }
  }

  if (node.type === "Action.OpenUrl") {
    if (!node.url) error(`${path}.url`, "Action.OpenUrl requires url.");
    if (typeof node.url === "string" && !/^https:\/\//i.test(node.url) && !/^msteams:/i.test(node.url)) {
      warn(`${path}.url`, "Prefer HTTPS or valid Teams deep links for Action.OpenUrl.");
    }
  }

  if (node.type === "Action.Submit") {
    if (target === "webhook") {
      error(path, "Action.Submit is not supported in webhook cards; use Action.OpenUrl or a bot.");
    } else if (target === "graph") {
      warn(path, "Action.Submit needs a bot/backend invoke path; Graph-sent cards have no bot backend.");
    }
    if (Object.prototype.hasOwnProperty.call(node, "isEnabled")) {
      warn(`${path}.isEnabled`, "Teams does not support isEnabled for Action.Submit.");
    }
  }

  if (node.type === "Action.Execute") {
    if (version && versionLt(version, "1.4")) {
      error(path, "Action.Execute requires Adaptive Card version 1.4 or newer.");
    }
    if (target !== "bot") {
      warn(path, "Action.Execute requires Universal Actions bot invoke handling; verify this transport has a bot backend.");
    }
    if (!node.verb) warn(`${path}.verb`, "Action.Execute should include a verb for backend dispatch.");
  }

  if (node.type === "Action.ToggleVisibility") {
    if (!Array.isArray(node.targetElements) || node.targetElements.length === 0) {
      error(`${path}.targetElements`, "Action.ToggleVisibility requires targetElements.");
    }
  }

  if (node.type === "Action.ShowCard") {
    warn(path, "Action.ShowCard can be awkward in Teams mobile; keep nested cards small and test.");
  }

  if (node.type?.startsWith("Action.") && node.style) {
    warn(`${path}.style`, "Teams does not support positive/destructive Adaptive Card action styling; do not rely on color.");
  }
}

function printResults(file, target) {
  const order = { ERROR: 0, WARN: 1, INFO: 2 };
  issues.sort((a, b) => order[a.severity] - order[b.severity] || a.path.localeCompare(b.path));

  console.log(`Teams Adaptive Card check: ${basename(file)} (target: ${target})`);
  if (issues.length === 0) {
    console.log("OK: no Teams-specific issues found.");
    return 0;
  }

  for (const issue of issues) {
    console.log(`${issue.severity}: ${issue.path}: ${issue.message}`);
  }

  const errors = issues.filter((issue) => issue.severity === "ERROR").length;
  const warnings = issues.filter((issue) => issue.severity === "WARN").length;
  const infos = issues.filter((issue) => issue.severity === "INFO").length;
  console.log(`Summary: ${errors} error(s), ${warnings} warning(s), ${infos} info item(s).`);
  return errors > 0 ? 1 : 0;
}

const { target: requestedTarget, file } = parseArgs(process.argv.slice(2));
const payload = readJson(file);
const target = requestedTarget === "auto" ? inferTarget(payload) : requestedTarget;
const cards = collectCards(payload, target);

cards.forEach(({ card, path }) => validateCard(card, path, target));

process.exit(printResults(file, target));
