/* ═══════════════════════════════════════════════════════════════════════
   acceso.js — la puerta del sitio de Roli: login, «sin ficha» y arranque.
   Sello: acceso-1 (14-nov-2026). Lo usan index.html y jugar.html: la puerta no
   se duplica (PROTOCOLO-DESARROLLO § 3). Toca Firebase SÓLO por firebase-init.js.

   Tener cuenta no es tener permiso: se entra con una ficha `usuarios/{uid}` con
   `activo: true`, que escribe sólo Mauro (firestore.rules).
   ═══════════════════════════════════════════════════════════════════════ */
import * as I from "./firebase-init.js";
import { esc, puedeEntrar } from "./registro.js";

export const VERSION = "acceso-1";
const DATOS = "https://maurogasta-crypto.github.io/datos/";
let _errores = null;
import(DATOS + "errores.js").then((m) => { _errores = m; }).catch(() => {});
import(DATOS + "ojos.js").catch(() => {});       // el ojo 👁 de las contraseñas; sin él la contraseña anda igual
const PROPIAS = {
  "permission-denied": "La base dijo que no: esta cuenta no tiene permiso para eso. Si es la primera vez, Mauro tiene que activar tu ficha (usuarios/).",
  "sdk-no-baja": "No se pudo cargar Firebase (los servidores de Google): suele ser falta de señal o una red que bloquea ese dominio.",
};
export const explicar = (e) => (_errores ? _errores.explicar(e, PROPIAS) : (PROPIAS[e && e.code] || (e && e.message) || String(e)));

/** Muestra un aviso arriba de `v` que se va solo. */
export function aviso(v, t, tipo = "mal") { const d = document.createElement("div"); d.className = "msj " + tipo; d.textContent = t; v.prepend(d); setTimeout(() => d.remove(), 7000); }

/** Pone la puerta en `v` y llama a `listo({ user, ficha })` cuando hay una ficha activa.
 *  `alSalir()` se llama cuando se cierra la sesión (para soltar escuchas). */
export async function abrir(v, listo, alSalir = () => {}) {
  const $ = (id) => v.querySelector("#" + id);
  let user = null;
  const login = (msj) => {
    alSalir();
    v.innerHTML = '<div class="tarj"><h2>Entrar</h2><form id="f"><label for="m">Mail</label><input id="m" type="email" autocomplete="username" required>'
      + '<label for="c">Contraseña</label><input id="c" type="password" autocomplete="current-password" required>'
      + '<button class="p" type="submit">Entrar</button><button type="button" id="olvide">Olvidé la contraseña</button></form>'
      + (msj ? '<div class="msj mal">' + esc(msj) + "</div>" : "") + "</div>";
    $("f").onsubmit = async (ev) => { ev.preventDefault(); try { await I.signInWithEmailAndPassword(I.auth, $("m").value.trim(), $("c").value); } catch (e) { login(explicar(e)); } };
    $("olvide").onclick = async () => {
      const m = $("m").value.trim(); if (!m) return aviso(v, "Escribí tu mail arriba y volvé a tocar.");
      try { await I.sendPasswordResetEmail(I.auth, m); aviso(v, "Te mandamos un mail para cambiar la contraseña.", "ok"); } catch (e) { aviso(v, explicar(e)); }
    };
  };
  const sinFicha = () => {
    alSalir();
    v.innerHTML = '<div class="tarj"><h2>Tu cuenta todavía no tiene permiso</h2><p>Entraste como <b>' + esc(user.email) + '</b>. Tener cuenta no alcanza: Mauro tiene que activar tu ficha. Pasale este código:</p>'
      + '<p><code>' + esc(user.uid) + '</code></p><p class="gris">(Si sos Mauro, podés crear tu ficha de administrador acá abajo.)</p>'
      + '<button id="mia">Crear mi ficha de administrador</button><button id="salir">Salir</button></div>';
    $("salir").onclick = () => I.signOut(I.auth);
    $("mia").onclick = async () => { try { await I.setDoc(I.doc(I.db, "usuarios", user.uid), { activo: true, rol: "admin", nombre: "Mauro" }); await cargar(); } catch (e) { aviso(v, explicar(e)); } };
  };
  const cargar = async () => {
    let ficha = null;
    try { const s = await I.getDoc(I.doc(I.db, "usuarios", user.uid)); ficha = s.exists() ? s.data() : null; } catch (e) { ficha = null; }
    if (puedeEntrar(ficha)) listo({ user, ficha }); else sinFicha();
  };
  try { await I.cargarFirebase(); } catch (e) { v.innerHTML = '<div class="msj mal">' + esc(explicar(e)) + "</div>"; return; }
  I.onAuthStateChanged(I.auth, (u) => { user = u; if (!u) login(); else cargar(); });
}
