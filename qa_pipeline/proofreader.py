import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm_engine import generate_structured_data

def run_proofreader(draft_data: dict, model_name: str = 'gemini-2.5-pro') -> dict:
    """
    专业校对代理 (Copy-editing Agent)。
    专注于语义、错别字、标点符号及小学语文教学规范的深度润色。
    """
    print("\n[Proofreader Agent] 🕵️ 正在进行深度语义校对与润色...")
    
    draft_json = json.dumps(draft_data, ensure_ascii=False, indent=2)
    
    prompt = f"""
你是一位拥有国家级普通话水平和资深审稿经验的小学语文教研员 (Proofreader)。
请对以下【教案草稿 JSON】进行严格的错别字校对、语病修改和专业润色。

审查维度：
1. 错别字与标点：修复所有错别字，统一标点符号用法（如全角标点）。
2. 语病与流畅度：修复语病，使句子更加通顺，符合中文表达习惯。
3. 专业度：确保话术符合“部编版小学语文教学”的官方语境，避免生硬的机器翻译感。
4. 【红线规则】：绝对不能改变草稿原有的 JSON 结构（Key 不变）、数量（如目标只有2条就不准加到3条）以及特殊符号（如末尾的 ⭐ 必须保留）。
5. 【数据流扁平化】：你返回的 JSON 必须是纯粹的一层键值对，Value 必须是纯中文字符串。严禁在 Value 中嵌套任何字典或对象！

待校对的草稿：
{draft_json}

请直接返回经过完美润色的、扁平化的 JSON 数据：
"""
    
    polished_data = generate_structured_data(prompt, model_name)
    if polished_data:
        print("  -> ✨ 校对完成！文本已提升至专业教研级标准。")
        return polished_data
    else:
        print("  -> ⚠️ 校对超时或异常，保留原草稿。")
        return draft_data
