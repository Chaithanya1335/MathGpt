# 🧮 MathGPT - Intelligent Mathematics Tutor

An advanced Agentic-RAG (Retrieval-Augmented Generation) system that provides intelligent mathematics tutoring with step-by-step problem solving, visual diagram generation, and comprehensive explanations.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Components](#components)
- [API Keys Required](#api-keys-required)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

MathGPT is an intelligent mathematics tutoring system that combines:
- **Internal Knowledge Base**: Curated mathematics content from NCERT Class 12 textbooks
- **External Web Search**: Latest information from the internet when needed
- **AI Reasoning**: Step-by-step problem solving with clear explanations
- **Visual Diagram Generation**: Automatic generation of mathematical diagrams when required
- **Safety Guardrails**: Input and output validation for secure and appropriate responses

The system uses CrewAI for agent orchestration, Gemini 2.5 Flash for language understanding, and Qdrant for vector storage and retrieval.

## ✨ Features

### Core Capabilities
- 🔍 **Intelligent Document Retrieval**: Searches internal knowledge base first, then web if needed
- 📊 **Visual Diagram Generation**: Automatically generates mathematical diagrams (vectors, graphs, geometric shapes)
- 📝 **Step-by-Step Solutions**: Clear, structured explanations with LaTeX math notation
- 🛡️ **Input/Output Guardrails**: Privacy protection, content filtering, and quality validation
- 🎨 **Beautiful Web Interface**: Modern Streamlit-based UI with responsive design
- 🧠 **Agentic Reasoning**: Advanced reasoning capabilities for complex problem solving

### Supported Math Topics
- Algebra and Equations
- Calculus (Differentiation, Integration)
- Trigonometry
- Geometry and Vectors
- Linear Algebra (Matrices, Determinants)
- Probability and Statistics
- Differential Equations
- And more from NCERT Class 12 syllabus

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│                  (User Interface)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Input Guardrails                        │
│           (Privacy & Content Validation)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    MathAgent                             │
│              (CrewAI Agent Orchestration)                │
└──────┬──────────────────┬──────────────────┬────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Knowledge  │  │ Diagram Tool │  │ Web Search   │
│  Base (KB)  │  │ (Matplotlib) │  │ (Tavily)     │
│  Retriever  │  │              │  │              │
└──────┬──────┘  └──────────────┘  └──────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              Vector Database (Qdrant)                   │
│        (Embeddings: sentence-transformers)              │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Core Frameworks
- **CrewAI**: Agent orchestration and task management
- **LangChain**: LLM framework and tool integration
- **Streamlit**: Web application framework
- **Qdrant**: Vector database for semantic search
- **Google Gemini 2.5 Flash**: Large Language Model

### Supporting Libraries
- **sentence-transformers**: Embedding model for semantic search
- **matplotlib**: Diagram and visualization generation
- **pypdf**: PDF document processing
- **Tavily**: Web search API
- **pydantic**: Data validation and settings management

### MCP (Model Context Protocol)
- **langchain-mcp-adapters**: Integration with MCP servers
- Custom MCP servers for tool communication

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API keys for required services (see [API Keys Required](#api-keys-required))

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd "New folder"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Package in Development Mode
```bash
pip install -e .
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Google Gemini API Key
Gemini_Api_Key=your_gemini_api_key_here

# Qdrant Cloud API Key
Qdrant_Api_Key=your_qdrant_api_key_here

# Tavily Search API Key
Tavily_Api_Key=your_tavily_api_key_here
```

### Vector Database Setup

The system uses Qdrant Cloud for vector storage. The connection details are configured in `src/utils.py`. If you need to initialize the vector database with your own documents:

1. Place PDF files in the `Data/` directory
2. Run the vector database initialization:
```python
from src.knowledgebase.VectorDB import VectorDB
vector_db = VectorDB(initialize=True)
```

## 🚀 Usage

### Running the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Math Agent Programmatically

```python
import asyncio
from src.agent.math_agent import MathAgent

async def main():
    math_agent = MathAgent()
    agent = await math_agent.create_agent()
    
    response = await math_agent.run_agent(
        "Solve the quadratic equation x² + 5x + 6 = 0"
    )
    print(response)
    
    math_agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example Queries

- **Algebraic Problems**: "Solve x² + 5x + 6 = 0"
- **Calculus**: "Find the derivative of sin(x)cos(x)"
- **Geometry**: "Explain the Pythagorean theorem"
- **Visual Requests**: "Draw a vector diagram showing 40 km displacement 30° east of north"
- **Theory**: "Explain the chain rule in calculus"

## 📁 Project Structure

```
.
├── app.py                      # Main Streamlit application
├── setup.py                    # Package setup configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/                        # Source code directory
│   ├── __init__.py
│   ├── utils.py                # Utility functions (LLM, embeddings, MCP client)
│   │
│   ├── agent/                  # Agent implementation
│   │   ├── __init__.py
│   │   └── math_agent.py       # Main MathAgent class
│   │
│   ├── tools/                  # CrewAI tools
│   │   ├── Retriever_Tool.py   # Knowledge base retrieval tool
│   │   └── Diagram_Tool.py     # Mathematical diagram generation
│   │
│   ├── knowledgebase/          # Vector database management
│   │   ├── __init__.py
│   │   └── VectorDB.py         # Qdrant vector store wrapper
│   │
│   ├── data_loader/            # Document loading utilities
│   │   ├── __init__.py
│   │   └── data_loader.py      # PDF document loader
│   │
│   └── guardrails/             # Safety and validation
│       ├── __init__.py
│       ├── input_guardrail.py  # Input validation and sanitization
│       └── output_guardrail.py # Output quality validation
│
├── Servers/                    # MCP server implementations
│   └── web_search.py           # Web search MCP server
│
├── Data/                       # PDF documents (knowledge base source)
│   ├── Chapter 1 Relations and Functions.pdf
│   ├── Chapter 2 Inverse Trigonometric Functions.pdf
│   └── ... (NCERT Class 12 Math chapters)
│
└── test.ipynb                  # Jupyter notebook for testing
```

## 🔧 Components

### 1. MathAgent (`src/agent/math_agent.py`)
The core agent that orchestrates problem solving:
- Creates CrewAI agent with appropriate tools
- Manages MCP server connections
- Coordinates between knowledge base, web search, and diagram tools

### 2. Vector Database (`src/knowledgebase/VectorDB.py`)
Manages the vector store:
- Initializes Qdrant connection
- Handles document ingestion and chunking
- Provides semantic search capabilities

### 3. Tools

#### Retriever Tool (`src/tools/Retriever_Tool.py`)
- Searches internal knowledge base using semantic similarity
- Returns top 5 relevant document chunks

#### Diagram Tool (`src/tools/Diagram_Tool.py`)
- Generates mathematical diagrams (vectors, graphs, geometry)
- Supports multiple diagram types
- Outputs base64-encoded PNG images

### 4. Guardrails

#### Input Guardrail (`src/guardrails/input_guardrail.py`)
- Detects and redacts PII (emails, phone numbers, etc.)
- Filters inappropriate content
- Validates mathematical relevance
- Prevents SQL injection attempts

#### Output Guardrail (`src/guardrails/output_guardrail.py`)
- Validates response quality
- Checks for mathematical accuracy
- Provides quality scores and suggestions

### 5. Web Interface (`app.py`)
Streamlit application features:
- Chat-based interface
- Real-time response rendering
- Diagram display
- LaTeX math rendering
- Conversation history
- Input/output validation UI

## 🔑 API Keys Required

1. **Google Gemini API Key**
   - Get it from: https://ai.google.dev/
   - Used for: LLM reasoning and text generation

2. **Qdrant Cloud API Key**
   - Get it from: https://cloud.qdrant.io/
   - Used for: Vector database storage and retrieval

3. **Tavily API Key**
   - Get it from: https://tavily.com/
   - Used for: Web search functionality

## 🎓 Educational Use Cases

- **Homework Help**: Get step-by-step solutions to math problems
- **Concept Learning**: Understand mathematical concepts with detailed explanations
- **Visual Learning**: See graphical representations of mathematical concepts
- **Exam Preparation**: Review NCERT Class 12 mathematics topics
- **Self-Study**: Learn at your own pace with an AI tutor

## 🔒 Privacy & Security

- **Input Guardrails**: Automatically detect and redact personal information
- **Content Filtering**: Filter inappropriate or harmful content
- **Safe Output**: Validate responses for quality and appropriateness
- **No Data Storage**: Conversations are stored only in session memory

## 🐛 Troubleshooting

### Common Issues

1. **Agent Initialization Failed**
   - Check that all API keys are correctly set in `.env`
   - Verify internet connection for Qdrant Cloud
   - Ensure Python version is 3.8+

2. **Vector Database Connection Error**
   - Verify Qdrant API key is valid
   - Check Qdrant Cloud service status
   - Ensure collection name matches configuration

3. **Diagram Generation Issues**
   - Ensure matplotlib is properly installed
   - Check that description contains sufficient detail
   - Verify numpy is installed correctly

4. **Streamlit App Not Loading**
   - Check port 8501 is not in use
   - Verify all dependencies are installed
   - Check console for error messages

## 📝 Development

### Running Tests
```bash
# Run vector DB test
python src/knowledgebase/VectorDB.py

# Test agent
python src/agent/math_agent.py
```

### Adding New Tools
1. Create tool class in `src/tools/`
2. Inherit from `crewai.tools.BaseTool`
3. Define input schema with Pydantic
4. Implement `_run` method
5. Add tool to `MathAgent.create_agent()` method

### Extending Knowledge Base
1. Add PDF files to `Data/` directory
2. Run `VectorDB(initialize=True)` to re-index
3. The system will automatically use new documents

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. When contributing:
1. Follow the existing code style
2. Add comments for complex logic
3. Update documentation as needed
4. Test your changes thoroughly

## 📄 License

This project is part of an internship task. Please refer to your organization's licensing terms.

## 👤 Author

**Gnana Chaithanya Mangammagari**



