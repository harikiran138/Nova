# Nova API Setup Guide

To use Nova with Gemini or OpenRouter, you need to "activate" the APIs by setting environment variables.

## Option 1: Quick Activation (Temporary)
Run these commands in your terminal for the current session:

### For Gemini
```bash
export GEMINI_API_KEY=AIzaSyCzgciErD5KbyJLt9ln-I3YkpQmgH6xZ1M
export MODEL_PROVIDER=gemini
```

### For OpenRouter
```bash
export OPENROUTER_API_KEY=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
export MODEL_PROVIDER=openrouter
```

### Back to Local (Ollama)
```bash
export MODEL_PROVIDER=ollama
```

---

## Option 2: Easy Activation Script (Recommended)
I have created a script `activate_nova.sh` in your project root.

**To use Gemini:**
```bash
source activate_nova.sh gemini
```

**To use OpenRouter:**
```bash
source activate_nova.sh openrouter
```

**To use Ollama:**
```bash
source activate_nova.sh ollama
```

---

## Option 3: Permanent Setup
Add the variables to your shell profile (`~/.zshrc` or `~/.bashrc`) so they are always available.

```bash
# Add to ~/.zshrc
export GEMINI_API_KEY=AIzaSyCzgciErD5KbyJLt9ln-I3YkpQmgH6xZ1M
export OPENROUTER_API_KEY=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
# Default Provider
export MODEL_PROVIDER=gemini 
```
Then run `source ~/.zshrc`.
