from agent import schedule_agent

def main():
    print("-------------------------------------------------------")
    print("⛴️  SOUNDHOPPER (LangGraph Edition) - LOCAL TERMINAL")
    print("   Type 'quit' or 'q' to exit.")
    print("-------------------------------------------------------")

    # This ID tells the agent "This is the same conversation"
    # In a real app, this would be the user's Session ID.
    config = {"configurable": {"thread_id": "1"}}

    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "q", "exit"]:
                print("SoundHopper: Safe travels!")
                break
            
            input_message = {"messages": [("user", user_input)]}

            # We pass 'config' so the agent loads the previous memories
            result = schedule_agent.invoke(input_message, config=config)

            # --- CLEANER OUTPUT LOGIC ---
            # Gemini 2.5 sometimes returns a list of blocks [{'text': '...'}]
            # instead of a simple string. This handles both.
            raw_content = result["messages"][-1].content
            
            if isinstance(raw_content, list):
                # Join all text parts together
                clean_text = "".join([block.get("text", "") for block in raw_content if "text" in block])
                print(f"SoundHopper: {clean_text}")
            else:
                # It's just a normal string
                print(f"SoundHopper: {raw_content}")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()