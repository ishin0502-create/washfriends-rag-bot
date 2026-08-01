"""
image_analyzer.py
Wash Friends Vietnam â€” Stain Photo Analyzer

Analyzes a stain photo using Claude Vision and returns structured entities
compatible with the graphrag_engine pipeline.

Supported inputs:
  - Image URL (from Zalo / Facebook CDN)
  - Base64-encoded image bytes

Returns the same entity dict format as entity_extractor.py,
so the rest of the pipeline is unchanged.
"""

import os
import base64
import re
from typing import Optional
from urllib.request import urlopen, Request

from anthropic import Anthropic

_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

VISION_SYSTEM = """Báº¡n lÃ  chuyÃªn gia giáº·t á»§i cá»§a Wash Friends Vietnam vá»›i kinh nghiá»‡m 20 nÄƒm.
Nhiá»‡m vá»¥: PhÃ¢n tÃ­ch áº£nh váº¿t báº©n vÃ  tráº£ lá»i báº±ng JSON.

Tráº£ lá»i ONLY valid JSON, khÃ´ng thÃªm text nÃ o khÃ¡c.

JSON schema:
{
  "stain_type": "tÃªn váº¿t báº©n báº±ng tiáº¿ng Viá»‡t (vÃ­ dá»¥: váº¿t dáº§u Äƒn, váº¿t mÃ¡u, váº¿t cÃ  phÃª)",
  "stain_type_ko": "tÃªn váº¿t báº©n báº±ng tiáº¿ng HÃ n (vÃ­ dá»¥: ê¸°ë¦„, í˜ˆì•¡, ì»¤í”¼)",
  "stain_color": "red|yellow|brown|black|blue|green|white|mixed",
  "fabric_type": "loáº¡i váº£i náº¿u cÃ³ thá»ƒ nhÃ¬n tháº¥y (lá»¥a/cotton/wool/synthetic/unknown)",
  "group_id": "group_oil|group_tannin|group_protein|group_dye|group_special|unknown",
  "estimated_age": "fresh (< 2 giá»)|dry (2-24 giá»)|old (> 24 giá»)|unknown",
  "severity": "light|medium|heavy",
  "confidence": "high|medium|low",
  "visible_chemicals": "dáº¥u hiá»‡u Ä‘áº·c biá»‡t nhÆ° mÃ¹i/káº¿t cáº¥u (mÃ´ táº£ ngáº¯n hoáº·c null)",
  "diagnosis_vi": "cháº©n Ä‘oÃ¡n tÃ³m táº¯t báº±ng tiáº¿ng Viá»‡t (1-2 cÃ¢u)",
  "diagnosis_ko": "cháº©n Ä‘oÃ¡n tÃ³m táº¯t báº±ng tiáº¿ng HÃ n (1-2 cÃ¢u)"
}

Quy táº¯c phÃ¢n tÃ­ch:
- MÃ u Ä‘á»/nÃ¢u Ä‘á» â†’ cÃ³ thá»ƒ protein (mÃ¡u, nÆ°á»›c máº¯m, nÆ°á»›c sá»‘t)
- MÃ u vÃ ng/nÃ¢u â†’ dáº§u hoáº·c tannin (cÃ  phÃª, trÃ , dáº§u Äƒn)
- Trong suá»‘t/loang dáº§u â†’ nhÃ³m dáº§u (group_oil)
- MÃ u xanh/Ä‘en Ä‘áº­m â†’ má»±c hoáº·c thuá»‘c nhuá»™m (group_dye)
- Váº¿t trÃ²n lan rá»™ng â†’ gá»‘c nÆ°á»›c (tannin/protein)
- Váº¿t khÃ´ng lan/bÃ³ng â†’ gá»‘c dáº§u
- Náº¿u khÃ´ng cháº¯c â†’ confidence: "low" vÃ  mÃ´ táº£ rÆ° nhá»¯ng gÃ¬ nhÃ¬n tháº¥y"""


