import webrtcvad
import numpy as np

class VAD:
    def __init__(self, sample_rate=16000, mode=1, frame_duration=30):
        self.vad = webrtcvad.Vad(mode)
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        self.debug = False  # Toggle for debug output

    def is_speech(self, chunk):
        '''Returns True if speech is detected in the chunk. Checks all frames.'''
        if len(chunk) < self.frame_size:
            print(f"[VAD] Chunk too short: {len(chunk)} < {self.frame_size}")
            return False
        
        num_frames = len(chunk) // self.frame_size
        speech_detected = False
        
        for i in range(num_frames):
            frame = chunk[i*self.frame_size:(i+1)*self.frame_size]
            if self.vad.is_speech(frame.tobytes(), self.sample_rate):
                speech_detected = True
                break

        if self.debug:
            print(f"[VAD] is_speech={speech_detected} | chunk len={len(chunk)}")

        return speech_detected


if __name__ == '__main__':
    from Live_Caption import capture_mic
    ac = capture_mic.AudioCapture()
    vad = VAD()
    for chunk in ac.chunks():
        print('Speech:', vad.is_speech(chunk)) 