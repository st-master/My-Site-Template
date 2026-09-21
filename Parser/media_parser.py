import shutil
from pathlib import Path

class MediaHandler:
    """3次元のメディア素材（画像・音声・動画）をScreenへ同期転送する2次元ロジック"""

    def sync_directory(self, src_dir, dst_dir):
        src_path = Path(src_dir)
        dst_path = Path(dst_dir)

        if not src_path.exists():
            return

        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        print(f"[*] アセット同期完了: {src_path.name} -> {dst_path}")