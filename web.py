import openai
import re
import time

def generate_web_page(prompt, max_retries=3):
    # API配置
    openai.api_base = "https://openai.api2d.net/v1"
    openai.api_key = "fk88888888888" #请替换实际密钥

    # 模型参数优化
    config = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 500,
        "request_timeout": 30
    }

    # 增强提示模板
    components = {
        "content": """请生成以下内容的网页文案（严格使用中文）：
主题：{theme}
要求：
1. 包含公司名称（后缀为科技有限公司）
2. 3段产品描述（每段不超过80字） 
3. 3个核心优势（使用图标符号★表示）
4. 联系方式包含电话和邮箱
请用```text包裹响应内容""",

        "html": """请生成符合HTML5标准的网页结构，包含：
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>[标题]</title>
</head>
<body>
    <!-- 包含header、main、footer结构 -->
</body>
</html>
输入内容：{content}
请用```html包裹完整代码""",

        "css": """请为以下HTML生成响应式CSS：
{html}
要求：
1. 使用Flexbox布局
2. 包含移动端媒体查询
3. 定义CSS变量管理主题色
请用```css包裹完整代码"""
    }

    # 增强代码提取函数
    def extract_code(response, lang):
        patterns = [
            fr'```{lang}\s*(.*?)```',  # 带语言标记
            fr'```\s*(.*?)```'        # 无标记
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return match.group(1).strip()
        return response  # 降级处理

    # 带重试机制的生成函数
    def generate_with_retry(prompt_template, variables):
        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    messages=[{
                        "role": "user",
                        "content": prompt_template.format(**variables)
                    }],
                    **config
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"请求失败，重试中 ({attempt+1}/{max_retries})...")
                time.sleep(2**attempt)  # 指数退避
        raise Exception("API请求失败")

    # 生成流程
    try:
        # 步骤1：生成内容
        content = generate_with_retry(components["content"], {"theme": prompt})
        print("="*40 + "\n原始内容响应:\n", content)
        clean_content = extract_code(content, "text")

        # 步骤2：生成HTML
        html_response = generate_with_retry(
            components["html"], {"content": clean_content}
        )
        print("="*40 + "\n原始HTML响应:\n", html_response)
        html_code = extract_code(html_response, "html")

        # 步骤3：生成CSS
        css_response = generate_with_retry(
            components["css"], {"html": html_code}
        )
        print("="*40 + "\n原始CSS响应:\n", css_response)
        css_code = extract_code(css_response, "css")

        # 组装最终页面
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{prompt}</title>
    <style>
        /* 生成时间：{time.strftime('%Y-%m-%d %H:%M')} */
        {css_code}
    </style>
</head>
{html_code}
</html>"""

    except Exception as e:
        print(f"生成失败: {str(e)}")
        return "<html><body><h1>页面生成失败</h1></body></html>"

# 使用示例
if __name__ == "__main__":
    page_html = generate_web_page(
        "智能家居解决方案提供商",
        max_retries=2
    )
    
    with open("generated_page.html", "w", encoding="utf-8") as f:
        f.write(page_html)
    
    print("网页已成功生成到 generated_page.html")
