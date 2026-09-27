import { useState, useCallback } from "react";
import { useWebSocket } from "../hooks/webSocketHook";
import ChatMessages from "./ChatMessages";
import styles from "./CameraChat.module.css"

export function CameraChat() {
    const [message, setMessage] = useState("");
    const [history, setHistory] = useState<Record<string, string | boolean>[]>([]);
    const agent = "camera-agent";

    const handleReceiveMessage = useCallback(
        (data: Record<string, unknown>) => {
            if (
                data.type === "response"
                && typeof data.message === "string"
                && typeof data.agent === "string"
            ) {
                const responseMessage = data.message;
                const responseAgent = data.agent;
                setHistory(prev => [...prev, {
                    message: responseMessage,
                    isUser: false,
                    agent: responseAgent,
                }])
            };
        },
        []
    );

    const { send } = useWebSocket(
        import.meta.env.VITE_BACKEND_URL ?? "ws://localhost:8080",
        {
            onMessage: handleReceiveMessage,
            onClose: undefined,
            onOpen: undefined,
            reconnect: true
        }
    );

    const handleSendMessage = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        if (!message.trim()) return;
        send({
            type: agent,
            question: message,
        });
        setHistory(prev => [...prev, { message, isUser: true, agent: agent }]);
        setMessage("");
    };

    return (
        <div className={styles.chatPage}>
            <div className={styles.chatBox}>
                <ChatMessages
                    agent={ agent }
                    message={ message }
                    setMessage={ setMessage }
                    history={ history }
                    handleSendMessage={ handleSendMessage }
                />
            </div>
        </div>
    )
}
