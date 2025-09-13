# Plaza Application Setup Guide

## Overview

Plaza is a news discussion platform that fetches real-time articles, generates AI-powered conversations between different expert personas, and provides bias detection for news content.

## Features

- **Real-time News**: Fetches articles from NewsAPI
- **AI Summarization**: Summarizes articles using OpenAI GPT or Anthropic Claude
- **Multi-perspective Conversations**: 8 different expert personas discuss topics
- **Bias Detection**: Analyzes articles for potential bias
- **Interactive Chat**: Users can ask questions and get AI responses
- **Modern UI**: Clean, responsive interface with Tailwind CSS

## Quick Start

### 1. Set up Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required: Get from https://newsapi.org/
NEWS_API_KEY=your_newsapi_key_here

# Optional: For AI features (get from https://openai.com/ or https://anthropic.com/)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Install Dependencies

#### Backend (Python)
```bash
cd plaza/backend
pip install -r requirements.txt
```

#### Frontend (Node.js)
```bash
cd plaza/frontend
npm install
```

### 3. Run the Application

#### Option A: Use the startup script
```bash
cd plaza
./start.sh
```

#### Option B: Run manually

Terminal 1 (Backend):
```bash
cd plaza/backend
python app.py
```

Terminal 2 (Frontend):
```bash
cd plaza/frontend
npm start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001

## API Keys Setup

### NewsAPI (Required)
1. Go to https://newsapi.org/
2. Sign up for a free account
3. Copy your API key
4. Add it to `plaza/backend/.env` as `NEWS_API_KEY=your_key`

### OpenAI (Optional - for AI features)
1. Go to https://openai.com/
2. Create an account and get API access
3. Generate an API key
4. Add it to `plaza/backend/.env` as `OPENAI_API_KEY=your_key`

### Anthropic (Optional - alternative AI provider)
1. Go to https://anthropic.com/
2. Sign up for API access
3. Generate an API key
4. Add it to `plaza/backend/.env` as `ANTHROPIC_API_KEY=your_key`

## How It Works

### 1. News Fetching
- Backend fetches articles from NewsAPI
- Articles are categorized by topic (Technology, Politics, etc.)
- Each article is summarized using AI

### 2. Conversation Generation
- AI personas discuss topics based on recent news
- 8 different expert perspectives:
  - Dr. Sarah Chen (Nature) - Environmental scientist
  - Mike Rodriguez (WSJ) - Business reporter
  - Dr. Elena Patel (Scientific American) - Science journalist
  - Leo (MIT Tech Review) - Technology analyst
  - Rin (Financial Times) - International business correspondent
  - Zoe (Nature) - Research scientist
  - Kai (AP) - Fact-checking reporter
  - Jules (FiveThirtyEight) - Data journalist

### 3. Bias Detection
- Analyzes articles for sentiment bias
- Detects loaded language and subjective terms
- Provides bias scores and confidence levels

### 4. Interactive Chat
- Users can ask questions about topics
- AI personas respond based on their expertise
- Responses are contextual and persona-specific

## API Endpoints

- `GET /api/news` - Fetch latest news articles
- `GET /api/topic/<topic>` - Get topic-specific data and conversation
- `POST /api/chat` - Send user message and get AI response
- `GET /api/bias/<article_id>` - Get bias analysis for article
- `GET /api/health` - Health check

## Troubleshooting

### Backend Issues
- Check that all API keys are set correctly
- Ensure Python dependencies are installed
- Check console for error messages

### Frontend Issues
- Ensure Node.js dependencies are installed
- Check browser console for errors
- Verify backend is running on port 5000

### API Issues
- NewsAPI has rate limits on free tier
- OpenAI/Anthropic keys may have usage limits
- Check API key validity and permissions

## Development

### Backend Structure
- `plaza/backend/app.py` - Main Flask application
- `plaza/backend/requirements.txt` - Python dependencies
- `plaza/backend/.env` - Environment variables

### Frontend Structure
- `plaza/frontend/src/App.js` - Main React component
- `plaza/frontend/src/data/` - Static data files
- `plaza/frontend/package.json` - Node.js dependencies

### Project Structure
```
plaza/
├── backend/           # Python Flask backend
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   └── README.md
├── frontend/          # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── start.sh           # Startup script
├── SETUP.md           # Setup guide
└── README.md          # Project overview
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect API terms of service and rate limits.