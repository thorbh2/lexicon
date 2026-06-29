import { makeReader, write, connectWallet, activeAccount, balanceOf, short, toGen, GEN, fmtErr }
  from "./shared/genlayer-lite.js";

const CONTRACT = "0xBDa72fA79808d9221bA33D7223E9d1a5187E60A7";
const { read } = makeReader(CONTRACT);
const PENDING = 0, PUBLISHED = 1, REJECTED = 2;
const STLABEL = ["Pending", "Published", "Rejected"];
const STCLS = ["ps-pending", "ps-published", "ps-rejected"];
let account = null, posts = [], coc = "";
const $ = (id) => document.getElementById(id);
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

$("contractLink").textContent = "Contract " + short(CONTRACT);

function toast(msg, kind = "", title = "lexicon") {
  const el = document.createElement("div"); el.className = "toast " + kind;
  el.innerHTML = `<span class="tt">${title}</span>`; el.appendChild(document.createTextNode(msg));
  $("log").appendChild(el); setTimeout(() => el.remove(), kind === "err" ? 15000 : 5000);
}

async function refreshWallet() {
  account = await activeAccount();
  const slot = $("walletslot");
  if (account) { let bal = 0n; try { bal = await balanceOf(account); } catch (_) {} slot.innerHTML = `<span class="mono" style="font-size:13px;color:var(--grey)">${short(account)} · ${toGen(bal)} GEN</span>`; }
  else { slot.innerHTML = `<button class="btn ghost sm" id="connectBtn">Connect</button>`; $("connectBtn").onclick = doConnect; }
}
async function doConnect() { try { account = await connectWallet(); toast("Connected on studionet.", "ok"); await refreshWallet(); } catch (e) { toast(fmtErr(e), "err"); } }
async function ensureWallet() { if (!account) account = await connectWallet(); await refreshWallet(); }

async function load() {
  try {
    coc = await read("get_code");
    $("cocText").textContent = coc && coc.trim() ? coc : "No code of conduct set yet.";
    const count = Number(await read("get_post_count"));
    const out = [];
    for (let i = 0; i < count; i++) out.push({ id: i, ...(await read("get_post", [i])) });
    posts = out; renderFeed();
    $("stTotal").textContent = count;
    $("stPub").textContent = out.filter((p) => Number(p.status) === PUBLISHED).length;
    $("stRej").textContent = out.filter((p) => Number(p.status) === REJECTED).length;
  } catch (e) { $("postList").innerHTML = `<div class="p-empty">Could not reach the chain. ${fmtErr(e)}</div>`; }
}

function renderFeed() {
  const el = $("postList");
  if (!posts.length) { el.innerHTML = `<div class="p-empty">No posts yet. Be the first to write.</div>`; return; }
  el.innerHTML = "";
  [...posts].reverse().forEach((p) => {
    const st = Number(p.status);
    const title = p.body.length > 96 ? p.body.slice(0, 96) + "…" : p.body;
    const item = document.createElement("article"); item.className = "post";
    item.innerHTML = `<div class="post-main">
        <span class="post-status ${STCLS[st]}">${STLABEL[st]}</span>
        <h3 class="post-title">${esc(title)}</h3>
        <div class="post-byline">by <span class="mono">${short(p.author)}</span></div>
        ${st === REJECTED && p.reason ? `<div class="post-reason">${esc(p.reason)}</div>` : ""}
      </div><i class="ph-bold ph-arrow-right post-arrow"></i>`;
    item.onclick = () => openDetail(p.id);
    el.appendChild(item);
  });
}

function openDrawer() { $("scrim").classList.add("on"); $("drawer").classList.add("on"); }
function closeDrawer() { $("scrim").classList.remove("on"); $("drawer").classList.remove("on"); }

function openNew() {
  $("drawerTitle").textContent = "Post to the feed";
  $("drawerBody").innerHTML = `
    <div class="coc-mini"><div class="cm-h">Code of conduct</div><blockquote>${esc(coc) || "No code of conduct set yet."}</blockquote></div>
    <label>Your post</label><textarea id="nBody" placeholder="Share something with the community…"></textarea>
    <div class="hint">It will be read against the code of conduct before it appears on the feed.</div>
    <button class="btn primary block" id="createBtn"><i class="ph-bold ph-paper-plane-tilt"></i> Submit post</button>`;
  $("createBtn").onclick = doCreate; openDrawer();
}

