> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# Nova UI Design System

## Philosophy
Nova's UI is designed to be **futuristic, minimal, and information-dense**. It draws inspiration from cyberpunk aesthetics and modern developer tools like Amp.

## Color Palette (Nova-Blue)
- **Primary**: `#00aeff` (Electric Blue)
- **Secondary**: `#0077cc` (Deep Blue)
- **Accent**: `#00ff9d` (Cyber Green)
- **Background**: `#0a0a12` (Deep Space)
- **Surface**: `#151520` (Panel BG)

## Layout
The TUI uses a split-pane layout:
- **Left (66%)**: Chat Interface. Scrollable history + Multi-line input.
- **Right (33%)**: Context Panel. Active tools, file tree, or documentation.
- **Bottom**: Status Bar. Real-time indicators for Model, Git, and Sandbox.

## Components
### Command Palette (Ctrl+P)
A modal dialog for quick actions. Supports fuzzy search.
- `Switch Model`
- `Toggle Sandbox`
- `Clear Chat`

### Status Bar
Displays:
- 🤖 Model Name
- 👤 Agent Profile
- 🛠️ Active Tool Count
- 🔒 Sandbox Status (Safe/Unsafe)
- 📂 Current Workspace
