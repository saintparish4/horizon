---
name: Antler Technical Development Plan
overview: Comprehensive technical roadmap for building Antler's production-ready memory infrastructure, covering backend API, database architecture, SDK development, infrastructure, and DevOps over a 12-week development cycle.
todos:
  - id: project-setup
    content: Initialize project structure, dependencies, and development environment
    status: pending
  - id: database-schema
    content: Create database migrations with optimized indexes and partitioning
    status: pending
  - id: auth-middleware
    content: Implement API key authentication and rate limiting middleware
    status: pending
  - id: memory-api
    content: Build memory CRUD endpoints with embedding generation
    status: pending
  - id: search-api
    content: Implement semantic search with vector similarity and filters
    status: pending
    dependencies:
      - memory-api
  - id: usage-tracking
    content: Build usage logging and organization management APIs
    status: pending
  - id: testing-suite
    content: Create comprehensive unit and integration tests
    status: pending
    dependencies:
      - search-api
  - id: python-sdk
    content: Develop Python SDK with sync/async support and documentation
    status: pending
  - id: js-sdk
    content: Build JavaScript/TypeScript SDK with React hooks
    status: pending
    dependencies:
      - python-sdk
  - id: docker-setup
    content: Create Dockerfile and docker-compose for local development
    status: pending
  - id: ci-cd
    content: Set up GitHub Actions for testing and deployment
    status: pending
  - id: production-deploy
    content: Deploy to Railway/Render with Neon database
    status: pending
    dependencies:
      - docker-setup
      - ci-cd
  - id: monitoring
    content: Integrate Sentry, DataDog, and Prometheus metrics
    status: pending
    dependencies:
      - production-deploy
  - id: advanced-features
    content: Implement deduplication, collections, and webhooks
    status: pending
    dependencies:
      - testing-suite
  - id: dashboard-ui
    content: Build analytics dashboard with usage charts and memory browser
    status: pending
  - id: billing-integration
    content: Integrate Stripe for subscription management
    status: pending
    dependencies:
      - dashboard-ui
---

# Antler Technical Development Plan

## Technical Architecture Overview

`````mermaid
graph TB
    subgraph ClientLayer[Client Layer]
        PythonSDK[Python SDK]
        JSSDK[JavaScript SDK]
        DirectAPI[Direct REST API]
    end
    
    subgraph APIGateway[API Gateway Layer]
        RateLimit[Rate Limiter]
        Auth[Auth Middleware]
        CORS[CORS Handler]
    end
    
    subgraph ApplicationLayer[Application Layer]
        MemoryRoutes[Memory Routes]
        OrgRoutes[Organization Routes]
        SearchService[Search Service]
        EmbeddingService[Embedding Service]
    end
    
    subgraph DataLayer[Data Layer]
        PostgreSQL[(PostgreSQL + pgvector)]
        Redis[(Redis Cache)]
    end
    
    subgraph ExternalServices[External Services]
        OpenAI[OpenAI API]
        Stripe[Stripe]
        Monitoring[Sentry/DataDog]
    end
    
    PythonSDK --> RateLimit
    JSSDK --> RateLimit
    DirectAPI --> RateLimit
    RateLimit --> Auth
    Auth --> CORS
    CORS --> MemoryRoutes
    CORS --> OrgRoutes
    MemoryRoutes --> SearchService
    MemoryRoutes --> EmbeddingService
    SearchService --> PostgreSQL
    SearchService --> Redis
    EmbeddingService --> OpenAI
    OrgRoutes --> PostgreSQL
    MemoryRoutes --> Monitoring
```



## Phase 1: Backend Foundation (Weeks 1-4)

### Week 1: Core Infrastructure Setup

#### Database Schema Enhancement

Create migration in `python/migrations/001_initial_schema.py`:

```python
# Add indexes for performance
CREATE INDEX CONCURRENTLY idx_memories_embedding_vector 
ON memories USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX idx_memories_org_user_session 
ON memories (org_id, user_id, session_id, created_at DESC);

CREATE INDEX idx_memories_tags_gin ON memories USING GIN (tags);

# Add partitioning for scale
CREATE TABLE memories_partitioned (LIKE memories INCLUDING ALL) 
PARTITION BY RANGE (created_at);
```

**New Models to Create:**

1. `python/models/usage.py` - Track API usage per organization
```python
class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    operation_type = Column(String(50))  # 'store', 'search', 'retrieve'
    operation_count = Column(Integer, default=1)
    date = Column(Date, index=True)
    cost_cents = Column(Integer)  # Track COGS
```




