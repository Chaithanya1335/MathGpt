import asyncio
import sys
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from src.utils import get_llm_model, get_mcp_client
from src.tools.Retriever_Tool import GetRelevantDocumentsTool
from src.tools.Diagram_Tool import GenerateDiagramTool
from config.config import role, goal, backstory, server_params

class MathAgent:
    def __init__(self):
        self.llm = get_llm_model(model_name="gemini-2.5-flash")
        self.mcp_client = get_mcp_client()
        self.agent = None

    async def create_agent(self):
        """
        Create the agent using internal KB + external web search MCP.
        """
      
        kb_tool = GetRelevantDocumentsTool()
        diagram_tool = GenerateDiagramTool()

        # Create MCP adapter synchronously (correct)
        self.mcp_adapter = MCPServerAdapter(server_params, connect_timeout=60)
        mcp_tools = self.mcp_adapter.__enter__()  # explicitly open the adapter

        print(
            f"Available MCP tools: {[tool.name for tool in mcp_tools]}",
            file=sys.stderr,
        )

        tools = [kb_tool, diagram_tool] + list(mcp_tools)

        self.agent = Agent(
            llm=self.llm,
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            reasoning=True,
            verbose=True,
        )

        return self.agent

    async def run_agent(self, query: str):
        """
        Run the agent with the given math query.
        """
        task = Task(
            description = f"""Solve the following mathematical problem:

{query}

Your response should be clear, well-structured, and easy to follow, written in a natural, flowing manner rather than a rigid step-by-step list. Follow this approach:

## Understanding the Problem
Briefly acknowledge what the question is asking and what needs to be solved. If you retrieve relevant knowledge from the internal knowledge base (GetRelevantDocumentsTool) or web search, summarize the key concepts that will be used.

## Visual Representation (ONLY if needed)
Use the "Generate Mathematical Diagram" tool **only** when:
- The question explicitly asks to "represent graphically", "draw", "show diagram", "plot", "visualize", or "graph";
- OR the problem involves vectors, coordinate systems, geometric shapes (triangles, circles, etc.), or function graphs;
- OR the question explicitly mentions visual/spatial concepts.

Do **not** use the diagram tool for pure algebra, calculus without graphing, theoretical/abstract math, or word problems solvable purely by calculation.

If a diagram is required, call the tool and include a marker in the text where the diagram appears using this format:
[DIAGRAM:diagram_type:title:description]
Example: [DIAGRAM:vector:Displacement Vector:A displacement of 40 km, 30° east of north]

## Solution Process
Work through the problem logically and explain your reasoning. Show work and use LaTeX for math:
- Use `$...$` for inline math and `$$...$$` for displayed equations.
Reference any diagrams if generated.

## Final Answer
Present the final answer clearly and directly, using appropriate mathematical notation.

## Clear Explanation
Give an intuitive explanation that helps the student understand why the answer makes sense. Use simple language and helpful analogies when appropriate.

### Formatting & Tone
- Use Markdown (headings like ##, ### where helpful).
- Use a conversational, educational tone (like a helpful tutor).
- Avoid rigid "Step 1/Step 2" lists unless the problem genuinely benefits from numbered steps.
- If you used the GetRelevantDocumentsTool or web search, briefly cite the key retrieved facts in your explanation.
"""
,
            agent=self.agent,
            expected_output=(
        "A clear, natural explanation using Markdown and LaTeX. Include diagrams only when required."
    ),
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task]
        )

        results = crew.kickoff({"input":query})

        # Extract string from CrewOutput object
        if hasattr(results, 'tasks_output') and results.tasks_output:
            return str(results.tasks_output[-1])
        elif hasattr(results, 'raw'):
            return str(results.raw)
        else:
            return str(results)

        

    def close(self):
        """Cleanly shut down the MCP adapter."""
        if self.mcp_adapter:
            self.mcp_adapter.__exit__(None, None, None)


async def main():
    math_agent = MathAgent()
    agent = await math_agent.create_agent()

    try:
        response = await math_agent.run_agent(
            "Compare the latest advancements in quantum computing (as of 2025) with traditional transistor-based architectures."
        )
        print("\n🔹 Response from Math Agent:")
        print(response)
    finally:
        math_agent.close()


if __name__ == "__main__":
    asyncio.run(main())
