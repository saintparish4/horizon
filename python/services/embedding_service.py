"""
Embedding service for generating OpenAI embeddings
Supports both sync and async operations with batching
"""
import asyncio
import os 
from openai import OpenAI, AsyncOpenAI
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmbeddingService:
    """Service for generating embeddings using OpenAI API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize embedding service

        Args:
        api_key: OpenAI API key (defaults to OPENAI_API_KEY from environment variables)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set in environment variables"
            )

        # Initialize clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        # Model configuration
        self.model = "text-embedding-3-small" # 1536 dimensions, cost effective for most use cases
        self.max_batch_size = 100 # OpenAI API limit

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (up to 100)
        
        Args:
            texts: List of texts to embed (max 100)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        if len(texts) > self.max_batch_size:
            raise ValueError(
                f"Batch size {len(texts)} exceeds maximum of {self.max_batch_size}"
            )
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")
    
    async def generate_embedding_async(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (async)
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            response = await self.async_client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {str(e)}")
    
    async def batch_generate_async(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (async, up to 100)
        
        Args:
            texts: List of texts to embed (max 100)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        if len(texts) > self.max_batch_size:
            raise ValueError(
                f"Batch size {len(texts)} exceeds maximum of {self.max_batch_size}"
            )
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")
        
        try:
            response = await self.async_client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to generate batch embeddings: {str(e)}")
    
    async def batch_generate_large(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for large lists by chunking into batches
        
        Args:
            texts: List of texts to embed (any size)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Split into chunks
        chunks = [
            texts[i:i + self.max_batch_size] 
            for i in range(0, len(texts), self.max_batch_size)
        ]
        
        # Process chunks concurrently
        tasks = [self.batch_generate_async(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        embeddings = []
        for batch_embeddings in results:
            embeddings.extend(batch_embeddings)
        
        return embeddings


# Convenience functions for quick usage
def generate_embedding(text: str, api_key: Optional[str] = None) -> List[float]:
    """
    Quick function to generate a single embedding
    
    Args:
        text: Text to embed
        api_key: Optional OpenAI API key
        
    Returns:
        Embedding vector
    """
    service = EmbeddingService(api_key=api_key)
    return service.generate_embedding(text)


def batch_generate(texts: List[str], api_key: Optional[str] = None) -> List[List[float]]:
    """
    Quick function to generate batch embeddings
    
    Args:
        texts: List of texts to embed (max 100)
        api_key: Optional OpenAI API key
        
    Returns:
        List of embedding vectors
    """
    service = EmbeddingService(api_key=api_key)
    return service.batch_generate(texts)


async def generate_embedding_async(text: str, api_key: Optional[str] = None) -> List[float]:
    """
    Quick async function to generate a single embedding
    
    Args:
        text: Text to embed
        api_key: Optional OpenAI API key
        
    Returns:
        Embedding vector
    """
    service = EmbeddingService(api_key=api_key)
    return await service.generate_embedding_async(text)


async def batch_generate_async(texts: List[str], api_key: Optional[str] = None) -> List[List[float]]:
    """
    Quick async function to generate batch embeddings
    
    Args:
        texts: List of texts to embed (max 100)
        api_key: Optional OpenAI API key
        
    Returns:
        List of embedding vectors
    """
    service = EmbeddingService(api_key=api_key)
    return await service.batch_generate_async(texts)


