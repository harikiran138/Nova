from setuptools import setup, find_packages

setup(
    name="nova-agent-cli",
    version="2.0.0",
    description="Local AI Agent CLI powered by Ollama",
    author="Nova Team",
    packages=find_packages(include=["src", "src.*"]),
    # py_modules=["nova_cli"],
    install_requires=[
        "click>=8.0.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "faker>=19.0.0",
        "qrcode>=7.0",
        "pypdf>=3.0.0",
        "duckduckgo-search>=3.8.0",
        "beautifulsoup4>=4.12.0",
        "yfinance>=0.2.0",
        "textual>=0.40.0",
        "SpeechRecognition>=3.10.0",
        "chromadb>=0.4.0",  # RAG
        "docker>=6.1.0",    # Docker Sandbox
        "psutil>=5.9.0",    # System Tools
        "fastapi>=0.109.0", # API
        "uvicorn>=0.27.0",  # ASGI Server
        "langchain>=0.1.0", # LLM Framework
        "langchain-community>=0.0.10",
        "langchain-mongodb>=0.1.0",
        "pymongo>=4.6.0",   # MongoDB Driver
    ],
    entry_points={
        "console_scripts": [
            "nova=src.nova_cli:main",
        ],
    },
    python_requires=">=3.8",
)
