"""
文件处理工具模块
支持压缩包解压和文件夹处理
"""

import os
import zipfile
import tarfile
import rarfile
from pathlib import Path
from typing import List, Tuple
from app.utils.log_util import logger


def is_archive_file(filename: str) -> bool:
    """
    判断文件是否为压缩包

    Args:
        filename: 文件名

    Returns:
        bool: 是否为压缩包
    """
    archive_extensions = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}
    file_ext = Path(filename).suffix.lower()

    # 处理 .tar.gz 等双扩展名
    if file_ext in {".gz", ".bz2", ".xz"}:
        stem = Path(filename).stem
        if stem.endswith(".tar"):
            return True

    return file_ext in archive_extensions


def extract_archive(archive_path: str, extract_to: str) -> Tuple[bool, str, List[str]]:
    """
    解压压缩包到指定目录

    Args:
        archive_path: 压缩包路径
        extract_to: 解压目标目录

    Returns:
        Tuple[bool, str, List[str]]: (是否成功, 错误信息, 解压的文件列表)
    """
    extracted_files = []

    try:
        archive_path = Path(archive_path)
        extract_to = Path(extract_to)

        # 确保目标目录存在
        extract_to.mkdir(parents=True, exist_ok=True)

        file_ext = archive_path.suffix.lower()

        # 处理 ZIP 文件
        if file_ext == ".zip":
            logger.info(f"开始解压 ZIP 文件: {archive_path}")
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                # 获取所有文件列表
                file_list = zip_ref.namelist()
                logger.info(f"ZIP 文件包含 {len(file_list)} 个文件")

                # 解压所有文件
                extracted_files = []
                for member in file_list:
                    zip_ref.extract(member, extract_to)
                    extracted_files.append(member)

                logger.info(f"成功解压 {len(extracted_files)} 个文件")

        # 处理 RAR 文件
        elif file_ext == ".rar":
            logger.info(f"开始解压 RAR 文件: {archive_path}")
            try:
                with rarfile.RarFile(archive_path, "r") as rar_ref:
                    file_list = rar_ref.namelist()
                    logger.info(f"RAR 文件包含 {len(file_list)} 个文件")

                    extracted_files = []
                    for member in file_list:
                        rar_ref.extract(member, extract_to)
                        extracted_files.append(member)

                    logger.info(f"成功解压 {len(extracted_files)} 个文件")
            except rarfile.NeedFirstVolume:
                return False, "需要RAR压缩包的第一卷", []
            except rarfile.Error as e:
                return False, f"RAR解压失败: {str(e)}", []

        # 处理 TAR 文件（包括 .tar.gz, .tar.bz2 等）
        elif file_ext in {".tar", ".gz", ".bz2", ".xz"} or archive_path.name.endswith(
            (".tar.gz", ".tar.bz2", ".tar.xz")
        ):
            logger.info(f"开始解压 TAR 文件: {archive_path}")

            # 自动检测压缩类型
            mode = "r:*"  # 自动检测

            with tarfile.open(archive_path, mode) as tar_ref:
                file_list = tar_ref.getnames()
                logger.info(f"TAR 文件包含 {len(file_list)} 个文件")

                # 安全解压（防止路径遍历攻击）
                def is_safe_path(path, base_path):
                    """检查解压路径是否安全"""
                    return os.path.realpath(os.path.join(base_path, path)).startswith(
                        base_path
                    )

                for member in tar_ref.getmembers():
                    if is_safe_path(member.name, str(extract_to)):
                        tar_ref.extract(member, extract_to)
                        extracted_files.append(member.name)

                logger.info(f"成功解压 {len(extracted_files)} 个文件")

        # 处理 7Z 文件（需要额外的库）
        elif file_ext == ".7z":
            try:
                import py7zr

                logger.info(f"开始解压 7Z 文件: {archive_path}")

                with py7zr.SevenZipFile(archive_path, mode="r") as z:
                    file_list = z.getnames()
                    logger.info(f"7Z 文件包含 {len(file_list)} 个文件")

                    extracted_files = []
                    for name in file_list:
                        z.extract(targets=[name], path=extract_to)
                        extracted_files.append(name)

                    logger.info(f"成功解压 {len(extracted_files)} 个文件")
            except ImportError:
                return False, "不支持 7Z 格式（需要安装 py7zr 库）", []
            except Exception as e:
                return False, f"7Z解压失败: {str(e)}", []

        else:
            return False, f"不支持的压缩格式: {file_ext}", []

        # 删除原始压缩包（可选）
        # archive_path.unlink()

        return True, "", extracted_files

    except zipfile.BadZipFile:
        error_msg = f"损坏的ZIP文件: {archive_path}"
        logger.error(error_msg)
        return False, error_msg, []

    except tarfile.TarError as e:
        error_msg = f"TAR文件处理错误: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, []

    except Exception as e:
        error_msg = f"解压失败: {str(e)}"
        logger.error(error_msg)
        return False, error_msg, []


def save_uploaded_file(file_content: bytes, save_path: str) -> bool:
    """
    保存上传的文件

    Args:
        file_content: 文件内容
        save_path: 保存路径

    Returns:
        bool: 是否保存成功
    """
    try:
        save_path = Path(save_path)

        # 确保父目录存在
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(save_path, "wb") as f:
            f.write(file_content)

        logger.info(f"成功保存文件: {save_path}")
        return True

    except Exception as e:
        logger.error(f"保存文件失败 {save_path}: {str(e)}")
        return False


def get_file_tree(directory: str, max_depth: int = 3) -> dict:
    """
    获取目录树结构

    Args:
        directory: 目录路径
        max_depth: 最大深度

    Returns:
        dict: 目录树结构
    """

    def build_tree(path: Path, current_depth: int = 0):
        if current_depth > max_depth:
            return None

        tree = {
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "path": str(path),
        }

        if path.is_dir():
            children = []
            try:
                for child in sorted(path.iterdir()):
                    child_tree = build_tree(child, current_depth + 1)
                    if child_tree:
                        children.append(child_tree)
                tree["children"] = children
            except PermissionError:
                pass

        return tree

    return build_tree(Path(directory))


def count_files_in_directory(directory: str) -> int:
    """
    统计目录中的文件数量（递归）

    Args:
        directory: 目录路径

    Returns:
        int: 文件数量
    """
    try:
        path = Path(directory)
        if not path.exists():
            return 0

        if path.is_file():
            return 1

        count = 0
        for item in path.rglob("*"):
            if item.is_file():
                count += 1

        return count
    except Exception as e:
        logger.error(f"统计文件数量失败: {str(e)}")
        return 0
