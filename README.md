## Model Context Protocol (MCP) Implementations
A collection of practical MCP (Model Context Protocol) server implementations demonstrating three different approaches to connect AI models with external tools and data sources.


## What is MCP?
Model Context Protocol (MCP) is an open standard that allows AI applications to securely connect with external tools, databases, and services. Think of it as a universal connector between AI models and the real world.

### Repository Structure
This repository contains multiple MCP implementations:

<img width="560" height="167" alt="image" src="https://github.com/user-attachments/assets/c62873e4-c1df-43ad-9ddb-d60f1f06abc5" />

## Key Projects

#### **1. Expense Tracker MCP**
- Folders: expense_tracker_mcp/ and exp-tracker-mcp-with-async/
- A fully functional expense tracking system using MCP protocol that allows AI assistants to:

      Add and manage expenses
      Track spending by category
      Set and monitor budgets
      Generate financial summaries

**Features:**
- Database integration
- Budget management
- Category-based tracking
- Both sync and async implementations

2. Chatbot with MCP
Folder: chatbot_mcp/
An intelligent chatbot that leverages MCP to access external tools and data sources in real-time.
3. LangGraph MCP Client
Folder: client_using_langgraph/
Demonstrates how to build an MCP client using LangGraph for complex agentic workflows.
4. Remote MCP Server
Folder: remote_mcp_server/
Shows how to deploy and connect to MCP servers running remotely for scalable AI applications.
5. Manim MCP Server
Folder: manim-mcp-server/
Integrates Manim (Mathematical Animation Engine) with MCP for generating mathematical animations through AI.
Getting Started
Prerequisites

Python 3.10+
uv package manager (recommended) or pip

Installation

Clone the repository:

bashgit clone https://github.com/sushanttwayana/Model_Context_Protocol-MCP-.git
cd Model_Context_Protocol-MCP-

Install dependencies using uv:

bashuv sync
Or using pip:
bashpip install -r requirements.txt
Quick Start
Try the demo to understand MCP basics:
bashcd start_demo
python main.py
Running Specific Projects
Expense Tracker
bashcd expense_tracker_mcp
python server.py
Chatbot
bashcd chatbot_mcp
python app.py
LangGraph Client
bashcd client_using_langgraph
python client.py
How It Works
MCP follows a client-server architecture:

MCP Server - Exposes tools, resources, and capabilities
MCP Client - Connects AI models to servers
AI Model - Uses tools via MCP to complete tasks

┌──────────┐         ┌─────────────┐         ┌──────────────┐
│ AI Model │ ◄─────► │ MCP Client  │ ◄─────► │  MCP Server  │
└──────────┘         └─────────────┘         └──────────────┘
                                                      │
                                              ┌───────┴────────┐
                                              │ Tools/Database │
                                              └────────────────┘
Use Cases

Personal Finance Management - Track expenses with AI
Conversational AI - Build chatbots with tool access
Data Analysis - Query databases through natural language
Automation - Create AI agents that interact with APIs
Content Generation - Generate animations or visualizations

Technologies Used

Python - Core language
FastMCP - Python MCP framework
LangGraph - Agent orchestration
SQLite - Database for expense tracker
Manim - Mathematical animations

Project Structure Explained
Each folder contains a complete MCP implementation:

server.py or main.py - MCP server implementation
client.py - MCP client (if separate)
requirements.txt - Dependencies
README.md - Project-specific documentation