2. `python/models/api_key.py` - Support key rotation
```python
class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    key_hash = Column(String(64), unique=True, index=True)
    name = Column(String(255))  # "Production", "Development"
    scopes = Column(ARRAY(String))  # ['read', 'write', 'admin']
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
```




#### API Routes Structure

Create FastAPI application in `python/main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

app = FastAPI(
    title="Antler Memory API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Mount routers
from routes import memories, organizations, search, usage
app.include_router(memories.router, prefix="/v1/memories", tags=["memories"])
app.include_router(organizations.router, prefix="/v1/organizations", tags=["organizations"])
app.include_router(search.router, prefix="/v1/search", tags=["search"])
app.include_router(usage.router, prefix="/v1/usage", tags=["usage"])
```



#### Authentication Middleware

Create `python/middleware/auth.py`:

```python
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from models.organization import Organization
from config.database import get_db
import hashlib

async def verify_api_key(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> Organization:
    """Verify API key and return organization"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header")
    
    api_key = authorization[7:]
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    org = db.query(Organization).filter(
        Organization.api_key_hash == key_hash,
        Organization.is_active == True
    ).first()
    
    if not org:
        raise HTTPException(401, "Invalid API key")
    
    return org

# Rate limiting based on plan
async def check_rate_limit(
    org: Organization = Depends(verify_api_key)
):
    # Check usage against plan limits
    daily_usage = get_daily_usage(org.id)
    
    limits = {
        "FREE": 100,
        "STARTER": 3000,
        "PRO": 100000,
        "ENTERPRISE": float('inf')
    }
    
    if daily_usage >= limits[org.plan_type.value.upper()]:
        raise HTTPException(429, "Rate limit exceeded for your plan")
    
    return org
```



### Week 2: Memory API Endpoints

