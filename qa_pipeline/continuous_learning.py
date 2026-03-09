import os
import json
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "history_intent.json"

def load_lessons_learned() -> list:
    """读取历史错误教训作为强化学习记忆"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Continuous Learning] 读取记忆库失败: {e}")
    return []

def save_lesson_learned(intent: str):
    """保存新学习到的用户意图/错误教训"""
    lessons = load_lessons_learned()
    if intent not in lessons:
        lessons.append(intent)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(lessons, f, ensure_ascii=False, indent=2)
        print(f"🧠 [强化学习] 新意图已永久存入记忆库: {intent}")

def get_learning_context() -> str:
    """生成给大模型的记忆上下文"""
    lessons = load_lessons_learned()
    if not lessons:
        return ""
    
    context = "\n【⚠️ 历史严重错误教训（请绝对避免再犯）】:\n"
    for i, lesson in enumerate(lessons, 1):
        context += f"{i}. {lesson}\n"
    return context
