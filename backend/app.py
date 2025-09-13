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

# Random names for conversation participants
RANDOM_NAMES = [
    "Alex", "Jordan", "Casey", "Riley", "Morgan", "Taylor", "Avery", "Quinn",
    "Sage", "River", "Dakota", "Phoenix", "Blake", "Cameron", "Drew", "Emery",
    "Finley", "Hayden", "Jamie", "Kendall", "Logan", "Parker", "Reese", "Sage",
    "Skyler", "Tatum", "Val", "Wren", "Zion", "Ari", "Briar", "Cedar"
]

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

def get_random_name():
    """Get a random name for conversation participants."""
    import random
    return random.choice(RANDOM_NAMES)

def clean_json_string(json_str):
    """Clean JSON string to remove control characters and fix common issues."""
    import re
    
    # Remove control characters that break JSON parsing
    json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)
    
    # Fix common JSON issues
    json_str = re.sub(r',\s*\]', ']', json_str)  # Remove trailing commas before ]
    json_str = re.sub(r',\s*}', '}', json_str)   # Remove trailing commas before }
    
    # Fix incomplete JSON by adding missing closing brackets
    if json_str.count('[') > json_str.count(']'):
        json_str += ']'
    if json_str.count('{') > json_str.count('}'):
        json_str += '}'
    
    return json_str

def generate_conversation(articles, topic, style="casual"):
    """Generate a texting conversation based on article opinions using Anthropic."""
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
URL: {article.get('url', '')}
Content: {description[:300]}...
Sentiment: {sentiment}
""")
    
    context = f"Recent news articles about {topic}:\n" + "\n".join(article_contexts)
    
    # Create conversation prompt based on style
    if style == "genz":
        style_instructions = """
Create a Gen Z-style texting conversation (max one sentence per person) where each news source reacts to the articles with their typical perspective and tone. Use:
- Gen Z slang, abbreviations, and emojis (ngl, ok but, bruh, etc.)
- Casual language and modern expressions
- Different perspectives from each source
- References to the actual articles
- Natural conversation flow
- Max 6-8 messages total
"""
    else:  # casual style
        style_instructions = """
Create a casual, natural texting conversation (max one sentence per person) where each news source reacts to the articles with their typical perspective and tone. Use:
- Casual, conversational language
- Different perspectives from each source
- References to the actual articles
- Natural conversation flow
- Max 6-8 messages total
"""

    prompt = f"""
You are creating a short texting conversation between different news sources discussing these articles.

{context}

{style_instructions}

CRITICAL: You must return ONLY a valid JSON array. Follow this EXACT format:
[
  {{"speaker": "Reuters", "side": "left", "text": "Your message here", "timestamp": "2024-01-15T10:30:00Z", "source_url": "https://example.com", "quote": "Relevant quote from the article"}},
  {{"speaker": "BBC News", "side": "right", "text": "Another message here", "timestamp": "2024-01-15T10:31:00Z", "source_url": "https://example.com", "quote": "Another relevant quote"}}
]

RULES:
- Use double quotes for all strings
- Escape any quotes inside text with backslash: \"
- No trailing commas
- Each message must have speaker, side, text, timestamp, source_url, and quote
- Keep text messages short (max one sentence)
- Use actual news source names from the articles
- For source_url, use the actual URL from the article context
- For quote, extract a relevant 1-2 sentence quote from the article content that supports the speaker's perspective
- Alternate the "side" field between "left" and "right" for each message to create a natural conversation flow

