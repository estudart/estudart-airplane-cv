import { CameraAgentPort } from "../ports/camera-agent.port.js";
import { SpeakerRestAdapterPort } from "../../infrastructure/ports/speaker-rest-adapter.port.js";
import { UnknownAgentError } from "../errors/unknown-agent.error.js";

export class CameraAssistent {
    _speakerRestAdapter: SpeakerRestAdapterPort;
    _cameraAgent: CameraAgentPort;
    _agentMap: Record<string, CameraAgentPort>;

    constructor(
        speakerRestAdapter: SpeakerRestAdapterPort,
        cameraAgent: CameraAgentPort
    ) {
        this._speakerRestAdapter = speakerRestAdapter;
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

    async speak(text: string): Promise<Boolean> {
        try {
            await this._speakerRestAdapter.speak(text);
            return true
        } catch (error) {
            return false
        }
    }

    responseText(response: unknown): string | undefined {
        if (typeof response === "string") return response;
        if (!Array.isArray(response)) return undefined;

        const textBlock = response.find((item) => item?.type === "text");
        return typeof textBlock?.text === "string" ? textBlock.text : undefined;
    }
}
