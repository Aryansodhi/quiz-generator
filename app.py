import streamlit as st  # type: ignore
from utils.qg_ollama import generate_mcq_ollama

st.set_page_config(page_title="MCQ Generator", layout="centered")

st.title("📘 MCQ Generator using Ollama (Mistral)")
st.markdown("Upload a `.txt`, `.pdf`, or `.docx` file to generate multiple-choice questions.")

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])
num_qs = st.slider("Number of questions", 1, 10, 3)

if st.button("Generate MCQs"):
    if uploaded_file is not None:
        with st.spinner("Generating questions..."):
            mcqs = generate_mcq_ollama(uploaded_file, num_questions=num_qs)

        if mcqs:
            for i, q in enumerate(mcqs, 1):
                st.markdown(f"### Question {i}: {q['question']}")
                for opt in q['options']:
                    st.markdown(f"- {opt}")

                with st.expander("Show Answer"):
                    st.markdown(f"**Answer:** {q['answer']}")
        else:
            st.warning("⚠️ No valid questions generated. Try a different file or reduce the number of questions.")
    else:
        st.warning("📂 Please upload a file first.")
