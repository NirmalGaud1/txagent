import streamlit as st
import google.generativeai as genai

# Configure Gemini
API_KEY = "AIzaSyA-9-lTQTWdNM43YdOXMQwGKDy0SrMwo6c"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Mock Therapeutic Tools
THERAPEUTIC_TOOLS = {
    "get_drug_info": {
        "description": "Get drug indications, dosage, and warnings",
        "parameters": ["drug_name"]
    },
    "check_interactions": {
        "description": "Check interactions between two drugs",
        "parameters": ["drug1", "drug2"]
    },
    "get_guidelines": {
        "description": "Get clinical guidelines for a condition",
        "parameters": ["condition"]
    }
}

# Mock Tool Responses (Replace with real API calls)
def execute_tool(tool_name, args):
    mock_responses = {
        "get_drug_info": {
            "indications": ["Hypertension", "Heart Failure"],
            "dosage": "50 mg/day",
            "warnings": ["Avoid in pregnancy"]
        },
        "check_interactions": {
            "severity": "High",
            "risk": "Increased potassium levels"
        },
        "get_guidelines": {
            "recommendations": ["First-line treatment for hypertension"]
        }
    }
    return mock_responses.get(tool_name, {})

# Tool Selection Prompt
TOOL_PROMPT = """You are a clinical reasoning AI. Available tools:
{tools}

Current query: {query}
Previous steps: {history}

Respond ONLY in this format:
THOUGHT: [Your reasoning]
TOOL: [Tool name or FINISH]
ARGS: [JSON arguments or null]"""

# Streamlit App
st.title("TxAgent Lite - Therapeutic Reasoning AI")

user_query = st.text_input("Enter clinical query:", 
                          "Can a pregnant patient take lisinopril with spironolactone?")

if st.button("Analyze"):
    reasoning_steps = []
    current_query = user_query
    final_answer = None
    
    with st.status("Reasoning...", expanded=True) as status:
        for step in range(3):  # Limit to 3 reasoning steps for demo
            # Generate tool selection
            tools_str = "\n".join([f"{name}: {desc['description']}" 
                                 for name, desc in THERAPEUTIC_TOOLS.items()])
            
            prompt = TOOL_PROMPT.format(
                tools=tools_str,
                query=current_query,
                history=reasoning_steps[-1]["result"] if reasoning_steps else "None"
            )
            
            response = model.generate_content(prompt)
            text = response.text
            
            # Parse response
            thought = text.split("TOOL:")[0].replace("THOUGHT:", "").strip()
            tool = text.split("TOOL:")[1].split("ARGS:")[0].strip()
            args = text.split("ARGS:")[1].strip() if "ARGS:" in text else None
            
            st.write(f"**Step {step+1}:** {thought}")
            
            if tool == "FINISH":
                final_answer = args
                break
                
            if tool not in THERAPEUTIC_TOOLS:
                st.error("Invalid tool selected")
                break
                
            # Execute tool
            args_dict = eval(args) if args else {}
            result = execute_tool(tool, args_dict)
            
            reasoning_steps.append({
                "tool": tool,
                "args": args_dict,
                "result": result
            })
            
            current_query = f"Previous result: {result}. Original query: {user_query}"
            
        status.update(label="Analysis Complete", state="complete")
    
    if final_answer:
        st.subheader("Final Recommendation")
        st.success(final_answer)
    
    st.subheader("Reasoning Steps")
    for i, step in enumerate(reasoning_steps):
        st.write(f"""
        **Step {i+1}**
        - Tool: {step['tool']}
        - Arguments: {step['args']}
        - Result: {step['result']}
        """)
