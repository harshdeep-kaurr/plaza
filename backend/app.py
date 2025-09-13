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

def extract_subtopics(articles, topic_name):
    """Extract subtopics from articles using keyword clustering and AI analysis."""
    if not articles:
        return []
    
    # Common subtopic patterns for different topics
    subtopic_patterns = {
        'business': [
            'IPO', 'earnings', 'merger', 'acquisition', 'layoffs', 'hiring', 'stock', 'market',
            'startup', 'funding', 'venture capital', 'cryptocurrency', 'bitcoin', 'tesla',
            'apple', 'google', 'microsoft', 'amazon', 'meta', 'netflix', 'uber', 'airbnb'
        ],
        'technology': [
            'AI', 'artificial intelligence', 'machine learning', 'chatgpt', 'openai', 'google',
            'apple', 'microsoft', 'meta', 'tesla', 'spacex', 'quantum', 'blockchain',
            'cybersecurity', 'data privacy', 'algorithm', 'software', 'hardware'
        ],
        'sports': [
            'nfl', 'nba', 'mlb', 'nhl', 'soccer', 'football', 'basketball', 'baseball',
            'olympics', 'world cup', 'championship', 'playoff', 'draft', 'trade',
            'injury', 'contract', 'salary', 'coach', 'player'
        ],
        'health': [
            'covid', 'vaccine', 'pandemic', 'mental health', 'cancer', 'diabetes',
            'heart disease', 'alzheimer', 'dementia', 'depression', 'anxiety',
            'medication', 'treatment', 'research', 'clinical trial'
        ],
        'politics': [
            'election', 'president', 'congress', 'senate', 'house', 'bill', 'law',
            'policy', 'immigration', 'healthcare', 'economy', 'tax', 'budget',
            'supreme court', 'justice', 'federal', 'state', 'local'
        ],
        'entertainment': [
            'movie', 'film', 'netflix', 'disney', 'hbo', 'streaming', 'oscar',
            'grammy', 'emmy', 'music', 'album', 'concert', 'tour', 'celebrity',
            'actor', 'actress', 'director', 'producer'
        ]
    }
    
    # Get patterns for this topic
    patterns = subtopic_patterns.get(topic_name.lower(), [])
    
    # Group articles by subtopics
    subtopic_groups = {}
    
    for article in articles:
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}"
        
        # Find matching patterns
        matched_patterns = []
        for pattern in patterns:
            if pattern.lower() in content:
                matched_patterns.append(pattern)
        
        # If no specific pattern matches, try to extract key entities
        if not matched_patterns:
            # Simple keyword extraction - look for capitalized words that might be entities
            words = title.split()
            for word in words:
                if len(word) > 3 and word[0].isupper() and word.isalpha():
                    matched_patterns.append(word)
        
        # Group by the first matching pattern or use a generic category
        if matched_patterns:
            subtopic_key = matched_patterns[0]
        else:
            subtopic_key = 'general'
        
        if subtopic_key not in subtopic_groups:
            subtopic_groups[subtopic_key] = []
        subtopic_groups[subtopic_key].append(article)
    
    # Convert to subtopic format
    subtopics = []
    for i, (key, articles_list) in enumerate(subtopic_groups.items()):
        if len(articles_list) >= 2:  # Only include subtopics with at least 2 articles
            # Create a title for the subtopic
            if key == 'general':
                subtopic_title = f"General {topic_name.title()} News"
            else:
                subtopic_title = f"{key.title()} News"
            
            # Get the most recent article for preview
            latest_article = max(articles_list, key=lambda x: x.get('publishedAt', ''))
            
            subtopics.append({
                'id': f"{topic_name}_{key}_{i}",
                'title': subtopic_title,
                'description': latest_article.get('description', '')[:150] + '...',
                'article_count': len(articles_list),
                'latest_article': latest_article,
                'articles': articles_list[:5],  # Limit to top 5 articles
                'created_at': datetime.now().isoformat()
            })
    
    # Sort by article count (most active subtopics first)
    subtopics.sort(key=lambda x: x['article_count'], reverse=True)
    
    return subtopics[:8]  # Return top 8 subtopics

