import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import { CameraView } from "./pages/CameraView/CameraView";


createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <CameraView />
  </StrictMode>
);
