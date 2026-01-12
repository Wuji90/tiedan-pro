import os
import json
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from groq import Groq

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IronEgg")

app = FastAPI()

# 初始化 Groq 客户端 (从环境变量拿 Key，安全！)
client = Groq(api_key=os.environ.get("LLM_API_KEY"))

# 系统提示词 (你可以在 Render 环境变量里随时改 SYSTEM_PROMPT)
sys_prompt = os.environ.get("SYSTEM_PROMPT", "你叫铁蛋，是一个幽默的山东大汉。用简短的一两句话回答。")

@app.get("/")
async def get():
    return {"status": "IronEgg Pro is Running!", "version": "2.0"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("ESP32 Connected!")
    
    try:
        # 发送握手成功信号 (适配小智协议)
        await websocket.send_text(json.dumps({"type": "hello", "msg": "连接成功"}))
        
        while True:
            # 接收数据 (可能是文本 json，也可能是音频 binary)
            data = await websocket.receive()
            
            if "text" in data:
                # 处理文本消息 (心跳或握手)
                msg = json.loads(data["text"])
                if msg.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({"type": "heartbeat"}))
                    continue
            
            if "bytes" in data:
                # 收到音频流！(这里暂时做个回声测试，确保链路通畅)
                # 后续我们在这里加百度语音转文字
                audio_data = data["bytes"]
                logger.info(f"收到音频数据: {len(audio_data)} bytes")
                
                # 临时逻辑：只要收到声音，就让 Groq 随便回个话，证明大脑活着
                # (真正的语音识别等部署成功了再加，防报错)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": "我说话了，你听到了吗？"} 
                    ],
                    model="llama3-8b-8192",
                )
                response_text = chat_completion.choices[0].message.content
                
                # 发回给 ESP32 (文本格式)
                await websocket.send_text(json.dumps({
                    "type": "tts", 
                    "text": response_text
                }))

    except WebSocketDisconnect:
        logger.info("ESP32 Disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