Return ONLY the JSON array, no other text.
"""
    
    try:
        if anthropic_client:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text.strip()
            
            # Try to parse JSON response
            try:
                import json
                import re
                
                # Clean up the response text to extract JSON
                if '[' in response_text and ']' in response_text:
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    json_text = response_text[start:end]
                else:
                    json_text = response_text
                
                # Fix incomplete JSON by adding missing closing brackets
                if json_text.count('[') > json_text.count(']'):
                    json_text += ']'
                if json_text.count('{') > json_text.count('}'):
                    json_text += '}'
                
                # Clean the JSON string using our helper function
                json_text = clean_json_string(json_text)
                
                # Try to parse the cleaned JSON
                conversation = json.loads(json_text)
                
                # Validate and clean up the conversation
                cleaned_conversation = []
                used_names = set()
                for i, msg in enumerate(conversation):
                    if isinstance(msg, dict) and 'speaker' in msg and 'text' in msg:
                        # Alternate between left and right sides for AI messages
                        side = 'right' if i % 2 == 1 else 'left'
                        
                        # Get a random name that hasn't been used yet
                        original_speaker = str(msg.get('speaker', 'Unknown'))
                        random_name = get_random_name()
                        while random_name in used_names:
                            random_name = get_random_name()
                        used_names.add(random_name)
                        
                        cleaned_msg = {
                            'speaker': random_name,
                            'side': side,
                            'text': str(msg.get('text', '')),
                            'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                            'source_url': str(msg.get('source_url', '')),
                            'quote': str(msg.get('quote', '')),
                            'news_source': original_speaker,  # Store original news source
                            'news_source_url': str(msg.get('source_url', ''))
                        }
                        cleaned_conversation.append(cleaned_msg)
                
                if cleaned_conversation:
                    return cleaned_conversation
                else:
                    raise ValueError("No valid messages found in JSON")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parsing failed: {e}")
                print(f"Response text: {response_text[:500]}...")
                print(f"Cleaned JSON text: {json_text[:500]}...")
                
                # Try to extract individual message objects from incomplete JSON
                try:
                    # Look for individual message objects in the response with more flexible patterns
                    message_patterns = [
                        # Pattern for complete message objects with URLs and quotes
                        r'\{"speaker":\s*"([^"]+)",\s*"side":\s*"([^"]+)",\s*"text":\s*"([^"]+)",\s*"timestamp":\s*"([^"]+)",\s*"source_url":\s*"([^"]*)",\s*"quote":\s*"([^"]*)"\}',
                        # Pattern for basic message objects
                        r'\{"speaker":\s*"([^"]+)",\s*"side":\s*"([^"]+)",\s*"text":\s*"([^"]+)",\s*"timestamp":\s*"([^"]+)"\}',
                        # Pattern for speaker and text only
                        r'"speaker":\s*"([^"]+)"[^}]*"text":\s*"([^"]+)"',
                        # Pattern for malformed JSON
                        r'speaker[:\s]*["\']?([^"\'},]+)["\']?[^}]*text[:\s]*["\']([^"\'}]+)["\']?'
                    ]
                    
                    conversation = []
                    used_names = set()
                    for pattern in message_patterns:
                        matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
                        if matches:
                            for i, match in enumerate(matches):
                                if len(match) >= 2:
                                    original_speaker = match[0].strip()
                                    text = match[1].strip()
                                    
                                    # Extract additional fields if available
                                    source_url = match[4] if len(match) > 4 else ""
                                    quote = match[5] if len(match) > 5 else ""
                                    
                                    if len(original_speaker) > 1 and len(text) > 5:
                                        # Get a random name that hasn't been used yet
                                        random_name = get_random_name()
                                        while random_name in used_names:
                                            random_name = get_random_name()
                                        used_names.add(random_name)
                                        
                                        # Alternate between left and right sides
                                        side = 'right' if i % 2 == 1 else 'left'
                                        conversation.append({
                                            "speaker": random_name,
                                            "side": side,
                                            "text": text,
                                            "timestamp": datetime.now().isoformat(),
                                            "source_url": source_url,
                                            "quote": quote,
                                            "news_source": original_speaker,
                                            "news_source_url": source_url
                                        })
                            if conversation:
                                break
                    
                    if conversation:
                        return conversation
                except Exception as extract_error:
                    print(f"Message extraction failed: {extract_error}")
                
                # If all else fails, create conversation from text
                return create_fallback_conversation(response_text, articles, style)
                
        elif OPENAI_API_KEY:
            # Fallback to OpenAI if Anthropic not available
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.8
            )
            response_text = response.choices[0].message.content.strip()
            return create_fallback_conversation(response_text, articles, style)
        else:
            # No AI available, create basic conversation
            return create_basic_conversation(articles, topic, style)
            
    except Exception as e:
        print(f"Error generating conversation: {e}")
        return create_basic_conversation(articles, topic, style)

def create_fallback_conversation(response_text, articles, style="casual"):
    """Create conversation from AI response text when JSON parsing fails."""
    import re
    
    conversation = []
    
    # Try to extract speaker and text from malformed JSON-like text
    # Look for patterns like: {speaker: "Name", text: "message"}
    speaker_text_pattern = r'\{?speaker[:\s]*["\']?([^"\'},]+)["\']?[,\s]*[^}]*text[:\s]*["\']([^"\'}]+)["\']?'
    matches = re.findall(speaker_text_pattern, response_text, re.IGNORECASE)
    
    # If that doesn't work, try a more flexible pattern
    if not matches:
        # Look for speaker and text in separate lines or with different formatting
        speaker_pattern = r'\{?speaker[:\s]*["\']?([^"\'},]+)["\']?'
        text_pattern = r'text[:\s]*["\']([^"\'}]+)["\']?'
        
        speakers = re.findall(speaker_pattern, response_text, re.IGNORECASE)
        texts = re.findall(text_pattern, response_text, re.IGNORECASE)
        
        # Match speakers with texts
        for i in range(min(len(speakers), len(texts))):
            matches.append((speakers[i], texts[i]))
    
    used_names = set()
    for i, (speaker, text) in enumerate(matches):
        original_speaker = speaker.strip().replace('{', '').replace('}', '')
        text = text.strip().replace('{', '').replace('}', '')
        
        if len(original_speaker) > 2 and len(text) > 5:
            # Get a random name that hasn't been used yet
            random_name = get_random_name()
            while random_name in used_names:
                random_name = get_random_name()
            used_names.add(random_name)
            
            # Alternate between left and right sides
            side = 'right' if i % 2 == 1 else 'left'
            conversation.append({
                "speaker": random_name,
                "side": side, 
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "news_source": original_speaker,
                "news_source_url": ""
            })
    
    # If we didn't get enough messages, add some basic ones
    if len(conversation) < 3:
        conversation.extend(create_basic_conversation(articles, "news", style)[:3-len(conversation)])
    
    return conversation[:6]  # Max 6 messages

def create_basic_conversation(articles, topic, style="casual"):
    """Create a basic conversation when AI is not available."""
    if not articles:
        return []
    
    # Get unique sources from articles
    sources = list(set([article.get('source', 'News Source') for article in articles[:4]]))
    if len(sources) < 2:
        sources = ['TechCrunch', 'Reuters', 'Associated Press', 'Wall Street Journal'][:len(sources)+2]
    
    conversation = []
    
    if style == "genz":
        responses = [
            "ok but this is actually wild 😳",
            "ngl this is giving me mixed feelings",
            "wait this is lowkey concerning",
            "ok but why is no one talking about this??",
            "this is actually so interesting",
            "bruh this is crazy",
            "ok but what does this mean for us tho",
            "this is giving me anxiety ngl",
            "wait this is actually a big deal",
            "ok but this is lowkey exciting"
        ]
    else:  # casual style
        responses = [
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
    
    used_names = set()
    for i, source in enumerate(sources[:4]):
        if i < len(responses):
            # Get a random name that hasn't been used yet
            random_name = get_random_name()
            while random_name in used_names:
                random_name = get_random_name()
            used_names.add(random_name)
            
            # Alternate between left and right sides
            side = 'right' if i % 2 == 1 else 'left'
            conversation.append({
                "speaker": random_name,
                "side": side,
                "text": responses[i],
                "timestamp": datetime.now().isoformat(),
                "source_url": "",
                "quote": "",
                "news_source": source,
                "news_source_url": ""
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
        # Get conversation style from query parameter
        style = request.args.get('style', 'casual')
        
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
        
        # Generate conversation for this subtopic with the specified style
        conversation = generate_conversation(subtopic_articles, target_subtopic['title'], style)
        
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
        style = data.get('style', 'casual')
        
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
        
        # Create style-specific instructions
        if style == "genz":
            style_instruction = "Respond in a Gen Z texting style (max one sentence) with your perspective on this topic. Use Gen Z slang, abbreviations, and emojis if appropriate."
        else:  # casual style
            style_instruction = "Respond in a casual, conversational style (max one sentence) with your perspective on this topic. Use natural, friendly language that's easy to understand."
        
        prompt = f"""
        You are {selected_persona}, {persona['background']}.
        Your perspective: {persona['perspective']}
        Your communication style: {persona['style']}
        
        Context:
        {full_context}
        
        User's question: {user_message}
        
        {style_instruction}
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
                if style == "genz":
                    ai_response = f"ngl this is actually pretty interesting from my perspective as {persona['background']} 🤔"
                else:
                    ai_response = f"This is actually pretty interesting from my perspective as {persona['background']}"
        except Exception as e:
            print(f"Error generating AI response: {e}")
            if style == "genz":
                ai_response = "ngl this is a complex topic but i'm having some technical difficulties rn 😅"
            else:
                ai_response = "This is a complex topic but I'm having some technical difficulties right now"
        
        # Find a relevant article for source information
        source_url = ""
        quote = ""
        if articles:
            # Use the first article as the source
            source_url = articles[0].get('url', '')
            quote = articles[0].get('description', '')[:200] + "..." if articles[0].get('description') else ""
        
        return jsonify({
            'success': True,
            'response': {
                'speaker': get_random_name(),
                'side': 'left',
                'text': ai_response,
                'timestamp': datetime.now().isoformat(),
                'source_url': source_url,
                'quote': quote,
                'news_source': selected_persona,
                'news_source_url': source_url
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