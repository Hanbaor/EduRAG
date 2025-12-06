import os
import faiss
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    StorageContext, 
    load_index_from_storage
)
from llama_index.vector_stores.faiss import FaissVectorStore

def load_or_build_index():
    """
    基于 FAISS 向量数据库加载或构建索引
    """
    PERSIST_DIR = "./storage"
    DATA_DIR = "./data"
    
    # BAAI/bge-small-zh-v1.5 的维度是 512
    d = 512 

    # 1. 尝试从本地加载 FAISS 索引
    if os.path.exists(PERSIST_DIR):
        print("📂 [Data] 发现本地 FAISS 索引，正在加载...")
        try:
            # 加载向量存储
            vector_store = FaissVectorStore.from_persist_dir(PERSIST_DIR)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, 
                persist_dir=PERSIST_DIR
            )
            return load_index_from_storage(storage_context)
        except Exception as e:
            print(f"⚠️ [Data] 索引加载失败，将重新构建: {e}")

    # 2. 重新构建索引
    print("🚀 [Data] 正在初始化 FAISS 并构建索引...")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        return None

    try:
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        if not documents:
            print("❌ [Data] data 文件夹为空！")
            return None
        
        # --- FAISS 核心初始化代码 ---
        faiss_index = faiss.IndexFlatIP(d) # 使用内积 (Inner Product) 计算相似度
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        # --------------------------

        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context
        )
        
        # 保存到本地
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("✅ [Data] FAISS 索引构建完成并已保存！")
        return index
    except Exception as e:
        print(f"❌ [Data] 构建索引出错: {e}")
        return None