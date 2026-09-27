import { useCallback, useState } from "react";

import { useWebSocket } from "../hooks/webSocketHook";
import styles from "./CameraStream.module.css";


export function CameraStream() {
    const [frame, setFrame] = useState("");
    const [status, setStatus] = useState("connecting");
    const websocketUrl = import.meta.env.VITE_BACKEND_URL ?? "ws://localhost:8080";

    const handleMessage = useCallback((data: Record<string, unknown>) => {
        if (data.type === "camera-frame" && typeof data.frame === "string") {
            setFrame(`data:image/jpeg;base64,${data.frame.trim()}`);
        }
    }, []);

    const handleOpen = useCallback(() => setStatus("connected"), []);
    const handleClose = useCallback(() => setStatus("reconnecting"), []);

    useWebSocket(
        `${websocketUrl}?subscribeType=camera-data-consumer&detected=true`,
        {
            onMessage: handleMessage,
            onOpen: handleOpen,
            onClose: handleClose,
            reconnect: true,
        }
    );

    return (
        <section className={styles.cameraStream}>
            <section className={styles.cameraView} aria-live="polite">
                {frame ? (
                    <img
                        className={styles.cameraFrame}
                        src={frame}
                        alt="Detected camera stream"
                    />
                ) : (
                    <p>Waiting for detected camera frames…</p>
                )}
            </section>
            <small className={styles.status}>{status}</small>
        </section>
    );
}

