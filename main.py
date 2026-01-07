from fastapi import FastAPI
import sys
from pathlib import Path

# Add python directory to path
sys.path.append(str(Path(__file__).parent / "python"))

try:
    from config.database import engine, Base
    from models import Organization, Memory
except ImportError:
    pass

app = FastAPI(title="Antler API")

@app.get("/")
def read_root():
    return {"message": "Antler API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
