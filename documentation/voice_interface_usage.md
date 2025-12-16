# Voice Interface Usage

Nova supports voice input for hands-free interaction.

## Prerequisites
1.  **Microphone**: A working audio input device.
2.  **Libraries**:
    - `SpeechRecognition` (Python package)
    - `PyAudio` (System dependency, optional but recommended)

## How to Use
1.  Start Nova TUI: `nova ui`
2.  Press `Ctrl+J`.
3.  Speak your command clearly.
4.  Wait for transcription. The text will appear in the input box.
5.  Press `Enter` to send.

## Troubleshooting
If voice input fails:
- Check your microphone settings.
- Install system audio libraries:
    - **Mac**: `brew install portaudio` then `pip install pyaudio`
    - **Linux**: `sudo apt-get install python3-pyaudio`
