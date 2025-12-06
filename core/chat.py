# core/chat.py
from llama_index.core.chat_engine.types import ChatMode

def create_chat_engine(index):
    """
    创建一个具备上下文记忆的聊天引擎
    """
    if not index:
        return None
    
    # 使用 "condense_question" 或 "context" 模式
    # context 模式最适合基于文档的问答
    chat_engine = index.as_chat_engine(
        chat_mode=ChatMode.CONTEXT,
        system_prompt = (
            "你是一个专业的课程助教机器人。"
            "请始终严格基于提供的【上下文知识库】来回答用户的问题。"
            "如果用户的提问超出了知识库的范围，或者知识库里没有相关信息，"
            "请直接回答：'**根据当前的知识库，我没有找到相关信息。**'，"
            "不要尝试编造答案，也不要列出不相关的引用。"
        ),
        similarity_top_k=3  # 每次检索参考 3 段原文
    )
    return chat_engine