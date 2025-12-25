> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# Agent Profiles & Modes

Nova supports different "personas" or profiles to specialize its behavior for different tasks.

## Available Profiles

### 1. General (`general`)
- **Description**: A versatile assistant for everyday tasks.
- **Tools**: All available tools.
- **Sandbox**: Disabled by default.
- **Use Case**: Chatting, simple questions, exploring features.

### 2. Coder (`coder`)
- **Description**: An expert software engineer focused on writing and debugging code.
- **Tools**: File operations (`file.*`), Shell commands (`shell.*`), Web GET (`web.get`).
- **Sandbox**: **Enabled** by default.
- **Use Case**: Building projects, writing scripts, refactoring code.

### 3. Researcher (`researcher`)
- **Description**: A thorough researcher who finds and summarizes information.
- **Tools**: Web tools (`web.*`), File reading/writing (`file.read`, `file.write`).
- **Sandbox**: Disabled by default.
- **Use Case**: Gathering data, summarizing articles, fact-checking.

## Managing Profiles
Profiles are defined in `src/agent_core/profiles.yaml`. You can edit this file to add custom profiles.

### Listing Profiles
```bash
nova agents list
```

### Using a Profile
```bash
nova --agent coder
```