def _fetch_image_as_b64(url: str) -> Optional[tuple[str, str]]:
    """
    Download image from URL â†’ return (base64_string, media_type).
    Returns None on failure.
    """
    try:
        req = Request(url, headers={"User-Agent": "WashFriendsBot/1.0"})
        with urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            # Normalize media type
            if "png" in content_type:
                media_type = "image/png"
            elif "gif" in content_type:
                media_type = "image/gif"
            elif "webp" in content_type:
                media_type = "image/webp"
            else:
                media_type = "image/jpeg"

            raw = resp.read()
            return base64.standard_b64encode(raw).decode("utf-8"), media_type
    except Exception as e:
        print(f"[IMAGE FETCH ERROR] {url}: {e}")
        return None


def analyze_stain_image(
    image_url: Optional[str] = None,
    image_b64: Optional[str] = None,
    media_type: str = "image/jpeg",
    user_caption: str = "",
) -> dict:
    """
    Analyze a stain photo and return entity dict for graphrag_engine.

    Args:
        image_url   : Direct URL to image (Zalo/FB CDN)
        image_b64   : Base64-encoded image (alternative to URL)
        media_type  : MIME type (image/jpeg, image/png, etc.)
        user_caption: Any text the user sent alongside the photo

    Returns:
        Entity dict compatible with graphrag_engine._fetch_graph_context()
        Falls back to a "mystery" intent dict on failure.
    """
    # Resolve image source
    b64_data = image_b64
    if not b64_data and image_url:
        result = _fetch_image_as_b64(image_url)
        if result:
            b64_data, media_type = result

    if not b64_data:
        return _image_fallback(user_caption)

    # Build prompt with optional user caption
    user_prompt = "PhÃ¢n tÃ­ch váº¿t báº©n trong áº£nh nÃ y."
    if user_caption.strip():
        user_prompt += f" KhÃ¡ch hÃ ng nÃ³i: \"{î±êİ\—ØØ\[Û‹œİš\