def generate_conversation(articles, topic):
    """Generate a casual texting conversation based on article opinions using Anthropic."""
    if not articles:
        return []
    
    # Create context from articles with their opinions/sentiment
    article_contexts = []
    for article in articles[:5]:  # Use top 5 articles
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        source = article.get('source', 'Unknown')
        
        # Get bias/sentiment analysis
        bias_analysis = article.get('bias_analysis', {})
        sentiment = bias_analysis.get('bias_type', 'neutral')
        
        article_contexts.append(f"""
Article: {title}
Source: {source}
Content: {description[:300]}...
Sentiment: {sentiment}
""")
    
    context = f"Recent news articles about {topic}:\n" + "\n".join(article_contexts)
    
    # Create casual conversation prompt
    prompt = f"""
You are creating a short casual texting conversation between different news sources discussing these articles.

{context}

Create a casual, natural texting conversation (max one sentence per person) where each news source reacts to the articles with their typical perspective and tone. Use:
- Casual, conversational language
- Different perspectives from each source
- References to the actual articles
- Natural conversation flow
- Max 6-8 messages total

IMPORTANT: Return ONLY a valid JSON array in this exact format:
[
  {{"speaker": "Source Name", "side": "left", "text": "message", "timestamp": "2024-01-15T10:30:00Z"}},
  {{"speaker": "Another Source", "side": "left", "text": "another message", "timestamp": "2024-01-15T10:31:00Z"}}
]

Make it sound like a natural, casual conversation about news - engaging and authentic.
"""
    
    try:
        if anthropic_client:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text.strip()
            
            # Try to parse JSON response
            try:
                import json
                # Clean up the response text to extract JSON
                if '[' in response_text and ']' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    json_text = response_text[start:end]
                    conversation = json.loads(json_text)
                else:
                    conversation = json.loads(response_text)
                
                # Add timestamps if missing and ensure proper format
                for i, msg in enumerate(conversation):
                    if 'timestamp' not in msg:
                        msg['timestamp'] = datetime.now().isoformat()
                    if 'side' not in msg:
                        msg['side'] = 'left'
                
                return conversation
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parsing failed: {e}")
                # If JSON parsing fails, create conversation from text
                return create_fallback_conversation(response_text, articles)
                
        elif OPENAI_API_KEY:
            # Fallback to OpenAI if Anthropic not available
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.8
            )
            response_text = response.choices[0].message.content.strip()
            return create_fallback_conversation(response_text, articles)
        else:
            # No AI available, create basic conversation
            return create_basic_conversation(articles, topic)
            
    except Exception as e:
        print(f"Error generating Gen Z conversation: {e}")
        return create_basic_conversation(articles, topic)

def create_fallback_conversation(response_text, articles):
    """Create conversation from AI response text when JSON parsing fails."""
    # Extract potential messages from the response
    lines = response_text.split('\n')
    conversation = []
    
    # Simple extraction of quoted text or lines that look like messages
    for i, line in enumerate(lines):
        line = line.strip()
        if line and ('"' in line or ':' in line) and len(line) > 10:
            # Extract speaker and message
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip().replace('"', '').replace('*', '')
                    message = parts[1].strip().replace('"', '')
                    
                    if len(message) > 5:  # Valid message
                        conversation.append({
                            "speaker": speaker,
                            "side": "left",
                            "text": message,
                            "timestamp": datetime.now().isoformat()
                        })
    
    # If we didn't get enough messages, add some basic ones
    if len(conversation) < 3:
        conversation.extend(create_basic_conversation(articles, "news")[:3-len(conversation)])
    
    return conversation[:6]  # Max 6 messages

