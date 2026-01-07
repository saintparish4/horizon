# 🦌 Antler

**Memory infrastructure for AI agents** — so your AI systems remember, learn, and get smarter over time.

## Overview

Antler provides persistent, intelligent memory for AI agents through semantic search and context management. Built for developers who need their AI systems to maintain long-term memory across sessions, conversations, and interactions.

## Key Features

- **🧠 Semantic Memory** - Store and retrieve context using vector embeddings
- **🔍 Smart Search** - Find relevant memories with natural language queries
- **📦 Context Management** - Organize by user, session, or custom tags
- **⚡ Blazing Fast** - Millisecond-level retrieval with optimized indexing
- **🔒 Secure & Scalable** - Multi-tenant architecture with API key authentication
- **🛠️ Developer-First** - Simple SDKs for Python and JavaScript

## Quick Start

### Python

```python
import antler

client = antler.Client(api_key="your_api_key")

# Store a memory
memory = client.memories.create(
    content="User prefers dark mode",
    user_id="user_123",
    tags=["preference", "ui"]
)

# Search memories
results = client.memories.search(
    query="What are the user's UI preferences?",
    user_id="user_123"
)
```

### JavaScript

```javascript
import { AntlerClient } from '@antler/sdk';

const client = new AntlerClient({ apiKey: 'your_api_key' });

// Store a memory
const memory = await client.memories.create({
  content: 'User prefers dark mode',
  userId: 'user_123',
  tags: ['preference', 'ui']
});

// Search memories
const results = await client.memories.search({
  query: "What are the user's UI preferences?",
  userId: 'user_123'
});
```

## Use Cases

- **AI Chatbots** - Remember conversation history and user preferences
- **Autonomous Agents** - Learn from past actions and decisions
- **Personal Assistants** - Maintain context about user habits and needs
- **Customer Support** - Recall previous interactions and support tickets

## Project Structure

```
Antler/
├── frontend/          # Next.js landing page and dashboard
├── python/            # Backend API and services
│   ├── config/        # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── services/      # Business logic (embeddings, search)
│   └── scripts/       # Database utilities
├── sdks/              # Client libraries (coming soon)
│   ├── python-antler/ # Python SDK
│   └── js-antler/     # JavaScript/TypeScript SDK
└── docs/              # Documentation site (coming soon)
```

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- Node.js 18+ (for frontend)
- OpenAI API key

### Backend Setup

```bash
# Install dependencies
pip install -e .

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/antler"
export OPENAI_API_KEY="your_openai_key"

# Run migrations
python python/scripts/create_tables.py

# Start server
uvicorn python.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Visit `/docs` when running the server for interactive API documentation.

### Core Endpoints

- `POST /v1/memories` - Store a new memory
- `POST /v1/memories/search` - Semantic search
- `GET /v1/memories` - List memories with filters
- `PUT /v1/memories/{id}` - Update memory
- `DELETE /v1/memories/{id}` - Delete memory

## Architecture

```
Client SDK → API Gateway → FastAPI Backend → PostgreSQL + pgvector
                                          → OpenAI Embeddings
```

- **Backend**: FastAPI with async support
- **Database**: PostgreSQL with pgvector for vector similarity search
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Deployment**: Railway (API) + Vercel (Frontend) + Neon (Database)

## Roadmap

- [x] Core memory API
- [x] Semantic search with vector embeddings
- [x] Multi-tenant organization management
- [ ] Python SDK (Week 5-6)
- [ ] JavaScript SDK (Week 5-6)
- [ ] Dashboard UI (Week 11-12)
- [ ] LangChain integration
- [ ] AutoGPT integration
- [ ] Memory collections (namespaces)
- [ ] Webhook notifications
- [ ] Advanced analytics

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) (coming soon).

## License

Proprietary - © 2025 Antler

## Contact

- Website: [antler.dev](https://antler.dev)
- Email: support@antler.dev
- Discord: [Join our community](https://discord.gg/antler)
- Twitter: [@AntlerMemory](https://twitter.com/AntlerMemory)

---

**Built for the future of AI** 🦌