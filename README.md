# Model Context Protocol (MCP) Implementations

A collection of practical MCP (Model Context Protocol) server implementations demonstrating three different approaches to connect AI models with external tools and data sources.

## What is MCP?

Model Context Protocol (MCP) is an open standard that allows AI applications to securely connect with external tools, databases, and services. Think of it as a universal connector between AI models and the real world.

## 📁 Repository Structure

This repository contains multiple MCP implementations:

<img width="551" height="170" alt="image" src="https://github.com/user-attachments/assets/444a0ab7-17ad-4c01-b13d-0f676b036463" />



## 🚀 Key Projects

### 1. Expense Tracker MCP
**Folders:** `expense_tracker_mcp/` and `exp-tracker-mcp-with-async/`

A fully functional expense tracking system using MCP protocol that allows AI assistants to:
- Add and manage expenses
- Track spending by category
- Set and monitor budgets
- Generate financial summaries

**Features:**
- Database integration
- Budget management
- Category-based tracking
- Both sync and async implementations

### 2. Chatbot with MCP
**Folder:** `chatbot_mcp/`

An intelligent chatbot that leverages MCP to access external tools and data sources in real-time.

### 3. LangGraph MCP Client
**Folder:** `client_using_langgraph/`

Demonstrates how to build an MCP client using LangGraph for complex agentic workflows.

### 4. Remote MCP Server
**Folder:** `remote_mcp_server/`

Shows how to deploy and connect to MCP servers running remotely for scalable AI applications.

### 5. Manim MCP Server
**Folder:** `manim-mcp-server/`

Integrates Manim (Mathematical Animation Engine) with MCP for generating mathematical animations through AI.

## 🏁 Getting Started

### Prerequisites
- Python 3.10+
- uv package manager (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sushanttwayana/Model_Context_Protocol-MCP-.git
cd Model_Context_Protocol-MCP-
```


2. To run any files go through the folder and
```bash
uv sync
uv add fastmcp
pip install fastmcp
```

3. To run any files go through the folder and run these commands
```bash
uv run fastmcp dev main.py
```

4. For running the mcp server in the claude desktpop as well
```bash
uv run fastmcp install claaude--deskptop main.py
```

5. To run Remote MCP Servers
```bash
mcp.run()
or
uv  run main.py
or
fastmcp run server.py --transport http --host 0.0.0.0 --port 8000
```

## How It Works
MCP follows a client-server architecture:

- MCP Server - Exposes tools, resources, and capabilities
- MCP Client - Connects AI models to servers
- AI Model - Uses tools via MCP to complete tasks

<img width="520" height="150" alt="image" src="https://github.com/user-attachments/assets/0be91307-4d1e-48cf-bd94-dc6c070bb72e" />

## Use Cases

- Personal Finance Management - Track expenses with AI
- Conversational AI - Build chatbots with tool access
- Data Analysis - Query databases through natural language
- Automation - Create AI agents that interact with APIs
- Content Generation - Generate animations or visualizations

### Technologies Used

- Python - Core language
- FastMCP - Python MCP framework
- LangGraph - Agent orchestration
- SQLite - Database for expense tracker
- Manim - Mathematical animations

## Project Structure Explained
Each folder contains a complete MCP implementation:

- server.py or main.py - MCP server implementation
- client.py - MCP client (if separate)
- requirements.txt - Dependencies
- README.md - Project-specific documentation


## Configuration
**MCP servers can be configured in your AI client (like Claude Desktop):**

```python
{
  "mcpServers": {
    "expense-tracker": {
      "command": "python",
      "args": ["path/to/expense_tracker_mcp/server.py"]
    }
  }
}
```

