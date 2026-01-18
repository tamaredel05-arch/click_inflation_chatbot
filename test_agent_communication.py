"""
Test: How a sub-agent returns information to a root agent in ADK
"""

import asyncio
from google.adk.agents import Agent


# ========== Sub Agent ==========

sub_agent = Agent(
    name="sub_agent",
    model="gemini-2.0-flash-exp",
    description="Simple sub-agent",
    instruction="""
You are a sub-agent.
When someone asks you something, return JSON:
{"status": "done", "message": "I did the work"}
"""
)


# ========== Root Agent ==========

root_agent_with_sub = Agent(
    name="root_agent",
    model="gemini-2.0-flash-exp", 
    description="Root agent with sub-agent",
    instruction="""
You are a root agent.

When receiving a question from the user:
1. Pass the question to sub_agent
2. When you get a response from sub_agent, check the status returned
3. If status="done" - tell the user "The sub-agent completed successfully!"
4. Otherwise - say "Something went wrong"

Look at the response that comes back from sub_agent and decide what to do.
""",
    sub_agents=[sub_agent]
)


# ========== Test ==========

async def test():
    print("=" * 70)
    print("🧪 Test: How Root receives information from Sub Agent")
    print("=" * 70)
    
    # Run Root with a question
    print("\n📝 Sending question to Root Agent...")
    
    result = await root_agent_with_sub.run(
        input_data={"user_question": "do something"}
    )
    
    print("\n✅ Result returned:")
    print(f"Type: {type(result)}")
    print(f"Content: {result}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test())
