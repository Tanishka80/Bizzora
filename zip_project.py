import shutil
import os

source_dir = r"c:\Users\tanuv\Downloads\microproject"
zip_path = r"c:\Users\tanuv\Downloads\Bizzora_Project"

ignore_patterns = shutil.ignore_patterns("env", ".venv", "__pycache__", ".git", ".idea", ".vscode")

temp_dir = r"c:\Users\tanuv\Downloads\Bizzora_Temp"
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)

shutil.copytree(source_dir, temp_dir, ignore=ignore_patterns)
shutil.make_archive(zip_path, 'zip', temp_dir)
shutil.rmtree(temp_dir)
print(f"Created zip archive at {zip_path}.zip")
