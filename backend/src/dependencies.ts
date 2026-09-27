import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { MCPAdapter } from "./infrastructure/mcp-adapter.js";
import { CameraAgent } from "./application/agents/camera-agent.js";
import { CAMERA_AGENT_SYSTEM_PROMPT } from "./application/agents/prompts/camera-agent-prompt.js"
import { CameraAssistent } from "./application/services/camera-assistent.service.js";
import { WebSocketService } from "./application/services/wss-handler.service.js";

const CAMERA_AGENT_TOOLS = ["capture_image", "get_latest_frame_info", "mcp_status"];
const mcpServerUrl = process.env.MCP_SERVER_URL ?? "http://localhost:8000"

const MCPUrl = `${mcpServerUrl}/mcp`
const client = await getClient(MCPUrl);

const mcpAdapter = new MCPAdapter(client);
const mcpTools = await mcpAdapter.listTools();

const pick = (names: string[]) => mcpTools.filter((tool) => names.includes(tool.name));

const cameraAgent = new CameraAgent(
    CAMERA_AGENT_SYSTEM_PROMPT,
    process.env.MODEL ?? "gpt-4o-mini",
    mcpAdapter,
    pick(CAMERA_AGENT_TOOLS),
)

const cameraAssistent = new CameraAssistent(cameraAgent);

async function getClient(url: string) {
    const transport = new StreamableHTTPClientTransport(new URL(url));
    const client = new Client(
        { name: "camera-server", version: "1.0.0"},
        { capabilities: {} }
    )
    await client.connect(transport);
    return client;
}

const webSocketService = new WebSocketService(cameraAssistent);

export { mcpAdapter, cameraAgent, cameraAssistent, webSocketService };

