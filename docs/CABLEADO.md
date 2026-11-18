# El cableado de Roli · 18-nov-2026

Guía para rehacer **todas** las conexiones de Roli con los chicos, sin protoboard: lo que
comparte una conexión (los 5 V y el GND) se une con **empalmes soldados**. Suma tres cosas
nuevas: el **zumbador**, los **dos encoders** de las ruedas y el **medidor de batería**
(dos resistencias de 10 kΩ).

El programa que va con este cableado es el `firmware/roli_programa.ino` del 18-nov (el servo
pasó del pin 3 al **7**). **Si se conecta así y se deja el programa viejo, el cuello no se
mueve**: hay que subir el programa nuevo (paso 9).

---

## 0 · Antes de empezar

**Materiales:** soldador con su soporte, estaño fino, termocontraíble (o cinta aisladora),
encendedor o pistola de calor, pela-cables (o tijera con cuidado), pinza, multímetro, cables
dupont macho-hembra y hembra-hembra de colores, precintos, cinta de papel y marcador.

**Reglas de la mesa (se leen en voz alta):**

1. **Roli apagado**: se saca una batería del portapilas. Nadie conecta con Roli prendido.
2. **El soldador lo agarra un adulto** o un chico con un adulto al lado. Siempre en su
   soporte. Se suelda con la ventana abierta y sin respirar el humo.
3. **Antes de prender, otro revisa**: el que no conectó sigue cada cable con el dedo y dice
   en voz alta adónde va.
4. **Una foto antes de desconectar nada**, para poder volver atrás.

**Roles (rotan):** el que **lee** el paso · el que **conecta** · el que **revisa**.

**Los lados de Roli:** miramos a Roli **desde atrás** (el L298N rojo y el sensor de atrás
cerca nuestro, el cuello con el sensor de adelante lejos).
- **Izquierda** = la rueda del lado del **Bluetooth**.
- **Derecha** = la rueda del lado del **zumbador**.

---

## 1 · El código de colores

Los colores son un idioma: si todos lo hablan, cualquiera encuentra una falla.

| Color | Qué lleva | Para recordar |
|---|---|---|
| 🔴 **Rojo** | **5 V del Arduino** (sensores, Bluetooth, zumbador) | rojo = fuerza |
| ⚫ **Negro** | **GND**, el «−» de todo | negro = tierra |
| 🟠 **Naranja** | **5 V del L298N**, sólo para el servo | naranja = la fuerza aparte del servo |
| 🟡 **Amarillo** | señal del **servo** → pin **7** | como el cable amarillo del servo |
| ⚪ **Blanco** | **Trig** de los dos sensores de distancia | blanco = el grito |
| 🩶 **Gris** | **Echo** de los dos sensores de distancia | gris = el eco que vuelve |
| 🔵 **Azul** | los dos **encoders** (pines **2** y **3**) | azul = ruedas; con cinta **I** o **D** |
| 🟢 **Verde** | Bluetooth **TXD** → pin **11** | verde = Roli escucha |
| 🟤 **Marrón** | Bluetooth **RXD** → pin **12** | marrón = Roli habla |
| 🟣 **Violeta** | **zumbador** → pin **8** | violeta = la voz |
| 🏷️ cualquiera con cinta «BAT» | el medio de las resistencias → **A2** | |

Los **cables gruesos de las baterías** (rojo y negro) y los **cuatro del motor** (IN1–IN4) se
dejan como están.

---

## 2 · El mapa completo (lo que va a cada pin del Arduino)

| Pin del Arduino | Qué se conecta | Color |
|---|---|---|
| **2** | Encoder **izquierdo** · DO | azul (cinta **I**) |
| **3** | Encoder **derecho** · DO | azul (cinta **D**) |
| **5, 6** | L298N IN1, IN2 (motor izquierdo) | los que están |
| **7** | Servo · señal (**antes iba al 3**) | amarillo |
| **8** | Zumbador · I/O | violeta |
| **9, 10** | L298N IN3, IN4 (motor derecho) | los que están |
| **11** | Bluetooth · TXD | verde |
| **12** | Bluetooth · RXD | marrón |
| **13** | (el led de la placa) | — |
| **A0 / A1** | Sensor de **adelante** (el del cuello) · Trig / Echo | blanco / gris |
| **A2** | Medidor de batería (el medio de las dos de 10 kΩ) | cinta «BAT» |
| **A3 / A4** | Sensor de **atrás** · Trig / Echo | blanco / gris |
| **5V** | arnés rojo (sección 4) | rojo |
| **GND** (3 pines) | arneses negros (sección 4) | negro |
| **VIN** | + de las baterías (ya está) + la resistencia de arriba | rojo grueso |
| libres | 0 y 1 (son del USB: no se usan), 4 y A5 | — |

Y en el **L298N**: borne **5V** → naranja al **+ del servo**; borne **GND** → negro al **− del
servo** (comparte con el − de las baterías, que ya está).

**¿Por qué el servo cambió de pin?** Los pines **2 y 3** son los únicos del Arduino UNO que
**avisan solos** («interrupciones»): aunque Roli esté haciendo otra cosa, no se pierde ningún
agujero del disco. El servo se mueve con pulsos que el programa arma en cualquier pin, así que
se mudó al 7.

