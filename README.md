<div align="center">

# 🎓 EduRAG: Intelligent Tutoring System

<!-- Badges -->
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-v0.10-important?style=flat-square)](https://www.llamaindex.ai/)
[![FAISS](https://img.shields.io/badge/VectorDB-FAISS-blue?style=flat-square)](https://github.com/facebookresearch/faiss)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**基于 RAG 技术的垂直领域智能学习与问答助手**

[特性介绍](#-核心特性) •
[快速开始](#-快速开始) •
[系统架构](#-系统架构) •
[效果演示](#-效果演示)

</div>

---

## 📖 项目简介

**EduRAG** 是一个专为垂直领域教育（如《计算机网络》课程）设计的智能助教系统。

针对通用大模型在专业领域容易产生“幻觉”和“知识边界模糊”的问题，本项目基于 **Retrieval-Augmented Generation (RAG)** 技术，结合 **FAISS** 向量数据库与 **DeepSeek** 大模型，构建了一个严谨、可追溯且具备主动出题能力的交互式学习平台。

## ✨ 核心特性

- **📚 严守知识边界 (Strict Boundary)**  
  通过 Prompt Engineering 与相似度阈值过滤，拒绝回答教材以外的问题，杜绝模型幻觉。

- **🧩 动态随机出题 (Randomized Quiz)**  
  独创 **"广撒网 + 随机捞" (Expand-then-Sample)** 检索策略，从向量库长尾分布中挖掘考点，避免题目同质化。

- **⚡ 毫秒级热启动 (Hot Start)**  
  基于本地持久化机制，实现了索引的序列化存储。二次启动无需重新计算 Embedding，启动速度提升 **37倍**。

- **🔍 引用溯源 (Source Citation)**  
  每一次回答都会精准标注参考的文档来源（文件名 + 文本片段），让学习有据可依。

## 🛠️ 技术栈

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **LLM** | DeepSeek-Chat | 强大的指令跟随能力与 32K 上下文窗口 |
| **Embedding** | BAAI/bge-small-zh-v1.5 | 针对中文语义优化的轻量级向量模型 (512维) |
| **Vector DB** | FAISS (IndexFlatIP) | 基于内积的高效精确检索 |
| **Framework** | LlamaIndex | RAG 数据编排与流水线管理 |
| **Frontend** | Streamlit | 极简的交互式 Web 界面 |

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/Hanbaor/EduRAG.git
cd EduRAG
```

### 2. 安装依赖
建议使用 Python 3.10+ 环境：
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
在项目根目录创建 `.env` 文件，填入你的 API Key：
```ini
# 使用 DeepSeek 或兼容 OpenAI 格式的 API
OPENAI_API_KEY="sk-your-api-key-here"
OPENAI_API_BASE="https://api.deepseek.com/v1"
```

### 4. 准备数据
将你的 PDF 或 TXT 教材放入 `data/` 目录。
> *注：首次运行时，系统会自动扫描该目录并构建向量索引。*

### 5. 启动应用
```bash
streamlit run app.py
```
浏览器自动打开 `http://localhost:8501` 即可使用。

## 📂 项目结构

```bash
EduRAG/
├── core/                   # 核心算法模块
│   ├── config.py           # 模型配置
│   ├── data_loader.py      # ETL 与 索引构建 (Data Pipeline)
│   ├── chat.py             # 对话逻辑
│   └── quiz.py             # 出题策略
├── data/                   # 原始文档存放区
├── storage/                # 向量索引持久化目录
├── app.py                  # 前端入口
└── requirements.txt        # 依赖列表
```

## 📸 效果演示

### 智能问答 & 引用溯源
*(此处可放入你的问答截图，例如：回答“什么是死锁”并显示来源)*

### 知识自测 & 自动出题
*(此处可放入你的侧边栏出题截图)*

## 👨‍💻 作者与致谢

*   **Student**: Li Zongyang (Hanbaor)
*   **Course**: Fundamentals and Applications of Large Models
*   **Date**: November 2025

---
<div align="center">
Created with ❤️ by Hanbaor
</div>
