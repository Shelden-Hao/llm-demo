"""
02_知识库
"""
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime


def check_md5(md5_str: str):
    """检查传入的md5字符串是否已经被处理过了
        return False(md5未处理过)  True(已经处理过，已有记录）
    """
    if not os.path.exists(config.md5_path):
        # if进入表示文件不存在，那肯定没有处理过这个md5了
        # 打开文件并关闭（创建文件）
        open(config.md5_path, 'w', encoding='utf-8').close()
        return False
    else:
        for line in open(config.md5_path, 'r', encoding='utf-8').readlines():
            line = line.strip()  # 处理字符串前后的空格和回车
            if line == md5_str:
                return True  # 已处理过

        return False


def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存"""
    # with 执行 open() 的 __enter__() 方法 → 打开文件
    # 将文件对象赋值给变量 f
    # 执行代码块 → 写入数据
    # 代码块结束后，自动执行 __exit__() 方法 → 关闭文件
    with open(config.md5_path, 'a', encoding="utf-8") as f:
        f.write(md5_str + '\n')


def get_string_md5(input_str: str, encoding='utf-8'):
    """将传入的字符串转换为md5字符串"""

    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding=encoding)

    # 创建md5对象
    md5_obj = hashlib.md5()  # 得到md5对象
    md5_obj.update(str_bytes)  # 更新内容（传入即将要转换的字节数组）
    md5_hex = md5_obj.hexdigest()  # 得到md5的十六进制字符串

    return md5_hex


# Python 2：
# 必须显式继承 object 才能成为"新式类"（new-style class）
# 不继承 object 的是"旧式类"（old-style class），功能受限
# Python 3：
# 所有类都自动继承 object，无论是否显式写出
# class KnowledgeBaseService(object): 和 class KnowledgeBaseService: 完全等价
class KnowledgeBaseService(object):  # 继承 object 的
    """
    03_知识库更新服务
    """

    def __init__(self):
        # 如果文件夹不存在则创建，如果存在则跳过
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,  # 数据库的表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,  # 数据库本地存储文件夹
        )  # 向量存储的实例 Chroma向量库对象

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  # 分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,  # 连续文本段之间的字符重叠数量
            separators=config.separators,  # 自然段落划分的符号
            length_function=len,  # 使用Python自带的len函数做长度统计的依据
        )  # 文本分割器的对象

    def upload_by_str(self, data: str, filename):
        """将传入的字符串，进行向量化，存入向量数据库中"""
        # 先得到传入字符串的md5值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"

        if len(data) > config.min_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:  # 如果太短的字符将不被分割
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            # 2025-01-01 10:00:00
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "heo",
        }

        self.chroma.add_texts(  # 将文本转为向量，存入向量数据库中
            # iterable -> list \ tuple
            knowledge_chunks, # 分割后的文本片段
            metadatas=[metadata for _ in knowledge_chunks],  # 为 knowledge_chunks 中的每个片段复制一份元数据 metadata
        )

        #
        save_md5(md5_hex)

        return "[成功]内容已经成功载入向量库"


if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("heooo", "testfile")
    print(r)
