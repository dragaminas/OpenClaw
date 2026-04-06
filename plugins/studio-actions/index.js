import { execFile } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..", "..");
const blenderActionScript = path.join(repoRoot, "scripts", "actions", "blender-action.sh");
const comfyuiActionScript = path.join(repoRoot, "scripts", "actions", "comfyui-action.sh");
const runnerActionScript = path.join(repoRoot, "scripts", "actions", "runner-action.sh");
const defaultCommandPrefix = "studio";
const defaultChannels = ["whatsapp"];
const workflowAdvisorRequests = new Map();
const workflowAdvisorTtlMs = 5 * 60 * 1000;

function normalizeChannels(pluginConfig) {
  return Array.isArray(pluginConfig?.channels) && pluginConfig.channels.length > 0
    ? pluginConfig.channels.map((value) => String(value).trim()).filter(Boolean)
    : defaultChannels;
}

function normalizeCommandPrefix(pluginConfig) {
  const value = typeof pluginConfig?.commandPrefix === "string" ? pluginConfig.commandPrefix.trim() : "";
  return value || defaultCommandPrefix;
}

function normalizeMessage(text) {
  return String(text ?? "").replace(/\s+/g, " ").trim();
}

function normalizeIntentText(text) {
  return normalizeMessage(text)
    .toLowerCase()
    .replace(/^[¿?¡!.,:;()[\]{}"']+/u, "")
    .replace(/[¿?¡!.,:;()[\]{}"']+$/u, "")
    .trim();
}

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizeWorkflowRef(rawValue) {
  return normalizeMessage(rawValue)
    .replace(/^(workflow|flujo)\s+/i, "")
    .replace(/^que hace\s+/i, "")
    .trim();
}

function parseWorkflowComparisonRefs(rawValue) {
  const normalized = normalizeMessage(rawValue)
    .replace(/^(entre)\s+/i, "")
    .replace(/^(workflow|workflows|flujo|flujos)\s+/i, "")
    .trim();

  if (!normalized) return null;

  for (const separator of [/\s+y\s+/i, /\s+con\s+/i, /\s+vs\.?\s+/i, /\s+contra\s+/i]) {
    const parts = normalized
      .split(separator)
      .map((value) => normalizeWorkflowRef(value))
      .filter(Boolean);

    if (parts.length === 2) {
      return {
        leftWorkflowRef: parts[0],
        rightWorkflowRef: parts[1]
      };
    }
  }

  return null;
}

function stripWakeWord(rawText, prefix) {
  const normalized = normalizeMessage(rawText);
  const low = normalized.toLowerCase();
  const lowPrefix = prefix.toLowerCase();
  if (low === lowPrefix) return "";

  const pattern = new RegExp(`^${escapeRegExp(prefix)}(?:\\s*[,.:;!?-]\\s*|\\s+)`, "i");
  const match = normalized.match(pattern);
  if (match) return normalized.slice(match[0].length).trim();

  const rawLines = String(rawText ?? "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of rawLines) {
    const linePattern = new RegExp(`^${escapeRegExp(prefix)}(?:\\s*[,.:;!?-]\\s*|\\s+|$)`, "i");
    const lineMatch = line.match(linePattern);
    if (lineMatch) return line.slice(lineMatch[0].length).trim();
  }

  return null;
}

function buildHelpText(prefix) {
  return [
    `Empieza siempre con "${prefix}" al principio del mensaje.`,
    "Despues puedes escribir de forma sencilla.",
    "Ejemplos:",
    `${prefix} abre blender`,
    `${prefix} como esta blender`,
    `${prefix} crea proyecto castillo`,
    `${prefix} abre proyecto castillo`,
    `${prefix} haz una prueba de blender`,
    `${prefix} abre comfyui`,
    `${prefix} inicia comfyui`,
    `${prefix} reinicia comfyui`,
    `${prefix} como esta comfyui`,
    `${prefix} comfyui workflows`,
    `${prefix} que hace prepara-video`,
    `${prefix} compara prepara-video y render-video`,
    `${prefix} comfyui abre workflow prepara-video`,
    `${prefix} comfyui ruta workflow prepara-video`,
    `${prefix} comfyui smoke`,
    `${prefix} comfyui smoke SMK-VID-04-01`,
    `${prefix} comfyui estado smoke-light-5`,
    `${prefix} comfyui evidencia smoke-light-5`,
    "",
    "Tambien funciona el modo tecnico:",
    `${prefix} blender status`,
    `${prefix} comfyui status`,
    `${prefix} comfyui restart`,
    `${prefix} comfyui validate atomic AT-IMG-02-01`,
    `${prefix} comfyui validate composed CP-VIDEO-01`
  ].join("\n");
}

function parseRunnerAction(tokens) {
  const runnerId = tokens[0]?.toLowerCase() ?? "";
  const action = tokens[1]?.toLowerCase() ?? "help";
  const rawArg = tokens.slice(2).join(" ").trim();

  if (runnerId !== "comfyui") return null;

  switch (action) {
    case "smoke":
      return {
        kind: "runner-start",
        runnerId,
        operationKind: "validate_smoke",
        targetId: rawArg || null
      };
    case "estado":
      return rawArg
        ? { kind: "runner-status", runnerId, runId: rawArg }
        : { kind: "error", text: "Dime el run_id. Ejemplo: studio comfyui estado smoke-20260404-120000" };
    case "cancela":
    case "cancel":
    case "cancelar":
      return rawArg
        ? { kind: "runner-cancel", runnerId, runId: rawArg }
        : { kind: "error", text: "Dime el run_id. Ejemplo: studio comfyui cancela smoke-20260404-120000" };
    case "evidencia":
    case "resultado":
    case "result":
      return rawArg
        ? { kind: "runner-result", runnerId, runId: rawArg }
        : { kind: "error", text: "Dime el run_id. Ejemplo: studio comfyui evidencia smoke-20260404-120000" };
    case "validate": {
      const validationKind = tokens[2]?.toLowerCase() ?? "";
      const targetId = tokens.slice(3).join(" ").trim();
      if (validationKind === "atomic") {
        return targetId
          ? { kind: "runner-start", runnerId, operationKind: "validate_atomic", targetId }
          : { kind: "error", text: "Dime el test_id atomico. Ejemplo: studio comfyui validate atomic AT-IMG-02-01" };
      }
      if (validationKind === "composed") {
        return targetId
          ? { kind: "runner-start", runnerId, operationKind: "validate_composed", targetId }
          : { kind: "error", text: "Dime el test_id compuesto. Ejemplo: studio comfyui validate composed CP-VIDEO-01" };
      }
      return { kind: "error", text: "Usa validate atomic <test_id> o validate composed <test_id>." };
    }
    default:
      return null;
  }
}

function parseLegacyCommand(stripped, prefix) {
  const tokens = stripped.split(" ").filter(Boolean);
  if (tokens.length === 0) return { kind: "help" };

  const tool = tokens[0].toLowerCase();
  if (tool !== "blender" && tool !== "comfyui") {
    return {
      kind: "unsupported",
      text: `Por ahora solo estan habilitadas acciones de Blender y ComfyUI. Escribe "${prefix}" para ver ayuda.`
    };
  }

  const runnerAction = parseRunnerAction(tokens);
  if (runnerAction) return runnerAction;

  const action = tokens[1]?.toLowerCase() ?? "help";
  const rawArg = tokens.slice(2).join(" ").trim();

  if (tool === "comfyui") {
    const workflowSubject = tokens[2]?.toLowerCase() ?? "";
    const workflowRef = tokens.slice(3).join(" ").trim();

    switch (action) {
      case "help":
        return { kind: "help" };
      case "workflows":
        return { kind: "comfyui-workflows" };
      case "que":
        if (tokens[2]?.toLowerCase() === "hace") {
          const workflowRef = normalizeWorkflowRef(tokens.slice(3).join(" "));
          return workflowRef
            ? { kind: "comfyui-workflow-info", workflowRef }
            : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio comfyui que hace prepara-video" };
        }
        return { kind: "error", text: `No reconozco esa accion de ComfyUI. Escribe "${prefix}" para ver ayuda.` };
      case "abre":
        if (workflowSubject === "workflow") {
          return workflowRef
            ? { kind: "comfyui-workflow-open", workflowRef }
            : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio comfyui abre workflow prepara-video" };
        }
        return { kind: "comfyui-open" };
      case "status":
        return { kind: "comfyui-status" };
      case "start":
      case "launch":
        return { kind: "comfyui-start" };
      case "restart":
      case "reload":
        return { kind: "comfyui-restart" };
      case "open":
        if (workflowSubject === "workflow") {
          return workflowRef
            ? { kind: "comfyui-workflow-open", workflowRef }
            : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio comfyui open workflow prepara-video" };
        }
        return { kind: "comfyui-open" };
      case "ruta":
      case "path":
        if (workflowSubject === "workflow") {
          return workflowRef
            ? { kind: "comfyui-workflow-path", workflowRef }
            : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio comfyui ruta workflow prepara-video" };
        }
        return { kind: "error", text: `No reconozco esa accion de ComfyUI. Escribe "${prefix}" para ver ayuda.` };
      case "explica":
      case "describe":
        return normalizeWorkflowRef(rawArg)
          ? { kind: "comfyui-workflow-info", workflowRef: normalizeWorkflowRef(rawArg) }
          : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio comfyui explica prepara-video" };
      case "compara":
      case "compare": {
        const comparison = parseWorkflowComparisonRefs(rawArg);
        return comparison
          ? { kind: "comfyui-workflow-compare", ...comparison }
          : { kind: "error", text: "Dime dos aliases. Ejemplo: studio comfyui compara prepara-video y render-video" };
      }
      case "stop":
        return { kind: "comfyui-stop" };
      case "url":
        return { kind: "comfyui-url" };
      default:
        return { kind: "error", text: `No reconozco esa accion de ComfyUI. Escribe "${prefix}" para ver ayuda.` };
    }
  }

  switch (action) {
    case "help":
      return { kind: "help" };
    case "launch":
      return { kind: "blender-launch" };
    case "status":
      return { kind: "blender-status" };
    case "new":
      return rawArg
        ? { kind: "blender-new", arg: rawArg }
        : { kind: "error", text: "Dime el nombre del proyecto. Ejemplo: crea proyecto castillo" };
    case "open":
      return rawArg
        ? { kind: "blender-open", arg: rawArg }
        : { kind: "error", text: "Dime que proyecto quieres abrir. Ejemplo: abre proyecto castillo" };
    case "smoke-test":
      return rawArg
        ? { kind: "blender-smoke-test", arg: rawArg }
        : { kind: "error", text: "Dime el nombre de la prueba. Ejemplo: haz una prueba de blender" };
    default:
      return { kind: "error", text: `No reconozco esa accion. Escribe "${prefix}" para ver ayuda.` };
  }
}

function extractProjectName(normalized, prefixes) {
  const low = normalized.toLowerCase();
  for (const prefix of prefixes) {
    if (low.startsWith(prefix)) {
      const value = normalized.slice(prefix.length).trim();
      if (!value) return "";
      return value.replace(/^llamado\s+/i, "").replace(/^que se llame\s+/i, "").trim();
    }
  }
  return null;
}

function parseNaturalSpanish(normalized) {
  const low = normalizeIntentText(normalized);

  if ([
    "blender",
    "abre blender",
    "abrir blender",
    "abre el blender",
    "abre la app de blender"
  ].includes(low)) {
    return { kind: "blender-launch" };
  }

  if ([
    "estado blender",
    "como esta blender",
    "como está blender",
    "blender status",
    "estado de blender",
    "blender esta listo"
  ].includes(low)) {
    return { kind: "blender-status" };
  }

  if ([
    "abre comfyui",
    "abrir comfyui",
    "abre la ui de comfyui",
    "abre la interfaz de comfyui"
  ].includes(low)) {
    return { kind: "comfyui-open" };
  }

  if ([
    "inicia comfyui",
    "arranca comfyui",
    "levanta comfyui",
    "iniciar comfyui",
    "arrancar comfyui"
  ].includes(low)) {
    return { kind: "comfyui-start" };
  }

  if ([
    "reinicia comfyui",
    "reiniciar comfyui",
    "reinicia la ui de comfyui",
    "reinicia el servicio de comfyui",
    "restart comfyui"
  ].includes(low)) {
    return { kind: "comfyui-restart" };
  }

  if ([
    "estado comfyui",
    "como esta comfyui",
    "como está comfyui",
    "comfyui status",
    "estado de comfyui",
    "comfyui esta listo"
  ].includes(low)) {
    return { kind: "comfyui-status" };
  }

  if ([
    "para comfyui",
    "deten comfyui",
    "detener comfyui",
    "stop comfyui"
  ].includes(low)) {
    return { kind: "comfyui-stop" };
  }

  if ([
    "workflows comfyui",
    "lista workflows comfyui",
    "muestra workflows comfyui",
    "lista los workflows de comfyui"
  ].includes(low)) {
    return { kind: "comfyui-workflows" };
  }

  const workflowInfo = extractProjectName(normalized, [
    "que hace ",
    "que hace el workflow ",
    "que hace el flujo ",
    "explica workflow ",
    "explica el workflow ",
    "explica ",
    "describe workflow ",
    "describe el workflow "
  ]);
  if (workflowInfo !== null) {
    const normalizedWorkflowInfo = normalizeWorkflowRef(workflowInfo);
    return normalizedWorkflowInfo
      ? { kind: "comfyui-workflow-info", workflowRef: normalizedWorkflowInfo }
      : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio que hace prepara-video" };
  }

  const workflowComparison = extractProjectName(normalized, [
    "compara ",
    "compara workflow ",
    "compara workflows ",
    "compara el workflow ",
    "compara los workflows ",
    "compara flujo ",
    "compara flujos ",
    "compara el flujo ",
    "compara los flujos ",
    "compara workflows de comfyui ",
    "compara workflows en comfyui "
  ]);
  if (workflowComparison !== null) {
    const comparison = parseWorkflowComparisonRefs(workflowComparison);
    return comparison
      ? { kind: "comfyui-workflow-compare", ...comparison }
      : { kind: "error", text: "Dime dos aliases. Ejemplo: studio compara prepara-video y render-video" };
  }

  const openWorkflow = extractProjectName(normalized, [
    "abre workflow ",
    "abrir workflow ",
    "abre el workflow ",
    "abrir el workflow ",
    "abre workflow de comfyui ",
    "abrir workflow de comfyui "
  ]);
  if (openWorkflow !== null) {
    return openWorkflow
      ? { kind: "comfyui-workflow-open", workflowRef: openWorkflow }
      : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio abre workflow prepara-video" };
  }

  const workflowPath = extractProjectName(normalized, [
    "ruta workflow ",
    "muestra ruta workflow ",
    "path workflow ",
    "ruta del workflow "
  ]);
  if (workflowPath !== null) {
    return workflowPath
      ? { kind: "comfyui-workflow-path", workflowRef: workflowPath }
      : { kind: "error", text: "Dime el alias del workflow. Ejemplo: studio ruta workflow prepara-video" };
  }

  if ([
    "corre smoke de comfyui",
    "ejecuta smoke de comfyui",
    "haz smoke de comfyui",
    "comfyui smoke"
  ].includes(low)) {
    return {
      kind: "runner-start",
      runnerId: "comfyui",
      operationKind: "validate_smoke",
      targetId: null
    };
  }

  const newProject = extractProjectName(normalized, [
    "crea proyecto ",
    "crear proyecto ",
    "crea un proyecto ",
    "crear un proyecto ",
    "nuevo proyecto ",
    "proyecto nuevo ",
    "crea proyecto de blender ",
    "crear proyecto de blender "
  ]);
  if (newProject !== null) {
    return newProject
      ? { kind: "blender-new", arg: newProject }
      : { kind: "error", text: "Dime el nombre del proyecto. Ejemplo: crea proyecto castillo" };
  }

  const openProject = extractProjectName(normalized, [
    "abre proyecto ",
    "abrir proyecto ",
    "abre el proyecto ",
    "abrir el proyecto ",
    "abre archivo ",
    "abrir archivo "
  ]);
  if (openProject !== null) {
    return openProject
      ? { kind: "blender-open", arg: openProject }
      : { kind: "error", text: "Dime que proyecto quieres abrir. Ejemplo: abre proyecto castillo" };
  }

  const smokeTest = extractProjectName(normalized, [
    "haz una prueba de blender ",
    "haz prueba de blender ",
    "prueba de blender ",
    "blender prueba ",
    "smoke test blender "
  ]);
  if (smokeTest !== null) {
    return smokeTest
      ? { kind: "blender-smoke-test", arg: smokeTest }
      : { kind: "blender-smoke-test", arg: "prueba-blender" };
  }

  if ([
    "haz una prueba de blender",
    "haz prueba de blender",
    "prueba de blender",
    "smoke test blender"
  ].includes(low)) {
    return { kind: "blender-smoke-test", arg: "prueba-blender" };
  }

  return null;
}

function parseSafeActionMessage(text, prefix) {
  const rawText = String(text ?? "");
  const normalized = normalizeMessage(rawText);
  if (!normalized) return null;

  const stripped = stripWakeWord(rawText, prefix);
  if (stripped === null) return null;
  if (!stripped) return { kind: "help" };

  const low = normalizeIntentText(stripped);
  if (low === "help" || low === "ayuda") {
    return { kind: "help" };
  }

  const natural = parseNaturalSpanish(stripped);
  if (natural) return natural;

  return parseLegacyCommand(stripped, prefix);
}

function buildFailureText(error) {
  const stderr = typeof error?.stderr === "string" ? error.stderr.trim() : "";
  const stdout = typeof error?.stdout === "string" ? error.stdout.trim() : "";
  const message = typeof error?.message === "string" ? error.message.trim() : "";
  return stderr || stdout || message || "No se pudo completar la accion solicitada.";
}

async function execActionScript(scriptPath, args) {
  return execFileAsync(scriptPath, args, {
    cwd: repoRoot,
    env: process.env,
    maxBuffer: 1024 * 1024
  });
}

async function runScriptAction(scriptPath, args) {
  try {
    const { stdout, stderr } = await execActionScript(scriptPath, args);
    const text = [stdout, stderr].map((value) => String(value ?? "").trim()).filter(Boolean).join("\n");
    return {
      handled: true,
      text: text || "Accion completada."
    };
  } catch (error) {
    return {
      handled: true,
      text: buildFailureText(error)
    };
  }
}

async function runBlenderAction(args) {
  return runScriptAction(blenderActionScript, args);
}

async function runComfyUIAction(args) {
  return runScriptAction(comfyuiActionScript, args);
}

function formatHomePath(filePath) {
  const normalized = String(filePath ?? "").trim();
  const homeDir = process.env.HOME ? path.resolve(process.env.HOME) : "";
  if (!normalized || !homeDir) return normalized;
  const resolved = path.resolve(normalized);
  return resolved.startsWith(`${homeDir}${path.sep}`) ? `~${resolved.slice(homeDir.length)}` : normalized;
}

function parseRunnerPayload(rawText) {
  const normalized = String(rawText ?? "").trim();
  if (!normalized) return null;
  try {
    return JSON.parse(normalized);
  } catch {
    return null;
  }
}

function formatRunnerResponseText(payload) {
  if (!payload || typeof payload !== "object") return "No se pudo interpretar la respuesta del runner.";

  const lines = [];
  if (payload.run_id) lines.push(`run_id=${payload.run_id}`);
  if (payload.status) lines.push(`status=${payload.status}`);
  if (payload.target_id) lines.push(`target=${payload.target_id}`);
  if (payload.current_target_id) lines.push(`actual=${payload.current_target_id}`);
  if (typeof payload.accepted === "boolean") lines.push(`accepted=${String(payload.accepted)}`);
  if (payload.message) lines.push(`mensaje=${payload.message}`);

  const evidencePath = payload.evidence_path || payload?.metadata?.evidence_path;
  if (evidencePath) lines.push(`evidencia=${formatHomePath(evidencePath)}`);

  const summaryPath = payload.summary_path || payload?.metadata?.summary_path;
  if (summaryPath) lines.push(`summary=${formatHomePath(summaryPath)}`);

  const manifestPath = payload.manifest_path || payload?.metadata?.manifest_path;
  if (manifestPath) lines.push(`manifiesto=${formatHomePath(manifestPath)}`);

  if (payload?.metadata?.current_prompt_id) {
    lines.push(`prompt_id=${payload.metadata.current_prompt_id}`);
  }
  if (payload?.metadata?.cancel_requested === true && payload.status === "running") {
    lines.push("cancelacion=solicitada");
  }

  return lines.join("\n") || "Accion completada.";
}

async function runRunnerAction(args) {
  try {
    const { stdout, stderr } = await execFileAsync(runnerActionScript, args, {
      cwd: repoRoot,
      env: process.env,
      maxBuffer: 1024 * 1024
    });
    const payload = parseRunnerPayload(stdout);
    if (payload) {
      return {
        handled: true,
        text: formatRunnerResponseText(payload)
      };
    }

    const text = [stdout, stderr].map((value) => String(value ?? "").trim()).filter(Boolean).join("\n");
    return {
      handled: true,
      text: text || "Accion completada."
    };
  } catch (error) {
    return {
      handled: true,
      text: buildFailureText(error)
    };
  }
}

function buildWorkflowAdvisorKeyCandidates(text) {
  const normalized = normalizeIntentText(text);
  if (!normalized) return [];
  const strippedPrefix = normalized.replace(/^studio\s+/i, "").trim();
  return Array.from(new Set([normalized, strippedPrefix].filter(Boolean)));
}

function pruneWorkflowAdvisorRequests(now = Date.now()) {
  for (const [key, value] of workflowAdvisorRequests.entries()) {
    if (!value || typeof value !== "object" || now - value.createdAt > workflowAdvisorTtlMs) {
      workflowAdvisorRequests.delete(key);
    }
  }
}

function registerWorkflowAdvisorRequest(messageText, advisoryContext) {
  const now = Date.now();
  pruneWorkflowAdvisorRequests(now);
  for (const key of buildWorkflowAdvisorKeyCandidates(messageText)) {
    workflowAdvisorRequests.set(key, {
      advisoryContext,
      createdAt: now
    });
  }
}

function consumeWorkflowAdvisorRequest(promptText) {
  pruneWorkflowAdvisorRequests();
  for (const key of buildWorkflowAdvisorKeyCandidates(promptText)) {
    const match = workflowAdvisorRequests.get(key);
    if (match) {
      workflowAdvisorRequests.delete(key);
      return match.advisoryContext;
    }
  }
  return null;
}

function buildWorkflowAdvisorPromptContext(advisoryContext, promptText) {
  const advisoryPayload = typeof advisoryContext === "string"
    ? { mode: "single", advisoryContext }
    : advisoryContext;
  const mode = advisoryPayload?.mode === "compare" ? "compare" : "single";
  const groundedContext = String(advisoryPayload?.advisoryContext ?? "").trim();

  return [
    "Studio advisory mode is active for this turn.",
    `The user asked: ${promptText}`,
    "Use the following grounded workflow context to answer interactively and naturally.",
    mode === "compare"
      ? "Compare the workflows below. Explain what each one does, how they differ, and when to choose one or chain them together."
      : "Explain how the workflow works and how to use it in ComfyUI.",
    "Prefer the real workflow entry nodes, prompt nodes, model nodes, and outputs from the context.",
    "Do not claim to see nodes or settings that are not present below.",
    "",
    groundedContext
  ].join("\n");
}

async function prepareWorkflowAdvisorTurn(event, parsed) {
  try {
    const { stdout, stderr } = await execActionScript(comfyuiActionScript, [
      "workflow-advisory",
      parsed.workflowRef
    ]);
    const advisoryContext = [stdout, stderr]
      .map((value) => String(value ?? "").trim())
      .filter(Boolean)
      .join("\n");

    if (!advisoryContext) {
      return {
        handled: true,
        text: "No pude preparar contexto suficiente para explicar ese workflow."
      };
    }

    registerWorkflowAdvisorRequest(event?.content ?? event?.body ?? "", {
      mode: "single",
      advisoryContext
    });
    return { handled: false };
  } catch (error) {
    return {
      handled: true,
      text: buildFailureText(error)
    };
  }
}

async function prepareWorkflowComparisonAdvisorTurn(event, parsed) {
  try {
    const { stdout, stderr } = await execActionScript(comfyuiActionScript, [
      "workflow-compare-advisory",
      parsed.leftWorkflowRef,
      parsed.rightWorkflowRef
    ]);
    const advisoryContext = [stdout, stderr]
      .map((value) => String(value ?? "").trim())
      .filter(Boolean)
      .join("\n");

    if (!advisoryContext) {
      return {
        handled: true,
        text: "No pude preparar contexto suficiente para comparar esos workflows."
      };
    }

    registerWorkflowAdvisorRequest(event?.content ?? event?.body ?? "", {
      mode: "compare",
      advisoryContext
    });
    return { handled: false };
  } catch (error) {
    return {
      handled: true,
      text: buildFailureText(error)
    };
  }
}

async function handleBeforeDispatch(event, ctx, pluginConfig = {}, logger = console) {
  const allowedChannels = normalizeChannels(pluginConfig);
  if (!allowedChannels.includes(ctx?.channelId ?? "")) return undefined;
  if (event?.isGroup === true && pluginConfig?.allowGroupMessages !== true) return undefined;

  const prefix = normalizeCommandPrefix(pluginConfig);
  const parsed = parseSafeActionMessage(event?.content ?? event?.body ?? "", prefix);
  if (!parsed) {
    return { handled: true };
  }

  switch (parsed.kind) {
    case "help":
      return { handled: true, text: buildHelpText(prefix) };
    case "unsupported":
    case "error":
      return { handled: true, text: parsed.text };
    case "blender-launch":
      return runBlenderAction(["launch"]);
    case "blender-status":
      return runBlenderAction(["status"]);
    case "blender-new":
      return runBlenderAction(["new", parsed.arg]);
    case "blender-open":
      return runBlenderAction(["open", parsed.arg]);
    case "blender-smoke-test":
      return runBlenderAction(["smoke-test", parsed.arg]);
    case "comfyui-status":
      return runComfyUIAction(["status"]);
    case "comfyui-start":
      return runComfyUIAction(["start"]);
    case "comfyui-restart":
      return runComfyUIAction(["restart"]);
    case "comfyui-open":
      return runComfyUIAction(["open"]);
    case "comfyui-workflows":
      return runComfyUIAction(["workflows"]);
    case "comfyui-workflow-info":
      return prepareWorkflowAdvisorTurn(event, parsed);
    case "comfyui-workflow-compare":
      return prepareWorkflowComparisonAdvisorTurn(event, parsed);
    case "comfyui-workflow-open":
      return runComfyUIAction(["open-workflow", parsed.workflowRef]);
    case "comfyui-workflow-path":
      return runComfyUIAction(["workflow-path", parsed.workflowRef]);
    case "comfyui-stop":
      return runComfyUIAction(["stop"]);
    case "comfyui-url":
      return runComfyUIAction(["url"]);
    case "runner-start": {
      const args = ["start", parsed.runnerId, parsed.operationKind];
      if (parsed.targetId) args.push(parsed.targetId);
      args.push("--requested-by", String(ctx?.conversationId ?? "whatsapp"));
      args.push("--channel", String(ctx?.channelId ?? "whatsapp"));
      return runRunnerAction(args);
    }
    case "runner-status":
      return runRunnerAction(["status", parsed.runnerId, parsed.runId]);
    case "runner-cancel":
      return runRunnerAction([
        "cancel",
        parsed.runnerId,
        parsed.runId,
        "--requested-by",
        String(ctx?.conversationId ?? "whatsapp"),
        "--channel",
        String(ctx?.channelId ?? "whatsapp")
      ]);
    case "runner-result":
      return runRunnerAction(["result", parsed.runnerId, parsed.runId]);
    default:
      logger?.warn?.(`studio-actions: accion desconocida ${parsed.kind}`);
      return { handled: true, text: `No reconozco esa accion segura. Usa "${prefix} help".` };
  }
}

const studioActionsPlugin = {
  id: "studio-actions",
  name: "Studio Actions",
  description: "Puente seguro entre WhatsApp y wrappers locales para Blender y ComfyUI.",
  configSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      commandPrefix: { type: "string", minLength: 1 },
      channels: {
        type: "array",
        items: { type: "string", minLength: 1 }
      },
      allowGroupMessages: { type: "boolean" }
    }
  },
  register(api) {
    api.on("before_dispatch", async (event, ctx) => {
      try {
        return await handleBeforeDispatch(event, ctx, api.pluginConfig ?? {}, api.logger);
      } catch (error) {
        api.logger?.error?.(`studio-actions: ${buildFailureText(error)}`);
        return {
          handled: true,
          text: "La capa segura de Studio fallo antes de ejecutar la accion."
        };
      }
    });
    api.on("before_prompt_build", (event) => {
      try {
        const advisoryContext = consumeWorkflowAdvisorRequest(event?.prompt ?? "");
        if (!advisoryContext) return undefined;
        return {
          prependContext: buildWorkflowAdvisorPromptContext(
            advisoryContext,
            String(event?.prompt ?? "").trim()
          )
        };
      } catch (error) {
        api.logger?.error?.(`studio-actions prompt injection: ${buildFailureText(error)}`);
        return undefined;
      }
    });
  }
};

export {
  buildHelpText,
  buildWorkflowAdvisorPromptContext,
  consumeWorkflowAdvisorRequest,
  handleBeforeDispatch,
  parseSafeActionMessage,
  parseWorkflowComparisonRefs,
  prepareWorkflowComparisonAdvisorTurn,
  prepareWorkflowAdvisorTurn,
  registerWorkflowAdvisorRequest
};
export default studioActionsPlugin;
