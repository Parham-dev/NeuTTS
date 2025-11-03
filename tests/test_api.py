#!/usr/bin/env python3
"""
Test script for NeuTTS Air API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8001"


def test_health():
    """Test health check endpoint"""
    print("=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_list_voices():
    """Test list voices endpoint"""
    print("=" * 60)
    print("Testing List Voices")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/voices")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_synthesize(text, voice="dave"):
    """Test synthesis endpoint - now returns JSON with audio URL"""
    print("=" * 60)
    print(f"Testing Synthesis with voice: {voice}")
    print("=" * 60)
    print(f"Text: {text}")

    response = requests.post(
        f"{BASE_URL}/synthesize",
        json={"text": text, "voice": voice}
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")

        # Download the audio file
        audio_url = f"{BASE_URL}{data['audio_url']}"
        print(f"\n📥 Downloading audio from: {audio_url}")
        audio_response = requests.get(audio_url)

        if audio_response.status_code == 200:
            filename = f"tests/output_{voice}.wav"
            with open(filename, "wb") as f:
                f.write(audio_response.content)
            print(f"✓ Audio saved to: {filename}")
            print(f"⏱️  Duration: {data['duration']:.2f}s")
            print(f"🚀 Generation time: {data['generation_time']:.2f}s")
    else:
        print(f"Error: {response.text}")
    print()


if __name__ == "__main__":
    print("\n🎤 NeuTTS Air API Test Suite\n")

    # Test 1: Health check
    test_health()

    # Test 2: List voices
    test_list_voices()

    # Test 3: Synthesize with Dave
    test_synthesize(
        text="Hello, this is Dave speaking. How are you today?",
        voice="dave"
    )

    # Test 4: Synthesize with Jo
    test_synthesize(
        text="Hi there, I'm Jo. Nice to meet you!",
        voice="jo"
    )

    print("=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)
