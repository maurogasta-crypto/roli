# roli — CLAUDE.md

## Qué es este proyecto

Robot Arduino UNO para enseñar programación a niños. Código del Arduino (`firmware/`), consola de la laptop (`laptop/`) y documentos (`docs/`). Sin servidor; desde el 14-nov-2026 tiene una base privada para lo sensible (abajo).

## Secretos

**Regla de oro:** ningún valor real de una credencial entra jamás a este repositorio, a ningún otro, ni a ningún chat.

¿Usa variables de entorno? **No.** No hay funciones de servidor: el firmware se carga por USB, la consola corre en la laptop y el sitio es estático.

**Desde el 14-nov-2026 hay una base privada** (Firebase `roli-467a4`: calibraciones, partidas y notas; sitio `index.html`, reglas `firestore.rules`).

| Nombre | Qué hace | Tipo | Dónde vive el valor real | Consumido por |
|---|---|---|---|---|
| `firebaseConfig.*` | identifica `roli-467a4` ante la API web; **no da permisos** | público por diseño | `firebase-init.js` (única copia) | todo el sitio |
| Contraseña de cada persona | entrar | dato en runtime | Firebase Authentication de `roli-467a4` | `index.html` |
| UID de Mauro y del agente | lo que comparan `esMauro()` y `esAgente()` | configuración | marcadores `TU-UID-ACA` y `UID-DEL-AGENTE` en `firestore.rules`; los valores, en el panel (`proyectos/roli`) | Firestore |
| Contraseña del usuario del agente | que un chat lea la base | dato en runtime | variables de entorno de Claude Code (`FB_AGENTE_*` o `FB_PANEL_*`, las mismas de las otras bases), cargadas por Mauro | `datos/herramientas/firestore.mjs` |

Un UID real, una contraseña o el nombre de un chico no entran a este repositorio (es público).

- **Lo que se carga al jugar es lo sensible, y va a la base** (14-nov-2026, Mauro): `jugar.html` pide login y guarda `jugadores` (nombre, edad, nota) y `partidas` (equipo, rondas, estrellas, medidas) en `roli-467a4`. **Nada de eso en `localStorage`** (el banco lo comprueba); en `sessionStorage` sólo qué pasos de preparación se tildaron. Los juegos y los roles son de `roli.js` del panel y se traen al abrir. La puerta (login y ficha) es `acceso.js`, compartida con `index.html`.
- **El agente entra a esta base con el usuario de las otras** (cae a `FB_PANEL_*` si no hay `FB_ROLI_*`); puede leer todo, y escribe como una persona con ficha (la ficha `usuarios/` la escribe sólo Mauro).

## Al trabajar en este repo

- Se empuja a `main` directo (criterio general de Mauro, 3-nov-2026).
- El firmware se verifica compilando contra un Arduino simulado (g++ con una cabecera `Arduino.h` mínima) para los niveles 1 a 6 y los tres `MAPA_PINES`.
- El `.ino` entregado es el que Mauro calibró en el robot: no se pisan sus valores de servo, velocidades, empujón ni zigzag. **Salvo lo que él pide cambiar:** el 14-nov-2026 pidió «el cero» (velocidades 90/84, empujón 160, enderezado de la rueda loca) y calibrar desde el robot con `calibrar` y `desvio`, sin recargar (`firmware/CALIBRACION.md`). Si cambia un valor del cero, cambia también `firmware/calibracion_cero.txt` (el banco lo compara).
- Antes de subir: `node pruebas-sitio.mjs` (13 casos: el registro, las reglas v2 y que el SDK sólo se toque en `firebase-init.js`) y `bash pruebas/correr.sh` (compila los 6 niveles y los 3 mapas, corre las simulaciones y la prueba de la consola).
- Después de publicar unas reglas: `node pruebas-reglas-vivas.mjs` (9 casos contra la base real, sin dejar documentos; verificado el 14-nov con las v2).
- Archivos completos, nunca diffs.
- Si cambia el cableado o un comando, cambian en el mismo cambio el `README.md` y los documentos de `docs/`.
- Las actividades para los chicos y la lista de compras viven en el panel (`roli.html` y `roli.js` de `maurogasta-crypto/datos`). Si cambia una palabra del firmware, cambia `roli.js` en la misma tanda.