Create `python/routes/memories.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from models.memory import Memory
from models.organization import Organization
from services.embedding_service import EmbeddingService
from middleware.auth import verify_api_key
from config.database import get_db

router = APIRouter()

# Request/Response schemas
class MemoryCreate(BaseModel):
    content: str
    context_type: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[dict] = {}
    tags: Optional[List[str]] = []

class MemoryResponse(BaseModel):
    id: int
    content: str
    context_type: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    metadata: dict
    tags: List[str]
    created_at: str
    
    class Config:
        from_attributes = True

class MemorySearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context_type: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 10
    min_similarity: float = 0.7

@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(
    memory: MemoryCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Store a new memory with automatic embedding generation"""
    
    # Check storage limits
    memory_count = db.query(Memory).filter(Memory.org_id == org.id).count()
    if memory_count >= org.memory_limit:
        raise HTTPException(403, f"Memory limit reached ({org.memory_limit})")
    
    # Generate embedding
    embedding_service = EmbeddingService()
    embedding = await embedding_service.generate_embedding_async(memory.content)
    
    # Create memory record
    db_memory = Memory(
        org_id=org.id,
        content=memory.content,
        embedding=embedding,
        context_type=memory.context_type,
        user_id=memory.user_id,
        session_id=memory.session_id,
        meta=memory.metadata,
        tags=memory.tags
    )
    
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    
    # Log usage
    log_usage(org.id, "store", db)
    
    return db_memory

@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(
    search: MemorySearchRequest,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Semantic search across memories using vector similarity"""
    
    # Generate query embedding
    embedding_service = EmbeddingService()
    query_embedding = await embedding_service.generate_embedding_async(search.query)
    
    # Build query with filters
    query = db.query(
        Memory,
        Memory.embedding.cosine_distance(query_embedding).label("distance")
    ).filter(Memory.org_id == org.id)
    
    if search.user_id:
        query = query.filter(Memory.user_id == search.user_id)
    if search.session_id:
        query = query.filter(Memory.session_id == search.session_id)
    if search.context_type:
        query = query.filter(Memory.context_type == search.context_type)
    if search.tags:
        query = query.filter(Memory.tags.overlap(search.tags))
    
    # Order by similarity and limit
    results = query.filter(
        Memory.embedding.cosine_distance(query_embedding) < (1 - search.min_similarity)
    ).order_by("distance").limit(search.limit).all()
    
    # Update accessed_at timestamps
    for memory, _ in results:
        memory.accessed_at = datetime.now(timezone.utc)
    db.commit()
    
    # Log usage
    log_usage(org.id, "search", db)
    
    return [memory for memory, _ in results]

@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context_type: Optional[str] = None,
    tags: Optional[str] = Query(None),  # Comma-separated
    limit: int = 50,
    offset: int = 0,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """List memories with filtering and pagination"""
    
    query = db.query(Memory).filter(Memory.org_id == org.id)
    
    if user_id:
        query = query.filter(Memory.user_id == user_id)
    if session_id:
        query = query.filter(Memory.session_id == session_id)
    if context_type:
        query = query.filter(Memory.context_type == context_type)
    if tags:
        tag_list = tags.split(",")
        query = query.filter(Memory.tags.overlap(tag_list))
    
    results = query.order_by(Memory.created_at.desc()).offset(offset).limit(limit).all()
    
    log_usage(org.id, "retrieve", db)
    
    return results

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Get a specific memory by ID"""
    
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.org_id == org.id
    ).first()
    
    if not memory:
        raise HTTPException(404, "Memory not found")
    
    memory.accessed_at = datetime.now(timezone.utc)
    db.commit()
    
    return memory

@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int,
    memory_update: MemoryCreate,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Update memory content and regenerate embedding"""
    
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.org_id == org.id
    ).first()
    
    if not memory:
        raise HTTPException(404, "Memory not found")
    
    # Regenerate embedding if content changed
    if memory.content != memory_update.content:
        embedding_service = EmbeddingService()
        memory.embedding = await embedding_service.generate_embedding_async(
            memory_update.content
        )
    
    # Update fields
    memory.content = memory_update.content
    memory.context_type = memory_update.context_type
    memory.user_id = memory_update.user_id
    memory.session_id = memory_update.session_id
    memory.meta = memory_update.metadata
    memory.tags = memory_update.tags
    
    db.commit()
    db.refresh(memory)
    
    return memory

@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: int,
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Delete a memory"""
    
    memory = db.query(Memory).filter(
        Memory.id == memory_id,
        Memory.org_id == org.id
    ).first()
    
    if not memory:
        raise HTTPException(404, "Memory not found")
    
    db.delete(memory)
    db.commit()
    
    return None

@router.post("/batch", response_model=List[MemoryResponse])
async def batch_create_memories(
    memories: List[MemoryCreate],
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Bulk create memories with batch embedding generation"""
    
    if len(memories) > 100:
        raise HTTPException(400, "Maximum 100 memories per batch")
    
    # Check limits
    current_count = db.query(Memory).filter(Memory.org_id == org.id).count()
    if current_count + len(memories) > org.memory_limit:
        raise HTTPException(403, "Memory limit would be exceeded")
    
    # Batch generate embeddings
    embedding_service = EmbeddingService()
    texts = [m.content for m in memories]
    embeddings = await embedding_service.batch_generate_async(texts)
    
    # Create records
    db_memories = []
    for memory, embedding in zip(memories, embeddings):
        db_memory = Memory(
            org_id=org.id,
            content=memory.content,
            embedding=embedding,
            context_type=memory.context_type,
            user_id=memory.user_id,
            session_id=memory.session_id,
            meta=memory.metadata,
            tags=memory.tags
        )
        db_memories.append(db_memory)
    
    db.add_all(db_memories)
    db.commit()
    
    for db_memory in db_memories:
        db.refresh(db_memory)
    
    log_usage(org.id, "store", db, count=len(memories))
    
    return db_memories
```



### Week 3: Organization & Usage APIs

Create `python/routes/organizations.py`:

```python
@router.post("/signup", response_model=OrganizationResponse)
async def signup(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """Self-service organization signup"""
    
    # Check if email already exists
    existing = db.query(Organization).filter(
        Organization.email == org_data.email
    ).first()
    
    if existing:
        raise HTTPException(409, "Email already registered")
    
    # Create organization with free plan
    org = Organization(
        name=org_data.name,
        email=org_data.email,
        plan_type=PlanType.FREE,
        memory_limit=10000
    )
    
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Send welcome email with API key
    send_welcome_email(org.email, org.api_key)
    
    return org

@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    org: Organization = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Get current month usage statistics"""
    
    current_month = datetime.now().replace(day=1)
    
    usage = db.query(
        func.sum(UsageLog.operation_count).label("total_operations"),
        func.sum(UsageLog.cost_cents).label("total_cost_cents")
    ).filter(
        UsageLog.org_id == org.id,
        UsageLog.date >= current_month
    ).first()
    
    memory_count = db.query(Memory).filter(Memory.org_id == org.id).count()
    storage_gb = db.query(
        func.sum(func.length(Memory.content))
    ).filter(Memory.org_id == org.id).scalar() / (1024**3)
    
    return {
        "operations": usage.total_operations or 0,
        "memory_count": memory_count,
        "storage_gb": round(storage_gb, 2),
        "cost_cents": usage.total_cost_cents or 0,
        "plan_type": org.plan_type.value,
        "limits": {
            "memory_limit": org.memory_limit,
            "operations_limit": get_operation_limit(org.plan_type)
        }
    }
```



