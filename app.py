import streamlit as st
import asyncio
import sys
import re
import json
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from src.agent.math_agent import MathAgent
from src.tools.Diagram_Tool import GenerateDiagramTool
from src.guardrails.input_guardrail import create_input_guardrail
from src.guardrails.output_guardrail import create_output_guardrail
from src.agent.feedback_agent import FeedbackAgent

# Page configuration
st.set_page_config(
    page_title="MathGPT - Intelligent Math Tutor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    /* Main background and styling */
    .main {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Chat container */
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    
    .assistant-message {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #667eea;
        padding: 0.75rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102,126,234,0.4);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Success message */
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-text {
        animation: pulse 2s infinite;
        color: #667eea;
        font-weight: 600;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
    st.session_state.agent_initialized = False

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'initialization_error' not in st.session_state:
    st.session_state.initialization_error = None

# Initialize guardrails
if 'input_guardrail' not in st.session_state:
    st.session_state.input_guardrail = create_input_guardrail()

if 'output_guardrail' not in st.session_state:
    st.session_state.output_guardrail = create_output_guardrail()

# Header
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🧮 MathGPT</h1>
        <p class="header-subtitle">Your Intelligent Mathematics Tutor with Agentic-RAG</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📚 About")
    st.markdown("""
    **MathGPT** is an intelligent mathematics tutoring system that combines:
    
    - 📖 **Internal Knowledge Base** - Access to curated math content
    - 🌐 **Web Search** - Latest information from the internet
    - 🤖 **AI Reasoning** - Step-by-step problem solving
    
    Simply type your math question and get a comprehensive solution!
    """)
    
    st.divider()
    
    st.header("🎯 How to Use")
    st.markdown("""
    1. Enter your math question in the input field
    2. Click **"Ask MathGPT"** button
    3. Wait for the AI to process your question
    4. View the step-by-step solution
    
    **Examples:**
    - "Solve x² + 5x + 6 = 0"
    - "Explain the chain rule in calculus"
    - "What is the derivative of sin(x)?"
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    clear_history = st.button("🗑️ Clear Chat History", use_container_width=True)
    if clear_history:
        st.session_state.chat_history = []
        st.rerun()

# Initialize agent function
async def initialize_agent():
    """Initialize the MathAgent asynchronously"""
    if not st.session_state.agent_initialized:
        try:
            math_agent = MathAgent()
            agent = await math_agent.create_agent()
            st.session_state.agent = math_agent
            st.session_state.agent_initialized = True
            st.session_state.initialization_error = None
            return True
        except Exception as e:
            st.session_state.initialization_error = str(e)
            return False
    return True

# Run async function helper
def run_async(coro):
    """Helper to run async functions in Streamlit safely"""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, use ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(coro)

def extract_and_display_diagrams(response: str):
    """
    Extract diagram information from response and display diagrams.
    Returns tuple: (modified_response_without_diagram_data, list_of_diagram_data)
    """
    diagrams = []
    seen_diagrams = set()  # Track seen diagrams to avoid duplicates
    modified_response = response
    
    # Look for JSON diagram data in the response - more robust pattern
    # Try to find JSON objects that contain diagram data
    # Pattern: find { ... "diagram_generated" ... } with proper JSON structure
    json_patterns = [
        r'\{[^{}]*"diagram_generated"[^{}]*"image_base64"[^{}]*\}',  # Simple pattern
        r'\{[^{}]*"diagram_generated".*?"image_base64".*?\}',  # More flexible
    ]
    
    for pattern in json_patterns:
        json_matches = re.findall(pattern, response, re.DOTALL)
        for json_str in json_matches:
            try:
                # Try to parse as JSON
                diagram_data = json.loads(json_str)
                if diagram_data.get("diagram_generated") and diagram_data.get("image_base64"):
                    # Use title as unique identifier to avoid duplicates
                    diagram_id = diagram_data.get("title", "") + diagram_data.get("image_base64", "")[:50]
                    if diagram_id not in seen_diagrams:
                        diagrams.append(diagram_data)
                        seen_diagrams.add(diagram_id)
                    # Remove the JSON from the response
                    modified_response = modified_response.replace(json_str, "")
                    break  # Found valid diagram, move on
            except json.JSONDecodeError:
                # Try to find complete JSON by expanding search
                try:
                    # Look for opening { and find matching closing }
                    start_idx = response.find(json_str)
                    if start_idx != -1:
                        brace_count = 0
                        end_idx = start_idx
                        for i, char in enumerate(response[start_idx:], start_idx):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end_idx = i + 1
                                    break
                        if end_idx > start_idx:
                            complete_json = response[start_idx:end_idx]
                            diagram_data = json.loads(complete_json)
                            if diagram_data.get("diagram_generated") and diagram_data.get("image_base64"):
                                # Use title as unique identifier to avoid duplicates
                                diagram_id = diagram_data.get("title", "") + diagram_data.get("image_base64", "")[:50]
                                if diagram_id not in seen_diagrams:
                                    diagrams.append(diagram_data)
                                    seen_diagrams.add(diagram_id)
                                modified_response = modified_response.replace(complete_json, "")
                except json.JSONDecodeError:
                    continue
    
    # Also look for diagram markers like [DIAGRAM:type:title:description]
    diagram_marker_pattern = r'\[DIAGRAM:([^:]+):([^:]+):([^\]]+)\]'
    marker_matches = re.findall(diagram_marker_pattern, modified_response)
    
    diagram_tool = GenerateDiagramTool()
    for diagram_type, title, description in marker_matches:
        try:
            result = diagram_tool._run(
                diagram_type=diagram_type,
                description=description,
                title=title
            )
            diagram_data = json.loads(result)
            if diagram_data.get("diagram_generated") and diagram_data.get("image_base64"):
                # Use title as unique identifier to avoid duplicates
                diagram_id = diagram_data.get("title", "") + diagram_data.get("image_base64", "")[:50]
                if diagram_id not in seen_diagrams:
                    diagrams.append(diagram_data)
                    seen_diagrams.add(diagram_id)
                    # Replace marker with placeholder that we'll handle in display
                    modified_response = modified_response.replace(
                        f"[DIAGRAM:{diagram_type}:{title}:{description}]",
                        f"[DIAGRAM_PLACEHOLDER_{len(diagrams)-1}]"
                    )
                else:
                    # Remove marker even if diagram is duplicate
                    modified_response = modified_response.replace(
                        f"[DIAGRAM:{diagram_type}:{title}:{description}]",
                        ""
                    )
        except Exception as e:
            st.warning(f"Could not generate diagram: {str(e)}")
    
    return modified_response, diagrams


def process_agent_response(response: str) -> tuple:
    """
    Process agent response to extract content from LaTeX documents if needed,
    extract diagrams, and ensure proper Markdown formatting for Streamlit.
    Returns tuple: (processed_text, diagrams_list)
    """
    # Extract diagrams first
    response, diagrams = extract_and_display_diagrams(response)
    
    # If response starts with \documentclass, it's a LaTeX document - extract content
    if response.strip().startswith('\\documentclass'):
        # Try to extract content between \begin{document} and \end{document}
        doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', response, re.DOTALL)
        if doc_match:
            content = doc_match.group(1).strip()
            
            # Remove LaTeX commands and convert to Markdown where possible
            # Remove \section*{}, \subsection*{}, etc. and convert to Markdown headers
            content = re.sub(r'\\section\*\{([^}]+)\}', r'## \1', content)
            content = re.sub(r'\\subsection\*\{([^}]+)\}', r'### \1', content)
            
            # Remove \begin{itemize}/\end{itemize} and keep itemize items
            content = re.sub(r'\\begin\{itemize\}', '', content)
            content = re.sub(r'\\end\{itemize\}', '', content)
            content = re.sub(r'\\item\s+', '- ', content)
            
            # Remove \begin{enumerate}/\end{enumerate} and convert to numbered list
            content = re.sub(r'\\begin\{enumerate\}', '', content)
            content = re.sub(r'\\end\{enumerate\}', '', content)
            # Better enumerate handling - preserve numbering context
            content = re.sub(r'\\item\s+', '\n1. ', content)
            
            # Remove TikZ/tikzpicture environments (they won't render in Streamlit)
            content = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', 
                           '\n*[Note: Diagram was included in original response]*\n', 
                           content, flags=re.DOTALL)
            
            # Remove other LaTeX environments that won't render
            content = re.sub(r'\\begin\{[^}]+\}.*?\\end\{[^}]+\}', '', content, flags=re.DOTALL)
            
            # Remove \captionof, \vspace, etc.
            content = re.sub(r'\\captionof\{[^}]+\}\{([^}]+)\}', r'*\1*', content)
            content = re.sub(r'\\vspace\{[^}]+\}', '\n', content)
            content = re.sub(r'\\center', '', content)
            
            # Remove \textbf{} and keep content (Markdown bold is **)
            content = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', content)
            
            # Remove \text{} commands but preserve content
            content = re.sub(r'\\text\{([^}]+)\}', r'\1', content)
            
            # Remove remaining LaTeX formatting commands that don't affect math
            content = re.sub(r'\\[a-zA-Z]+\*?\{[^}]*\}', '', content)
            
            # Clean up multiple newlines and whitespace
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
            
            return content.strip(), diagrams
    
    # If already in Markdown format, just return it with diagrams
    return response, diagrams

# Initialize agent on first run
if not st.session_state.agent_initialized and st.session_state.initialization_error is None:
    with st.spinner("🚀 Initializing MathGPT Agent..."):
        success = run_async(initialize_agent())
        if success:
            st.success("✅ Agent initialized successfully!")
            st.rerun()

# Show initialization error if any
if st.session_state.initialization_error:
    st.error(f"❌ Error initializing agent: {st.session_state.initialization_error}")
    st.info("Please check your environment variables and API keys in the .env file")

# Main content area
if st.session_state.agent_initialized:
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        
        for i, (role, message) in enumerate(st.session_state.chat_history):
            if role == "user":
                st.markdown(f"""
                    <div class="user-message">
                        <strong>You:</strong><br>
                        {message}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("#### 🧮 MathGPT")
                # Process message in case it contains LaTeX document structure
                processed_message, diagrams = process_agent_response(message)
                
                # Display diagrams if any (only once, not duplicated in history)
                if diagrams:
                    for idx, diagram_data in enumerate(diagrams):
                        if diagram_data.get("image_base64"):
                            img_data = base64.b64decode(diagram_data["image_base64"])
                            title = diagram_data.get("title", f"Diagram {idx + 1}")
                            st.markdown(f"### 📊 {title}")
                            # Use smaller width to reduce size
                            st.image(img_data, use_container_width=False, width=400)
                            st.markdown("---")
                
                # Replace diagram placeholders with nothing (already displayed above)
                processed_message = re.sub(r'\[DIAGRAM_PLACEHOLDER_\d+\]', '', processed_message)
                
                st.markdown(processed_message)
                
                # Add feedback section after each assistant response in history
                feedback_key = f"feedback_{i}"
                if feedback_key not in st.session_state:
                    st.session_state[feedback_key] = None
                
                feedback = st.radio(
                    "📝 Rate this response:",
                    options=["", "👍 Helpful", "👎 Not Helpful", "❓ Unclear"],
                    key=feedback_key,
                    horizontal=True
                )
                
                if feedback and feedback != "" and feedback != st.session_state.get(f"feedback_submitted_{i}", ""):
                    st.session_state[f"feedback_submitted_{i}"] = feedback
                    with st.spinner("🔄 Generating improved response..."):
                        try:
                            # Find the user query that corresponds to this assistant response
                            user_query_for_feedback = ""
                            if i > 0 and st.session_state.chat_history[i-1][0] == "user":
                                user_query_for_feedback = st.session_state.chat_history[i-1][1]
                            else:
                                # If we can't find it in history, use the first user message before this
                                for j in range(i-1, -1, -1):
                                    if st.session_state.chat_history[j][0] == "user":
                                        user_query_for_feedback = st.session_state.chat_history[j][1]
                                        break
                            
                            improved_response = FeedbackAgent().run_agent(
                                original_query=user_query_for_feedback,
                                mathgpt_solution=processed_message,
                                user_feedback=feedback
                            )
                            
                            # Ensure response is a string
                            if not isinstance(improved_response, str):
                                if hasattr(improved_response, 'tasks_output') and improved_response.tasks_output:
                                    improved_response = str(improved_response.tasks_output[-1])
                                elif hasattr(improved_response, 'raw'):
                                    improved_response = str(improved_response.raw)
                                else:
                                    improved_response = str(improved_response)
                            
                            # Process improved response
                            processed_improved, improved_diagrams = process_agent_response(improved_response)
                            
                            # Display improved response
                            st.markdown("#### 🔄 Improved Response Based on Your Feedback")
                            
                            # Display diagrams if any
                            if improved_diagrams:
                                for idx, diagram_data in enumerate(improved_diagrams):
                                    if diagram_data.get("image_base64"):
                                        img_data = base64.b64decode(diagram_data["image_base64"])
                                        title = diagram_data.get("title", f"Diagram {idx + 1}")
                                        st.markdown(f"### 📊 {title}")
                                        st.image(img_data, use_container_width=False, width=400)
                                        st.markdown("---")
                            
                            # Display improved response text
                            display_improved = re.sub(r'\[DIAGRAM_PLACEHOLDER_\d+\]', '', processed_improved)
                            st.markdown(display_improved)
                            
                            # Add improved response to chat history
                            st.session_state.chat_history.append(("assistant", improved_response))
                            st.rerun()
                            
                        except ValueError as e:
                            st.error(f"❌ Invalid value error: {str(e)}")
                        except RuntimeError as e:
                            st.error(f"❌ Runtime error: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error generating improved response: {str(e)}")
                
                st.divider()
    
    # Input section
    st.markdown("### 💭 Ask Your Math Question")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_query = st.text_input(
            "Enter your math question:",
            placeholder="e.g., Solve x² + 5x + 6 = 0 or Explain the chain rule...",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.button("🚀 Ask MathGPT", use_container_width=True, type="primary")
    
    # Process query
    if submit_button and user_query:
        # Step 1: Input validation with guardrails
        input_validation = st.session_state.input_guardrail.validate(user_query)
        
        if not input_validation.is_valid:
            st.error("❌ Input validation failed")
            if input_validation.warnings:
                for warning in input_validation.warnings:
                    st.warning(f"⚠️ {warning}")
            if input_validation.pii_detected:
                st.info("ℹ️ Personal information was detected and redacted for your privacy.")
            st.stop()
        
        # Use sanitized input if it was modified
        sanitized_query = input_validation.sanitized_input
        if sanitized_query != user_query:
            st.info(f"ℹ️ Input was sanitized. PII detected: {input_validation.pii_detected}")
        
        # Show warnings if any (non-blocking)
        if input_validation.warnings:
            for warning in input_validation.warnings:
                st.warning(f"⚠️ {warning}")
        
        # Add user message to history (use sanitized query)
        st.session_state.chat_history.append(("user", sanitized_query))
        
        # Show user message
        st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong><br>
                {sanitized_query}
            </div>
        """, unsafe_allow_html=True)
        
        # Process with agent
        with st.spinner("🤔 MathGPT is thinking..."):
            try:
                raw_response = run_async(st.session_state.agent.run_agent(sanitized_query))
                
                # Ensure response is a string (CrewOutput might be returned)
                if not isinstance(raw_response, str):
                    if hasattr(raw_response, 'tasks_output') and raw_response.tasks_output:
                        raw_response = str(raw_response.tasks_output[-1])
                    elif hasattr(raw_response, 'raw'):
                        raw_response = str(raw_response.raw)
                    else:
                        raw_response = str(raw_response)
                
                # Step 2: Output validation with guardrails
                output_validation = st.session_state.output_guardrail.validate(raw_response, sanitized_query)
                
                # Show output warnings if any (non-blocking)
                if output_validation.warnings:
                    with st.expander("⚠️ Output Quality Warnings", expanded=False):
                        for warning in output_validation.warnings:
                            st.warning(warning)
                
                # Show quality score
                if output_validation.quality_score < 0.7:
                    st.info(f"📊 Response Quality Score: {output_validation.quality_score:.2f}/1.0")
                
                # Show suggestions if any
                if output_validation.suggestions:
                    with st.expander("💡 Suggestions for Better Responses", expanded=False):
                        for suggestion in output_validation.suggestions:
                            st.info(suggestion)
                
                # Process response to handle LaTeX documents and extract diagrams
                processed_response, diagrams = process_agent_response(raw_response)
                
                # Add assistant response to history (store raw response to preserve diagram data)
                st.session_state.chat_history.append(("assistant", raw_response))
                
                # Display response with proper markdown rendering
                st.markdown("#### 🧮 MathGPT Response")
                
                # Display diagrams first if any
                if diagrams:
                    for idx, diagram_data in enumerate(diagrams):
                        if diagram_data.get("image_base64"):
                            img_data = base64.b64decode(diagram_data["image_base64"])
                            title = diagram_data.get("title", f"Diagram {idx + 1}")
                            st.markdown(f"### 📊 {title}")
                            # Use smaller width to reduce size
                            st.image(img_data, use_container_width=False, width=400)
                            st.markdown("---")
                
                # Replace diagram placeholders with nothing (already displayed above)
                display_response = re.sub(r'\[DIAGRAM_PLACEHOLDER_\d+\]', '', processed_response)
                st.markdown(display_response)
                
                # Success indicator
                st.markdown("""
                    <div class="success-box">
                        ✅ Response generated successfully!
                    </div>
                """, unsafe_allow_html=True)
                
                # Add feedback section for new response
                new_response_feedback_key = "new_response_feedback"
                if new_response_feedback_key not in st.session_state:
                    st.session_state[new_response_feedback_key] = None
                
                feedback = st.radio(
                    "📝 Rate this response:",
                    options=["", "👍 Helpful", "👎 Not Helpful", "❓ Unclear"],
                    key=new_response_feedback_key,
                    horizontal=True
                )
                
                if feedback and feedback != "":
                    with st.spinner("🔄 Generating improved response..."):
                        try:
                            improved_response = FeedbackAgent().run_agent(
                                original_query=sanitized_query,
                                mathgpt_solution=display_response,
                                user_feedback=feedback
                            )
                            
                            # Ensure response is a string
                            if not isinstance(improved_response, str):
                                if hasattr(improved_response, 'tasks_output') and improved_response.tasks_output:
                                    improved_response = str(improved_response.tasks_output[-1])
                                elif hasattr(improved_response, 'raw'):
                                    improved_response = str(improved_response.raw)
                                else:
                                    improved_response = str(improved_response)
                            
                            # Process improved response
                            processed_improved, improved_diagrams = process_agent_response(improved_response)
                            
                            # Display improved response
                            st.markdown("#### 🔄 Improved Response Based on Your Feedback")
                            
                            # Display diagrams if any
                            if improved_diagrams:
                                for idx, diagram_data in enumerate(improved_diagrams):
                                    if diagram_data.get("image_base64"):
                                        img_data = base64.b64decode(diagram_data["image_base64"])
                                        title = diagram_data.get("title", f"Diagram {idx + 1}")
                                        st.markdown(f"### 📊 {title}")
                                        st.image(img_data, use_container_width=False, width=400)
                                        st.markdown("---")
                            
                            # Display improved response text
                            display_improved = re.sub(r'\[DIAGRAM_PLACEHOLDER_\d+\]', '', processed_improved)
                            st.markdown(display_improved)
                            
                            # Add improved response to chat history
                            st.session_state.chat_history.append(("assistant", improved_response))
                            st.session_state[new_response_feedback_key] = None  # Reset feedback
                            st.rerun()
                            
                        except ValueError as e:
                            st.error(f"❌ Invalid value error: {str(e)}")
                        except RuntimeError as e:
                            st.error(f"❌ Runtime error: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error generating improved response: {str(e)}")

                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append(("assistant", error_msg))
        
        st.rerun()
    
    elif submit_button and not user_query:
        st.warning("⚠️ Please enter a math question first!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Powered by <strong>CrewAI</strong> | <strong>Gemini</strong> | <strong>LangChain</strong></p>
        <p>Built with ❤️ for mathematics education</p>
    </div>
    """, unsafe_allow_html=True)

else:
    if st.session_state.initialization_error is None:
        st.info("🔄 Initializing agent... Please wait.")
    else:
        st.error("❌ Failed to initialize agent. Please check your configuration.")

