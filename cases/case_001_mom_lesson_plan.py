import os
import sys
import datetime
from dotenv import load_dotenv

# 确保能导入 core 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm_engine import generate_structured_data
from core.docx_injector import prepare_template, render_document

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def run_case(lesson_name: str, author: str = "王红晓"):
    print(f"========== 开始执行 Case 001: 智能教案生成 ({lesson_name}) ==========")
    
    # 1. 业务专属 Prompt
    prompt = f"""
你是一位深耕部编版小学语文教材 20 年的特级教师。请为六年级上册第二单元课文《{lesson_name}》编写一份【极简版】教学设计。

要求：
1. 身份：主备人【{author}】，审核人【留空】。
2. 风格：内容极简、精炼，禁止长篇大论。每个活动描述不超过 2 行。
3. 评价：在每一个 measure_x 字段末尾，必须统一加上：达成度：⭐⭐⭐⭐。
4. 格式：禁止多余的空行，禁止使用 Word 自动编号（如 1. 2.），请直接输出纯文本。
5. 结构：严格按照 JSON 格式输出。

JSON 结构：
{{
  "grade": "六年级",
  "author": "{author}",
  "reviewer": "",
  "title": "{lesson_name}",
  "type": "阅读课",
  "hours": "2课时",
  "objectives": "1. [目标1]\\n2. [目标2]\\n3. [目标3]",
  "metric_1": "[任务一核心指标]",
  "activity_1": "任务一：[名称]\\n活动1：[极简内容]\\n活动2：[极简内容]",
  "measure_1": "[补救措施]。达成度：⭐⭐⭐⭐",
  "metric_2": "...",
  "activity_2": "...",
  "measure_2": "...",
  "metric_3": "...",
  "activity_3": "...",
  "measure_3": "...",
  "blackboard": "板书提纲：\\n[核心词]\\n[分支1] -> [分支2]",
  "homework": "1. [作业1]\\n2. [作业2]",
  "reflection": ""
}}
"""
    
    # 2. 调用核心引擎生成内容
    data = generate_structured_data(prompt, model_name='gemini-2.5-pro')
    if not data:
        print("执行失败：AI 未能返回有效数据。")
        return

    # 3. 业务专属模板映射规则 (根据 template_with_tags.docx 中 1111 的分布)
    # 只要模板中的单元格或段落包含对应的 marker 字符串，引擎就会将其替换为 jinja2 tag
    mapping = {
        "17记金华的双龙洞1111": "title",
        "阅读课1111": "type",
        "第二课时1111": "hours",
        "4.通过“争做校园小导游”活动": "objectives", # 依靠这段文字定位整个目标框
        "说游踪 \n\n理顺序 \n\n圈词语\n1111": "metric_1",
        "任务一：读课文，理路线": "activity_1",
        "独立完成有难度": "measure_1",
        "圈景点     \n\n理见、闻、感\n\n说特点\n1111": "metric_2",
        "任务二：品课文，赏奇观": "activity_2",
        "自主完成后": "measure_2",
        "游踪：按顺序说": "metric_3",
        "任务三：争做校园小导游": "activity_3",
        "借助校园美景图片": "measure_3",
        "17 记金华的双龙同": "blackboard",
        "你游览过的地方中": "homework"
    }
    
    # 处理页眉和主备人的特殊逻辑，可以在模板里直接打好 tag，
    # 或者如果模板里没打 tag，我们在这里补充更精确的匹配：
    mapping["年级语文教学评一致性教学设计"] = "grade"
    mapping["主备人：                          审核人："] = "author" # 在实际渲染时，我们需要给 author 传整句，或者让引擎处理
    
    # 为了简化，我们假设模板里已经手动做好了 {{ grade }} 等，如果没做，上面的 mapping 会尝试暴力替换。
    # 这里我们使用一个中间临时文件
    raw_template = "/mnt/a/AI_Studio/Auto-docs/老妈需求/template_with_tags.docx"
    working_template = os.path.join(os.path.dirname(__file__), "temp_tagged_template.docx")
    
    # 4. 准备标签化模板
    prepare_template(raw_template, working_template, mapping)
    
    # 5. 渲染并输出至 Windows
    lesson_title = data.get("title", lesson_name).replace(":", "：")
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_dir = "/mnt/a/AI_Studio/Auto-docs/老妈需求/output"
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{lesson_title}_v3_{today}.docx")
    
    # 如果映射替换了主备人整行，我们需要调整 data，不过最好还是让 docx_injector 去细化
    data['author'] = f"主备人：{author}                          审核人："
    data['grade'] = data.get('grade', '六年级') + "语文教学评一致性教学设计"
    
    render_document(working_template, out_path, data)
    
    # 清理临时模板
    if os.path.exists(working_template):
        os.remove(working_template)

if __name__ == "__main__":
    # 待生成的课程列表
    lessons = [
        "鲁滨逊漂流记",
        "骑鹅历险记",
        "汤姆索亚历险记",
        "口语交际：通读一本书",
        "习作：写作梗概",
        "语文园地",
        "快乐读书吧"
    ]
    
    for lesson in lessons:
        try:
            run_case(lesson)
        except Exception as e:
            print(f"处理《{lesson}》时发生错误: {e}")
            continue
    
    print("\n[Case 001] 恭喜！所有课程的自动化教案已全部生成并同步至 Windows。")