### Week 4: Testing & Documentation

#### Unit Tests Structure

Create `python/tests/` directory:

```javascript
tests/
├── conftest.py          # Pytest fixtures
├── test_memory.py       # Memory CRUD tests
├── test_search.py       # Search functionality tests
├── test_auth.py         # Authentication tests
├── test_usage.py        # Usage tracking tests
└── test_integration.py  # End-to-end tests
```

Example `python/tests/test_memory.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from models.organization import Organization

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_org(db):
    org = Organization(name="Test Org", email="test@example.com")
    db.add(org)
    db.commit()
    return org

def test_create_memory(client, test_org):
    response = client.post(
        "/v1/memories",
        json={
            "content": "User prefers dark mode",
            "user_id": "user123",
            "context_type": "preference"
        },
        headers={"Authorization": f"Bearer {test_org.api_key}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "User prefers dark mode"
    assert data["user_id"] == "user123"
    assert "id" in data

def test_search_memories(client, test_org):
    # Create test memories
    memories = [
        "User likes Python programming",
        "User prefers VS Code editor",
        "User works on AI projects"
    ]
    
    for content in memories:
        client.post(
            "/v1/memories",
            json={"content": content, "user_id": "user123"},
            headers={"Authorization": f"Bearer {test_org.api_key}"}
        )
    
    # Search
    response = client.post(
        "/v1/memories/search",
        json={
            "query": "What programming language does the user like?",
            "user_id": "user123",
            "limit": 5
        },
        headers={"Authorization": f"Bearer {test_org.api_key}"}
    )
    
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert "Python" in results[0]["content"]

def test_rate_limiting(client, test_org):
    # Set org to free plan
    test_org.plan_type = PlanType.FREE
    
    # Make 101 requests (free plan limit is 100/day)
    for i in range(101):
        response = client.post(
            "/v1/memories",
            json={"content": f"Test memory {i}"},
            headers={"Authorization": f"Bearer {test_org.api_key}"}
        )
    
    assert response.status_code == 429
    assert "rate limit" in response.json()["detail"].lower()
```



#### API Documentation

Create OpenAPI documentation in `python/main.py`:

````python
app = FastAPI(
    title="Antler Memory API",
    description="""
    🦌 **Antler** - Memory Infrastructure for AI Agents
    
    ## Features
        - **Semantic Search**: Vector-based memory retrieval
        - **Context Management**: Organize by user, session, type
        - **Automatic Embeddings**: No manual vector generation
        - **Multi-tenant**: Secure organization isolation
    
    ## Quick Start
    ```python
    import antler
    
    client = antler.Client(api_key="mem_xxx")
    
    # Store a memory
    memory = client.memories.create(
        content="User prefers dark mode",
        user_id="user123"
    )
    
    # Search memories
    results = client.memories.search(
        query="What are user's preferences?",
        user_id="user123"
    )
    ```
    
    ## Rate Limits
        - Free: 100 operations/day
        - Starter: 3K operations/day  
        - Pro: 100K operations/day
        - Enterprise: Unlimited
    """,
    version="1.0.0",
    contact={
        "name": "Antler Support",
        "email": "support@antler.dev",
        "url": "https://docs.antler.dev"
    },
    license_info={
        "name": "Proprietary"
    }
)
````



## Phase 2: SDK Development (Weeks 5-6)

### Python SDK Architecture

Create `sdks/python-antler/` structure:

```javascript
python-antler/
├── antler/
│   ├── __init__.py
│   ├── client.py          # Main client class
│   ├── resources/
│   │   ├── memories.py    # Memory operations
│   │   ├── search.py      # Search operations
│   │   └── usage.py       # Usage tracking
│   ├── models.py          # Pydantic models
│   ├── exceptions.py      # Custom exceptions
│   ├── http.py            # HTTP client wrapper
│   └── async_client.py    # Async support
├── tests/
├── examples/
│   ├── basic_usage.py
│   ├── langchain_integration.py
│   └── async_example.py
├── setup.py
├── pyproject.toml
└── README.md
```

**Core SDK Implementation** (`sdks/python-antler/antler/client.py`):

