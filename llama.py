import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up API key and endpoints
API_KEY = os.getenv("llama_key")  # Set this in your .env file
LLAMA_API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Streamlit page settings
st.set_page_config(page_title="LLaMA 3 Chat & Code Analyzer", layout="centered")
st.title("🤖 LLaMA 3 Chat & Code Complexity Analyzer")

# --- Chat with LLaMA 3 ---
st.header("💬 Chat with LLaMA 3")

user_input = st.text_input("Enter your message:")

if st.button("Send") and user_input:
    chat_payload = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    with st.spinner("Waiting for LLaMA 3 response..."):
        response = requests.post(LLAMA_API_URL, headers=headers, json=chat_payload)

    if response.status_code == 200:
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        st.success("✅ AI Response:")
        st.markdown(ai_response)
    else:
        st.error(f"❌ Error {response.status_code}: {response.text}")

# --- Code Analysis Section ---
st.header("📊 Upload Code for Cyclomatic Complexity Analysis")

uploaded_file = st.file_uploader("Upload a file (.py, .java, .cpp):", type=["py", "java", "cpp"])

# Helper to detect language from file extension
def detect_language(filename):
    if filename.endswith(".py"):
        return "Python"
    elif filename.endswith(".java"):
        return "Java"
    elif filename.endswith(".cpp") or filename.endswith(".cc") or filename.endswith(".cxx"):
        return "C++"
    return "Unknown"

# If file is uploaded
if uploaded_file is not None:
    code_content = uploaded_file.read().decode("utf-8")
    language = detect_language(uploaded_file.name)

    if language == "Unknown":
        st.error("Unsupported file type.")
    else:
        st.subheader("📄 File Content (Copy or Edit Below)")
        user_editable_code = st.text_area("File content:", value=code_content, height=300)

        # Truncate if needed
        if len(user_editable_code) > 4000:
            user_editable_code = user_editable_code[:4000] + "\n# (Truncated for analysis)"

        st.subheader("🧠 LLaMA-Powered Code Analysis")
        analysis_prompt = f"""
        You are an expert software engineer.

        Analyze the following {language} code and provide:
        1. Estimated cyclomatic complexity.
        2. Key areas where the code could be improved.
        3. Potential bugs or inefficiencies.
        4. Suggestions for cleaner structure or optimization.

        5. Return the result in the following JSON format exactly, without extra explanation:

        {{
        "filename": "filename.py",
        "data": [
            {{
            "function_name": "process_data",
            "complexity": 12,
            "line_no": 11
            }},
            {{
            "function_name": "clean_text",
            "complexity": 5,
            "line_no": 35
            }}
        ]
        }}

        Code:
        """

        analysis_prompt += user_editable_code

        analysis_payload = {
            "model": "meta-llama/llama-3-70b-instruct",
            "messages": [
                {"role": "system", "content": "You are a professional software reviewer."},
                {"role": "user", "content": analysis_prompt}
            ],
            "temperature": 0.3
        }

        if st.button("Analyze Code"):
            with st.spinner("Analyzing code with LLaMA 3..."):
                response = requests.post(LLAMA_API_URL, headers=headers, json=analysis_payload)

            if response.status_code == 200:
                analysis_result = response.json()["choices"][0]["message"]["content"]
                st.success("✅ Code Analysis Result:")
                st.markdown(analysis_result)
            else:
                st.error(f"❌ Error {response.status_code}: {response.text}")
else:
    st.info("Please upload a .py, .java, or .cpp file for analysis.")
