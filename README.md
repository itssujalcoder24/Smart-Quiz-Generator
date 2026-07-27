🧠 Smart Quiz Generator
AI-Powered Quiz Generator for DPES AI/ML Club
Created With ❤️ By Sujal Das
Turn your study notes into interactive quizzes instantly!
https://python.org
https://fastapi.tiangolo.com
https://streamlit.io
LICENSE
✨ Features
🤖 AI-Powered Question Generation — Uses Flan-T5 (220M params) to generate contextual MCQs from your notes
📄 Multi-Format Support — Upload PDF, TXT, or paste text directly
🎯 Smart Difficulty Levels — Easy, Medium, Hard questions tailored to your content
💡 Instant Explanations — Learn from detailed explanations for every answer
📊 Performance Analytics — Track your progress with score breakdowns and topic analysis
🎨 Beautiful UI — Modern gradient design with interactive components
🐳 Docker Ready — One-command deployment with Docker Compose
🔄 Mock Mode — Works offline with built-in demo quiz data
🏗️ Architecture
plain
┌─────────────────┐     HTTP      ┌──────────────────┐
│   Streamlit     │◄────────────►│    FastAPI       │
│   Frontend      │   (8501)     │    Backend       │
│   (app.py)      │              │    (main.py)     │
└─────────────────┘              └────────┬─────────┘
                                            │
                              ┌─────────────┼─────────────┐
                              │             │             │
                        ┌─────▼─────┐ ┌─────▼─────┐ ┌────▼────┐
                        │  PDF/Text │ │  Flan-T5  │ │ SQLite  │
                        │ Extractor │ │   LLM     │ │   DB    │
                        └───────────┘ └───────────┘ └─────────┘
🚀 Quick Start
Prerequisites
Python 3.11+
pip
Git
1. Clone & Setup
bash
git clone <your-repo-url>
cd smart-quiz-generator

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
2. Install Dependencies
bash
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
3. Run the Application
Open two terminal windows (both with venv activated):
Terminal 1 — Backend:
bash
cd backend
uvicorn main:app --reload --port 8000
Terminal 2 — Frontend:
bash
cd frontend
streamlit run app.py --server.port 8501
4. Open in Browser
🌐 Frontend: http://localhost:8501
📡 Backend API Docs: http://localhost:8000/docs
🔍 Backend Health: http://localhost:8000/health
🐳 Docker Deployment
Option 1: Docker Compose (Recommended)
bash
# Build and start all services
cd docker
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
Option 2: Individual Containers
bash
# Build backend
docker build -f docker/Dockerfile.backend -t sqg-backend .

# Build frontend
docker build -f docker/Dockerfile.frontend -t sqg-frontend .

# Run backend
docker run -p 8000:8000 sqg-backend

# Run frontend
docker run -p 8501:8501 -e BACKEND_URL=http://host.docker.internal:8000 sqg-frontend
📁 Project Structure
plain
smart-quiz-generator/
├── 📂 backend/              # FastAPI Backend
│   ├── main.py              # App entry point
│   ├── config.py            # Settings & env vars
│   ├── dependencies.py      # Shared dependencies
│   ├── 📂 api/routes/       # REST API endpoints
│   │   ├── upload.py        # File upload & processing
│   │   ├── quiz.py          # Quiz generation & retrieval
│   │   ├── answer.py        # Answer submission & scoring
│   │   └── results.py       # Results & analytics
│   ├── 📂 api/models/       # Pydantic schemas
│   ├── 📂 core/             # Business logic
│   │   ├── pdf_extractor.py      # PDF text extraction
│   │   ├── text_processor.py     # Text cleaning & chunking
│   │   ├── question_generator.py # LLM-based QG engine
│   │   ├── distractor_generator.py # Wrong option generator
│   │   └── quiz_engine.py        # Quiz scoring logic
│   ├── 📂 ml/               # ML Model Layer
│   │   ├── model_loader.py  # Load Flan-T5/Phi-2
│   │   ├── inference.py     # LLM inference wrapper
│   │   └── prompts.py       # Prompt templates
│   ├── 📂 db/               # Database Layer
│   │   ├── database.py      # SQLAlchemy connection
│   │   ├── models.py        # ORM models
│   │   └── crud.py          # Database operations
│   └── 📂 utils/            # Helper utilities
│
├── 📂 frontend/             # Streamlit Frontend
│   ├── app.py               # Main app & routing
│   ├── 📂 pages/            # Page components
│   │   ├── upload_page.py   # File upload UI
│   │   ├── quiz_page.py     # Quiz taking UI
│   │   └── results_page.py  # Results & review UI
│   └── 📂 components/       # Reusable UI components
│       ├── sidebar.py       # Navigation sidebar
│       ├── progress_bar.py  # Progress indicators
│       └── feedback_card.py # Answer feedback cards
│
├── 📂 docker/               # Docker configs
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── 📂 tests/                # Test suite
│   ├── test_api.py          # API endpoint tests
│   └── test_ml.py           # ML model tests
│
├── 📂 models/               # Downloaded model weights (gitignored)
├── 📂 data/                 # Uploaded files (gitignored)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
⚙️ Configuration
Copy .env.example to .env and customize:
bash
cp .env.example .env
Table
Variable	Default	Description
BACKEND_URL	http://localhost:8000	Backend API URL
DATABASE_URL	sqlite:///./quiz.db	Database connection
MODEL_NAME	google/flan-t5-base	HuggingFace model ID
MODEL_CACHE_DIR	./models	Local model storage
DEBUG	true	Debug mode
LOG_LEVEL	info	Logging level
🧪 Running Tests
bash
# Run all tests
pytest tests/ -v

# Run API tests only
pytest tests/test_api.py -v

# Run ML tests only
pytest tests/test_ml.py -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
🛠️ Tech Stack
Table
Layer	Technology
Frontend	Streamlit 1.36+
Backend	FastAPI 0.111+
Server	Uvicorn + Gunicorn
ML Model	Flan-T5-Base (220M) via Transformers
NLP	spaCy, Sentence-Transformers
PDF Parsing	pdfplumber, PyMuPDF
Database	SQLite (PostgreSQL ready)
Container	Docker + Docker Compose
Testing	pytest, TestClient
🎯 Roadmap
[x] Frontend UI (Streamlit)
[x] Docker deployment
[x] Test suite
[ ] Backend API (FastAPI)
[ ] ML Model integration (Flan-T5)
[ ] PDF text extraction
[ ] Database persistence
[ ] User authentication
[ ] Quiz history & analytics
[ ] Multi-language support
[ ] Cloud deployment (AWS/GCP)
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
👥 Team
DPES AI/ML Club
Dhole Patil College of Engineering
Advisor: Prof. Yugashree Pawar
📄 License
This project is licensed under the MIT License.
🙏 Acknowledgments
Hugging Face for Flan-T5 model
Streamlit for the amazing frontend framework
FastAPI for the blazing-fast backend
DPES for supporting the AI/ML Club
<p align="center">
  Made with 💜 by Sujal Das, AI/ML Club, DPES<br>
  <i>"Learning by doing, one quiz at a time!"</i>
</p>