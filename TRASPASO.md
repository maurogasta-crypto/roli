# Roli — traspaso (9-nov-2026)

Para quien retome Roli desde otra sesión, en particular **la que ya está en el panel** (`maurogasta-crypto/datos`), que tiene las credenciales del agente. Idioma con Mauro: castellano rioplatense.

## 1 · Qué quedó hecho

- El repo `maurogasta-crypto/roli` (privado) tiene el firmware, la consola de la laptop, los PDFs, las fuentes de los PDFs y un banco de pruebas con Arduino simulado. Todo en `main`.
- **Lo que NO se hizo: el proyecto Roli dentro del panel.** La sesión que armó esto no tenía las credenciales del agente (`FB_AGENTE_MAIL` y `FB_AGENTE_CLAVE`) ni salida a Firestore. No se tomó línea de trabajo, no se reservó repo y no existe `proyectos/roli`. Eso es lo que sigue (sección 5).

## 2 · Qué es Roli

Robot Arduino UNO que Mauro armó con sus hijos Yacko (10) y Kala (7) para aprender a programar con palabras. Se maneja desde una laptop Lubuntu por Bluetooth BLE. Un solo programa con seis niveles: se desbloquean cambiando `#define NIVEL` (1 a 6) y subiendo por USB.

| Nivel | Palabras |
|---|---|
| 1 | `hola`, `di`, `led`, `parpadear`, `ayuda` (y `info`, `bateria` en cualquier nivel) |
| 2 | `adelante`, `atras`, `izquierda`, `derecha`, `parar`, `probar` (atajos `d a i e r`) |
| 3 | tiempo (`adelante 2`), `velocidad 150`, `velocidad izq/der`, `zigzag 1/0` |
| 4 | `programa … fin`, `listar`, `ejecutar n`, `esperar`, `borrar` |
| 5 | `distancia`, `distancia atras`, `escanear`, `mirar izq/der/frente/<grados>`, `proteccion n` |
| 6 | `cuando obstaculo <orden>`, `explorar [segundos]`, `girar der/izq <grados>` |

`explorar` avanza sin parar mientras el servo barre ±30°. Si algo queda cerca, frena, mira siete direcciones (y atrás con el sensor trasero) y se va por donde ve más lejos. Después de frenar exige `proteccion + 10 cm` para reanudar. Si todo está cerrado, se detiene. Sin límite de tiempo salvo `explorar N`.

## 3 · Cableado real (MAPA_PINES 1)

- **Motores:** L298N HW-095 con los jumpers de ENA/ENB puestos; cables en IN1–IN4. Izquierdo IN1=5, IN2=6; derecho IN3=9, IN4=10. La velocidad (PWM) va por los mismos pines IN.
- **Sensor delantero HC-SR04:** Trig A0, Echo A1. **Servo SG90:** señal en el pin 3, con pulsos propios (544–2400 µs) porque `Servo.h` desactiva el PWM de los pines 9 y 10.
- **Sensor trasero HC-SR04** (fijo, sin servo): Trig A3, Echo A4.
- **Bluetooth BLE:** módulo en 11 (RX) y 12 (TX), 9600. Aparece como "HC-06" pero es BLE (servicio FFE0/FFE1). Una conexión a la vez: el celular tiene que estar desconectado. Sin divisor 1k/2k en el RX del módulo (anda).
- **Energía:** 2×18650 en serie (7,4–8,4 V) a los bornes 12V y GND del L298N, y en paralelo al VIN y GND del Arduino. El regulador del Arduino alimenta la barra de 5 V (sensores, servo, BLE). El borne 5V del L298N queda libre. USB y baterías juntos es seguro.
- **Pines libres:** 2, 4, 7, 8, 13 (el 13 es el LED de la placa) y A2 (reservado al medidor de batería) y A5.

## 4 · Parámetros calibrados en el robot

Están al principio del `.ino`. Los puso Mauro probando; **no se pisan**:

| Parámetro | Valor | Nota |
|---|---|---|
| `SERVO_FRENTE` / `SERVO_IZQ` / `SERVO_DER` | 80 / 140 / 20 | el centro estaba corrido a la izquierda |
| `VEL_IZQ_INICIAL` / `VEL_DER_INICIAL` | 95 / 88 | compensa que la rueda izquierda rinde distinto |
| `KICK_VEL` / `KICK_MS` | 200 / 150 | empujón de arranque al retroceder y girar desde parado (la rueda loca frenaba) |
| `ZIG_DELTA` / `ZIG_MEDIO_MS` | 12 / 350 | zigzag suave al ir derecho o en reversa |
| `ZIG_PULSO` / `ZIG_PULSO_MS` / `ZIG_PULSO_CADA_MS` | 45 / 70 / 1500 | golpe corto de potencia cada tanto |
| `GIRO_MS_POR_GRADO` | 8 | **sin calibrar** con el empujón nuevo: probar `girar der 90` |
| `MARGEN_TRAS_FRENO` | 10 | cm extra que exige `explorar` para reanudar |
| `TRIG` / `ECHO` | A0 / A1 | si `distancia` siempre dice "no veo nada", se invierten |
| `HAY_SENSOR_TRASERO` | `true` | |
| `HAY_MEDIDOR_BATERIA` | `false` | el divisor no está armado |

