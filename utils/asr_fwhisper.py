from faster_whisper import WhisperModel
import numpy as np
import traceback
import re

def is_repetitive_phrase(text, min_phrase_len=2, max_phrase_len=5, min_repeats=3):
    # Remove all punctuation
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    n = len(words)
    for phrase_len in range(min_phrase_len, max_phrase_len+1):
        if n < phrase_len * min_repeats:
            continue
        for start in range(n - phrase_len * min_repeats + 1):
            phrase = words[start:start+phrase_len]
            count = 1
            idx = start + phrase_len
            while idx + phrase_len <= n and words[idx:idx+phrase_len] == phrase:
                count += 1
                idx += phrase_len
            if count >= min_repeats:
                return True
    return False

class ASR_FWhisper:
    _model_cache = {}  # (model_size, device) -> WhisperModel

    def __init__(self, sample_rate=16000, model_path="", model_size="medium", device="cpu"):
        self.sample_rate = sample_rate
        self.model_size = model_size
        self.device = device
        key = (self.model_size, self.device)
        if key in ASR_FWhisper._model_cache:
            self.whisper_model = ASR_FWhisper._model_cache[key]
        else:
            # Use optimal compute type for best performance
            compute_type = "float16" if device == "cuda" else "int8"
            print(f"Loading Whisper model: {model_size} on {device}")
            self.whisper_model = WhisperModel(self.model_size, device=self.device, compute_type=compute_type)
            ASR_FWhisper._model_cache[key] = self.whisper_model
            print("Whisper model loaded successfully")

    def _preprocess_audio(self, audio):
        """Preprocess audio for optimal Whisper performance."""
        if len(audio) > 0:
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                audio = audio / max_val * 0.95  # Leave headroom
            
            # Apply high-pass filter to remove low-frequency noise
            from scipy import signal
            b, a = signal.butter(4, 80/(self.sample_rate/2), btype='high')
            audio = signal.filtfilt(b, a, audio)
            
            # Ensure audio is in float32 range [-1, 1]
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
        return audio

    def transcribe(self, chunk):
        """
        Accepts a complete speech chunk (np.int16) and transcribes it.
        No buffering needed - process the chunk directly.
        """
        if not isinstance(chunk, np.ndarray) or chunk.dtype != np.int16:
            raise ValueError("Input chunk must be a numpy array of dtype int16")
        
        try:
            # Preprocess the chunk directly
            processed_audio = self._preprocess_audio(chunk)
            
            # Transcribe with Whisper
            segments, info = self.whisper_model.transcribe(
                processed_audio,
                language="en",
                beam_size=20,                # Higher for best accuracy
                best_of=20,                  # Higher for best accuracy
                temperature=0.0,             # Deterministic, best for accuracy
                condition_on_previous_text=True,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=1000,  # Shorter for more segments, longer for fewer
                    speech_pad_ms=100,
                    threshold=0.7
                ),
                word_timestamps=True,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.7
            )
            
            # Collect high-confidence segments
            results = []
            for segment in segments:
                print(f"[ASR_FWhisper] Segment: '{segment.text.strip()}' | avg_logprob: {segment.avg_logprob}")
                if segment.avg_logprob > -1.0 and segment.text.strip():
                    results.append(segment.text.strip())
                else:
                    print(f"[ASR_FWhisper] Filtered out segment: '{segment.text.strip()}' | avg_logprob: {segment.avg_logprob}")
            
            # Return the transcription
            text = " ".join(results).strip()
            if text and is_repetitive_phrase(text):
                print(f"[ASR_FWhisper] Ignored repetitive phrase: {text}")
                return ""
            return text
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            traceback.print_exc()
            return "" 