**¿Por qué el servo come aparte?** El servo, cuando arranca, chupa de golpe mucha corriente.
Si come de los 5 V del Arduino, el Arduino se puede reiniciar solo (le pasaba a Roli al
explorar). El L298N tiene su propio regulador de 5 V que hoy no usaba nadie: es la «cocina
aparte» del servo. Los dos GND quedan unidos, eso sí.

---

## 3 · Practicar el empalme (antes de tocar a Roli)

Se practica primero con cables sueltos que sobran, hasta que salga lindo.

**El empalme en Y** (une tres puntas: una que llega y dos que siguen):

1. **Pelar** 1 cm la punta de cada cable. Sin cortar los hilitos de cobre.
2. **Ponerle el termocontraíble ANTES** a uno de los cables y correrlo lejos del calor
   (¡el error más común es olvidarlo!).
3. **Retorcer** las tres puntas juntas, bien apretadas, en el mismo sentido.
4. **Estañar**: el soldador calienta los cables 2 o 3 segundos y el estaño se apoya **en los
   cables, no en la punta del soldador**. Tiene que correr adentro y quedar brillante.
5. **No mover** mientras se enfría (10 segundos). Si quedó gris y grumoso, se recalienta.
6. **Doblar** el empalme para que quede en línea, **subir el termocontraíble** y calentarlo
   hasta que abrace. Sin termocontraíble: dos vueltas de cinta aisladora.
7. **Tirón de prueba**: se tira suave de cada cable. Si se sale, se rehace.

**El empalme de una resistencia** es igual: la pata de la resistencia hace de cable.

---

## 4 · Armar los arneses en la mesa (fuera de Roli)

Un **arnés** es un grupo de cables ya empalmados que después se enchufa de una vez. Antes de
cortar, **presentar los cables sobre Roli** para medir el largo (que sobren 3 cm).

Cada punta que va a un pin termina en un **dupont** del tipo que corresponda: macho para los
pines del Arduino (que son agujeros), hembra para los pines de los módulos (que son patitas).
La forma fácil: cortar un cable dupont por la mitad y empalmar a la mitad la punta que hace
falta.

### Arnés 1 · ROJO (5 V del Arduino) · 6 salidas, 5 empalmes

Sale del pin **5V** del Arduino:

```
 pin 5V ──Y0──┬── sensor de ATRÁS · VCC
              └──Y1──┬── encoder DERECHO · VCC
                     └──Y2──┬── zumbador · VCC
                            └──Y3──┬── sensor de ADELANTE · VCC
                                   └──Y4──┬── Bluetooth · VCC
                                          └── encoder IZQUIERDO · VCC
```

### Arnés 2 · NEGRO de adelante · 5 salidas, 4 empalmes

Sale de un pin **GND** del Arduino (de los dos que están al lado del 5V):

```
 GND ──Y1──┬── encoder DERECHO · GND
           └──Y2──┬── zumbador · GND
                  └──Y3──┬── sensor de ADELANTE · GND
                         └──Y4──┬── Bluetooth · GND
                                └── encoder IZQUIERDO · GND
```

### Arnés 3 · NEGRO de atrás + medidor de batería

Sale del otro **GND** del Arduino:

```
 GND ──Y──┬── sensor de ATRÁS · GND
          └── resistencia de ABAJO (10 kΩ)
```

### Arnés 4 · el medidor de batería (las dos de 10 kΩ)

```
 cable de VIN ──Y──┬── pin VIN del Arduino (como antes)
 (+ de baterías)   └── [10 kΩ de ARRIBA] ──●── [10 kΩ de ABAJO] ── al arnés 3 (GND)
                                           │
                                           └── cable «BAT» → pin A2
```

1. Soldar las **dos resistencias en fila** (una pata con otra) y, en esa misma unión, el
   cable «BAT». Termocontraíble sobre toda la tira, dejando ver sólo las puntas.
2. Cortar el cable rojo grueso que va al **VIN** a 5 cm del Arduino y hacer ahí el **Y**: el
   que viene de las baterías, el que vuelve al VIN y la resistencia de arriba.
3. La resistencia de abajo va al empalme del **arnés 3**.

Las dos son iguales (10 kΩ): da lo mismo cuál es la de arriba. Así el Arduino mide la
**mitad** de la batería (unos 4 V), que es lo que aguanta su pin.

### Arnés 5 · el servo

El servo tiene su ficha de 3 (marrón, rojo, amarillo). Se le enchufan **tres cables
macho-macho**:

| Servo | Cable | Va a |
|---|---|---|
| marrón (−) | negro | borne **GND** del L298N (aflojar el tornillo, meter junto al que ya está, apretar) |
| rojo (+) | **naranja** | borne **5V** del L298N |
| amarillo (señal) | amarillo | pin **7** del Arduino |

---

## 5 · Montar en Roli, de a un módulo

Siempre en este orden: **GND primero, después 5 V, la señal al final.** Después de cada
módulo, el que revisa lo controla contra la tabla de la sección 2.