function openDetail(id) {
  const p = posts.find((x) => x.id === id); if (!p) return;
  const st = Number(p.status);
  $("drawerTitle").textContent = "Post #" + id;
  let verdict = "";
  if (st === PUBLISHED) verdict = `<div class="verdict-box vb-ok"><b>Published.</b> ${p.reason ? esc(p.reason) : "Complies with the code of conduct."}</div>`;
  if (st === REJECTED) verdict = `<div class="verdict-box vb-no"><b>Held back.</b> ${p.reason ? esc(p.reason) : "Violates the code of conduct."}</div>`;
  const actions = st === PENDING
    ? `<button class="btn primary block" id="modBtn"><i class="ph-bold ph-scales"></i> Run AI moderation</button><div class="hint" style="text-align:center;margin-top:8px">Validators read the post against the code. Calls a real LLM.</div>`
    : "";
  $("drawerBody").innerHTML = `
    <div class="d-post">${esc(p.body)}</div>
    ${verdict}
    <div class="kv"><span class="k">Author</span><span class="v mono">${short(p.author)}</span></div>
    <div class="kv"><span class="k">Status</span><span class="v">${STLABEL[st]}</span></div>
    ${p.reason ? `<div class="kv"><span class="k">Reason</span><span class="v">${esc(p.reason)}</span></div>` : ""}
    <div style="margin-top:16px">${actions}</div>`;
  openDrawer();
  if (st === PENDING) $("modBtn").onclick = () => doModerate(id);
}

async function doCreate() {
  const body = $("nBody").value.trim();
  if (!body) return toast("Write something first.", "err");
  const btn = $("createBtn"); btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> submitting';
  try { await ensureWallet(); await write(CONTRACT, "submit_post", [body]); toast("Post submitted — pending moderation.", "ok"); closeDrawer(); await load(); }
  catch (e) { toast(fmtErr(e), "err"); btn.disabled = false; btn.innerHTML = "Submit post"; }
}
async function doModerate(id) {
  if (!confirm("Run AI moderation? Validators read the post against the code of conduct. Calls a real LLM.")) return;
  const btn = $("modBtn"); btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> validators reading';
  try { await ensureWallet(); toast("Validators reading against the code…", "", "moderate"); await write(CONTRACT, "moderate", [id]); toast("Moderated on-chain.", "ok"); closeDrawer(); await load(); }
  catch (e) { toast(fmtErr(e), "err"); if (btn) { btn.disabled = false; btn.textContent = "Run AI moderation"; } }
}

$("heroPostBtn").onclick = openNew;
$("ctaPostBtn").onclick = openNew;
$("navPostBtn").onclick = openNew;
$("refreshBtn").onclick = load;
$("closeDrawer").onclick = closeDrawer;
$("scrim").onclick = closeDrawer;
const _cb = $("connectBtn"); if (_cb) _cb.onclick = doConnect;
if (window.ethereum) window.ethereum.on?.("accountsChanged", refreshWallet);

refreshWallet();
load();

// ====== Subtle ink-particle masthead (Three.js, low-key editorial) ======
(function ink() {
  const canvas = $("inkCanvas"); if (!canvas || !window.THREE) return;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
  camera.position.z = 14;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  function resize() { const w = canvas.clientWidth, h = canvas.clientHeight || 400; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }

  // drifting motes of "ink" — orange + warm grey, very soft
  const N = 160, pos = new Float32Array(N * 3), col = new Float32Array(N * 3), spd = [];
  const c1 = new THREE.Color("#ff6719"), c2 = new THREE.Color("#d9c7b8");
  for (let i = 0; i < N; i++) {
    pos[i*3] = (Math.random() - .5) * 34; pos[i*3+1] = (Math.random() - .5) * 18; pos[i*3+2] = (Math.random() - .5) * 12;
    const c = Math.random() < .35 ? c1 : c2; col[i*3] = c.r; col[i*3+1] = c.g; col[i*3+2] = c.b;
    spd.push({ x: (Math.random() - .5) * .006, y: .004 + Math.random() * .008 });
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ size: .16, vertexColors: true, transparent: true, opacity: .55, sizeAttenuation: true }));
  scene.add(pts);

  resize(); addEventListener("resize", resize);
  let running = true;
  const vis = new IntersectionObserver((es) => { running = es[0].isIntersecting; if (running) loop(); }, { threshold: 0 });
  vis.observe(canvas);
  function loop() {
    if (!running) return;
    requestAnimationFrame(loop);
    const p = g.attributes.position.array;
    for (let i = 0; i < N; i++) {
      p[i*3] += spd[i].x; p[i*3+1] += spd[i].y;
      if (p[i*3+1] > 9) { p[i*3+1] = -9; p[i*3] = (Math.random() - .5) * 34; }
      if (p[i*3] > 17) p[i*3] = -17; if (p[i*3] < -17) p[i*3] = 17;
    }
    g.attributes.position.needsUpdate = true;
    pts.rotation.z += 0.0004;
    renderer.render(scene, camera);
  }
  loop();
})();
