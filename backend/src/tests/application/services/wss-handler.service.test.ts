import WebSocket from "ws";
import { after, before, describe, it } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import express, { Application } from "express";
import { AddressInfo } from "node:net";
import { Stream } from "node:stream";
import { IncomingMessage } from "node:http";

import { CameraAssistent } from "../../../application/services/camera-assistent.service.js";
import { WebSocketService } from "../../../application/services/wss-handler.service.js";


describe(WebSocketService.name, () => {
    let port: number;
    let app: Application;
    let server: http.Server;
    let service: WebSocketService;
    let spokenMessage = "";

    before(async () => {
        app = express();
        server = http.createServer(app);
        const cameraAgent = {
            async invokeAgent(question: string) {
                return [{ type: "text", text: "CameraAgent: " + question }];
            },
        };
        const speakerRestAdapter = {
            async speak(text: string) {
                spokenMessage = text;
            },
        };
        const cameraAssistent = new CameraAssistent(
            speakerRestAdapter,
            cameraAgent,
        );
        service = new WebSocketService(cameraAssistent);

        server.on("upgrade", (
            request: IncomingMessage,
            socket: Stream.Duplex,
            upgradeHead: Buffer,
        ) => {
            service.handleUpgrade(request, socket, upgradeHead);
        });

        await new Promise<void>((resolve) => server.listen(0, resolve));
        port = (server.address() as AddressInfo).port;
    });

    after(async () => {
        service._wss.clients.forEach((client) => client.terminate());
        await new Promise<void>((resolve) => server.close(() => resolve()));
    });

    it("streams camera frames to detected consumers", async () => {
        const consumer = new WebSocket(
            `ws://localhost:${port}?subscribeType=camera-data-consumer&detected=true`
        );
        const producer = new WebSocket(`ws://localhost:${port}`);

        await Promise.all([
            new Promise<void>((resolve) => consumer.once("open", resolve)),
            new Promise<void>((resolve) => producer.once("open", resolve)),
        ]);

        const frame = await new Promise<string>((resolve, reject) => {
            consumer.once("message", (message) => {
                resolve(JSON.parse(message.toString()).frame);
            });
            producer.send(JSON.stringify({ type: "camera-frame", message: "frame-b64" }));
            setTimeout(() => reject(new Error("Camera frame was not streamed")), 2000);
        });

        consumer.close();
        producer.close();
        assert.equal(frame, "frame-b64");
    });

    it("answers CameraAgent messages and sends the answer to speaker", async () => {
        const chat = new WebSocket("ws://localhost:" + port);
        await new Promise<void>((resolve) => chat.once("open", resolve));

        const answer = await new Promise<string>((resolve, reject) => {
            chat.once("message", (message) => {
                resolve(JSON.parse(message.toString()).message);
            });
            chat.send(JSON.stringify({ type: "camera-agent", question: "What do you see?" }));
            setTimeout(() => reject(new Error("CameraAgent did not answer")), 2000);
        });

        chat.close();
        assert.equal(answer, "CameraAgent: What do you see?");
        assert.equal(spokenMessage, answer);
    });

    it("does not subscribe consumers without detected=true", async () => {
        const consumer = new WebSocket(
            `ws://localhost:${port}?subscribeType=camera-data-consumer`
        );

        await new Promise<void>((resolve) => consumer.once("open", resolve));
        assert.equal(service._connections.includes(consumer), false);
        consumer.close();
    });
});
