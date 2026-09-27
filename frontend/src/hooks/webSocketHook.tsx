import { useCallback, useEffect, useRef } from "react";


export type WebSocketOptions = {
    onMessage: (data: Record<string, unknown>) => void;
    onOpen?: () => void;
    onClose?: (event: CloseEvent) => void;
    reconnect: boolean;
};

export function useWebSocket(url: string, options: WebSocketOptions) {
    const { onMessage, onOpen, onClose, reconnect = true } = options;
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimer = useRef<number | undefined>(undefined);
    const attemptRef = useRef(0);
    const connectRef = useRef<() => void>(() => undefined);

    const connect = useCallback(() => {
        const socket = new WebSocket(url);
        wsRef.current = socket;

        socket.onopen = () => {
            attemptRef.current = 0;
            onOpen?.();
        };

        socket.onmessage = (event) => {
            onMessage(JSON.parse(event.data));
        };

        socket.onclose = (event) => {
            onClose?.(event);
            if (reconnect && event.code !== 1000) {
                const attempt = attemptRef.current;
                if (attempt >= 10) return;

                const baseDelay = Math.min(1000 * 2 ** attempt, 30000);
                const jitter = Math.random() * 1000;
                reconnectTimer.current = window.setTimeout(() => {
                    attemptRef.current += 1;
                    connectRef.current();
                }, baseDelay + jitter);
            }
        };
    }, [url, onMessage, onOpen, onClose, reconnect]);

    useEffect(() => {
        connectRef.current = connect;
        connect();
        return () => {
            window.clearTimeout(reconnectTimer.current);
            wsRef.current?.close(1000, "hook cleanup");
        };
    }, [connect]);

    const send = useCallback((data: Record<string, unknown>) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
        }
    }, []);

    return { send, wsRef };
}

