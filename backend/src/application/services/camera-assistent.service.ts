import { CameraAgentPort } from "../ports/camera-agent.port.js";
import { UnknownAgentError } from "../errors/unknown-agent.error.js";

export class CameraAssistent {
    _cameraAgent: CameraAgentPort;
    _agentMap: Record<string, CameraAgentPort>;

    constructor(cameraAgent: CameraAgentPort) {
        this._cameraAgent = cameraAgent;
        this._agentMap = {
            "camera-agent": this._cameraAgent,
        }
    }

    async invoke(agent: string, question: string) {
        if (Object.keys(this._agentMap).includes(agent)) {
            return this._agentMap[agent].invokeAgent(question);
        } else {
            throw new UnknownAgentError(`Agent ${agent} does not exist!`);
        }
    }

    responseText(response: unknown): string | undefined {
        if (typeof response === "string") return response;
        if (!Array.isArray(response)) return undefined;

        const textBlock = response.find((item) => item?.type === "text");
        return typeof textBlock?.text === "string" ? textBlock.text : undefined;
    }
}
