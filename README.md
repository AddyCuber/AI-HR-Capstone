# Resume AI Matcher Pro - Full Stack Application

A modern full-stack application that provides AI-powered resume analysis and job matching capabilities. Built with Next.js frontend and FastAPI backend.

## 🚀 Features

- **📄 Resume Upload & Parsing**: Support for PDF, DOCX, and TXT files with advanced text extraction
- **💼 Job Description Management**: Generate job descriptions with AI or upload existing ones
- **🤖 AI-Powered Analysis**: Advanced matching algorithms with detailed insights
- **📊 Interactive Visualizations**: Beautiful charts and metrics using Plotly.js
- **🎯 Detailed Results**: Comprehensive analysis with strengths, weaknesses, and suggestions
- **🔧 Resume Enhancement**: Actionable suggestions to improve your resume
- **📱 Modern UI**: Clean, responsive design with Tailwind CSS

## 🏗️ Architecture

### Frontend (Next.js)
- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS with custom components
- **Visualizations**: Plotly.js for interactive charts
- **Icons**: Lucide React for beautiful icons
- **State Management**: React hooks for local state

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **PDF Processing**: PyMuPDF, pdfplumber, PyPDF2
- **AI Integration**: Mistral AI and OpenAI APIs
- **Document Processing**: python-docx for DOCX files
- **CORS**: Configured for frontend communication

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose (optional)

## 🛠️ Installation & Setup

### Option 1: Local Development

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MISTRAL_API_KEY="your_mistral_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export AI_MODEL_PROVIDER="mistral"  # or "openai"

# Run the backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variable
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# Run the frontend
npm run dev
```

### Option 2: Docker Setup

```bash
# Clone the repository
git clone <repository-url>
cd resume-ai-matcher-pro

# Create .env file with your API keys
echo "MISTRAL_API_KEY=your_mistral_api_key" > .env
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "AI_MODEL_PROVIDER=mistral" >> .env

# Run with Docker Compose
docker-compose up --build
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📚 API Endpoints

### Resume Upload
- `POST /upload-resume` - Upload and parse resume file

### Job Description
- `POST /generate-job-description` - Generate job description with AI

### Analysis
- `POST /match-resume` - Match resume to job description
- `POST /enhance-resume` - Generate resume enhancement suggestions

## 🎯 Usage

1. **Upload Resume**: Drag and drop or select your resume file (PDF, DOCX, TXT)
2. **Add Job Description**: Generate with AI, upload a file, or type manually
3. **Run Analysis**: Click "Start AI Analysis" to process your resume
4. **Review Results**: View detailed analysis with interactive charts and suggestions

## 🔧 Configuration

### Environment Variables

#### Backend
- `MISTRAL_API_KEY`: Your Mistral AI API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `AI_MODEL_PROVIDER`: Choose between "mistral" or "openai"

#### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## 📁 Project Structure

```
resume-ai-matcher-pro/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend Docker configuration
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main page component
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   ├── ResumeUpload.tsx # Resume upload component
│   │   ├── JobDescriptionInput.tsx # Job description input
│   │   └── AnalysisResults.tsx # Results display
│   ├── lib/
│   │   └── api.ts           # API client
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Frontend Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md               # This file
```

## 🚀 Deployment

### Production Build

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run build
npm start
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## 🔍 Development

### Backend Development
- FastAPI with automatic API documentation
- Hot reload enabled for development
- Comprehensive error handling
- Async support for better performance

### Frontend Development
- Next.js with TypeScript
- Tailwind CSS for styling
- Component-based architecture
- Responsive design

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Features in Detail

### Resume Parsing
- Multi-format support (PDF, DOCX, TXT)
- Advanced text extraction using PyMuPDF
- Fallback mechanisms for complex documents
- Structured data extraction (skills, experience, education)

### AI Analysis
- Skill matching with weighted scoring
- Experience alignment analysis
- Project relevance assessment
- Detailed reasoning and suggestions

### Interactive Visualizations
- Gauge charts for match scores
- Progress indicators
- Responsive design for all devices
- Real-time data updates

### Resume Enhancement
- Actionable improvement suggestions
- Power verbs and quantified achievements
- Skill gap analysis
- Formatting recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.

## 🔮 Roadmap

- [ ] PDF annotation with highlights
- [ ] Advanced explainable AI analysis
- [ ] Resume template generation
- [ ] Multi-language support
- [ ] Integration with job boards
- [ ] Advanced analytics dashboard 