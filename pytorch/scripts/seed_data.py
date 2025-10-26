"""
Seed the database with test data
Creates a test organization and sample memories
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import config and models
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from config.database import SessionLocal 
from models import Organization, Memory, PlanType

def seed_data():
    """
    Seed the database with test data
    """
    db: Session = SessionLocal()

    try:
        print("Seeding test data...\n")

        # Create test organization
        test_org = Organization(
            name="Bluesky Labs",
            email="test@blueskylabs.com",
            plan_type=PlanType.PROFESSIONAL,
            memory_limit=10000 
        )
        db.add(test_org)
        db.commit()
        db.refresh(test_org)

        print(f"Organization created:")
        print(f" - ID: {test_org.id}")
        print(f" - Name: {test_org.name}")
        print(f" - Email: {test_org.email}")
        print(f" - Plan: {test_org.plan_type.value}")
        print(f" - API Key: {test_org.api_key}")

        # Save API key to file
        print(f"\nSaving API key to .api_key file...")
        with open(".api_key", "w") as f:
            f.write(test_org.api_key)
        print("API key saved to .api_key")

        # Create test memories (without embeddings for now)
        print(f"\nCreating test memories...")

        test_memories = [
            {
                "content": "User prefers dark mode interfaces and keyboard shortcyts for navigation.",
                "context_type": "user_preference",
                "user_id": "user_123",
                "session_id": "session_001",
                "tags": ["preferences", "ui", "accessibility"],
                "meta": {"source": "settings_page", "confidence": 0.95}
            },
            {
                "content": "Previous conversation discussed implementing a RAG system using FastAPI and PostgreSQL",
                "context_type": "conversation",
                "user_id": "user_123",
                "session_id": "session_002",
                "tags": ["technical", "architecture", "backend"],
                "meta": {"topic": "system_design", "sentiment": "positive"}
            },
            {
                "content": "User's company is in the e-commerce sector, focusing on sustainable products",
                "context_type": "user_profile",
                "user_id": "user_123",
                "tags": ["business", "industry", "company_info"],
                "meta": {"verified": True, "source": "onboarding"}
            },
            {
                "content": "Customer mentioned birthday is coming up next month, looking for gift ideas",
                "context_type": "conversation",
                "user_id": "user_456",
                "session_id": "session_003",
                "tags": ["personal", "events", "shopping"],
                "meta": {"intent": "gift_search", "urgency": "medium"}
            },
            {
                "content": "User reported a bug in the checkout process on mobile devices",
                "context_type": "support_ticket",
                "user_id": "user_789",
                "session_id": "session_004",
                "tags": ["bug", "mobile", "checkout"],
                "meta": {"priority": "high", "status": "open", "device": "iOS"}
            }
        ]

        for i, memory_data in enumerate(test_memories, 1):
            memory = Memory(
                org_id=test_org.id,
                **memory_data
            )
            db.add(memory)
            print(f" {i}. {memory_data['content'][:60]}...")

        db.commit()
        print(f" Created {len(test_memories)} test memories")

        # Display summary
        print("\n" + "="*70)
        print("🎉 DATABASE SEEDING COMPLETE!")
        print("="*70)
        print(f"\n📋 Summary:")
        print(f"   - Organizations: 1")
        print(f"   - Memories: {len(test_memories)}")
        print(f"\n🔑 API KEY (save this!):")
        print(f"   {test_org.api_key}")
        print(f"\n💡 Next steps:")
        print(f"   1. Use the API key above in your application")
        print(f"   2. Test the memory endpoints")
        print(f"   3. Add embeddings to enable semantic search")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()


