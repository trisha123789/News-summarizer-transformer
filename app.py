import streamlit as st
from transformers import pipeline
import pdfplumber
from docx import Document
from reportlab.pdfgen import canvas
import tempfile

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="AI Meeting Minutes Summarizer",
    page_icon="📝",
    layout="wide"
)

# ---------------------------
# Header
# ---------------------------
st.title("📝 AI Meeting Minutes Summarizer")

# ---------------------------
# Load Summarization Model
# ---------------------------
@st.cache_resource
def load_model():
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn"
    )

summarizer = load_model()

# ---------------------------
# File Reading Functions
# ---------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# ---------------------------
# Summary PDF Generator
# ---------------------------
def create_pdf(summary_text):
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    c = canvas.Canvas(temp_pdf.name)
    c.drawString(50, 800, "AI Generated Summary")

    y = 760
    for line in summary_text.split("\n"):
        c.drawString(50, y, line[:100])
        y -= 20

    c.save()

    return temp_pdf.name

# ---------------------------
# Section 1
# ---------------------------
st.subheader("Section 1: Enter Meeting Notes")

meeting_notes = st.text_area(
    "Paste meeting notes here...",
    height=250
)

# ---------------------------
# Bonus 1: Upload PDF
# ---------------------------
pdf_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if pdf_file:
    meeting_notes = read_pdf(pdf_file)
    st.success("PDF loaded successfully!")

# ---------------------------
# Bonus 2: Upload DOCX
# ---------------------------
docx_file = st.file_uploader(
    "Upload DOCX",
    type=["docx"]
)

if docx_file:
    meeting_notes = read_docx(docx_file)
    st.success("DOCX loaded successfully!")

# ---------------------------
# Section 2
# ---------------------------
st.subheader("Section 2: Generate Summary")

if st.button("Generate Summary"):

    if meeting_notes.strip():

        summary = summarizer(
            meeting_notes,
            max_length=120,
            min_length=30,
            do_sample=False
        )[0]["summary_text"]

        # ---------------------------
        # Section 3
        # ---------------------------
        st.subheader("Section 3: AI Generated Summary")

        st.success(summary)

        # ---------------------------
        # Statistics
        # ---------------------------
        original_words = len(meeting_notes.split())
        summary_words = len(summary.split())

        compression_ratio = (
            (original_words - summary_words)
            / original_words
        ) * 100

        st.subheader("Section 4: Statistics")

        st.write(f"**Original Words:** {original_words}")
        st.write(f"**Summary Words:** {summary_words}")
        st.write(
            f"**Compression Ratio:** {compression_ratio:.2f}%"
        )

        # ---------------------------
        # Bonus 3 Download PDF
        # ---------------------------
        pdf_path = create_pdf(summary)

        with open(pdf_path, "rb") as file:
            st.download_button(
                label="📥 Download Summary as PDF",
                data=file,
                file_name="meeting_summary.pdf",
                mime="application/pdf"
            )

    else:
        st.warning("Please enter meeting notes.")