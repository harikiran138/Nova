> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# Nova Coding Capabilities

Nova is designed to be a capable pair programmer.

## Coding Tools
- **`file.read(path)`**: Read file contents.
- **`file.write(path, content)`**: Create or overwrite files.
- **`file.patch(path, target, replacement)`**: Surgically edit code without rewriting the whole file.
- **`search.code(query)`**: Grep/Search for code patterns.
- **`git.status`, `git.diff`, `git.commit`**: Manage version control.

## Workflows

### 1. Refactoring
```bash
nova code "Refactor src/main.py to use a class structure"
```
Nova will:
1.  Read `src/main.py`.
2.  Plan the refactor.
3.  Use `file.write` or `file.patch` to apply changes.
4.  (Optional) Run tests if asked.

### 2. Feature Implementation
```bash
nova code "Add a new endpoint /health to api.py"
```
Nova will:
1.  Locate `api.py`.
2.  Add the new endpoint code.
3.  Verify the file content.

### 3. Code Review & Explanation
```bash
nova ask "Explain the logic in src/auth.py"
```
Nova will read the file and explain it.

## Safety
By default, `nova code` runs in **Sandbox Mode** (`~/.nova/sandbox`).
To run on your actual project files, use:
```bash
nova --no-sandbox code "Fix the bug in main.py"
```
**Warning**: Always use version control when running without sandbox.
