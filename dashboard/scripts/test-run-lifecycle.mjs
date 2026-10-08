import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";
import ts from "typescript";

// Exercise the actual page callbacks with browser/fetch doubles, without
// invoking a model or touching a target-product repository.
const page = readFileSync(new URL("../app/page.tsx", import.meta.url), "utf8").replaceAll("\r\n", "\n");
function execute(source, context) {
  const js = ts.transpileModule(source, {
    compilerOptions: { target: ts.ScriptTarget.ES2022 },
  }).outputText;
  return vm.runInNewContext(js, context);
}

test("refresh reconnects after the launcher fragment has been removed", async () => {
  const start = page.indexOf("  useEffect(() => {\n    const params");
  assert.ok(start >= 0);
  const end = page.indexOf("  }, []);", start) + "  }, []);".length;
  const values = new Map();
  let connected;
  const window = {
    location: { hash: "#api_base=http://127.0.0.1:8765&api_token=test-token", pathname: "/", search: "" },
    history: { replaceState: () => { window.location.hash = ""; } },
    sessionStorage: { getItem: key => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, value) },
    setTimeout: callback => { callback(); return 1; },
    clearTimeout: () => {},
  };
  const context = { window, URLSearchParams, JSON,
    useEffect: callback => callback(),
    loadFromApi: (base, token) => { connected = [base, token]; } };
  execute(page.slice(start, end), context);
  assert.equal(window.location.hash, "");
  connected = undefined;
  execute(page.slice(start, end), context);
  assert.deepEqual(connected, ["http://127.0.0.1:8765", "test-token"]);
});

for (const status of ["FAILED", "INTERRUPTED", "READY_FOR_DECISION"]) {
  test(`polling loads final evidence for ${status} and terminates`, async () => {
    const start = page.indexOf("  const waitForRunCompletion =");
    const end = page.indexOf("  const loadFromApi =", start);
    let fetched = 0;
    let loaded = 0;
    const context = {
      apiBase: "http://127.0.0.1:8765", apiToken: "test-token",
      apiHeaders: () => ({}), setActiveRun: () => {}, setNotice: () => {},
      fetch: async () => { fetched++; return { ok: true, json: async () => ({ terminal: true, status, error: "failure evidence" }) }; },
      loadRunFromApi: async () => { loaded++; },
    };
    const promise = execute(page.slice(start, end) + '\nwaitForRunCompletion("run-example");', context);
    if (status === "READY_FOR_DECISION") await promise;
    else await assert.rejects(promise, /failure evidence/);
    assert.equal(fetched, 1);
    assert.equal(loaded, 1);
  });
}