_Wˆ‚‚ˆN‚ˆ™\ÜÛœÙHHØÛY[›Y\ÜØYÙ\Ë˜Ü™X]Jˆ[Ù[H˜Û]YK\ÛÛ›™]MMH‹Èš\Ú[Ûˆİ\ÜˆX^İÚÙ[œÏMLL‹ˆŞ\İ[OU’TÒSÓ—ÔÖTÕSKˆY\ÜØYÙ\ÏVÂˆÂˆœ›ÛHˆ\Ù\ˆ‹ˆ˜ÛÛ[ˆÂˆÂˆ\Hˆš[XYÙH‹ˆœÛİ\˜ÙHˆÂˆ\Hˆ˜˜\ÙM‹ˆ›YYXWİ\HˆYYXWİ\Kˆ™]HˆÙ]KˆKˆKˆÈ\Hˆ^‹^ˆ\Ù\—Ü›Û\KˆKˆBˆKˆ
B‚ˆ˜]ÈH™\ÜÛœÙK˜ÛÛ[ÌK^œİš\

BˆÈİš\X\šÙİÛˆ™[˜Ù\Âˆ˜]ÈH™KœİXŠˆ—˜
ÎšœÛÛŠO×Êˆ‹ˆ‹˜]ÊBˆ˜]ÈH™KœİXŠˆ—Ê˜	‹ˆ‹˜]ÊB‚ˆ[\ÜœÛÛ‚ˆ[˜[\Ú\ÈHœÛÛ‹›ØYÊ˜]ÊB‚ˆÈX\ÈÜ˜\˜Y×Ù[™Ú[™H[]H›Ü›X]ˆ™]\›ˆØ[˜[\Ú\×İ×Ù[]Y\Ê[˜[\Ú\Ë\Ù\—ØØ\[ÛŠB‚ˆ^Ù\^Ù\[Ûˆ\ÈN‚ˆš[
ˆ–ÒSPQÑHSSTÒTÈT”“Ô—HÙ_HŠBˆ™]\›ˆÚ[XYÙWÙ˜[˜XÚÊ\Ù\—ØØ\[ÛŠB‚‚™YˆØ[˜[\Ú\×İ×Ù[]Y\Ê[˜[\Ú\ÎˆXİ\Ù\—ØØ\[ÛˆİŠHOˆXİ‚ˆˆˆÛÛ™\š\Ú[Ûˆ[˜[\Ú\ÈXİÈÜ˜\˜Y×Ù[™Ú[™H[]H›Ü›X]ˆˆˆ‚ˆÈX\\İ[X]YØYÙH8¡¤ˆİ\œ×ÜÚ[˜ÙBˆYÙWÛX\HÈ™œ™\ÚˆKŒ™HˆL‹Œ›ÛˆŒ[šÛ›İÛˆˆŒBˆİ\œÈHYÙWÛX\™Ù]
[˜[\Ú\Ë™Ù]
™\İ[X]YØYÙH‹[šÛ›İÛˆŠKŒ
B‚ˆÈX\˜XœšX×İ\HÈÛÛY][™ÈH[™Ú[™HØ[ˆ\ÙBˆ˜XœšXÈH[˜[\Ú\Ë™Ù]
™˜XœšX×İ\H‹[šÛ›İÛˆŠBˆYˆ˜XœšXÈ[ˆ
[šÛ›İÛˆ‹ˆŠN‚ˆ˜XœšXÈH›Û™B‚ˆÈÛÛ™šY[˜ÙKX]Ø\™H[[ˆİÈÛÛ™šY[˜ÙH8¡¤ˆ^\İ\H[ÙBˆÛÛ™šY[˜ÙHH[˜[\Ú\Ë™Ù]
˜ÛÛ™šY[˜ÙH‹›YY][HŠBˆ[[H›^\İ\HˆYˆÛÛ™šY[˜ÙHOH›İÈˆ[ÙH™X]Y[‚‚ˆÈ™Y™\ˆİZ[—İ\WÚÛÈ›ÜˆÛÜ™X[ˆ\Ù\ˆY\ÜØYÙ\ÂˆİZ[—İ\HH[˜[\Ú\Ë™Ù]
œİZ[—İ\HŠHÜˆ[˜[\Ú\Ë™Ù]
œİZ[—İ\WÚÛÈŠHÜˆˆ‚‚ˆ™]\›ˆÂˆœİZ[—İ\HˆİZ[—İ\Kˆ™˜XœšX×İ\Hˆ˜XœšXËˆš[[ˆ[[ˆšİ\œ×ÜÚ[˜ÙHˆİ\œËˆœİZ[—ØÛÛÜˆˆ[˜[\Ú\Ë™Ù]
œİZ[—ØÛÛÜˆŠKˆœÛY[ˆ›Û™KˆØ]\—ÜÜ™XYÈˆ›Û™Kˆ™Ü›İ\ÚYˆ[˜[\Ú\Ë™Ù]
™Ü›İ\ÚYŠHYˆ[˜[\Ú\Ë™Ù]
™Ü›İ\ÚYŠHOH[šÛ›İÛˆˆ[ÙH›Û™KˆœİZ[—ÚYˆ›Û™Kˆ˜][\Û[X™\ˆˆ›Û™Kˆ›[™ÈˆšH‹ˆÈ^˜Hš\Ú[Ûˆ]H
\ÜÙY›İYÚ›ÜˆHÛÛ^
Bˆ—Ú[XYÙWØ[˜[\Ú\ÈˆÂˆ™XYÛ›ÜÚ\×İšHˆ[˜[\Ú\Ë™Ù]
™XYÛ›ÜÚ\×İšH‹ˆŠKˆ™XYÛ›ÜÚ\×ÚÛÈˆ[˜[\Ú\Ë™Ù]
™XYÛ›ÜÚ\×ÚÛÈ‹ˆŠKˆœÙ]™\š]Hˆ[˜[\Ú\Ë™Ù]
œÙ]™\š]H‹›YY][HŠKˆ˜ÛÛ™šY[˜ÙHˆÛÛ™šY[˜ÙKˆ™\İ[X]YØYÙHˆ[˜[\Ú\Ë™Ù]
™\İ[X]YØYÙH‹[šÛ›İÛˆŠKˆKˆB‚‚™YˆÚ[XYÙWÙ˜[˜XÚÊ\Ù\—ØØ\[ÛˆİˆHˆŠHOˆXİ‚ˆˆˆ”ØY™H˜[˜XÚÈÚ[ˆ[XYÙHØ[››İ™H›ØÙ\ÜÙYˆˆˆ‚ˆ™]\›ˆÂˆœİZ[—İ\Hˆ\Ù\—ØØ\[Û–ÎŒLHYˆ\Ù\—ØØ\[Ûˆ[ÙH›Û™Kˆ™˜XœšX×İ\Hˆ›Û™Kˆš[[ˆ›^\İ\H‹ˆšİ\œ×ÜÚ[˜ÙHˆ›Û™KˆœİZ[—ØÛÛÜˆˆ›Û™KˆœÛY[ˆ›Û™KˆØ]\—ÜÜ™XYÈˆ›Û™Kˆ™Ü›İ\ÚYˆ›Û™KˆœİZ[—ÚYˆ›Û™Kˆ˜][\Û[X™\ˆˆ›Û™Kˆ›[™ÈˆšH‹ˆ—Ú[XYÙWØ[˜[\Ú\Èˆ›Û™KˆB‚‚™YˆZ[Ú[XYÙWØÛÛ^Ü™Yš^
[]Y\ÎˆXİ
HOˆİ‚ˆˆˆ‚ˆ™]\›œÈHšY]˜[Y\ÙH™Yš^È™\[™ÈHH›Û\ˆÚ[ˆH]Y\HÜšYÚ[˜]Yœ›ÛH[ˆ[XYÙK‚ˆˆˆ‚ˆ[˜[\Ú\ÈH[]Y\Ë™Ù]
—Ú[XYÙWØ[˜[\Ú\ÈŠBˆYˆ›İ[˜[\Ú\Î‚ˆ™]\›ˆˆ‚‚ˆÛÛ™šY[˜ÙWÛX™[HÂˆšYÚˆÚ8n«ØÈÚ8n«Ûˆ‹ˆ›YY][HˆğìÈ8nàÈ‹ˆ›İÈˆ’0ëˆ8n©^H‹ˆK™Ù]
[˜[\Ú\ÖÈ˜ÛÛ™šY[˜ÙH—KˆŠB‚ˆYÙWÛX™[HÂˆ™œ™\Úˆ˜ğì›ˆ1¬…†¡i (dÆ°á»›i 2 giá»)",
        "dry":     "Ã„°Ã£ khÃ´ (2-24 giá»)",
        "old":     "cæ£´ (hÆ°Ãªn 24 giá»)",
        "unknown": "khÃ´ng xÃ¡c Ä‘á»‹nh Ã„Ñá»£c thá»i gian",
    }.get(analysis["estimated_age"], "")

    severity_label = {
        "light":  "nháº¹",
        "medium": "vá»«a",
        "heavy":  "náº·ng",
    }.get(analysis["severity"], "vá»«a")

    lines = [
        f"ğŸ“¸ PhÃ¢n tÃ­ch áº£nh: {confidence_label} {analysis.get('diagnosis_vi', '')}",
        f"â±ï¸ Váº¿t báº©n {age_label}, má»©c Ä‘á»™ {severity_label}.",
    ]
    return "\n".join(lines) + "\n\n"
