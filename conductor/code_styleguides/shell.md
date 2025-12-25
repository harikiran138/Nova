# Shell Script Style Guide

## 1. General
*   **Shebang:** Always start with `#!/bin/bash` (or appropriate shell).
*   **Extension:** Use `.sh` extension.
*   **Permissions:** Ensure scripts are executable (`chmod +x`).

## 2. Safety
*   Use `set -euo pipefail` at the start of scripts to fail fast on errors.
*   Quote all variables to prevent word splitting.

## 3. Naming
*   `snake_case` for variables and functions.
*   `UPPER_CASE` for exported environment variables.
