/**
 * Extract Wash Friends KB protocols from laundry_kb_v3_viewer HTML → markdown.
 * Output is franchise-facing: Vietnamese primary, no external source citations.
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const VIEWER =
  process.argv[2] ||
  path.join(process.env.USERPROFILE || "", "Downloads", "laundry_kb_v3_viewer_4.html");
const OUT_DIR = process.argv[3] || path.join(__dirname, "..", "kb");

const FILE_MAP = {
  oil: "laundry_kb_v3_stains_oil.md",
  tannin: "laundry_kb_v3_stains_tannin.md",
  special: "laundry_kb_v3_stains_special.md",
  dye: "laundry_kb_v3_stains_dye.md",
  items: "laundry_kb_v3_items_clothing.md",
  home: "laundry_kb_v3_items_home.md",
  ironing: "laundry_kb_v3_items_ironing.md",
  tools: "laundry_kb_v3_tools_equipment.md",
  business: "laundry_kb_v3_items_business.md",
};

const TITLES = {
  oil: {
    vi: "NHÓM DẦU MỠ (Oil / Grease)",
    ko: "유성 오염 (기름/지방)",
    intro:
      "Nguyên tắc: hút dầu trước (N3), rồi surfactant (D2/D3), dầu nặng dùng dung môi (D1) có thông gió. Không ủi/sấy khi còn vết dầu.",
  },
  tannin: {
    vi: "NHÓM TANNIN",
    ko: "탄닌 오염",
    intro:
      "Nguyên tắc: nước lạnh ngay, acid nhẹ (A3) phá liên kết tannin, sau đó oxy bleach (B1) nếu còn màu. Không dùng nước nóng lúc đầu.",
  },
  special: {
    vi: "NHÓM ĐẶC BIỆT",
    ko: "특수 오염",
    intro:
      "Các vết phức tạp / hiếm gặp. Luôn thử góc khuất, ưu tiên phương pháp nhẹ trước, dừng ngay khi vết hết.",
  },
  dye: {
    vi: "NHÓM THUỐC NHUỘM & MỰC",
    ko: "염료/잉크",
    intro:
      "Nguyên tắc: thấm từ mặt trái, không chà lan màu. Dung môi (A1/A2) cho mực; bột kiềm + nắng cho curcumin (cà ri/nghệ).",
  },
  items: {
    vi: "LOẠI ĐỒ / ITEM TYPES",
    ko: "의류 유형별",
    intro:
      "Protocol theo loại trang phục. Kiểm tra nhãn giặt ủi trước; lụa/len không enzyme; áo dài và đồ mỏng lực tay thấp.",
  },
  home: {
    vi: "HOME TEXTILE",
    ko: "홈 텍스타일",
    intro:
      "Ga giường, khăn, rèm, thảm nhỏ. Ưu tiên phân loại màu, kiểm tra độ phai, không dùng chlorine trên màu.",
  },
  ironing: {
    vi: "ỦI & HOÀN THIỆN",
    ko: "다림질 & 피니싱",
    intro:
      "Chỉ ủi khi vết bẩn đã hết. Nhiệt độ theo sợi vải. Đặt khăn bảo vệ với vải mỏng / in / thêu.",
  },
  tools: {
    vi: "DỤNG CỤ & THIẾT BỊ",
    ko: "도구 & 장비",
    intro:
      "Chuẩn bị dụng cụ tiếp nhận và xử lý. Dụng cụ sạch riêng theo nhóm vết để tránh lây chéo.",
  },
  business: {
    vi: "VẬN HÀNH CỬA HÀNG",
    ko: "매장 운영",
    intro:
      "Tiếp nhận, từ chối, khiếu nại, an toàn hóa chất. Trả lời điểm chủ theo quy trình Wash Friends — rõ ràng, chuyên nghiệp.",
  },
};

function pick(obj, lang = "vi") {
  if (obj == null) return "";
  if (typeof obj === "string") return obj;
  return obj[lang] || obj.vi || obj.en || obj.ko || "";
}

function stars(n) {
  const d = Math.max(1, Math.min(5, Number(n) || 1));
  return "★".repeat(d) + "☆".repeat(5 - d);
}

function forceLabel(f) {
  const map = {
    1: "1 (baby face) — siêu nhẹ",
    2: "2 (cleaning glasses) — nhẹ",
    3: "3 (wiping table) — trung bình",
    4: "4 (scrubbing) — mạnh",
  };
  return map[f] || String(f);
}

function protocolToMd(p, idx) {
  const nameVi = pick(p.name, "vi");
  const nameKo = pick(p.name, "ko");
  const nameEn = pick(p.name, "en");
  const rule = pick(p.rule, "vi");
  const chems = (p.chems || []).join(", ") || "—";
  const lines = [];
  lines.push(`## PROTOCOL: ${nameVi}`);
  lines.push(`**Tên**: ${nameVi} / ${nameKo} / ${nameEn}`);
  lines.push(`**Độ khó**: ${stars(p.diff)}`);
  lines.push(`**Hóa chất**: ${chems}`);
  if (rule) lines.push(`**Quy tắc vàng**: ${rule}`);
  lines.push("");
  if (Array.isArray(p.steps) && p.steps.length) {
    lines.push("| Bước | Thao tác | Lực tay | Chi tiết | Checkpoint |");
    lines.push("|---|---|---|---|---|");
    for (const st of p.steps) {
      const action = pick(st.action, "vi").replace(/\|/g, "/");
      const detail = pick(st.detail, "vi").replace(/\|/g, "/");
      const sens = (st.sensory || [])
        .map((x) => pick(x, "vi"))
        .filter(Boolean)
        .join("; ")
        .replace(/\|/g, "/");
      lines.push(
        `| ${st.n} | ${action} | ${forceLabel(st.force)} | ${detail || "—"} | ${sens || "—"} |`
      );
    }
    lines.push("");
  }
  // Extra fields some item/topic cards use
  for (const key of ["warn", "note", "tip", "when", "never", "tools", "check"]) {
    if (p[key]) {
      const v = pick(p[key], "vi");
      if (v) lines.push(`**${key}**: ${v}`, "");
    }
  }
  if (p.groups && Array.isArray(p.groups)) {
    for (const g of p.groups) {
      lines.push(`### ${pick(g.name || g.title, "vi")}`);
      if (g.steps) {
        for (const st of g.steps) {
          lines.push(`- **B${st.n}**: ${pick(st.action, "vi")}`);
        }
      }
      lines.push("");
    }
  }
  lines.push("---");
  lines.push("");
  return lines.join("\n");
}

function buildFile(key, protocols) {
  const meta = TITLES[key];
  const header = [
    `# PROTOCOL XỬ LÝ v3.0 — ${meta.vi}`,
    `# 세탁 처리 프로토콜 v3.0 — ${meta.ko}`,
    `# Wash Friends Professional Knowledge System`,
    `# Phiên bản: 3.0 (recovered from training viewer)`,
    "",
    "---",
    "",
    `## NGUYÊN TẮC CỐT LÕI`,
    "",
    meta.intro,
    "",
    "Trả lời điểm chủ theo chuẩn Wash Friends: rõ bước, rõ hóa chất (mã E/D/B/A/N/S), rõ lực tay, kiểm tra trước khi sấy/ủi.",
    "",
    "---",
    "",
  ].join("\n");
  const body = (protocols || []).map((p, i) => protocolToMd(p, i)).join("\n");
  return header + body;
}

function loadDb(html) {
  // Pull from first DB.oil / const DB through last likely assignment before render helpers
  const start = html.indexOf("const DB = {}");
  if (start < 0) throw new Error("const DB = {} not found");
  // End before UI render if present
  let end = html.indexOf("// ====================  RENDER", start);
  if (end < 0) end = html.indexOf("function render", start);
  if (end < 0) end = html.indexOf("</script>", start);
  const chunk = html.slice(start, end);
  const code = `
    function t(ko,vi,en){return{ko,vi,en}};
    ${chunk}
    module.exports = DB;
  `;
  const sandbox = { module: { exports: {} }, exports: {} };
  vm.runInNewContext(code, sandbox, { timeout: 10000 });
  return sandbox.module.exports;
}

function main() {
  if (!fs.existsSync(VIEWER)) {
    console.error("Viewer not found:", VIEWER);
    process.exit(1);
  }
  const html = fs.readFileSync(VIEWER, "utf8");
  console.log("Reading", VIEWER, html.length, "chars");
  const DB = loadDb(html);
  const keys = Object.keys(DB);
  console.log("DB keys:", keys.join(", "));
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const summary = [];
  for (const [key, filename] of Object.entries(FILE_MAP)) {
    const protocols = DB[key];
    if (!protocols || !protocols.length) {
      console.warn("SKIP empty:", key);
      continue;
    }
    const md = buildFile(key, protocols);
    const out = path.join(OUT_DIR, filename);
    fs.writeFileSync(out, md, "utf8");
    summary.push({ key, filename, count: protocols.length, bytes: md.length });
    console.log("Wrote", filename, protocols.length, "protocols,", md.length, "bytes");
  }
  // Advanced topic packs → one franchise field file (WF voice, no citations)
  const advancedKeys = [
    "fabric",
    "label",
    "mystery",
    "yellowing",
    "colorbleed",
    "dryclean",
    "downcare",
    "laterite",
    "nodc",
    "decolor",
    "motorbike",
  ];
  const adv = [];
  for (const k of advancedKeys) {
    if (DB[k] && DB[k].length) {
      adv.push(`# ${k.toUpperCase()}`, "");
      for (const p of DB[k]) adv.push(protocolToMd(p));
    }
  }
  if (adv.length) {
    const advPath = path.join(OUT_DIR, "laundry_kb_v3_advanced_field.md");
    const advMd =
      [
        "# PROTOCOL NÂNG CAO / FIELD CASES v3.0",
        "# Wash Friends Professional Knowledge System",
        "",
        "Các tình huống chuyên sâu tại cửa hàng. Trả lời như kinh nghiệm vận hành Wash Friends.",
        "",
        "---",
        "",
      ].join("\n") + adv.join("\n");
    fs.writeFileSync(advPath, advMd, "utf8");
    summary.push({
      key: "advanced",
      filename: "laundry_kb_v3_advanced_field.md",
      count: advancedKeys.filter((k) => DB[k]?.length).length,
      bytes: advMd.length,
    });
    console.log("Wrote advanced_field.md", advMd.length, "bytes");
  }
  console.log(JSON.stringify(summary, null, 2));
}

main();
