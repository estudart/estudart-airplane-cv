import axios from "axios";

import { SpeakerRestAdapterPort } from "./ports/speaker-rest-adapter.port.js";


export class SpeakerError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "SpeakerError";
    }
}

export class SpeakerRestAdapter implements SpeakerRestAdapterPort {
    _apiClientUrl: string;

    constructor(apiClientUrl: string) {
        this._apiClientUrl = apiClientUrl;
    }

    async speak(text: string) {
        try {
            const { data } = await axios.post(
                `${this._apiClientUrl}/speak`,
                undefined,
                { params: { text } },
            );
            return data;
        } catch (error) {
            throw new SpeakerError(`Could not speak text: ${error}`);
        }
    }
}
