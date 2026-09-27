export interface CameraAgentPort {
    invokeAgent(question: string): Promise<string | undefined | Array<any>>;
}

