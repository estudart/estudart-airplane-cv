export interface MCPPort {
    listTools(): Promise<Record<string, any>[]>;
    callTool(toolName: string, args: Record<string, string>): any;
}

