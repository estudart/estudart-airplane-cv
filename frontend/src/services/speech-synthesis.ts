export interface SpeechOutput {
    cancel: () => void;
    speak: (utterance: SpeechSynthesisUtterance) => void;
}

export function speakResponse(
    responseMessage: string,
    speechOutput: SpeechOutput,
    createUtterance: (text: string) => SpeechSynthesisUtterance,
) {
    speechOutput.cancel();
    speechOutput.speak(createUtterance(responseMessage));
}
