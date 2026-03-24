#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Zoe-Doctor - 系统健康检查工具

检测项目:
- 内核 Socket 连通性
- 环境变量配置
- Python 依赖完整性
- Zig 构建环境
"""

import os
import sys
import socket
import shutil
import subprocess
from pathlib import Path

SOCKET_PATH = "/tmp/zoe.sock"

# ============ 检查项 ============

def check_kernel_socket() -> tuple[bool, str]:
    """检查内核 Socket 是否可达"""
    if not Path(SOCKET_PATH).exists():
        return False, f"Socket 文件不存在: {SOCKET_PATH}"
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(SOCKET_PATH)
        sock.close()
        return True, f"内核 Socket 正常: {SOCKET_PATH}"
    except OSError as e:
        return False, f"无法连接内核 Socket: {e}"


def check_env_vars() -> tuple[bool, str]:
    """检查必要的环境变量"""
    missing = []
    if not os.environ.get("ZOE_API_KEY"):
        missing.append("ZOE_API_KEY")
    if missing:
        return False, f"缺少环境变量: {', '.join(missing)}"
    return True, "环境变量配置完整"


def check_python_deps() -> tuple[bool, str]:
    """检查 Python 依赖"""
    required = ["requests"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        return False, f"缺少 Python 包: {', '.join(missing)}"
    return True, "Python 依赖完整"


def check_zig_env() -> tuple[bool, str]:
    """检查 Zig 构建环境"""
    zig = shutil.which("zig")
    if not zig:
        return False, "未找到 zig 命令，请安装 Zig: https://ziglang.org/download/"
    try:
        result = subprocess.run(
            ["zig", "version"], capture_output=True, text=True, timeout=5
        )
        version = result.stdout.strip()
        return True, f"Zig 已安装: {version}"
    except Exception as e:
        return False, f"Zig 检查失败: {e}"


def check_build_artifacts() -> tuple[bool, str]:
    """检查 build.zig 是否存在"""
    repo_root = Path(__file__).parent.parent
    build_zig = repo_root / "build.zig"
    if not build_zig.exists():
        return False, "未找到 build.zig"
    return True, "build.zig 存在"


# ============ 主函数 ============

CHECKS = [
    ("🔌 内核 Socket", check_kernel_socket),
    ("🔑 环境变量", check_env_vars),
    ("🐍 Python 依赖", check_python_deps),
    ("⚡ Zig 环境", check_zig_env),
    ("📦 构建文件", check_build_artifacts),
]


def main():
    print("\n🐝 Zoe-Doctor — 系统健康检查\n" + "=" * 40)
    all_ok = True
    for name, fn in CHECKS:
        ok, msg = fn()
        status = "✅" if ok else "❌"
        print(f"  {status}  {name}: {msg}")
        if not ok:
            all_ok = False

    print("=" * 40)
    if all_ok:
        print("🟢 所有检查通过，系统健康。\n")
    else:
        print("🔴 部分检查未通过，请根据上述提示修复。\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
