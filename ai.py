from __future__ import annotations
import io, json
from typing import Optional
from PIL import Image
from google import genai
from google.genai import types
from config import GEMINI_MODEL, SYSTEM_PROMPT


def image_to_part(uploaded_file) -> Optional[types.Part]:
    if uploaded_file is None:
        return None
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((1400, 1400))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")


def analyze(api_key: str, user: dict, bazi: dict, ziwei: dict, face=None, left_palm=None, right_palm=None) -> str:
    client = genai.Client(api_key=api_key)
    prompt = SYSTEM_PROMPT + "\n\n使用者資料：\n" + json.dumps(user, ensure_ascii=False, indent=2)
    prompt += "\n\nPython 八字計算結果：\n" + json.dumps(bazi, ensure_ascii=False, indent=2)
    ziwei_for_ai = {k: v for k, v in ziwei.items() if k != "semantic_text"}
    prompt += "\n\nPython 紫微斗數正式排盤資料：\n" + json.dumps(ziwei_for_ai, ensure_ascii=False, indent=2)
    prompt += "\n\n紫微排盤引擎語義資料（以此為事實基礎，不得自行改星曜或格局）：\n" + ziwei.get("semantic_text", "")

    contents = [prompt]
    for label, f in [("面相正面照片", face), ("左手掌照片", left_palm), ("右手掌照片", right_palm)]:
        part = image_to_part(f)
        if part:
            contents.extend([f"以下是{label}：", part])

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(thinking_config=types.ThinkingConfig(thinking_level="medium")),
    )
    return response.text or "Gemini 未回傳文字結果。"
