export interface SpeakerRestAdapterPort {
    speak(text: string): Promise<unknown>;
}

