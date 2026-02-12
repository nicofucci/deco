import asyncio
import logging
from app.agents.dispatcher import dispatcher

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_rag_agent():
    print("Testing A-RAG Agent...")
    
    # 1. Store a document
    print("\n1. Storing document...")
    store_response = await dispatcher.dispatch_to_agent(
        agent_code="A-RAG",
        intent="store",
        params={
            "content": "Jarvis is an advanced AI system designed for cybersecurity operations. It integrates various tools like Nmap, Metasploit, and custom agents.",
            "metadata": {"source": "manual_entry", "topic": "jarvis_intro"}
        },
        from_agent="test-script"
    )
    
    if store_response.status.value == "success":
        print(f"✅ Document stored! ID: {store_response.details['doc_id']}")
    else:
        print(f"❌ Storage failed: {store_response.summary}")
        return

    # 2. Query the document
    print("\n2. Querying document...")
    query_response = await dispatcher.dispatch_to_agent(
        agent_code="A-RAG",
        intent="query",
        params={"query": "What is Jarvis designed for?"},
        from_agent="test-script"
    )
    
    if query_response.status.value == "success":
        print("✅ Query successful!")
        print(f"Summary: {query_response.summary}")
        print("\nArtifacts (Context):")
        for artifact in query_response.artifacts:
            print(artifact)
            
        # Verify content match
        if "cybersecurity operations" in query_response.artifacts[0]:
            print("\n✅ Verification Passed: Retrieved content matches expected context.")
        else:
            print("\n❌ Verification Failed: Content mismatch.")
    else:
        print(f"❌ Query failed: {query_response.summary}")

if __name__ == "__main__":
    asyncio.run(test_rag_agent())
