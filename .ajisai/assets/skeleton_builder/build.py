import sys
from pathlib import Path
import yaml

def create_structure(base_path: Path, data):
    """YAMLのデータ構造を再帰的に解析してディレクトリとファイルを自動生成"""
    if isinstance(data, dict):
        for dir_name, contents in data.items():
            dir_path = base_path / str(dir_name)
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[📁 フォルダ作成] {dir_path}")
            
            if contents:
                create_structure(dir_path, contents)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                file_path = base_path / item
                # 親フォルダがなければ自動作成して空ファイルを準備
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch(exist_ok=True)
                print(f"[📄 ファイル作成]   {file_path}")
            else:
                create_structure(base_path, item)

def main():
    yaml_file = Path("structure.yaml")

    if not yaml_file.exists():
        print(f"エラー: 定義ファイル '{yaml_file}' が見つかりません。")
        sys.exit(1)

    print("YAML定義書を読み込み、ディレクトリ構築を開始します...\n")

    with open(yaml_file, "r", encoding="utf-8") as f:
        try:
            structure_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"YAMLの構文エラーが発生しました: {e}")
            sys.exit(1)

    # カレントディレクトリを起点に構築実行
    create_structure(Path("."), structure_data)
    print("\nすべてのディレクトリとファイルの自動構築が完了しました！")

if __name__ == "__main__":
    main()