# Researcher_Agent!

## 1.基础

### 1.创建虚拟环境

* 在终端输入：

```
python -m venv venv
```

### 2.激活虚拟环境：

- Windows：

  ```
  venv\Scripts\activate
  ```

- Mac/Linux：

  ```
  source venv/bin/activate
  ```

看到命令行前面出现 `(venv)` 就对了。

### 3.安装依赖

```bash
pip install langgraph langchain-openai tavily-python python-dotenv
```

`python-dotenv` 用来读取 `.env` 文件里的密钥。

### 4. 新建 `.env` 文件

在项目根目录下新建 `.env` 文件，写入：

```
OPENAI_API_KEY=你的OpenAI的key
TAVILY_API_KEY=你的Tavily的key
```

（如果你还没注册 Tavily，我可以教你用它的免费 key，或者我们先用固定字符串假装有搜索结果。）

### 5. 新建 `main.py`

在项目根目录新建 `main.py`，把我之前给你的代码粘贴进去。
 不过要稍微改一下，加上 dotenv 支持：

```python
# 导入操作系统相关的模块，用于处理文件路径、环境变量等系统相关操作
import os

# 从dotenv库导入load_dotenv函数，用于从.env文件中加载环境变量
from dotenv import load_dotenv

# 从langgraph.graph导入StateGraph类和END常量，用于构建状态图工作流
from langgraph.graph import StateGraph, END

# 从langchain_openai导入ChatOpenAI类，用于调用OpenAI的聊天模型API
from langchain_openai import ChatOpenAI

# 从tavily库导入TavilyClient类，用于调用Tavily搜索引擎的API
from tavily import TavilyClient

# 调用load_dotenv()函数，它会自动查找并加载.env文件中的环境变量
load_dotenv()

# 定义一个研究状态类，继承自dict类
class ResearcherState(dict):
    """
    这是一个类型化的字典类，用于存储研究过程中的状态数据
    """
    query: str           # 存储搜索查询字符串
    search_results: list # 存储搜索结果的列表
    report: str         # 存储生成的报告内容

# 创建TavilyClient实例，用于执行网络搜索
# 从环境变量中获取TAVILY_API_KEY
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 定义搜索节点函数，用于执行网络搜索
def serach_node(state: ResearcherState) -> ResearcherState:
    """
    这个函数接收当前状态，执行搜索，然后更新状态
    """
    # 从状态字典中获取查询字符串
    query = state["query"]
    
    # 使用Tavily客户端执行搜索，最多返回3个结果
    results = tavily.search(query, max_results=3)
    
    # 调试输出：打印Tavily返回的完整结果
    print(">>> Tavily 返回结果:", results)
    
    # 从搜索结果中提取results部分，存入状态字典
    state["search_results"] = results["results"]
    
    # 返回更新后的状态
    return state

# 创建ChatOpenAI实例，用于调用OpenAI的语言模型
# 使用gpt-4o-mini模型，从环境变量获取API密钥
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# 定义总结节点函数，用于生成研究报告
def summarize_node(state: ResearcherState) -> ResearcherState:
    """
    这个函数接收搜索结果，使用LLM生成报告，然后更新状态
    """
    # 打印调试信息
    print(">>> Summarize Node 正在运行...")
    
    # 将所有搜索结果的内容合并成一个字符串，每个结果用换行符分隔
    docs = "\n".join([r["content"] for r in state["search_results"]])
    
    # 构建提示词，要求LLM根据搜索结果生成报告
    prompt = f"请根据以下搜索结果写一份简短研究报告，并保留引用：\n\n{docs}"
    
    # 调用语言模型，传入提示词获取响应
    response = llm.invoke(prompt)
    
    # 调试输出：打印LLM返回的完整响应
    print(">>> LLM 返回:", response)
    
    # 从响应中提取内容部分，存入状态字典
    state["report"] = response.content
    
    # 返回更新后的状态
    return state

# 创建一个新的状态图实例，使用ResearcherState作为状态类型
graph = StateGraph(ResearcherState)

# 向图中添加节点
graph.add_node("search", serach_node)      # 添加搜索节点，关联到serach_node函数
graph.add_node("summarize", summarize_node) # 添加总结节点，关联到summarize_node函数

# 设置图的入口点为"search"节点
graph.set_entry_point("search")

# 添加节点之间的边（连接）
graph.add_edge("search", "summarize")  # 从search节点到summarize节点
graph.add_edge("summarize", END)       # 从summarize节点到结束状态

# 编译图，生成可执行的应用程序
app = graph.compile()

# 主程序入口点
if __name__ == "__main__":
    # 提示用户输入研究主题
    query = input("请输入研究主题：")
    
    # 调用应用程序，传入初始状态（包含查询）
    result = app.invoke({"query": query})
    
    # 注意：这里可以添加代码来输出或处理结果
    # 例如：print(result["report"]) 可以打印生成的报告

```

