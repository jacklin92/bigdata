import os

def generate_first_level_tree(start_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{os.path.basename(start_path)}/\n")
        with os.scandir(start_path) as entries:
            for entry in entries:
                prefix = '├── '
                if entry.is_dir():
                    f.write(f"{prefix}{entry.name}/\n")
                else:
                    f.write(f"{prefix}{entry.name}\n")

# 使用範例
generate_first_level_tree(r'C:\Users\jackl\OneDrive\文件\課程\bigdata\Mid\site_news_analysis_v2', 'tree_output.txt')
