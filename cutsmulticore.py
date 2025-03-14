import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import concurrent.futures

def process_image(args):
    file_path, selected_folder, new_folder_path, crop_box = args
    try:
        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        if not file_name.endswith("_B"):
            return (file_path, None, None)
        img = Image.open(file_path)
        cropped_img = img.crop(crop_box)
        relative_dir = os.path.relpath(os.path.dirname(file_path), selected_folder)
        target_dir = os.path.join(new_folder_path, relative_dir)
        os.makedirs(target_dir, exist_ok=True)
        new_file_name = file_name + "_已裁切" + file_ext
        new_file_path = os.path.join(target_dir, new_file_name)
        cropped_img.save(new_file_path)
        return (file_path, new_file_path, None)
    except Exception as e:
        return (file_path, None, str(e))

def main():
    root_dir = os.getcwd()
    tk.Tk().withdraw()
    selected_folder = filedialog.askdirectory(initialdir=root_dir, title="请选择要处理的子文件夹")
    if not selected_folder:
        print("没有选择任何文件夹，程序退出！")
        return

    parent_folder = os.path.dirname(selected_folder)
    folder_name = os.path.basename(selected_folder)
    new_folder_name = folder_name + "(已裁切)"
    new_folder_path = os.path.join(parent_folder, new_folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    
    crop_box = (170, 1193, 1458, 2149)
    
    file_list = []
    for root, dirs, files in os.walk(selected_folder):
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            if file_name.endswith("_B"):
                file_list.append(os.path.join(root, file))
    
    total_count = len(file_list)
    print(f"共找到 {total_count} 张符合条件的图片，即将开始处理...")
    
    error_files = []
    processed_count = 0
    log_interval = 100  # 每处理100张图片打印一次进度

    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        tasks = [(file_path, selected_folder, new_folder_path, crop_box) for file_path in file_list]
        futures = [executor.submit(process_image, task) for task in tasks]
        
        for future in concurrent.futures.as_completed(futures):
            source_file, target_file, error = future.result()
            processed_count += 1
            if error:
                error_files.append((source_file, error))
                # 如有必要，也可以立刻打印错误信息：
                print(f"处理出错: {source_file} 错误信息: {error}")
            if processed_count % log_interval == 0 or processed_count == total_count:
                print(f"处理进度：{processed_count}/{total_count}")

    error_count = len(error_files)
    print("\n==========================================")
    print(f"处理结束，共有 {error_count} 张图片处理出错。")
    if error_count > 0:
        print("出错的图片及错误信息如下：")
        for file_path, error_msg in error_files:
            print(f"{file_path}  错误信息: {error_msg}")
    print("==========================================")

if __name__ == '__main__':
    main()
