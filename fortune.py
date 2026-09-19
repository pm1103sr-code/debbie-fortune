from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

try:
    from lunar_python import Solar
except ImportError:
    Solar = None

try:
    from x_iztro import Astro
except ImportError:
    Astro = None

@dataclass
class BaziResult:
    solar_datetime: str
    lunar_text: str
    year_pillar: str
    month_pillar: str
    day_pillar: str
    time_pillar: str
    note: str = "四柱由 lunar-python 曆法引擎計算；十神、旺衰與八字格局可於後續版本依選定流派擴充。"


def calculate_bazi(dt: datetime) -> dict[str, Any]:
    if Solar is None:
        raise RuntimeError("尚未安裝 lunar-python，請先 pip install -r requirements.txt")
    solar = Solar.fromYmdHms(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    return asdict(BaziResult(
        solar_datetime=dt.isoformat(sep=" ", timespec="minutes"),
        lunar_text=lunar.toString(),
        year_pillar=ec.getYear(), month_pillar=ec.getMonth(),
        day_pillar=ec.getDay(), time_pillar=ec.getTime(),
    ))


def _ziwei_time_index(dt: datetime) -> int:
    """x-iztro: 0=早子(00-01), 1=丑(01-03)...11=亥(21-23), 12=晚子(23-24)."""
    h = dt.hour
    if h == 23:
        return 12
    if h == 0:
        return 0
    return (h + 1) // 2


def _star_text(star: Any) -> str:
    name = getattr(star, "name", None) or getattr(star, "key", None) or str(star)
    mutagen = getattr(star, "mutagen", None)
    brightness = getattr(star, "brightness", None)
    extras = [str(x) for x in (brightness, mutagen) if x]
    return f"{name}（{'、'.join(extras)}）" if extras else str(name)


def calculate_ziwei(dt: datetime, gender_zh: str) -> dict[str, Any]:
    if Astro is None:
        raise RuntimeError("尚未安裝 x-iztro，請先執行 pip install x-iztro")
    if gender_zh not in ("女", "男"):
        raise ValueError("紫微斗數排盤需要選擇『女』或『男』，以決定大限等傳統排盤方向。")

    gender = "female" if gender_zh == "女" else "male"
    solar_date = f"{dt.year}-{dt.month}-{dt.day}"
    chart = Astro().by_solar(solar_date, _ziwei_time_index(dt), gender, language="zh-CN")

    palaces = []
    ming_gong = ""
    shen_gong = ""
    for p in chart.palaces:
        name = str(getattr(p, "name", ""))
        is_body = bool(getattr(p, "is_body_palace", False))
        if "命" in name:
            ming_gong = name
        if is_body:
            shen_gong = name
        palaces.append({
            "name": name,
            "stem_branch": f"{getattr(p, 'heavenly_stem', '')}{getattr(p, 'earthly_branch', '')}",
            "is_body_palace": is_body,
            "major_stars": [_star_text(s) for s in getattr(p, "major_stars", [])],
            "minor_stars": [_star_text(s) for s in getattr(p, "minor_stars", [])],
            "adjective_stars": [_star_text(s) for s in getattr(p, "adjective_stars", [])],
            "decadal": str(getattr(p, "decadal", "")),
        })

    patterns = []
    for hit in chart.patterns():
        patterns.append({
            "name": str(getattr(hit, "name", "")),
            "palace": str(getattr(hit, "palace_name", "")),
            "variant": str(getattr(hit, "variant", "") or ""),
            "broken": bool(getattr(hit, "broken", False)),
        })

    return {
        "status": "complete",
        "solar_date": str(chart.solar_date),
        "lunar_date": str(chart.lunar_date),
        "chinese_date": str(chart.chinese_date),
        "time": str(chart.time),
        "time_range": str(chart.time_range),
        "zodiac": str(chart.zodiac),
        "sign": str(chart.sign),
        "soul_star": str(chart.soul),
        "body_star": str(chart.body),
        "five_elements_class": str(chart.five_elements_class),
        "ming_gong": ming_gong,
        "shen_gong": shen_gong,
        "palaces": palaces,
        "patterns": patterns,
        "patterns_text": chart.patterns_to_text(),
        "semantic_text": chart.to_text(),
        "rules_note": "x-iztro 預設 ChartConfig；公曆輸入、fix_leap=True、zh-CN。出生時間目前依使用者輸入的當地民用時間換算時辰，尚未校正真太陽時。",
    }
