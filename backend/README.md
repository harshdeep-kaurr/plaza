# Plaza Backend

A comprehensive backend for the Plaza application that provides news article retrieval, summarization, conversation generation, bias detection, and interactive chat functionality.

## Features

- **News Article Retrieval**: Fetches articles from NewsAPI with topic categorization
- **AI-Powered Summarization**: Summarizes articles using OpenAI GPT or Anthropic Claude
- **Conversation Generation**: Creates multi-perspective conversations between different expert personas
- **Bias Detection**: Analyzes articles for potential bias using sentiment analysis and language patterns
- **Interactive Chat**: Allows users to ask questions and get responses from AI personas
- **CORS Support**: Configured to work with the frontend application

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the backend directory with:
```
NEWS_API_KEY=your_newsapi_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

3. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### GET /api/news
Fetches latest news articles with summaries and bias analysis.

**Query Parameters:**
- `q` (optional): Search query
- `days` (optional): Number of days back to fetch (default: 7)

**Response:**
```json
{
  "success": true,
  "articles": [
    {
      "id": 1,
      "title": "Article Title",
      "description": "Article description",
      "summary": "AI-generated summary",
      "topic": "Technology",
      "bias_analysis": {
        "bias_score": 45.2,
        "bias_type": "mixed",
        "confidence": 78.5
      },
      "url": "https://...",
      "source": "Source Name",
      "publishedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "total_articles": 10
}
```

### GET /api/topic/<topic_name>
Gets articles and generates conversation for a specific topic.

**Response:**
```json
{
  "success": true,
  "topic": "Technology",
  "articles": [...],
  "conversation": [
    {
      "speaker": "Dr. Sarah Chen (Nature)",
      "side": "left",
      "text": "Response text",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "facts": ["Fact 1", "Fact 2"]
}
```

### POST /api/chat
Handles user chat messages and generates AI responses.

**Request Body:**
```json
{
  "message": "User's question",
  "topic": "Technology",
  "history": [
    {
      "speaker": "User",
      "text": "Previous message",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "speaker": "Dr. Elena Patel (Scientific American)",
    "side": "left",
    "text": "AI response text",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### GET /api/bias/<article_id>
Gets detailed bias analysis for a specific article.

### GET /api/health
Health check endpoint.

## AI Personas

The system includes 8 different expert personas:

1. **Dr. Sarah Chen (Nature)** - Environmental scientist
2. **Mike Rodriguez (WSJ)** - Business reporter
3. **Dr. Elena Patel (Scientific American)** - Science journalist
4. **Leo (MIT Tech Review)** - Technology analyst
5. **Rin (Financial Times)** - International business correspondent
6. **Zoe (Nature)** - Research scientist
7. **Kai (AP)** - Fact-checking reporter
8. **Jules (FiveThirtyEight)** - Data journalist

## Bias Detection

The system analyzes articles for:
- Sentiment bias (positive/negative/neutral)
- Loaded language usage
- Subjective language patterns
- Source reliability indicators

## Dependencies

- Flask: Web framework
- OpenAI: AI text generation
- Anthropic: Alternative AI provider
- Transformers: Bias detection models
- TextBlob: Text processing
- NLTK: Natural language processing
- scikit-learn: Machine learning utilities

## Environment Variables

- `NEWS_API_KEY`: Required for fetching news articles
- `OPENAI_API_KEY`: Optional, for AI-powered features
- `ANTHROPIC_API_KEY`: Optional, alternative AI provider
- `HUGGINGFACE_API_TOKEN`: Optional, for enhanced bias detection

## CORS Configuration

The backend is configured with CORS to allow requests from the frontend running on different ports.