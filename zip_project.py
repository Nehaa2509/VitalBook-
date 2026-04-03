import os
import zipfile

def zip_directory(folder_path, zip_path):
    print(f"Creating zip file at: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            # Exclude folders
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', '.vscode', '.gemini', '.idea']]
            
            for file in files:
                if file.endswith('.pyc') or file == 'zip_project.py' or file == 'vitalbook.zip':
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
                
    print("Done!")

if __name__ == '__main__':
    project_dir = r"E:\Sneha\INTERSHIP\hospital"
    output_zip = r"E:\Sneha\INTERSHIP\vitalbook.zip"
    zip_directory(project_dir, output_zip)