------

### 6. 运行测试

在 VS Code 的终端里输入：

```
python main.py
```

输入一个问题，例如：

```
人工智能在医疗上的最新应用
```

如果一切顺利，你会得到一份搜索结果整合后的简短报告。



 ##  更换API接口

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="doubao-seed-1-6-flash-250828",
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url="https://api.doubao.com/v1",  # 替换为豆包的 API 地址
)
```

## 2.最终版本

```python
import os
import time
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
import markdown

load_dotenv()

# ========== 初始化 LLM & Tavily ==========
llm = ChatOpenAI(
    model="doubao-seed-1-6-flash-250828",
    api_key=os.getenv("DOUBAO_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# ========== 定义状态 ==========
class ResearchTeamState(dict):
    query: str
    outline: str
    sub_questions: list
    research_results: dict
    reviews: dict
    revisions: dict
    report_format: str
    citation_style: str
    language: str
    final_report: str
    published_report: str

# ========== 智能体节点定义 ==========
def chief_editor_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Chief Editor: 初始化项目")
    state.setdefault("research_results", {})
    state.setdefault("reviews", {})
    state.setdefault("revisions", {})
    state.setdefault("final_report", "")
    state.setdefault("published_report", "")
    state["project_started_at"] = time.strftime("%Y%m%d-%H%M%S")
    state.setdefault("report_format", "markdown")
    state.setdefault("citation_style", "APA")
    state.setdefault("language", "中文")
    return state

def editor_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Editor: 生成研究大纲和子问题...")
    query = state["query"]
    prompt = f"""
你是研究项目的编辑。请根据主题生成研究大纲和子问题。

主题：{query}

要求：
1. 输出一个结构化研究大纲（引言、几个主要部分、结论）。
2. 给出 3-5 个子问题，用于后续研究。
3. 使用 {state.get("language","中文")}。
"""
    response = llm.invoke(prompt)
    content = response.content
    lines = content.split("\n")
    sub_questions = [line.strip("-• ") for line in lines if "?" in line or "？" in line]
    state["outline"] = content
    state["sub_questions"] = sub_questions
    print(">>> 子问题:", sub_questions)
    return state

def researcher_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Researcher: 针对子问题研究...")
    results = {}
    for q in state.get("sub_questions", []):
        print(f"\n--- 正在研究: {q} ---")
        tavily_results = tavily.search(q, max_results=3)
        docs = "\n".join([r["content"] for r in tavily_results["results"]])
        prompt = f"""
请根据以下搜索结果写一段研究摘要，并保留引用：

子问题：{q}
搜索结果：
{docs}
"""
        resp = llm.invoke(prompt)
        results[q] = resp.content
    state["research_results"] = results
    return state

def reviewer_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Reviewer: 审查研究结果...")
    reviews = {}
    for q, answer in state.get("research_results", {}).items():
        prompt = f"""
你是评审员，请检查以下研究结果：
- 内容是否准确
- 是否完整
- 逻辑是否清晰
- 引用是否合理

子问题：
{q}

研究结果：
{answer}
"""
        resp = llm.invoke(prompt)
        reviews[q] = resp.content
    state["reviews"] = reviews
    return state

def revisor_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Revisor: 根据评审意见修改结果...")
    revisions = {}
    for q, answer in state.get("research_results", {}).items():
        review = state["reviews"].get(q,"")
        prompt = f"""
请根据评审意见修改研究结果，使其逻辑更严谨、内容更完整：

子问题：
{q}

原始研究结果：
{answer}

评审意见：
{review}
"""
        resp = llm.invoke(prompt)
        revisions[q] = resp.content
    state["revisions"] = revisions
    return state

def writer_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Writer: 生成完整报告...")
    final_report = f"# 研究主题: {state['query']}\n\n"
    final_report += f"## 大纲\n{state.get('outline','')}\n\n"
    final_report += "## 研究内容\n"
    for q, ans in state.get("revisions", {}).items():
        final_report += f"\n### {q}\n{ans}\n"
    state["final_report"] = final_report
    return state

def publisher_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Publisher: 输出最终报告...")
    fmt = state.get("report_format","markdown").lower()
    content = state.get("final_report","")
    if fmt == "html":
        state["published_report"] = markdown.markdown(content)
    else:
        state["published_report"] = content
    return state

# ========== LangGraph 构建 ==========
graph = StateGraph(ResearchTeamState)

graph.add_node("chief_editor", chief_editor_node)
graph.add_node("editor", editor_node)
graph.add_node("researcher", researcher_node)
graph.add_node("reviewer", reviewer_node)
graph.add_node("revisor", revisor_node)
graph.add_node("writer", writer_node)
graph.add_node("publisher", publisher_node)

graph.set_entry_point("chief_editor")
graph.add_edge("chief_editor","editor")
graph.add_edge("editor","researcher")
graph.add_edge("researcher","reviewer")
graph.add_edge("reviewer","revisor")
graph.add_edge("revisor","writer")
graph.add_edge("writer","publisher")
graph.add_edge("publisher",END)

app = graph.compile()

# ========== 运行示例 ==========
if __name__ == "__main__":
    query = input("请输入研究主题：")
    result = app.invoke({"query": query})
    print("\n--- 最终发布报告 ---\n")
    print(result["published_report"])

```

## 3.前端页面

```python
import streamlit as st
from main import app
import time

def generate_report(query: str) -> dict:
    """ 封装报告生成流程 """
    try:
        return app.invoke({"query": query})
    except Exception as e:
        st.error(f"报告生成失败: {str(e)}")
        return None

# 网页布局
st.set_page_config(page_title="智能研究助手", layout="wide")
st.title("📑 智能研究助手")

# 侧边栏配置
with st.sidebar:
    st.header("配置选项")
    report_format = st.selectbox("输出格式", ["Markdown", "HTML"])
    language = st.selectbox("语言", ["中文", "English"])

# 主界面
query = st.text_input("请输入研究主题", placeholder="例如：人工智能在医疗中的应用")
col1, col2 = st.columns([3, 1])

if col2.button("开始研究", use_container_width=True):
    with st.status("研究进行中..."):
        st.write("1. 正在初始化研究项目...")
        start_time = time.time()
        
        st.write("2. 生成研究大纲...")
        result = generate_report(query)
        
        if result:
            st.success(f"研究完成！耗时 {time.time()-start_time:.1f}秒")
            
            # 显示报告预览
            with col1:
                st.subheader("研究报告预览")
                if report_format == "Markdown":
                    st.markdown(result["published_report"])
                else:
                    st.html(result["published_report"])
                
                # 下载按钮
                st.download_button(
                    label="下载报告",
                    data=result["published_report"],
                    file_name=f"研究报告_{query[:20]}.{report_format.lower()}",
                    mime="text/markdown" if report_format=="Markdown" else "text/html"
                )
```

需要安装依赖：

```bash
pip install streamlit
```

运行方式：

```bash
streamlit run c:\Users\i\Desktop\researcher_agent\webui.py
```
