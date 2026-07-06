# 🎓 CTU Academic Chatbot

Welcome to the **CTU Chatbot** project! This is a specialized RAG-based (Retrieval-Augmented Generation) AI assistant designed to provide accurate academic support, scholarship calculations, and policy information for students at Can Tho University (CTU).

## ✨ Features

- **Context-Aware Conversations**: Employs Google Gemini / Groq Llama alongside Qdrant Vector Database to provide highly accurate, context-aware answers.
- **Automated PDF Ingestion**: Directly upload PDF documents. The system automatically converts them to clean Markdown using LlamaParse and indexes them into the vector database.
- **Smart Scholarship Tool**: Integrated tool-calling allows the AI to automatically invoke internal functions to calculate and estimate scholarship rewards based on academic policies.
- **Persistent Chat Memory**: Seamlessly stores chat histories via Redis (short-term) and PostgreSQL (long-term), allowing users to review and resume past sessions.
- **Modern UI/UX**: Clean, responsive, and dynamic web interface built with vanilla HTML/CSS/JS, featuring fluid animations and a polished sidebar.

## 🚀 Quick Start

1. **Environment Setup**: Ensure you have WSL/Ubuntu installed.
2. **Install Dependencies**:
   ```bash
   python3 -m venv wsl_venv
   source wsl_venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Environment Variables**: Configure your `.env` file with necessary API keys (Google Gemini, Groq, PostgreSQL URL, Redis URL, LlamaCloud).
4. **Run the Server**:
   ```bash
   ./start_env.sh
   ```
   Or run manually:
   ```bash
   python app/main.py
   ```
5. **Access**: Open `http://localhost:8000` in your web browser.

## 📁 Project Structure
- `app/`: Core backend logic (FastAPI, LLM Services, PostgreSQL Schemas).
- `frontend/`: UI assets (HTML, CSS, JS, Logos).
- `data/`: Raw input datasets and processed markdown files.
- `docs/`: Technical architecture and system planning documentation.

---
*Built with ❤️ for Can Tho University students.*
