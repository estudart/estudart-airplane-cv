import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { speakResponse } from "../services/speech-synthesis.js";


describe(speakResponse.name, () => {
    it("cancels the current speech and speaks one new response", () => {
        const calls: string[] = [];
        const utterance = { text: "What the camera sees" } as SpeechSynthesisUtterance;
        const speechOutput = {
            cancel: () => calls.push("cancel"),
            speak: (received: SpeechSynthesisUtterance) => {
                calls.push("speak");
                assert.equal(received, utterance);
            },
        };

        speakResponse(
            utterance.text,
            speechOutput,
            (text) => {
                assert.equal(text, utterance.text);
                return utterance;
            },
        );

        assert.deepEqual(calls, ["cancel", "speak"]);
    });
});
