export const VISION_SOCKET_URL =
    import.meta.env.VITE_VISION_URL ?? "ws://localhost:8000/ws";

export const CAMERA_CONSUMER_URL =
    `${VISION_SOCKET_URL}?subscribeType=camera-data-consumer&detected=true`;
