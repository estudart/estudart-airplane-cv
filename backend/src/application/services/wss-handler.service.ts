import { WebSocketServer, WebSocket } from "ws";
import { Stream } from "node:stream";
import { IncomingMessage } from "node:http";
import { CameraAssistent } from "./camera-assistent.service.js";
import { UnknownAgentError } from "../errors/unknown-agent.error.js";


export class WebSocketService {
    _wss: WebSocketServer;
    _cameraAssistent: CameraAssistent;
    _connections: WebSocket[];

    constructor(
        cameraAssistent: CameraAssistent,
    ) {
        this._wss = new WebSocketServer({ noServer: true });
        this._cameraAssistent = cameraAssistent;
        this.setEventHandlers();
        this._connections = [];
    }

    setEventHandlers() {
        this._wss.on("connection", (ws: WebSocket, request: IncomingMessage) => {
            const urlParams = new URL(request.url || '', 'http://localhost').searchParams;

            if (
                urlParams.get("subscribeType") === "camera-data-consumer"
                && urlParams.get("detected") === "true"
            ) {
                this._connections.push(ws);
            }

            console.log("New client connected");

            ws.on("message", async (message) => {
                let response;
                try {
                    const data = JSON.parse(message.toString());
                    const dataType = data.type;
                    if (dataType === "camera-frame") {
                        if (this._connections.length) {
                            this._connections.forEach((connection) => {
                                if (connection.readyState === WebSocket.OPEN) {
                                    connection.send(JSON.stringify({ type: dataType, frame: data.message }))
                                }
                            })
                        }
                    } else {
                        const agent = dataType;
                        const question = data.question;

                        response = await this._cameraAssistent.invoke(agent, question);
                        const responseMessage = this._cameraAssistent.responseText(response);
                        if (responseMessage !== undefined) {
                            await this._cameraAssistent.speak(responseMessage);
                            ws.send(JSON.stringify({ type: "response", message: responseMessage, agent }))
                        }
                    };
                } catch (error) {
                    if (error instanceof UnknownAgentError) {
                        ws.send(JSON.stringify({
                            type: "error",
                            message: `${error}`
                        }));
                    } else {
                        ws.send(JSON.stringify({
                            type: "error",
                            message: `${error}`
                        }));
                    }
                };
            });

            ws.on('close', () => {
                this._connections = this._connections.filter(
                    (connection) => connection !== ws
                );
                console.log("Connection closed");
            });
        })
    }

    handleUpgrade(request: IncomingMessage, socket: Stream.Duplex, upgradeHead: Buffer) {
        this._wss.handleUpgrade(request, socket, upgradeHead, (ws) => {
            this._wss.emit('connection', ws, request);
        }) 
    }

}
