from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from textblob import TextBlob
import openai
from anthropic import Anthropic
# import numpy as np  # Removed for now to avoid build issues
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
except ImportError:
    print("Warning: scikit-learn not available, some features may be limited")
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Initialize AI clients
openai.api_key = OPENAI_API_KEY
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# NewsAPI configuration
NEWS_API_URL = 'https://newsapi.org/v2/everything'

# Initialize bias detection model (optional - requires transformers)
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    bias_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    bias_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
    bias_analyzer = pipeline("text-classification", model=bias_model, tokenizer=bias_tokenizer)
except Exception as e:
    print(f"Warning: Could not load bias detection model: {e}")
    bias_analyzer = None

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Personas for conversation generation
PERSONAS = {
    "Dr. Sarah Chen (Nature)": {
        "background": "Environmental scientist with expertise in climate research",
        "perspective": "Data-driven, focuses on peer-reviewed research and scientific consensus",
        "style": "Academic, precise, evidence-based"
    },
    "Mike Rodriguez (WSJ)": {
        "background": "Business and economics reporter for Wall Street Journal",
        "perspective": "Market-focused, emphasizes economic implications and business impact",
        "style": "Professional, analytical, business-oriented"
    },
    "Dr. Elena Patel (Scientific American)": {
        "background": "Science journalist specializing in emerging technologies",
        "perspective": "Interdisciplinary approach, explains complex science for general audience",
        "style": "Engaging, educational, accessible"
    },
    "Leo (MIT Tech Review)": {
        "background": "Technology analyst and innovation researcher",
        "perspective": "Future-focused, emphasizes technological potential and disruption",
        "style": "Forward-thinking, technical but accessible"
    },
    "Rin (Financial Times)": {
        "background": "International business correspondent",
        "perspective": "Global economic perspective, geopolitical implications",
        "style": "Sophisticated, international outlook, analytical"
    },
    "Zoe (Nature)": {
        "background": "Research scientist and peer review expert",
        "perspective": "Rigorous scientific methodology, replication and validation",
        "style": "Methodical, cautious, peer-review focused"
    },
    "Kai (AP)": {
        "background": "Associated Press reporter with fact-checking expertise",
        "perspective": "Neutral, fact-based reporting, multiple source verification",
        "style": "Objective, thorough, verification-focused"
    },
    "Jules (FiveThirtyEight)": {
        "background": "Data journalist and statistical analyst",
        "perspective": "Statistical analysis, data interpretation, probability assessment",
        "style": "Statistical, probabilistic, data-driven"
    }
}

