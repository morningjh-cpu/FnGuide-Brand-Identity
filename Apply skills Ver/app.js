// FnGuide Brand Identity — 리뉴얼 시안 동작
// 로고·서체 데이터는 out/brand-site 의 logos.js · font-data.js · symbols.js 를 그대로 쓴다 (기존 index.html 과 같은 원본)
(() => {
  const { groups, logos, archive } = window.BRAND;
  const G = Object.fromEntries(groups.map(g => [g.id, g]));
  const L = Object.fromEntries(logos.map(l => [l.id, l]));
  const SYM = window.SYMBOLS || {};
  const $ = s => document.querySelector(s);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const icon = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2v8M4.5 6.5 8 10l3.5-3.5M3 13h10"/></svg>';
  const ext = '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M4 2h6v6M10 2 3 9"/></svg>';
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // 그룹 정보 (기존 사이트와 같은 문구)
  const INFO = {
    b2b: { menu: "B2B 대표상품", h1: 'B2B<span class="ko">대표상품</span>', mood: "열정, 자신감, 역동성, 현대적", ratio: 6.69,
      desc: "대표 주력 상품으로 FnRed 2025 컬러를 단독으로 사용합니다.", extra: "Flagship 브랜드" },
    contract: { menu: "B2B 계약상품", h1: 'B2B<span class="ko">계약상품</span>', mood: "고객사 맞춤형 서비스", ratio: 16.45,
      desc: "고객사에 맞춰 제공하는 계약형 서비스 그룹입니다(고객사 전용 화면·웹 서비스)." },
    fund: { menu: "펀드 상품", h1: 'Fund<span class="ko">상품</span>', mood: "신뢰, 정확성, 전문성", ratio: 12.17,
      desc: "FundGuide·FnSpectrum 같은 펀드·평가 서비스 그룹입니다." },
    index: { menu: "지수 상품", h1: 'Index<span class="ko">상품</span>', mood: "성장, 투명성, 중립성", ratio: 2.49,
      desc: "FnIndex·WiseIndex·CryptoGuide 같은 지수 서비스 그룹입니다.", extra: "지수 산출의 중립성과 투명한 처리과정", darkBg: true },
    b2c: { menu: "B2C 독립 체계", h1: 'B2C<span class="ko">독립 체계</span>', mood: "사용자 친화적, 서비스별 독립 컬러",
      desc: "개인 고객에게 특화된 서비스로, 사용자 트렌드에 맞게 독립적인 컬러와 서체를 씁니다." },
    ci: { menu: "FnGuide CI", h1: "FnGuide CI", mood: "고급스러움, 신뢰, 무게감, 헤리티지", ratio: 8.16,
      desc: "FnGuide의 CI는 금융시장을 바라보는 새로운 창이라는 컨셉으로 디자인했습니다." },
  };
  const ORDER = ["b2b", "contract", "fund", "index", "b2c", "ci"];
  const B2C_COLORS = { retamin: "#1C1C3A", wisereport: "#594FC8", fnapi: "#2457C5" };
  const bgOf = l => l.group === "b2c" ? B2C_COLORS[l.id] : l.kind === "improved" ? "#B9023D" : G[l.group].color;
  const dotOf = id => id === "b2c" ? "#2457C5" : G[id].color;

  // 로고 크기: 어디서나 같은 배율 (높이 맞춤 금지). 회사 CI 원본은 크기 기준이 달라 따로 맞춘다
  const sized = (svg, w, h) => svg.replace(/width="[^"]*" height="[^"]*"/, `width="${w.toFixed(1)}" height="${h.toFixed(1)}"`);
  const fit = l => ({ official: 0.7, logotype: 0.6 }[l.kind] || 1);
  const at = (svg, l, k = 1) => sized(svg, l.w * k * fit(l), l.h * k * fit(l));

  // ---------- 받기 ----------
  let tId;
  function toast(msg) {
    const t = $("#toast"); t.textContent = msg; t.classList.add("on");
    clearTimeout(tId); tId = setTimeout(() => t.classList.remove("on"), 1800);
  }
  function save(blob, name) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    toast(name + " 저장");
  }
  // 받는 파일은 그림 둘레에 여백: SVG 10px, PNG 16px (기존 사이트와 같음)
  const PAD_SVG = 10, PAD_PNG = 16;
  function padSvg(svg, m = PAD_SVG) {
    return svg.replace(/<svg\b[^>]*>/, tag => {
      const get = n => (tag.match(new RegExp("\\s" + n + '="([^"]+)"')) || [])[1];
      const w = parseFloat(get("width")), h = parseFloat(get("height"));
      const [x, y, vw, vh] = get("viewBox").split(/[\s,]+/).map(Number);
      const px = m * vw / w, py = m * vh / h, r = v => Math.round(v * 100) / 100;
      return tag.replace(/(\swidth=")[^"]+/, "$1" + r(w + 2 * m)).replace(/(\sheight=")[^"]+/, "$1" + r(h + 2 * m))
        .replace(/(\sviewBox=")[^"]+/, "$1" + [r(x - px), r(y - py), r(vw + 2 * px), r(vh + 2 * py)].join(" "));
    });
  }
  function pngBlob(svg, w, h, scale = 4) {
    return new Promise(done => {
      const img = new Image();
      img.onload = () => {
        const c = document.createElement("canvas");
        c.width = Math.round(w * scale) + 2 * PAD_PNG; c.height = Math.round(h * scale) + 2 * PAD_PNG;
        c.getContext("2d").drawImage(img, PAD_PNG, PAD_PNG, Math.round(w * scale), Math.round(h * scale));
        c.toBlob(done, "image/png");
      };
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
    });
  }
  const sizeOf = svg => svg.match(/width="([\d.]+)" height="([\d.]+)"/).slice(1).map(Number);
  // ZIP 묶기 (압축 없이 담기만 — 외부 라이브러리 없이 사내망에서도 동작)
  const CRC = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc32 = u => { let c = 0xFFFFFFFF; for (const b of u) c = CRC[(c ^ b) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  async function makeZip(files) {
    const enc = new TextEncoder(), parts = [], dir = []; let off = 0;
    const le = (n, b) => { const a = new Uint8Array(b); for (let i = 0; i < b; i++) a[i] = (n >>> (8 * i)) & 255; return a; };
    for (const f of files) {
      const data = new Uint8Array(await f.blob.arrayBuffer()), nm = enc.encode(f.name), crc = crc32(data);
      const head = [le(0x04034b50, 4), le(20, 2), le(0x0800, 2), le(0, 2), le(0, 4), le(crc, 4), le(data.length, 4), le(data.length, 4), le(nm.length, 2), le(0, 2), nm];
      dir.push([le(0x02014b50, 4), le(20, 2), le(20, 2), le(0x0800, 2), le(0, 2), le(0, 4), le(crc, 4), le(data.length, 4), le(data.length, 4), le(nm.length, 2), le(0, 2), le(0, 2), le(0, 2), le(0, 2), le(0, 4), le(off, 4), nm]);
      parts.push(...head, data); off += head.reduce((t, a) => t + a.length, 0) + data.length;
    }
    const cd = dir.flat(), size = cd.reduce((t, a) => t + a.length, 0);
    return new Blob([...parts, ...cd, le(0x06054b50, 4), le(0, 2), le(0, 2), le(files.length, 2), le(files.length, 2), le(size, 4), le(off, 4), le(0, 2)], { type: "application/zip" });
  }
  // 개별 받기 단추
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-dl]"); if (!b) return;
    const l = L[b.dataset.id], v = b.dataset.v;
    const svg = v === "color" ? l.svg : v === "white" ? l.white : l.variants.find(x => x.key === v).svg;
    const base = l.id + (v === "color" ? "" : "-" + v);
    const [w, h] = sizeOf(svg);
    b.dataset.dl === "svg" ? save(new Blob([padSvg(svg)], { type: "image/svg+xml" }), base + ".svg")
      : pngBlob(svg, w, h).then(bl => save(bl, `${base}@4x.png`));
  });
  const dl = (id, v = "color", label = "") => `<span class="btns"><button class="btn" data-dl="svg" data-v="${v}" data-id="${id}">${icon}${label}SVG</button><button class="btn" data-dl="png" data-v="${v}" data-id="${id}">${icon}${label}PNG</button></span>`;

  // 전체 받기 (기존 다운로드 화면과 같은 목록·파일 구성)
  const dlList = ["ci", "b2b", "contract", "fund", "index", "b2c"].flatMap(gid => logos.filter(l => l.group === gid)).filter(l => l.id !== "fnguide-inc");
  let zipping = false;
  document.addEventListener("click", async e => {
    const b = e.target.closest("[data-zip]"); if (!b || zipping) return;
    zipping = true;
    const btns = document.querySelectorAll("[data-zip]"), labels = [...btns].map(x => x.innerHTML);
    btns.forEach(x => { x.disabled = true; x.textContent = "파일을 묶는 중…"; });
    try {
      const files = [];
      for (const l of dlList) for (const [v, svg] of [["color", l.svg], ["white", l.white]]) {
        if (!svg) continue;
        const base = l.id + (v === "color" ? "" : "-white"), dirName = v === "color" ? "color" : "white";
        const [w, h] = sizeOf(svg);
        files.push({ name: `FnGuide-logotypes/svg/${dirName}/${base}.svg`, blob: new Blob([padSvg(svg)], { type: "image/svg+xml" }) });
        files.push({ name: `FnGuide-logotypes/png/${dirName}/${base}@4x.png`, blob: await pngBlob(svg, w, h) });
      }
      save(await makeZip(files), "FnGuide-logotypes.zip");
    } finally { zipping = false; btns.forEach((x, i) => { x.disabled = false; x.innerHTML = labels[i]; }); }
  });

  // ---------- 공통 ----------
  $("#mark").innerHTML = L.fnguide.svg + "<span>Brand Identity</span>";
  $("#footMark").innerHTML = sized(L.fnguide.white, L.fnguide.w, L.fnguide.h).replace("<svg ", '<svg preserveAspectRatio="xMinYMax meet" ');
  const bar = $("#bar");
  addEventListener("scroll", () => { bar.classList.toggle("lift", scrollY > 8); document.body.classList.toggle("scrolled", scrollY > 8); }, { passive: true });
  $("#menuWord").addEventListener("click", () => {
    const open = bar.classList.toggle("open");
    $("#menuWord").setAttribute("aria-expanded", open); $("#menuWord").textContent = open ? "닫기" : "메뉴";
  });

  // ---------- 홈 ----------
  // 첫 화면: 이름이 한 줄로 흐르고, FnRed 네모를 지나는 부분만 흰 글자 (같은 줄 두 벌을 같은 속도로)
  // 제목(h1)에는 글자를 한 번만 두고, 이어지는 복사본은 화면 읽기 프로그램이 건너뛰게 한다
  const W = "FnGuide Brand Identity", copy = `<span aria-hidden="true">${W}</span>`;
  $(".hero .ink .track").insertAdjacentHTML("beforeend", copy.repeat(3));
  $(".hero .paper .track").innerHTML = `<span>${W}</span>` + copy.repeat(3);
  function speed() { // 초당 40px 정도로 일정하게
    const t = $(".hero .track"); if (!t) return;
    const d = (t.scrollWidth / 2) / 40;
    document.querySelectorAll(".hero .track").forEach(x => x.style.setProperty("--dur", d + "s"));
  }
  document.fonts.ready.then(speed); addEventListener("resize", speed);

  $("#ciSquare").innerHTML = sized(L.fnguide.white, L.fnguide.w, L.fnguide.h).replace(/width="[^"]*" height="[^"]*"/, 'width="100%"');

  // 사업별 컬러 띠: 그룹마다 하나의 색 면, 폭은 일부러 다르게. 로고는 모두 같은 배율
  const BAND = [
    { id: "ci", g: 4, bg: "#94243A", logo: "fnguide-ci", v: "white", name: "FnGuide CI", hex: "FnWine #94243A · FnDarkGray #778288" },
    { id: "b2b", g: 5, bg: "#B9023D", logo: "fnguide-com", v: "white", name: "B2B 대표상품", hex: "FnRed #B9023D" },
    { id: "contract", g: 3, bg: "#1C1C3A", logo: "etfglobal", v: "white", name: "B2B 계약상품", hex: "Contract #1C1C3A" },
    { id: "fund", g: 3, bg: "#0C3178", logo: "fundguide", v: "white", name: "펀드", hex: "Fund #0C3178" },
    { id: "index", g: 3, bg: "#45B792", logo: "fnindex", v: "white", name: "지수", hex: "Index #45B792" },
    { id: "b2c", g: 4, bg: "#F4F2F1", logos: ["retamin", "wisereport", "fnapi"], name: "B2C 독립 체계", hex: "Retamin #1C1C3A · WiseReport #594FC8 · API #2457C5", light: true },
  ];
  const BAND_K = 0.78;
  $("#band").innerHTML = BAND.map(b => {
    let art;
    if (b.logos) art = b.logos.map(id => at(L[id].svg, L[id], BAND_K)).join("");
    else art = at(L[b.logo].white, L[b.logo], BAND_K);
    return `<a href="#logo/${b.id}" style="--g:${b.g};background:${b.bg}"${b.light ? ' class="light"' : ""}>
      <span class="nm">${b.name}<small>${b.hex}</small></span>
      <span class="lg">${art}<span class="go">로고 보기</span></span></a>`;
  }).join("");

  $("#modLogos").innerHTML = ["fnguide", "dataguide", "fundguide"].map(id => at(L[id].svg, L[id], 0.7)).join("");
  $("#modIcons").insertAdjacentHTML("beforeend", ["dataguide", "wisereport", "retamin"].filter(id => SYM[id])
    .map(id => `<img alt="${id} 심볼 아이콘" src="data:image/svg+xml;charset=utf-8,${encodeURIComponent(SYM[id].svg)}">`).join(""));

  // ---------- 전용서체 ----------
  $("#fontFiles").innerHTML = [
    ["OTF", "디자인 툴용 (Figma, Illustrator 등)"], ["TTF", "오피스용 (Word, PowerPoint)"], ["WOFF2", "사내 웹 서비스용 (작은 파일)"], ["WOFF", "사내 웹 서비스용"],
  ].map(([f, d]) => `<li><b>${f}</b><span>${d}</span><a class="btn primary" href="out/brand-site/fonts/FnGuideLogotype-Regular.${f.toLowerCase()}" download>${icon}${f} 받기</a></li>`).join("");

  const spec = $("#specText"), input = $("#specInput");
  let typed = false;
  input.addEventListener("input", () => { spec.textContent = input.value || " "; typed = input.value.trim() !== ""; });
  spec.addEventListener("keydown", e => { if (e.key === "Enter") e.preventDefault(); });
  spec.addEventListener("input", () => { input.value = spec.textContent; typed = input.value.trim() !== ""; });
  const size = $("#specSize"), sizeNum = $("#specSizeNum");
  const setSize = v => { spec.style.fontSize = v + "px"; size.value = v; sizeNum.value = v; };
  const syncSize = () => { if (!spec.style.fontSize) size.value = sizeNum.value = Math.round(parseFloat(getComputedStyle(spec).fontSize)); };
  addEventListener("resize", syncSize);
  size.addEventListener("input", () => setSize(size.value));
  sizeNum.addEventListener("input", () => { const v = Number(sizeNum.value); if (v >= 32 && v <= 150) { spec.style.fontSize = v + "px"; size.value = v; } });
  sizeNum.addEventListener("change", () => setSize(Math.min(150, Math.max(32, Math.round(Number(sizeNum.value)) || 120))));
  const CHECKER = "repeating-conic-gradient(#C4C4C4 0 25%, #E2E2E2 0 50%) 0 0 / 20px 20px"; // 투명 배경 표시용 격자 (taste-skill-ignore)
  const SW = [
    { c: "#B9023D", bg: "#FFFFFF", word: "FnGuide", name: "B2B 대표" },
    { c: "#1C1C3A", bg: "#FFFFFF", word: "ETF Global", name: "B2B 계약" },
    { c: "#0C3178", bg: "#FFFFFF", word: "FundGuide", name: "펀드" },
    { c: "#45B792", bg: "#FFFFFF", word: "FnIndex", name: "지수" },
    { c: "#594FC8", bg: "#FFFFFF", word: "WiseReport", name: "WiseReport" },
    { c: "#2457C5", bg: "#FFFFFF", word: "FnAPI", name: "API" },
    { c: "#FFFFFF", bg: CHECKER, word: "FnGuide", name: "흰색" },
  ];
  $("#swatches").innerHTML = SW.map((s, i) =>
    `<span class="sw-item"><button class="sw" aria-label="${s.name} ${s.c}" aria-pressed="${i === 0}" data-i="${i}" style="background:${s.bg === CHECKER ? CHECKER.replace("20px 20px", "8px 8px") : s.c}"></button><small>${s.name}</small></span>`).join("")
    + `<span class="sw-item"><span class="sw sw-custom" title="사용자 지정 색상"><input type="color" value="#1C1C3A" aria-label="사용자 지정 색상"></span><small>사용자</small></span>`
    + `<input type="text" class="sw-hex" maxlength="7" placeholder="#RRGGBB" aria-label="사용자 지정 색상 웹 컬러 코드">`;
  const pressed = el => document.querySelectorAll(".sw").forEach(x => x.setAttribute("aria-pressed", x === el));
  $("#swatches").addEventListener("click", e => {
    const b = e.target.closest(".sw"); if (!b || b.classList.contains("sw-custom")) return;
    const s = SW[b.dataset.i]; pressed(b);
    $("#specimen").style.background = s.bg; paint(s.c);
    if (s.word && !typed) { spec.textContent = s.word; input.value = s.word; }
  });
  const light = c => { const [r, g, b] = [1, 3, 5].map(k => parseInt(c.slice(k, k + 2), 16)); return 0.299 * r + 0.587 * g + 0.114 * b > 230; };
  let specColor;
  function paint(c) { spec.style.color = c; specColor = c; size.style.setProperty("--thumb", light(c) ? "#9AA0A6" : c); }
  $("#specimen").style.background = "#FFFFFF"; paint(SW[0].c);
  const custom = $(".sw-custom"), picker = custom.querySelector("input"), hex = $(".sw-hex");
  function applyCustom(c) { pressed(custom); custom.style.background = c; $("#specimen").style.background = light(c) ? CHECKER : "#FFFFFF"; paint(c); }
  picker.addEventListener("input", () => { const c = picker.value.toUpperCase(); hex.value = c; hex.classList.remove("bad"); applyCustom(c); });
  hex.addEventListener("input", () => {
    let v = hex.value.trim().replace(/^#?/, "#").toUpperCase();
    if (/^#[0-9A-F]{3}$/.test(v)) v = "#" + [...v.slice(1)].map(x => x + x).join("");
    const ok = /^#[0-9A-F]{6}$/.test(v);
    hex.classList.toggle("bad", !ok && hex.value.trim() !== "");
    if (ok) { picker.value = v.toLowerCase(); applyCustom(v); }
  });
  // 미리보기 문구를 글자 윤곽선으로 그려 SVG·PNG 저장 (서체의 합자·간격 규칙 그대로, font-data.js)
  function shape(text) {
    const F = window.FONT_DATA, out = [], missing = new Set();
    let i = 0, x = 0, prev = null;
    while (i < text.length) {
      const lg = F.liga.find(([seq]) => text.startsWith(seq, i));
      const name = lg ? lg[1] : F.cmap[text[i]];
      i += lg ? lg[0].length : 1;
      if (!name) { missing.add(text[i - 1]); continue; }
      if (prev) x += F.kern[prev + " " + name] || 0;
      out.push([name, x]); x += F.glyphs[name][0]; prev = name;
    }
    return { glyphs: out, missing: [...missing] };
  }
  const shift = (d, dx) => d.replace(/([MLCQHVZ])([^MLCQHVZ]*)/g, (_, c, args) => {
    const n = args.trim() ? args.trim().split(/[\s,]+/).map(Number) : [];
    return c + n.map((v, k) => c === "V" || (c !== "H" && k % 2) ? v : Math.round((v + dx) * 100) / 100).join(" ");
  });
  function pathBox(d) {
    const probe = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    probe.style.cssText = "position:absolute;width:0;height:0;visibility:hidden";
    probe.innerHTML = `<path d="${d}"/>`;
    document.body.appendChild(probe);
    const bb = probe.firstChild.getBBox(); probe.remove();
    return bb;
  }
  function specSvg() {
    const text = spec.textContent.replace(/\s+/g, " ");
    const { glyphs, missing } = shape(text);
    const d = glyphs.map(([n, x]) => shift(window.FONT_DATA.glyphs[n][1], x)).join("");
    if (!d) return { missing };
    const bb = pathBox(d), k = parseFloat(getComputedStyle(spec).fontSize) / window.FONT_DATA.upem, r = v => Math.round(v * 100) / 100;
    const w = r(bb.width * k), h = r(bb.height * k);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${r(bb.x)} ${r(bb.y)} ${r(bb.width)} ${r(bb.height)}"><path fill="${specColor}" d="${d}"/></svg>\n`;
    return { svg, w, h, missing, name: text.trim().replace(/[\\/:*?"<>|\s]+/g, "-").slice(0, 40) || "FnGuide-Logotype" };
  }
  $("#specDl").addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    const r = specSvg();
    if (!r.svg) { toast("저장할 글자가 없습니다 (한글은 서체에 없습니다)"); return; }
    b.dataset.type === "svg" ? save(new Blob([padSvg(r.svg)], { type: "image/svg+xml" }), r.name + ".svg") : pngBlob(r.svg, r.w, r.h).then(bl => save(bl, r.name + "@4x.png"));
    if (r.missing.length) setTimeout(() => toast("서체에 없는 글자는 빠졌습니다: " + r.missing.join(" ")), 1900);
  });

  // ---------- 로고타입 ----------
  const site = l => l.url ? `<a class="site" href="${l.url}" target="_blank" rel="noopener">서비스 바로가기 (새 창) ${ext}</a>` : "";
  const pending = l => l.group === "contract" ? '<small class="pending">로고 컬러 변경 예정 · 현재 파일 사용</small>'
    : l.id === "fnspectrum" ? '<small class="pending">로고 변경 예정 · 현재 파일 사용</small>'
    : l.id === "wisereport" ? '<small class="pending">2026년 디자인 리뉴얼 버전</small>' : "";
  function row(l, info) {
    const white = `<div class="stage white"><small>흰 배경</small>${at(l.svg, l)}</div>`;
    if (!l.white) return `<div class="row"><div class="stages" style="grid-template-columns:1fr">${white}</div>
      <div class="meta"><div class="name"><strong>${esc(l.name)}${pending(l)}</strong>${site(l)}</div>${dl(l.id)}</div></div>`;
    const second = info.darkBg
      ? `<div class="stage" style="background:#1C1C3A;color:#fff"><small>어두운 배경 · 권장</small>${at(l.svg, l)}</div>`
      : `<div class="stage" style="background:${bgOf(l)};color:#fff"><small>컬러 배경 · 흰색 버전</small>${at(l.white, l)}</div>`;
    return `<div class="row"><div class="stages">${white}${second}</div>
      <div class="meta"><div class="name"><strong>${esc(l.name)}${pending(l)}</strong>${site(l)}</div>${dl(l.id)}${dl(l.id, "white", "흰색 ")}</div></div>`;
  }
  function renderGroup(id) {
    const g = G[id], i = INFO[id], items = logos.filter(l => l.group === id);
    const color = id === "b2c" ? [["Retamin 주", "#1C1C3A"], ["Retamin 보조", "#26C0D2"], ["WiseReport", "#594FC8"], ["API", "#2457C5"]]
      : id === "ci" ? [["FnWine", "#94243A"], ["FnDarkGray", "#778288"]] : [[g.colorName, g.color]];
    let html = `<nav class="tabs" aria-label="로고타입 그룹">${logoTabs(id)}</nav>
      <div class="g-hero"><h1>${i.h1}</h1><p class="lead">${i.desc}</p>
        <dl><dt>컬러</dt><dd>${color.map(([n, c]) => `<span class="chip" style="background:${c}"></span>${n} ${c}`).join("<br>")}</dd>
        <dt>성격</dt><dd>${i.mood}</dd>${i.extra ? `<dt>의미</dt><dd>${i.extra}</dd>` : ""}
        ${i.ratio ? `<dt>흰 배경 대비</dt><dd>${i.ratio} — ${i.ratio >= 4.5 ? "작은 글자도 잘 보임(4.5 이상)" : "큰 글자·그래픽용(4.5 미만)"}</dd>` : ""}</dl></div>`;
    if (id === "index") html += `<p class="alert"><b>흰 배경 비권장.</b> Index 컬러는 흰 배경에서 명도 대비가 낮아(2.49) 어두운 배경과 조합하세요.</p>`;
    if (id === "b2c") html += `<p class="alert">리타민은 B2C 독립 체계에 따라 전용서체가 아닌 서비스 고유 로고를 씁니다(주 #1C1C3A, 보조 #26C0D2). 보조 색상은 흰 배경 대비가 낮아(2.20) 흰 배경 글자에는 권장하지 않습니다. WiseReport(#594FC8)와 FnAPI(#2457C5)는 전용서체 로고타입에 서비스별 독립 컬러를 씁니다.</p>`;
    if (id === "ci") {
      const ci = L["fnguide-ci"], improved = L.fnguide;
      const sys = [["FnWine", "#94243A", "Pantone 704 C", "148 / 36 / 58", "50 / 100 / 80 / 0"], ["FnDarkGray", "#778288", "Pantone 431 C", "119 / 130 / 136", "15 / 0 / 0 / 60"], ["FnLightGray", "#A8B0B6", "Pantone 429 C", "155 / 165 / 165", "5 / 0 / 0 / 35"]];
      const mono = [["#94243A", ci.white, "FnWine 배경 · 흰색"], ["#FFFFFF", ci.variants[0].svg, "단색 FnWine"], ["#778288", ci.white, "FnDarkGray 배경 · 흰색"], ["#FFFFFF", ci.variants[1].svg, "단색 FnDarkGray"]];
      html += `<div class="g-sec"><h2>공식 로고 · CI</h2>
          <div class="rows"><div class="row"><div class="stages"><div class="stage white"><small>흰 배경</small>${at(ci.svg, ci)}</div><div class="stage" style="background:#94243A;color:#fff"><small>FnWine 배경 · 흰색</small>${at(ci.white, ci)}</div></div>
            <div class="meta"><div class="name"><strong>${esc(ci.name)}</strong><a class="site" href="https://corp.fnguide.com/Company/CIP" target="_blank" rel="noopener">원본 제공: 회사 홈페이지 브랜드 리소스 (새 창) ${ext}</a></div>${dl(ci.id)}${dl(ci.id, "white", "흰색 ")}
              <span class="btns"><a class="btn primary" href="out/brand-site/files/fnguide-logo-AI.zip" download>${icon}AI 원본</a><a class="btn primary" href="out/brand-site/files/fnguide-logo-PNG.zip" download>${icon}PNG 원본</a></span></div></div></div>
        </div>
        <div class="g-sec"><h2>개선된 브랜드 로고</h2><p class="sub">리뉴얼 후 FnRed 2025(#B9023D)를 쓰는 브랜드 로고입니다.</p><div class="rows">${row(improved, i)}</div>
          <div class="story"><div><span>이전</span><h3>2000년의 클래식 세리프</h3><p>회사의 역사를 담은 클래식 세리프 로고타입으로, 2000년에 만들었습니다.</p></div>
            <div><span>개선</span><h3>볼륨 향상</h3><p>서체 고유의 유니크함을 유지하되, 시인성을 높이기 위해 전체 볼륨을 키웠습니다.</p></div>
            <div><span>컬러</span><h3>Dark Wine에서 FnRed로</h3><p>더 밝고 선명한 빨강으로 바꿔, 화면에서 힘 있게 보이도록 했습니다.</p></div></div></div>
        <div class="g-sec"><h2>로고타입</h2><p class="sub">임의로 타이핑하거나 색을 바꾸거나 일부만 쓰는 등 변형할 수 없습니다.</p><div class="rows">${["fnguide-inc", "fnguide-kr"].map(k => row(L[k], i)).join("")}</div></div>
        <div class="g-sec"><h2>전용색상</h2><p class="sub">FnGuide의 두 가지 핵심 컬러는 FnWine과 FnDarkGray입니다.</p>
          <table class="ci-table"><thead><tr><th>컬러</th><th>HEX</th><th>Pantone</th><th>RGB</th><th>CMYK</th></tr></thead>
          <tbody>${sys.map(([n, hx, p, rgb, cmyk]) => `<tr><td><span class="smp" style="background:${hx}"></span><b>${n}</b></td><td>${hx}</td><td>${p}</td><td>${rgb}</td><td>${cmyk}</td></tr>`).join("")}</tbody></table></div>
        <div class="g-sec"><h2>단색</h2><p class="sub">한 가지 색으로 표현해야 할 때 씁니다.</p>
          <div class="mono">${mono.map(([bg, svg, cap]) => `<figure><div class="stage${bg === "#FFFFFF" ? " white" : ""}" style="${bg === "#FFFFFF" ? "" : `background:${bg}`}">${sized(svg, ci.w * 0.4, ci.h * 0.4)}</div><figcaption>${cap}</figcaption></figure>`).join("")}</div>
          <div class="meta"><span class="name">단색 파일</span><span class="btns">${dl(ci.id, "wine", "FnWine ")}${dl(ci.id, "darkgray", "FnDarkGray ")}</span></div></div>
        <div class="g-sec"><h2>그 밖의 CI</h2><p class="sub">기록용으로만 보여 드리며 다운로드는 제공하지 않습니다.</p>
          <div class="archive">${archive.map(a => `<div><div class="stage">${a.svg}</div><p><b>${esc(a.name)}</b> · ${esc(a.desc)}</p></div>`).join("")}</div></div>`;
    } else {
      html += `<div class="g-sec"><h2>로고타입 ${items.length}종</h2><div class="rows">${items.map(l => row(l, i)).join("")}</div>
        <div class="dl-all"><button type="button" class="btn primary big" data-zip>${icon}로고 전체 받기 (ZIP)</button><span>로고 ${dlList.length}종 · 컬러와 흰색 · SVG와 PNG(4배 크기)</span></div></div>`;
    }
    $("#page-logo").innerHTML = html;
  }

  // ---------- 하위 메뉴(탭) ----------
  const FONT_TABS = [["font", "서체 소개"], ["font/update", "폰트 업데이트"], ["font/critique", "디자인 크리틱"]];
  const fontTabs = cur => FONT_TABS.map(([h, n]) => `<a href="#${h}"${h === cur ? ' aria-current="page"' : ""}>${n}</a>`).join("");
  const logoTabs = cur => ORDER.map(k => `<a href="#logo/${k}"${k === cur ? ' aria-current="page"' : ""}><i style="background:${dotOf(k)}"></i>${INFO[k].menu}</a>`).join("")
    + `<a href="#download"${cur === "download" ? ' aria-current="page"' : ""}>${icon}로고 받기</a>`;

  // ---------- 로고 받기 ----------
  // 표의 로고는 모두 같은 배율 (칸에 맞춰 줄이지 않음). 한글 로고타입만 조금 크게 (기존 사이트와 같음)
  const DL_SCALE = 0.6, DL_FIT = { "fnguide-kr": 0.8 };
  const dlFit = l => DL_FIT[l.id] || fit(l);
  const zipLabel = `${icon}로고 전체 받기 (ZIP)`;
  document.querySelectorAll("button[data-zip]:empty").forEach(b => b.innerHTML = zipLabel);
  $("#dlNote").textContent = `로고 ${dlList.length}종 · 컬러와 흰색 · SVG와 PNG(4배 크기)`;
  $("#dlGroups").innerHTML = ["ci", "b2b", "contract", "fund", "index", "b2c"].map(gid => {
    const items = dlList.filter(l => l.group === gid);
    return `<div class="dl-group"><h2><i class="chip" style="background:${dotOf(gid)}"></i>${INFO[gid].menu}</h2>
      <ul class="dl-list">${items.map(l => `<li>
        <span class="dl-logo">${sized(l.svg, l.w * DL_SCALE * dlFit(l), l.h * DL_SCALE * dlFit(l))}</span>
        <b>${esc(l.name)}</b>
        <span class="dl-btns"><span class="dl-k">컬러</span>${dl(l.id)}</span>
        <span class="dl-btns"><span class="dl-k">흰색</span>${l.white ? dl(l.id, "white") : '<span class="dl-none">없음</span>'}</span></li>`).join("")}</ul></div>`;
  }).join("");

  // ---------- 디자인 아티클: 파비콘·아이콘·오픈 그래프 (기존 사이트와 같은 결과물) ----------
  const artList = dlList.filter(l => l.white); // 오픈 그래프에 흰색 로고가 필요하므로 흰색 판이 있는 로고만
  const ciI = artList.findIndex(l => l.id === "fnguide-ci"), imI = artList.findIndex(l => l.id === "fnguide");
  [artList[ciI], artList[imI]] = [artList[imI], artList[ciI]]; // 여기서만: 개선 로고를 FnGuide CI 앞으로
  const OG_DEFAULT = "Your Best Financial Guide";
  const OG_TEXT = {
    "fnguide-com": "따라가기 힘든 금융 정보, 에프앤가이드로 한 발 앞서가세요!",
    "fnguide-ci": OG_DEFAULT, fnguide: "데이터로 세상을 바꾸는 사람들",
    quantiwise: "기업/주식투자 분석 시스템",
    wisereport: "흩어져 있는 투자 정보는 와이즈리포트에서",
    retamin: "하루 한 번, 건강한 투자 습관 리타민",
    cryptoguide: "디지털자산 정보 플랫폼",
    dataguide: "단 하나의 솔루션으로 필요한 모든 데이터를 탐색하세요",
    fnspace: "금융데이터를 API를 통해 쉽고 편리하게",
    companyguide: "데일리 업데이트되는 온라인 상장기업분석", companywise: "데일리 업데이트되는 온라인 상장기업분석",
  };
  const OG_GROUP = { index: "국내 민간 최초 실시간 지수 서비스 구현", fund: "데이터 기반의 고객 맞춤형 펀드평가 서비스" };
  const ICON_SIZES = [16, 24, 32, 64, 128, 256, 512];
  const APPLE_FILL = { dataguide: "#B9023D" }; // 모서리가 둥근 심볼: 아이폰 아이콘은 투명 모서리를 심볼 색으로 채움
  const art = { l: artList[0], kind: "fn", text: {}, ogSize: 50 };
  const sizedTo = (svg, n) => svg.replace(/width="[^"]*" height="[^"]*"/, `width="${n}" height="${n}"`);
  // "Fn" 아이콘: 사업 색 네모 + 전용서체 흰 Fn (피그마 Icon 시안). n 의 왼쪽 세리프를 F 윗팔 끝에 붙인다
  function fnIcon(color, text = "Fn", size = 100) {
    const g = c => window.FONT_DATA.glyphs[window.FONT_DATA.cmap[c]][1], bF = pathBox(g("F")), bN = pathBox(g("n"));
    const fn = g("F") + shift(g("n"), bF.x + bF.width - 1 - bN.x);
    const d = text === "Fn" ? fn : shape(text).glyphs.map(([n, x]) => shift(window.FONT_DATA.glyphs[n][1], x)).join("");
    const bb = pathBox(d), k = 377 / pathBox(fn).width * size / 100, r = v => Math.round(v * 1000) / 1000;
    const tx = (text === "Fn" ? 252.6 : 256) - (bb.x + bb.width / 2) * k, ty = 256.2 + 350 * k;
    return `<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512"><defs><filter id="fnShadow" x="-10%" y="-10%" width="120%" height="130%" color-interpolation-filters="sRGB"><feDropShadow dx="0" dy="4" stdDeviation="2" flood-color="#000" flood-opacity=".25"/></filter></defs>`
      + `<rect width="512" height="512" fill="${color}"/><g filter="url(#fnShadow)"><path fill="#FFFFFF" transform="translate(${r(tx)} ${r(ty)}) scale(${r(k)})" d="${d}"/></g></svg>\n`;
  }
  const artSvg = () => art.kind === "symbol" ? SYM[art.l.id].svg + "\n" : fnIcon(bgOf(art.l));
  const apple = { kind: "text", text: "Fn", size: 100 };
  const appleText = () => [...apple.text.trim()].filter(c => window.FONT_DATA.cmap[c]).join("") || "Fn";
  function symbolFilled(id) {
    const { svg, size: n } = SYM[id], f = APPLE_FILL[id];
    return (f ? svg.replace(/<svg\b[^>]*>/, m => m + `<rect width="${n}" height="${n}" fill="${f}"/>`) : svg) + "\n";
  }
  const appleSvg = () => apple.kind === "symbol" && SYM[art.l.id] ? symbolFilled(art.l.id) : fnIcon(bgOf(art.l), appleText(), apple.size);
  const loadImg = svg => new Promise(ok => { const i = new Image(); i.onload = () => ok(i); i.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg); });
  async function iconPng(svg, n, fill) {
    const c = document.createElement("canvas"); c.width = c.height = n;
    const x = c.getContext("2d");
    if (fill) { x.fillStyle = fill; x.fillRect(0, 0, n, n); }
    x.drawImage(await loadImg(svg), 0, 0, n, n);
    return new Promise(ok => c.toBlob(ok, "image/png"));
  }
  // ico 파일: 여러 크기 PNG 를 한 파일에 담음 (크기 칸은 1바이트라 256 이상은 0 — 실제 크기는 안의 PNG 가 알려 줌)
  async function icoBlob(svg, sizes = [16, 32, 48]) {
    const pngs = await Promise.all(sizes.map(n => iconPng(svg, n).then(b => b.arrayBuffer())));
    const head = new DataView(new ArrayBuffer(6 + 16 * sizes.length));
    head.setUint16(2, 1, true); head.setUint16(4, sizes.length, true);
    let off = head.byteLength;
    sizes.forEach((n, i) => {
      const p = 6 + 16 * i;
      head.setUint8(p, n & 255); head.setUint8(p + 1, n & 255); head.setUint16(p + 4, 1, true); head.setUint16(p + 6, 32, true);
      head.setUint32(p + 8, pngs[i].byteLength, true); head.setUint32(p + 12, off, true); off += pngs[i].byteLength;
    });
    return new Blob([head, ...pngs], { type: "image/x-icon" });
  }
  // 오픈 그래프 1200×630: 사업 색 바탕 + 흰 로고 + 가로선(가운데 흰색→양 끝 흐림, 폭 932) + 소개 문구(Pretendard 600, 줄간격 148%, 폭 1040)
  let ogTurn = 0;
  function wrapLines(x, text, maxW) {
    const ok = t => x.measureText(t).width <= maxW, lines = [];
    for (const para of text.split("\n")) {
      let line = "";
      for (const word of para.trim().split(/ +/)) { const t = line ? line + " " + word : word; if (ok(t) || !line) line = t; else { lines.push(line); line = word; } }
      lines.push(line);
    }
    return lines.flatMap(l => {
      if (ok(l)) return [l];
      const out = []; let cur = "";
      for (const c of l) { if (cur && !ok(cur + c)) { out.push(cur); cur = c; } else cur += c; }
      return [...out, cur];
    });
  }
  async function drawOg(cv, l, text) {
    const turn = cv === $("#artOg") ? ++ogTurn : 0, W = 1200, H = 630, k = 3 * fit(l), w = l.w * k, h = l.h * k, fs = art.ogSize, lh = fs * 1.48;
    const [img] = await Promise.all([loadImg(l.white), document.fonts.load('600 44px "Pretendard Variable"').catch(() => {})]);
    if (turn && turn !== ogTurn) return;
    const x = cv.getContext("2d");
    x.fillStyle = bgOf(l); x.fillRect(0, 0, W, H);
    x.font = `600 ${fs}px "Pretendard Variable", Pretendard, "Malgun Gothic", sans-serif`;
    const LW = 932, lines = text ? wrapLines(x, text, 1040) : [];
    const gap = h + 40 + 2 + 62, first = gap + fs * 0.81;
    const top = Math.round((H - (lines.length ? gap + 50 * 0.88 : h)) / 2);
    x.drawImage(img, (W - w) / 2, top, w, h);
    if (!lines.length) return;
    const g = x.createLinearGradient((W - LW) / 2, 0, (W + LW) / 2, 0); // 시안의 가로선 (taste-skill-ignore)
    g.addColorStop(0, "rgba(255,255,255,.1)"); g.addColorStop(.5, "#FFFFFF"); g.addColorStop(1, "rgba(255,255,255,.1)");
    x.fillStyle = g; x.fillRect((W - LW) / 2, Math.round(top + h + 40), LW, 2);
    x.fillStyle = "#FFFFFF"; x.textAlign = "center"; x.textBaseline = "alphabetic";
    lines.forEach((t, i) => x.fillText(t, W / 2, top + first + i * lh));
  }
  async function ogBlob(l, text) {
    const c = document.createElement("canvas"); c.width = 1200; c.height = 630;
    await drawOg(c, l, text);
    return new Promise(ok => c.toBlob(ok, "image/png"));
  }
  const ogText = () => (art.text[art.l.id] ?? OG_TEXT[art.l.id] ?? OG_GROUP[art.l.group] ?? OG_DEFAULT).trim();
  const absUrl = n => /^https?:/.test(art.l.url || "") ? new URL(n, art.l.url).href : "/" + n;
  function headCode() {
    const l = art.l, t = ogText();
    return [
      `<link rel="icon" href="/favicon.ico" sizes="48x48">`,
      `<link rel="icon" href="/favicon.svg" type="image/svg+xml">`,
      `<link rel="apple-touch-icon" href="/apple-touch-icon.png">`,
      `<link rel="manifest" href="/site.webmanifest">`,
      `<meta property="og:title" content="${esc(l.name)}">`,
      t ? `<meta property="og:description" content="${esc(t.replace(/\s*\n\s*/g, " "))}">` : "",
      `<meta property="og:image" content="${esc(absUrl("og-image.png"))}">`,
      `<meta property="og:image:width" content="1200">`,
      `<meta property="og:image:height" content="630">`,
    ].filter(Boolean).join("\n") + "\n";
  }
  const manifest = () => JSON.stringify({
    name: art.l.name, short_name: art.l.name,
    icons: [192, 512].map(n => ({ src: `/icon-${n}.png`, sizes: `${n}x${n}`, type: "image/png" })),
    theme_color: art.kind === "symbol" ? APPLE_FILL[art.l.id] || bgOf(art.l) : bgOf(art.l), background_color: "#FFFFFF",
  }, null, 2) + "\n";

  const uid = (svg, k) => svg.replace(/(id="|url\(#)([\w-]+)/g, `$1$2-${k}`); // 같은 그림을 여러 번 넣으므로 이름이 겹치지 않게
  // 서비스 고르기: 바에서 펼치는 판 — 그룹으로 좁히기 + 그룹별 로고 타일(한 줄에 그룹 이름 + 타일)
  const PICK_GROUPS = ["ci", "b2b", "contract", "fund", "index", "b2c"];
  const pick = { g: "all" };
  const PICK_K = 0.5; // 타일 로고도 모두 같은 배율
  // 로고 옆 작은 글자: 로고만으로 구별이 안 되는 것(예: 개선 로고)은 이름을, 심볼이 있으면 "심볼"
  const tileNote = l => { const extra = (l.name.match(/\(.+\)/) || [""])[0]; return (extra ? `<span class="tile-nm">${esc(extra)}</span>` : "") + (SYM[l.id] ? '<em class="tile-sym">심볼</em>' : ""); };
  function renderPick() {
    $("#artGroups").innerHTML = [["all", "전체", artList.length]].concat(PICK_GROUPS.map(g => [g, INFO[g].menu, artList.filter(l => l.group === g).length]))
      .map(([g, n, c]) => `<button type="button" data-g="${g}" aria-pressed="${pick.g === g}">${g === "all" ? "" : `<i class="chip" style="background:${dotOf(g)}"></i>`}${n}<span>${c}</span></button>`).join("");
    $("#artList").innerHTML = PICK_GROUPS.filter(g => pick.g === "all" || g === pick.g).map(g => {
      const items = artList.filter(l => l.group === g);
      return items.length ? `<div class="pick-g"><h3>${INFO[g].menu}</h3><div class="tiles">${items.map(l => `<button type="button" class="tile" data-id="${l.id}" aria-pressed="${l.id === art.l.id}" aria-label="${esc(l.name)}${SYM[l.id] ? " · 심볼 있음" : ""}">
        <span class="tile-logo" aria-hidden="true">${uid(at(l.svg, l, PICK_K), "p-" + l.id)}</span><span class="tile-tags" aria-hidden="true">${tileNote(l)}</span></button>`).join("")}</div></div>` : "";
    }).join("");
  }
  const panel = $("#artPanel"), pickBtn = $("#artPickBtn");
  function openPick(open) {
    panel.hidden = !open; pickBtn.setAttribute("aria-expanded", open);
    if (open) { renderPick(); fitTiles(); ($("#artList .tile[aria-pressed=true]") || $("#artList .tile")).focus(); }
  }
  // 타일 크기 통일: 전체 서비스 중 가장 긴 타일(로고 + 옆 표시)의 폭에 모두 맞춤. 판이 보일 때 한 번 재고 기억
  let tileW = 0;
  function fitTiles() {
    if (!tileW) {
      const keep = pick.g; pick.g = "all"; renderPick();
      tileW = Math.ceil(Math.max(...[...document.querySelectorAll("#artList .tile")].map(t => t.getBoundingClientRect().width)));
      pick.g = keep; renderPick();
    }
    $("#artList").style.setProperty("--tile-w", tileW + "px");
  }
  pickBtn.addEventListener("click", () => openPick(panel.hidden));
  $("#artGroups").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { pick.g = b.dataset.g; renderPick(); } });
  $("#artList").addEventListener("click", e => {
    const t = e.target.closest(".tile"); if (!t) return;
    chooseService(t.dataset.id); openPick(false); pickBtn.focus();
  });
  $("#artList").addEventListener("keydown", e => { // 화살표로 타일 사이 이동
    const tiles = [...document.querySelectorAll("#artList .tile")], i = tiles.indexOf(document.activeElement);
    if (i < 0) return;
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]; if (!step) return;
    e.preventDefault();
    tiles[Math.max(0, Math.min(i + step, tiles.length - 1))].focus();
  });
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !panel.hidden) { openPick(false); pickBtn.focus(); } });
  // 판 밖을 누르면 닫음 (판 안의 단추는 누르면 다시 그려지므로 누른 순간의 경로로 판단)
  document.addEventListener("click", e => { if (!panel.hidden && !e.composedPath().some(n => n.id === "artPick")) openPick(false); });
  function renderArt() {
    const l = art.l, svg = artSvg();
    $("#artKind").hidden = !SYM[l.id];
    $("#artKind").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.k === art.kind));
    $("#artCurIc").innerHTML = uid(sizedTo(svg, 36), "cur");
    $("#artCurName").textContent = l.name;
    $("#artNote").innerHTML = art.kind === "symbol" ? `서비스 심볼: ${esc(SYM[l.id].desc)}`
      : `<i class="chip" style="background:${bgOf(l)}"></i>${INFO[l.group].menu} 컬러 ${bgOf(l)} + 전용서체 Fn`;
    $("#artIcons").innerHTML = ICON_SIZES.filter(n => n < 512).map(n => `<figure>${uid(sizedTo(svg, n), n)}<figcaption>${n}px</figcaption></figure>`).join("");
    $("#appleKind").hidden = !SYM[l.id];
    $("#appleKind").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.k === apple.kind));
    ["#appleText", "#appleSize", "#appleSizeNum"].forEach(q => $(q).disabled = apple.kind === "symbol");
    const a = appleSvg();
    $("#artApple").innerHTML = `<figure>${uid(sizedTo(a, 180), "a1")}<figcaption>받는 파일 · 180px</figcaption></figure>`
      + `<figure class="ios">${uid(sizedTo(a, 120), "a2")}<figcaption>아이폰 홈 화면</figcaption></figure>`
      + `<figure class="android">${uid(sizedTo(a, 120), "a3")}<figcaption>안드로이드 홈 화면</figcaption></figure>`;
    const input = $("#artText");
    if (document.activeElement !== input) input.value = ogText();
    drawOg($("#artOg"), l, ogText());
    $("#artCode").textContent = headCode();
    $("#artAll").innerHTML = `${icon}${esc(l.name)} 전체 받기 (ZIP)`;
  }
  function chooseService(id) {
    art.l = L[id]; art.kind = SYM[art.l.id] ? "symbol" : "fn";
    // 서비스를 바꾸면 기본값으로: 오픈 그래프 글자 50px, 애플 아이콘 심볼(있으면)·이니셜 Fn·크기 100%
    art.ogSize = $("#ogSize").value = $("#ogSizeNum").value = 50;
    apple.kind = SYM[art.l.id] ? "symbol" : "text"; apple.text = $("#appleText").value = "Fn";
    apple.size = $("#appleSize").value = $("#appleSizeNum").value = 100;
    renderArt();
  }
  $("#artKind").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { art.kind = b.dataset.k; renderArt(); } });
  $("#artText").addEventListener("input", e => { art.text[art.l.id] = e.target.value; renderArt(); });
  $("#appleKind").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { apple.kind = b.dataset.k; renderArt(); } });
  $("#appleText").addEventListener("input", e => {
    apple.text = e.target.value; renderArt();
    const miss = [...e.target.value.trim()].filter(c => !window.FONT_DATA.cmap[c]);
    if (miss.length) toast("서체에 없는 글자는 빠집니다: " + miss.join(" "));
  });
  function pairInputs(range, num, min, max, def, set) {
    range.addEventListener("input", () => { num.value = range.value; set(Number(range.value)); });
    num.addEventListener("input", () => { const v = Number(num.value); if (v >= min && v <= max) { range.value = v; set(v); } });
    num.addEventListener("change", () => { const v = Math.min(max, Math.max(min, Math.round(Number(num.value)) || def)); range.value = num.value = v; set(v); });
  }
  pairInputs($("#ogSize"), $("#ogSizeNum"), 28, 72, 50, v => { art.ogSize = v; renderArt(); });
  pairInputs($("#appleSize"), $("#appleSizeNum"), 50, 150, 100, v => { apple.size = v; renderArt(); });
  $("#appleDl").addEventListener("click", async () => save(await iconPng(appleSvg(), 180), `${art.l.id}-apple-touch-icon.png`)); // 채널톡 아이콘과 같은 180px
  // 터치 아이콘 ZIP: 한 파일 안에서 아이폰·안드로이드 폴더를 나눔
  //   iphone/  180 아이폰 · 167 아이패드 프로 · 152 아이패드 · 120 옛 아이폰
  //   android/ 192 · 512 (같은 그림을 정사각형으로, 모양은 기기가 원형 등으로 깎음)
  $("#appleZip").addEventListener("click", async () => {
    const svg = appleSvg(), dir = `${art.l.id}-touch-icon/`, files = [];
    for (const n of [180, 167, 152, 120]) files.push({ name: `${dir}iphone/apple-touch-icon-${n}x${n}.png`, blob: await iconPng(svg, n) });
    for (const n of [192, 512]) files.push({ name: `${dir}android/android-chrome-${n}x${n}.png`, blob: await iconPng(svg, n) });
    save(await makeZip(files), `${art.l.id}-touch-icon.zip`);
  });
  const artBase = () => art.l.id + (art.kind === "symbol" ? "-symbol" : "-fn");
  $("#artIconDl").addEventListener("click", async e => {
    const b = e.target.closest("button"); if (!b) return;
    const svg = artSvg();
    if (b.dataset.a === "ico") save(await icoBlob(svg), `${art.l.id}-favicon.ico`);
    if (b.dataset.a === "icon") save(await icoBlob(svg, [16, 24, 32, 48, 64, 128, 256, 512]), `${artBase()}-icon.ico`);
    if (b.dataset.a === "svg") save(new Blob([svg], { type: "image/svg+xml" }), `${artBase()}-icon.svg`);
    if (b.dataset.a === "png") { // 모든 크기 PNG 를 압축 파일 하나로 (icon.ico 와 같은 8개 크기)
      const dir = `${artBase()}-icon-png/`, files = [];
      for (const n of [16, 24, 32, 48, 64, 128, 256, 512]) files.push({ name: `${dir}icon-${n}.png`, blob: await iconPng(svg, n) });
      save(await makeZip(files), `${artBase()}-icon-png.zip`);
    }
  });
  $("#artOgDl").addEventListener("click", async () => save(await ogBlob(art.l, ogText()), `${art.l.id}-og-image.png`));
  $("#artAll").addEventListener("click", async () => {
    const btn = $("#artAll"); if (btn.disabled) return;
    btn.disabled = true; btn.textContent = "파일을 묶는 중…";
    try {
      const svg = artSvg(), dir = `${art.l.id}-web-icons/`, text = (s, type) => new Blob([s], { type });
      const files = [
        { name: dir + "favicon.ico", blob: await icoBlob(svg) },
        { name: dir + "favicon.svg", blob: text(svg, "image/svg+xml") },
        { name: dir + "apple-touch-icon.png", blob: await iconPng(appleSvg(), 180) },
        { name: dir + "icon-192.png", blob: await iconPng(svg, 192) },
        { name: dir + "icon-512.png", blob: await iconPng(svg, 512) },
        { name: dir + "og-image.png", blob: await ogBlob(art.l, ogText()) },
        { name: dir + "site.webmanifest", blob: text(manifest(), "application/manifest+json") },
        { name: dir + "head.html", blob: text(headCode(), "text/html") },
      ];
      for (const n of ICON_SIZES) files.push({ name: `${dir}icons/icon-${n}.png`, blob: await iconPng(svg, n) });
      save(await makeZip(files), `${art.l.id}-web-icons.zip`);
    } finally { btn.disabled = false; renderArt(); }
  });
  art.kind = SYM[art.l.id] ? "symbol" : "fn";
  apple.kind = SYM[art.l.id] ? "symbol" : "text";
  document.fonts.ready.then(renderArt);

  // ---------- 사용 규칙: 배경 조합 ----------
  const PAIRS = [
    ["회사 CI", "FnWine", ["#94243A"], "8.16", true, "흰 배경 / FnWine·FnDarkGray 배경에 흰색 버전"],
    ["B2B 대표상품 · 개선 로고", "FnRed 2025", ["#B9023D"], "6.69", true, "흰 배경 / FnRed 배경에 흰색 버전"],
    ["지수", "Index", ["#45B792"], "2.49", false, "어두운 배경(#1C1C3A)과 조합"],
    ["펀드", "Fund", ["#0C3178"], "12.17", true, "흰 배경 / Fund 배경에 흰색 버전"],
    ["B2B 계약상품", "Contract", ["#1C1C3A"], "16.45", true, "흰 배경 / 어두운 배경에 흰색 버전"],
    ["B2C · 리타민", "주", ["#1C1C3A"], "16.45", true, "흰 배경 / 주 색상 배경에 흰색 버전"],
    ["B2C · 리타민", "보조", ["#26C0D2"], "2.20", false, "보조 색상은 흰 배경 글자에 쓰지 않음"],
    ["B2C · WiseReport", "WiseReport", ["#594FC8"], "6.22", true, "흰 배경 / WiseReport 배경에 흰색 버전"],
    ["B2C · API", "API", ["#2457C5"], "6.47", true, "흰 배경 / API 배경에 흰색 버전"],
  ];
  $("#pairs").innerHTML = `<ul class="pair-list">${PAIRS.map(([g, n, [c], r, ok, rec]) => `<li>
    <span class="pair-sw"><span style="background:${c}">Fn</span><span style="color:${c}">Fn</span></span>
    <span class="pair-name"><b>${g}</b><span>${n} ${c}</span></span>
    <span class="pair-ratio ${ok ? "ok" : "warn"}"><b>${r}</b>${ok ? "본문까지 가능" : "흰 배경 비권장"}</span>
    <span class="pair-rec">${rec}</span></li>`).join("")}</ul>`;

  document.addEventListener("click", e => { // 같은 화면 안의 회차로 부드럽게 이동
    const a = e.target.closest("a.jump"); if (!a) return;
    e.preventDefault(); document.querySelector(a.getAttribute("href")).scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
  });

  // ---------- 등장 ----------
  const io = "IntersectionObserver" in window && !reduce ? new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }), { rootMargin: "0px 0px -8% 0px" }) : null;
  function reveal(root) {
    if (!io) return;
    root.querySelectorAll(".reveal .wrap > *, .reveal > figure, .reveal > .intro-text > *, .mods > *, .lineup > li, .rows > .row, .figs > figure, .g-sec > h2, .g-sec > .sub").forEach(el => {
      if (el.dataset.r !== undefined) return;
      const sibs = [...el.parentElement.children];
      el.style.setProperty("--i", Math.min(sibs.indexOf(el), 6));
      el.dataset.r = ""; io.observe(el);
    });
  }

  // ---------- 쪽 넘기기 ----------
  function route() {
    let [page, sub] = (location.hash.slice(1) || "home").split("/");
    if (!["home", "font", "logo", "download", "article", "rules"].includes(page)) page = "home";
    if (page === "logo") renderGroup(ORDER.includes(sub) ? sub : "b2b");
    const fsub = page === "font" && ["update", "critique"].includes(sub) ? sub : "";
    const shown = fsub || page;
    document.querySelectorAll("section.page").forEach(s => s.classList.toggle("on", s.id === "page-" + shown));
    document.querySelectorAll('[data-tabs="font"]').forEach(n => n.innerHTML = fontTabs(fsub ? "font/" + fsub : "font"));
    document.querySelectorAll('[data-tabs="logo"]').forEach(n => n.innerHTML = logoTabs("download"));
    document.querySelectorAll("#links a").forEach(a => {
      const on = (a.dataset.page || a.getAttribute("href").slice(1)).split(" ").includes(page);
      on ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current");
    });
    bar.classList.remove("open"); $("#menuWord").setAttribute("aria-expanded", "false"); $("#menuWord").textContent = "메뉴";
    if (page === "font") syncSize();
    window.scrollTo(0, 0);
    const cur = document.querySelector(".page.on > .tabs [aria-current]"); // 휴대폰에서 고른 메뉴가 보이게 옆으로 맞춤
    if (cur) cur.parentElement.scrollLeft = cur.offsetLeft - 16;
    reveal($("#page-" + shown));
  }
  addEventListener("hashchange", route);
  route();
})();
