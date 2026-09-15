import os
import glob
import subprocess
import frontmatter
from jinja2 import Template

# ルートディレクトリ（My-Site-Template 直下）を基準に定義
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "documents")
INDEX_TEMPLATE_PATH = os.path.join(BASE_DIR, "index.html")

def scan_and_parse_md():
    """documents ディレクトリ内の全.mdファイルを走査し、メタデータを取得"""
    cards = []
    md_files = glob.glob(os.path.join(DOCS_DIR, "**/*.md"), recursive=True)
    
    for filepath in md_files:
        try:
            post = frontmatter.load(filepath)
            meta = post.metadata
            
            card_data = {
                'type': meta.get('type', 'card'),
                'title': meta.get('title', os.path.basename(filepath).replace('.md', '')),
                'date': str(meta.get('date', '1970.0101.00')),
                'category': meta.get('category', './Fortune'),
                'tags': meta.get('tags', []),
                'filepath': os.path.basename(filepath),
            }
            cards.append(card_data)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            
    # 日付の新しい順にソート
    cards.sort(key=lambda x: x['date'], reverse=True)
    return cards

def render_index_html(cards):
    """index.html にカードデータをレンダリングして上書き"""
    if not os.path.exists(INDEX_TEMPLATE_PATH):
        print(f"エラー: {INDEX_TEMPLATE_PATH} が存在しません。")
        return

    with open(INDEX_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)
    rendered_html = template.render(cards=cards)

    with open(INDEX_TEMPLATE_PATH, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
        
    print(f"成功: [{INDEX_TEMPLATE_PATH}] に {len(cards)} 件のカードを出力しました。")

def auto_git_push(message="auto: rebuild site with clean skeleton structure"):
    """Git コミットおよび Push の自動化"""
    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("成功: GitHub への送信（Push）が完了しました。")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作中にエラーが発生しました（変更なし等の可能性）: {e}")

if __name__ == "__main__":
    cards = scan_and_parse_md()
    render_index_html(cards)
    auto_git_push()