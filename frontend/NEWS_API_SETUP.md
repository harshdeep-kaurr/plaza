# News API Setup

This application uses the News API to fetch real-time news articles for each topic category.

## Setup Instructions

1. **Get a News API Key**
   - Visit [https://newsapi.org/](https://newsapi.org/)
   - Sign up for a free account
   - Get your API key from the dashboard

2. **Configure Environment Variables**
   - Create a `.env` file in the `frontend` directory
   - Add your API key:
     ```
     REACT_APP_NEWS_API_KEY=your_news_api_key_here
     ```

3. **Restart the Development Server**
   - Stop your current development server
   - Run `npm start` again to load the new environment variables

## Features

- **Real-time News**: Fetches articles from the past week for each category
- **Dynamic Facts**: Generates fact summaries from recent news articles
- **Interactive Chat**: AI personas respond based on current news content
- **Categories**: Business, Entertainment, General, Health, Science, Sports, Technology

## API Limits

- Free tier: 1000 requests per day
- Articles are cached for better performance
- Fallback content is shown if API is unavailable

## Troubleshooting

- **"News API key not found"**: Make sure your `.env` file is in the correct location and contains the API key
- **"News API error"**: Check your API key is valid and you haven't exceeded daily limits
- **No articles found**: Some categories may have limited recent content; the app will show fallback content
- **CORS errors**: The News API doesn't support direct browser requests; use a backend proxy or the News API's CORS-enabled endpoints

## Fallback Content

If the News API is unavailable or returns no results, the app will display:
- Relevant fallback facts for each category
- Sample discussion from different reporter personas
- Graceful error handling without breaking the user experience
