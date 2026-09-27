import subprocess
from threading import Lock


class SpeechAdapter:
    def __init__(self, device: str, enabled: bool = True):
        self._device = device
        self._enabled = enabled
        self._speech_lock = Lock()

    def speak(self, text: str) -> None:
        text = str(text).strip()
        if not text:
            print("Did not receive a valid text")
            return

        if not self._enabled:
            print("Speaker is disabled")
            return

        with self._speech_lock:
            subprocess.run([
                "espeak-ng",
                "-d", self._device,
                "-a", "200",
                "-s", "160",
                text
            ])
