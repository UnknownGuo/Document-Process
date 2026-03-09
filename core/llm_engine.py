import os
import json
from google import genai
from google.genai import types

def generate_structured_data(prompt: str, model_name: str = 'gemini-2.5-pro') -> dict:
    """
    通用的大语言模型核心引擎。
    """
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("严重错误：环境变量中未找到 GEMINI_API_KEY。请检查项目根目录的 .env 文件。")
        
    client = genai.Client()
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        
        # 通用数据清洗：去除首尾空格，将连续空行合并
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip().replace("\n\n", "\n")
                
        return data
        
    except Exception as e:
        print(f"[核心引擎] AI 生成或解析 JSON 失败: {e}")
        return None

def generate_with_review(base_prompt: str, constraints: str, model_name: str = 'gemini-2.5-pro', max_retries: int = 3) -> dict:
    """
    混合架构核心：Writer + Reviewer 多智能体自我审查循环。
    """
    current_prompt = base_prompt
    
    for attempt in range(max_retries):
        print(f"\n[Writer Agent] 正在撰写草稿 (第 {attempt + 1}/{max_retries} 次尝试)...")
        draft_data = generate_structured_data(current_prompt, model_name)
        
        if not draft_data:
            return None
            
        print(f"[Reviewer Agent] 正在严格审查生成的教案质量...")
        reviewer_prompt = f"""
请你作为严格的质检员 (Reviewer)，审查以下 Writer 生成的 JSON 数据是否完全满足了所有的核心约束条件。

【必须严格遵守的核心约束条件】
{constraints}

【Writer 生成的 JSON 数据】
{json.dumps(draft_data, ensure_ascii=False, indent=2)}

任务：
1. 严格打分 (1-10分)。只要有任何一条约束没有满足（例如：目标写了4条而不是2-3条，或者某些行末尾缺少了 ⭐，或者包含了前缀），都必须扣分！
2. 如果分数 < 8 分，或者存在明显违反约束的情况，请将 passed 设为 false，并给出详细的修改建议 (feedback)。

返回纯 JSON 格式：
{{
  "score": 8,
  "passed": true,
  "feedback": "完全符合要求/某某地方未加星星，需要重写..."
}}
"""
        review_result = generate_structured_data(reviewer_prompt, model_name)
        
        if review_result:
            score = review_result.get("score", 0)
            passed = review_result.get("passed", False)
            feedback = review_result.get("feedback", "无反馈")
            
            print(f"  -> 审查得分: {score}/10 | 状态: {'✅ 通过' if passed else '❌ 打回'}")
            print(f"  -> 审查意见: {feedback}")
            
            if passed and score >= 8:
                return draft_data
            else:
                print(f"[系统调度] 稿件未达标，已将意见反馈给 Writer 进行重写。")
                current_prompt = base_prompt + f"\n\n【Reviewer 质检员的打回修改意见，请务必在这次生成中改正】：\n{feedback}"
        else:
            print("[系统调度] Reviewer 审查超时或异常，默认采纳当前初稿。")
            return draft_data
            
    print("[系统调度] 达到最大重试次数，输出最终稳定版本。")
    return draft_data
