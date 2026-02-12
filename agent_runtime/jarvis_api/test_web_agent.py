import asyncio
import logging
from app.agents.dispatcher import dispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_web_agent():
    print("Testing A-WEB Agent...")
    
    # 1. Check if registered
    agents = dispatcher.get_available_agents()
    web_agent = next((a for a in agents if a["code"] == "A-WEB"), None)
    
    if not web_agent:
        print("❌ A-WEB agent NOT found in registry!")
        return
    
    print(f"✅ A-WEB found: {web_agent['name']}")
    
    # 2. Dispatch search request
    print("\nDispatching search request for 'Kali Linux tools'...")
    response = await dispatcher.dispatch_to_agent(
        agent_code="A-WEB",
        intent="search",
        params={"query": "Kali Linux top 10 tools 2024"},
        from_agent="test-script"
    )
    
    if response.status.value == "success":
        print("✅ Search successful!")
        print(f"Summary: {response.summary}")
        print("\nArtifacts (Results):")
        for artifact in response.artifacts:
            print(artifact[:500] + "...") # Print first 500 chars
    else:
        print(f"❌ Search failed: {response.summary}")
        print(f"Errors: {response.errors}")

if __name__ == "__main__":
    asyncio.run(test_web_agent())