```python
from typing import Optional, List, Dict
import httpx
from .resources.memories import Memories
from .resources.search import Search
from .exceptions import AntlerError, AuthenticationError, RateLimitError

class AntlerClient:
    """Antler Memory API Client
    
    Example:
        >>> client = AntlerClient(api_key="mem_xxx")
        >>> memory = client.memories.create(
        ...     content="User prefers dark mode",
        ...     user_id="user123"
        ... )
        >>> results = client.memories.search(
        ...     query="user preferences",
        ...     user_id="user123"
        ... )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.antler.dev/v1",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url
        
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout
        )
        
        # Initialize resources
        self.memories = Memories(self)
        self.search = Search(self)
    
    def request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with error handling"""
        try:
            response = self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            else:
                raise AntlerError(f"API error: {e.response.text}")
    
    def close(self):
        """Close HTTP client"""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

**Memory Resource** (`sdks/python-antler/antler/resources/memories.py`):

```python
from typing import List, Optional, Dict
from ..models import Memory, MemoryCreate

class Memories:
    """Memory operations resource"""
    
    def __init__(self, client):
        self._client = client
    
    def create(
        self,
        content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context_type: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ) -> Memory:
        """Store a new memory
        
        Args:
            content: The memory content to store
            user_id: Optional user identifier
            session_id: Optional session identifier
            context_type: Optional context type (e.g., 'conversation', 'preference')
            metadata: Optional metadata dictionary
            tags: Optional list of tags
        
        Returns:
            Memory object with id and timestamps
        
        Example:
            >>> memory = client.memories.create(
            ...     content="User likes Python",
            ...     user_id="user123",
            ...     tags=["preference", "language"]
            ... )
        """
        data = {
            "content": content,
            "user_id": user_id,
            "session_id": session_id,
            "context_type": context_type,
            "metadata": metadata or {},
            "tags": tags or []
        }
        
        response = self._client.request("POST", "/memories", json=data)
        return Memory(**response)
    
    def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Memory]:
        """Semantic search for memories
        
        Args:
            query: Natural language search query
            user_id: Filter by user
            session_id: Filter by session
            context_type: Filter by context type
            tags: Filter by tags
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)
        
        Returns:
            List of Memory objects ordered by relevance
        
        Example:
            >>> results = client.memories.search(
            ...     query="What does the user like?",
            ...     user_id="user123",
            ...     limit=5
            ... )
        """
        data = {
            "query": query,
            "user_id": user_id,
            "session_id": session_id,
            "context_type": context_type,
            "tags": tags,
            "limit": limit,
            "min_similarity": min_similarity
        }
        
        response = self._client.request("POST", "/memories/search", json=data)
        return [Memory(**m) for m in response]
    
    def list(
        self,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Memory]:
        """List memories with filtering"""
        params = {
            "user_id": user_id,
            "session_id": session_id,
            "limit": limit,
            "offset": offset
        }
        
        response = self._client.request("GET", "/memories", params=params)
        return [Memory(**m) for m in response]
    
    def get(self, memory_id: int) -> Memory:
        """Get a specific memory by ID"""
        response = self._client.request("GET", f"/memories/{memory_id}")
        return Memory(**response)
    
    def update(self, memory_id: int, **kwargs) -> Memory:
        """Update a memory"""
        response = self._client.request("PUT", f"/memories/{memory_id}", json=kwargs)
        return Memory(**response)
    
    def delete(self, memory_id: int) -> None:
        """Delete a memory"""
        self._client.request("DELETE", f"/memories/{memory_id}")
    
    def batch_create(self, memories: List[MemoryCreate]) -> List[Memory]:
        """Bulk create memories (up to 100)"""
        data = [m.dict() for m in memories]
        response = self._client.request("POST", "/memories/batch", json=data)
        return [Memory(**m) for m in response]
```



### JavaScript SDK Architecture

Create `sdks/js-antler/` structure:

```javascript
js-antler/
├── src/
│   ├── index.ts         # Main exports
│   ├── client.ts        # Client class
│   ├── resources/
│   │   ├── memories.ts
│   │   └── search.ts
│   ├── types.ts         # TypeScript types
│   ├── errors.ts
│   └── http.ts
├── examples/
│   ├── basic.ts
│   ├── nextjs-app.tsx
│   └── react-hooks.tsx
├── package.json
├── tsconfig.json
└── README.md
```

**Core Client** (`sdks/js-antler/src/client.ts`):

```typescript
import axios, { AxiosInstance } from 'axios';
import { Memories } from './resources/memories';
import { AntlerError, AuthenticationError, RateLimitError } from './errors';

