/* ═══════════════════════════════════════════════════════════════════════
   firebase-init.js — EL ÚNICO CONTACTO CON EL SDK DE FIREBASE.
   Sello: init-1 (14-nov-2026)

   Ninguna otra página importa nada de gstatic.com (PROTOCOLO-DESARROLLO § 2,
   repo `maurogasta-crypto/datos`).

   LA CONFIGURACIÓN NO ES UN SECRETO: identifica el proyecto `roli-467a4` ante
   la API web y no da un solo permiso. Lo que da o niega acceso son las reglas
   (`firestore.rules`). Pública por diseño: no hay que rotarla.

   EL SDK SE CARGA DIFERIDO, con `import()` dentro de un try. Un import estático
   deja la página en blanco si gstatic no contesta; así la pantalla abre igual y
   dice qué falta. Lo que se exporta son `let` (enlaces vivos): valen
   `undefined` hasta que `cargarFirebase()` resuelve, así que nada que use
   Firebase puede correr antes de esa espera.
   ═══════════════════════════════════════════════════════════════════════ */

export const VERSION = "init-1";
const SDK = "https://www.gstatic.com/firebasejs/12.16.0/";

export const firebaseConfig = {
  apiKey: "AIzaSyBJHfPcCoYZkm7As--nMxeVieqFEKduAMk",
  authDomain: "roli-467a4.firebaseapp.com",
  projectId: "roli-467a4",
  storageBucket: "roli-467a4.firebasestorage.app",
  messagingSenderId: "874061926322",
  appId: "1:874061926322:web:c4f169f0a9926b1e699eab"
};

export let app, auth, db;
export let onAuthStateChanged, signInWithEmailAndPassword, signOut, sendPasswordResetEmail;
export let doc, getDoc, setDoc, updateDoc, deleteDoc, collection, addDoc, query, orderBy, limit, onSnapshot;
export let cargado = null;

let _promesa = null;
export function cargarFirebase() {
  if (_promesa) return _promesa;
  _promesa = (async () => {
    let mA, mU, mF;
    try {
      [mA, mU, mF] = await Promise.all([
        import(SDK + "firebase-app.js"),
        import(SDK + "firebase-auth.js"),
        import(SDK + "firebase-firestore.js")
      ]);
    } catch (e) {
      const err = new Error("No se pudo cargar Firebase desde gstatic.com. Suele ser falta de señal o una red que bloquea ese dominio.");
      err.code = "sdk-no-baja"; err.causa = e;
      _promesa = null; cargado = false;
      throw err;
    }
    app = mA.getApps().length ? mA.getApp() : mA.initializeApp(firebaseConfig);
    auth = mU.getAuth(app);
    ({ onAuthStateChanged, signInWithEmailAndPassword, signOut, sendPasswordResetEmail } = mU);
    db = mF.getFirestore(app);
    ({ doc, getDoc, setDoc, updateDoc, deleteDoc, collection, addDoc, query, orderBy, limit, onSnapshot } = mF);
    cargado = true;
  })();
  return _promesa;
}