def create_basic_conversation(articles, topic):
    """Create a basic conversation when AI is not available."""
    if not articles:
        return []
    
    # Get unique sources from articles
    sources = list(set([article.get('source', 'News Source') for article in articles[:4]]))
    if len(sources) < 2:
        sources = ['TechCrunch', 'Reuters', 'Associated Press', 'Wall Street Journal'][:len(sources)+2]
    
    conversation = []
    casual_responses = [
        "This is really interesting stuff",
        "I'm not sure what to make of this",
        "This seems concerning to me",
        "Why isn't this getting more attention?",
        "This is actually pretty fascinating",
        "This is crazy news",
        "What does this mean for everyone?",
        "This is making me worried",
        "This is actually a big deal",
        "This is pretty exciting news"
    ]
    
    for i, source in enumerate(sources[:4]):
        if i < len(casual_responses):
            conversation.append({
                "speaker": source,
                "side": "left",
                "text": casual_responses[i],
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

@app.route('/api/subtopics/<topic_name>', methods=['GET'])
def get_subtopics(topic_name):
    """Get subtopics and headlines for a main topic (e.g., Business -> Figma IPO, Tesla earnings, etc.)."""
    try:
        # Fetch articles for the topic
        articles = fetch_news_articles(query=topic_name, days_back=7, page_size=50)
        processed_articles = process_articles(articles)
        
        # Filter articles by topic
        filtered_articles = [article for article in processed_articles 
                           if article['topic'].lower() == topic_name.lower()]
        
        # Group articles by subtopics using clustering or keyword extraction
        subtopics = extract_subtopics(filtered_articles, topic_name)
        
        return jsonify({
            'success': True,
            'topic': topic_name,
            'subtopics': subtopics,
            'total_articles': len(filtered_articles)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching subtopics: {str(e)}',
            'subtopics': []
        }), 500

@app.route('/api/subtopic/<topic_name>/<subtopic_id>', methods=['GET'])
def get_subtopic_data(topic_name, subtopic_id):
    """Get articles and conversation for a specific subtopic."""
    try:
        # Fetch articles for the main topic
        articles = fetch_news_articles(query=topic_name, days_back=7, page_size=50)
        processed_articles = process_articles(articles)
        
        # Filter articles by topic
        filtered_articles = [article for article in processed_articles 
                           if article['topic'].lower() == topic_name.lower()]
        
        # Get subtopics to find the specific one
        subtopics = extract_subtopics(filtered_articles, topic_name)
        target_subtopic = None
        
        for subtopic in subtopics:
            if subtopic['id'] == subtopic_id:
                target_subtopic = subtopic
                break
        
        if not target_subtopic:
            return jsonify({
                'success': False,
                'message': 'Subtopic not found'
            }), 404
        
        # Get articles for this specific subtopic
        subtopic_articles = target_subtopic.get('articles', [])
        
        # Generate conversation for this subtopic
        conversation = generate_conversation(subtopic_articles, target_subtopic['title'])
        
        return jsonify({
            'success': True,
            'topic': topic_name,
            'subtopic': target_subtopic,
            'articles': subtopic_articles,
            'conversation': conversation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching subtopic data: {str(e)}',
            'articles': [],
            'conversation': []
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle user chat messages and generate AI responses."""
    try:
        data = request.json
        user_message = data.get('message', '')
        topic = data.get('topic', '')
        subtopic = data.get('subtopic', '')
        articles = data.get('articles', [])
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
        
        # Create context from articles if available
        articles_context = ""
        if articles:
            article_summaries = []
            for article in articles[:3]:  # Use top 3 articles
                summary = article.get('summary', article.get('description', ''))[:200]
                article_summaries.append(f"- {article.get('title', '')}: {summary}")
            articles_context = f"Relevant articles:\n" + "\n".join(article_summaries)
        
        # Build the full context
        full_context = f"Topic: {topic}"
        if subtopic:
            full_context += f"\nSubtopic: {subtopic}"
        if articles_context:
            full_context += f"\n{articles_context}"
        if history_context:
            full_context += f"\nRecent conversation:\n{history_context}"
        
        prompt = f"""
        You are {selected_persona}, {persona['background']}.
        Your perspective: {persona['perspective']}
        Your communication style: {persona['style']}
        
        Context:
        {full_context}
        
        User's question: {user_message}
        
        Respond in a casual, conversational style (max one sentence) with your perspective on this topic.
        Use natural, friendly language that's easy to understand.
        If there are relevant articles mentioned in the context, reference them briefly.
        Be authentic to your background but keep it conversational and engaging.
        """
        
        try:
            if anthropic_client:
                response = anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_response = response.content[0].text.strip()
            elif OPENAI_API_KEY:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.8
                )
                ai_response = response.choices[0].message.content.strip()
            else:
                ai_response = f"This is actually pretty interesting from my perspective as {persona['background']}"
        except Exception as e:
            print(f"Error generating AI response: {e}")
            ai_response = "This is a complex topic but I'm having some technical difficulties right now"
        
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