from pathlib import Path

class TemplateHandler:
    """Structure/ から受け取った骨格データを合成し、最終的な HTML (Screen) を生成する2次元 Bean"""

    def _get_default_styles(self):
        """
        [CSS 変数による視覚表現の抽象化]
        将来的に Design/ Bean へスタイル管理を委譲しやすい設計に切り出し
        """
        return """
        :root {
            /* 基礎カラーパレット */
            --op-bg-color: #f8f9fa;
            --op-text-color: #212529;
            --op-text-muted: #6c757d;
            --op-card-bg: #ffffff;
            --op-border-color: #e9ecef;
            --op-accent-color: #0d6efd;
            
            /* タイポグラフィ & レイアウト */
            --op-font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --op-max-width: 800px;
            --op-radius: 8px;
            --op-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }

        body {
            font-family: var(--op-font-family);
            background-color: var(--op-bg-color);
            color: var(--op-text-color);
            line-height: 1.7;
            margin: 0;
            padding: 0;
        }

        header.site-header {
            background: var(--op-card-bg);
            border-bottom: 1px solid var(--op-border-color);
            padding: 2rem 1rem;
            text-align: center;
        }

        header.site-header h1 {
            margin: 0;
            font-size: 1.8rem;
            letter-spacing: 0.05em;
        }

        main.container {
            max-width: var(--op-max-width);
            margin: 2rem auto;
            padding: 0 1rem;
        }

        article.op-document {
            background: var(--op-card-bg);
            border: 1px solid var(--op-border-color);
            border-radius: var(--op-radius);
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--op-shadow);
        }

        .document-header {
            border-bottom: 1px solid var(--op-border-color);
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }

        .document-title {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
        }

        .document-meta {
            font-size: 0.85rem;
            color: var(--op-text-muted);
        }

        .document-date {
            margin-right: 1rem;
        }

        .no-content {
            text-align: center;
            color: var(--op-text-muted);
            padding: 3rem 0;
        }

        footer.site-footer {
            text-align: center;
            padding: 2rem 1rem;
            font-size: 0.85rem;
            color: var(--op-text-muted);
            border-top: 1px solid var(--op-border-color);
            margin-top: 3rem;
        }
        """

    def render_index(self, structured_documents, site_name="Oriented Philosophia", custom_css=None):
        """
        複数のドキュメント骨格群を index.html のテンプレート枠組みへ流し込む
        custom_css パラメータを指定することで Design/ Bean からの注入にも柔軟に対応
        """
        articles_html = "\n".join([doc["structured_html"] for doc in structured_documents])
        
        if not articles_html:
            articles_html = '<p class="no-content">コンテンツがまだ存在しません。</p>'

        # Design/ からの指定があれば優先、なければデフォルト変数を採用
        css_content = custom_css if custom_css is not None else self._get_default_styles()

        full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_name}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <header class="site-header">
        <h1>{site_name}</h1>
    </header>
    
    <main class="container">
{articles_html}
    </main>

    <footer class="site-footer">
        <p>&copy; Oriented Philosophia Model - Projected by OPModel</p>
    </footer>
</body>
</html>"""
        return full_html

    def write_output(self, html_content, output_dir, file_name="index.html"):
        """生成された HTML を dist/ 配下へ出力保存する"""
        out_path = Path(output_dir) / file_name
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[*] HTML 投影完了: {out_path}")