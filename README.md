# Plaza - Multi-Perspective News Discussion Platform

Plaza is a news discussion platform that fetches real-time articles, generates AI-powered conversations between different expert personas, and provides bias detection for news content.

## 🚀 Quick Start

1. **Set up API keys** in `backend/.env`:
   ```
   NEWS_API_KEY=your_newsapi_key
   OPENAI_API_KEY=your_openai_key (optional)
   ANTHROPIC_API_KEY=your_anthropic_key (optional)
   ```

2. **Run the application**:
   ```bash
   ./start.sh
   ```

3. **Access the app**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## 📁 Project Structure

```
plaza/
├── backend/           # Python Flask backend
│   ├── app.py        # Main application with AI features
│   ├── requirements.txt
│   ├── .env          # API keys (create this)
│   └── README.md     # Backend documentation
├── frontend/          # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── start.sh           # Startup script for both servers
├── SETUP.md           # Detailed setup guide
└── README.md          # This file
```

## ✨ Features

- **Real-time News**: Fetches articles from NewsAPI
- **AI Summarization**: Summarizes articles using OpenAI GPT or Anthropic Claude
- **Multi-perspective Conversations**: 8 expert personas discuss topics
- **Bias Detection**: Analyzes articles for potential bias
- **Interactive Chat**: Users can ask questions and get AI responses

## 📚 Documentation

- **SETUP.md** - Complete setup and usage guide
- **backend/README.md** - Backend API documentation

## 🛠️ Development

See `SETUP.md` for detailed setup instructions and API documentation.