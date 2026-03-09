import os
import sys
from google import genai
from google.genai import types
from PIL import Image
import io

def run_visual_layout_check(template_img_path, generated_img_path, model_name='gemini-2.5-pro'):
    """
    视觉一致性校验：利用多模态大模型对比原模板与成品的视觉排版。
    """
    print("\n[Visual Check Agent] 👁️ 正在进行跨系统多模态排版校验...")
    
    if not os.path.exists(template_img_path) or not os.path.exists(generated_img_path):
        print("  -> ⚠️ 跳过：未检测到截图文件。请提供 A:\\AI_Studio\\Auto-docs\\老妈需求\\ 目录下的图片。")
        return None

    client = genai.Client()
    
    # 读取图片
    with open(template_img_path, 'rb') as f:
        template_img = f.read()
    with open(generated_img_path, 'rb') as f:
        generated_img = f.read()

    prompt = """
请作为一位专业的排版排版质检员，对比以下两张截图。
第一张是【原始空白模板】，第二张是【AI生成的成品文档】。

任务：
1. 检查是否存在严重的排版畸变（如：表格被内容撑爆变形、字体大小突变、缩进丢失）。
2. 评估视觉美感：内容分布是否均匀，是否存在某些格子过空或过满的情况。
3. 给出是否通过的结论。

请返回 JSON 格式：
{
  "visual_score": 9,
  "passed": true,
  "issues": ["文字略显拥挤", "..."],
  "suggestion": "减少任务二的文字描述"
}
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                prompt,
                types.Part.from_bytes(data=template_img, mime_type='image/png'),
                types.Part.from_bytes(data=generated_img, mime_type='image/png')
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        import json
        result = json.loads(response.text)
        print(f"  -> 视觉评分: {result.get('visual_score')}/10 | 通过: {result.get('passed')}")
        return result
    except Exception as e:
        print(f"  -> ❌ 视觉校验失败: {e}")
        return None
