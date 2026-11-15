/* ═══════════════════════════════════════════════════════════════════════
   registro.js — la lógica del registro privado de Roli, SIN DOM NI RED.
   Sello: registro-2 (15-nov-2026: `cambiosJugador`, para corregir a una persona). Se prueba con `node pruebas-sitio.mjs`.

   Lo que se guarda en la base `roli-467a4` (detrás del login):
     · calibraciones/{id}  — la lista que imprime `calibrar exportar` en el robot
     · partidas/{id}       — una ronda de juego: equipo, juego, estrellas, medidas
     · notas/{id}          — lo que se aprende y no cabe en un campo
   La razón de la base: nombres de los chicos, medidas del robot de cada día y
   notas de desarrollo no pueden estar en un repositorio público ni en el
   navegador de la tablet.
   ═══════════════════════════════════════════════════════════════════════ */
export const VERSION = "registro-2";

/* Los nombres de la calibración son los mismos que las constantes del .ino y
   los de firmware/calibracion_cero.txt: si cambia uno allá, cambia acá. */
export const PARAMETROS = [
  "VEL_IZQ_INICIAL", "VEL_DER_INICIAL", "KICK_VEL", "KICK_MS",
  "ENDEREZAR_GOLPES", "ENDEREZAR_FUERZA", "ENDEREZAR_MS", "ENDEREZAR_PAUSA_MS",
  "ZIG_DELTA", "ZIG_PULSO", "GIRO_MS_POR_GRADO",
];

export const CERO = { VEL_IZQ_INICIAL: 90, VEL_DER_INICIAL: 84, KICK_VEL: 160, KICK_MS: 150, ENDEREZAR_GOLPES: 4, ENDEREZAR_FUERZA: 160, ENDEREZAR_MS: 60, ENDEREZAR_PAUSA_MS: 60, ZIG_DELTA: 12, ZIG_PULSO: 45, GIRO_MS_POR_GRADO: 8 };

export const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

/** Lee el texto de `calibrar exportar`. Devuelve { valores, programa, ignoradas, problemas }.
 *  Sólo acepta nombres conocidos con un número entero; lo demás se cuenta, no se guarda. */
export function leerCalibracion(texto) {
  const valores = {}, ignoradas = [], problemas = [];
  let programa = "";
  for (const crudo of String(texto || "").split(/\r?\n/)) {
    const l = crudo.trim();
    if (!l || l.startsWith("===") || l.startsWith("#")) continue;
    const p = l.match(/^programa:\s*(.+)$/i);
    if (p) { programa = p[1].slice(0, 80); continue; }
    const m = l.match(/^([A-Z_]+)\s+(-?\d+)$/);
    if (m && PARAMETROS.includes(m[1])) {
      const n = Number(m[2]);
      if (n < 0 || n > 5000) problemas.push(m[1] + " fuera de rango: " + n); else valores[m[1]] = n;
    } else if (/^calibrar\s/.test(l) || /^para volver/i.test(l)) { /* las órdenes equivalentes: no se guardan */ }
    else ignoradas.push(l.slice(0, 60));
  }
  return { valores, programa, ignoradas, problemas };
}

/** Qué cambió respecto del cero de fábrica (o de otra calibración). */
export function diferencias(valores, base = CERO) {
  return PARAMETROS.filter((k) => valores[k] != null && base[k] != null && valores[k] !== base[k]).map((k) => ({ k, antes: base[k], ahora: valores[k] }));
}

/** El documento de una calibración, con sólo los campos que dejan las reglas. */
export function docCalibracion({ valores, programa }, { uid, nombre, nota = "" }, ahora = Date.now()) {
  if (!Object.keys(valores).length) throw new Error("No encontré ningún valor de calibración en ese texto.");
  return { valores, programa: programa || "", nota: String(nota).slice(0, 300), uid, por: String(nombre || "").slice(0, 40), creado: ahora };
}

/** Una persona que juega. Es información de personas (a veces de chicos): sólo detrás del login. */
export function docJugador({ nombre, edad, nota }, { uid, nombre: por }, ahora = Date.now()) {
  const n = String(nombre || "").trim();
  if (!n) throw new Error("Falta el nombre.");
  const e = Number(edad);
  return { nombre: n.slice(0, 20), edad: Number.isFinite(e) && e > 0 && e < 120 ? Math.round(e) : null, nota: String(nota || "").slice(0, 200), activo: true, uid, por: String(por || "").slice(0, 40), creado: ahora };
}

/** Lo que cambia al corregir a una persona: sólo nombre, edad y nota (el dueño, la fecha y `activo` no se tocan).
 *  Mismas reglas de forma que `docJugador`. */
export function cambiosJugador({ nombre, edad, nota }) {
  const n = String(nombre || "").trim();
  if (!n) throw new Error("Falta el nombre.");
  const e = Number(edad);
  return { nombre: n.slice(0, 20), edad: edad !== "" && edad != null && Number.isFinite(e) && e > 0 && e < 120 ? Math.round(e) : null, nota: String(nota || "").slice(0, 200) };
}

/** Una partida: se crea al empezar a jugar y se va completando ronda por ronda.
 *  `rondas`: { <idRonda>: { intentos, logrado } } · `hechos`: { "<idRonda>:<paso>": true }. */
export function docPartida({ juego, equipo, jugadores, meta, medidas, nota }, { uid, nombre }, ahora = Date.now()) {
  const eq = (equipo || []).map((x) => String(x).trim().slice(0, 20)).filter(Boolean).slice(0, 8);
  if (!juego) throw new Error("Falta el juego.");
  if (eq.length < 2) throw new Error("El equipo necesita al menos dos personas.");
  const n = (v) => (v === "" || v == null || !Number.isFinite(Number(v)) || Number(v) < 0 ? null : Number(v));
  return {
    juego: String(juego).slice(0, 60), equipo: eq, jugadores: (jugadores || []).map((x) => String(x).slice(0, 40)).slice(0, 8),
    estrellas: 0, meta: n(meta) ?? 0, estado: "en curso", actual: 0, rondas: {}, hechos: {},
    medidas: { velocidad: n(medidas && medidas.velocidad), segundosPorMetro: n(medidas && medidas.segundosPorMetro), giro90: n(medidas && medidas.giro90) },
    nota: String(nota || "").slice(0, 400), uid, por: String(por_(nombre)), creado: ahora, fin: null,
  };
}
const por_ = (x) => String(x || "").slice(0, 40);

export function docNota({ titulo, texto }, { uid, nombre }, ahora = Date.now()) {
  const t = String(titulo || "").trim(), x = String(texto || "").trim();
  if (!t) throw new Error("Falta el título.");
  return { titulo: t.slice(0, 80), texto: x.slice(0, 2000), uid, por: String(nombre || "").slice(0, 40), creado: ahora };
}

/** ¿Puede entrar esta ficha? Es la misma cuenta que hacen las reglas (`activo()`). */
export const puedeEntrar = (ficha) => !!(ficha && ficha.activo === true);

export const fecha = (ms) => { try { return new Date(ms).toLocaleString("es-UY", { dateStyle: "short", timeStyle: "short" }); } catch (e) { return ""; } };
