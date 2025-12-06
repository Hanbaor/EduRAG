FROM python:3.10-slim

# 工作目录设为 /app
WORKDIR /app


ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 安装基础工具
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# --- 虚拟环境配置 ---
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# --- 安装依赖 ---
# 因为 context 是 "..", 所以这里 COPY 会去根目录找 requirements.txt
# 这就是为什么要把 context 设为上一级的原因！
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口
EXPOSE 8501

# 这里的 CMD 其实会被 VS Code 覆盖，但留着也没事
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]