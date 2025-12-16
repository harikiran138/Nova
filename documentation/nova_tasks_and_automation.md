# Tasks & Automation

Nova can automate various non-coding tasks using its toolset.

## Research & Content
Nova can browse the web (via DuckDuckGo) and summarize information.

**Example:**
```bash
nova --agent researcher task run "Research the latest features of Python 3.12 and write a summary to python_312.md"
```

## System Automation
Nova can use shell commands to automate system tasks.

**Example:**
```bash
nova task run "Organize the Downloads folder by moving images to Pictures and docs to Documents"
```
*(Note: Requires `--no-sandbox` to access real user folders)*

## Data Processing
With Python libraries installed, Nova can process data.

**Example:**
```bash
nova code "Read data.csv and calculate the average age"
```

## Task Management
View the status of your tasks:
```bash
nova task status
```
*(Feature in development: Persistence of task history)*
