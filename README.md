# Researcher Agent - 智能研究助手

一个基于 LangGraph 构建的自动化研究助手系统，通过多智能体协作完成从主题研究到报告生成的全流程。

## 项目简介

Researcher Agent 是一个智能化的研究工具，能够根据用户输入的研究主题，自动执行以下任务：

- 生成结构化研究大纲
- 分解关键子问题
- 并行搜索和收集资料
- 审查和修订研究结果
- 生成完整的研究报告
- 支持多种输出格式

## 核心特性

### 智能体协作系统
系统采用多智能体架构，每个智能体负责特定任务：

- **Chief Editor（总编辑）**：初始化项目，设置研究参数
- **Editor（编辑）**：生成研究大纲和关键子问题
- **Researcher（研究员）**：并行搜索和收集研究资料
- **Reviewer（评审员）**：审查研究结果的准确性和完整性
- **Revisor（修订员）**：根据评审意见修订研究结果
- **Writer（撰稿人）**：整合所有内容生成完整报告
- **Publisher（发布员）**：格式化并输出最终报告

### 技术优势

- **并行处理**：使用线程池并行执行搜索、审查和修订任务，大幅提升效率
- **灵活配置**：支持自定义报告格式（Markdown/HTML）、引用风格（APA等）和语言
- **实时反馈**：每个步骤都有清晰的进度提示
- **可扩展性**：基于 LangGraph 的状态机架构，易于添加新的智能体节点

## 系统架构

```
用户输入研究主题
        ↓
    Chief Editor (初始化)
        ↓
    Editor (生成大纲和子问题)
        ↓
    Researcher (并行研究)
        ↓
    Reviewer (并行审查)
        ↓
    Revisor (并行修订)
        ↓
    Writer (生成报告)
        ↓
    Publisher (格式化输出)
        ↓
    最终研究报告
```

## 安装步骤

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install langgraph langchain-openai tavily-python python-dotenv markdown
```

### 4. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
DOUBAO_API_KEY=你的豆包API密钥
TAVILY_API_KEY=你的Tavily搜索API密钥
```

**获取 API 密钥：**
- 豆包 API：访问 [火山引擎](https://www.volcengine.com/) 注册获取
- Tavily API：访问 [Tavily](https://tavily.com/) 注册获取免费额度

## 使用方法

### 命令行模式

```bash
python main.py
```

输入研究主题，例如：
```
人工智能在医疗领域的最新应用
```

系统将自动执行完整的研究流程并输出报告。

### Web 界面模式

安装 Streamlit：
```bash
pip install streamlit
```

运行 Web 界面：
```bash
streamlit run webui.py
```

在浏览器中打开显示的地址，通过图形界面使用研究助手。

## 配置选项

### 研究参数

可以在代码中修改以下默认参数：

```python
state.setdefault("report_format", "markdown")  # 报告格式：markdown/html
state.setdefault("citation_style", "APA")       # 引用风格
state.setdefault("language", "中文")            # 输出语言
```

### LLM 配置

当前使用豆包模型，如需更换其他模型：

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",  # 替换为其他模型
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1",
)
```

## 技术栈

- **LangGraph**：构建多智能体工作流
- **LangChain**：LLM 调用和管理
- **Tavily**：网络搜索和数据收集
- **Python-dotenv**：环境变量管理
- **Markdown**：文档格式转换
- **Streamlit**：Web 界面（可选）

## 项目结构

```
researcher_agent/
├── main.py              # 核心程序入口
├── webui.py             # Web 界面（可选）
├── .env                 # 环境变量配置
├── README.md            # 项目说明文档
└── venv/                # 虚拟环境
```

## 工作流程示例

1. **用户输入**："量子计算在密码学中的应用"
2. **Editor 生成大纲**：
   - 引言
   - 量子计算基础
   - 传统密码学面临的挑战
   - 量子密码学解决方案
   - 未来发展趋势
3. **Researcher 并行研究**：
   - 量子计算的基本原理是什么？
   - 传统加密算法为何会被量子计算破解？
   - 量子密钥分发如何实现安全通信？
4. **Reviewer 审查**：检查每个子问题的研究质量
5. **Revisor 修订**：根据审查意见优化内容
6. **Writer 整合**：生成完整的研究报告
7. **Publisher 输出**：格式化为 Markdown 或 HTML

## 注意事项

- 确保网络连接正常，Tavily 搜索需要访问互联网
- API 密钥需要足够的额度，建议使用付费账户以获得更好的搜索结果
- 首次运行可能需要较长时间下载依赖包
- 并行处理会同时发起多个 API 请求，请注意 API 速率限制

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。
