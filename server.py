from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from langserve import add_routes
from agent import schedule_agent

app = FastAPI(
    title="SoundHopper (Local)",
    version="1.0",
    description="The SoundHopper Ferry Agent"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SoundHopper Ferry Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: sans-serif; background: #005151; display: flex; justify-content: center; height: 100vh; align-items: center; }
            .container { width: 90%; max-width: 800px; height: 90vh; background: white; border-radius: 20px; display: flex; flex-direction: column; }
            .header { background: #007B5F; color: white; padding: 20px; text-align: center; font-weight: bold; }
            #chat { flex: 1; overflow-y: auto; padding: 20px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 10px; max-width: 80%; }
            .user { align-self: flex-end; background: #007B5F; color: white; margin-left: auto; }
            .assistant { align-self: flex-start; background: #f0f0f0; color: black; }
            .input-area { padding: 20px; display: flex; gap: 10px; }
            input { flex: 1; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
            button { padding: 10px 20px; background: #007B5F; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">⛴️ SoundHopper</div>
            <div id="chat"></div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Ask about ferries..." autofocus>
                <button id="send">Send</button>
            </div>
        </div>
        <script>
            const chat = document.getElementById('chat');
            const input = document.getElementById('input');
            
            async function sendMessage() {
                const msg = input.value.trim();
                if (!msg) return;
                
                addMessage(msg, 'user');
                input.value = '';
                
                try {
                    const response = await fetch('/agent/invoke', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            input: { messages: [{type: "human", content: msg}] },
                            config: { configurable: {"thread_id": "web-" + Date.now()} }
                        })
                    });
                    const data = await response.json();
                    const lastMsg = data.output.messages[data.output.messages.length - 1];
                    let text = Array.isArray(lastMsg.content) ? lastMsg.content.map(b => b.text).join("") : lastMsg.content;
                    addMessage(text, 'assistant');
                } catch (e) {
                    addMessage("Error: " + e.message, 'assistant');
                }
            }
            
            function addMessage(text, cls) {
                const div = document.createElement('div');
                div.className = 'message ' + cls;
                div.innerText = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }
            
            document.getElementById('send').onclick = sendMessage;
            input.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
        </script>
    </body>
    </html>
    """

add_routes(
    app,
    schedule_agent,
    path="/agent"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)