# Topic keywords for categorization
TOPIC_KEYWORDS = {
    'Technology': [
        'artificial intelligence', 'ai', 'machine learning', 'tech', 'software', 'hardware',
        'computer', 'internet', 'digital', 'cyber', 'data', 'algorithm', 'app', 'startup',
        'innovation', 'robot', 'automation', 'blockchain', 'cryptocurrency', 'bitcoin',
        'programming', 'coding', 'developer', 'tech company', 'silicon valley'
    ],
    'Politics': [
        'election', 'government', 'president', 'congress', 'senate', 'vote', 'campaign',
        'policy', 'law', 'bill', 'legislation', 'democrat', 'republican', 'political',
        'parliament', 'minister', 'prime minister', 'mayor', 'governor', 'senator',
        'representative', 'cabinet', 'administration', 'federal', 'state', 'local'
    ],
    'Economy': [
        'economy', 'economic', 'market', 'stock', 'finance', 'financial', 'bank',
        'investment', 'trading', 'recession', 'inflation', 'gdp', 'unemployment',
        'business', 'corporate', 'company', 'earnings', 'profit', 'revenue',
        'dollar', 'currency', 'trade', 'export', 'import', 'budget', 'debt'
    ],
    'Health': [
        'health', 'medical', 'medicine', 'doctor', 'hospital', 'patient', 'disease',
        'treatment', 'drug', 'pharmaceutical', 'vaccine', 'covid', 'pandemic',
        'research', 'study', 'clinical', 'therapy', 'surgery', 'diagnosis',
        'healthcare', 'wellness', 'fitness', 'nutrition', 'mental health'
    ],
    'Environment': [
        'climate', 'environment', 'environmental', 'global warming', 'carbon',
        'emission', 'pollution', 'renewable', 'energy', 'solar', 'wind', 'green',
        'sustainability', 'conservation', 'wildlife', 'nature', 'forest', 'ocean',
        'weather', 'temperature', 'greenhouse', 'fossil fuel', 'clean energy'
    ],
    'Sports': [
        'sports', 'football', 'basketball', 'baseball', 'soccer', 'tennis', 'golf',
        'olympics', 'championship', 'tournament', 'game', 'match', 'player',
        'team', 'coach', 'league', 'season', 'playoff', 'victory', 'defeat',
        'athlete', 'training', 'fitness', 'stadium', 'arena'
    ],
    'Entertainment': [
        'movie', 'film', 'cinema', 'actor', 'actress', 'director', 'producer',
        'music', 'song', 'album', 'artist', 'singer', 'band', 'concert',
        'television', 'tv', 'show', 'series', 'episode', 'streaming', 'netflix',
        'hollywood', 'celebrity', 'award', 'oscar', 'grammy', 'entertainment'
    ],
    'Science': [
        'science', 'scientific', 'research', 'study', 'discovery', 'experiment',
        'laboratory', 'scientist', 'physics', 'chemistry', 'biology', 'space',
        'nasa', 'astronomy', 'universe', 'planet', 'moon', 'mars', 'earth',
        'evolution', 'genetics', 'dna', 'molecule', 'atom', 'quantum'
    ]
}

def categorize_article(title, description, content):
    """Categorize an article based on its title, description, and content."""
    text = f"{title} {description} {content}".lower()
    
    topic_scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        topic_scores[topic] = score
    
    if topic_scores:
        best_topic = max(topic_scores, key=topic_scores.get)
        if topic_scores[best_topic] > 0:
            return best_topic
    
    return 'General'

def fetch_news_articles(query=None, days_back=7, page_size=100):
    """Fetch news articles from NewsAPI."""
    if not NEWS_API_KEY:
        return []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    params = {
        'apiKey': NEWS_API_KEY,
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d'),
        'sortBy': 'popularity',
        'pageSize': page_size,
        'language': 'en'
    }
    
    if query:
        params['q'] = query
    
    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok':
            return data['articles']
        else:
            print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

def summarize_article(article):
    """Summarize an article using OpenAI or Anthropic."""
    content = article.get('content', '') or article.get('description', '')
    title = article.get('title', '')
    
    if not content:
        return article.get('description', '')[:200] + '...'
    
    # Truncate content if too long
    if len(content) > 3000:
        content = content[:3000] + "..."
    
    prompt = f"""
    Please provide a concise, neutral summary of this news article in 2-3 sentences:
    
    Title: {title}
    Content: {content}
    
    Summary:
    """
    
    try:
        if OPENAI_API_KEY:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        elif anthropic_client:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
    except Exception as e:
        print(f"Error summarizing article: {e}")
    
    # Fallback to description truncation
    return article.get('description', '')[:200] + '...'

