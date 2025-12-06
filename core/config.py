# core/config.py
import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def init_settings():
    """初始化全局 LlamaIndex 设置"""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    # 1. 配置 DeepSeek (作为通用 LLM)
    Settings.llm = OpenAILike(
        model="deepseek-chat", 
        api_key=api_key,
        api_base=api_base,
        temperature=0.5,
        is_chat_model=True,
        max_tokens=4096,
        context_window=32768,
    )

    # 2. 配置本地 HuggingFace 嵌入模型
    print("⚙️ [Config] 正在加载嵌入模型...")
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    print("✅ [Config] 模型配置完成")