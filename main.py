import os
import time
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
import markdown
from concurrent.futures import ThreadPoolExecutor

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
2. 给出 3 个关键子问题（不要超过 3 个）。
3. 使用 {state.get("language","中文")}。
"""
    response = llm.invoke(prompt)
    content = response.content
    lines = content.split("\n")
    sub_questions = [line.strip("-• ") for line in lines if "?" in line or "？" in line][:3]
    state["outline"] = content
    state["sub_questions"] = sub_questions
    print(">>> 子问题:", sub_questions)
    return state

def researcher_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Researcher: 并行研究子问题...")

    def research_one(q):
        tavily_results = tavily.search(q, max_results=2)  # 减少搜索数量加速
        docs = "\n".join([r["content"] for r in tavily_results["results"]])
        prompt = f"""
请根据以下搜索结果写一段研究摘要，并保留引用：

子问题：{q}
搜索结果：
{docs}
"""
        resp = llm.invoke(prompt)
        return q, resp.content

    results = {}
    with ThreadPoolExecutor() as executor:
        for q, ans in executor.map(research_one, state.get("sub_questions", [])):
            results[q] = ans

    state["research_results"] = results
    return state

def reviewer_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Reviewer: 并行审查研究结果...")

    def review_one(item):
        q, answer = item
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
        return q, resp.content

    reviews = {}
    with ThreadPoolExecutor() as executor:
        for q, review in executor.map(review_one, state["research_results"].items()):
            reviews[q] = review

    state["reviews"] = reviews
    return state

def revisor_node(state: ResearchTeamState) -> ResearchTeamState:
    print(">>> Revisor: 并行修订研究结果...")

    def revise_one(item):
        q, answer = item
        review = state["reviews"].get(q, "")
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
        return q, resp.content

    revisions = {}
    with ThreadPoolExecutor() as executor:
        for q, revision in executor.map(revise_one, state["research_results"].items()):
            revisions[q] = revision

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