def detect_bias(article):
    """Detect potential bias in an article."""
    content = article.get('content', '') or article.get('description', '')
    title = article.get('title', '')
    
    if not content:
        return {"bias_score": 0, "bias_type": "neutral", "confidence": 0}
    
    # Combine title and content for analysis
    full_text = f"{title} {content}"
    
    # Sentiment analysis
    sentiment_scores = sia.polarity_scores(full_text)
    
    # TextBlob sentiment
    blob = TextBlob(full_text)
    polarity = blob.sentiment.polarity
    
    # Analyze for loaded language and subjective language
    subjective_words = ['amazing', 'terrible', 'shocking', 'incredible', 'devastating', 'brilliant']
    loaded_words = ['controversial', 'scandal', 'crisis', 'breakthrough', 'failure', 'success']
    
    subjective_count = sum(1 for word in subjective_words if word.lower() in full_text.lower())
    loaded_count = sum(1 for word in loaded_words if word.lower() in full_text.lower())
    
    # Calculate bias score (0-100, higher = more biased)
    sentiment_bias = abs(sentiment_scores['compound']) * 50
    polarity_bias = abs(polarity) * 50
    language_bias = (subjective_count + loaded_count) * 5
    
    total_bias = min(sentiment_bias + polarity_bias + language_bias, 100)
    
    # Determine bias type
    if total_bias < 20:
        bias_type = "neutral"
    elif sentiment_scores['compound'] > 0.1:
        bias_type = "positive"
    elif sentiment_scores['compound'] < -0.1:
        bias_type = "negative"
    else:
        bias_type = "mixed"
    
    return {
        "bias_score": round(total_bias, 1),
        "bias_type": bias_type,
        "confidence": round(min(total_bias, 100), 1),
        "sentiment_breakdown": {
            "positive": round(sentiment_scores['pos'], 3),
            "negative": round(sentiment_scores['neg'], 3),
            "neutral": round(sentiment_scores['neu'], 3),
            "compound": round(sentiment_scores['compound'], 3)
        }
    }

