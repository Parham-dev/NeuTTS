#!/usr/bin/env python3
"""
Simple entry point to start the NeuTTS Air API server
"""

if __name__ == "__main__":
    import uvicorn
    from api.server import app

    print("🎤 Starting NeuTTS Air API Server...")
    print("📍 URL: http://localhost:8001")
    print("📖 Docs: http://localhost:8001/docs")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
