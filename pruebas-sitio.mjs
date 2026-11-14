// pruebas-sitio.mjs — el banco del sitio privado de Roli (index.html, registro.js, firebase-init.js,
// firestore.rules). Sin npm ni red:  node pruebas-sitio.mjs
import fs from "node:fs";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import * as R from "./registro.js";

let ok = 0, mal = 0;
const t = (n, f) => { try { f(); ok++; console.log("  ✓ " + n); } catch (e) { mal++; console.log("  ✖ " + n + "\n      " + e.message); } };
const leer = (f) => fs.readFileSync(new URL(f, import.meta.url), "utf8");
const reglas = leer("./firestore.rules"), html = leer("./index.html"), init = leer("./firebase-init.js"), ino = leer("./firmware/roli_programa.ino"), cero = leer("./firmware/calibracion_cero.txt");

t("lee la lista de «calibrar exportar» y no guarda lo que no conoce", () => {
  const c = R.leerCalibracion("=== CALIBRACION ===\nprograma: NIVEL 6 MAPA 1 calibrar-v1\nVEL_IZQ_INICIAL 92\nVEL_DER_INICIAL 86\nHOLA 5\ncalibrar velocidad 92 86\nalgo raro\n=== FIN ===");
  assert.deepEqual(c.valores, { VEL_IZQ_INICIAL: 92, VEL_DER_INICIAL: 86 }); assert.equal(c.programa, "NIVEL 6 MAPA 1 calibrar-v1");
  assert.deepEqual(c.ignoradas, ["HOLA 5", "algo raro"]); assert.deepEqual(c.problemas, []);
  assert.deepEqual(R.leerCalibracion("").valores, {}); assert.deepEqual(R.leerCalibracion(null).valores, {});
});
t("un valor fuera de rango es un problema y no un dato", () => {
  const c = R.leerCalibracion("KICK_VEL 99999\nKICK_MS -4"); assert.deepEqual(c.valores, {}); assert.equal(c.problemas.length, 2); assert.equal(c.ignoradas.length, 0);
});
t("el cero del sitio es el cero del robot: los mismos nombres y valores que calibracion_cero.txt y el .ino", () => {
  const f = R.leerCalibracion(cero); assert.deepEqual(f.valores, R.CERO); assert.deepEqual(Object.keys(f.valores).sort(), [...R.PARAMETROS].sort());
  for (const k of R.PARAMETROS) assert.ok(new RegExp("\\b" + k + "\\b").test(ino), k + " no está en el .ino");
});
t("las diferencias con el cero", () => {
  assert.deepEqual(R.diferencias(R.CERO), []); assert.deepEqual(R.diferencias({ VEL_IZQ_INICIAL: 92, KICK_VEL: 160 }), [{ k: "VEL_IZQ_INICIAL", antes: 90, ahora: 92 }]);
});
t("los documentos llevan exactamente los campos que dejan las reglas", () => {
  const u = { uid: "u1", nombre: "Mauro" };
  const campos = (col) => { const m = reglas.match(new RegExp("match /" + col + "/\\{id\\}[\\s\\S]*?hasOnly\\(\\[([^\\]]+)\\]")); assert.ok(m, col); return m[1].split(",").map((x) => x.trim().replace(/'/g, "")).sort(); };
  assert.deepEqual(Object.keys(R.docCalibracion(R.leerCalibracion("KICK_VEL 150"), u, 1)).sort(), campos("calibraciones"));
  assert.deepEqual(Object.keys(R.docPartida({ juego: "j", equipo: ["a", "b"], estrellas: 3 }, u, 1)).sort(), campos("partidas"));
  assert.deepEqual(Object.keys(R.docNota({ titulo: "t", texto: "x" }, u, 1)).sort(), campos("notas"));
});
t("lo que no tiene sentido no se arma: calibración vacía, partida sin juego o con un solo jugador, nota sin título", () => {
  const u = { uid: "u1", nombre: "M" };
  assert.throws(() => R.docCalibracion(R.leerCalibracion("nada"), u)); assert.throws(() => R.docPartida({ equipo: ["a", "b"] }, u));
  assert.throws(() => R.docPartida({ juego: "j", equipo: ["a"] }, u)); assert.throws(() => R.docNota({ titulo: " " }, u));
  const p = R.docPartida({ juego: "j", equipo: ["a", " ", "b"], estrellas: "x", medidas: { segundosPorMetro: "2.2", giro90: "-1" } }, u, 5);
  assert.equal(p.estrellas, 0); assert.deepEqual(p.equipo, ["a", "b"]); assert.equal(p.medidas.segundosPorMetro, 2.2); assert.equal(p.medidas.giro90, null);
});
t("entra sólo una ficha activa", () => { assert.ok(R.puedeEntrar({ activo: true })); assert.ok(!R.puedeEntrar({ activo: "true" })); assert.ok(!R.puedeEntrar(null)); assert.ok(!R.puedeEntrar({})); });
t("las reglas: UID sólo como marcadores, deny por defecto, nadie edita, y ninguna lectura abierta", () => {
  assert.ok(reglas.includes('"TU-UID-ACA"') && reglas.includes('"UID-DEL-AGENTE"'));
  assert.ok(!/uid == "[A-Za-z0-9]{20,}"/.test(reglas), "un UID real en las reglas");
  assert.ok(!/if true/.test(reglas), "hay una regla abierta"); assert.ok(!/match \/\{document=\*\*\}/.test(reglas));
  for (const c of ["calibraciones", "partidas", "notas"]) assert.ok(new RegExp("match /" + c + "/\\{id\\}[\\s\\S]*?allow update: if false").test(reglas), c + " se puede editar");
  assert.ok(/match \/_historial[\s\S]*allow update, delete: if false/.test(reglas));
});
t("el SDK sólo se toca en firebase-init.js, diferido, y es el proyecto roli-467a4", () => {
  assert.ok(!/from\s+["']https:\/\/www\.gstatic/.test(html) && !/gstatic/.test(html), "index.html toca gstatic");
  assert.ok(/import\(SDK \+/.test(init) && !/^import .*gstatic/m.test(init)); assert.ok(init.includes('projectId: "roli-467a4"'));
  assert.ok(!/service_account|private_key|client_secret/i.test(init + html));
});
t("el JavaScript de index.html y los módulos parsean como MÓDULO", () => {
  const s = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
  for (const [n, c] of [["index.html", s], ["registro.js", leer("./registro.js")], ["firebase-init.js", init]]) {
    try { execFileSync("node", ["--input-type=module", "--check"], { input: c, stdio: ["pipe", "pipe", "pipe"] }); } catch (e) { throw new Error(n + ": " + String(e.stderr).split("\n").slice(0, 3).join(" ")); }
  }
});
t("la contraseña tiene su ojo y el sitio dice que es privado", () => { assert.ok(html.includes("ojos.js")); assert.ok(html.includes('name="robots"') || html.includes("noindex")); });
t("hay publicación propia de Pages y no consume secretos", () => { const w = leer("./.github/workflows/pages.yml"); assert.ok(w.includes("deploy-pages") && !/secrets\./.test(w)); });

console.log(`\n${ok} pasadas, ${mal} fallidas`); process.exit(mal ? 1 : 0);