## 5 · Qué se probó y qué no

- **Probado en el robot:** consola BLE desde la laptop (con reconexión), ruedas y velocidad, programa de nivel 1 a 3, centrado del servo. Mauro dejó el `.ino` con sus valores y dijo que las pruebas básicas andaban.
- **Probado sólo en simulación (lógica, no hardware):** `explorar` completo, sensor trasero, empujón de arranque, zigzag, margen tras frenar. Corren con `pruebas/` (ver `pruebas/LEEME.md`).
- **Sin confirmar en el robot:** que `distancia` y `distancia atras` midan bien (hubo un "no mide" con A0/A1 y no quedó cerrado), el barrido del servo con las ruedas andando, el efecto real del zigzag y los golpes, y que `explorar` no se resetee por el consumo del servo. Si se resetea: baterías cargadas o un capacitor de 470 µF cerca del servo.

## 6 · Pendientes de hardware y de documentación

1. Probar y cerrar los dos sensores (`distancia`, `distancia atras`) y el barrido.
2. Calibrar `GIRO_MS_POR_GRADO` con `girar der 90` y `girar izq 90`.
3. Medidor de batería: divisor de dos resistencias de 10 kΩ de VIN a A2 y de A2 a GND, y poner `HAY_MEDIDOR_BATERIA = true`.
4. Cargar las 2 celdas: el módulo TP4056 es de una sola celda (4,2 V); la batería en serie necesita cargar cada celda por separado o un cargador 2S con protección.
5. Ir derecho de verdad: sin sensor de giro no hay forma de detectar un motor forzando. Lo que funcionaría es un **giroscopio MPU-6050** (I2C en A4/A5; habría que mover el Echo trasero a otro pin libre) o encoders. Un sensor de corriente sólo detecta trabas.
6. **Actualizar el manual y la guía del nivel 3** (`docs/`): no mencionan el sensor trasero, `explorar` nuevo, `girar`, `zigzag` ni el empujón. Las fuentes están en `docs/fuente/`.
7. Opcional: divisor 1k/2k en el RX del BLE.

## 7 · La laptop (Bluetooth)

Lubuntu con adaptador Intel 7265. Se tuvo que fijar `btusb enable_autosuspend=n` y una regla udev (script `laptop/bt_arreglar.sh`, con sudo y reinicio) porque el adaptador se reseteaba. `laptop/roli.sh` destraba rfkill, enciende el Bluetooth y abre `consola_robot.py` en `~/ble-env` (Python 3.14, `bleak`). La consola reconecta sola hasta 5 veces. MAC del módulo: ver `consola_robot.py`. Si algo falla, `bt_diagnostico.sh` junta el diagnóstico en `~/Roli/`.

## 8 · Lo que sigue: Roli como proyecto del panel

Mauro pidió: «un proyecto dentro de mi panel para Roli». Eligió **repo propio `roli`** (hecho) y que **la sesión del panel lo cree** con las credenciales del agente.

Pasos, según el reglamento de `datos` (`PROTOCOLO-GENERAL.md` § 4.3 y § 2.1 quinquies/sexies):

1. Leer `TRASPASO.md` de `datos` y abrir con `node herramientas/ronda.mjs abrir`.
2. **Tomar una línea** de trabajo para Roli (con `fusionar`, nunca `escribir`) y **reservar** los repos `datos` y `roli` con `--chat`.
3. Mirar cómo está armado un proyecto parecido (por ejemplo `hilux` o el de inmuebles) para copiar los campos, no inventarlos.
4. Crear `proyectos/roli` con: nombre, `sitio.repo = maurogasta-crypto/roli`, `estructura` (intro, `nodos` y `partes` con `explica` y `detalle`, y el `mapa` con cada cosa marcada `anda`, `desarrollo` o `idea`) y `sitio.guias` hacia la página de pruebas. Escribirlo **para alguien que no programa**, con la sección 2 y 3 de este archivo como fuente. Marcar como `desarrollo` el sensor trasero, `explorar`, el zigzag y el medidor de batería, y como `idea` el giroscopio.
5. Una página de pruebas guiadas estilo `placa.html` en `datos` (raíz, plana, con `hoja.css`): niveles, cableado y pruebas en orden. Si se agrega, subir el sello y la `VERSION` de `sw.js`, y correr los bancos de `datos` antes de empujar.
6. Dar de alta los pendientes de la sección 6 como pendientes del proyecto en el panel.
7. Regenerar `herramientas/bodega.json` (`telefono.mjs manifiesto`) si el reglamento lo pide al dar de alta un proyecto.
8. **Sin credenciales ni bases propias:** Roli no usa variables de entorno, ni Firebase propio, ni funciones de servidor. No hace falta ficha de titularidad con claves ni entrada en `PROYECTOS` de `firestore.mjs`.
9. Soltar la línea y las reservas al cerrar, y escribir la tanda.

Nada de lo de acá abre algo: todo es dato de configuración y puede ir al panel.
