# core/quiz.py
import json
import random
from llama_index.core import Settings

def generate_quiz(index, difficulty="中等"):
    """
    基于 RAG 随机出题 (优化版：大幅提升随机性)
    """
    if not index:
        return None, "索引未初始化"

    # --- 扩展关键词库  ---
    keywords = [
        # 基础类
        "定义", "概念", "原理", "特征", "分类", "组成",
        # 比较类
        "区别", "优缺点", "异同", "对比", "关系",
        # 过程类
        "流程", "步骤", "阶段", "生命周期", "算法",
        # 细节类
        "协议", "参数", "格式", "标准", "模型", "架构",
        # 场景类
        "应用", "场景", "案例", "实现", "作用"
    ]
    
    # 随机选一个关键词
    search_query = random.choice(keywords)

    # ---"广撒网"策略 ---
    # 我们检索前 20 个最相关的片段，而不是前 2 个
    # 这样能覆盖到书的更多角落，而不仅是绪论
    retriever = index.as_retriever(similarity_top_k=20)
    nodes = retriever.retrieve(search_query)
    
    if not nodes:
        return None, "未检索到足够内容，无法出题"

    # --- "随机捞"策略 ---
    # 从检索到的 20 个结果中，随机挑一个
    # 这样即使搜同一个词，每次拿到的段落也不一样
    selected_node = random.choice(nodes)
    context_text = selected_node.text

    # 构造 Prompt
    prompt = f"""
    你是一位大学老师。请根据以下参考文档，出一道【单项选择题】。
    
    【难度要求】：{difficulty}
    
    【参考文档】：
    {context_text}
    
    【出题要求】：
    1. 题目必须严格基于上述文档内容，不能编造。
    2. 选项要有迷惑性，但正确答案必须唯一且明确。
    3. "analysis" 字段必须引用文档原意进行解释。
    
    【输出格式要求】：
    1. 必须是严格的 JSON 格式，不要包含 Markdown 标记。
    2. 字段包含：question (题干), options (4个选项列表), answer (正确选项内容), analysis (解析)。
    
    示例 JSON:
    {{
        "question": "题目内容?",
        "options": ["A", "B", "C", "D"],
        "answer": "A",
        "analysis": "解析内容"
    }}
    """
    
    try:
        response = Settings.llm.complete(prompt)
        # 清洗数据
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        quiz_data = json.loads(clean_json)
        return quiz_data, context_text
    except Exception as e:
        print(f"❌ [Quiz] 出题失败: {e}")
        return None, f"生成错误: {str(e)}"