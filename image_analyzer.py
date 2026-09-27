"""
image_analyzer.py
Wash Friends Vietnam - Stain / Care-label Photo Analyzer

Uses GPT-4o-mini Vision. Returns GraphRAG entities for stains, or structured
care-label fields. Low-confidence stain photos trigger clarify + label request.
"""

from __future__ import annotations

import os
import base64
import json
import re
from urllib.request import urlopen, Request

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

VISION_PROMPT = """You are a laundry expert AI for Wash Friends franchise owners.

Decide what the photo is, then fill JSON only (no markdown).

image_kind:
- "care_label" = clothing care/composition tag with wash symbols or fiber %
- "stain_photo" = garment/fabric with a stain or soiling
- "other" = neither

If image_kind is "stain_photo":
{
  "image_kind": "stain_photo",
  "stain_type": "coffee|blood|oil|grass|wine|ink|rust|makeup|mud|unknown",
  "fabric_type": "cotton|silk|polyester|wool|denim|linen|unknown",
  "severity": "light|medium|heavy",
  "characteristics": ["dried|fresh", "..."],
  "confidence": "high|medium|low",
  "care_notes": "brief",
  "stain_color": "red|yellow|brown|black|blue|green|white|null",
  "lang": "vi"
}
If fabric or stain is unclear, set confidence to "low".

If image_kind is "care_label":
{
  "image_kind": "care_label",
  "fiber_text": "as printed on label",
  "fabric_type": "cotton|silk|polyester|wool|denim|linen|blend|unknown",
  "wash": {"allowed": true, "max_temp_c": 40, "hand_wash_only": false, "gentle": false, "do_not_wash": false},
  "bleach": {"allowed": false, "oxygen_only": false, "do_not_bleach": true},
  "dry": {"tumble_ok": false, "low_heat": false, "shade": true, "flat_dry": false, "do_not_tumble": true},
  "iron": {"allowed": true, "max_temp_c": 150, "no_steam": false, "do_not_iron": false},
  "dry_clean": {"allowed": false, "code": "", "do_not_dry_clean": false},
  "confidence": "high|medium|low",
  "notes": "VN label may be wrong — note uncertainty",
  "lang": "vi"
}

If image_kind is "other":
{"image_kind": "other", "confidence": "low", "notes": "...", "lang": "vi"}
"""


def fetch_image_as_base64(url):
    """Download an image from a URL and return (base64_data, media_type)."""
    headers = {
        "User-Agent": "WashFriendsBot/1.0",
        "Accept": "image/*",
    }
    req = Request(url, headers=headers)
    with urlopen(req, timeout=10) as resp:
        content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        data = resp.read()
    return base64.standard_b64encode(data).decode("utf-8"), content_type


def _detect_lang(caption: str, fallback: str = "vi") -> str:
    try:
        from reply_lang import detect_reply_lang
        if caption and str(caption).strip():
            return detect_reply_lang(caption)
    except Exception:
        pass
    if caption and re.search(r"[가-힣]", caption):
        return "ko"
    return fallback or "vi"


def _parse_vision_json(raw: str) -> dict:
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        return {}
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return {}


def _vision_call(image_base64: str, media_type: str, user_caption: str = "") -> dict:
    prompt_text = VISION_PROMPT
    if user_caption:
        prompt_text += f"\n\nUser caption/hint: {user_caption}"

    message = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=700,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_base64}",
                        },
                    },
                    {"type": "text", "text": prompt_text},
                ],
            }
        ],
    )
    raw = message.choices[0].message.content.strip()
    parsed = _parse_vision_json(raw)
    if not parsed:
        return {
            "image_kind": "other",
            "confidence": "low",
            "notes": raw[:200],
            "lang": _detect_lang(user_caption),
        }
    if not parsed.get("lang"):
        parsed["lang"] = _detect_lang(user_caption)
    return parsed


