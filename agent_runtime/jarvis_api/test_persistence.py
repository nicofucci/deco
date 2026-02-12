import requests
import json
import time

BASE_URL = "http://localhost:8000/api/chat"

def test_chat_persistence():
    print("1. Creating a new session...")
    response = requests.post(f"{BASE_URL}/sessions", json={"title": "Test Persistence"})
    if response.status_code != 200:
        print(f"Failed to create session: {response.text}")
        return
    
    session = response.json()
    session_id = session["id"]
    print(f"Session created: {session_id}")
    
    print("2. Sending a message...")
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/message", json={"message": "Hello, do you remember this?"})
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
        return
        
    print("Message sent. Checking response...")
    updated_session = response.json()
    print(f"Messages count: {len(updated_session['messages'])}")
    
    print("3. Listing sessions to verify persistence...")
    response = requests.get(f"{BASE_URL}/sessions")
    sessions = response.json()
    found = False
    for s in sessions:
        if s["id"] == session_id:
            found = True
            print(f"Found session {session_id} in list.")
            break
            
    if not found:
        print("Session NOT found in list! Persistence failed.")
    else:
        print("Persistence verified successfully.")

if __name__ == "__main__":
    test_chat_persistence()
