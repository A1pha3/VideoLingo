import os
import shutil

from core.utils.models import _AUDIO_SEGS_DIR, _AUDIO_TMP_DIR, _AUDIO_TTS_SIGNATURE

def delete_dubbing_files():
    files_to_delete = [
        os.path.join("output", "dub.wav"),
        os.path.join("output", "dub.mp3"),
        os.path.join("output", "dub.srt"),
        os.path.join("output", "normalized_dub.wav"),
        os.path.join("output", "output_dub.mp4"),
        _AUDIO_TTS_SIGNATURE,
    ]
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {str(e)}")
        else:
            print(f"File not found: {file_path}")
    
    for folder_path in (_AUDIO_SEGS_DIR, _AUDIO_TMP_DIR):
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"Deleted folder and contents: {folder_path}")
            except Exception as e:
                print(f"Error deleting folder {folder_path}: {str(e)}")
        else:
            print(f"Folder not found: {folder_path}")

if __name__ == "__main__":
    delete_dubbing_files()