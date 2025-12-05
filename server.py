from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from langserve import add_routes
from graph import graph

app = FastAPI(
    title="Swiss Air Agent (GCP)",
    version="1.0",
    description="A LangGraph agent deployed on Google Cloud Run"
)

# CUSTOM CHAT UI - This MUST come BEFORE add_routes
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Swiss Air Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .header {
                background: #667eea;
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }
            #chat {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin: 15px 0;
                display: flex;
                animation: fadeIn 0.3s;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .message.user {
                justify-content: flex-end;
            }
            .message-content {
                max-width: 70%;
                padding: 12px 18px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            .user .message-content {
                background: #667eea;
                color: white;
                border-bottom-right-radius: 4px;
            }
            .assistant .message-content {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 4px;
            }
            .input-area {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            #input {
                flex: 1;
                padding: 12px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 15px;
                outline: none;
                transition: border 0.3s;
            }
            #input:focus {
                border-color: #667eea;
            }
            #send {
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }
            #send:hover {
                background: #5568d3;
            }
            #send:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .typing {
                padding: 12px 18px;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 18px;
                border-bottom-left-radius: 4px;
                color: #666;
                font-style: italic;
            }
            .error {
                background: #fee;
                border-color: #fcc;
                color: #c33;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                ✈️ Swiss Air Assistant
            </div>
            <div id="chat">
                <div class="message assistant">
                    <div class="message-content">
                        Hi! I'm your Swiss Air assistant. I can help you look up flights and hotels. 
                        Try asking: "Find flights from ZRH to ORD" or "Book a hotel in Chicago"
                    </div>
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Ask about flights or hotels..." autofocus>
                <button id="send">Send</button>
            </div>
        </div>
        
        <script>
            const chat = document.getElementById('chat');
            const input = document.getElementById('input');
            const send = document.getElementById('send');
            
            async function sendMessage() {
                const message = input.value.trim();
                if (!message) return;
                
                input.disabled = true;
                send.disabled = true;
                
                addMessage(message, 'user');
                input.value = '';
                
                const typingId = 'typing-' + Date.now();
                chat.innerHTML += '<div class="message assistant" id="' + typingId + '"><div class="message-content typing">Thinking...</div></div>';
                chat.scrollTop = chat.scrollHeight;
                
                try {
                    const response = await fetch('/agent/invoke', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            input: {
                                messages: [{type: "human", content: message}]
                            },
                            config: {
                                configurable: {"thread_id": "web-session-1"}
                            }
                        })
                    });
                    
                    document.getElementById(typingId).remove();
                    
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    
                    const data = await response.json();
                    const messages = data.output.messages;
                    const lastMessage = messages[messages.length - 1];
                    
                    addMessage(lastMessage.content, 'assistant');
                    
                } catch (error) {
                    document.getElementById(typingId).remove();
                    addMessage('Sorry, something went wrong. Please try again. Error: ' + error.message, 'assistant error');
                    console.error('Error:', error);
                }
                
                input.disabled = false;
                send.disabled = false;
                input.focus();
            }
            
            function addMessage(text, className) {
                const div = document.createElement('div');
                div.className = 'message ' + className;
                const content = document.createElement('div');
                content.className = 'message-content';
                content.textContent = text;
                div.appendChild(content);
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }
            
            send.onclick = sendMessage;
            input.onkeypress = (e) => { 
                if (e.key === 'Enter' && !input.disabled) sendMessage(); 
            };
        </script>
    </body>
    </html>
    """

# API routes - these go AFTER the custom route
# API routes - these go AFTER the custom route
add_routes(
    app,
    graph.with_config(configurable={"thread_id": "default"}),
    path="/agent",
    playground_type="default",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)