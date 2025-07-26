# 🧩 Resume AI Matcher

A Streamlit application that uses AI to match resumes against job descriptions, providing detailed analysis and scoring.

## ✨ Features

### 📄 Resume Upload & Parsing
- **Drag-and-drop PDF upload** interface
- **Intelligent text extraction** from PDF resumes
- **Structured data parsing** (name, email, skills, experience)
- **Real-time preview** of extracted information

### 💼 Job Description Handling
- **Upload existing job descriptions** (PDF/text)
- **Manual job description input**
- **AI-powered job description generation** from role and keywords
- **Flexible input methods** for different use cases

### 🤖 AI-Powered Matching
- **Intelligent resume-job matching** using Mistral AI (configurable to OpenAI)
- **Comprehensive scoring system** (0-100 scale)
- **Skills overlap analysis**
- **Experience relevance assessment**
- **Detailed feedback and recommendations**

### 📊 Results & Analytics
- **Visual score dashboard** with gauge charts
- **Detailed breakdown** of strengths and weaknesses
- **Missing skills identification**
- **Actionable improvement recommendations**
- **Downloadable reports** (planned feature)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Mistral AI API key (or OpenAI API key)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Capstone
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the template
   cp env_template.txt .env
   
   # Edit .env and add your API key
   MISTRAL_API_KEY=your_actual_mistral_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📋 Usage Guide

### Step 1: Upload Resume
1. Click "1. Upload Resume" in the sidebar
2. Drag and drop your PDF resume or click to browse
3. The app will automatically parse and extract information
4. Review the extracted data in the preview

### Step 2: Provide Job Description
Choose one of three options:
- **Upload**: Upload an existing job description file
- **Type**: Manually enter the job description
- **Generate**: Use AI to create a job description from role and keywords

### Step 3: AI Matching
1. Click "3. AI Matching" in the sidebar
2. Click "Start AI Matching" to begin analysis
3. Wait for the AI to process and score the match

### Step 4: Review Results
- View the overall match score (0-100%)
- Analyze skills match and experience relevance
- Review strengths and areas for improvement
- Get actionable recommendations

## 🔧 Configuration

### Environment Variables

Edit your `.env` file to configure the application:

```env
# API Keys
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional

# AI Model Configuration
AI_MODEL_PROVIDER=mistral  # Change to 'openai' to switch providers
MISTRAL_MODEL=mistral-large-latest
OPENAI_MODEL=gpt-4

# Application Settings
NODE_ENV=development
PORT=8501
MAX_FILE_SIZE=10485760  # 10MB
```

### Switching AI Providers

To switch from Mistral to OpenAI:

1. Update your `.env` file:
   ```env
   AI_MODEL_PROVIDER=openai
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Restart the application

## 🏗️ Architecture

### Core Components

- **ResumeParser**: Handles PDF text extraction and structured data parsing
- **AIMatcher**: Manages AI API calls and matching logic
- **Streamlit UI**: Provides the user interface and navigation

### AI Integration

- **Mistral AI**: Primary AI provider for job description generation and matching
- **OpenAI**: Alternative provider (easily configurable)
- **Fallback Logic**: Graceful degradation when AI services are unavailable

### Data Flow

1. **PDF Upload** → Text Extraction → Structured Parsing
2. **Job Description** → Input/Generation → Storage
3. **AI Matching** → Analysis → Scoring → Results
4. **Results Display** → Visualization → Recommendations

## 🛠️ Development

### Project Structure
```
Capstone/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── env_template.txt    # Environment variables template
├── README.md          # This file
└── .env               # Your environment variables (create from template)
```

### Adding Features

The application is modular and easily extensible:

- **New AI Providers**: Add methods to `AIMatcher` class
- **Enhanced Parsing**: Extend `ResumeParser` with more sophisticated NLP
- **Additional Visualizations**: Add new Plotly charts to results page
- **Export Features**: Implement PDF report generation

### Testing

```bash
# Install test dependencies
pip install pytest streamlit-testing

# Run tests (when implemented)
pytest tests/
```

## 🔒 Security & Privacy

- **Local Processing**: All file processing happens locally
- **No Data Storage**: Files are processed in memory, not stored
- **API Key Security**: Use environment variables for sensitive data
- **Session Management**: Streamlit handles session state securely

## 🚧 Planned Features

- [ ] **PDF Report Generation**: Download detailed analysis reports
- [ ] **Resume Enhancement**: AI-powered suggestions for resume improvement
- [ ] **Batch Processing**: Handle multiple resumes at once
- [ ] **Advanced NLP**: More sophisticated resume parsing
- [ ] **Custom Scoring**: Configurable matching criteria
- [ ] **Database Integration**: Save and compare multiple matches
- [ ] **Email Integration**: Send results via email

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the console for error messages
2. Verify your API keys are correctly set
3. Ensure all dependencies are installed
4. Check that your PDF files are not corrupted

For additional help, please open an issue on the repository.

---

**Built with ❤️ using Streamlit and AI** 