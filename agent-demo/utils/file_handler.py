"""
02_文件处理
"""
import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_md5_hex(filepath: str):  # 获取文件的md5的十六进制字符串，用于去重

    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 4KB分片，避免文件过大爆内存
    try:
        with open(filepath, "rb") as f:  # 必须二进制读取
            """
            open() 返回的文件对象内部维护一个文件指针(file pointer / cursor),记录当前读到哪里了:
            文件内容: [====已读====][==未读==]
                                  ↑
                                指针位置
            - 每次 f.read(n):从指针位置读 n 字节,指针自动后移 n 个字节
            - 文件指针是文件对象的内部状态,存在 f 里面
            - 再次调用 f.read(n) 时,f 知道自己上次停在哪,直接从那里继续
            """
            # 把文件按 4KB 一块流式喂给 hashlib.md5() 对象,逐块更新哈希状态,直到读完整个文件
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            """
            等价于：
            chunk = f.read(chunk_size)
            while chunk:
                md5_obj.update(chunk)
                chunk = f.read(chunk_size)
            """
            # 得到 32 位的十六进制 MD5 值
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):  # 返回文件夹内的文件列表（允许的文件后缀）
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):
        if f.endswith(allowed_types): # 允许的文件后缀
            files.append(os.path.join(path, f))

    return tuple(files) # 允许得到的文件路径列表


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    return PyPDFLoader(filepath, passwd).load()


def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()
