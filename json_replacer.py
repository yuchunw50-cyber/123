import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def process_directory(src_dir, dest_dir):
    # 防止目标文件夹选在源文件夹内部导致无限循环嵌套
    if os.path.abspath(dest_dir).startswith(os.path.abspath(src_dir)):
        messagebox.showerror("错误", "目标文件夹不能在源文件夹内部，请重新选择！")
        return

    json_modified_count = 0
    other_copied_count = 0

    try:
        for root, dirs, files in os.walk(src_dir):
            # 获取当前目录的相对路径，并在目标文件夹中构建相同的层级结构
            rel_path = os.path.relpath(root, src_dir)
            target_root = os.path.join(dest_dir, rel_path)

            if not os.path.exists(target_root):
                os.makedirs(target_root)

            for file in files:
                src_file = os.path.join(root, file)
                target_file = os.path.join(target_root, file)

                # 处理 JSON 文件（纯文本级操作，不使用 json 库，保证格式绝对保真）
                if file.lower().endswith('.json'):
                    try:
                        with open(src_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 精准替换
                        new_content = content.replace('"N/A"', '"NA"')
                        
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        json_modified_count += 1
                    except UnicodeDecodeError:
                        # 如果 JSON 不是 utf-8 编码读取失败，则将其当作普通文件原样复制
                        shutil.copy2(src_file, target_file)
                        other_copied_count += 1
                else:
                    # 非 JSON 文件，原样带时间戳复制
                    shutil.copy2(src_file, target_file)
                    other_copied_count += 1

        # 处理完成提示
        messagebox.showinfo(
            "处理完成", 
            f"✅ 任务圆满结束！\n\n"
            f"📄 成功处理并克隆的 JSON 文件：{json_modified_count} 个\n"
            f"📁 原样复制的其他文件：{other_copied_count} 个"
        )

    except Exception as e:
        messagebox.showerror("运行报错", f"处理过程中发生错误：\n{str(e)}")

def select_src():
    path = filedialog.askdirectory(title="选择【源文件夹】")
    if path:
        src_var.set(path)

def select_dest():
    path = filedialog.askdirectory(title="选择【目标文件夹】")
    if path:
        dest_var.set(path)

def start_processing():
    src = src_var.get()
    dest = dest_var.get()
    
    if not src or not dest:
        messagebox.showwarning("提示", "请先选择源文件夹和目标文件夹！")
        return
        
    process_directory(src, dest)

# === GUI 界面构建 ===
root = tk.Tk()
root.title("JSON 'N/A' 批量修正工具")
root.geometry("450x250")
root.resizable(False, False)

src_var = tk.StringVar()
dest_var = tk.StringVar()

# 源文件夹选取
tk.Label(root, text="第一步：选择包含原始文件的【源文件夹】").pack(pady=(15, 5))
tk.Entry(root, textvariable=src_var, width=50, state='readonly').pack()
tk.Button(root, text="浏览...", command=select_src).pack(pady=5)

# 目标文件夹选取
tk.Label(root, text="第二步：选择用于保存处理结果的【目标文件夹】").pack(pady=(15, 5))
tk.Entry(root, textvariable=dest_var, width=50, state='readonly').pack()
tk.Button(root, text="浏览...", command=select_dest).pack(pady=5)

# 开始按钮
tk.Button(root, text="🚀 一键开始处理", command=start_processing, bg="green", fg="black", font=("Arial", 10, "bold")).pack(pady=15)

root.mainloop()
