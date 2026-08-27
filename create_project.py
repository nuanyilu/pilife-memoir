import os

# 项目根目录（脚本所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 需要创建的目录列表（相对于 BASE_DIR/backend）
SUBDIRS = [
    "api",
    "wallet",
    "chat",
    "community",
    "diary",
    "emotion",
    "fortune",
    "drift_bottle",
    "memory",
    "db",
    "utils",
]

# 需要创建的 __init__.py 文件（每个子目录一个，再加上 backend 根目录）
INIT_FILES = ["backend/__init__.py"] + [f"backend/{d}/__init__.py" for d in SUBDIRS]

def create_project():
    created_dirs = []
    created_files = []

    # 1. 创建 backend 目录
    backend_path = os.path.join(BASE_DIR, "backend")
    if not os.path.exists(backend_path):
        os.makedirs(backend_path)
        created_dirs.append("backend")
        print(f"[创建目录] backend/")
    else:
        print(f"[已存在] backend/")

    # 2. 创建子目录
    for sub in SUBDIRS:
        dir_path = os.path.join(backend_path, sub)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            created_dirs.append(f"backend/{sub}")
            print(f"[创建目录] backend/{sub}/")
        else:
            print(f"[已存在] backend/{sub}/")

    # 3. 创建 __init__.py 文件
    for rel_path in INIT_FILES:
        file_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                pass  # 创建空文件
            created_files.append(rel_path)
            print(f"[创建文件] {rel_path}")
        else:
            print(f"[已存在] {rel_path}")

    # 打印汇总
    print("\n=== 创建完成 ===")
    print(f"新建目录数: {len(created_dirs)}")
    print(f"新建文件数: {len(created_files)}")
    if created_dirs:
        print("目录列表:")
        for d in created_dirs:
            print(f"  {d}/")
    if created_files:
        print("文件列表:")
        for f in created_files:
            print(f"  {f}")

if __name__ == "__main__":
    create_project()