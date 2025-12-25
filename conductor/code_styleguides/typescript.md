# TypeScript Style Guide

## 1. General Principles
*   **Strict Mode:** Enable `strict: true` in `tsconfig.json`.
*   **Explicit Types:** Avoid `any`. Define interfaces or types for all data structures.

## 2. Interfaces vs Types
*   Use `interface` for object definitions and public APIs.
*   Use `type` for unions, intersections, and primitives.

## 3. Async/Await
*   Prefer `async/await` over raw Promises.
*   Always handle errors with `try/catch`.
