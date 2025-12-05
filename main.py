from graph import graph
import uuid

# 1. Create a unique ID for this conversation
# In a real app, this would be the User ID or Session ID.
# This ensures the memory stays consistent for this specific chat.
thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": thread_id}}

print("------------------------------------------------")
print("🚀 SWISS AIR AGENT (GCP EDITION) IS ONLINE")
print("------------------------------------------------")
print("Type 'quit' to exit.")

# 2. The Chat Loop
while True:
    # Get User Input
    user_input = input("\nUser: ")
    
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    # 3. Send input to the Graph (The Brain)
    # We pass the input as a "user" message.
    events = graph.stream(
        {"messages": [("user", user_input)]},
        config,
        stream_mode="values"
    )

    # 4. Print the Output
    # The graph returns the WHOLE history every time.
    # We just want to see the last message.
    for event in events:
        messages = event.get("messages")
        if messages:
            last_message = messages[-1]
            # Only print if it's from the AI (not the user repeating themselves)
            if last_message.type == "ai":
                print(f"Agent: {last_message.content}")