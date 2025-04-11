# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from transcript_processor import process_transcript

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Meeting Assistant",
    page_icon="📝",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .result-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .action-item {
        background-color: #e3f2fd;
        padding: 0.8rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 4px solid #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.title("📝 Intelligent Meeting Assistant")
st.markdown("Upload a meeting transcript to generate a summary and extract action items.")

# File upload section
with st.expander("Upload Transcript", expanded=True):
    upload_option = st.radio(
        "Choose input method:",
        ["Upload a file", "Paste transcript text"]
    )
    
    transcript_text = ""
    
    if upload_option == "Upload a file":
        uploaded_file = st.file_uploader("Upload meeting transcript", type=["txt", "md", "doc", "docx"])
        if uploaded_file is not None:
            # For simplicity, we're assuming text files
            # In a production app, you would handle different file types
            transcript_text = uploaded_file.getvalue().decode("utf-8")
            st.success("File uploaded successfully!")
    else:
        transcript_text = st.text_area("Paste your meeting transcript here:", height=250)

# Process button
if transcript_text:
    st.divider()
    
    if st.button("Process Transcript", type="primary"):
        with st.spinner("Processing transcript... This may take a moment."):
            try:
                # Process the transcript using our backend
                results = process_transcript(transcript_text)
                
                # Store results in session state for persistence
                st.session_state.results = results
            except Exception as e:
                st.error(f"Error processing transcript: {str(e)}")
                st.stop()
        
        st.success("Transcript processed successfully!")

# Display results if available
if 'results' in st.session_state:
    results = st.session_state.results
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Meeting Summary")
        st.markdown(f"""
        <div class="result-container">
            {results["summary"]}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ✅ Action Items")
        
        if not results["action_items"]:
            st.info("No action items were found in this transcript.")
        else:
            for item in results["action_items"]:
                assignee = f"**Assignee:** {item['assignee']}" if item['assignee'] else ""
                deadline = f"**Deadline:** {item['deadline']}" if item['deadline'] else ""
                
                st.markdown(f"""
                <div class="action-item">
                    <strong>Task:</strong> {item['task']}<br>
                    {assignee}<br>
                    {deadline}
                </div>
                """, unsafe_allow_html=True)
    
    # Download options
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        summary_text = results["summary"]
        st.download_button(
            label="Download Summary",
            data=summary_text,
            file_name="meeting_summary.txt",
            mime="text/plain"
        )
    
    with col2:
        # Format action items for download
        action_items_text = "# ACTION ITEMS\n\n"
        for i, item in enumerate(results["action_items"], 1):
            action_items_text += f"{i}. Task: {item['task']}\n"
            if item['assignee']:
                action_items_text += f"   Assignee: {item['assignee']}\n"
            if item['deadline']:
                action_items_text += f"   Deadline: {item['deadline']}\n"
            action_items_text += "\n"
        
        st.download_button(
            label="Download Action Items",
            data=action_items_text,
            file_name="action_items.txt",
            mime="text/plain"
        )

# Footer
st.divider()
st.caption("Intelligent Meeting Assistant v1.0 | Powered by LangGraph and Groq")