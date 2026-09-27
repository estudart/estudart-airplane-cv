import { createAgent, ReactAgent } from "langchain";
import { ChatOpenAI } from "@langchain/openai";
import { MCPAdapter } from "../../infrastructure/mcp-adapter.js";
import { DynamicStructuredTool } from "@langchain/core/tools";
import { CameraAgentPort } from "../ports/camera-agent.port.js";

const CAPTURE_IMAGE_TOOL = "capture_image";

function formatToolResult(toolName: string, result: any) {
    if (toolName !== CAPTURE_IMAGE_TOOL || !Array.isArray(result?.content)) {
        return JSON.stringify(result);
    }

    const content = result.content.flatMap((item: any) => {
        if (item?.type === "image" && typeof item.data === "string") {
            return [{
                type: "input_image",
                image_url: `data:${item.mimeType ?? "image/jpeg"};base64,${item.data}`,
            }];
        }

        if (item?.type === "text" && typeof item.text === "string") {
            return [{ type: "input_text", text: item.text }];
        }

        return [];
    });

    return content.length > 0 ? content : JSON.stringify(result);
}

export class CameraAgent implements CameraAgentPort {
    _systemPrompt: string;
    _llmChat: ChatOpenAI;
    _agent: ReactAgent;
    _mcpAdapter: MCPAdapter;
    _mcpTools: Record<string, any>[];

    constructor(
        systemPrompt: string,
        model: string,
        mcpAdapter: MCPAdapter,
        mcpTools: Record<string, any>[]
    ) {
        this._systemPrompt = systemPrompt;

        this._mcpAdapter = mcpAdapter;
        this._mcpTools = mcpTools;

        this._llmChat = new ChatOpenAI({
            model: model,
            useResponsesApi: this._mcpTools.some((tool) => tool.name === CAPTURE_IMAGE_TOOL),
        });

        this._agent = createAgent({
            model: this._llmChat,
            systemPrompt: this._systemPrompt,
            tools: this._mcpTools.map((tool) =>
                new DynamicStructuredTool({
                    name: tool.name,
                    description: tool.description,
                    schema: tool.inputSchema,
                    func: async (args: Record<string, string>) => {
                        const result = await this._mcpAdapter.callTool(tool.name, args)
                        return formatToolResult(tool.name, result);
                    }
                }))
        });
    }

    async invokeAgent(question: string): Promise<any> {
        const response = await this._agent.invoke({
            messages: [{ role: "user", content: question }],
        })
        const lastMessage = response.messages.at(-1)?.content;
        console.log(lastMessage);
        return lastMessage;
    };
}