export interface AntlerClientConfig {
  apiKey: string;
  baseURL?: string;
  timeout?: number;
}

export class AntlerClient {
  private http: AxiosInstance;
  public memories: Memories;

  constructor(config: AntlerClientConfig) {
    this.http = axios.create({
      baseURL: config.baseURL || 'https://api.antler.dev/v1',
      timeout: config.timeout || 30000,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    // Error interceptor
    this.http.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          throw new AuthenticationError('Invalid API key');
        } else if (error.response?.status === 429) {
          throw new RateLimitError('Rate limit exceeded');
        }
        throw new AntlerError(error.message);
      }
    );

    this.memories = new Memories(this.http);
  }
}

export default AntlerClient;
```

**React Hooks** (`sdks/js-antler/src/react/hooks.ts`):

```typescript
import { useState, useEffect } from 'react';
import { AntlerClient } from '../client';
import { Memory } from '../types';

export function useMemory(client: AntlerClient, memoryId: number) {
  const [memory, setMemory] = useState<Memory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    client.memories.get(memoryId)
      .then(setMemory)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [client, memoryId]);

  return { memory, loading, error };
}

export function useMemorySearch(
  client: AntlerClient,
  query: string,
  options?: SearchOptions
) {
  const [results, setResults] = useState<Memory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const search = async () => {
    setLoading(true);
    try {
      const memories = await client.memories.search(query, options);
      setResults(memories);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return { results, loading, error, search };
}
```



## Phase 3: Infrastructure & DevOps (Weeks 7-8)

### Deployment Architecture

```mermaid
graph TB
    subgraph CloudInfra[Cloud Infrastructure]
        subgraph EdgeLayer[Edge Layer]
            Vercel[Vercel Frontend]
            CF[Cloudflare DNS]
        end
        
        subgraph ComputeLayer[Compute Layer]
            Railway[Railway Backend]
            Workers[Background Workers]
        end
        
        subgraph DataLayer[Data Layer]
            Neon[(Neon PostgreSQL)]
            Redis[(Redis Cloud)]
        end
        
        subgraph MonitoringLayer[Monitoring]
            Sentry[Sentry]
            DataDog[DataDog]
            Posthog[PostHog Analytics]
        end
    end
    
    Users[Users] --> CF
    CF --> Vercel
    CF --> Railway
    Railway --> Neon
    Railway --> Redis
    Railway --> Sentry
    Railway --> DataDog
    Vercel --> Posthog
```



### Docker Configuration

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY python/ /app/

# Run database migrations
CMD alembic upgrade head && \
    uvicorn main:app --host 0.0.0.0 --port $PORT
```

Create `docker-compose.yml` for local development:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
            - "8000:8000"
    environment:
            - DATABASE_URL=postgresql://postgres:postgres@db:5432/antler
            - REDIS_URL=redis://redis:6379
            - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
            - db
            - redis
    volumes:
            - ./python:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: pgvector/pgvector:pg16
    environment:
            - POSTGRES_USER=postgres
            - POSTGRES_PASSWORD=postgres
            - POSTGRES_DB=antler
    ports:
            - "5432:5432"
    volumes:
            - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
            - "6379:6379"

volumes:
  postgres_data:
```



### CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
            - uses: actions/checkout@v3
      
            - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
            - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
            - name: Run linters
        run: |
          black --check python/
          isort --check python/
          mypy python/
      
            - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest --cov=python --cov-report=xml
      
            - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
            - uses: actions/checkout@v3
      
            - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm i -g @railway/cli
          railway up
```



### Monitoring & Observability

Create `python/monitoring/metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Metrics
memory_operations = Counter(
    'antler_memory_operations_total',
    'Total memory operations',
    ['operation_type', 'org_id']
)

api_latency = Histogram(
    'antler_api_latency_seconds',
    'API endpoint latency',
    ['endpoint', 'method']
)

active_organizations = Gauge(
    'antler_active_organizations',
    'Number of active organizations'
)

embedding_latency = Histogram(
    'antler_embedding_latency_seconds',
    'Embedding generation latency'
)

def track_latency(endpoint: str):
    """Decorator to track API latency"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start
                api_latency.labels(endpoint=endpoint, method=func.__name__).observe(duration)
        return wrapper
    return decorator
```



## Phase 4: Advanced Features (Weeks 9-10)

### Smart Deduplication

Create `python/services/deduplication_service.py`:

```python
from sqlalchemy.orm import Session
from models.memory import Memory
from services.embedding_service import EmbeddingService

class DeduplicationService:
    """Detect and merge similar memories"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.threshold = similarity_threshold
    
    async def check_duplicates(
        self,
        content: str,
        org_id: int,
        user_id: str,
        db: Session
    ) -> tuple[bool, Optional[Memory]]:
        """Check if similar memory already exists"""
        
        # Generate embedding for new content
        embedding_service = EmbeddingService()
        new_embedding = await embedding_service.generate_embedding_async(content)
        
        # Find most similar existing memory
        similar = db.query(
            Memory,
            Memory.embedding.cosine_distance(new_embedding).label("distance")
        ).filter(
            Memory.org_id == org_id,
            Memory.user_id == user_id
        ).order_by("distance").first()
        
        if similar and (1 - similar[1]) >= self.threshold:
            return True, similar[0]
        
        return False, None
    
    def merge_memories(
        self,
        existing: Memory,
        new_content: str,
        db: Session
    ) -> Memory:
        """Merge duplicate memory by updating metadata"""
        
        existing.meta['duplicate_count'] = existing.meta.get('duplicate_count', 0) + 1
        existing.meta['last_duplicate'] = new_content
        existing.accessed_at = datetime.now(timezone.utc)
        
        db.commit()
        return existing
```



### Memory Collections

Add to `python/models/collection.py`:

```python
class MemoryCollection(Base):
    """Namespace isolation for different projects/agents"""
    __tablename__ = "memory_collections"
    
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    memories = relationship("Memory", back_populates="collection")

# Add to Memory model
class Memory(Base):
    # ... existing fields ...
    collection_id = Column(Integer, ForeignKey("memory_collections.id"), nullable=True)
    collection = relationship("MemoryCollection", back_populates="memories")
```



### Webhook Notifications

Create `python/services/webhook_service.py`:

```python
import httpx
from typing import Dict, Any

class WebhookService:
    """Send webhook notifications for memory events"""
    
    async def notify(
        self,
        webhook_url: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send webhook notification"""
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    webhook_url,
                    json={
                        "event": event_type,
                        "data": payload,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    timeout=5.0
                )
            except Exception as e:
                # Log webhook failure but don't block main operation
                logger.error(f"Webhook notification failed: {e}")
```



## Phase 5: Dashboard & Billing (Weeks 11-12)

### Dashboard Pages Structure

```javascript
frontend/app/dashboard/
├── layout.tsx                 # Dashboard shell with sidebar
├── page.tsx                   # Overview/analytics
├── memories/
│   ├── page.tsx              # Memory browser
│   └── [id]/page.tsx         # Memory detail
├── api-keys/
│   └── page.tsx              # API key management
├── usage/
│   └── page.tsx              # Usage & billing
├── settings/
│   └── page.tsx              # Organization settings
└── components/
    ├── memory-table.tsx
    ├── usage-chart.tsx
    └── api-key-card.tsx
```



### Analytics Dashboard

Create `frontend/app/dashboard/page.tsx`:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState(null);
  
  useEffect(() => {
    fetch('/api/dashboard/metrics', {
      headers: { 'Authorization': `Bearer ${apiKey}` }
    })
      .then(res => res.json())
      .then(setMetrics);
  }, []);
  
  return (
    <div className="space-y-8">
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        <MetricCard
          title="Total Memories"
          value={metrics?.memory_count}
          change="+12% from last month"
        />
        <MetricCard
          title="API Calls (30d)"
          value={metrics?.api_calls}
          change="+24% from last month"
        />
        <MetricCard
          title="Storage Used"
          value={`${metrics?.storage_gb} GB`}
          change="8% of limit"
        />
        <MetricCard
          title="Avg Search Latency"
          value={`${metrics?.avg_latency} ms`}
          change="-5% from last month"
        />
      </div>
      
      {/* Usage Chart */}
      <div className="rounded-2xl border p-6">
        <h2 className="mb-4 text-xl font-semibold">API Usage (Last 30 Days)</h2>
        <Line
          data={{
            labels: metrics?.usage_timeline?.map(d => d.date),
            datasets: [{
              label: 'Operations',
              data: metrics?.usage_timeline?.map(d => d.count),
              borderColor: 'rgb(0, 0, 0)',
              tension: 0.4
            }]
          }}
        />
      </div>
      
      {/* Recent Memories */}
      <div className="rounded-2xl border p-6">
        <h2 className="mb-4 text-xl font-semibold">Recent Memories</h2>
        <MemoryTable memories={metrics?.recent_memories} />
      </div>
    </div>
  );
}
```



### Stripe Integration

Create `python/services/billing_service.py`:

```python
import stripe
from models.organization import Organization, PlanType

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingService:
    """Manage subscriptions and billing"""
    
    PLAN_PRICES = {
        PlanType.STARTER: "price_starter_xxx",
        PlanType.PRO: "price_pro_xxx",
        PlanType.TEAM: "price_team_xxx"
    }
    
    async def create_checkout_session(
        self,
        org: Organization,
        plan_type: PlanType
    ) -> str:
        """Create Stripe checkout session for plan upgrade"""
        
        session = stripe.checkout.Session.create(
            customer_email=org.email,
            mode="subscription",
            line_items=[{
                "price": self.PLAN_PRICES[plan_type],
                "quantity": 1
            }],
            success_url="https://app.antler.dev/dashboard?upgrade=success",
            cancel_url="https://app.antler.dev/dashboard/usage",
            metadata={"org_id": org.id}
        )
        
        return session.url
    
    async def handle_webhook(self, event: Dict):
        """Handle Stripe webhook events"""
        
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            org_id = session["metadata"]["org_id"]
            
            # Update organization plan
            # Send confirmation email
            
        elif event["type"] == "invoice.payment_failed":
            # Handle failed payment
            # Send notification email
            pass
```



## Key Technical Decisions

### Technology Stack Justification

**Backend: FastAPI + PostgreSQL + pgvector**

- FastAPI: Best Python async performance, automatic OpenAPI docs, type safety
- PostgreSQL: Battle-tested, ACID compliance, excellent JSON support
- pgvector: Simpler than dedicated vector DB for MVP, can scale to 1M+ vectors

**Frontend: Next.js 14 + Tailwind**

- App Router for server components (better performance)
- Tailwind for rapid UI development
- TypeScript for type safety

**SDKs: Native languages vs generated**

- Hand-written SDKs for better DX (vs OpenAPI-generated)
- Async support built-in for Python/JavaScript
- React hooks for frontend integration

**Deployment: Railway + Neon + Vercel**

- Railway: Simplified container deployment with auto-scaling
- Neon: Serverless PostgreSQL with automatic branching for preview deploys
- Vercel: Best Next.js hosting with edge functions

### Scalability Considerations

**Database Optimization**

- Partitioning by created_at for time-series queries
- IVFFlat index on embeddings (faster than HNSW for <1M vectors)
- Connection pooling (PgBouncer) for high concurrency

**Caching Strategy**

- Redis for rate limiting state
- Application-level caching for frequent searches
- CDN caching for static assets

**Horizontal Scaling**

- Stateless API servers (can scale to N instances)
- Background job queue (Celery) for batch operations
- Read replicas for analytics queries

**Cost Optimization**

- Embedding caching to reduce OpenAI API calls
- Compression for stored memories
- Usage-based alerts to prevent runaway costs

## Success Metrics

### Engineering Metrics

- API uptime: 99.9%+ (target 99.95%)
- P95 latency: <200ms for memory operations
- P95 latency: <500ms for search operations
- Test coverage: >80%
- Zero critical security vulnerabilities

### Performance Benchmarks

- 1000 memories stored: <30 seconds
- Search across 10K memories: <100ms
- Batch embedding (100 items): <5 seconds
- Database query performance: <50ms

### Developer Experience

- Time to first API call: <5 minutes
- SDK installation: 1 command
- Documentation completeness: 100% endpoint coverage
- Example code: 10+ use cases

## Risk Mitigation

### Technical Risks

1. **pgvector scaling limits**

- Mitigation: Monitor query performance, plan migration to Pinecone/Weaviate at 1M+ vectors
- Trigger: P95 search latency >1 second

2. **OpenAI API dependency**

- Mitigation: Implement retry logic, fallback to Cohere embeddings
- Cost control: Cache embeddings, offer BYO API key for enterprise

3. **Database costs at scale**

- Mitigation: Implement data retention policies, compression
- Monitoring: Track storage growth rate

### Security Considerations

- API key hashing (SHA-256)
- Row-level security for multi-tenancy
- Rate limiting per organization
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Secrets management (environment variables)
- Regular dependency updates

## Next Implementation Steps

1. **Week 1**: Set up project structure, database migrations, core models
2. **Week 2**: Implement memory CRUD API endpoints with authentication
3. **Week 3**: Build semantic search functionality, usage tracking
4. **Week 4**: Unit tests, integration tests, API documentation
5. **Week 5-6**: Python and JavaScript SDK development
6. **Week 7-8**: Deployment infrastructure, CI/CD, monitoring


`````