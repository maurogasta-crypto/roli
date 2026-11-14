# roli — CLAUDE.md

## Qué es este proyecto

Robot Arduino UNO para enseñar programación a niños. Código del Arduino (`firmware/`), consola de la laptop (`laptop/`) y documentos (`docs/`). Sin servidor ni base de datos.

## Secretos

**Regla de oro:** ningún valor real de una credencial entra jamás a este repositorio, a ningún otro, ni a ningún chat.

¿Usa variables de entorno? **No.** No hay funciones de servidor ni despliegue: el firmware se carga por USB y la consola corre en la laptop. No hay tabla de secretos porque no hay secretos.

## Al trabajar en este repo

- Se empuja a `main` directo (criterio general de Mauro, 3-nov-2026).
- El firmware se verifica compilando contra un Arduino simulado (g++ con una cabecera `Arduino.h` mínima) para los niveles 1 a 6 y los tres `MAPA_PINES`.
- El `.ino` entregado es el que Mauro calibró en el robot: no se pisan sus valores de servo, velocidades, empujón ni zigzag. **Salvo lo que él pide cambiar:** el 14-nov-2026 pidió «el cero» (velocidades 90/84, empujón 160, enderezado de la rueda loca) y calibrar desde el robot con `calibrar` y `desvio`, sin recargar (`firmware/CALIBRACION.md`). Si cambia un valor del cero, cambia también `firmware/calibracion_cero.txt` (el banco lo compara).
- Antes de subir: `bash pruebas/correr.sh` (compila los 6 niveles y los 3 mapas, corre las simulaciones y la prueba de la consola).
- Archivos completos, nunca diffs.
- Si cambia el cableado o un comando, cambian en el mismo cambio el `README.md` y los documentos de `docs/`.
- Las actividades para los chicos y la lista de compras viven en el panel (`roli.html` y `roli.js` de `maurogasta-crypto/datos`). Si cambia una palabra del firmware, cambia `roli.js` en la misma tanda.
