import { handleBeforeDispatch } from "./index.js";

const message = process.argv[2] ?? "studio blender status";
const result = await handleBeforeDispatch(
  {
    content: message,
    isGroup: false
  },
  {
    channelId: "whatsapp",
    conversationId: "self"
  },
  {
    commandPrefix: process.env.OPENCLAW_STUDIO_ACTIONS_COMMAND_PREFIX ?? "studio",
    channels: (process.env.OPENCLAW_STUDIO_ACTIONS_CHANNELS ?? "whatsapp").split(",").map((value) => value.trim()).filter(Boolean),
    allowGroupMessages: process.env.OPENCLAW_STUDIO_ACTIONS_ALLOW_GROUP_MESSAGES === "true"
  },
  console
);

console.log(JSON.stringify(result, null, 2));
if (result == null) process.exit(2);
