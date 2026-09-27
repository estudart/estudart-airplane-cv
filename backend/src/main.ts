import http from "node:http";
import { Stream } from "node:stream";
import { IncomingMessage } from "node:http";
import express, { Application } from "express";
import cors from "cors";

import { webSocketService } from "./dependencies.js";
import cameraAssistentRoutes from "./presentation/routes/agent.route.js";
import healthRoutes from "./presentation/routes/health.route.js";


export const port: number = Number(process.env.API_PORT) || 8080;
export const app: Application = express();
export const server: http.Server = http.createServer(app);

app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cameraAssistentRoutes);
app.use(healthRoutes);

server.on("upgrade", (
    request: IncomingMessage,
    socket: Stream.Duplex,
    upgradeHead: Buffer,
) => {
    webSocketService.handleUpgrade(request, socket, upgradeHead);
});

server.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

