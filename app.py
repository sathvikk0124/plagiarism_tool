import streamlit as st
import PyPDF2
import docx
from transformers import pipeline

# --- 1. TEXT EXTRACTION FUNCTIONS ---
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# --- 2. AI DETECTION ENGINE (Using HuggingFace) ---
@st.cache_resource # Cache the model so it doesn't reload every time
def load_ai_detector():
    # This downloads a free model that detects ChatGPT-generated text
    # Note: This is a small model for demonstration. Paid APIs are more accurate.
    return pipeline("text-classification", model("roberta-base-openai-detector"))

def check_ai_probability(text):
    try:
        # We truncate to 512 tokens because local models have limits
        # In a real app, you would chunk the text and average the score
        truncated_text = text[:1500] 
        
        # For demo purposes, let's simulate a score based on text patterns 
        # (Real implementation requires the heavy model download above, 
        # so here is a logic simulation for instant feedback without 2GB download)
        
        # simplified logic for demo:
        if "As an AI language model" in text or "In conclusion," in text:
            return 85.5, "High AI Probability"
        else:
            return 12.0, "Low AI Probability"
    except Exception as e:
        return 0.0, "Error"

# --- 3. PLAGIARISM CHECKER (API Placeholder) ---
def check_plagiarism(text):
    # REAL WORLD: You would send 'text' to an API like Copyleaks or EdenAI here.
    # returning a mock result for demonstration.
    import random
    score = random.randint(0, 20) # Simulating a low plagiarism score
    sources = ["Wikipedia - General Knowledge", "Academic Source A"] if score > 10 else []
    return score, sources

# --- 4. MAIN APP UI ---
def main():
    st.set_page_config(page_title="Content Integrity Tool", layout="wide")
    
    st.title("🕵️ Content Integrity Scanner")
    st.markdown("Upload a document to check for **AI Generation** and **Plagiarism**.")

    # Sidebar for input method
    option = st.sidebar.selectbox("Input Method", ["Upload File", "Paste Text"])
    
    user_text = ""

    if option == "Upload File":
        uploaded_file = st.file_uploader("Choose a PDF or Docx file", type=['pdf', 'docx'])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                user_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith('.docx'):
                user_text = extract_text_from_docx(uploaded_file)
            st.success(f"File '{uploaded_file.name}' processed successfully!")
            
    elif option == "Paste Text":
        user_text = st.text_area("Paste your content here...", height=200)

    # Analyze Button
    if st.button("Analyze Content"):
        if user_text and len(user_text) > 50:
            col1, col2 = st.columns(2)
            
            with st.spinner('Running AI Forensics...'):
                # 1. Check AI
                ai_score, ai_label = check_ai_probability(user_text)
                
                # 2. Check Plagiarism
                plag_score, sources = check_plagiarism(user_text)

            # Display Results
            with col1:
                st.subheader("🤖 AI Detection Score")
                st.metric(label="Likelihood of AI", value=f"{ai_score}%")
                if ai_score > 50:
                    st.warning(f"Flagged: {ai_label}")
                else:
                    st.success("Looks Human-Written")

            with col2:
                st.subheader("📝 Plagiarism Check")
                st.metric(label="Plagiarized Content", value=f"{plag_score}%")
                if sources:
                    st.write("Potential Sources:")
                    for s in sources:
                        st.write(f"- {s}")
                else:
                    st.success("No major matches found (Simulation)")
                    
            # Text preview
            with st.expander("View Extracted Text"):
                st.write(user_text)
                
        else:
            st.error("Please provide text longer than 50 characters.")

if __name__ == "__main__":
    main()