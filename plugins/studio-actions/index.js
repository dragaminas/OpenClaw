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
const defaultCommandPrefix = "studio";
const defaultChannels = ["whatsapp"];

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

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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
    `${prefix} como esta comfyui`,
    "",
    "Tambien funciona el modo tecnico:",
    `${prefix} blender status`,
    `${prefix} comfyui status`
  ].join("\n");
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

  const action = tokens[1]?.toLowerCase() ?? "help";
  const rawArg = tokens.slice(2).join(" ").trim();

  if (tool === "comfyui") {
    switch (action) {
      case "help":
        return { kind: "help" };
      case "status":
        return { kind: "comfyui-status" };
      case "start":
      case "launch":
        return { kind: "comfyui-start" };
      case "open":
        return { kind: "comfyui-open" };
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
  const low = normalized.toLowerCase();

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

  const low = stripped.toLowerCase();
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

async function runBlenderAction(args) {
  try {
    const { stdout, stderr } = await execFileAsync(blenderActionScript, args, {
      cwd: repoRoot,
      env: process.env,
      maxBuffer: 1024 * 1024
    });
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

async function runComfyUIAction(args) {
  try {
    const { stdout, stderr } = await execFileAsync(comfyuiActionScript, args, {
      cwd: repoRoot,
      env: process.env,
      maxBuffer: 1024 * 1024
    });
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
    case "comfyui-open":
      return runComfyUIAction(["open"]);
    case "comfyui-stop":
      return runComfyUIAction(["stop"]);
    case "comfyui-url":
      return runComfyUIAction(["url"]);
    default:
      logger?.warn?.(`studio-actions: accion desconocida ${parsed.kind}`);
      return { handled: true, text: `No reconozco esa accion segura. Usa "${prefix} help".` };
  }
}

const studioActionsPlugin = {
  id: "studio-actions",
  name: "Studio Actions",
  description: "Puente seguro entre WhatsApp y wrappers locales para Blender.",
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
  }
};

export { buildHelpText, handleBeforeDispatch, parseSafeActionMessage };
export default studioActionsPlugin;
