# Plaza Frontend

A React application for exploring news topics with different perspectives and personas.

## Features

- **Topic Exploration**: Browse different news topics and categories
- **Article Display**: View articles with bias indicators and source information
- **Chat Interface**: Engage in conversations with AI personas representing different political perspectives
- **Responsive Design**: Built with Tailwind CSS for modern, mobile-friendly UI

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm (comes with Node.js)

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (one-way operation)

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── NewsCard.jsx    # Article display component
│   ├── ChatBubble.jsx  # Chat message component
│   └── Navbar.jsx      # Navigation component
├── pages/              # Main application pages
│   ├── Home.jsx        # Topic and article listing
│   └── Chat.jsx        # Conversation interface
├── data/               # Static data files
│   ├── topics.json     # Available topics
│   └── conversations.json # Sample conversations
├── App.js              # Main application component
├── index.js            # Application entry point
└── index.css           # Global styles with Tailwind
```

## Technologies Used

- **React 18** - UI library
- **React Router DOM** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Create React App** - Build tooling and development server

## API Integration

The frontend expects the following API endpoints:

- `GET /data/topics.json` - Fetch available topics
- `GET /api/articles?topic={topic}` - Fetch articles for a topic
- `GET /api/conversations?topic={topic}&article={articleId}` - Load conversation history
- `POST /api/conversations` - Start new conversation
- `POST /api/conversations/message` - Send message in conversation

## Development Notes

- The app uses functional components with React hooks
- Tailwind CSS classes are used for styling
- Components are designed to be reusable and modular
- The app includes responsive design for mobile and desktop
