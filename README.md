# Roli

Robot Arduino UNO que Mauro armó con sus hijos Yacko y Kala (10 y 7 años) para aprender a programar con palabras. Se maneja desde una laptop Lubuntu por Bluetooth (BLE).

## Qué hay acá

| Carpeta | Qué es |
|---|---|
| `firmware/roli_programa.ino` | El programa del Arduino. Seis niveles: se desbloquean cambiando `#define NIVEL` (1 a 6) |
| `laptop/` | La consola en Python (`consola_robot.py`), `roli.sh` para abrirla y los scripts que arreglan el Bluetooth de la laptop |
| `docs/` | El manual para Yacko y Kala y la guía de actividades del nivel 3 |

## Los seis niveles

1. Hablar: `hola`, `di`, `led`, `parpadear`, `ayuda`
2. Moverse: `adelante`, `atras`, `izquierda`, `derecha`, `parar`
3. Tiempo y velocidad: `adelante 2`, `velocidad 150`, `zigzag`
4. Programas: `programa … fin`, `listar`, `ejecutar`, `esperar`
5. Ojos: `distancia`, `escanear`, `mirar`, `proteccion`
6. Decidir: `cuando obstaculo …`, `explorar`, `girar`

## Cableado (MAPA_PINES 1)

- Motores en L298N: izquierdo IN1=5, IN2=6; derecho IN3=9, IN4=10 (jumpers de ENA/ENB puestos)
- Sensor delantero HC-SR04: Trig A0, Echo A1; servo en el pin 3
- Sensor trasero HC-SR04 (fijo): Trig A3, Echo A4
- Bluetooth BLE en 11 (RX) y 12 (TX)
- Baterías 2×18650 en serie a 12V/GND del L298N y a VIN/GND del Arduino

## Cómo se carga

1. En el Arduino IDE abrí `firmware/roli_programa.ino`, elegí el nivel y subilo por USB.
2. En la laptop: `bash laptop/roli.sh` abre la consola (`roli>`). Con `teclado` se maneja con las flechas.

## Ajustes calibrados en el robot real

Centro del servo (`SERVO_FRENTE`, `SERVO_IZQ`, `SERVO_DER`), velocidades iniciales, empujón de arranque (`KICK_VEL`), enderezado, zigzag y `GIRO_MS_POR_GRADO` están al principio del `.ino`. Si se cambia algo en el robot, se actualiza acá.

**El cero (14-nov-2026):** velocidades 90 / 84, arranque desde cero con un empujón de 160 y cuatro golpes cortos para enderezar la rueda loca (`firmware/calibracion_cero.txt`). Desde el nivel 3 se calibra **sin volver a cargar el programa**: `calibrar ver | recto | velocidad 90 84 | kick 160 | ender 4 | zigzag 12 | giro mas | guardar | exportar | cero` y `desvio izq | der`. Al final de la sesión la consola ofrece guardar en `laptop/calibraciones/` la lista de texto para llevarla al chat. Todo en `firmware/CALIBRACION.md`. Banco: `bash pruebas/correr.sh`.

## Pendiente

- Medidor de batería (dos resistencias de 10 kΩ en A2; `HAY_MEDIDOR_BATERIA`)
- Cargador de la batería de 2 celdas
- Giroscopio (MPU-6050) para ir derecho


## Traspaso

Estado, cableado, parámetros calibrados, pendientes y el plan para dar de alta Roli en el panel: ver [`TRASPASO.md`](TRASPASO.md).

- `pruebas/`: Arduino simulado (g++) para verificar los niveles 1 a 6 y los mapas de pines. Ver `pruebas/LEEME.md`.
- `docs/fuente/`: fuentes de los PDFs (hoy desactualizados). Ver `docs/fuente/LEEME.md`.

## El registro privado (`index.html`) y el juego (`jugar.html`), desde el 14-nov-2026

Un sitio con login (mail y contraseña) para guardar lo que no puede ser público: las calibraciones (`calibrar exportar`), las partidas con los nombres del equipo y las notas del desarrollo. Base `roli-467a4`; reglas en `firestore.rules` (plantilla, UID como marcadores). Tener cuenta no es tener permiso: Mauro activa cada ficha en la pestaña «Personas». Banco: `node pruebas-sitio.mjs`.

`jugar.html` es «A jugar con Roli»: preparar (el adulto), elegir el juego y quiénes juegan, y el tablero ronda por ronda. Los nombres, las edades y las partidas se guardan en la base (`jugadores`, `partidas`), no en el aparato. Reglas v2.
