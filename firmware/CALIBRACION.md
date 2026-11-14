# Calibrar a Roli sin volver a cargar el programa

**El cero (14-nov-2026).** Roli sale de fábrica con estos valores, que son el punto de partida desde el que se va afinando. Están en `firmware/calibracion_cero.txt` y arriba de `roli_programa.ino`, con los mismos nombres.

| Qué | Valor | Para qué |
|---|---|---|
| `VEL_IZQ_INICIAL` / `VEL_DER_INICIAL` | 90 / 84 | velocidad de crucero de cada rueda; la diferencia compensa la desviación medida |
| `KICK_VEL` / `KICK_MS` | 160 / 150 ms | arranca desde cero con un empujón (manteniendo la proporción 90/84) para vencer la inercia y la rueda loca |
| `ENDEREZAR_GOLPES` / `_FUERZA` / `_MS` / `_PAUSA_MS` | 4 / 160 / 60 ms / 60 ms | al empezar a ir derecho (adelante o atrás), después del empujón: golpes cortos y bruscos, una rueda fuerte y la otra suelta, **alternando** izquierda y derecha, para forzar a la rueda loca a enderezarse. `0` golpes = sin enderezado |
| `ZIG_DELTA` / `ZIG_PULSO` | 12 / 45 | el zigzag suave que sigue mientras va derecho |
| `GIRO_MS_POR_GRADO` | 8 | cuánto tarda en girar un grado (nivel 6) |

**Ojo:** el empujón y el enderezado son **valores de partida sin probar en el robot** (la lógica está probada en simulación, no el efecto sobre la rueda loca real). Para eso están las órdenes de abajo. Y como cada movimiento arranca así, un `adelante 2` incluye los ~0,6 s del arranque dentro de sus 2 segundos.

## Las órdenes (desde el nivel 3)

| Orden | Qué hace |
|---|---|
| `calibrar ver` | muestra los valores en uso |
| `calibrar recto` | avanza 2 segundos y pregunta si fue derecho: es **una instancia de calibración** para hacer en el juego |
| `desvio izq` / `desvio der` | «se fue hacia la izquierda / derecha»: Roli sube un poco la fuerza de esa rueda (2 por vez; `desvio izq 5` sube 5) |
| `calibrar velocidad 90 84` | las dos velocidades (izq der), de 60 a 255 |
| `calibrar kick 160` / `calibrar kick 160 150` | fuerza (60–255) y duración (0–500 ms) del empujón |
| `calibrar ender 4` / `calibrar ender 4 160 60` | golpes (0–10), fuerza y duración de cada golpe |
| `calibrar zigzag 12` / `calibrar zigzag 12 45` | diferencia (0–30) y golpe (0–100) |
| `calibrar giro mas` / `menos` / `8` | el giro (nivel 6); probarlo con `girar der 90` |
| `calibrar guardar` | deja los valores **en la memoria del robot**: sobreviven al apagado y se cargan al prender |
| `calibrar cero` | vuelve al cero de fábrica y borra lo guardado |
| `calibrar exportar` | imprime **la lista de texto para llevar al chat** (abajo) |

Un valor fuera de rango se rechaza y no cambia nada. Un programa grabado (`programa … fin`) **no puede calibrar**.

## La sesión guiada (14-nov-2026): `sesion`

En la consola de la laptop escribí **`sesion`** y ella te guía, sin que tengas que acordarte de las órdenes:

1. **Derecho:** Roli avanza 2 segundos y te pregunta cómo fue (`d` derecho, `i` se fue a la izquierda, `r` a la derecha, `o` otra vez). Corrige solo con `desvio izq` o `desvio der` y repite.
2. **Arranque:** ¿la rueda loca queda derecha? Si no, `m` hace más golpes (`calibrar ender 6`, 8…) y `p` menos.
3. **Giro (opcional, nivel 6):** gira 90° y te pregunta si fue justo, de menos o se pasó (`calibrar giro mas` / `menos`).
4. **Guardar:** pregunta si lo guarda en el robot (`calibrar guardar`), pide la lista, la guarda en `laptop/calibraciones/`, **la copia al portapapeles y abre el sitio** en «Calibraciones».

En el sitio (con tu cuenta): pegás con Ctrl+V y tocás «Guardar». La consola no tiene ninguna clave del sitio: lo último lo hace una persona. Con `x` en cualquier pregunta se corta sin guardar nada en el robot. Después, `sitio` vuelve a abrir la página y `copiar` vuelve a copiar la última lista. Necesita `wl-copy`, `xclip` o `xsel` para copiar (si no hay, la consola muestra la lista para copiarla a mano).

## Una sesión de calibración (a mano)

1. `calibrar ver` y `calibrar recto`. ¿Se fue de lado? `desvio izq` o `desvio der`, y `calibrar recto` otra vez, hasta que vaya derecho.
2. Mirar el arranque: ¿la rueda loca queda derecha? Si no, `calibrar ender 6` (más golpes) o `calibrar ender 4 200 80` (más fuertes). `calibrar ender 0` para probar sin ellos.
3. Con `girar der 90`, `calibrar giro mas` / `menos` hasta que gire 90°.
4. `calibrar guardar`. Roli ya queda calibrado, aunque se apague.
5. **Al salir de la consola**, si cambiaste algo, la consola pregunta si guarda la lista; si decís que sí, le pide `calibrar exportar` al robot y la guarda en `laptop/calibraciones/roli-calibracion-AAAAMMDD-HHMMSS.txt`. También se guarda sola cuando escribís `calibrar exportar`.

## La lista para llevar al chat

```
=== CALIBRACION DE ROLI (llevala al chat) ===
programa: NIVEL 6 MAPA 1 calibrar-v1
VEL_IZQ_INICIAL 92
VEL_DER_INICIAL 86
KICK_VEL 160
...
para volver a poner estos valores sin cargar el programa:
calibrar velocidad 92 86
...
calibrar guardar
=== FIN ===
```

Pegá ese texto en el chat y pedile **«reajustá `roli_programa.ino` con esta calibración»**: los nombres son los del programa, así que cambia esas constantes y vos lo cargás por USB (el cero nuevo queda como punto de partida de fábrica). Mientras tanto no hace falta cargar nada: con `calibrar guardar` ya quedó en el robot. Las mismas órdenes del final sirven para volver a poner esos valores en cualquier momento.

## Lo que se probó y lo que no

- **Probado en simulación** (`bash pruebas/correr.sh`): el cero, el arranque (empujón 160/149 y cuatro golpes alternados, también hacia atrás; los giros llevan el empujón pero no los golpes), cada orden y sus rangos, guardar y recuperar de la memoria (y rechazar una memoria rota), `desvio`, `exportar` con los nombres del programa, `cero`, y la parte de la consola que guarda la lista.
- **No probado:** el efecto real sobre la rueda loca, la memoria EEPROM del Arduino de verdad, ni el espacio que ocupa en un Arduino UNO (no hay compilador AVR acá: si al cargarlo el IDE dice que falta memoria, bajar de nivel o sacar texto de `ayuda()`).
