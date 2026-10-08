"use client";

import {
  ChangeEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  Activity,
  Archive,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Clock3,
  Code2,
  Download,
  FileJson,
  Gauge,
  GitBranch,
  Layers3,
  MemoryStick,
  Play,
  Plus,
  RefreshCcw,
  ShieldAlert,
  Sparkles,
  TestTube2,
  Upload,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";


type Gate =
  | "pending"
  | "approved"
  | "repair"
  | "rejected";

type Imported = Record<string, unknown>;

type WorkspaceTab =
  | "overview"
  | "evidence"
  | "memory";


declare global {
  interface Document {
    modelContext?: {
      registerTool: (
        tool: Record<string, unknown>,
        options?: {
          signal?: AbortSignal;
        },
      ) => void | Promise<void>;
    };
  }
}


const fallbackPhases = [
  ["Plan", "completed"],
  ["Review", "completed"],
  ["Execute", "completed"],
  ["Verify", "completed"],
  ["Gate", "active"],
] as const;

const fallbackChanges = [
  [
    "src/forgelab/api.py",
    "integrated",
    "API locale autenticata",
  ],
  [
    "dashboard/",
    "integrated",
    "Control Plane locale",
  ],
];

const fallbackTests = [
  ["Core", 1, 1],
  ["Governance", 1, 1],
  ["Orchestration", 1, 1],
  ["API / UI", 1, 1],
] as const;

const models = [
  [
    "S0 deterministic",
    "Local tools",
    "0 token",
    "?0",
    100,
  ],
  [
    "S1-S2 economy",
    "Provider alias",
    "non attivo",
    "n/d",
    50,
  ],
  [
    "S3-S4 premium",
    "Provider alias",
    "non attivo",
    "n/d",
    25,
  ],
] as const;

const memory = [
  [
    "DEC-006",
    "Deny-by-default per tool ad alto rischio",
    "Decisione",
  ],
  [
    "PAT-014",
    "Evidence bundle immutabile per ogni run",
    "Pattern",
  ],
  [
    "RSK-009",
    "Promotion richiede approvazione umana",
    "Vincolo",
  ],
] as const;


function asRecord(
  value: unknown,
): Record<string, unknown> | undefined {
  if (
    value &&
    typeof value === "object" &&
    !Array.isArray(value)
  ) {
    return value as Record<string, unknown>;
  }

  return undefined;
}


function downloadJson(
  name: string,
  data: unknown,
) {
  const blob = new Blob(
    [JSON.stringify(data, null, 2)],
    {
      type: "application/json",
    },
  );

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");

  a.href = url;
  a.download = name;
  a.click();

  URL.revokeObjectURL(url);
}


function Metric({
  label,
  value,
  detail,
  tone = "",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: string;
}) {
  return (
    <div className="metric-card">
      <p>{label}</p>
      <strong className={tone}>{value}</strong>
      <span>{detail}</span>
    </div>
  );
}


function Panel({
  title,
  icon,
  eyebrow,
  children,
  className = "",
}: {
  title: string;
  icon: React.ReactNode;
  eyebrow: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-head">
        <div className="panel-icon">{icon}</div>
        <div>
          <p>{eyebrow}</p>
          <h2>{title}</h2>
        </div>
      </header>

      {children}
    </section>
  );
}


export default function Home() {
  const [gate, setGate] =
    useState<Gate>("pending");

  const [activeTab, setActiveTab] =
    useState<WorkspaceTab>("overview");

  const [
    selectedEvidence,
    setSelectedEvidence,
  ] = useState("Changes.patch");

  const [imported, setImported] =
    useState<Record<string, Imported>>({});

  const [notice, setNotice] = useState(
    "M8.2 pronta ? il Control Plane pu? creare run locali.",
  );

  const [newRun, setNewRun] =
    useState(false);

  const [apiSetup, setApiSetup] =
    useState(false);

  const [apiBase, setApiBase] =
    useState(
      "http://127.0.0.1:8765",
    );

  const [apiToken, setApiToken] =
    useState("");

  const [
    apiConnected,
    setApiConnected,
  ] = useState(false);

  const [
    runtimeSha,
    setRuntimeSha,
  ] = useState("unknown");

  const [
    connecting,
    setConnecting,
  ] = useState(false);

  const [
    creatingRun,
    setCreatingRun,
  ] = useState(false);

  const [
    activeRun,
    setActiveRun,
  ] = useState<{
    run_id: string;
    status: string;
    repository: string;
    objective: string;
    editor_engine: string;
  } | null>(null);

  const [
    runFormError,
    setRunFormError,
  ] = useState("");

  const [
    repairDialog,
    setRepairDialog,
  ] = useState(false);

  const [
    repairFeedback,
    setRepairFeedback,
  ] = useState("");

  const [
    repairError,
    setRepairError,
  ] = useState("");

  const [
    repairing,
    setRepairing,
  ] = useState(false);

  const [objective, setObjective] =
    useState(
      "Implementare il prossimo cambiamento con evidenze verificabili",
    );

  const [repository, setRepository] =
    useState("");

  const [targetPath, setTargetPath] =
    useState("");

  const [oldText, setOldText] =
    useState("");

  const [newText, setNewText] =
    useState("");

  const [
    initialNewText,
    setInitialNewText,
  ] = useState("");

  const [testCommand, setTestCommand] =
    useState(
      '["py","-3.11","-m","unittest","discover","-v"]',
    );

  const [risk, setRisk] =
    useState("normal");


  const [aiMode, setAiMode] = useState(false);

  const [
    aiDeveloperMode,
    setAiDeveloperMode,
  ] = useState(false);
  const [
    maxRepairAttempts,
    setMaxRepairAttempts,
  ] = useState(1);

  const fileRef =
    useRef<HTMLInputElement>(null);

  const artifactCount =
    Object.keys(imported).length;

  const summary =
    asRecord(imported["RunSummary.json"]);

  const executionPlan =
    asRecord(imported["ExecutionPlan.json"]);

  const usage =
    asRecord(imported["UsageReport.json"]);

  const evidence =
    asRecord(imported["TestEvidence.json"]);

  const aiPlan =
    asRecord(imported["AIPlan.json"]);

  const aiReview =
    asRecord(imported["AIReview.json"]);

  const reviewReport =
    asRecord(imported["ReviewReport.json"]);

  const prewriteFailure =
    asRecord(
      imported["PrewriteRecoveryFailure.json"],
    );

  const editorFailure =
    asRecord(
      imported["EditorFailure.json"],
    );

  const providerFailure =
    asRecord(
      imported["ProviderFailure.json"],
    );

  const rawUsageRecords =
    usage?.records;

  const usageRecords = (
    Array.isArray(rawUsageRecords)
      ? rawUsageRecords
          .map(
            (item) => asRecord(item)
          )
          .filter(
            (
              record,
            ): record is Record<string, unknown> =>
              Boolean(record),
          )
      : []
  );

  const llmCalls =
    Number(usage?.llm_calls ?? 0);

  const inputTokens =
    usageRecords.reduce(
      (total, record) =>
        total + Number(
          record.input_tokens ?? 0
        ),
      0,
    );

  const outputTokens =
    usageRecords.reduce(
      (total, record) =>
        total + Number(
          record.output_tokens ?? 0
        ),
      0,
    );

  const isAiDeveloper =
    activeRun?.editor_engine === "aider"
    || summary?.change_operation ===
      "ai_generate";

  const isLocalAi =
    usage?.runtime === "hybrid_local_ai"
    && llmCalls > 0;

  const evidenceFiles = [
    ...(imported["RunStatus.json"]
      ? ["RunStatus.json"]
      : []),
    "Changes.patch",
    "ExecutionPlan.json",
    "RunSummary.json",
    "TestEvidence.json",
    "SecurityReport.json",
    "UsageReport.json",
    "ReviewReport.json",
    ...(imported["PrewriteRecoveryFailure.json"]
      ? ["PrewriteRecoveryFailure.json"]
      : []),
    ...(imported["EditorFailure.json"]
      ? ["EditorFailure.json"]
      : []),
    ...(imported["ProviderFailure.json"]
      ? ["ProviderFailure.json"]
      : []),
    ...(isLocalAi
      ? [
          "AIPlan.json",
          ...(imported["AIDeveloperPatch.json"]
            ? ["AIDeveloperPatch.json"]
            : []),
          "AIReview.json",
          ...(imported["AIDiagnostics.json"]
            ? ["AIDiagnostics.json"]
            : []),
        ]
      : []),
  ];

  const selectedEvidenceValue =
    imported[selectedEvidence];

  const selectedEvidenceRecord =
    asRecord(selectedEvidenceValue);

  const selectedEvidenceText =
    selectedEvidence === "Changes.patch"
      ? String(
          selectedEvidenceRecord?.text ??
            "Patch non disponibile.",
        )
      : selectedEvidenceValue
        ? JSON.stringify(
            selectedEvidenceValue,
            null,
            2,
          )
        : "Artefatto non disponibile.";

  const localProvider =
    String(
      aiPlan?.provider
      ?? usageRecords[0]?.provider
      ?? "ollama"
    );

  const localModel =
    String(
      aiPlan?.model
      ?? aiReview?.model
      ?? usageRecords[0]?.model_id
      ?? "qwen2.5-coder:7b"
    );

  const providerSpent =
    String(
      usage?.spent
      ?? usage?.estimated_cost
      ?? "0"
    );

  const runtimeValue =
    isAiDeveloper
      ? "M8.6 Multi-file AI Developer"
      : isLocalAi
        ? "M8.3 Hybrid AI"
        : "M8.2 Deterministic";

  const runtimeDetail =
    isAiDeveloper
      ? "objective -> AI Developer -> tests -> review"
      : isLocalAi
        ? "dashboard -> API -> Ollama GPU"
        : "dashboard -> API -> orchestrator";

  const providerDetail =
    isLocalAi
      ? `${llmCalls} LLM calls - ${inputTokens + outputTokens} token`
      : "LLM disabled";

  const providerCostValue =
    isLocalAi
      ? `EUR ${providerSpent}`
      : String(
          usage?.estimated_cost ?? "0"
        );

  const displayModels =
    isLocalAi
      ? [
          [
            "S0 deterministic",
            "Local tools",
            "test / diff / policy",
            "EUR 0",
            100,
          ],
          [
            "S1-S2 local AI",
            `${localProvider} / ${localModel}`,
            `${llmCalls} calls - ${inputTokens + outputTokens} token`,
            `EUR ${providerSpent}`,
            100,
          ],
          [
            "S3-S4 premium",
            "Not used",
            "0 token",
            "EUR 0",
            20,
          ],
        ]
      : models;

  const security =
    asRecord(imported["SecurityReport.json"]);

  const runId = useMemo(
    () =>
      String(
        activeRun?.run_id ??
          summary?.run_id ??
          summary?.runId ??
          asRecord(imported["RunStatus.json"])?.run_id ??
          "run-m8-2-local",
      ),
    [activeRun, summary, imported],
  );

  const runTitle = String(
    activeRun?.objective ??
      summary?.plan ??
      "ForgeLab Local Control Plane",
  );

  const repositoryLabel = String(
    activeRun?.repository ??
      summary?.repository ??
      "repository locale",
  );

  const runState = String(
    activeRun?.status ??
      asRecord(imported["RunStatus.json"])?.status ??
      summary?.status ??
      "READY",
  );

  const testState = String(
    activeRun
      ? "PENDING"
      : (
          summary?.tests ??
          "?"
        ),
  );

  const repairAttempts =
    Number(
      summary?.repair_attempts ?? 0,
    );

  const planTasks =
    Array.isArray(executionPlan?.tasks)
      ? (
          executionPlan?.tasks as Array<unknown>
        )
          .map(asRecord)
          .filter(
            (
              item,
            ): item is Record<string, unknown> =>
              Boolean(item),
          )
      : [];

  const runChanges =
    Array.isArray(summary?.changes)
      ? (
          summary?.changes as unknown[]
        ).map(String)
      : [];

  const evidenceItems =
    Array.isArray(evidence?.evidence)
      ? (
          evidence?.evidence as Array<unknown>
        )
          .map(asRecord)
          .filter(
            (
              item,
            ): item is Record<string, unknown> =>
              Boolean(item),
          )
      : [];

  const testEvents =
    evidenceItems.filter(
      (item) =>
        item.check_type === "tests",
    );

  const passedTests =
    testEvents.filter(
      (item) =>
        Number(item.exit_status) === 0,
    ).length;

  const failedTestEvent =
    [...testEvents]
      .reverse()
      .find(
        (item) =>
          Number(item.exit_status) !== 0,
      );

  const rawReviewFindings =
    Array.isArray(reviewReport?.findings)
      ? reviewReport.findings
      : [];

  const firstReviewFinding =
    rawReviewFindings[0];

  const firstReviewFindingRecord =
    asRecord(firstReviewFinding);

  const reviewFailureDetail =
    firstReviewFindingRecord
      ? String(
          firstReviewFindingRecord.summary
          ?? firstReviewFindingRecord.message
          ?? firstReviewFindingRecord.finding
          ?? JSON.stringify(
            firstReviewFindingRecord,
          ),
        )
      : firstReviewFinding !== undefined
        ? String(firstReviewFinding)
        : String(
            reviewReport?.summary
            ?? "Reviewer non ha approvato il candidate.",
          );

  const terminalBlock =
    runState === "FAILED" || runState === "INTERRUPTED"
      ? {
          phase: "RUN",
          reason: runState,
          detail: String(asRecord(imported["RunStatus.json"])?.error ?? runState),
          artifact: "RunStatus.json",
        }
      : runState === "CLOSED"
      ? editorFailure
        ? {
            phase: String(
              editorFailure.phase
              ?? "EDITOR",
            ),
            reason: String(
              editorFailure.reason
              ?? "EDITOR_EXECUTION_FAILED",
            ),
            detail: String(
              editorFailure.final_error
              ?? "Reusable editor execution failed.",
            ),
            artifact:
              "EditorFailure.json",
          }
        : prewriteFailure
        ? {
            phase: String(
              prewriteFailure.phase
              ?? "PREWRITE",
            ),
            reason: String(
              prewriteFailure.reason
              ?? "PREWRITE_RECOVERY_EXHAUSTED",
            ),
            detail: String(
              prewriteFailure.final_error
              ?? prewriteFailure.first_error
              ?? "Validazione pre-write esaurita.",
            ),
            artifact:
              "PrewriteRecoveryFailure.json",
          }
        : providerFailure
          ? {
              phase: String(
                providerFailure.phase
                ?? "PROVIDER",
              ),
              reason: String(
                providerFailure.reason
                ?? "PROVIDER_FAILURE",
              ),
              detail: String(
                providerFailure.final_error
                ?? "Provider locale non disponibile.",
              ),
              artifact:
                "ProviderFailure.json",
            }
          : failedTestEvent
            ? {
                phase: "TESTING",
                reason:
                  "DETERMINISTIC_TEST_FAILED",
                detail: String(
                  failedTestEvent.stderr
                  || failedTestEvent.stdout
                  || failedTestEvent.summary
                  || "Test deterministico fallito.",
                ),
                artifact:
                  "TestEvidence.json",
              }
            : String(
                reviewReport?.status
                ?? "",
              ).toUpperCase() === "FAIL"
              ? {
                  phase: "REVIEW",
                  reason:
                    "SEMANTIC_REVIEW_FAILED",
                  detail:
                    reviewFailureDetail,
                  artifact:
                    "ReviewReport.json",
                }
              : {
                  phase: "RUN",
                  reason:
                    "CLOSED_BEFORE_DECISION_READY",
                  detail:
                    "La run si e chiusa senza raggiungere READY_FOR_DECISION.",
                  artifact:
                    "RunSummary.json",
                }
      : undefined;

  const sourceUnchanged =
    security?.source_repository_unchanged;

  const apiHeaders = (
    token = apiToken,
  ) => ({
    Authorization: `Bearer ${token}`,
  });

  const applyArtifacts = (artifacts: Record<string, Imported>) => {
    setImported(artifacts);
    const loadedSummary = asRecord(artifacts["RunSummary.json"]);
    const loadedPlan = asRecord(artifacts["ExecutionPlan.json"]);
    if (typeof loadedSummary?.repository === "string") {
      const loadedRepository = loadedSummary.repository;
      setRepository(current => current || loadedRepository);
    }
    if (Array.isArray(loadedSummary?.changes) && loadedSummary.changes.length) {
      const loadedPath = String(loadedSummary.changes[0]);
      setTargetPath(current => current || loadedPath);
    }
    if (Array.isArray(loadedPlan?.test_command)) {
      setTestCommand(JSON.stringify(loadedPlan.test_command));
    }
    setRunFormError("");
  };


  const loadRunFromApi = async (
    requestedRunId: string,
    base = apiBase,
    token = apiToken,
  ) => {
    const normalized =
      base.replace(/\/$/, "");

    const response = await fetch(
      `${normalized}/v1/runs/${encodeURIComponent(
        requestedRunId,
      )}/artifacts`,
      {
        headers: apiHeaders(token),
      },
    );

    if (!response.ok) {
      throw new Error(
        `Artifacts ${response.status}`,
      );
    }

    const payload =
      await response.json() as {
        artifacts?: Record<
          string,
          Imported
        >;
      };

    setApiBase(normalized);
    setApiToken(token);
    const artifacts =
      payload.artifacts ?? {};

    applyArtifacts(artifacts);
    setActiveRun(null);

    const gateArtifact = asRecord(
      artifacts["GateDecision.json"],
    );
    const gateDecision = String(
      gateArtifact?.decision ?? "PENDING",
    ).toUpperCase();

    setGate(
      gateDecision === "APPROVE"
        ? "approved"
        : gateDecision === "REPAIR"
          ? "repair"
          : gateDecision === "REJECT"
            ? "rejected"
            : "pending",
    );
    setApiConnected(true);

    return artifacts;
  };


  const waitForRunCompletion = async (
    requestedRunId: string,
    base = apiBase,
    token = apiToken,
  ) => {
    const normalized =
      base.replace(/\/$/, "");

    while (true) {
      const response = await fetch(
        `${normalized}/v1/runs/${encodeURIComponent(
          requestedRunId,
        )}/status`,
        {
          headers: apiHeaders(token),
        },
      );

      const payload =
        await response.json() as {
          run_id?: string;
          status?: string;
          terminal?: boolean;
          error?: string;
        };

      if (!response.ok) {
        throw new Error(
          payload.error ??
            `Run status ${response.status}`,
        );
      }

      const status =
        String(
          payload.status ??
            "RUNNING",
        ).toUpperCase();

      setActiveRun(
        (current) =>
          current
            ? {
                ...current,
                status,
              }
            : current,
      );

      setNotice(
        `Run ${requestedRunId} in corso ? ${status}`,
      );

      if (payload.terminal) {
        await loadRunFromApi(
          requestedRunId,
          normalized,
          token,
        );
        if (
          status === "FAILED"
          || status === "INTERRUPTED"
        ) {
          throw new Error(
            payload.error ??
              `Run terminata: ${status}`,
          );
        }

        return payload;
      }

      await new Promise(
        (resolve) =>
          window.setTimeout(
            resolve,
            1000,
          ),
      );
    }
  };


  const loadFromApi = async (
    base = apiBase,
    token = apiToken,
  ) => {
    setConnecting(true);

    try {
      const normalized =
        base.replace(/\/$/, "");

      let discoveredRuntimeSha =
        "unknown";

      try {
        const healthResponse =
          await fetch(
            `${normalized}/health`,
          );

        if (healthResponse.ok) {
          const health =
            await healthResponse.json() as {
              runtime_sha?: string;
            };

          discoveredRuntimeSha =
            String(
              health.runtime_sha
              ?? "unknown",
            );
        }
      } catch {
        discoveredRuntimeSha =
          "unknown";
      }

      setRuntimeSha(
        discoveredRuntimeSha,
      );

      const listResponse =
        await fetch(
          `${normalized}/v1/runs`,
          {
            headers:
              apiHeaders(token),
          },
        );

      if (!listResponse.ok) {
        throw new Error(
          `API ${listResponse.status}`,
        );
      }

      const list =
        await listResponse.json() as {
          runs?: Array<{
            run_id: string;
            status?: string;
            terminal?: boolean;
          }>;
        };

      const latest =
        list.runs?.[0];

      if (!latest?.run_id) {
        throw new Error(
          "Nessuna run disponibile",
        );
      }

      setApiBase(normalized);
      setApiToken(token);
      setApiConnected(true);
      setApiSetup(false);
      setRunFormError("");
      try {
        window.sessionStorage.setItem("forgelab.connection", JSON.stringify({ base: normalized, token }));
      } catch {
        // Storage can be disabled; the current connection still works.
      }

      if (latest.terminal === false) {
        const statusResponse =
          await fetch(
            `${normalized}/v1/runs/${encodeURIComponent(
              latest.run_id,
            )}/status`,
            {
              headers:
                apiHeaders(token),
            },
          );

        const statusPayload =
          await statusResponse.json() as {
            run_id?: string;
            status?: string;
            repository?: string;
            objective?: string;
            editor_engine?: string;
            error?: string;
          };

        if (!statusResponse.ok) {
          throw new Error(
            statusPayload.error ??
              `Run status ${statusResponse.status}`,
          );
        }

        setImported({});
        setGate("pending");
        setActiveRun({
          run_id:
            latest.run_id,
          status:
            String(
              statusPayload.status ??
                latest.status ??
                "RUNNING",
            ).toUpperCase(),
          repository:
            String(
              statusPayload.repository ??
                "repository locale",
            ),
          objective:
            String(
              statusPayload.objective ??
                "Run ForgeLab in corso",
            ),
          editor_engine:
            String(
              statusPayload.editor_engine ??
                "custom",
            ),
        });

        setNotice(
          `Runner locale ${discoveredRuntimeSha.slice(0, 12)} ? ripresa run ${latest.run_id}`,
        );

        void waitForRunCompletion(
          latest.run_id,
          normalized,
          token,
        ).catch(
          (error) => {
            setNotice(
              `Run ${latest.run_id} interrotta: ${
                error instanceof Error
                  ? error.message
                  : "errore sconosciuto"
              }`,
            );
          },
        );

        return;
      }

      await loadRunFromApi(
        latest.run_id,
        normalized,
        token,
      );

      setNotice(
        `Runner locale ${discoveredRuntimeSha.slice(0, 12)} ? ${latest.run_id}`,
      );
    } catch (error) {
      setApiConnected(false);

      setNotice(
        `Collegamento non riuscito: ${
          error instanceof Error
            ? error.message
            : "errore sconosciuto"
        }`,
      );
    } finally {
      setConnecting(false);
    }
  };


  const decide = (
    decision: Gate,
  ) => {
    if (!apiConnected) {
      setGate(decision);
      setNotice(
        "Runner locale non collegato: decisione non eseguita.",
      );
      return;
    }

    setNotice(
      decision === "approved"
        ? "Verifica gate e promotion locale in corso..."
        : "Registrazione decisione in corso...",
    );

    void (async () => {
      try {
        const response = await fetch(
          `${apiBase}/v1/runs/${encodeURIComponent(
            runId,
          )}/decisions`,
          {
            method: "POST",
            headers: {
              ...apiHeaders(),
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              decision:
                decision === "approved"
                  ? "approve"
                  : decision,
              actor: "Product Owner",
            }),
          },
        );

        const payload =
          await response.json() as {
            error?: string;
            decision?: string;
            status?: string;
            promotion_executed?: boolean;
            promotion_branch?: string;
            commit?: string;
          };

        if (!response.ok) {
          throw new Error(
            payload.error ??
              `API ${response.status}`,
          );
        }

        await loadRunFromApi(runId);

        if (payload.promotion_executed) {
          setNotice(
            `Promotion locale completata su ${
              payload.promotion_branch ??
                "branch dedicato"
            } @ ${
              payload.commit?.slice(0, 12) ??
                "commit locale"
            }. Nessun push o merge eseguito.`,
          );
        } else {
          setNotice(
            `Decisione ${
              String(payload.decision ?? "").toLowerCase()
            } registrata. Nessuna promotion eseguita.`,
          );
        }
      } catch (error) {
        setNotice(
          `Decisione/promotion bloccata: ${
            error instanceof Error
              ? error.message
              : "errore sconosciuto"
          }`,
        );
      }
    })();
  };


  const requestRepair = async () => {
    const feedback =
      repairFeedback.trim();

    setRepairError("");

    if (!apiConnected) {
      setRepairError(
        "Runner locale non collegato.",
      );
      setApiSetup(true);
      return;
    }

    if (feedback.length < 8) {
      setRepairError(
        "Descrivi il fix richiesto con almeno 8 caratteri.",
      );
      return;
    }

    setRepairing(true);
    setNotice(
      "Creazione della revisione corretta in corso...",
    );

    try {
      const response = await fetch(
        `${apiBase}/v1/runs/${encodeURIComponent(
          runId,
        )}/repairs`,
        {
          method: "POST",
          headers: {
            ...apiHeaders(),
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            actor: "Product Owner",
            feedback,
          }),
        },
      );

      const payload =
        await response.json() as {
          error?: string;
          run_id?: string;
          parent_run_id?: string;
          decision?: string;
          status?: string;
        };

      if (!response.ok) {
        throw new Error(
          payload.error ??
            `API ${response.status}`,
        );
      }

      const childRunId =
        String(
          payload.run_id ?? "",
        );

      if (!childRunId) {
        throw new Error(
          "La revisione non ha restituito una nuova run.",
        );
      }

      await loadRunFromApi(
        childRunId,
      );

      setRepairDialog(false);
      setRepairFeedback("");
      setRepairError("");
      setActiveTab("overview");

      setNotice(
        `Fix completato in ${childRunId}: ${String(
          payload.status ??
            "stato disponibile",
        )}. La run precedente non e stata promossa.`,
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "errore sconosciuto";

      setRepairError(message);
      setNotice(
        `Fix non completato: ${message}`,
      );
    } finally {
      setRepairing(false);
    }
  };


  const exportDecision = () =>
    downloadJson(
      "GateDecision.json",
      {
        schema_version: "1.0",
        run_id: runId,
        decision: gate,
        decided_at:
          new Date().toISOString(),
        decided_by:
          "product-owner",
        source:
          "forgelab-control-plane",
        promotion_executed: Boolean(
          imported["PromotionResult.json"],
        ),
      },
    );


  const createRun = async () => {
    const failRunForm = (
      message: string,
    ) => {
      setRunFormError(message);
      setNotice(
        `Nuova run bloccata: ${message}`,
      );
    };

    setRunFormError("");

    if (!apiConnected) {
      failRunForm(
        "Runner locale non collegato.",
      );
      setApiSetup(true);
      return;
    }

    if (repository.trim().length === 0) {
      failRunForm(
        "Repository locale mancante.",
      );
      return;
    }

    if (objective.trim().length < 8) {
      failRunForm(
        "Obiettivo troppo breve: usa almeno 8 caratteri.",
      );
      return;
    }

    if (targetPath.trim().length === 0) {
      failRunForm(
        "Indica almeno un file autorizzato.",
      );
      return;
    }

    if (
      !aiDeveloperMode &&
      oldText.length === 0
    ) {
      failRunForm(
        "Modalita non-AI: inserisci il testo esistente da sostituire.",
      );
      return;
    }

    if (testCommand.trim().length === 0) {
      failRunForm(
        "Comando test mancante.",
      );
      return;
    }

    let parsedCommand: unknown;

    try {
      parsedCommand =
        JSON.parse(testCommand);
    } catch {
      failRunForm(
        "Comando test non valido: usa un array JSON di argomenti.",
      );
      return;
    }

    if (
      !Array.isArray(parsedCommand) ||
      parsedCommand.length === 0 ||
      !parsedCommand.every(
        (item) =>
          typeof item === "string" &&
          item.length > 0,
      )
    ) {
      failRunForm(
        "Comando test non valido.",
      );
      return;
    }

    const authorizedPaths =
      targetPath
        .split(/[\r\n,]+/)
        .map((item) => item.trim())
        .filter((item) => item.length > 0);

    if (aiDeveloperMode) {
      if (
        authorizedPaths.length < 1 ||
        authorizedPaths.length > 3
      ) {
        failRunForm(
          "AI Developer richiede da 1 a 3 file autorizzati.",
        );
        return;
      }

      if (
        new Set(authorizedPaths).size !==
        authorizedPaths.length
      ) {
        failRunForm(
          "I file autorizzati devono essere univoci.",
        );
        return;
      }
    } else if (authorizedPaths.length !== 1) {
      failRunForm(
        "La modalita non-AI richiede esattamente un file.",
      );
      return;
    }

    setCreatingRun(true);

    try {
      const body = {
        repository:
          repository.trim(),
        objective:
          objective.trim(),

        change:
          aiDeveloperMode
            ? {
                operation:
                  "ai_generate",
                paths:
                  authorizedPaths,
              }
            : {
                operation:
                  "replace_text",
                path:
                  authorizedPaths[0],
                old:
                  oldText,
                new:
                  newText,
                ...(
                  initialNewText.length > 0
                    ? {
                        initial_new:
                          initialNewText,
                      }
                    : {}
                ),
              },

        test_command:
          parsedCommand,

        timeout_seconds: 60,
        editor_timeout_seconds:
          aiDeveloperMode
            ? 300
            : 60,
        risk,
        ai_mode:
          aiDeveloperMode
            ? true
            : aiMode,
        max_repair_attempts:
          maxRepairAttempts,
        editor_engine:
          aiDeveloperMode
            ? "aider"
            : "custom",
      };

      const response =
        await fetch(
          `${apiBase}/v1/runs`,
          {
            method: "POST",

            headers: {
              ...apiHeaders(),
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify(body),
          },
        );

      const result =
        await response.json() as {
          run_id?: string;
          status?: string;
          error?: string;
        };

      if (!response.ok) {
        throw new Error(
          result.error ??
            `API ${response.status}`,
        );
      }

      if (!result.run_id) {
        throw new Error(
          "API non ha restituito run_id",
        );
      }

      setImported({});
      setGate("pending");
      setActiveRun({
        run_id: result.run_id,
        status: String(
          result.status ??
            "QUEUED",
        ).toUpperCase(),
        repository:
          repository.trim(),
        objective:
          objective.trim(),
        editor_engine:
          aiDeveloperMode
            ? "aider"
            : "custom",
      });

      setRunFormError("");
      setNewRun(false);

      setNotice(
        `Run ${result.run_id} accettata ? monitoraggio in corso`,
      );

      const completed =
        await waitForRunCompletion(
          result.run_id,
        );

      setNotice(
        `Run ${result.run_id} completata ? ${
          completed.status ??
          "stato disponibile"
        }`,
      );

    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "errore sconosciuto";

      setRunFormError(message);
      setNotice(
        `Nuova run fallita: ${message}`,
      );
    } finally {
      setCreatingRun(false);
    }
  };


  const importFiles =
    async (
      event:
        ChangeEvent<HTMLInputElement>,
    ) => {
      const next:
        Record<string, Imported> = {};

      let errors = 0;

      for (
        const file
        of Array.from(
          event.target.files ?? [],
        )
      ) {
        try {
          next[file.name] =
            JSON.parse(
              await file.text(),
            );
        } catch {
          errors++;
        }
      }

      applyArtifacts(next);
      setGate("pending");

      setNotice(
        `${
          Object.keys(next).length
        } artefatti importati localmente${
          errors
            ? `; ${errors} ignorati`
            : ""
        }.`,
      );

      event.target.value = "";
    };


  useEffect(() => {
    const params =
      new URLSearchParams(
        window.location.hash.slice(1),
      );

    let base =
      params.get("api_base");

    let token =
      params.get("api_token");

    if (base && token) {
      try {
        window.sessionStorage.setItem("forgelab.connection", JSON.stringify({ base, token }));
      } catch {
        // Keep credentials out of the URL even when storage is disabled.
      }
      window.history.replaceState(
        null,
        "",
        window.location.pathname +
          window.location.search,
      );

    } else {
      try {
        const saved = JSON.parse(window.sessionStorage.getItem("forgelab.connection") ?? "null");
        if (typeof saved?.base === "string" && typeof saved?.token === "string") {
          base = saved.base;
          token = saved.token;
        }
      } catch {
        // A missing/invalid tab session falls back to manual connection.
      }
    }
    if (base && token) {
      const connectionBase = base;
      const connectionToken = token;
      const timer = window.setTimeout(() => {
        void loadFromApi(connectionBase, connectionToken);
      }, 0);
      return () => window.clearTimeout(timer);
    }
  }, []);


  useEffect(() => {
    const ctx =
      document.modelContext;

    if (!ctx?.registerTool) {
      return;
    }

    const life =
      new AbortController();

    const register =
      async () => {
        await ctx.registerTool(
          {
            name:
              "stage_gate_decision",

            title:
              "Prepara decisione gate",

            description:
              "Aggiorna la decisione visibile senza promotion automatica.",

            inputSchema: {
              type: "object",
              properties: {
                decision: {
                  type: "string",
                  enum: [
                    "approved",
                    "repair",
                    "rejected",
                  ],
                },
              },
              required: [
                "decision",
              ],
              additionalProperties:
                false,
            },

            annotations: {
              readOnlyHint: false,
              untrustedContentHint:
                false,
            },

            execute:
              (input: unknown) => {
                const decision =
                  (
                    input as {
                      decision?: string;
                    }
                  )?.decision;

                if (
                  ![
                    "approved",
                    "repair",
                    "rejected",
                  ].includes(
                    decision ?? "",
                  )
                ) {
                  throw new Error(
                    "Decisione non valida",
                  );
                }

                decide(
                  decision as Gate,
                );

                return {
                  run_id:
                    runId,
                  decision,
                  promotion_executed:
                    false,
                };
              },
          },
          {
            signal:
              life.signal,
          },
        );

        await ctx.registerTool(
          {
            name:
              "prepare_run_request",

            title:
              "Prepara nuova run",

            description:
              "Apre il form per creare una run ForgeLab nel runner locale.",

            inputSchema: {
              type: "object",
              properties: {
                objective: {
                  type: "string",
                  minLength: 8,
                },
              },
              required: [
                "objective",
              ],
              additionalProperties:
                false,
            },

            annotations: {
              readOnlyHint: false,
              untrustedContentHint:
                false,
            },

            execute:
              (input: unknown) => {
                const value =
                  (
                    input as {
                      objective?: string;
                    }
                  )?.objective?.trim();

                if (
                  !value ||
                  value.length < 8
                ) {
                  throw new Error(
                    "Obiettivo troppo breve",
                  );
                }

                setObjective(
                  value,
                );

                setNewRun(true);

                return {
                  staged: true,
                  objective: value,
                };
              },
          },
          {
            signal:
              life.signal,
          },
        );
      };

    void register()
      .catch(() => undefined);

    return () =>
      life.abort();

  }, [runId]);


  const gateClass =
    gate === "approved"
      ? "gate-approved"
      : gate === "repair"
        ? "gate-repair"
        : gate === "rejected"
          ? "gate-rejected"
          : "gate-pending";


  const planRows =
    planTasks.length > 0
      ? planTasks
      : [
          {
            task_id: "01",
            role: "CONTROL",
            objective:
              "Caricare una run ForgeLab",
          },
        ];


  return (
    <main className="min-h-screen bg-[#071019] text-slate-100">

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Code2 size={20} />
          </div>

          <div>
            <strong>ForgeLab</strong>
            <span>Control Plane</span>
          </div>
        </div>

        <div className="top-actions">
          <Badge
            variant="outline"
            className="env-badge"
          >
            <CircleDot />
            Ambiente privato
          </Badge>

          <Button
            variant="outline"
            onClick={() =>
              setApiSetup(true)
            }
            className="dark-button"
          >
            {
              apiConnected
                ? <Wifi />
                : <WifiOff />
            }

            {
              apiConnected
                ? "Runner collegato"
                : "Collega runner"
            }
          </Button>

          <input
            ref={fileRef}
            type="file"
            accept="application/json,.json"
            multiple
            className="hidden"
            onChange={importFiles}
          />

          <Button
            variant="outline"
            onClick={() =>
              fileRef.current?.click()
            }
            className="dark-button"
          >
            <Upload />
            Importa artefatti
          </Button>

          <Button
            onClick={() =>
              setNewRun(true)
            }
            className="primary-button"
          >
            <Plus />
            Nuova run
          </Button>
        </div>
      </header>


      <div className="shell">
        <aside className="sidebar">

          <nav
            aria-label="Navigazione principale"
          >
            <a
              className={
                `nav-item ${activeTab === "overview"
                  ? "active"
                  : ""}`
              }
              href="#overview"
              onClick={(event) => {
                event.preventDefault();
                setActiveTab("overview");
              }}
            >
              <Gauge />
              Panoramica
            </a>

            <a
              className={
                `nav-item ${activeTab === "evidence"
                  ? "active"
                  : ""}`
              }
              href="#evidence"
              onClick={(event) => {
                event.preventDefault();
                setActiveTab("evidence");
              }}
            >
              <Archive />
              Evidenze
            </a>

            <a
              className={
                `nav-item ${activeTab === "memory"
                  ? "active"
                  : ""}`
              }
              href="#memory"
              onClick={(event) => {
                event.preventDefault();
                setActiveTab("memory");
              }}
            >
              <MemoryStick />
              Project Memory
            </a>
          </nav>

          <div className="side-run">
            <p>RUN ATTIVA</p>
            <strong>{runId}</strong>

            <span>
              <i />
              {runState}
            </span>
          </div>

          <div className="side-foot">
            <ShieldAlert />

            <p>
              API locale loopback-only.
              Nessuna promotion automatica.
            </p>
          </div>
        </aside>


        <div className="content">

          <div
            className="status-strip"
            role="status"
          >
            <Sparkles />
            <span>{notice}</span>

            {
              artifactCount > 0 &&
              <Badge className="file-badge">
                {artifactCount} file
              </Badge>
            }
          </div>


          <section
            className="run-head"
            id="overview"
          >
            <div>
              <p className="kicker">
                {isAiDeveloper
                  ? "RUN CONTROL - MILESTONE 8.6"
                  : isLocalAi
                    ? "RUN CONTROL - MILESTONE 8.3"
                    : "RUN CONTROL - MILESTONE 8.2"}
              </p>

              <h1>{runTitle}</h1>

              <div className="run-meta">
                <span>
                  <GitBranch />
                  {repositoryLabel}
                </span>

                <span>
                  <Clock3 />
                  locale
                </span>

                <span>
                  <Activity />
                  {runState}
                </span>

                <span>
                  <Code2 />
                  runner {
                    runtimeSha === "unknown"
                      ? "SHA n/d"
                      : runtimeSha.slice(0, 12)
                  }
                </span>
              </div>
            </div>

            <div
              className={
                `gate-chip ${gateClass}`
              }
            >
              <span>GATE</span>

              <strong>
                {
                  gate === "pending"
                    ? "Decisione richiesta"
                    : gate === "approved"
                      ? "Approvata"
                      : gate === "repair"
                        ? "Riparazione"
                        : "Rifiutata"
                }
              </strong>
            </div>
          </section>


          <div className="phase-track">
            {
              fallbackPhases.map(
                (
                  [name, state],
                  index,
                ) => (
                  <div
                    key={name}
                    className={
                      `phase ${state}`
                    }
                  >
                    <span>
                      {
                        state === "completed"
                          ? <Check />
                          : index + 1
                      }
                    </span>

                    <p>{name}</p>

                    {
                      index < 4 &&
                      <i />
                    }
                  </div>
                ),
              )
            }
          </div>


          <div className="metrics">

            <Metric
              label="Test"
              value={testState}
              detail={
                testEvents.length > 0
                  ? `${passedTests}/${testEvents.length} tentativi PASS`
                  : "evidenza della run"
              }
              tone={
                testState === "PASS"
                  ? "good"
                  : ""
              }
            />

            <Metric
              label="Repair"
              value={
                String(
                  repairAttempts,
                )
              }
              detail="tentativi eseguiti"
            />

            <Metric
              label="Runtime"
              value={runtimeValue}
              detail={runtimeDetail}
            />

            <Metric
              label="Costo provider"
              value={providerCostValue}
              detail={providerDetail}
              tone="good"
            />
          </div>


          {
            terminalBlock &&
            <section
              className="terminal-blocker"
              role="alert"
            >
              <div className="terminal-blocker-head">
                <ShieldAlert />

                <div>
                  <p>BLOCCO CORRENTE</p>
                  <strong>
                    {terminalBlock.reason}
                  </strong>
                </div>

                <span>
                  {terminalBlock.phase}
                </span>
              </div>

              <p className="terminal-blocker-detail">
                {terminalBlock.detail}
              </p>

              <button
                type="button"
                className="terminal-blocker-link"
                onClick={() => {
                  setSelectedEvidence(
                    terminalBlock.artifact,
                  );
                  setActiveTab("evidence");
                }}
              >
                Apri evidenza: {
                  terminalBlock.artifact
                }
              </button>
            </section>
          }


          <Tabs
            value={activeTab}
            onValueChange={(value) =>
              setActiveTab(
                value as WorkspaceTab,
              )
            }
            className="workspace-tabs"
          >
            <TabsList className="tabs-list">

              <TabsTrigger value="overview">
                Panoramica
              </TabsTrigger>

              <TabsTrigger value="evidence">
                Evidenze
              </TabsTrigger>

              <TabsTrigger value="memory">
                Project Memory
              </TabsTrigger>

            </TabsList>


            <TabsContent
              value="overview"
              className="panel-grid"
            >

              <Panel
                title="Piano di esecuzione"
                eyebrow="PLAN"
                icon={<Layers3 />}
              >
                <ol className="plan-list">
                  {
                    planRows.map(
                      (
                        task,
                        index,
                      ) => (
                        <li
                          key={
                            String(
                              task.task_id ??
                              index,
                            )
                          }
                        >
                          <span>
                            {
                              String(
                                index + 1,
                              ).padStart(
                                2,
                                "0",
                              )
                            }
                          </span>

                          <div>
                            <strong>
                              {
                                String(
                                  task.role ??
                                  task.task_id ??
                                  "TASK",
                                )
                              }
                            </strong>

                            <p>
                              {
                                String(
                                  task.objective ??
                                  "Task ForgeLab",
                                )
                              }
                            </p>
                          </div>

                          <CheckCircle2 />
                        </li>
                      ),
                    )
                  }
                </ol>
              </Panel>


              <Panel
                title="Modifiche prodotte"
                eyebrow="CHANGES"
                icon={<GitBranch />}
              >
                <div className="change-list">
                  {
                    runChanges.length > 0
                      ? runChanges.map(
                          (path) => (
                            <div key={path}>
                              <FileJson />

                              <div>
                                <strong>
                                  {path}
                                </strong>

                                <p>
                                  Patch isolata
                                </p>
                              </div>

                              <span>
                                changed
                              </span>
                            </div>
                          ),
                        )
                      : artifactCount > 0
                        ? (
                            <div>
                              <FileJson />

                              <div>
                                <strong>
                                  Nessuna modifica applicata
                                </strong>

                                <p>
                                  La run si e fermata prima di produrre
                                  un change-set governato.
                                </p>
                              </div>

                              <span>
                                none
                              </span>
                            </div>
                          )
                        : fallbackChanges.map(
                          (change) => (
                            <div
                              key={
                                change[0]
                              }
                            >
                              <FileJson />

                              <div>
                                <strong>
                                  {
                                    change[0]
                                  }
                                </strong>

                                <p>
                                  {
                                    change[2]
                                  }
                                </p>
                              </div>

                              <span>
                                {
                                  change[1]
                                }
                              </span>
                            </div>
                          ),
                        )
                  }
                </div>
              </Panel>


              <Panel
                title="Verifica automatica"
                eyebrow="TESTS"
                icon={<TestTube2 />}
              >
                <div className="test-summary">
                  <strong>
                    {
                      testState === "PASS"
                        ? "PASS"
                        : testState
                    }
                  </strong>

                  <div>
                    <p>
                      {
                        testEvents.length > 0
                          ? `${testEvents.length} esecuzioni test`
                          : "Evidence bundle"
                      }
                    </p>

                    <Progress
                      value={
                        testState === "PASS"
                          ? 100
                          : 0
                      }
                    />
                  </div>
                </div>

                <div className="test-list">
                  {
                    testEvents.length > 0
                      ? testEvents.map(
                          (
                            item,
                            index,
                          ) => (
                            <div
                              key={index}
                            >
                              <CheckCircle2 />

                              <span>
                                {
                                  String(
                                    item.summary ??
                                    `Test ${index + 1}`,
                                  )
                                }
                              </span>

                              <strong>
                                {
                                  Number(
                                    item.exit_status,
                                  ) === 0
                                    ? "PASS"
                                    : "FAIL"
                                }
                              </strong>
                            </div>
                          ),
                        )
                      : fallbackTests.map(
                          (test) => (
                            <div
                              key={
                                test[0]
                              }
                            >
                              <CheckCircle2 />

                              <span>
                                {test[0]}
                              </span>

                              <strong>
                                {
                                  test[1]
                                }/{test[2]}
                              </strong>
                            </div>
                          ),
                        )
                  }
                </div>
              </Panel>


              <Panel
                title="Rischio e sicurezza"
                eyebrow="RISK"
                icon={<ShieldAlert />}
              >
                <div className="risk-score">
                  <div>
                    <span>?</span>
                  </div>

                  <div>
                    <strong>
                      {
                        sourceUnchanged === false
                          ? "Verifica richiesta"
                          : "Repository protetto"
                      }
                    </strong>

                    <p>
                      {
                        sourceUnchanged === true
                          ? "Repository sorgente rimasto invariato durante l'esecuzione."
                          : "Workspace isolato e human gate attivi."
                      }
                    </p>
                  </div>
                </div>

                <div className="risk-items">
                  <p>
                    <span className="low">
                      LOW
                    </span>
                    {isLocalAi
                      ? `Provider locale attivo: ${localProvider} / ${localModel}`
                      : "Provider LLM disattivato"}
                  </p>

                  <p>
                    <span className="info">
                      INFO
                    </span>
                    Promotion richiede gate umano
                  </p>
                </div>
              </Panel>


              <Panel
                title="Routing modelli"
                eyebrow="MODEL ROUTES"
                icon={<Activity />}
              >
                <div className="model-list">
                  {
                    displayModels.map(
                      (model) => (
                        <div
                          key={
                            model[0]
                          }
                        >
                          <div>
                            <strong>
                              {
                                model[0]
                              }
                            </strong>

                            <span>
                              {
                                model[1]
                              }
                            </span>
                          </div>

                          <div className="model-bar">
                            <i
                              style={{
                                width:
                                  `${model[4]}%`,
                              }}
                            />
                          </div>

                          <p>
                            {model[2]}
                            <b>
                              {model[3]}
                            </b>
                          </p>
                        </div>
                      ),
                    )
                  }
                </div>
              </Panel>


              <Panel
                title="Decisione di promotion"
                eyebrow="DECISION"
                icon={<CircleDot />}
                className="decision-panel"
              >
                <p className="decision-copy">
                  Approva esegue una promotion locale
                  governata. Richiedi fix apre un feedback
                  del Product Owner e crea automaticamente
                  una nuova run bounded con lo stesso scope.
                  Nessun push o merge automatico.
                </p>

                <div className="decision-actions">
                  <Button
                    onClick={() =>
                      decide("approved")
                    }
                    className="approve"
                  >
                    <Check />
                    Approva
                  </Button>

                  <Button
                    onClick={() => {
                      setRepairError("");
                      setRepairDialog(true);
                    }}
                    variant="outline"
                    className="repair"
                  >
                    <RefreshCcw />
                    Richiedi fix
                  </Button>

                  <Button
                    onClick={() =>
                      decide("rejected")
                    }
                    variant="ghost"
                    className="reject"
                  >
                    <X />
                    Rifiuta
                  </Button>
                </div>

                {
                  gate !== "pending" &&
                  <Button
                    onClick={
                      exportDecision
                    }
                    variant="outline"
                    className="download"
                  >
                    <Download />
                    Scarica GateDecision.json
                  </Button>
                }
              </Panel>

            </TabsContent>


            <TabsContent
              value="evidence"
              id="evidence"
            >
              <Panel
                title="Evidence bundle"
                eyebrow="AUDIT"
                icon={<Archive />}
              >
                <div className="evidence-table">

                  <div className="evidence-row head">
                    <span>Artefatto</span>
                    <span>Stato</span>
                    <span>Origine</span>
                  </div>

                  {
                    evidenceFiles.map(
                      (file) => (
                        <button
                          type="button"
                          className={
                            `evidence-row evidence-row-button ${selectedEvidence === file
                              ? "selected"
                              : ""}`
                          }
                          key={file}
                          onClick={() =>
                            setSelectedEvidence(file)
                          }
                        >
                          <strong>
                            {file}
                          </strong>

                          <Badge className="verified">
                            {
                              imported[file]
                                ? "Verificato"
                                : "Assente"
                            }
                          </Badge>

                          <span>
                            {
                              imported[file]
                                ? apiConnected
                                  ? "Runner locale"
                                  : "Importato"
                                : "?"
                            }
                          </span>
                        </button>
                      ),
                    )
                  }

                </div>

                <div
                  className="evidence-detail"
                  aria-live="polite"
                >
                  <div className="evidence-detail-head">
                    <strong>
                      {selectedEvidence}
                    </strong>
                    <span>
                      Contenuto in sola lettura
                    </span>
                  </div>

                  <pre>
                    {selectedEvidenceText}
                  </pre>
                </div>
              </Panel>
            </TabsContent>


            <TabsContent
              value="memory"
              id="memory"
            >
              <Panel
                title="Memoria del progetto"
                eyebrow="PROJECT MEMORY"
                icon={<MemoryStick />}
              >
                <div className="memory-list">
                  {
                    memory.map(
                      (item) => (
                        <div
                          key={
                            item[0]
                          }
                        >
                          <span>
                            {item[0]}
                          </span>

                          <div>
                            <strong>
                              {
                                item[1]
                              }
                            </strong>

                            <p>
                              {
                                item[2]
                              }
                            </p>
                          </div>

                          <ChevronRight />
                        </div>
                      ),
                    )
                  }
                </div>
              </Panel>
            </TabsContent>

          </Tabs>
        </div>
      </div>


      {
        repairDialog &&
        <div
          className="modal-backdrop"
          onMouseDown={() =>
            !repairing &&
            setRepairDialog(false)
          }
        >
          <section
            className="run-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="repair-title"
            onMouseDown={
              (event) =>
                event.stopPropagation()
            }
          >
            <div className="modal-icon">
              <RefreshCcw />
            </div>

            <p className="kicker">
              PRODUCT OWNER REPAIR
            </p>

            <h2 id="repair-title">
              Descrivi il fix richiesto
            </h2>

            <p>
              ForgeLab manterra repository,
              file autorizzati, test e governance
              della run corrente e generera una
              nuova proposta verificata.
            </p>

            <label htmlFor="repair-feedback">
              Feedback
            </label>

            <textarea
              id="repair-feedback"
              value={repairFeedback}
              onChange={
                (event) =>
                  setRepairFeedback(
                    event.target.value,
                  )
              }
              rows={7}
              placeholder="Indica cosa manca o cosa deve essere corretto nella proposta corrente."
            />

            {
              repairError &&
              <div
                className="modal-note"
                role="alert"
              >
                <ShieldAlert />
                <span>
                  {repairError}
                </span>
              </div>
            }

            <div className="modal-actions">
              <Button
                variant="ghost"
                disabled={repairing}
                onClick={() =>
                  setRepairDialog(false)
                }
                className="cancel"
              >
                Annulla
              </Button>

              <Button
                disabled={repairing}
                onClick={() =>
                  void requestRepair()
                }
                className="primary-button"
              >
                {
                  repairing
                    ? "Correzione..."
                    : "Avvia fix"
                }

                <ArrowRight />
              </Button>
            </div>
          </section>
        </div>
      }


      {
        newRun &&
        <div
          className="modal-backdrop"
          onMouseDown={() =>
            !creatingRun &&
            setNewRun(false)
          }
        >
          <section
            className="run-modal run-modal-wide"
            role="dialog"
            aria-modal="true"
            aria-labelledby="new-run-title"
            onMouseDown={
              (event) =>
                event.stopPropagation()
            }
          >
            <div className="modal-icon">
              <Play />
            </div>

            <p className="kicker">
              NEW RUN - M8.6
            </p>

            <h2 id="new-run-title">
              Avvia una nuova esecuzione
            </h2>

            <p>
              Il Control Plane invia la
              richiesta al runner locale.
              Il lavoro verra eseguito in
              un workspace Git isolato.
            </p>


            <div className="run-form-grid" onChange={() => setRunFormError("")}>

              <div className="full">
                <label htmlFor="repository">
                  Repository locale
                </label>

                <input
                  id="repository"
                  value={repository}
                  onChange={
                    (event) =>
                      setRepository(
                        event.target.value,
                      )
                  }
                  placeholder="C:\Users\...\my-repository"
                />
              </div>


              <div className="full">
                <label htmlFor="objective">
                  Obiettivo della run
                </label>

                <textarea
                  id="objective"
                  value={objective}
                  onChange={
                    (event) =>
                      setObjective(
                        event.target.value,
                      )
                  }
                  rows={3}
                />
              </div>


              <div className="full">
                <label htmlFor="target-path">
                  {
                    aiDeveloperMode
                      ? "File autorizzati - 1 a 3"
                      : "File da modificare"
                  }
                </label>

                <textarea
                  id="target-path"
                  value={targetPath}
                  onChange={
                    (event) =>
                      setTargetPath(
                        event.target.value,
                      )
                  }
                  rows={
                    aiDeveloperMode
                      ? 3
                      : 1
                  }
                  placeholder={
                    aiDeveloperMode
                      ? "src/example.py\nsrc/example_test.py"
                      : "src/example.py"
                  }
                />
              </div>


              {!aiDeveloperMode && (
              <div>
                <label htmlFor="old-text">
                  Testo esistente
                </label>

                <textarea
                  id="old-text"
                  value={oldText}
                  onChange={
                    (event) =>
                      setOldText(
                        event.target.value,
                      )
                  }
                  rows={5}
                  placeholder="Testo esatto da sostituire"
                />
              </div>
              )}


              {!aiDeveloperMode && (
              <div>
                <label htmlFor="new-text">
                  Nuovo testo
                </label>

                <textarea
                  id="new-text"
                  value={newText}
                  onChange={
                    (event) =>
                      setNewText(
                        event.target.value,
                      )
                  }
                  rows={5}
                  placeholder="Sostituzione finale"
                />
              </div>
              )}


              {!aiDeveloperMode && (
              <div className="full">
                <label htmlFor="initial-new">
                  Primo candidato opzionale
                </label>

                <textarea
                  id="initial-new"
                  value={initialNewText}
                  onChange={
                    (event) =>
                      setInitialNewText(
                        event.target.value,
                      )
                  }
                  rows={2}
                  placeholder="Usalo per testare il ciclo failure -> diagnose -> repair"
                />
              </div>
              )}


              {aiDeveloperMode && (
                <div className="full modal-note">
                  <Sparkles />
                  <span>
                    REUSE-FIRST: ForgeLab usera Aider + Ollama locale
                    per generare autonomamente il candidate sui file
                    autorizzati. ForgeLab mantiene scope, compile gate,
                    test, Reviewer, Security e ToolGateway. ChatGPT non
                    partecipa alla run del prodotto target.
                  </span>
                </div>
              )}


              <div className="full">
                <label htmlFor="test-command">
                  Comando test - array JSON
                </label>

                <textarea
                  id="test-command"
                  value={testCommand}
                  onChange={
                    (event) =>
                      setTestCommand(
                        event.target.value,
                      )
                  }
                  rows={2}
                />
              </div>


              <div>
                <label>
                  Modalita run
                  <select
                    value={
                      aiDeveloperMode
                        ? "ai-developer"
                        : aiMode
                          ? "ai-local"
                          : "deterministic"
                    }
                    onChange={(event) => {
                      const value =
                        event.target.value;

                      setAiDeveloperMode(
                        value === "ai-developer",
                      );

                      setAiMode(
                        value === "ai-local"
                        || value === "ai-developer",
                      );
                    }}
                  >
                    <option value="deterministic">
                      Deterministica - EUR 0 - nessun LLM
                    </option>

                    <option value="ai-local">
                      AI assistita - EUR 0 - PM + Reviewer
                    </option>

                    <option value="ai-developer">
                      AI Developer REUSE-FIRST - Aider + Ollama - EUR 0
                    </option>
                  </select>
                </label>

                <label htmlFor="risk">
                  Rischio
                </label>

                <select
                  id="risk"
                  value={risk}
                  onChange={
                    (event) =>
                      setRisk(
                        event.target.value,
                      )
                  }
                >
                  <option value="normal">
                    Normal
                  </option>

                  <option value="high">
                    High
                  </option>
                </select>
              </div>


              <div>
                <label htmlFor="repairs">
                  Repair massimi
                </label>

                <select
                  id="repairs"
                  value={
                    maxRepairAttempts
                  }
                  onChange={
                    (event) =>
                      setMaxRepairAttempts(
                        Number(
                          event.target.value,
                        ),
                      )
                  }
                >
                  <option value={0}>0</option>
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                  <option value={3}>3</option>
                </select>
              </div>

            </div>


            <div className="modal-note">
              <ShieldAlert />
              {
                apiConnected
                  ? (
                      aiDeveloperMode
                        ? "REUSE-FIRST attivo. Aider usa Ollama locale sui soli file autorizzati; ForgeLab valida e applica con ToolGateway. ChatGPT assistance target run: 0. Costo API EUR 0."
                        : aiMode
                          ? "AI assistita attiva. Ollama GPU locale verra chiamato. Costo provider EUR 0."
                          : "Runner locale autenticato. Nessun provider LLM verra chiamato."
                    )
                  : "Runner non collegato: avvia ForgeLab dal launcher."
              }
            </div>


            {
              runFormError &&
              <div
                className="modal-note"
                role="alert"
              >
                <ShieldAlert />
                <span>
                  {runFormError}
                </span>
              </div>
            }


            <div className="modal-actions">

              <Button
                variant="ghost"
                disabled={creatingRun}
                onClick={() =>
                  setNewRun(false)
                }
                className="cancel"
              >
                Annulla
              </Button>

              <Button
                disabled={creatingRun}
                onClick={() =>
                  void createRun()
                }
                className="primary-button"
              >
                {
                  creatingRun
                    ? "Esecuzione..."
                    : "Avvia run"
                }

                <ArrowRight />
              </Button>

            </div>
          </section>
        </div>
      }


      {
        apiSetup &&
        <div
          className="modal-backdrop"
          onMouseDown={() =>
            setApiSetup(false)
          }
        >
          <section
            className="run-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="api-title"
            onMouseDown={
              (event) =>
                event.stopPropagation()
            }
          >
            <div className="modal-icon">
              <Wifi />
            </div>

            <p className="kicker">
              LOCAL RUNNER
            </p>

            <h2 id="api-title">
              Collega il runner ForgeLab
            </h2>

            <p>
              La connessione ? accettata
              solo dall?API locale
              autenticata.
            </p>

            <label htmlFor="api-base">
              Indirizzo API
            </label>

            <input
              id="api-base"
              value={apiBase}
              onChange={
                (event) =>
                  setApiBase(
                    event.target.value,
                  )
              }
            />

            <label htmlFor="api-token">
              Token locale
            </label>

            <input
              id="api-token"
              type="password"
              value={apiToken}
              onChange={
                (event) =>
                  setApiToken(
                    event.target.value,
                  )
              }
            />

            <div className="modal-note">
              <ShieldAlert />
              Il token resta nella memoria
              della pagina.
            </div>

            <div className="modal-actions">

              <Button
                variant="ghost"
                onClick={() =>
                  setApiSetup(false)
                }
                className="cancel"
              >
                Annulla
              </Button>

              <Button
                disabled={
                  connecting ||
                  apiToken.length < 24
                }
                onClick={() =>
                  void loadFromApi()
                }
                className="primary-button"
              >
                {
                  connecting
                    ? "Connessione?"
                    : "Collega"
                }

                <ArrowRight />
              </Button>

            </div>
          </section>
        </div>
      }

    </main>
  );
}
