import re
from pathlib import Path

class StructureHandler:
    """カレントの空点 '.' における構造解析および HTML 骨格変換を担当する2次元 Bean"""

    def scan_context(self, base_dir="."):
        """物理フォルダ構造をスキャンしてコンポーネントマップを生成"""
        base_path = Path(base_dir)
        ignore_dirs = {
            ".git", ".vscode", "__pycache__", "dist",
            "Parser", "Design", "Structure", "Template", "OPModel"
        }
        
        detected_dirs = [
            d.name for d in base_path.iterdir() 
            if d.is_dir() and d.name not in ignore_dirs
        ]

        target_map = {
            "documents": ("content_dir", "./documents"),
            "assets": ("assets_dir", "./assets"),
            "images": ("images_dir", "./images"),
            "audios": ("audios_dir", "./audios"),
            "videos": ("videos_dir", "./videos")
        }

        components = {}
        for dir_name, (config_key, path_val) in target_map.items():
            if dir_name in detected_dirs:
                components[config_key] = path_val

        components["output_dir"] = "./dist"
        return components

    def markdown_to_html(self, md_text):
        """簡易 Markdown -> HTML 変換器 (見出し、太字、コード、リスト、段落)"""
        html = md_text

        # 1. コードブロック (``` ... ```)
        html = re.sub(r'```(.*?)\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

        # 2. 見出し (# 〜 ####)
        html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # 3. 装飾 (太字・斜体・インラインコード)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)

        # 4. リスト (- または *)
        lines = html.split('\n')
        in_list = False
        new_lines = []
        for line in lines:
            if re.match(r'^\s*[\-\*]\s+(.*)$', line):
                item = re.sub(r'^\s*[\-\*]\s+(.*)$', r'<li>\1</li>', line)
                if not in_list:
                    new_lines.append('<ul>')
                    in_list = True
                new_lines.append(item)
            else:
                if in_list:
                    new_lines.append('</ul>')
                    in_list = False
                new_lines.append(line)
        if in_list:
            new_lines.append('</ul>')
        html = '\n'.join(new_lines)

        # 5. 空行区切りの段落 (<p>)
        paragraphs = html.split('\n\n')
        processed_p = []
        for p in paragraphs:
            p_strip = p.strip()
            if not p_strip:
                continue
            # すでに HTML タグで始まっている場合は <p> で囲まない
            if re.match(r'^<(h[1-6]|ul|ol|li|pre|blockquote|article|section)', p_strip):
                processed_p.append(p_strip)
            else:
                processed_p.append(f'<p>{p_strip.replace("\n", "<br>")}</p>')

        return '\n'.join(processed_p)

    def build_document_structure(self, metadata, body_text):
        """メタデータと本文を受け取り、セマンティックな HTML 骨格 (<article>) を構築する"""
        raw_html_body = self.markdown_to_html(body_text)
        
        title = metadata.get("title", "Untitled")
        date = metadata.get("date", "")
        category = metadata.get("category", "")

        # HTML 構造体の組み立て
        structured_html = f"""<article class="op-document">
  <header class="document-header">
    <h1 class="document-title">{title}</h1>
    <div class="document-meta">
      {f'<span class="document-date">{date}</span>' if date else ''}
      {f'<span class="document-category">{category}</span>' if category else ''}
    </div>
  </header>
  <section class="document-body">
{raw_html_body}
  </section>
</article>"""

        return {
            "title": title,
            "date": date,
            "category": category,
            "structured_html": structured_html
        }