def generate_conversation(articles, topic):
    """Generate a conversation between different personas based on articles."""
    if not articles:
        return []
    
    # Select 3-4 personas for the conversation
    selected_personas = list(PERSONAS.keys())[:4]
    
    conversation = []
    
    # Create initial context from articles
    article_summaries = []
    for article in articles[:3]:  # Use top 3 articles
        summary = summarize_article(article)
        article_summaries.append(f"- {article['title']}: {summary}")
    
    context = f"Recent news about {topic}:\n" + "\n".join(article_summaries)
    
    for i, persona_name in enumerate(selected_personas):
        persona = PERSONAS[persona_name]
        
        prompt = f"""
        You are {persona_name}, {persona['background']}.
        Your perspective: {persona['perspective']}
        Your communication style: {persona['style']}
        
        Context: {context}
        
        Please provide a brief comment (2-3 sentences) on this news from your perspective.
        Be authentic to your background and expertise. Don't repeat what others have said.
        """
        
        try:
            if OPENAI_API_KEY:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.7
                )
                message_text = response.choices[0].message.content.strip()
            elif anthropic_client:
                response = anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                message_text = response.content[0].text.strip()
            else:
                # Fallback responses
                fallback_responses = [
                    f"From my perspective as {persona['background']}, this development raises important questions about {topic}.",
                    f"As someone with expertise in {persona['background']}, I see both opportunities and challenges here.",
                    f"This is a complex issue that requires careful consideration from multiple angles, especially given my background in {persona['background']}."
                ]
                message_text = fallback_responses[i % len(fallback_responses)]
            
            conversation.append({
                "speaker": persona_name,
                "side": "left",
                "text": message_text,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error generating response for {persona_name}: {e}")
            # Add fallback message
            conversation.append({
                "speaker": persona_name,
                "side": "left",
                "text": f"As {persona['background']}, I believe this requires further analysis.",
                "timestamp": datetime.now().isoformat()
            })
    
    return conversation

def process_articles(articles):
    """Process and enhance articles with summaries and bias detection."""
    processed_articles = []
    
    for article in articles:
        if not article.get('title') or not article.get('description'):
            continue
        
        # Categorize the article
        topic = categorize_article(
            article.get('title', ''),
            article.get('description', ''),
            article.get('content', '')
        )
        
        # Generate summary
        summary = summarize_article(article)
        
        # Detect bias
        bias_analysis = detect_bias(article)
        
        processed_article = {
            'id': len(processed_articles) + 1,
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'content': article.get('content', ''),
            'url': article.get('url', ''),
            'urlToImage': article.get('urlToImage', ''),
            'publishedAt': article.get('publishedAt', ''),
            'source': article.get('source', {}).get('name', ''),
            'topic': topic,
            'summary': summary,
            'bias_analysis': bias_analysis
        }
        
        processed_articles.append(processed_article)
    
    return processed_articles

# API Endpoints

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get the latest news articles with summaries and bias analysis."""
    try:
        query = request.args.get('q', None)
        days_back = int(request.args.get('days', 7))
        
        articles = fetch_news_articles(query=query, days_back=days_back)
        
        if not articles:
            return jsonify({
                'success': False,
                'message': 'No articles found or NewsAPI key not configured',
                'articles': []
            })
        
        processed_articles = process_articles(articles)
        
        return jsonify({
            'success': True,
            'articles': processed_articles,
            'total_articles': len(processed_articles)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching news: {str(e)}',
            'articles': []
        }), 500

@app.route('/api/topic/<topic_name>', methods=['GET'])
def get_topic_data(topic_name):
    """Get articles and generate conversation for a specific topic."""
    try:
        # Fetch articles for the topic
        articles = fetch_news_articles(query=topic_name, days_back=7, page_size=20)
        processed_articles = process_articles(articles)
        
        # Filter articles by topic
        filtered_articles = [article for article in processed_articles 
                           if article['topic'].lower() == topic_name.lower()]
        
        # Generate conversation
        conversation = generate_conversation(filtered_articles, topic_name)
        
        # Create facts from article summaries
        facts = []
        for article in filtered_articles[:5]:
            facts.append(article['summary'])
        
        return jsonify({
            'success': True,
            'topic': topic_name,
            'articles': filtered_articles,
            'conversation': conversation,
            'facts': facts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching topic data: {str(e)}',
            'articles': [],
            'conversation': [],
            'facts': []
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle user chat messages and generate AI responses."""
    try:
        data = request.json
        user_message = data.get('message', '')
        topic = data.get('topic', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': 'No message provided'
            }), 400
        
        # Generate response from a random persona
        import random
        selected_persona = random.choice(list(PERSONAS.keys()))
        persona = PERSONAS[selected_persona]
        
        # Create context from conversation history
        history_context = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 messages
            history_context = "\n".join([f"{msg.get('speaker', 'User')}: {msg.get('text', '')}" 
                                       for msg in recent_messages])
        
        prompt = f"""
        You are {selected_persona}, {persona['background']}.
        Your perspective: {persona['perspective']}
        Your communication style: {persona['style']}
        
        Context about {topic}:
        {history_context}
        
        User's question: {user_message}
        
        Please provide a thoughtful response (2-3 sentences) from your perspective.
        Be authentic to your background and expertise.
        """
        
        try:
            if OPENAI_API_KEY:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content.strip()
            elif anthropic_client:
                response = anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_response = response.content[0].text.strip()
            else:
                ai_response = f"As {persona['background']}, I believe this is an important question that requires careful consideration from multiple perspectives."
        except Exception as e:
            print(f"Error generating AI response: {e}")
            ai_response = "I appreciate your question. This is a complex topic that deserves thoughtful analysis."
        
        return jsonify({
            'success': True,
            'response': {
                'speaker': selected_persona,
                'side': 'left',
                'text': ai_response,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing chat: {str(e)}'
        }), 500

@app.route('/api/bias/<article_id>', methods=['GET'])
def get_article_bias(article_id):
    """Get detailed bias analysis for a specific article."""
    try:
        # This would typically fetch from a database
        # For now, return a sample analysis
        return jsonify({
            'success': True,
            'article_id': article_id,
            'bias_analysis': {
                'bias_score': 45.2,
                'bias_type': 'mixed',
                'confidence': 78.5,
                'detailed_analysis': {
                    'sentiment': 'slightly negative',
                    'loaded_language': 'moderate',
                    'source_reliability': 'high',
                    'factual_claims': 'mostly verified'
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error analyzing bias: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'news_api_configured': bool(NEWS_API_KEY),
        'openai_configured': bool(OPENAI_API_KEY),
        'anthropic_configured': bool(ANTHROPIC_API_KEY),
        'bias_detection_available': bias_analyzer is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)