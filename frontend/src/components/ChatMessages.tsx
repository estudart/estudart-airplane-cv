import styles from "./CameraChat.module.css"

interface ChatProps {
    agent: string;
    message: string;
    setMessage: React.Dispatch<React.SetStateAction<string>>;
    history: Record<string, string | boolean>[];
    handleSendMessage: (event: React.FormEvent<HTMLFormElement>) => void;
}

export default function ChatMessages(
    { agent, message, setMessage, history, handleSendMessage }: ChatProps) {
    return (
        <div className={styles.chatMessages}>
            <div className={styles.chatHistory}>
                {history.map((data, index) =>
                    data.agent === agent &&
                    <div key={index} className={data.isUser ? styles.userMessageContainer : styles.agentMessageContainer}>
                        <p className={data.isUser ? styles.userMessage : styles.agentMessage}>
                            {data.message}
                        </p>
                    </div>
                )}
            </div>
            <form
                className={styles.chatText}
                onSubmit={handleSendMessage}
            >
                <input
                    type="text"
                    className={styles.chatInputBox}
                    placeholder="Ask about the latest camera frame!"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                />
                <button 
                    className={styles.chatButton}
                    type="submit"
                >
                    Send
                </button>
            </form>
        </div>
    )
}