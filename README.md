# GitHub Repo Explainer MCP

An MCP server that gives AI assistants like GitHub Copilot and Cursor **live access to any GitHub repository** — without cloning it first.

Ask your AI questions like:
- *"What does this repo do?"*
- *"What changed in the last 7 days?"*
- *"Are any dependencies outdated?"*
- *"Explain this specific file"*

And get answers backed by **real-time GitHub data**, not stale training data.

---

## Why this is different from Cursor or Copilot alone

| | Cursor / Copilot alone | This MCP server |
|---|---|---|
| Explain code | ✅ Local files only | ✅ Any repo, anywhere |
| Live GitHub data | ❌ | ✅ Stars, forks, activity |
| Recent commits & PRs | ❌ | ✅ Last N days |
| Dependency audit | ❌ | ✅ Checks PyPI live |
| Private repos | ❌ | ✅ With your token |
| No cloning needed | ❌ | ✅ |

---

## Tools

| Tool | What it does |
|---|---|
| `summarize_repo` | Summarizes a repo's purpose, structure, language, and key files |
| `explain_file` | Fetches and explains a specific file in any repo |
| `ask_repo` | Answers any freeform question about a repo |
| `recent_changes` | Shows commits and merged PRs from the last N days |
| `analyze_dependencies` | Lists dependencies and flags outdated packages via PyPI |

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/Pranavvr/Repo_Explainer_MCP.git
cd Repo_Explainer_MCP
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up your GitHub token

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then open `.env` and add your token:

```
GITHUB_TOKEN=your_github_token_here
```

> Get a token at [github.com/settings/tokens](https://github.com/settings/tokens). Only `repo` read scope needed.

### 4. Connect to VS Code

Open your MCP config file:

`Cmd + Shift + P` → `MCP: Open User MCP Configuration`

Add this:

```json
{
  "servers": {
    "github-repo-explainer": {
      "command": "python3",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

Replace the path with your actual path. Get it by running `pwd` in your project folder.

### 5. Restart VS Code and start asking questions

Open GitHub Copilot chat and try:

```
What does fastapi/fastapi do?
```

```
What changed in vercel/next.js in the last 7 days?
```

```
Are the dependencies in YOUR_USERNAME/YOUR_REPO outdated?
```

---

## Testing with MCP Inspector

To test your tools without an AI client:

```bash
npx @modelcontextprotocol/inspector python3 server.py
```

Opens a browser UI where you can call each tool manually.

---

## Project structure

```
github-repo-explainer-mcp/
├── server.py          # MCP server — defines and exposes the 5 tools
├── github_client.py   # GitHub API wrapper — all data fetching logic
├── .env               # Your GitHub token (never committed)
├── .env.example       # Token template for others
├── requirements.txt   # Dependencies
└── README.md
```

---

## Requirements

- Python 3.10+
- GitHub Personal Access Token (free, read-only scope)
- VS Code 1.99+ with GitHub Copilot, or any MCP-compatible client

---

## Built with

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — MCP server framework
- [PyGithub](https://github.com/PyGithub/PyGithub) — GitHub API client
- [python-dotenv](https://github.com/theskumar/python-dotenv) — environment variable management

---

## License

MIT