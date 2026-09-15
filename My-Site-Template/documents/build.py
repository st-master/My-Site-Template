import os
import glob
import subprocess
import frontmatter
from jinja2 import Template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def scan_and_parse_md():
    cards = []
    md_files = glob.glob(os.path.join(BASE_DIR, "**/*.md"), recursive=True)
    
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
            
    cards.sort(key=lambda x: x['date'], reverse=True)
    return cards

def render_index_html(cards, index_path):
    if not os.path.exists(index_path):
        print(f"Error: {index_path} が見つかりません。")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    template = Template(template_content)
    rendered_html = template.render(cards=cards)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)
        
    print(f"成功: [{index_path}] に {len(cards)} 件のカードを出力しました。")

def auto_git_push(message="auto: build capsule index.html"):
    """Gitのステージング・コミット・プッシュを自動化"""
    try:
        # 1. ステージング
        subprocess.run(["git", "add", "."], check=True)
        # 2. 確定（コミット）
        subprocess.run(["git", "commit", "-m", message], check=True)
        # 3. 昇華（リモートへのPush）
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("成功: Git への昇華（Push）が完了しました。")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作中にエラーが発生しました（変更がない等の可能性）: {e}")

if __name__ == "__main__":
    cards = scan_and_parse_md()
    index_html_path = os.path.join(BASE_DIR, "index.html")
    render_index_html(cards, index_html_path)
    
    # Git への自動反映を実行
    auto_git_push("auto: Update index.html via build.py")
    