def _to_graphrag_entities(analysis: dict, user_caption: str = "") -> dict:
    """Normalize vision stain output into graphrag_engine entity shape."""
    stain = analysis.get("stain_type") or None
    fabric = analysis.get("fabric_type") or None
    if stain in ("unknown", "", "null"):
        stain = None
    if fabric in ("unknown", "", "null"):
        fabric = None

    caption = (user_caption or "").strip()
    confidence = analysis.get("confidence", "low")

    # Map vision enum → stable graph stain_id (SOP route)
    _VISION_STAIN_ID = {
        "coffee": "S_BLACK_COFFEE",
        "ca phe": "S_BLACK_COFFEE",
        "blood": "S_BLOOD_FRESH",
        "mau": "S_BLOOD_FRESH",
        "oil": "S_COOKING_OIL",
        "dau": "S_COOKING_OIL",
        "grease": "S_GREASE",
        "grass": "S_GRASS",
        "co xanh": "S_GRASS",
        "wine": "S_RED_WINE",
        "ruou": "S_RED_WINE",
        "ink": "S_INK_PEN",
        "muc": "S_INK_PEN",
        "rust": "S_RUST",
        "ri set": "S_RUST",
        "makeup": "S_FOUNDATION",
        "foundation": "S_FOUNDATION",
        "lipstick": "S_LIPSTICK",
        "mud": "S_MUD",
        "bun": "S_MUD",
    }
    stain_id = None
    if stain:
        key = str(stain).strip().lower()
        stain_id = _VISION_STAIN_ID.get(key)
        if not stain_id:
            for k, sid in _VISION_STAIN_ID.items():
                if k in key:
                    stain_id = sid
                    break

    return {
        "stain_type": stain,
        "fabric_type": fabric,
        "intent": "mystery" if not stain else "treatment",
        "hours_since": None,
        "stain_color": analysis.get("stain_color")
        if analysis.get("stain_color") not in (None, "null")
        else None,
        "smell": None,
        "water_spreads": None,
        "group_id": None,
        "stain_id": stain_id,
        "attempt_number": None,
        "lang": analysis.get("lang") or _detect_lang(caption),
        "severity": analysis.get("severity", "medium"),
        "characteristics": analysis.get("characteristics") or [],
        "confidence": confidence,
        "care_notes": analysis.get("care_notes") or "",
        "image_kind": analysis.get("image_kind") or "stain_photo",
        "_image_analysis": True,
        "_user_caption": caption,
        "_raw": caption,
    }


def needs_clarification(entities: dict) -> bool:
    """True when owner should be asked for fabric/stain details and/or care label photo."""
    if not entities:
        return True
    conf = str(entities.get("confidence") or "low").lower()
    stain = entities.get("stain_type")
    fabric = entities.get("fabric_type")
    if conf == "low":
        return True
    if not stain or not fabric:
        return True
    if conf == "medium" and (not stain or not fabric):
        return True
    return False


def build_clarify_and_label_request(entities: dict | None = None, lang: str = "vi") -> str:
    """Ask follow-ups + request a care-label photo (KO/VI)."""
    entities = entities or {}
    lang = lang or entities.get("lang") or "vi"
    stain = entities.get("stain_type") or ""
    fabric = entities.get("fabric_type") or ""

    if lang == "ko":
        parts = [
            "사진만으로는 확정이 어렵습니다. 정확한 세탁법을 위해 알려주세요.",
            "",
            "1) 어떤 오염인가요? (예: 피, 커피, 기름, 흙)",
            "2) 원단은 무엇인가요? (예: 면, 폴리, 실크, 울, 데님)",
            "3) 가능하면 옷 안의 케어 라벨(세탁기호·혼용률) 사진을 보내 주세요.",
            "   라벨을 보면 수온·표백·건조·다림질을 더 정확히 안내할 수 있습니다.",
        ]
        if stain or fabric:
            parts.append("")
            parts.append(f"(참고 추정: 오염={stain or '?'}, 원단={fabric or '?'})")
        return "\n".join(parts)

    parts = [
        "Anh chua du ro de ket luan. De huong dan chinh xac, vui long cho biet:",
        "",
        "1) Loai vet ban? (mau, ca phe, dau, bun, ...)",
        "2) Chat lieu vai? (cotton, polyester, lua, len, denim, ...)",
        "3) Neu co, chup anh NHAN GIAT (ky hieu + thanh phan soi) gui them.",
        "   Nhan giup xac dinh nhiet do / tay / say / ui an toan hon.",
    ]
    if stain or fabric:
        parts.append("")
        parts.append(f"(Uoc luong tam: vet={stain or '?'}, vai={fabric or '?'})")
    return "\n".join(parts)


