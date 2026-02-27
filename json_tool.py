import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.scrolledtext as scrolledtext
import shutil
from pathlib import Path

def select_input_dir():
    # 【优化】获取路径，如果用户没点取消，才填入输入框
    path = filedialog.askdirectory(title="选择源文件夹")
    if path:
        input_var.set(path)

def select_output_dir():
    # 【优化】获取路径，如果用户没点取消，才填入输入框
    path = filedialog.askdirectory(title="选择保存的输出文件夹")
    if path:
        output_var.set(path)

# 向界面的文本框打印日志
def log_msg(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END) # 自动滚动到最底部
    root.update()       # 刷新界面

def run_process():
    input_folder = input_var.get()
    output_folder = output_var.get()
    
    if not input_folder or not output_folder:
        messagebox.showwarning("提示", "请先选择【源文件夹】和【输出文件夹】！")
        return
        
    # 清空旧日志，准备开始
    log_box.delete(1.0, tk.END)
    btn_start.config(state="disabled")
    log_msg("🚀 开始扫描文件夹...\n")
    
    try:
        input_dir = Path(input_folder)
        output_dir = Path(output_folder)
        
        # 获取所有文件
        all_files = [p for p in input_dir.rglob("*") if p.is_file()]
        
        if not all_files:
            log_msg("⚠️ 源文件夹中没有任何文件。")
            btn_start.config(state="normal")
            return

        json_index = 0      # 专门给 JSON 文件排的序号
        modified_list = []  # 记录被修改的序号和文件名
        other_count = 0     # 记录其他文件的数量
        
        for file_path in all_files:
            rel_path = file_path.relative_to(input_dir)
            out_path = output_dir / rel_path
            
            # 自动创建需要的子文件夹
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 核心逻辑：区分 JSON 和其他文件
            if file_path.suffix.lower() == '.json':
                json_index += 1  # 只要是 JSON，就分配一个序号
                
                # 读取内容
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 判断是否包含需要替换的 N/A
                if 'N/A' in content:
                    new_content = content.replace('N/A', 'NA')
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    # 记录这个被修改的序号
                    modified_list.append(f"序号 {json_index} : {rel_path.name}")
                    log_msg(f"✅ [已修改] 序号 {json_index} -> 发现 N/A，已替换！")
                else:
                    # 没有 N/A，直接复制，保持原样
                    shutil.copy2(file_path, out_path)
                    log_msg(f"⏩ [未修改] 序号 {json_index} -> 无 N/A，已原样复制。")
            else:
                # 非 JSON 文件，直接原样克隆
                shutil.copy2(file_path, out_path)
                other_count += 1
                
        # ================= 生成最终报告 =================
        log_msg("\n================ 处理完成 ================")
        log_msg(f"总计扫描 JSON 文件：{json_index} 个")
        log_msg(f"实际发生修改的 JSON：{len(modified_list)} 个")
        log_msg(f"原样复制的非 JSON 文件：{other_count} 个\n")
        
        if modified_list:
            log_msg("【具体被修改的序号清单】:")
            for m in modified_list:
                log_msg(m)
                
            # 把清单保存到输出文件夹里，方便以后查阅
            report_path = output_dir / "修改记录报告.txt"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("=== JSON 批量替换报告 (N/A -> NA) ===\n\n")
                f.write(f"总处理 JSON 数量: {json_index}\n")
                f.write(f"实际修改数量: {len(modified_list)}\n")
                f.write("-" * 40 + "\n")
                f.write("以下序号的文件发生了修改：\n")
                f.write("\n".join(modified_list))
                
            log_msg(f"\n📄 详细清单已自动保存为: {report_path.name}")
        else:
            log_msg("🎉 没有发现任何需要修改的 JSON 文件。")
            
        messagebox.showinfo("处理成功", f"任务完成！\n共修改了 {len(modified_list)} 个 JSON 文件。")
        
    except Exception as e:
        log_msg(f"\n❌ 处理过程中发生错误：\n{e}")
        messagebox.showerror("错误", f"发生报错：\n{e}")
    finally:
        btn_start.config(state="normal")

# ================= 界面绘制 (GUI) =================
root = tk.Tk()
root.title("JSON 批量处理专家")
root.geometry("650x450") 

input_var = tk.StringVar()
output_var = tk.StringVar()

# 顶部区域：选择文件夹
frame_top = tk.Frame(root)
frame_top.pack(pady=10, fill="x", padx=15)

tk.Label(frame_top, text="1. 源文件夹:").grid(row=0, column=0, sticky="w", pady=5)
# 【核心修改】删掉了 state="readonly"，打破 Mac 的输入框封锁
tk.Entry(frame_top, textvariable=input_var, width=35).grid(row=0, column=1, padx=5)
tk.Button(frame_top, text="浏览...", command=select_input_dir).grid(row=0, column=2)

tk.Label(frame_top, text="2. 输出文件夹:").grid(row=1, column=0, sticky="w", pady=5)
# 【核心修改】删掉了 state="readonly"，打破 Mac 的输入框封锁
tk.Entry(frame_top, textvariable=output_var, width=35).grid(row=1, column=1, padx=5)
tk.Button(frame_top, text="浏览...", command=select_output_dir).grid(row=1, column=2)

# 中间按钮
btn_start = tk.Button(root, text="🚀 开始一键处理", command=run_process, bg="#4CAF50", fg="black", font=("Arial", 11, "bold"))
btn_start.pack(pady=10)

# 底部区域：实时日志框
tk.Label(root, text="处理日志 (实时追踪序号):").pack(anchor="w", padx=15)
log_box = scrolledtext.ScrolledText(root, width=70, height=15, bg="#F0F0F0")
log_box.pack(padx=15, pady=5)

root.mainloop()
