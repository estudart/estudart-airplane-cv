import express, { Request, Response } from "express"

import { cameraAssistent } from "../../dependencies.js";

const cameraAssistentRoutes = express.Router()

cameraAssistentRoutes.post('/camera-assistent', async (req: Request, res: Response) => {
    try {
        const agentAnswer = await cameraAssistent.invoke(
            "camera-agent",
            req.body.question,
        );
        const responseMessage = cameraAssistent.responseText(agentAnswer);
        res.send(responseMessage ?? "");
    } catch (error) {
        res.status(400).send(String(error));
    }
});

export default cameraAssistentRoutes;