def format_care_label_reply(
    label: dict,
    *,
    lang: str = "vi",
    pending: dict | None = None,
    dry_clean_machine: bool | None = None,
) -> str:
    """Owner-facing care guidance from a parsed care label (no folk tips)."""
    lang = lang or label.get("lang") or "vi"
    conf = str(label.get("confidence") or "low").lower()
    fiber = label.get("fiber_text") or label.get("fabric_type") or ""
    wash = label.get("wash") or {}
    bleach = label.get("bleach") or {}
    dry = label.get("dry") or {}
    iron = label.get("iron") or {}
    dc = label.get("dry_clean") or {}
    notes = label.get("notes") or ""

    if lang == "ko":
        lines = ["케어 라벨 판독 결과입니다. (라벨 오표기 가능 → 고가·민감은 Cap1·표백 보류 후 확인·조정.)", ""]
        if fiber:
            lines.append(f"1) 조성/표기: {fiber}")
        # wash
        if wash.get("do_not_wash"):
            lines.append("2) 세탁: 물세탁 금지 → 전문 케어(드라이) 기준")
        elif wash.get("hand_wash_only"):
            temp = wash.get("max_temp_c") or 30
            lines.append(f"2) 세탁: 손세탁만, 최대 약 {temp}°C" + (" · 약하게" if wash.get("gentle") else ""))
        elif wash.get("allowed", True):
            temp = wash.get("max_temp_c")
            t = f"최대 약 {temp}°C" if temp else "라벨 수온 준수"
            g = " · 약코스" if wash.get("gentle") else ""
            lines.append(f"2) 세탁: 가능 · {t}{g}")
        else:
            lines.append("2) 세탁: 라벨 불명확 → 찬물·약하게 또는 전문 케어 확인")
        # bleach
        if bleach.get("do_not_bleach") or bleach.get("allowed") is False:
            if bleach.get("oxygen_only"):
                lines.append("3) 표백: 산소계만 가능 (염소계 금지)")
            else:
                lines.append("3) 표백: 금지")
        elif bleach.get("oxygen_only"):
            lines.append("3) 표백: 산소계만")
        elif bleach.get("allowed"):
            lines.append("3) 표백: 가능 (원단 색상 확인 후)")
        else:
            lines.append("3) 표백: 불명확 → 표백 금지로 처리")
        # dry
        if dry.get("do_not_tumble") or dry.get("tumble_ok") is False:
            shade = " · 그늘 건조 권장" if dry.get("shade") else ""
            flat = " · 뉘어 건조" if dry.get("flat_dry") else ""
            lines.append(f"4) 건조: 기계 건조 금지{shade}{flat}")
        elif dry.get("tumble_ok"):
            heat = "저온" if dry.get("low_heat") else "라벨 열 설정"
            lines.append(f"4) 건조: 기계 가능 ({heat})")
        else:
            lines.append("4) 건조: 그늘·통풍 우선")
        # iron
        if iron.get("do_not_iron") or iron.get("allowed") is False:
            lines.append("5) 다림질: 금지")
        elif iron.get("allowed", True):
            t = iron.get("max_temp_c")
            steam = " · 스팀 금지" if iron.get("no_steam") else ""
            lines.append(f"5) 다림질: 가능" + (f" · 최대 약 {t}°C" if t else "") + steam)
        else:
            lines.append("5) 다림질: 낮은 온도부터 테스트")
        # dry clean
        if dc.get("do_not_dry_clean"):
            lines.append("6) 드라이클리닝: 금지")
        elif dc.get("allowed"):
            code = dc.get("code") or ""
            lines.append(f"6) 드라이클리닝(전문 케어): 가능" + (f" ({code})" if code else ""))
        elif wash.get("do_not_wash"):
            lines.append("6) 전문 케어: 물세탁 금지 → 드라이/전문 기준 확인")
        if pending and (pending.get("stain_guess") or pending.get("caption")):
            lines.append("")
            lines.append(
                f"오염 참고: {pending.get('stain_guess') or pending.get('caption') or '?'} "
                f"— 얼룩 처리는 라벨 한도 안에서 진행하세요."
            )
        if conf == "low" or notes:
            lines.append("")
            lines.append("라벨이 흐리거나 VN 위조·오표기 가능 → 확정 안 되면 더 약한 조건(찬물·손세탁·표백 금지)으로.")
        if notes:
            lines.append(f"메모: {notes}")
        out = "\n".join(lines)
    else:
        # Vietnamese (default) / English share VI-style structure; EN via lang==en below
        if lang == "en":
            lines = [
                "Care-label reading (VN labels may be wrong — for expensive/sensitive items use safer settings).",
                "",
            ]
            if fiber:
                lines.append(f"1) Fiber: {fiber}")
            if wash.get("do_not_wash"):
                lines.append("2) Wash: do not wash in water → professional care")
            elif wash.get("hand_wash_only"):
                temp = wash.get("max_temp_c") or 30
                lines.append(f"2) Wash: hand only, max ~{temp}C" + (" · gentle" if wash.get("gentle") else ""))
            elif wash.get("allowed", True):
                temp = wash.get("max_temp_c")
                t = f"max ~{temp}C" if temp else "follow label temp"
                g = " · delicate" if wash.get("gentle") else ""
                lines.append(f"2) Wash: OK · {t}{g}")
            else:
                lines.append("2) Wash: unclear → prefer cold + gentle")
            if bleach.get("do_not_bleach") or bleach.get("allowed") is False:
                if bleach.get("oxygen_only"):
                    lines.append("3) Bleach: oxygen only (no chlorine)")
                else:
                    lines.append("3) Bleach: forbidden")
            elif bleach.get("oxygen_only"):
                lines.append("3) Bleach: oxygen only")
            elif bleach.get("allowed"):
                lines.append("3) Bleach: OK (check color)")
            else:
                lines.append("3) Bleach: unclear → treat as no bleach")
            if dry.get("do_not_tumble") or dry.get("tumble_ok") is False:
                shade = " · shade dry" if dry.get("shade") else ""
                flat = " · flat dry" if dry.get("flat_dry") else ""
                lines.append(f"4) Dry: no tumble{shade}{flat}")
            elif dry.get("tumble_ok"):
                heat = "low heat" if dry.get("low_heat") else "per label"
                lines.append(f"4) Dry: tumble OK ({heat})")
            else:
                lines.append("4) Dry: air dry preferred")
            if iron.get("do_not_iron") or iron.get("allowed") is False:
                lines.append("5) Iron: forbidden")
            elif iron.get("allowed", True):
                t = iron.get("max_temp_c")
                steam = " · no steam" if iron.get("no_steam") else ""
                lines.append(f"5) Iron: OK" + (f" · max ~{t}C" if t else "") + steam)
            else:
                lines.append("5) Iron: start low + test")
            if dc.get("do_not_dry_clean"):
                lines.append("6) Dry-clean: forbidden")
            elif dc.get("allowed"):
                code = dc.get("code") or ""
                lines.append(f"6) Dry-clean (professional): OK" + (f" ({code})" if code else ""))
            elif wash.get("do_not_wash"):
                lines.append("6) Professional care: no water wash — confirm dry-clean path")
            if pending and (pending.get("stain_guess") or pending.get("caption")):
                lines.append("")
                lines.append(
                    f"Stain note: {pending.get('stain_guess') or pending.get('caption') or '?'} "
                    f"— treat stain within label limits."
                )
            if conf == "low" or notes:
                lines.append("")
                lines.append("Blurry/wrong labels happen → if unsure: cold, hand, no strong bleach.")
            if notes:
                lines.append(f"Note: {notes}")
            out = "\n".join(lines)
        else:
            lines = [
                "Ket qua doc NHAN GIAT (chu y: nhan VN co the sai — do dat/nhay cam thi xu ly an toan hon).",
                "",
            ]
            if fiber:
                lines.append(f"1) Thanh phan: {fiber}")
            if wash.get("do_not_wash"):
                lines.append("2) Giat: CAM giat nuoc → cham soc chuyen nghiep")
            elif wash.get("hand_wash_only"):
                temp = wash.get("max_temp_c") or 30
                lines.append(f"2) Giat: CHI tay, toi da ~{temp}C" + (" · nhe" if wash.get("gentle") else ""))
            elif wash.get("allowed", True):
                temp = wash.get("max_temp_c")
                t = f"toi da ~{temp}C" if temp else "theo nhiet nhan"
                g = " · chuong trinh nhe" if wash.get("gentle") else ""
                lines.append(f"2) Giat: duoc · {t}{g}")
            else:
                lines.append("2) Giat: khong ro → uu tien lanh + nhe")
            if bleach.get("do_not_bleach") or bleach.get("allowed") is False:
                if bleach.get("oxygen_only"):
                    lines.append("3) Tay: chi oxy (CAM chlorine)")
                else:
                    lines.append("3) Tay: CAM")
            elif bleach.get("oxygen_only"):
                lines.append("3) Tay: chi oxy")
            elif bleach.get("allowed"):
                lines.append("3) Tay: duoc (kiem tra mau)")
            else:
                lines.append("3) Tay: khong ro → CAM tay")
            if dry.get("do_not_tumble") or dry.get("tumble_ok") is False:
                shade = " · phoi bong mat" if dry.get("shade") else ""
                flat = " · phoi phang" if dry.get("flat_dry") else ""
                lines.append(f"4) Say: CAM may{shade}{flat}")
            elif dry.get("tumble_ok"):
                heat = "nhiet thap" if dry.get("low_heat") else "theo nhan"
                lines.append(f"4) Say: may duoc ({heat})")
            else:
                lines.append("4) Say: uu tien bong mat / thoang")
            if iron.get("do_not_iron") or iron.get("allowed") is False:
                lines.append("5) Ui: CAM")
            elif iron.get("allowed", True):
                t = iron.get("max_temp_c")
                steam = " · CAM hoi" if iron.get("no_steam") else ""
                lines.append(f"5) Ui: duoc" + (f" · toi da ~{t}C" if t else "") + steam)
            else:
                lines.append("5) Ui: nhiet thap + test")
            if dc.get("do_not_dry_clean"):
                lines.append("6) Dry-clean: CAM")
            elif dc.get("allowed"):
                code = dc.get("code") or ""
                lines.append(f"6) Dry-clean (chuyen nghiep): duoc" + (f" ({code})" if code else ""))
            elif wash.get("do_not_wash"):
                lines.append("6) Cham soc chuyen nghiep: cam giat nuoc — xac nhan dry-clean")
            if pending and (pending.get("stain_guess") or pending.get("caption")):
                lines.append("")
                lines.append(
                    f"Vet tham khao: {pending.get('stain_guess') or pending.get('caption') or '?'} "
                    f"— xu ly vet trong gioi han nhan."
                )
            if conf == "low" or notes:
                lines.append("")
                lines.append("Nhan mo/sai co the xay ra → neu khong chac: lanh, tay, CAM tay hoa chat manh.")
            if notes:
                lines.append(f"Ghi chu: {notes}")
            out = "\n".join(lines)

    # Wet shop actions (ISO mapping) — never invent dry PROG numbers
    try:
        from care_label_iso3758 import needs_professional_care, professional_code, wet_action_lines

        acts = wet_action_lines(label, lang=lang if lang in {"ko", "vi", "en"} else "vi")
        if acts:
            if lang == "ko":
                out += "\n\n▶ 점주 액션(습식·한도)\n" + "\n".join(acts)
            elif lang == "en":
                out += "\n\n▶ Shop actions (wet / limits)\n" + "\n".join(acts)
            else:
                out += "\n\n▶ Hanh dong (uot / gioi han)\n" + "\n".join(acts)
        if needs_professional_care(label):
            from dry_clean_capability import lock_message, unlock_message

            has_m = bool(dry_clean_machine) if dry_clean_machine is not None else False
            code = professional_code(label)
            block = unlock_message(lang, code=code) if has_m else lock_message(lang)
            out += "\n\n" + block
    except Exception as e:
        print(f"[CARE_LABEL] enrich skip: {e}")

    return out


