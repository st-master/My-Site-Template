import re
import yaml
from pathlib import Path

class MarkdownHandler:
    """Markdown ファイルの Front Matter (YAML) と本文を分離・抽出する2次元ロジック"""

    def process_file(self, file_path):
        path = Path(file_path)
        if not path.exists():
            return {}, ""

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
            yaml_text = match.group(1)
            body = match.group(2)
            try:
                metadata = yaml.safe_load(yaml_text)
                # 読み込んだ結果が辞書(dict)でない場合は空辞書にする
                if not isinstance(metadata, dict):
                    metadata = {}
            except Exception:
                metadata = {}
            return metadata, body
        else:
            return {}, content