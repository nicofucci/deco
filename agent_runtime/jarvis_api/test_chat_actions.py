import requests
import sys

API_BASE = "http://localhost:8000/api/chat"

def test_chat_actions():
    print("Testing Chat Actions...")

    # 1. Create Conversation
    print("1. Creating conversation...")
    resp = requests.post(f"{API_BASE}/conversations", json={"title": "Original Title"})
    if resp.status_code != 200:
        print(f"❌ Failed to create: {resp.text}")
        sys.exit(1)
    chat = resp.json()
    chat_id = chat["id"]
    print(f"✅ Created chat: {chat_id} - {chat['title']}")

    # 2. Rename Conversation
    print("2. Renaming conversation...")
    new_title = "Renamed Title"
    resp = requests.patch(f"{API_BASE}/conversations/{chat_id}", json={"title": new_title})
    if resp.status_code != 200:
        print(f"❌ Failed to rename: {resp.text}")
        sys.exit(1)
    updated_chat = resp.json()
    if updated_chat["title"] == new_title:
        print(f"✅ Renamed successfully to: {updated_chat['title']}")
    else:
        print(f"❌ Rename mismatch: {updated_chat['title']}")
        sys.exit(1)

    # 3. Delete Conversation
    print("3. Deleting conversation...")
    resp = requests.delete(f"{API_BASE}/conversations/{chat_id}")
    if resp.status_code != 200:
        print(f"❌ Failed to delete: {resp.text}")
        sys.exit(1)
    print("✅ Delete request successful")

    # 4. Verify Deletion
    print("4. Verifying deletion...")
    resp = requests.get(f"{API_BASE}/conversations/{chat_id}")
    if resp.status_code == 404:
        print("✅ Conversation not found (as expected)")
    else:
        print(f"❌ Conversation still exists: {resp.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    test_chat_actions()
