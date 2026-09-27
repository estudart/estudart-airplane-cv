export class UnknownAgentError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "UnknownAgentError";
    }
}

