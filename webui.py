import streamlit as st
from main import app
import time

def generate_report(query: str, format: str, language: str) -> dict:
    """ 封装报告生成流程 """
    try:
        return app.invoke({
            "query": query,
            "report_format": format,  # 新增格式参数
            "language": language      # 新增语言参数
        })
    except Exception as e:
        st.error(f"报告生成失败: {str(e)}")
        return None

# 在网页布局前初始化session_state
if 'last_report' not in st.session_state:
    st.session_state.last_report = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# 网页布局
st.set_page_config(page_title="智能研究助手", layout="wide")
st.title("📑 智能研究助手")

# 侧边栏配置
with st.sidebar:
    st.header("配置选项")
    report_format = st.selectbox("输出格式", ["Markdown", "HTML"])
    language = st.selectbox("语言", ["中文", "English"])

# 主界面
query = st.text_input("请输入研究主题", placeholder="例如：人工智能在医疗中的应用", 
                     key="main_query", value=st.session_state.last_query)

# 当输入变化时清除旧结果
if query != st.session_state.last_query:
    st.session_state.last_report = None
    st.session_state.last_query = query

col1, col2 = st.columns([3, 1])

if col2.button("开始研究", use_container_width=True):
    with st.status("研究进行中..."):
        st.write("1. 正在初始化研究项目...")
        start_time = time.time()
        
        st.write("2. 生成研究大纲...")
        result = generate_report(query, report_format, language)  # 传递新参数
        
        if result:
            st.success(f"研究完成！耗时 {time.time()-start_time:.1f}秒")
            
            # 兼容报告字段获取
            report_content = result.get("published_report", result.get("final_draft", "无内容"))
            
            # 显示报告预览
            st.session_state.last_report = {
                "content": result.get("published_report", result.get("final_draft", "无内容")),
                "format": report_format
            }

# 显示结果（从session_state获取）
if st.session_state.last_report:
    report_content = st.session_state.last_report["content"]
    current_format = st.session_state.last_report["format"]
    
    with col1:
        st.subheader("研究报告预览")
        if current_format == "Markdown":
            st.markdown(report_content)
        else:
            st.html(report_content)
        
        # 下载按钮（保持可见）
        st.download_button(
            label="下载报告",
            data=report_content,
            file_name=f"研究报告_{query[:20]}.{current_format.lower()}",
            mime="text/markdown" if current_format=="Markdown" else "text/html"
        )

# 添加自定义CSS样式
st.markdown("""
<style>
/* 主容器样式 */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 标题样式 */
header h1 {
    color: #2e86c1;
    font-size: 2.5em;
    text-align: center;
    margin-bottom: 30px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

/* 侧边栏样式 */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.9) !important;
    box-shadow: 5px 0 15px rgba(0,0,0,0.1);
}

/* 输入框样式 */
.stTextInput input {
    border-radius: 25px !important;
    padding: 15px 20px !important;
    border: 2px solid #2e86c1 !important;
}

/* 按钮样式 */
.stButton button {
    background: #2e86c1 !important;
    border-radius: 25px !important;
    padding: 12px 30px !important;
    font-weight: bold;
    transition: all 0.3s ease !important;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(46,134,193,0.4);
}

/* 状态提示样式 */
[data-testid="stStatus"] {
    border-left: 5px solid #148f77 !important;
    background: rgba(255,255,255,0.9) !important;
}

/* 报告预览区域 */
.stMarkdown, .stHtml {
    background: white;
    border-radius: 15px;
    padding: 25px !important;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    margin-top: 20px;
}

/* 下载按钮 */
.stDownloadButton button {
    background: #28a745 !important;
    margin-top: 20px;
}

/* 配置选项样式 */
.stSelectbox div[role="listbox"] {
    border-radius: 15px !important;
    padding: 10px !important;
}
</style>
""", unsafe_allow_html=True)