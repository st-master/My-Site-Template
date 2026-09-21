import os
import sys
import glob
from pathlib import Path

# PyYAMLのチェック（必要に応じて install を促す）
try:
    import yaml
except ImportError:
    print("エラー: PyYAML がインストールされていません。")
    print("pip install pyyaml を実行してください。")
    sys.exit(1)

class OrientedPhilosophiaProjector:
    def __init__(self, relation_file="relation.yaml"):
        self.relation_file = Path(relation_file)
        self.config = {}
        
    def load_relation(self):
        """relation.yaml を読み込んでパースする"""
        if not self.relation_file.exists():
            print(f"警告: {self.relation_file} が見つかりません。デフォルト設定で動作します。")
            return self.get_default_config()

        print(f"[*] {self.relation_file} を解析中...")
        with open(self.relation_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        print(f"[+] Loaded Model: {self.config.get('model', 'Unknown')}")
        print(f"[+] Bean (Template): {self.config.get('extends', {}).get('template')}")
        return self.config

    def get_default_config(self):
        return {
            "components": {
                "content_dir": "./documents",
                "assets_dir": "./assets",
                "output_dir": "./dist"
            }
        }

    def project(self):
        """Film(素材)を読み込み、Screen(成果物)へと投影(ビルド)する"""
        self.load_relation()
        
        content_dir = Path(self.config.get("components", {}).get("content_dir", "./documents"))
        output_dir = Path(self.config.get("components", {}).get("output_dir", "./dist"))
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # mdファイルの収集
        md_files = list(content_dir.glob("*.md"))
        print(f"[*] 対象ドキュメント数: {len(md_files)} 件")
        
        for md_file in md_files:
            # 今後ここにテンプレート合成・HTML変換処理が入ります
            print(f"    - Processing: {md_file.name}")
            
        print("[✔] 投影（ビルド）処理が完了しました。")

if __name__ == "__main__":
    projector = OrientedPhilosophiaProjector()
    projector.project()
    