| # | Módulo | GND | 5 V | Señal |
|---|---|---|---|---|
| 1 | Sensor de **adelante** (cuello) | arnés 2 | arnés 1 | Trig → **A0** blanco · Echo → **A1** gris |
| 2 | Sensor de **atrás** | arnés 3 | arnés 1 | Trig → **A3** blanco · Echo → **A4** gris |
| 3 | **Bluetooth** | arnés 2 | arnés 1 | TXD → **11** verde · RXD → **12** marrón · STATE y EN: nada |
| 4 | **Zumbador** | arnés 2 | arnés 1 | I/O → **8** violeta |
| 5 | Encoder **izquierdo** | arnés 2 | arnés 1 | DO → **2** azul «I» · AO: nada |
| 6 | Encoder **derecho** | arnés 2 | arnés 1 | DO → **3** azul «D» · AO: nada |
| 7 | **Servo** | L298N GND | L298N **5V** (naranja) | → **7** amarillo |
| 8 | **Batería** | arnés 3 | — | «BAT» → **A2** |

**Ojo con los encoders:** el disco ranurado tiene que pasar **por el medio de la ranura** sin
tocar los bordes. Girar la rueda con la mano antes de fijar.

**Ojo con el L298N:** el **puente (jumper) de 5V** que está al lado de los bornes tiene que
estar puesto (es el que prende su regulador). **No unir nunca** el 5V del L298N con el 5V del
Arduino: son dos «cocinas» separadas; sólo los GND van juntos.

Al terminar: juntar los cables con precintos, que **ninguno toque una rueda**.

---

## 6 · La revisión de los cuatro ojos (antes de prender)

Uno lee, otro sigue el cable con el dedo:

- [ ] Ningún cable pelado toca otro (sobre todo rojo con negro y naranja con negro).
- [ ] El **naranja** va al borne 5V del L298N, **no** al Arduino.
- [ ] El **rojo** sale del pin **5V** del Arduino, **no** del VIN ni del 3.3V.
- [ ] Los encoders en **2** y **3**, el servo en **7**, el zumbador en **8**.
- [ ] La tira de resistencias entre **VIN** y **GND**, con el medio en **A2**.
- [ ] Bluetooth: TXD en 11 y RXD en 12 (si están al revés, no se rompe, pero no habla).

---

## 7 · Primer encendido y medición (con el multímetro)

1. Poner la batería. **Mirar y oler 5 segundos**: si algo calienta o huele, se apaga ya.
2. Multímetro en **20 V de continua**, punta negra en un GND:
   - pin **5V** del Arduino: entre **4,8 y 5,2 V**;
   - borne **5V** del L298N: entre **4,8 y 5,2 V**;
   - pin **A2**: **la mitad** de lo que marca el VIN (con baterías cargadas, unos 4 V).
3. Se prenden: el led de cada sensor de rueda y el led del Bluetooth (parpadea).

---

## 8 · Las pruebas a mano (todavía sin programa nuevo)

- **Encoders**: girar cada rueda despacito con la mano. **La segunda lucecita del sensor
  parpadea** con cada agujero. Uno gira una vuelta entera, otro cuenta: tiene que dar los
  agujeros del disco (suelen ser **20**). Anotarlo.
- **Zumbador**: sacar el violeta del pin 8 y tocar con su punta un **GND**: si suena seguido es
  **activo**; si hace «clic» es **pasivo**. Anotarlo y volver a ponerlo en el 8.

---

## 9 · Subir el programa nuevo y probar todo

1. Con la batería sacada, enchufar el **USB** y subir `firmware/roli_programa.ino` (nivel 6).
2. Desenchufar, poner la batería: **Roli pita dos veces** al despertar.
3. Con la consola (`./roli.sh`):

| Orden | Qué tiene que pasar |
|---|---|
| `info` | dice el nivel, **cuántos agujeros contó cada rueda**, la **batería** y pita |
| girar la rueda izquierda una vuelta con la mano, `info` | **izq** subió unos 20 |
| girar la derecha, `info` | **der** subió unos 20 |
| `bateria` | dice los voltios (unos 7,4 a 8,4 con cargadas) y el % |
| `mirar izq` / `mirar der` | el **cuello** gira (ya con el pin 7) |
| `distancia` | el sensor de adelante dice centímetros |
| `probar` | cada rueda, de a una |
| `explorar` | anda solo; **ya no se debería reiniciar** al mover el cuello |

**Si algo no anda:**
- Una rueda no cuenta → el disco no pasa por la ranura, o el azul está en otro pin.
- Cuenta de a dos o de a muchos → el disco roza; acomodar el sensor.
- `bateria` dice casi 0 → el cable «BAT» no llega a A2, o falta la resistencia de abajo.
- El cuello no se mueve → el amarillo no está en el 7, o falta el naranja en el L298N, o se
  subió el programa viejo.
- No pita → el violeta no está en el 8, o el zumbador no tiene su rojo y su negro.

---

## 10 · Para el cuaderno de Roli

Anotar: agujeros por vuelta del disco ___ · zumbador activo / pasivo · voltios de la batería
al empezar ___ · quién soldó cada arnés.
