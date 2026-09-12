import fs from "node:fs/promises";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright";

let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const input = JSON.parse(raw);
const emit = process.stdout.write.bind(process.stdout);
const assertions = [];
const check = async (id, fn) => {
  try {
    await fn();
    assertions.push({ id, passed: true });
  } catch (e) {
    assertions.push({
      id,
      passed: false,
      detail: String(e.message).slice(0, 500),
    });
  }
};
let data;
try {
  if (input.mode === "drizzle") {
    const ts = await import("typescript"),
      orm = await import("drizzle-orm"),
      pg = await import("drizzle-orm/pg-core");
    const directory = await fs.mkdtemp("/tmp/drizzle-grade-");
    await fs.writeFile(directory + "/package.json", '{"type":"module"}');
    await fs.symlink("/opt/eval/node_modules", directory + "/node_modules");
    const source = directory + "/schema.ts";
    await fs.writeFile(source, input.candidate);
    const program = ts.createProgram([source], {
      noEmit: true,
      skipLibCheck: true,
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.NodeNext,
      moduleResolution: ts.ModuleResolutionKind.NodeNext,
    });
    const diagnostics = ts.getPreEmitDiagnostics(program);
    await check("drizzle-types", () =>
      assert.equal(
        diagnostics.length,
        0,
        diagnostics
          .map((d) => ts.flattenDiagnosticMessageText(d.messageText, " "))
          .join("\n"),
      ),
    );
    if (!diagnostics.length) {
      const js = ts.transpileModule(input.candidate, {
        compilerOptions: {
          target: ts.ScriptTarget.ES2022,
          module: ts.ModuleKind.ESNext,
        },
      }).outputText;
      await fs.writeFile(directory + "/schema.mjs", js);
      const answer = await import(pathToFileURL(directory + "/schema.mjs"));
      const table = (t) => {
        const config = pg.getTableConfig(t);
        return {
          name: config.name,
          columns: Object.fromEntries(
            config.columns.map((c) => [
              c.name,
              { type: c.getSQLType(), notNull: c.notNull, primary: c.primary },
            ]),
          ),
          indexes: config.indexes.map((i) =>
            i.config.columns.map((c) => c.name),
          ),
          foreignKeys: config.foreignKeys.map((k) => {
            const r = k.reference();
            return {
              columns: r.columns.map((c) => c.name),
              table: orm.getTableName(r.foreignTable),
              references: r.foreignColumns.map((c) => c.name),
              onDelete: k.onDelete,
            };
          }),
        };
      };
      const relation = answer.postsRelations.config(
        orm.createTableRelationsHelpers(answer.posts),
      ).author;
      data = {
        users: table(answer.users),
        posts: table(answer.posts),
        author: {
          table: orm.getTableName(relation.referencedTable),
          fields: relation.config.fields.map((c) => c.name),
          references: relation.config.references.map((c) => c.name),
        },
      };
    }
  } else if (input.mode === "javascript") {
    const directory = await fs.mkdtemp("/tmp/skill-grade-");
    await fs.writeFile(directory + "/answer.mjs", input.candidate);
    let answer;
    await check("module-loads", async () => {
      answer = await import(pathToFileURL(directory + "/answer.mjs"));
    });
    if (answer) {
      await check("required-exports", () => {
        for (const name of input.exports || [])
          assert.notEqual(answer[name], undefined, `Missing export ${name}`);
      });
      if (assertions.at(-1).passed) {
        const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor;
        let test;
        try {
          test = new AsyncFunction("answer", "assert", "check", input.test);
        } catch (error) {
          error.infrastructure = true;
          throw error;
        }
        await test(answer, assert, check);
      }
    }
  } else if (input.mode === "starlark") {
    const syntax = spawnSync(
      "buildifier",
      ["-type=" + (input.file_type || "build"), "-mode=fix"],
      {
        input: input.candidate,
        encoding: "utf8",
        timeout: 5000,
        maxBuffer: 1024 * 1024,
      },
    );
    await check("starlark-syntax", () =>
      assert.equal(syntax.status, 0, syntax.stderr),
    );
    if (syntax.status === 0) {
      const parsed = spawnSync("python3", ["/opt/eval/starlark.py"], {
        input: input.candidate,
        encoding: "utf8",
        timeout: 5000,
        maxBuffer: 1024 * 1024,
      });
      if (parsed.status !== 0)
        throw new Error("Unsupported declaration syntax: " + parsed.stderr);
      data = JSON.parse(parsed.stdout);
    }
  } else if (input.mode === "css" || input.mode === "mermaid") {
    const browser = await chromium
      .launch({
        headless: true,
        args: ["--no-sandbox", "--disable-dev-shm-usage"],
      })
      .catch((error) => {
        error.infrastructure = true;
        throw error;
      });
    try {
      if (input.mode === "css") {
        for (const state of input.states) {
          const page = await browser.newPage({
            viewport: state.viewport || { width: 800, height: 600 },
          });
          await page.route("**/*", (r) => r.abort());
          await page.emulateMedia(state.media || {});
          await page.setContent(input.html);
          if (state.dir)
            await page
              .locator("html")
              .evaluate(
                (element, dir) => element.setAttribute("dir", dir),
                state.dir,
              );
          for (const change of state.attributes || [])
            await page
              .locator(change.selector)
              .evaluate(
                (element, change) =>
                  element.setAttribute(change.name, change.value),
                change,
              );
          await page.addStyleTag({ content: input.candidate });
          if (state.focus) await page.locator(state.focus).focus();
          if (state.tab) await page.keyboard.press("Tab");
          if (state.hover) await page.locator(state.hover).hover();
          for (const rule of state.checks)
            await check(state.id + "/" + rule.id, async () => {
              const measured = await page.evaluate((r) => {
                const element = document.querySelector(r.selector || "body");
                if (!element) throw Error("Missing selector");
                if (r.kind === "style")
                  return getComputedStyle(element)
                    .getPropertyValue(r.property)
                    .trim();
                if (r.kind === "visible") {
                  const s = getComputedStyle(element),
                    rect = element.getBoundingClientRect();
                  return (
                    rect.width > 0 &&
                    rect.height > 0 &&
                    s.visibility !== "hidden" &&
                    Number(s.opacity) > 0
                  );
                }
                if (r.kind === "important") {
                  const walk = (rules) =>
                    [...rules].some(
                      (rule) =>
                        (rule.style &&
                          [...rule.style].some(
                            (p) =>
                              rule.style.getPropertyPriority(p) === "important",
                          )) ||
                        (rule.cssRules && walk(rule.cssRules)),
                    );
                  return [...document.styleSheets].some((sheet) =>
                    walk(sheet.cssRules),
                  );
                }
                if (r.kind === "overflow")
                  return document.documentElement.scrollWidth <= innerWidth;
                const a = element.getBoundingClientRect();
                if (r.kind === "rect") return a[r.property];
                const other = document.querySelector(r.other);
                if (!other) throw Error("Missing second selector");
                const b = other.getBoundingClientRect();
                if (r.kind === "same-row") return Math.abs(a.y - b.y) < 1;
                if (r.kind === "same-column") return Math.abs(a.x - b.x) < 1;
                if (r.kind === "gap-x") return b.left - a.right;
                if (r.kind === "gap-y") return b.top - a.bottom;
                if (r.kind === "before") return a.x < b.x;
                throw Error("Unknown CSS measurement");
              }, rule);
              if (typeof rule.value === "number")
                assert.ok(
                  Math.abs(measured - rule.value) < (rule.tolerance ?? 1),
                  `${measured} != ${rule.value}`,
                );
              else assert.deepEqual(measured, rule.value);
            });
          await page.close();
        }
      } else {
        const page = await browser.newPage();
        await page.route("**/*", (r) => r.abort());
        await page.setContent("<html><body></body></html>");
        await page.addScriptTag({
          path: "/opt/eval/node_modules/mermaid/dist/mermaid.min.js",
        });
        data = await page.evaluate(async (source) => {
          mermaid.initialize({
            startOnLoad: false,
            securityLevel: "strict",
            suppressErrorRendering: true,
          });
          const diagram = await mermaid.mermaidAPI.getDiagramFromText(source);
          const rendered = await mermaid.render("evaluationDiagram", source);
          document.body.innerHTML = rendered.svg;
          const convert = (x) =>
            JSON.parse(
              JSON.stringify(x, (_, v) =>
                v instanceof Map
                  ? Object.fromEntries(v)
                  : v instanceof Set
                    ? [...v]
                    : v,
              ),
            );
          const methods = [
            "getVertices",
            "getEdges",
            "getActors",
            "getMessages",
            "getEntities",
            "getRelationships",
            "getRootDocV2",
            "getStates",
            "getRelations",
            "getClasses",
            "getTasks",
          ];
          const db = {};
          for (const name of methods)
            if (typeof diagram.db[name] === "function") {
              try {
                db[name] = convert(diagram.db[name]());
              } catch {}
            }
          let edges = [];
          const vertices = db.getVertices || {},
            actors = db.getActors || {},
            entities = db.getEntities || {};
          const label = (id) =>
            vertices[id]?.text || actors[id]?.description || id;
          if (db.getEdges)
            edges = db.getEdges.map((e) => ({
              from: label(e.start),
              to: label(e.end),
              label: e.text || "",
              directed: e.type !== "arrow_open",
            }));
          else if (db.getMessages)
            edges = db.getMessages
              .filter((e) => e.from && e.to)
              .map((e) => ({
                from: label(e.from),
                to: label(e.to),
                label: e.message || "",
                style: e.type,
              }));
          else if (db.getRelationships) {
            const names = Object.fromEntries(
              Object.entries(entities).map(([name, e]) => [e.id, name]),
            );
            edges = db.getRelationships.map((e) => ({
              from: names[e.entityA],
              to: names[e.entityB],
              label: e.roleA,
              from_cardinality: e.relSpec.cardB,
              to_cardinality: e.relSpec.cardA,
            }));
          } else if (db.getRelations) {
            const name = (id) =>
              id === "root_start" || id === "root_end" ? "[*]" : id;
            edges = db.getRelations.map((e) => ({
              from: name(e.id1),
              to: name(e.id2),
              label: e.relationTitle || "",
              relation: e.relation,
            }));
          }
          const columns = Object.fromEntries(
            Object.entries(entities).map(([name, e]) => [
              name,
              Object.fromEntries(e.attributes.map((a) => [a.name, a])),
            ]),
          );
          const controls = (db.getMessages || [])
            .filter((e) => !e.from && !e.to)
            .map((e) => e.message)
            .filter(Boolean);
          const relationships = edges
            .filter((e) => e.from_cardinality)
            .map((e) => ({
              members: {
                [e.from]: e.from_cardinality,
                [e.to]: e.to_cardinality,
              },
            }));
          const messages = edges.map(({ from, to, label }) => ({
            from,
            to,
            label,
          }));
          const stateName = (id) =>
            id === "root_start" || id === "root_end" ? "[*]" : id;
          const nodes = [
            ...new Set(
              Object.keys(vertices).length
                ? Object.keys(vertices).map(label)
                : Object.keys(actors).length
                  ? Object.keys(actors).map(label)
                  : Object.keys(entities).length
                    ? Object.keys(entities)
                    : Object.keys(db.getStates || db.getClasses || {}).map(
                        stateName,
                      ),
            ),
          ];
          const inheritance = (db.getRelations || []).flatMap((r) =>
            r.relation?.type1 === 1
              ? [{ from: r.id2, to: r.id1 }]
              : r.relation?.type2 === 1
                ? [{ from: r.id1, to: r.id2 }]
                : [],
          );
          const tasks = Object.fromEntries(
            (db.getTasks || []).map((t) => [
              t.id,
              {
                label: t.task.trim(),
                start: t.startTime,
                end: t.endTime,
                depends_on: t.raw?.startTime?.startData,
              },
            ]),
          );
          return {
            type: diagram.type,
            labels: [
              ...document.querySelectorAll(
                "svg text, svg .nodeLabel, svg .edgeLabel",
              ),
            ]
              .map((n) => n.textContent.trim())
              .filter(Boolean),
            edges,
            columns,
            controls,
            relationships,
            messages,
            nodes,
            inheritance,
            tasks,
            db,
            svg: rendered.svg,
          };
        }, input.candidate);
        await check("diagram-renders", () =>
          assert.ok(data.svg.includes("<svg")),
        );
      }
    } finally {
      await browser.close();
    }
  } else throw Error("Unknown runtime mode");
  emit(input.nonce + JSON.stringify({ assertions, data }) + "\n");
} catch (error) {
  if (error.infrastructure) {
    emit(
      input.nonce +
        JSON.stringify({
          status: "blocked",
          detail:
            "Browser runtime unavailable; rebuild with python3 -m evals.prepare",
        }) +
        "\n",
    );
    process.exit(1);
  }
  emit(
    input.nonce +
      JSON.stringify({
        assertions,
        error: String(error.message).slice(0, 1000),
      }) +
      "\n",
  );
  process.exitCode = 1;
}