def analyze_image(image_url=None, image_base64=None, media_type="image/jpeg", user_caption=""):
    """
    Unified entry: returns dict with image_kind stain_photo | care_label | other.
    For stain_photo also includes GraphRAG-ready entity fields.
    """
    if image_url and not image_base64:
        image_base64, media_type = fetch_image_as_base64(image_url)

    if not image_base64:
        return _to_graphrag_entities(
            {
                "image_kind": "other",
                "stain_type": "unknown",
                "fabric_type": "unknown",
                "severity": "medium",
                "characteristics": [],
                "confidence": "low",
                "care_notes": "No image provided",
            },
            user_caption=user_caption,
        )

    parsed = _vision_call(image_base64, media_type, user_caption=user_caption)
    kind = parsed.get("image_kind") or "stain_photo"

    if kind == "care_label":
        parsed["image_kind"] = "care_label"
        parsed["_user_caption"] = user_caption or ""
        return parsed

    if kind == "other":
        ent = _to_graphrag_entities(
            {
                "image_kind": "other",
                "stain_type": "unknown",
                "fabric_type": "unknown",
                "confidence": "low",
                "care_notes": parsed.get("notes") or "Unrecognized image",
                "lang": parsed.get("lang"),
            },
            user_caption=user_caption,
        )
        ent["image_kind"] = "other"
        return ent

    ent = _to_graphrag_entities(parsed, user_caption=user_caption)
    ent["image_kind"] = "stain_photo"
    return ent


