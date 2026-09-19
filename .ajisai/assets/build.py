import os
import json
import mimetypes
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

def update_node_manifest(node_dir: Path) -> dict:
    """フォルダー内を走査し、node.json を自動作成・更新する"""
    children = []
    assets = []

    for entry in node_dir.iterdir():
        if entry.name.startswith('.'):
            continue
        
        if entry.is_dir():
            children.append(entry.name)
        elif entry.is_file():
            # システム制御用ファイルはアセットから除外
            if entry.name not in ['node.json', 'index.html', 'build.py', 'template.html', 'structure.yaml']:
                assets.append(entry.name)

    node_json_path = node_dir / "node.json"
    data = {}
    if node_json_path.exists():
        try:
            with open(node_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass

    # メタデータのデフォルト値補完と最新リストの書き換え
    data['id'] = data.get('id', node_dir.name)
    data['title'] = data.get('title', f"{node_dir.name.capitalize()} ギャラリー")
    data['icon'] = data.get('icon', '📁')
    data['children'] = sorted(children)
    data['assets'] = sorted(assets, reverse=True)

    with open(node_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data

def generate_cards(target_dir: Path, assets: list) -> str:
    """アセット群からカードUI HTMLを生成"""
    cards_html = ""
    for filename in assets:
        filepath = target_dir / filename
        mime_type, _ = mimetypes.guess_type(filepath)
        
        if mime_type and mime_type.startswith('image/'):
            media_tag = f'<img src="{filename}" alt="{filename}" loading="lazy">'
        elif mime_type and mime_type.startswith('video/'):
            media_tag = f'<video src="{filename}" controls preload="metadata"></video>'
        elif mime_type and mime_type.startswith('audio/'):
            media_tag = f'<audio src="{filename}" controls></audio>'
        else:
            media_tag = f'<a href="{filename}" target="_blank" class="doc-link">📄 {filename}</a>'

        cards_html += f"""
<article class="media-card">
  <div class="card-media">{media_tag}</div>
  <div class="card-body"><p class="filename">{filename}</p></div>
</article>"""
    return cards_html

def generate_child_node_cards(children: list, child_manifests: dict) -> str:
    """配下の子ノード（サブギャラリー）へのポータルカードUIを生成"""
    cards_html = ""
    for child in children:
        info = child_manifests.get(child, {})
        title = info.get('title', child)
        icon = info.get('icon', '📁')
        
        cards_html += f"""
<article class="media-card portal-card">
  <div class="card-body">
    <h3>{icon} {title}</h3>
    <a href="./{child}/" class="portal-btn">ノードを開く →</a>
  </div>
</article>"""
    return cards_html

def process_node(current_dir: Path, template_content: str, depth: int = 0):
    """ノードの更新とHTML生成を行う再帰処理"""
    # 1. 自身の node.json を自動更新
    node_data = update_node_manifest(current_dir)

    # 2. 配下の子ノードを再帰処理
    child_manifests = {}
    for child_name in node_data['children']:
        child_dir = current_dir / child_name
        child_manifests[child_name] = process_node(child_dir, template_content, depth + 1)

    # 3. 相対パスの計算（CSSやナビゲーション用）
    rel_css_path = "../" * depth + "style.css" if depth > 0 else "./style.css"
    
    # 4. HTMLの組み立て
    page = template_content.replace('{{TITLE}}', node_data['title'])
    page = page.replace('{{HEADER}}', f"{node_data['icon']} {node_data['title']}")
    
    # style.css へのリンク補正
    page = page.replace('href="style.css"', f'href="{rel_css_path}"')
    page = page.replace('href="../style.css"', f'href="{rel_css_path}"')

    # アセットカード ＋ 子ノードポータルカードの結合
    asset_cards = generate_cards(current_dir, node_data['assets'])
    child_cards = generate_child_node_cards(node_data['children'], child_manifests)
    all_cards = child_cards + asset_cards

    if '<!-- GALLERY-START -->' in page and '<!-- GALLERY-END -->' in page:
        b, a = page.split('<!-- GALLERY-START -->')[0], page.split('<!-- GALLERY-END -->')[1]
        page = f"{b}<!-- GALLERY-START -->\n<div class=\"gallery-grid\">\n{all_cards}\n</div>\n<!-- GALLERY-END -->{a}"

    # 5. index.html を出力
    index_path = current_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(page)

    print(f"✨ Node構築完了 [{ '根' if depth==0 else f'深さ:{depth}' }]: {current_dir.relative_to(BASE_DIR)}/index.html")
    return node_data

def main():
    template_path = BASE_DIR / "template.html"
    if not template_path.exists():
        print("⚠️ template.html が見つかりません。")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    print("⚡ ノード自動検知＆構築処理を開始します...")
    process_node(BASE_DIR, template_content, depth=0)
    print("\n🎉 全ノードの `node.json` 更新および HTML 具現化が完結しました！")

if __name__ == '__main__':
    main()