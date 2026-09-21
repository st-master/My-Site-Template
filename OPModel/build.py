import sys
import shutil
from pathlib import Path

# 親ディレクトリ (st-master) を検索パスの最優先に追加
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import yaml
except ImportError:
    print("エラー: PyYAML がインストールされていません。")
    sys.exit(1)

# 2次元 Bean のインポート
from Structure.structure_handler import StructureHandler
from Parser.markdown_parser import MarkdownHandler
from Parser.media_parser import MediaHandler
from Template.template_handler import TemplateHandler
from Design.design_handler import DesignHandler

class OrientedPhilosophiaProjector:
    def __init__(self, relation_file="relation.yaml"):
        self.relation_file = CURRENT_DIR / relation_file
        self.config = {}
        
        # 各 2次元 Bean プロセッサの初期化
        self.structure_handler = StructureHandler()
        self.md_handler = MarkdownHandler()
        self.media_handler = MediaHandler()
        self.template_handler = TemplateHandler()
        self.design_handler = None  # project() 時に relation.yaml から動的生成

    def sync_context(self):
        """Structure/ に構造解析を委譲し、relation.yaml (Context) を同期する"""
        detected_components = self.structure_handler.scan_context(CURRENT_DIR)

        if self.relation_file.exists():
            with open(self.relation_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {
                "name": "My-Site-Instance",
                "theme": "default",  # デフォルトテーマ
                "version": "1.0.0",
                "model": "OrientedPhilosophiaModel",
                "extends": {
                    "structure": "../Structure",
                    "design": "../Design",
                    "template": "../Template",
                    "parser": "../Parser"
                },
                "projector": {
                    "entry_point": "index.html",
                    "clean_output": True
                }
            }

        # theme キーが存在しない場合は追加
        if "theme" not in self.config:
            self.config["theme"] = "default"

        current_components = self.config.get("components", {})
        updated = False

        for key, val in detected_components.items():
            if current_components.get(key) != val:
                current_components[key] = val
                updated = True

        self.config["components"] = current_components

        if updated or not self.relation_file.exists():
            print(f"[*] Structure/ の解析に基づき {self.relation_file.name} を更新します...")
            with open(self.relation_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
            print(f"[✔] {self.relation_file.name} を自動同期・保存しました。")
        else:
            print(f"[*] {self.relation_file.name} の構成情報は最新状態です。")

    def project(self):
        """パイプライン処理: Structure -> Parser -> Design -> Template"""
        # 工程 0: 構造同期 (Structure Bean)
        self.sync_context()
        
        components = self.config.get("components", {})
        content_dir = CURRENT_DIR / Path(components.get("content_dir", "./documents"))
        output_dir = CURRENT_DIR / Path(components.get("output_dir", "./dist"))
        
        # 3. 事前クリーンアップ機能 (dist/ 内をクリア)
        if output_dir.exists():
            for item in output_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            print(f"[*] {output_dir.name}/ 内の過去ファイルをクリーンアップしました。")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 工程 1 & 2: ドキュメント解析 (Parser) ──> 骨格構造変換 (Structure)
        structured_documents = []
        if content_dir.exists():
            md_files = list(content_dir.glob("*.md"))
            print(f"[*] 対象ドキュメント数: {len(md_files)} 件")
            
            for md_file in md_files:
                metadata, body = self.md_handler.process_file(md_file)
                doc_structure = self.structure_handler.build_document_structure(metadata, body)
                structured_documents.append(doc_structure)
                print(f"    - Structured: [{doc_structure['date']}] {doc_structure['title']}")

        # 1. 日付順ソート（降順: 新しい順）
        structured_documents.sort(key=lambda x: str(x.get("date", "")), reverse=True)

        # 工程 3: メディア同期 (Parser Bean)
        media_keys = ["images_dir", "audios_dir", "videos_dir", "assets_dir"]
        for key in media_keys:
            if key in components:
                src = CURRENT_DIR / Path(components[key])
                self.media_handler.sync_directory(src, output_dir / src.name)

        # 2. テーマ動的読み込み (Design Bean)
        theme_name = self.config.get("theme", "default")
        self.design_handler = DesignHandler(theme=theme_name)
        custom_css = self.design_handler.get_custom_css()
        print(f"[*] 適用テーマ: '{theme_name}'")

        # 工程 5: レイアウト合成・書き出し (Template Bean)
        site_name = self.config.get("name", "Oriented Philosophia")
        final_html = self.template_handler.render_index(
            structured_documents, 
            site_name=site_name, 
            custom_css=custom_css
        )
        self.template_handler.write_output(final_html, output_dir)
            
        print("[✔] 投影パイプライン（Structure -> Parser -> Design -> Template）が全工程正常に完了しました。")

if __name__ == "__main__":
    projector = OrientedPhilosophiaProjector()
    projector.project()