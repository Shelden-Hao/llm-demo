"""
01_基于Streamlit完成WEB网页上传服务

pip install streamlit

Streamlit：当WEB页面元素发生变化，则代码重新执行一遍
"""
import time
import streamlit as st
from knowledge_base import KnowledgeBaseService

# 添加网页标题
st.title("知识库更新服务")

# file_uploader
uploader_file = st.file_uploader(
    "请上传TXT文件",
    type=['txt'],
    accept_multiple_files=False,  # False表示仅接受一个文件的上传
)

# session_state就是一个字典，用来保存会话状态，避免每次上传文件或者页面刷新时，页面所有状态重置
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()  # 单例模式

"""04_将上传服务和数据库更新服务连接起来"""

if uploader_file is not None:
    # 提取文件的信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024  # KB

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} KB")

    # 获取文件内容 getvalue -> bytes -> decode('utf-8')
    text = uploader_file.getvalue().decode("utf-8")

    # Python 中的 with 语句用于简化资源管理（上下文管理器）。
    # 在这里，st.spinner 是一个上下文管理器：
    # 1. 进入 with 块时：自动显示加载动画（spinner）。
    # 2. 执行块内代码：上传文件到知识库。
    # 3. 退出 with 块时（无论是否发生异常）：自动隐藏加载动画。
    # 这确保了用户体验的一致性，避免手动控制动画的显示和隐藏。
    with st.spinner("载入知识库中。。。"):
        time.sleep(1)  # 模拟耗时操作，实际项目中可移除
        result = st.session_state["service"].upload_by_str(text, file_name)

    # 将结果展示放在 spinner 之外，确保动画结束后再显示结果，体验更好
    st.success("上传成功！")
    st.write(result)
