# Nova TUI Overview

Nova v2 introduces a beautiful, interactive Terminal User Interface (TUI) powered by Textual.

## Features
- **Amp-Style Design**: Glowing text, dark theme, and ASCII art.
- **Command Palette**: Press `Ctrl+O` to toggle the tool panel.
- **Voice Input**: Press `Ctrl+J` to speak your command (requires microphone).
- **Real-time Streaming**: Watch the agent think and respond in real-time.
- **Tool Visualization**: See which tools are being used in the side panel.

## Usage
To start the TUI:
```bash
nova ui
```

To start with a specific agent:
```bash
nova --agent coder ui
```

## Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Quit | `Ctrl+C` |
| Toggle Tools | `Ctrl+O` |
| Voice Input | `Ctrl+J` |
| Submit Message | `Enter` |

## Troubleshooting
- **Voice not working?**: Ensure you have a working microphone and `portaudio` installed (system dependent).
- **Display issues?**: Use a terminal with TrueColor support (e.g., iTerm2, Windows Terminal).
