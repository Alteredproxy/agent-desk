from graph import graph
from langgraph.checkpoint.memory import InMemorySaver

config = {"configurable": {"thread_id": "1"}}

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit" or "quit" or "stop":
        break
    
    events = graph.stream({"messages": [("user", user_input)]}, config)
    for event in events:
        for node_name, node_state in event.items():
            if "messages" in node_state:
                for message in node_state["messages"]:
                    if message.type == "ai":
                        print("AI:", message.content)
                    continue

    state = graph.get_state(config)
    if 'tools' in state.next:
        user_input = input("Approve tool call? (y/n): ")
        if user_input == "y":
            events = graph.stream(None, config)
            state = graph.get_state(config)
            for event in events:
                for node_name, node_state in event.items():
                    if "messages" in node_state:
                        for message in node_state["messages"]:
                            if message.type == "ai":
                                print("AI:", message.content)
                            continue
        else:
            print("Agent did not approve tool call")
