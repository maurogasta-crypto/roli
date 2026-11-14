// pruebas-reglas-vivas.mjs — (14-nov-2026) comprueba contra la base REAL lo que las reglas publicadas tienen que negar, y lo que dejan leer. No deja documentos.
// Necesita FB_PANEL_MAIL y FB_PANEL_CLAVE (o los que use el agente) en el entorno:  node pruebas-reglas-vivas.mjs
// Prueba contra la base REAL de Roli lo que las reglas publicadas tienen que NEGAR (no deja documentos) y lo que dejan leer.
const K = "AIzaSyBJHfPcCoYZkm7As--nMxeVieqFEKduAMk", P = "roli-467a4";
const base = `https://firestore.googleapis.com/v1/projects/${P}/databases/(default)/documents`;
const r = await fetch("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + K, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email: process.env.FB_PANEL_MAIL, password: process.env.FB_PANEL_CLAVE, returnSecureToken: true }) });
const { idToken, localId } = await r.json();
const S = (s) => ({ stringValue: s }), N = (n) => ({ integerValue: String(n) });
async function llamar(m, ruta, token, cuerpo) {
  const res = await fetch(base + ruta, { method: m, headers: { "content-type": "application/json", ...(token ? { authorization: "Bearer " + token } : {}) }, body: cuerpo ? JSON.stringify({ fields: cuerpo }) : undefined });
  return res.status;
}
const casos = [
  ["sin sesión NO lee notas", () => llamar("GET", "/notas", null), 403],
  ["sin sesión NO crea una nota", () => llamar("POST", "/notas", null, { titulo: S("x"), texto: S("x"), uid: S("x"), por: S("x"), creado: N(1) }), 403],
  ["el agente NO crea una nota con un campo de más", () => llamar("POST", "/notas", idToken, { titulo: S("x"), texto: S("x"), uid: S(localId), por: S("x"), creado: N(1), extra: S("no") }), 403],
  ["el agente NO crea una nota a nombre de otro", () => llamar("POST", "/notas", idToken, { titulo: S("x"), texto: S("x"), uid: S("otro"), por: S("x"), creado: N(1) }), 403],
  ["el agente NO escribe una ficha en usuarios", () => llamar("PATCH", "/usuarios/probe-agente", idToken, { activo: { booleanValue: true } }), 403],
  ["una colección inventada está cerrada", () => llamar("GET", "/coleccion-inventada", idToken), 403],
  ["el agente LEE partidas", () => llamar("GET", "/partidas", idToken), 200],
  ["el agente LEE jugadores", () => llamar("GET", "/jugadores", idToken), 200],
  ["el agente LEE usuarios (las fichas sólo dicen rol y nombre)", () => llamar("GET", "/usuarios", idToken), 200],
];
let mal = 0;
for (const [n, f, esperado] of casos) { const s = await f(); const ok = s === esperado; if (!ok) mal++; console.log((ok ? "  ✓ " : "  ✖ ") + n + " → " + s + (ok ? "" : " (esperaba " + esperado + ")")); }
const u = await fetch(base + "/usuarios", { headers: { authorization: "Bearer " + idToken } }).then((x) => x.json());
console.log("fichas en usuarios:", (u.documents || []).map((d) => `${d.name.split("/").pop().slice(0, 6)}… ${d.fields.rol && d.fields.rol.stringValue} ${d.fields.activo && d.fields.activo.booleanValue}`).join(" | ") || "ninguna todavía");
process.exit(mal ? 1 : 0);
