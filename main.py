from fastapi import FastAPI

app = FastAPI(title="K9 AI", version="0.1.0")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "K9 AI backend is running",
        "version": "0.1.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}