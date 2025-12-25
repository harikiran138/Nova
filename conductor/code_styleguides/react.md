# React Style Guide

## 1. Components
*   **Functional Components:** Use functional components with Hooks. Avoid class components.
*   **PascalCase:** Filenames and Component names should be PascalCase.

## 2. Hooks
*   Follow the Rules of Hooks (top level only, dependency arrays).
*   Create custom hooks for reusable logic.

## 3. JSX
*   Use self-closing tags when there are no children.
*   Use fragments `<>` instead of `<div>` wrappers where possible.

## 4. Props
*   Destructure props in the function signature.
*   Use specific types for props, avoid `object`.
