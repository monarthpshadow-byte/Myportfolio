import os
import hashlib
from collections import defaultdict

def get_file_hash(filepath, chunk_size=8192):
    """محاسبه هش SHA-256 یک فایل"""
    hash_func = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def find_duplicates(folder_path):
    """پیدا کردن فایل‌های تکراری در یک پوشه"""
    hash_map = defaultdict(list)
    
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                file_hash = get_file_hash(filepath)
                hash_map[file_hash].append(filepath)
            except (IOError, OSError):
                continue
    
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return duplicates

def delete_duplicates(duplicates, keep_first=True):
    """حذف فایل‌های تکراری و نگه‌داری اولین نسخه"""
    deleted_count = 0
    for hash_val, paths in duplicates.items():
        if keep_first:
            paths_to_delete = paths[1:]  # نگه‌داری اولین فایل
        else:
            paths_to_delete = paths[:-1]  # نگه‌داری آخرین فایل
            
        for filepath in paths_to_delete:
            try:
                os.remove(filepath)
                print(f"حذف شد: {filepath}")
                deleted_count += 1
            except Exception as e:
                print(f"خطا در حذف {filepath}: {e}")
    
    return deleted_count

if __name__ == "__main__":
    folder = input("آدرس پوشه مورد نظر را وارد کنید: ").strip()
    
    if not os.path.exists(folder):
        print("پوشه وجود ندارد!")
    else:
        print("در حال اسکن پوشه...")
        duplicates = find_duplicates(folder)
        
        if not duplicates:
            print("هیچ فایل تکراری پیدا نشد.")
        else:
            total_files = sum(len(paths) for paths in duplicates.values())
            print(f"\nتعداد فایل‌های تکراری: {total_files}")
            print(f"تعداد گروه‌های تکراری: {len(duplicates)}")
            
            confirm = input("آیا می‌خواهید فایل‌های تکراری را حذف کنید؟ (y/n): ").lower()
            if confirm == 'y':
                deleted = delete_duplicates(duplicates)
                print(f"\n{deleted} فایل با موفقیت حذف شد.")