def analyze_stain_image(image_url=None, image_base64=None, media_type="image/jpeg", user_caption=""):
    """Backward-compatible: always return GraphRAG entity dict (stain path)."""
    result = analyze_image(
        image_url=image_url,
        image_base64=image_base64,
        media_type=media_type,
        user_caption=user_caption,
    )
    if result.get("image_kind") == "care_label":
        # Caller should use analyze_image; coerce to low-confidence stain ask
        return _to_graphrag_entities(
            {
                "image_kind": "care_label",
                "stain_type": "unknown",
                "fabric_type": result.get("fabric_type") or "unknown",
                "confidence": "low",
                "care_notes": "Care label photo received",
                "lang": result.get("lang"),
            },
            user_caption=user_caption,
        )
    return result


def build_image_entity_context(analysis):
    """Convert image analysis result into text prefix for GraphRAG LLM."""
    stain = analysis.get("stain_type") or "unknown"
    fabric = analysis.get("fabric_type") or "unknown"
    severity = analysis.get("severity", "medium")
    chars = analysis.get("characteristics", [])
    notes = analysis.get("care_notes", "")
    caption = analysis.get("_user_caption", "")
    conf = analysis.get("confidence", "")

    parts = [
        f"Anh phan tich: loai vet={stain}",
        f"vai={fabric}",
        f"muc do={severity}",
        f"confidence={conf}",
    ]
    if chars:
        parts.append("dac diem: " + ", ".join(str(c) for c in chars))
    if notes:
        parts.append("ghi chu: " + notes)
    if caption:
        parts.append("chu thich nguoi dung: " + caption)

    return " | ".join(parts)


# backward-compatibility alias used by zalo_handler and facebook_handler
build_image_context_prefix = build_image_entity_context
