# Improvement Todo List

While Nova is fully functional, the following improvements are recommended for v1.2:

1.  **Async Agent Loop**: Refactor `AgentLoop` to be fully asynchronous to prevent UI blocking during long tool executions.
2.  **Git Integration**: Improve `git` tools to handle non-repo directories more gracefully (e.g., auto-init or prompt).
3.  **Planner Robustness**: Fix the JSON parsing issue in `Planner` when the model outputs markdown-wrapped JSON.
4.  **Task Persistence**: Save task history to a database (SQLite/JSON) to allow resuming tasks across sessions.
5.  **Voice Feedback**: Add text-to-speech (TTS) for full voice interaction.
