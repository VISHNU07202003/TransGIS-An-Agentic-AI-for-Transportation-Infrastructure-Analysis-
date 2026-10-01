import json
import logging
from app.agents.navigator_client import NavigatorClient
from app.agents.tool_registry import AGENT_TOOLS
from app.agents.prompts import build_system_message, build_user_message

logging.basicConfig(level=logging.INFO)

prompts = [
    ("What is the AADT here?", {"latitude": 29.6516, "longitude": -82.3248}, None),
    ("Is this intersection signalized?", None, 80329),
    ("Tell me about the traffic at this location.", {"latitude": 29.6516, "longitude": -82.3248}, None),
    ("What was the hourly volume yesterday?", None, 80329),
    ("Are there any traffic monitoring sites nearby?", {"latitude": 29.6516, "longitude": -82.3248}, None),
    ("What is the weather like?", {"latitude": 29.6516, "longitude": -82.3248}, None),
    ("I need traffic info for University Ave.", None, None),
    ("Show me the congestion.", None, None),
    ("Are there traffic signals and what is the AADT?", None, 80329),
    ("How many pedestrians crossed here?", None, 80329),
    ("Is this location managed by the state or city?", {"latitude": 29.6516, "longitude": -82.3248}, None),
    ("What is the speed limit here?", None, 80329),
    ("Traffic traffic beep boop", None, None),
    ("Where did you get this traffic count?", None, 80329),
    ("What was the traffic volume on Jan 1 1990?", None, 80329),
    ("I want to know about the traffic at intersection 999999.", None, 999999),
]

def run_spike():
    client = NavigatorClient()
    if not client.is_configured():
        print("API key not configured! Cannot run tool spike.")
        return

    results = []
    for q, loc, i_id in prompts:
        print(f"Testing prompt: {q}")
        msgs = [build_system_message()]
        
        ctx = []
        if loc:
            ctx.append(f"Coordinates: lat={loc['latitude']}, lon={loc['longitude']}")
        if i_id:
            ctx.append(f"Selected intersection ID: {i_id}")
            
        msgs.append(build_user_message(q, ", ".join(ctx) if ctx else None))
        
        try:
            resp = client.chat_completion(messages=msgs, tools=AGENT_TOOLS)
            choice = resp.choices[0]
            msg = choice.message
            
            tool_calls = msg.tool_calls
            if tool_calls:
                for tc in tool_calls:
                    results.append({
                        "prompt": q,
                        "tool": tc.function.name,
                        "arguments": tc.function.arguments,
                        "status": "TOOL_CALLED"
                    })
            else:
                results.append({
                    "prompt": q,
                    "tool": "NONE",
                    "arguments": "",
                    "status": "TEXT_RESPONSE",
                    "content": msg.content
                })
        except Exception as e:
            results.append({
                "prompt": q,
                "tool": "ERROR",
                "arguments": str(e),
                "status": "ERROR"
            })
            
    with open("spike_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Done")

if __name__ == '__main__':
    run_spike()
