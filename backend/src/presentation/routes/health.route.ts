import { Router } from "express";


const healthRoutes = Router();

healthRoutes.get("/health", (_request, response) => {
    response.json({ status: "healthy", service: "backend" });
});

export default healthRoutes;

