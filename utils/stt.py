import threading
import numpy as np
import pyaudio
import noisereduce as nr
from utils.vad import VAD
from utils.asr_fwhisper import ASR_FWhisper

class MicrophoneSTT:
    def __init__(self, sample_rate=16000, chunk_size=1024, model_size="small", device="cpu"):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.model_size = model_size
        self.device = device
        self.channels = 1
        self.transcript = ""
        self._stop_event = threading.Event()
        self._thread = None
        self._init_audio()
        self._init_vad()
        self._init_asr()

    def _init_audio(self):
        self.p = pyaudio.PyAudio()
        device_index = self.p.get_default_input_device_info()['index']
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk_size
        )
        # Capture noise profile at initialization
        print("[STT] Capturing noise profile. Please wait...")
        noise_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
        self.noise_profile = np.frombuffer(noise_data, dtype=np.int16).astype(np.float32)
        print("[STT] Noise profile captured")

    def _init_vad(self):
        self.vad = VAD(self.sample_rate, mode=3)

    def _init_asr(self):
        self.asr = ASR_FWhisper(sample_rate=self.sample_rate, model_size=self.model_size, device=self.device)

    def _is_speech(self, chunk):
        return self.vad.is_speech(chunk)

    def _preprocess_audio(self, audio):
        if len(audio) > 0:
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val * 0.95
            from scipy import signal
            b, a = signal.butter(4, 80/(self.sample_rate/2), btype='high')
            audio = signal.filtfilt(b, a, audio)
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
        return audio

    def _capture_loop(self):
        buffer = []
        silence_counter = 0
        # About 0.8 seconds of silence (adjust as needed)
        silence_threshold = int(self.sample_rate / self.chunk_size * 0.8)
        while not self._stop_event.is_set():
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            chunk = np.frombuffer(data, dtype=np.int16)
            reduced_noise = nr.reduce_noise(
                y=chunk.astype(np.float32),
                sr=self.sample_rate,
                y_noise=self.noise_profile,
                stationary=False,
                n_fft=512,
                prop_decrease=1.0
            )
            reduced_noise_int16 = np.clip(reduced_noise, -32768, 32767).astype(np.int16)
            if self._is_speech(reduced_noise_int16):
                buffer.extend(reduced_noise_int16.tolist())
                silence_counter = 0  # Reset on speech
            elif buffer:
                silence_counter += 1
                if silence_counter > silence_threshold:
                    # End of speech, process buffer
                    audio = np.array(buffer, dtype=np.int16)
                    text = self.asr.transcribe(audio)
                    if text:
                        self.transcript = text
                    buffer = []
                    silence_counter = 0

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'p') and self.p:
            self.p.terminate()

    def get_transcript(self):
        return self.transcript
    

if __name__ == "__main__":
    import time

    # Example usage of MicrophoneSTT
    # You may need to adjust model_size/device as needed
    stt = MicrophoneSTT(model_size="tiny", device="cpu")
    stt.start()
    print("Speak something (Ctrl+C to stop)...")
    try:
        last_transcript = ""
        while True:
            transcript = stt.get_transcript()
            if transcript and transcript != last_transcript:
                print(f"Transcript: {transcript}")
                last_transcript = transcript
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stt.stop()
