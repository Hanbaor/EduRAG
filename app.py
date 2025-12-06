# app.py
import streamlit as st
from core.config import init_settings
from core.data_loader import load_or_build_index
from core.chat import create_chat_engine
from core.quiz import generate_quiz

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="AI 课程助教", 
    page_icon="🤖",
    layout="wide"  # 使用宽屏模式，让侧边栏和主界面更协调
)

# 注入 CSS 隐藏顶部 padding，让界面更紧凑
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem;}
    /* 让侧边栏的题目显示更清晰 */
    .stRadio p {font-size: 16px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. 系统初始化 ---
if "init_done" not in st.session_state:
    with st.spinner("正在启动 AI 引擎 & FAISS 数据库..."):
        init_settings()
        st.session_state.index = load_or_build_index()
        st.session_state.init_done = True
        
        if st.session_state.index:
            st.session_state.chat_engine = create_chat_engine(st.session_state.index)
        else:
            st.session_state.chat_engine = None

# 初始化 Session 状态
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好！我是你的专属 AI 助教。关于课程内容，尽管问我！"}]
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
    st.session_state.quiz_submitted = False

# ==================================================
#  👉 侧边栏：智能测验区 (Quiz Zone)
#  把“出题”移到左边，不打扰右边的对话
# ==================================================
with st.sidebar:
    st.title("🧩 知识自测")
    st.caption("学完知识点？来做个题巩固一下吧！")
    
    st.divider()
    
    # 出题控制区
    col_diff, col_btn = st.columns([1, 1.5])
    with col_diff:
        difficulty = st.selectbox("难度", ["简单", "中等", "困难"], label_visibility="collapsed")
    with col_btn:
        if st.button("🎲 生成新题", type="primary", use_container_width=True):
            with st.spinner("出题中..."):
                quiz, source = generate_quiz(st.session_state.index, difficulty)
                if quiz:
                    st.session_state.current_quiz = quiz
                    st.session_state.quiz_source = source
                    st.session_state.quiz_submitted = False
                    st.rerun()

    # 题目展示区
    if st.session_state.current_quiz:
        q = st.session_state.current_quiz
        
        # 题干
        st.markdown(f"**Q: {q['question']}**")
        
        # 选项
        user_choice = st.radio(
            "请选择答案:", 
            q['options'], 
            key="quiz_radio_sidebar",
            index=None,
            disabled=st.session_state.quiz_submitted
        )
        
        # 提交按钮
        if st.button("提交答案", use_container_width=True):
            if not user_choice:
                st.toast("⚠️ 请先选择一个选项", icon="⚠️")
            else:
                st.session_state.quiz_submitted = True
                if user_choice == q['answer']:
                    st.success("✅ 回答正确！")
                    st.balloons()
                else:
                    st.error(f"❌ 答错了，正确答案是：{q['answer']}")
                
                # 显示解析（用 expander 包裹，保持侧边栏整洁）
                with st.expander("💡 查看解析 & 来源", expanded=True):
                    st.markdown(f"**解析**：\n{q['analysis']}")
                    st.divider()
                    st.caption(f"📄 来源：\n{st.session_state.quiz_source[:80]}...")
    
    else:
        st.info("👈 点击上方按钮开始测试")

    # 底部工具栏
    st.divider()
    if st.button("🗑️ 清空对话历史"):
        st.session_state.messages = [{"role": "assistant", "content": "对话已重置。请问有什么可以帮您？"}]
        st.rerun()

# ==================================================
#  👉 主界面：核心对话区 (Chat Zone)
# ==================================================
st.subheader("💬 课程 AI 答疑")

# 1. 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 如果有引用源，优雅地展示
        if "sources" in msg and msg["sources"]:
            with st.expander(f"📚 参考了 {len(msg['sources'])} 处文档"):
                for idx, source in enumerate(msg["sources"]):
                    st.markdown(f"**[{idx+1}] {source['file_name']}**")
                    st.caption(source['text'])

# 2. 处理输入
if prompt := st.chat_input("输入问题，例如：什么是死锁？..."):
    # 记录用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成 AI 回答
    with st.chat_message("assistant"):
        if st.session_state.chat_engine:
            response_placeholder = st.empty()
            full_response = ""
            sources = []
            
            try:
                # 流式生成
                streaming_response = st.session_state.chat_engine.stream_chat(prompt)
                
                for token in streaming_response.response_gen:
                    full_response += token
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # ---  【核心修改：智能引用过滤】  ---
                
                # 1. 定义拒答关键词（根据 core/chat.py 里的设定）
                refusal_signs = [
                    "没有找到", "无法回答", "不包含", "超出", 
                    "没有相关信息", "unknown", "don't know"
                ]
                
                # 2. 判断 AI 是否拒答
                # 逻辑：如果回答里包含上述关键词，说明知识库里没货
                is_refusal = any(sign in full_response for sign in refusal_signs)

                # 3. 只有在“非拒答”的情况下，才提取引用源
                if not is_refusal and hasattr(streaming_response, "source_nodes"):
                    for node in streaming_response.source_nodes:
                        # 4. (可选) 增加分数过滤：如果相关度太低(score < 0.35)，也过滤掉
                        # 注意：不同模型的 score 范围不同，需根据实际情况调整，这里先注释掉
                        # if node.score < 0.35: continue 

                        file_name = node.metadata.get("file_name", "未知文档")
                        text_preview = node.text[:100].replace("\n", " ") + "..."
                        sources.append({"file_name": file_name, "text": text_preview})

                # 4. 展示引用 (只有当 sources 不为空时才显示)
                if sources:
                    with st.expander(f"📚 参考了 {len(sources)} 处文档"):
                        for idx, source in enumerate(sources):
                            st.markdown(f"**[{idx+1}] {source['file_name']}**")
                            st.caption(source['text'])
                
                # ---------------------------------- 

                # 保存历史
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response, 
                    "sources": sources
                })
                
            except Exception as e:
                st.error(f"生成出错: {e}")
        else:
            st.error("系统初始化失败，请检查日志。")