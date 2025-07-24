from utils.stt import MicrophoneSTT
import time

def listen_for_command(handle_transcribe, model_size="medium", device="cpu"):
    """
    Listen for a voice command using the MicrophoneSTT class.
    """
    stt = MicrophoneSTT(model_size=model_size, device=device)
    stt.start()
    print("Please speak your command...")
    print("Speak something (Ctrl+C to stop)...")
    try:
        last_transcript = ""
        while True:
            transcript = stt.get_transcript()
            if transcript and transcript != last_transcript:
                print(f"Transcript: {transcript}")
                handle_transcribe(transcript)
                last_transcript = transcript
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stt.stop()