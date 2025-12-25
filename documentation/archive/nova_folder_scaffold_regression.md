> **ARCHIVED**: Superseded by [Project_Overview.md](../Project_Overview.md) on 2025-12-25.

# Nova Folder Scaffold Regression Report

## Summary
**Status**: ✅ FIXED
**Date**: 2025-11-28
**Component**: Tool Layer & Agent Loop

## Issue
Nova was failing to create folders and scaffold projects because:
1.  Missing directory tools (`file.mkdir`, `file.makedirs`).
2.  Agent was hallucinating tool names (`mkdir`, `file.make_dirs`).
3.  Agent was nesting tool calls inside `shell.run` arguments.

## Fix Implementation
1.  **New Tools**: Added `FileMkdirTool` and `FileMakedirsTool` to `src/agent_core/tools/file.py`.
2.  **Registry Updates**: Registered new tools and added aliases (e.g., `file.make_dirs` -> `file.makedirs`) in `src/agent_core/tools/registry.py`.
3.  **Safety**: Added validation to `src/agent_core/tools/shell.py` to reject nested JSON tool calls.
4.  **Prompts**: Updated `src/agent_core/agent_loop.py` and `profiles.yaml` to explicitly forbid nesting and provide examples for directory tools.

## Verification
### Automated Regression Tests
Run `pytest tests/test_scaffold_regression.py`:
- ✅ `test_file_mkdir`: Verified directory creation.
- ✅ `test_file_makedirs`: Verified nested directory creation.
- ✅ `test_shell_run_rejects_nested_json`: Verified rejection of nested tools.

### Manual End-to-End Test
Command: `nova run "create a folder have small samplet of html css and js files about collage name that collage ncollage folder name is also same"`

**Result**:
- Folder `Ncollage` created.
- Subfolders `html`, `css`, `js` created.
- Files `index.html`, `style.css`, `script.js` created.

## Conclusion
The agent can now reliably scaffold web projects and handle directory creation tasks without hallucinating or using invalid syntax.
