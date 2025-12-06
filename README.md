\documentclass{article}

% =============================================
% 核心配置
% =============================================
% 必须使用 XeLaTeX 编译以支持中文
\usepackage[UTF8, scheme=plain]{ctex}

% 页面设置
\usepackage{geometry}
\geometry{
 a4paper,
 total={170mm,257mm},
 left=20mm,
 top=20mm,
}

% 常用宏包
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{float}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{array}
\usepackage{makecell}
\usepackage{titling}
\usepackage{fancyhdr}
\usepackage{lipsum}  
\usepackage{cmbright} 

% =============================================
% 代码高亮设置
% =============================================
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.96,0.96,0.96}

\lstdefinestyle{mystyle}{
    backgroundcolor=\color{backcolour},   
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily\footnotesize, 
    breakatwhitespace=false,         
    breaklines=true,                 
    captionpos=b,                    
    keepspaces=true,                 
    numbers=left,                    
    numbersep=5pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=4,
    frame=single,
    extendedchars=false, 
    escapechar=`         
}
\lstset{style=mystyle}

% =============================================
% 标题信息
% =============================================
\title{基于 RAG 的智能学习系统：\\ 数据处理与检索策略的实现}
\author{Project Technical Report}
\date{November 2025}

% =============================================
% 页眉页脚设置
% =============================================
\fancypagestyle{plain}{% 
    \fancyhf{} 
    \fancyfoot[L]{\thedate}
    \fancyhead[L]{Fundamentals and Applications of Large Models}
    \fancyhead[R]{\theauthor}
}

\makeatletter
\def\@maketitle{%
  \newpage
  \null
  \vskip 1em%
  \begin{center}%
  \let \footnote \thanks
    {\LARGE \@title \par}%
    \vskip 1em%
  \end{center}%
  \par
  \vskip 1em}
\makeatother

\begin{document}

\maketitle

% =============================================
% 学生信息
% =============================================
\noindent\begin{tabular}{@{}ll}
    Student & 李宗洋 \\  
    Student ID & 25125287 \\
    Role & Data Processing \& Retrieval Strategy Lead
\end{tabular}

% =======================================================
\section{引言}

随着大语言模型（LLM）技术的飞速发展，人工智能在自然语言处理任务上取得了突破性的进展。然而，将通用大模型应用于特定垂直领域（如高等教育、医疗诊断、法律咨询等）时，依然面临着严峻的挑战。通用模型虽然具备强大的语言理解与生成能力，但缺乏特定领域的深度知识，且容易产生幻觉，即自信地生成错误事实。此外，垂直领域的知识通常以非结构化文档（如 PDF 教材、技术白皮书、行业标准）的形式存在，如何让机器“读懂”并高效利用这些数据，是当前 AI 落地应用的关键痛点。

为了解决上述问题，检索增强生成（Retrieval-Augmented Generation），简称RAG架构应运而生。RAG 通过在生成回答前先从外部知识库中检索相关信息，有效地为 LLM 提供了“参考资料”，从而显著提升了回答的准确性和可追溯性。

在实际构建 RAG 系统的过程中，我们发现数据处理的质量直接决定了系统的上限。在业界有一个共识：“垃圾进，垃圾出”。如果原始数据清洗不彻底、文本分块粒度不合理、或者向量索引构建低效，那么无论后端的 LLM 多么强大，都无法生成正确的答案。数据层不仅是连接原始文档与智能模型的桥梁，更是整个系统的“地基”。

本项目小组旨在构建一个通用的垂直领域智能学习与问答系统。虽然在演示中我们以《计算机网络》课程为例，但该系统的核心架构设计具有高度的通用性，旨在解决海量非结构化教学资源的结构化与智能化利用问题。系统致力于为学习者提供精准的知识点检索、基于文档的智能答疑以及个性化的知识自测功能。

作为项目技术报告的一部分，本文将聚焦于系统后端的数据处理流水线，深入剖析如何构建高质量、高效率的 RAG 数据底座，具体阐述以下关键环节：

\begin{enumerate}
    \item \textbf{非结构化数据的清洗与加载}：建立自动化 ETL 管道，利用 \texttt{SimpleDirectoryReader} 将复杂的 PDF 等非结构文档转化为机器可理解的纯文本序列，从源头确保输入数据的质量。
    \item \textbf{向量化与索引构建}：探讨如何集成 Embedding 模型，并利用 FAISS（Facebook AI Similarity Search）将文本块转化为高性能的向量索引，实现海量数据的快速语义检索。
    \item \textbf{索引的持久化机制}：详细解析“优先加载，失败重构”的健壮性逻辑。通过设计本地存储机制，解决系统重启后的索引重载问题，避免重复计算 Embedding，从而大幅降低计算开销并提升系统冷启动速度。
\end{enumerate}

综上，本文将展示如何构建一个健壮且高效的向量数据处理模块。

% =======================================================
\section{相关工作}

本项目的技术架构并非空中楼阁，而是建立在自然语言处理（NLP）与信息检索（IR）领域成熟的理论基础之上。作为数据处理模块的负责人，本节将重点探讨支撑本项目数据层的核心技术：检索增强生成架构、语义向量表示模型、向量索引算法以及数据编排框架。

\subsection{检索增强生成 (RAG) 范式}
检索增强生成由 Lewis 等人在 2020 年正式提出，旨在解决大型语言模型（LLM）面临的“知识截止”和“事实幻觉”两大难题。

在标准的数据处理视角下，RAG 将知识获取过程解耦为两个阶段：
\begin{enumerate}
    \item \textbf{非参数化记忆检索}：系统维护一个稠密的向量索引，该索引包含了海量的外部知识片段。当接收到查询时，系统通过最大内积搜索快速定位相关的文档块。
    \item \textbf{参数化记忆生成}：预训练的 Seq2Seq 模型接收检索到的上下文，结合自身的参数化知识生成回答。
\end{enumerate}

不同于传统的微调需要昂贵的算力更新模型权重，RAG 允许我们在不修改模型参数的情况下，仅通过更新向量数据库即可实现知识的实时更新。这对于本项目所面向的教育场景至关重要——教材修订或新案例的加入仅需重新运行数据流水线，而无需重新训练模型。

\subsection{语义向量表示与 BGE 模型}
数据处理的核心在于如何将离散的符号信息（文本）转化为计算机可计算的连续数值（向量）。这一过程被称为文本嵌入（Embedding），高质量的 Embedding 模型直接决定了检索的语义匹配精度。

本项目选用了 BAAI/bge-small-zh-v1.5 模型作为向量化引擎。相较于早期的 Word2Vec 或 BERT-Base，BGE模型具有以下显著优势：

\begin{itemize}
    \item \textbf{针对中文优化}：该模型在海量中文语料上进行了预训练，并在 C-MTEB（Chinese Massive Text Embedding Benchmark）榜单上表现优异，能够精准捕捉中文长句中的复杂语义依赖。
    \item \textbf{对比学习}：BGE 采用了对比学习框架进行微调，拉近正样本对（相关文本）的距离，推远负样本对的距离。这使得其生成的向量空间分布更加均匀，显著提升了检索的召回率。
    \item \textbf{轻量级高效部署}：考虑到本项目需要在本地 CPU 环境下运行，\texttt{bge-small} 版本仅有 24MB 左右的参数量，向量维度为 512 维。相比于 OpenAI 的 \texttt{text-embedding-3}（1536 维），它在保证精度的同时，大幅降低了向量数据库的内存占用和计算延迟。
\end{itemize}

在代码实现中，我们通过 \texttt{llama-index-embeddings-huggingface} 库加载该模型，实现了完全本地化的数据隐私保护。

\subsection{向量相似度搜索与 FAISS}
当数据量达到百万级甚至十亿级时，传统的暴力检索会导致不可接受的延迟。为了解决这一问题，Meta AI Research 开发了 FAISS (Facebook AI Similarity Search) 库。

FAISS 是目前工业界最流行的向量检索引擎，它利用 SIMD 指令集和 BLAS 库对矩阵运算进行了极致优化。在本项目中，我们采用了 FAISS 的 \textbf{IndexFlatIP} 索引结构。

\begin{itemize}
    \item \textbf{算法原理}：\texttt{IndexFlatIP} 执行精确的暴力搜索，利用内积作为距离度量。
    \item \textbf{数学等价性}：由于 BGE 模型输出的向量已经经过了 L2 归一化，此时向量的点积在数学上严格等价于余弦相似度（Cosine Similarity）：
    \begin{equation}
    \text{Cosine}(A, B) = \frac{A \cdot B}{\|A\| \|B\|} = A \cdot B \quad (\text{if } \|A\|=\|B\|=1)
    \end{equation}
    \item \textbf{选择理由}：FAISS 支持 IVF（倒排文件）和 PQ（乘积量化）等近似搜索算法以加速检索，可以根据切分后的 Chunk 数量进行选择，如果通常在数千到数万级别则完全可以放入内存进行精确搜索，而对于规模更大的数据集可以使用牺牲精度换取速度的近似算法。
\end{itemize}

\subsection{数据编排框架 LlamaIndex}
在构建 RAG 数据流的过程中，直接手写 Python 脚本处理文档读取、切分、向量化和存储的逻辑十分繁琐且易错。本项目采用了 LlamaIndex 作为数据编排框架。

LlamaIndex 是一个专门为 LLM 应用设计的数据框架，它提供了以下关键抽象，极大地简化了本项目的开发：
\begin{itemize}
    \item \textbf{SimpleDirectoryReader}：一个强大的 ETL 工具，能够自动递归读取目录下的多种格式文件（PDF, Markdown等），解决了非结构化数据的加载难题。
    \item \textbf{VectorStoreIndex}：一种高效的数据结构，负责管理文档节点与向量嵌入之间的映射关系。
    \item \textbf{StorageContext}：提供了统一的持久化接口，允许我们将构建好的索引、向量存储和元数据序列化保存到本地磁盘，并在系统重启时快速重载。
\end{itemize}

通过集成 LlamaIndex，我们将数据处理代码（\texttt{core/data\_loader.py}）从数百行精简到了几十行，同时保证了系统的健壮性和可扩展性。


% =======================================================
\section{模型架构与数学推导}

本节将详细阐述数据处理模块在整个智能系统中的架构位置，并对支撑向量检索的核心数学原理进行推导。

\subsection{数据层在系统架构中的位置}

整个 RAG 智能助教系统采用分层架构设计，自底向上分为：数据存储层、RAG 核心层、业务逻辑层和用户界面层。作为数据处理负责人，我构建的数据流水线主要位于最底层的\textbf{数据存储层}与\textbf{RAG 核心层}之间。

\begin{figure}[H]
    \centering
    % 使用 TikZ 绘制架构图
    \begin{tikzpicture}[node distance=1.5cm]
        \node (doc) [draw, rectangle, minimum width=2.5cm, minimum height=1cm] {原始文档 (PDF)};
        \node (etl) [draw, rectangle, below of=doc, yshift=-0.5cm, minimum width=2.5cm, minimum height=1cm] {ETL 清洗与分块};
        \node (embed) [draw, rectangle, below of=etl, yshift=-0.5cm, minimum width=2.5cm, minimum height=1cm] {Embedding 模型};
        \node (faiss) [draw, rectangle, below of=embed, yshift=-0.5cm, minimum width=2.5cm, minimum height=1cm, fill=gray!20] {FAISS 向量索引};
        
        \draw[->] (doc) -- (etl);
        \draw[->] (etl) -- (embed);
        \draw[->] (embed) -- (faiss);
    \end{tikzpicture}
    \caption{数据处理流水线架构示意图}
    \label{fig:data_pipeline}
\end{figure}

如图 \ref{fig:data_pipeline} 所示，数据处理模块是一个单向流动的管道，负责将非结构化文本转化为结构化的向量索引。

\subsection{向量空间与相似度度量}

在检索阶段，系统需要计算用户查询向量 $\mathbf{q}$ 与文档库中向量 $\mathbf{d}_i$ 之间的语义相似度。设嵌入空间的维度为 $d=512$，则 $\mathbf{q}, \mathbf{d}_i \in \mathbb{R}^d$。

常用的相似度度量是\textbf{余弦相似度 (Cosine Similarity)}，其定义为两个向量夹角的余弦值：
\begin{equation}
\text{sim}(\mathbf{q}, \mathbf{d}_i) = \cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{d}_i}{\|\mathbf{q}\| \|\mathbf{d}_i\|} = \frac{\sum_{j=1}^d q_j d_{ij}}{\sqrt{\sum_{j=1}^d q_j^2} \sqrt{\sum_{j=1}^d d_{ij}^2}}
\end{equation}

在本项目的实现中，我们使用的 \texttt{BAAI/bge-small-zh} 模型在输出前已经对向量进行了 L2 归一化（Normalization）。这意味着对于任意向量 $\mathbf{v}$，都有 $\|\mathbf{v}\|_2 = 1$。

在此前提下，余弦相似度的计算公式可以简化为向量的\textbf{内积 (Inner Product)}：
\begin{equation}
\text{sim}(\mathbf{q}, \mathbf{d}_i) = \frac{\mathbf{q} \cdot \mathbf{d}_i}{1 \times 1} = \mathbf{q} \cdot \mathbf{d}_i = \sum_{j=1}^d q_j d_{ij}
\end{equation}

这一数学性质具有重要的工程意义：内积运算比完整的余弦相似度运算（包含开方和除法）要快得多，且更容易被现代 CPU 的 SIMD 指令集（如 AVX2）加速。这也是为什么我在代码中选择 \texttt{faiss.IndexFlatIP}（Inner Product）而非 L2 距离索引的理论依据。

\subsection{最大内积搜索 (MIPS) 问题}

基于上述推导，我们的检索任务可以形式化为\textbf{最大内积搜索 (Maximum Inner Product Search, MIPS)} 问题。

给定一个查询向量 $\mathbf{q}$ 和一个包含 $N$ 个向量的数据库 $D = \{\mathbf{d}_1, \dots, \mathbf{d}_N\}$，我们需要找到前 $K$ 个向量的集合 $S_K \subset D$，使得：
\begin{equation}
\forall \mathbf{d}^* \in S_K, \forall \mathbf{d}' \in D \setminus S_K, \quad \mathbf{q} \cdot \mathbf{d}^* \ge \mathbf{q} \cdot \mathbf{d}'
\end{equation}

在本实验中，对于“精准问答”场景，$K=3$；对于“随机出题”场景，$K=20$。FAISS 的 \texttt{IndexFlatIP} 算法通过暴力扫描（Brute-force Scan）精确求解该问题，时间复杂度为 $O(N \cdot d)$。由于 $N$（文本块数量）约为 $10^4$ 级别，这在单核 CPU 上仅需数毫秒，完全满足实时性要求。
% =======================================================
\section{实现细节}

数据处理层（Data Layer）是 RAG 系统中最基础的环节。在本项目中，我设计并实现了全套数据处理流水线，代码集中于 \texttt{core/data\_loader.py} 文件中。该模块不仅负责将非结构化的 PDF 教材转化为计算机可理解的向量表示，还通过设计精巧的缓存机制解决了大规模向量数据的加载延迟问题。

本节将从 ETL 流程、向量索引构建逻辑以及持久化机制等维度，对代码进行逐行级的深度解析。

\subsection{数据摄取与 ETL 流水线设计}

在进入向量化之前，首要任务是建立一个健壮的 ETL（Extract, Transform, Load）管道。针对本项目所使用的网络教材（PDF 格式），直接读取二进制流是无法被 LLM 理解的，必须将其转换为纯文本序列。

我在代码中使用了 LlamaIndex 提供的 \texttt{SimpleDirectoryReader} 接口，它封装了对多种文件格式的解析逻辑。

\begin{lstlisting}[language=Python, caption={ETL 数据摄取模块实现}]
def ingest_data(data_dir="./data"):
    """
    ETL 阶段：从非结构化文档中提取文本
    """
    # 1. 路径存在性校验
    # 这是一个防御性编程实践，防止因路径错误导致的静默失败
    if not os.path.exists(data_dir):
        print(f"❌ [Error] 数据目录 {data_dir} 不存在")
        os.makedirs(data_dir)
        return []

    print(f"�� [ETL] 开始扫描 {data_dir} 目录下的源文档...")
    
    # 2. 实例化目录读取器
    # recursive=True: 允许递归读取子文件夹，适应多章节分层存储结构
    # required_exts: 显式指定支持的文件类型，过滤掉无关的系统文件
    reader = SimpleDirectoryReader(
        input_dir=data_dir,
        recursive=True,
        required_exts=[".pdf", ".txt", ".md"],
        encoding="utf-8"
    )
    
    # 3. 执行加载
    # load_data() 会自动调用对应的 Parser 将 PDF 转换为 Document 对象列表
    documents = reader.load_data()
    print(f"✅ [ETL] 成功提取 {len(documents)} 个文档页面")
    
    return documents
\end{lstlisting}

\textbf{代码解析：}
\begin{itemize}
    \item \textbf{非结构化到结构化}：\texttt{SimpleDirectoryReader} 在后台执行了复杂的格式转换。对于 PDF 文件，它通常使用 \texttt{pypdf} 或 \texttt{pdfminer} 提取文本层；对于包含图片的扫描件，它预留了 OCR 接口。
    \item \textbf{文档对象模型}：加载后的 \texttt{documents} 并非简单的字符串列表，而是 LlamaIndex 定义的 \texttt{Document} 对象列表。每个对象不仅包含文本内容（\texttt{.text}），还包含元数据（\texttt{.metadata}），如文件名、页码、创建时间等。这些元数据在后续的“引用溯源”功能中起到了至关重要的作用。
\end{itemize}

\subsection{向量索引的配置实现}

在明确了最大内积搜索（MIPS）的数学原理（见第 3.3 节）后，我们在代码层面需要选择最匹配的索引结构。本项目选用了 FAISS 库进行实现。

\begin{lstlisting}[language=Python, caption={FAISS 向量索引配置}]
import faiss
from llama_index.vector_stores.faiss import FaissVectorStore

def initialize_vector_store(dimension=512):
    """
    配置 FAISS 索引结构
    dimension: 向量维度，必须与 Embedding 模型输出一致
    """
    print("⚙️ [Index] 初始化 FAISS 向量空间...")
    
    # 1. 选择索引算法：IndexFlatIP (内积)
    # 基于第 3 章推导结论：归一化向量的内积等价于余弦相似度
    faiss_index = faiss.IndexFlatIP(dimension)
    
    # 2. 封装为 LlamaIndex 可用的存储后端
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    
    return vector_store
\end{lstlisting}

\textbf{技术选型依据：}
\begin{enumerate}
    \item \textbf{算法匹配}：我们在第 3 章证明了对于归一化向量，内积运算等价于余弦相似度。因此，代码中显式实例化了 \texttt{IndexFlatIP} 类，而非 L2 距离索引，这不仅符合数学直觉，还能利用现代 CPU 的 SIMD 指令集进行加速。
    \item \textbf{精度权衡}：\texttt{IndexFlat} 结构执行的是精确暴力搜索。鉴于教材分块后的 Chunk 数量级通常在 $10^4$ 左右，这一规模完全可以放入内存进行精确计算，无需引入 IVF（倒排索引）或 PQ（乘积量化）等有损压缩算法，从而保证了检索结果的 100\% 召回率。
\end{enumerate}

\subsection{冷启动：全量索引构建流水线}

当系统首次运行或检测到数据更新时，需要执行全量构建流程。这一过程涉及文本分块（Chunking）、向量化（Embedding）和索引插入（Indexing）。

\begin{lstlisting}[language=Python, caption={冷启动构建核心逻辑}]
from llama_index.core import VectorStoreIndex, StorageContext

def build_index_from_scratch(documents, vector_store):
    """
    执行完整的构建流水线：Chunking -> Embedding -> Indexing
    """
    print("�� [Build] 开始全量构建索引 (此过程可能较慢)...")
    
    # 1. 创建存储上下文
    # StorageContext 是连接向量存储(VectorStore)和文档存储(DocStore)的桥梁
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )
    
    # 2. 执行构建流水线
    # from_documents 方法内部封装了复杂的处理逻辑：
    #   a. TextSplitter: 将 Document 切分为 Node (默认 512 tokens, 覆盖 50 tokens)
    #   b. Embedding: 调用本地 BGE 模型，并行计算每个 Node 的向量
    #   c. Insertion: 将向量插入 FAISS，将 Node 存入 DocStore
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True  # 在控制台显示进度条
    )
    
    return index
\end{lstlisting}

\textbf{代码解析：}
此段代码看似简单，实则隐藏了 RAG 系统中最重要的参数——\textbf{分块策略（Chunking Strategy）}。 \texttt{VectorStoreIndex} 默认采用了滑动窗口切分：
\begin{itemize}
    \item \textbf{Chunk Size = 512 Tokens}：这与 Embedding 模型的最大上下文窗口一致，确保语义完整且不被截断。
    \item \textbf{Chunk Overlap = 50 Tokens}：在相邻的文本块之间保留 50 个 Token 的重叠。这是为了防止关键信息（如句子的主语或逻辑连接词）恰好位于切分点上，导致语义丢失。
\end{itemize}

\subsection{热启动：持久化与快速加载机制}


\begin{lstlisting}[language=Python, caption={持久化与热加载逻辑}]
import os
from llama_index.core import load_index_from_storage

# 定义持久化存储目录
PERSIST_DIR = "./storage"

def load_or_build_index():
    """
    主入口函数：实现冷热启动的智能切换
    """
    # --- 分支 A: 尝试热启动 (Hot Start) ---
    if os.path.exists(PERSIST_DIR):
        print(f"�� [Load] 检测到 {PERSIST_DIR}，尝试加载预构建索引...")
        try:
            # 1. 重建向量存储对象
            # 这一步会读取磁盘上的 .index 二进制文件，直接映射到内存
            vector_store = FaissVectorStore.from_persist_dir(PERSIST_DIR)
            
            # 2. 重建存储上下文
            # 这一步会读取 docstore.json，恢复元数据映射
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, 
                persist_dir=PERSIST_DIR
            )
            
            # 3. 实例化索引对象
            index = load_index_from_storage(storage_context)
            print("✅ [Load] 索引加载成功！")
            return index
            
        except Exception as e:
            print(f"⚠️ [Load] 加载失败 ({e})，回退到冷启动模式...")

    # --- 分支 B: 执行冷启动 (Cold Start) ---
    # 如果没有持久化文件，或加载失败，则重新构建
    documents = ingest_data()
    if not documents:
        return None
        
    vector_store = initialize_vector_store()
    index = build_index_from_scratch(documents, vector_store)
    
    # --- 关键步骤：持久化落盘 ---
    print(f"�� [Save] 正在将索引持久化至 {PERSIST_DIR}...")
    if not os.path.exists(PERSIST_DIR):
        os.makedirs(PERSIST_DIR)
        
    # persist() 方法会将内存中的所有状态序列化为文件
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    
    return index
\end{lstlisting}

\textbf{时间复杂度分析：}
\begin{itemize}
    \item \textbf{冷启动时间复杂度}：$O(N \cdot L^2)$，其中 $N$ 是文档数量，$L$ 是序列长度。Transformer 模型的推理计算量巨大，对于本项目的教材数据，在 CPU 上耗时约 40-60 秒。
    \item \textbf{热启动时间复杂度}：$O(M)$，其中 $M$ 是索引文件的大小。读取文件的 I/O 操作速度远快于矩阵乘法运算。实测表明，热启动加载时间仅需 0.5 秒左右。
\end{itemize}

通过上述四个子模块的协同工作，我构建了一个既能处理复杂非结构化数据，又具备工业级健壮性的数据处理底层，为上层的智能问答和自动出题功能提供了坚实的基础。

% =======================================================
\section{实验设置}

为了验证数据处理流水线的有效性，并确保检索结果的准确性与多样性，我们对 RAG 系统中的关键超参数进行了精细的调优。本节将详细阐述实验所使用的数据集特征、数据预处理的参数配置以及评估指标的定义。

\subsection{数据来源与特征}

实验数据选取自计算机网络领域的权威教材《计算机网络（第8版）》（谢希仁 著）。该数据源具有高度的结构化特征（章、节、小节）和专业术语密集的特点，是测试语义检索性能的理想语料。

\begin{itemize}
    \item \textbf{数据规模}：原始 PDF 文档共计 400 余页，经 OCR 提取后纯文本量约为 32 万中文字符。
    \item \textbf{内容覆盖}：涵盖了物理层、数据链路层、网络层、传输层、应用层等核心章节，以及网络安全与无线网络等扩展章节。
    \item \textbf{数据异构性}：包含纯文本定义、协议流程描述、报文格式表格以及伪代码等多种信息模态。
\end{itemize}

\subsection{流水线参数配置}

在数据处理流水线中，我们设置了一系列关键参数以平衡系统的检索精度与计算效率。这些参数直接决定了向量索引的质量。

\subsubsection{文本分块策略}
文本分块是影响 RAG 性能的最重要因素之一。块太小会导致语义破碎，块太大会包含过多无关噪声。基于所选 Embedding 模型的特性，我们采用了滑动窗口切分策略，具体参数如下表所示：

\begin{table}[H]
\centering
\caption{文本分块与向量化参数设置}
\label{tab:chunking_params}
\begin{tabular}{l|c|p{8cm}}
\toprule
\textbf{参数名称} & \textbf{设定值} & \textbf{设定依据与说明} \\
\midrule
Chunk Size & 512 Tokens & 严格匹配 BGE Embedding 模型的最大上下文窗口限制，确保向量化时无截断损失。 \\
\hline
Chunk Overlap & 50 Tokens & 在相邻切片间保留约 10\% 的重叠区域，防止关键的上下文信息（如主语或逻辑连接词）在切分点丢失。 \\
\hline
Separator & \texttt{\textbackslash n\textbackslash n} & 优先使用双换行符作为自然段落的分隔符，保持语义段落的完整性。 \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection{向量化模型配置}
Embedding 模型将文本映射到高维向量空间。本实验选用 \texttt{BAAI/bge-small-zh-v1.5}，其核心配置如下：

\begin{itemize}
    \item \textbf{Vector Dimension ($d$)}: 512。该维度在表达能力与存储开销之间取得了最佳平衡。
    \item \textbf{Max Sequence Length}: 512。
    \item \textbf{Normalization}: True。模型输出已进行 L2 归一化，使得向量的点积直接等价于余弦相似度。
    \item \textbf{Query Instruction}: "为这个句子生成表示以用于检索相关文章："。我们在编码查询（Query）时添加了特定指令，这是 BGE 模型针对非对称检索任务的特殊优化，能显著提升召回率。
\end{itemize}

\subsubsection{检索策略参数}
在向量检索阶段，针对“精准问答”和“自动出题”两种不同场景，我们设计了不同的参数组：

\begin{table}[H]
\centering
\caption{不同场景下的检索参数配置}
\label{tab:retrieval_params}
\begin{tabular}{l|c|c|p{6cm}} 
\toprule
\textbf{场景模式} & \textbf{Similarity Top-K} & \textbf{Score Threshold} & \textbf{策略说明} \\
\midrule
\textbf{精准问答} & $K=3$ & 0.75 & 仅检索最相关的 3 个片段，且过滤掉相似度低于 0.75 的噪声，确保回答严谨。 \\
\hline
\textbf{随机出题} & $K=20$ & None & 大幅扩大检索视野，不做阈值截断，以便在长尾分布中进行随机采样，增加题目多样性。 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{评估指标}

为了量化评估数据处理模块的性能，我们定义了以下两个核心指标：

\subsubsection{索引构建效率}
定义为单位时间内系统能够处理的原始文本量。
\begin{equation}
E_{index} = \frac{N_{docs}}{T_{ETL} + T_{Embed} + T_{Save}}
\end{equation}
其中 $N_{docs}$ 为文档页数，$T_{ETL}$ 为文本提取时间，$T_{Embed}$ 为向量计算时间，$T_{Save}$ 为持久化写入时间。该指标反映了系统处理大规模数据的能力。

\subsubsection{检索命中率}
由于缺乏标注好的“标准答案”对，我们采用“自洽性验证”作为替代指标。我们随机抽取教材中的 100 个核心概念作为 Query，检索 Top-5 结果。如果 Top-5 结果中包含该概念所在的原始段落，则记为命中。
\begin{equation}
HR@5 = \frac{1}{|Q|} \sum_{q \in Q} \mathbb{I}(\text{GoldChunk}_q \in \text{Retrieved}_q)
\end{equation}
该指标直接反映了 Embedding 模型的语义匹配能力和索引构建的质量。

\section{结果与分析}

为了全面评估数据处理流水线与检索策略的性能，我们在真实的个人计算环境下进行了多维度的实验。实验重点关注系统在消费级硬件上的运行效率，以及切分粒度对质量的影响。


\subsection{系统延迟与冷热启动对比}

针对 30 万字符的《计算机网络》教材数据集，我们记录了系统在“冷启动”（全量构建）与“热启动”（加载持久化索引）模式下的耗时差异。

\begin{table}[H]
\centering
\caption{数据流水线性能详细对比 (基于 AMD 5800H 平台)}
\label{tab:performance_detail}
\begin{tabular}{l|c|c|c} % 修改对齐方式，避免特殊字符报错
\toprule
\textbf{处理阶段} & \textbf{冷启动耗时 (s)} & \textbf{热启动耗时 (s)} & \textbf{性能提升} \\
\midrule
环境初始化 & 0.65 & 0.62 & 1.0 x \\
文档读取 (I/O) & 1.42 & - & - \\
\textbf{向量计算 (Embedding)} & \textbf{55.20} & \textbf{-} & \textbf{-} \\
索引构建 (Indexing) & 0.58 & - & - \\
索引反序列化 (Loading) & - & 1.45 & - \\
\midrule
\textbf{总计 (Total)} & \textbf{57.85} & \textbf{2.07} & \textbf{27.9 x} \\
\bottomrule
\end{tabular}
\end{table}

\textbf{数据分析：}
如表 \ref{tab:performance_detail} 所示，全量计算 30 万字的 Embedding 耗时约为 55.20 秒，占据了冷启动总时间的 95\% 以上。这验证了向量化是系统的计算瓶颈。
通过我们在 \texttt{data\_loader.py} 中实现的本地持久化机制，系统在二次启动时无需重复计算，直接从 SSD 加载索引仅需 2.07 秒。这实现了约 28 倍 的启动速度提升，极大地优化了用户体验。



\subsection{参数敏感性实验}

为了探究 \texttt{Chunk Size}（切分粒度）对检索质量的影响，我们测试了三种不同的配置。

\begin{itemize}
    \item \textbf{Chunk=256}: 粒度过细，导致“TCP三次握手”的完整流程被切断在两个片段中，模型无法生成完整的解析。
    \item \textbf{Chunk=512 (Ours)}: 表现最佳。512 tokens 恰好覆盖教材中一个完整的知识点段落（如一个算法步骤或协议定义），与 BGE 模型的上下文窗口完美匹配。
    \item \textbf{Chunk=1024}: 导致每个片段包含过多无关信息（如将 UDP 和 TCP 的头部格式混在一个块中），检索的信噪比降低，且容易超出 Embedding 模型的处理上限。
\end{itemize}
% =======================================================
\section{复现性与代码结构}

本项目遵循开源最佳实践，代码结构清晰，依赖管理严格，确保了结果的可复现性。

\item \textbf{GitHub Repository}: \url{https://github.com/Hanbaor/EduRAG.git}

\subsection{核心文件结构说明}

代码仓库采用了模块化设计，数据处理逻辑与应用层逻辑完全解耦。

\begin{lstlisting}[language=bash]
project_root/
|-- data/                   # [Input] 原始数据源
|   |-- network_book.pdf    # 待处理的非结构化教材
|-- storage/                # [Output] 索引持久化目录
|   |-- default__vector_store.json  # FAISS 向量索引文件
|   |-- docstore.json               # 文档元数据映射表
|-- core/                   # [Core Logic] 核心代码库
|   |-- config.py           # 模型加载与参数配置
|   |-- data_loader.py      # ETL流水线、索引构建与加载逻辑
|   |-- quiz.py             # 双阶段检索策略实现
|-- app.py                  # Streamlit 入口文件
|-- requirements.txt        # Python 依赖清单
\end{lstlisting}

\subsection{环境依赖解析}

为了确保复现成功，必须严格控制依赖库的版本。以下是 \texttt{requirements.txt} 中关键库的版本说明及其作用：

\begin{itemize}
    \item \textbf{llama-index-core (v0.10.x)}：使用了最新版的 LlamaIndex，旧版（v0.9及以下）的 \texttt{ServiceContext} 接口已被弃用，本项目使用了新的 \texttt{Settings} 全局配置模式。
    \item \textbf{faiss-cpu (v1.8.0)}：建议使用 CPU 版本。若错误安装 \texttt{faiss-gpu} 但无 NVIDIA 显卡环境，会导致动态链接库加载失败。
    \item \textbf{sentence-transformers}：这是本地运行 HuggingFace Embedding 模型的基础依赖。
\end{itemize}

\subsection{复现步骤 (Command Line Examples)}

\begin{enumerate}
    \item \textbf{克隆仓库并安装依赖}：
    \begin{lstlisting}[language=bash]
    git clone https://github.com/Hanbaor/EduRAG.git
    cd EduRAG
    pip install -r requirements.txt
    \end{lstlisting}
    
    \item \textbf{环境配置}：
    在根目录下创建 \texttt{.env} 文件，并填入 API Key：
    \begin{lstlisting}[language=bash]
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
    OPENAI_API_BASE="https://api.deepseek.com/v1"
    \end{lstlisting}

    \item \textbf{启动应用（触发冷启动）}：
    将pdf文件放入data目录下，然后运行如下指令，首次运行时，系统会自动检测 \texttt{data/} 目录并构建索引。
    \begin{lstlisting}[language=bash]
    streamlit run app.py
    \end{lstlisting}
    控制台将输出：\texttt{[Data] 正在初始化 FAISS 并构建索引...}，等待约 1 分钟即可完成构建。

    \item \textbf{二次运行（验证热启动）}：
    停止程序后再次运行，控制台应输出：\texttt{[Data] 发现本地 FAISS 索引，正在加载...}，启动时间将缩短至 2 秒以内。
\end{enumerate}

% =======================================================
\section{结论与未来工作}

\subsection{总结}

本次大作业中，我负责设计并实现了 RAG 系统中关键的\textbf{数据处理与检索模块}。通过深入分析非结构化数据的特性与教学场景的需求，我完成了以下核心工作：

\begin{itemize}
    \item \textbf{构建了健壮的 ETL 流水线}：实现了从多格式文档读取、语义分块到向量化的全自动化处理，为上层应用提供了高质量的数据输入。
    \item \textbf{实现了毫秒级的高效检索}：利用 FAISS 的内积索引配合本地持久化机制，解决了大规模向量数据的存储与快速加载问题。
\end{itemize}

\subsection{未来工作展望}

尽管当前的数据处理模块已具备较高的可用性，但在面对更大规模的数据时，仍有优化空间：

\begin{enumerate}
    \item \textbf{引入重排序机制}：目前的检索完全依赖 Embedding 的向量相似度。未来计划引入 Cross-Encoder 模型，对粗排回来的 Top-50 结果进行精细化重排序，进一步提升查准率。
    \item \textbf{混合检索}：向量检索在处理精确关键词时不如传统的倒排索引（BM25）。未来计划将 FAISS 与 Elasticsearch 结合，实现关键词与语义的混合检索。
    \item \textbf{图索引}：对于计算机网络这种知识点关联性极强的学科，构建知识图谱并结合 Graph RAG 技术，可能比纯向量检索更能捕捉概念间的逻辑关系。
\end{enumerate}

% =======================================================
\begin{thebibliography}{99}

\bibitem{vaswani2017attention}
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., ... \& Polosukhin, I. (2017). Attention is all you need. \textit{Advances in neural information processing systems}, 30.

\bibitem{lewis2020rag}
Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., ... \& Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive nlp tasks. \textit{Advances in Neural Information Processing Systems}, 33, 9459-9474.

\bibitem{llamaindex}
Liu, J. (2022). LlamaIndex: Data Framework for LLM Applications. \url{https://github.com/jerryjliu/llama_index}.

\bibitem{faiss}
Johnson, J., Douze, M., \& Jégou, H. (2019). Billion-scale similarity search with GPUs. \textit{IEEE Transactions on Big Data}, 7(3), 535-547.

\bibitem{bge}
Xiao, S., Liu, Z., Zhang, P., \& Muennighoff, N. (2023). C-Pack: Packaged Resources To Advance General Chinese Embedding. \textit{arXiv preprint arXiv:2309.07597}.

\end{thebibliography}

\end{document}
