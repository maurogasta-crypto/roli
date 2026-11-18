/*
  ===========================================================
   ROLI, el robot de Yacko y Kala - "Programar con palabras" (Arduino UNO)
  ===========================================================
  Un solo programa con 6 NIVELES. Cada nivel desbloquea palabras nuevas.
  Para subir de nivel: cambia el numero de la linea  #define NIVEL  y
  vuelve a cargar el programa con el cable USB.

   NIVEL 1  Hablar:      hola, di, led, parpadear, ayuda
   NIVEL 2  Moverse:     adelante, atras, izquierda, derecha, parar
   NIVEL 3  Tiempo:      adelante 2 (segundos), velocidad 150, calibrar, desvio
   NIVEL 4  Programas:   programa ... fin, listar, ejecutar, esperar
   NIVEL 5  Ojos:        distancia, escanear, mirar, proteccion
   NIVEL 6  Decidir:     cuando obstaculo <orden>, explorar

  El robot entiende las ordenes por DOS caminos a la vez:
   - Cable USB    (Monitor Serie del Arduino IDE, 9600 baudios, "Nueva linea")
   - Bluetooth    (modulo BLE en los pines 11 y 12, con consola_robot.py)
  Contesta siempre por el mismo camino por el que le hablaron.

  CALIBRAR SIN VOLVER A CARGAR EL PROGRAMA (nivel 3 en adelante):
   calibrar ver | recto | velocidad 90 84 | kick 160 | ender 4 | zigzag 12 | giro mas
   desvio izq | desvio der      (le cuentas hacia donde se fue y el se corrige)
   calibrar guardar             (lo deja en la memoria del robot, sobrevive al apagado)
   calibrar exportar            (imprime una lista de texto para llevar al chat)
   calibrar cero                (vuelve a los valores de fabrica, el "cero")

  Escribir las ordenes SIN tildes y sin importar mayusculas/minusculas.
  Las comas de los decimales sirven:  adelante 0,5

  Conexiones (elegir MAPA_PINES 1, 2 o 3 mas abajo):
                  MAPA 1 (Roli)        MAPA 2
   Modulo BLE   TX->11, RX->12      TX->11, RX->12
   Motor izq    IN1=5,  IN2=6       ENA=10, IN1=9, IN2=8
   Motor der    IN3=9,  IN4=10      ENB=5,  IN3=7, IN4=6
   HC-SR04      TRIG=A0, ECHO=A1    TRIG=A0, ECHO=A1   (nivel 5; igual en los 3 mapas)
   Servo SG90   senal -> 3          senal -> 3         (nivel 5 en adelante)
   HC-SR04 trasero (opcional) TRIG2=A3, ECHO2=A4  (frena al ir hacia atras; nivel 5)

  CABLEADO DEL 18-NOV-2026 (el de la guia "docs/CABLEADO.md", igual en los 3 mapas):
   Servo SG90    senal -> 7  (antes el 3: el 2 y el 3 quedan para las ruedas)
                 su + al borne 5V del L298N, no al 5V del Arduino
   Encoder izq   DO -> 2     Encoder der   DO -> 3   (los unicos pines que avisan solos)
   Zumbador      I/O -> 8    (suena con LOW: "nivel bajo")
   Bateria       VIN -[10k]- A2 -[10k]- GND
   La palabra "info" muestra cuantos agujeros conto cada rueda y la bateria.

  Nota tecnica: el servo se mueve con pulsos propios (sin la libreria
  Servo) porque esa libreria desactiva la velocidad (PWM) de los pines 9 y
  10, que son los del motor derecho.
*/

#include <SoftwareSerial.h>

// >>> CAMBIA ESTE NUMERO (1 a 6) PARA DESBLOQUEAR PALABRAS NUEVAS <<<
#define NIVEL 6

// >>> ELEGI 1, 2 o 3 SEGUN COMO ESTE CABLEADO ROLI (ver el manual) <<<
//   1 = Roli como esta armado hoy: cables en IN1-IN4 y los puentes (jumpers)
//       puestos en ENA y ENB del L298N  (viene por defecto)
//   2 = cables tambien en ENA y ENB (sin puentes), 3 = uno propio (editar abajo)
// Si Roli no se mueve o una rueda no responde, escribi:  probar
#define MAPA_PINES 1
// Si una rueda gira al reves de lo esperado, pone true en esa rueda.
const bool INVERTIR_IZQ = false;
const bool INVERTIR_DER = false;

#if NIVEL >= 3
#include <EEPROM.h>                // la calibracion se puede guardar en el robot
#endif

// ---------- Pines ----------
SoftwareSerial miBT(11, 12);       // 11 = RX (recibe), 12 = TX (envia)
const byte SERVO_PIN = 7;          // servo del "cuello" (18-nov: del 3 al 7, el 3 es de la rueda derecha)
const byte LED = 13;               // led de la placa
#if MAPA_PINES == 1
// Mapa 1 (Roli): el L298N tiene puestos los puentes de ENA y ENB;
// la velocidad se manda por los mismos pines IN.
const byte IN1 = 5, IN2 = 6;       // motor izquierdo
const byte IN3 = 9, IN4 = 10;      // motor derecho
#elif MAPA_PINES == 2
// Mapa 2: ENA y ENB con cable propio (velocidad); IN1 a IN4 dan el sentido.
// Saca los puentes (jumpers) de ENA y ENB del L298N.
const byte ENA = 10, IN1 = 9, IN2 = 8;   // motor izquierdo
const byte ENB = 5,  IN3 = 7, IN4 = 6;   // motor derecho
#else
// Mapa 3: el tuyo. Cambia los numeros por los pines donde conectaste cada cable.
// (ENA y ENB deben ser pines con PWM: 3, 5, 6, 9, 10 u 11. El 3 y el 11 ya estan usados.)
const byte ENA = 10, IN1 = 9, IN2 = 8;   // motor izquierdo
const byte ENB = 5,  IN3 = 7, IN4 = 6;   // motor derecho
#endif

// Sensor ultrasonico HC-SR04 de Roli: sus cables van a los pines A0 (Trig) y A1 (Echo) (se usan
// como pines digitales comunes). Si 'distancia' dice siempre "no veo nada",
// intercambia A0 y A1 aqui abajo y vuelve a subir el programa.
const byte TRIG = A0, ECHO = A1;

// Segundo sensor (opcional), fijo mirando hacia ATRAS, sin servo. Sirve para no chocar
// al retroceder. Sus cables van a A3 (Trig) y A4 (Echo); Vcc y GND a la barra de 5 V.
// Si todavia no lo conectaste, deja HAY_SENSOR_TRASERO en false.
const bool HAY_SENSOR_TRASERO = true;
const byte TRIG2 = A3, ECHO2 = A4;

// ---------- Ajustes que se pueden tocar ----------
#define LINEA_MAX 40               // largo maximo de una orden
#define PASOS 12                   // pasos maximos de un programa
#define PASO_LEN 22                // largo maximo de cada paso
const unsigned long SEGURIDAD_MS = 4000UL;      // sin "tiempo", frena solo a los 4 s
const unsigned long EXPLORAR_MAX_MS = 0UL;      // explorar sigue hasta 'parar' (0 = sin limite; 'explorar 60' = 60 s)
const int SERVO_FRENTE = 80, SERVO_IZQ = 140, SERVO_DER = 20;  // si mira al reves, intercambia IZQ y DER

// Medidor de bateria (opcional). Se arma con dos resistencias: del pin VIN a A2 va
// R_ALTA, y de A2 a GND va R_BAJA. Cuando las conectes, cambia a true.
const bool HAY_MEDIDOR_BATERIA = true;            // 18-nov-2026: armado con dos de 10k
const byte PIN_BATERIA = A2;
const float R_ALTA = 10000.0, R_BAJA = 10000.0;   // ohmios (pueden ser 10k y 10k)

// Zumbador (18-nov-2026): modulo de 3 patas que suena con LOW ("nivel bajo").
// Si todavia no esta conectado, deja HAY_ZUMBADOR en false.
const bool HAY_ZUMBADOR = true;
const byte ZUMBADOR = 8;

// Encoders de las ruedas (18-nov-2026): un sensor de horquilla por rueda, con el disco de 22 ranuras (22 tics por vuelta de rueda)
// ranurado. Cada agujero que pasa es un "tic". Van en el 2 y el 3, los dos unicos pines del
// UNO que avisan solos (interrupciones) aunque el programa este haciendo otra cosa.
const bool HAY_ENCODERS = true;
const byte ENC_IZQ = 2, ENC_DER = 3;
volatile unsigned long ticsIzq = 0, ticsDer = 0;
void ticIzq() { ticsIzq++; }
void ticDer() { ticsDer++; }

// Un pitido que suena igual con zumbador activo o pasivo: una onda cuadrada de 2 kHz.
void pitido(unsigned int ms) {
  if (!HAY_ZUMBADOR) return;
  for (unsigned long i = 0; i < (unsigned long)ms * 2; i++) {
    digitalWrite(ZUMBADOR, LOW);  delayMicroseconds(250);
    digitalWrite(ZUMBADOR, HIGH); delayMicroseconds(250);
  }
  digitalWrite(ZUMBADOR, HIGH);    // HIGH = callado
}

// ---------- Estado general ----------
struct Linea { char b[LINEA_MAX]; byte n; unsigned long t; };
Linea lUSB = {{0}, 0, 0};
Linea lBT  = {{0}, 0, 0};
Stream* canalActual = &Serial;     // por donde hablo la ultima persona

bool progEjecutando = false;       // hay un programa corriendo
bool explorando = false;           // modo explorar activo

// ---------- Utilidades ----------
// Corta la siguiente palabra de un texto (separa por espacios).
char* tomar(char** p) {
  if (!*p) return NULL;
  while (**p == ' ') (*p)++;
  if (**p == 0) return NULL;
  char* ini = *p;
  while (**p && **p != ' ') (*p)++;
  if (**p) { **p = 0; (*p)++; }
  return ini;
}

bool esNumero(const char* s) {
  return s && (isdigit((unsigned char)s[0]) || s[0] == '.');
}

void ok(const char* palabra) {
  canalActual->print(F("ok "));
  canalActual->println(palabra);
}

// ===========================================================
//  NIVEL 2: MOTORES
// ===========================================================
#if NIVEL >= 2
char mov = 'S';                    // S=parado F=adelante B=atras L=izquierda R=derecha
unsigned long movInicio = 0, movFin = 0;

// ---------------------------------------------------------------------------
//  EL CERO: la calibracion de fabrica de Roli (14-nov-2026)
// ---------------------------------------------------------------------------
// Estos numeros son el punto de partida. Se pueden cambiar SIN cargar el programa con
// "calibrar ..." y guardar con "calibrar guardar". "calibrar exportar" imprime esta misma lista
// con estos MISMOS nombres, para llevarla al chat y reajustar el programa por USB.
// "calibrar cero" vuelve a estos valores.
const int VEL_IZQ_INICIAL = 90, VEL_DER_INICIAL = 84;   // la rueda derecha rinde distinto: esta diferencia compensa el desvio medido
// Arranque desde cero: al empezar a moverse desde parado, durante KICK_MS usa KICK_VEL
// (manteniendo la proporcion izq/der) para vencer la inercia y la rueda loca.
const int KICK_VEL = 160;                       // 60 a 255
const unsigned int KICK_MS = 150;               // 0 a 500
// Enderezado de la rueda loca: al empezar a ir derecho (adelante o atras), despues del empujon,
// da ENDEREZAR_GOLPES golpes cortos y bruscos, una rueda fuerte y la otra suelta, alternando
// izquierda y derecha, para forzar a la rueda loca a ponerse derecha. 0 = sin golpes.
const byte ENDEREZAR_GOLPES = 4;                // 0 a 10
const int ENDEREZAR_FUERZA = 160;               // 60 a 255
const unsigned int ENDEREZAR_MS = 60;           // duracion de cada golpe, 20 a 200
const unsigned int ENDEREZAR_PAUSA_MS = 60;     // entre golpe y golpe va a la velocidad normal, 0 a 300
// Zigzag suave mientras va derecho (despues del enderezado): las ruedas se alternan un poco.
const int ZIG_DELTA = 12;                       // 0 a 30. Mas alto = zigzag mas marcado
const int ZIG_PULSO = 45;                       // potencia extra del golpe cada tanto (0 = sin golpes), 0 a 100
const int GIRO_MS_POR_GRADO = 8;                // cuanto tarda en girar 1 grado (nivel 6: girar, explorar), 1 a 30

// Valores en uso (arrancan en el cero, o en lo guardado en el robot).
int kickVel = KICK_VEL;
unsigned int kickMs = KICK_MS;
byte enderN = ENDEREZAR_GOLPES;
int enderFuerza = ENDEREZAR_FUERZA;
unsigned int enderMs = ENDEREZAR_MS, enderPausaMs = ENDEREZAR_PAUSA_MS;
int zigDelta = ZIG_DELTA, zigPulso = ZIG_PULSO, giroMs = GIRO_MS_POR_GRADO;
byte enderFase = 0;                 // 0 no, 1 golpe, 2 pausa
byte enderK = 0;                    // cuantos golpes lleva
unsigned long enderHasta = 0;
unsigned long kickHasta = 0;
// Zigzag suave: al ir derecho (o en reversa) las ruedas se alternan un poco, izq mas fuerte / der mas
// fuerte, para que la rueda loca no se "enganche" en una direccion. En promedio va recto.
// Ademas, cada tanto da un golpe corto de potencia a las dos ruedas para sacarla de los bordes.
bool zigzagOn = true;                       // 'zigzag 0' lo apaga, 'zigzag 1' lo enciende
const unsigned long ZIG_MEDIO_MS = 350UL;   // cada cuanto cambia de lado
const unsigned long ZIG_PULSO_MS = 70UL;    // duracion de cada golpe
const unsigned long ZIG_PULSO_CADA_MS = 1500UL;  // cada cuanto
int zigSigno = 1;
unsigned long zigCambio = 0, pulsoProximo = 0, pulsoHasta = 0;
int velIzq = VEL_IZQ_INICIAL, velDer = VEL_DER_INICIAL;    // 60 a 255 (por debajo de ~70 los motores no arrancan)

// Una rueda: v > 0 adelante, v < 0 atras, 0 parada (de -255 a 255).
void rueda(bool izquierda, int v) {
  if (izquierda ? INVERTIR_IZQ : INVERTIR_DER) v = -v;
  int fuerza = abs(v);
  byte a = izquierda ? IN1 : IN3;
  byte b = izquierda ? IN2 : IN4;
#if MAPA_PINES == 1
  if (v > 0)      { analogWrite(a, fuerza); digitalWrite(b, LOW); }
  else if (v < 0) { digitalWrite(a, LOW);   analogWrite(b, fuerza); }
  else            { digitalWrite(a, LOW);   digitalWrite(b, LOW); }
#else
  digitalWrite(a, v > 0 ? HIGH : LOW);
  digitalWrite(b, v < 0 ? HIGH : LOW);
  analogWrite(izquierda ? ENA : ENB, fuerza);
#endif
}

void aplicarMotores() {
  int vi = velIzq, vd = velDer;
  bool recto = (mov == 'F' || mov == 'B');
  if (kickHasta && mov != 'S') {                     // arranque desde cero: empujon, en cualquier sentido
    int mx = (vi > vd) ? vi : vd;
    if (mx > 0 && mx < kickVel) { vi = (long)vi * kickVel / mx; vd = (long)vd * kickVel / mx; }
  } else if (recto && enderFase == 1) {              // golpe del enderezado: una rueda fuerte, la otra suelta
    if (enderK % 2 == 0) { vi = enderFuerza; vd = 0; } else { vi = 0; vd = enderFuerza; }
  } else if (zigzagOn && recto && !enderFase) {      // zigzag y golpes de potencia
    vi += zigSigno * zigDelta; vd -= zigSigno * zigDelta;
    if (pulsoHasta) { vi += zigPulso; vd += zigPulso; }
    vi = constrain(vi, 60, 255); vd = constrain(vd, 60, 255);
  }
  switch (mov) {
    case 'F': rueda(true,  vi); rueda(false,  vd); break;
    case 'B': rueda(true, -vi); rueda(false, -vd); break;
    case 'L': rueda(true, -vi); rueda(false,  vd); break;
    case 'R': rueda(true,  vi); rueda(false, -vd); break;
    default:  rueda(true, 0);       rueda(false, 0);
  }
}

void detener() { mov = 'S'; kickHasta = 0; enderFase = 0; pulsoHasta = 0; aplicarMotores(); }

// seg = 0 significa "hasta que le digas parar" (con frenado de seguridad)
void mover(char m, float seg) {
  if (mov != 'S' && mov != m) {    // pausa corta al cambiar de sentido (cuida las baterias)
    detener();
    delay(80);
  }
  kickHasta = (mov != m) ? millis() + kickMs : 0;   // empujon solo si arranca o cambia de sentido
  if (mov != m) enderFase = 0;
  if (mov != m) { zigCambio = millis() + ZIG_MEDIO_MS; pulsoProximo = millis() + ZIG_PULSO_CADA_MS; pulsoHasta = 0; }
  mov = m;
  movInicio = millis();
  movFin = (seg > 0) ? movInicio + (unsigned long)(seg * 1000.0) : 0;
  aplicarMotores();
}

char movimientoDe(const char* w) {
  if (!strcmp(w, "adelante"))  return 'F';
  if (!strcmp(w, "atras"))     return 'B';
  if (!strcmp(w, "izquierda")) return 'L';
  if (!strcmp(w, "derecha"))   return 'R';
  return 0;
}

// Fin del arranque (empujon y enderezado): desde ahora corre el zigzag normal.
void arranqueTermino(unsigned long ahora) {
  zigCambio = ahora + ZIG_MEDIO_MS; pulsoProximo = ahora + ZIG_PULSO_CADA_MS; pulsoHasta = 0;
}

void tickMovimiento() {
  if (mov == 'S') return;
  unsigned long ahora = millis();
  if (kickHasta && (long)(ahora - kickHasta) >= 0) {           // fin del empujon
    kickHasta = 0;
    if ((mov == 'F' || mov == 'B') && enderN > 0) { enderFase = 1; enderK = 0; enderHasta = ahora + enderMs; }
    else arranqueTermino(ahora);
    aplicarMotores();
  }
  if (enderFase && (long)(ahora - enderHasta) >= 0) {          // golpes de enderezado
    if (enderFase == 1) { enderFase = 2; enderHasta = ahora + enderPausaMs; }
    else {
      enderK++;
      if (enderK >= enderN) { enderFase = 0; arranqueTermino(ahora); }
      else { enderFase = 1; enderHasta = ahora + enderMs; }
    }
    aplicarMotores();
  }
  if (zigzagOn && (mov == 'F' || mov == 'B') && !kickHasta && !enderFase) {
    bool cambio = false;
    if ((long)(ahora - zigCambio) >= 0) { zigSigno = -zigSigno; zigCambio = ahora + ZIG_MEDIO_MS; cambio = true; }
    if (pulsoHasta && (long)(ahora - pulsoHasta) >= 0) { pulsoHasta = 0; cambio = true; }
    if (zigPulso > 0 && !pulsoHasta && (long)(ahora - pulsoProximo) >= 0) {
      pulsoHasta = ahora + ZIG_PULSO_MS; pulsoProximo = ahora + ZIG_PULSO_CADA_MS; cambio = true;
    }
    if (cambio) aplicarMotores();
  }
  if (movFin > 0) {
    if ((long)(ahora - movFin) >= 0) detener();
  } else if (!explorando && ahora - movInicio > SEGURIDAD_MS) {
    detener();
    canalActual->println(F("parada de seguridad"));
  }
}
#endif

// ===========================================================
//  NIVEL 5: SENSOR Y SERVO
// ===========================================================
#if NIVEL >= 5
int umbral = 20;                   // cm. 0 = proteccion apagada
unsigned long ultMedida = 0;

// Devuelve la distancia en cm. 0 = no hay eco (nada a la vista).
long medirCm(byte trig, byte echo) {
  digitalWrite(trig, LOW);  delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long dur = pulseIn(echo, HIGH, 25000UL);
  if (dur == 0) return 0;
  return dur / 58;
}
long distanciaCm()       { return medirCm(TRIG, ECHO); }      // sensor delantero (con servo)
long distanciaAtrasCm()  { return medirCm(TRIG2, ECHO2); }    // sensor trasero (fijo)

// Mueve el servo con pulsos propios (unos 0,35 s) y lo deja quieto.
void servoIr(int ang) {
  ang = constrain(ang, 0, 180);
  unsigned int us = 544 + (unsigned long)ang * (2400 - 544) / 180;
  for (byte i = 0; i < 18; i++) {
    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(us);
    digitalWrite(SERVO_PIN, LOW);
    delay(20);
  }
}

// Un solo pulso (para mover el servo sin frenar al robot) y una version rapida.
void servoPulso(int ang) {
  ang = constrain(ang, 0, 180);
  unsigned int us = 544 + (unsigned long)ang * (2400 - 544) / 180;
  digitalWrite(SERVO_PIN, HIGH);
  delayMicroseconds(us);
  digitalWrite(SERVO_PIN, LOW);
}
void servoRapido(int ang) {          // unos 0,18 s, suficiente para saltos de 20 grados
  for (byte i = 0; i < 9; i++) { servoPulso(ang); delay(20); }
}

// Si va hacia adelante y hay algo cerca: frena.
void tickProteccion() {
  if (umbral == 0) return;
  bool atras = (mov == 'B');
  if (mov != 'F' && !(atras && HAY_SENSOR_TRASERO)) return;
  if (explorando && !atras) return;     // explorar vigila el frente por su cuenta (barriendo)
  if (millis() - ultMedida < 60) return;
  ultMedida = millis();
  long d = atras ? distanciaAtrasCm() : distanciaCm();
  if (d > 0 && d < umbral) {
    detener();
    canalActual->print(atras ? F("OBSTACULO ATRAS a ") : F("OBSTACULO a "));
    canalActual->print(d);
    canalActual->println(F(" cm"));
  }
}
#endif

// ===========================================================
//  NIVEL 4: PROGRAMAS
// ===========================================================
#if NIVEL >= 4
char prog[PASOS][PASO_LEN];
byte progN = 0;                    // cuantos pasos hay guardados
byte progIdx = 0;                  // paso que toca
byte progVeces = 0;                // vueltas que faltan
unsigned long progEsperaHasta = 0;
bool modoGrabar = false;

void grabarPaso(char* l) {
  Stream* s = canalActual;
  if (!strcmp(l, "fin")) {
    modoGrabar = false;
    s->print(F("Programa guardado: ")); s->print(progN);
    s->println(F(" pasos. Prueba: ejecutar"));
    return;
  }
  if (progN >= PASOS) { s->println(F("Memoria llena. Escribe: fin")); return; }
  strncpy(prog[progN], l, PASO_LEN - 1);
  prog[progN][PASO_LEN - 1] = 0;
  progN++;
  s->print(F("  paso ")); s->print(progN); s->print(F(": ")); s->println(prog[progN - 1]);
}
#endif

// ===========================================================
//  NIVEL 6: REGLAS Y EXPLORAR
// ===========================================================
#if NIVEL >= 6
char reaccion[PASO_LEN] = "";      // lo que hace cuando ve un obstaculo (vacio = decide solo)
unsigned long exploraInicio = 0;
#endif

// Porcentaje aproximado de una celda de litio segun su tension (en reposo).
int porcentajeCelda(float v) {
  static const float tv[] = {3.00, 3.30, 3.50, 3.70, 3.80, 4.00, 4.20};
  static const int   tp[] = {0, 5, 15, 40, 55, 80, 100};
  if (v <= tv[0]) return 0;
  if (v >= tv[6]) return 100;
  for (byte i = 1; i < 7; i++) {
    if (v <= tv[i]) return tp[i - 1] + (int)((v - tv[i - 1]) * (tp[i] - tp[i - 1]) / (tv[i] - tv[i - 1]));
  }
  return 100;
}

void reportarBateria() {
  Stream* s = canalActual;
  if (!HAY_MEDIDOR_BATERIA) {
    s->println(F("No tengo medidor de bateria todavia."));
    s->println(F("(Falta armarlo: ver el manual.)"));
    return;
  }
  long suma = 0;
  for (byte i = 0; i < 16; i++) suma += analogRead(PIN_BATERIA);
  float pin = (suma / 16.0) * 5.0 / 1023.0;
  float total = pin * (R_ALTA + R_BAJA) / R_BAJA;     // tension de las dos pilas
  int pct = porcentajeCelda(total / 2.0);
  s->print(F("Bateria: ")); s->print(total, 2); s->print(F(" V  (aprox. "));
  s->print(pct); s->println(F("%)"));
  if (total < 3.0) s->println(F("(Casi no hay tension: estan encendidas las baterias?)"));
  else if (pct < 20) s->println(F("Bateria baja: hay que cargarla."));
  s->println(F("(Medila con Roli quieto: al moverse la tension baja un poco.)"));
}

#if NIVEL >= 2
// Prueba guiada: cada rueda sola, 1.2 s adelante y 1.2 s atras. Para el adulto que arma.
void probarRuedas() {
  Stream* s = canalActual;
  s->println(F("PRUEBA: Roli en el aire o con espacio libre!"));
  for (byte i = 0; i < 2; i++) {
    bool izq = (i == 0);
    s->print(F("rueda ")); s->print(izq ? F("IZQUIERDA") : F("DERECHA")); s->println(F(" adelante..."));
    rueda(izq, 110); delay(1200); rueda(izq, 0); delay(500);
    s->println(F("  ...y atras"));
    rueda(izq, -110); delay(1200); rueda(izq, 0); delay(500);
  }
  s->println(F("Fin. Si una rueda giro al reves: INVERTIR_IZQ/DER = true."));
  s->println(F("Si no giro ninguna: cambia MAPA_PINES (1, 2 o 3)."));
}
#endif

// ---------- Ayuda ----------
void ayuda() {
  Stream* s = canalActual;
  s->print(F("--- NIVEL ")); s->print(NIVEL); s->println(F(" ---"));
  s->println(F("hola | info | bateria | di <texto>"));
  s->println(F("led 1 | led 0"));
  s->println(F("parpadear <veces>"));
#if NIVEL >= 2
  s->println(F("adelante atras izquierda"));
  s->println(F("derecha parar"));
  s->println(F("(atajos: d a i e r)"));
  s->println(F("probar (prueba ruedas)"));
#endif
#if NIVEL >= 3
  s->println(F("adelante 2 (segundos)"));
  s->println(F("velocidad 150"));
  s->println(F("velocidad izq 140"));
  s->println(F("zigzag 1 | zigzag 0"));
  s->println(F("calibrar ver | recto | guardar"));
  s->println(F("desvio izq | desvio der"));
#endif
#if NIVEL >= 4
  s->println(F("programa ... fin"));
  s->println(F("listar | ejecutar 2"));
  s->println(F("esperar 1 | borrar"));
#endif
#if NIVEL >= 5
  s->println(F("distancia | distancia atras"));
  s->println(F("escanear"));
  s->println(F("mirar izq|der|frente"));
  s->println(F("proteccion 20 (0=apaga)"));
#endif
#if NIVEL >= 6
  s->println(F("cuando obstaculo <orden>"));
  s->println(F("explorar (explorar 60 = 60 s)"));
  s->println(F("girar der|izq <grados>"));
#endif
}

// ---------- Interprete de ordenes ----------
void ejecutar(char* l, bool enPrograma);

// ===========================================================
//  NIVEL 3: CALIBRAR SIN VOLVER A CARGAR EL PROGRAMA
// ===========================================================
// "calibrar ..." cambia los valores del cero mientras Roli esta encendido; "calibrar guardar" los deja en
// la memoria del robot (EEPROM) y los recupera al prender; "calibrar exportar" imprime la lista en
// texto plano para llevarla al chat y reajustar el programa por USB; "calibrar cero" vuelve a fabrica.
#if NIVEL >= 3
const byte CAL_MAGIA = 0x52, CAL_VER = 1, CAL_N = 11;     // en la memoria: magia, version, 11 valores de 2 bytes, suma

int calGet(byte i) {
  switch (i) {
    case 0: return velIzq;       case 1: return velDer;      case 2: return kickVel;     case 3: return kickMs;
    case 4: return enderN;       case 5: return enderFuerza; case 6: return enderMs;     case 7: return enderPausaMs;
    case 8: return zigDelta;     case 9: return zigPulso;    default: return giroMs;
  }
}
void calSet(byte i, int v) {
  switch (i) {
    case 0: velIzq = v; break;       case 1: velDer = v; break;      case 2: kickVel = v; break;     case 3: kickMs = v; break;
    case 4: enderN = v; break;       case 5: enderFuerza = v; break; case 6: enderMs = v; break;     case 7: enderPausaMs = v; break;
    case 8: zigDelta = v; break;     case 9: zigPulso = v; break;    default: giroMs = v; break;
  }
}
// Rangos validos: se usan al escribir una orden y al leer la memoria (si algo no cuadra, se ignora todo).
bool calValido(byte i, long v) {
  static const int lo[CAL_N] = {60, 60, 60,   0,  0, 60,  20,   0,  0,   0,  1};
  static const int hi[CAL_N] = {255, 255, 255, 500, 10, 255, 200, 300, 30, 100, 30};
  return v >= lo[i] && v <= hi[i];
}
byte calSuma() {
  byte x = 0xA5;
  for (byte a = 0; a < 2 + CAL_N * 2; a++) x ^= (byte)(EEPROM.read(a) + a);
  return x;
}
void calGuardar() {
  EEPROM.update(0, CAL_MAGIA); EEPROM.update(1, CAL_VER);
  for (byte i = 0; i < CAL_N; i++) { int v = calGet(i); EEPROM.update(2 + i * 2, v & 0xFF); EEPROM.update(3 + i * 2, (v >> 8) & 0xFF); }
  EEPROM.update(2 + CAL_N * 2, calSuma());
}
// true si habia una calibracion guardada valida y la cargo.
bool calCargar() {
  if (EEPROM.read(0) != CAL_MAGIA || EEPROM.read(1) != CAL_VER || EEPROM.read(2 + CAL_N * 2) != calSuma()) return false;
  int v[CAL_N];
  for (byte i = 0; i < CAL_N; i++) {
    v[i] = EEPROM.read(2 + i * 2) | (EEPROM.read(3 + i * 2) << 8);
    if (!calValido(i, v[i])) return false;
  }
  for (byte i = 0; i < CAL_N; i++) calSet(i, v[i]);
  return true;
}
void calCero() {
  velIzq = VEL_IZQ_INICIAL; velDer = VEL_DER_INICIAL; kickVel = KICK_VEL; kickMs = KICK_MS;
  enderN = ENDEREZAR_GOLPES; enderFuerza = ENDEREZAR_FUERZA; enderMs = ENDEREZAR_MS; enderPausaMs = ENDEREZAR_PAUSA_MS;
  zigDelta = ZIG_DELTA; zigPulso = ZIG_PULSO; giroMs = GIRO_MS_POR_GRADO;
  EEPROM.update(0, 0xFF);                       // lo guardado ya no vale: al prender vuelve al cero
}

void calLinea(const __FlashStringHelper* nombre, int v) {
  canalActual->print(nombre); canalActual->print(F(" ")); canalActual->println(v);
}
void calVer() {
  Stream* s = canalActual;
  s->println(F("Calibracion de Roli:"));
  s->print(F("  velocidad izq ")); s->print(velIzq); s->print(F(" der ")); s->println(velDer);
  s->print(F("  kick ")); s->print(kickVel); s->print(F(" por ")); s->print((int)kickMs); s->println(F(" ms"));
  s->print(F("  enderezar ")); s->print((int)enderN); s->print(F(" golpes de ")); s->print(enderFuerza);
  s->print(F(" (")); s->print((int)enderMs); s->print(F(" ms, pausa ")); s->print((int)enderPausaMs); s->println(F(" ms)"));
  s->print(F("  zigzag ")); s->print(zigDelta); s->print(F(" golpe ")); s->println(zigPulso);
  s->print(F("  giro ")); s->print(giroMs); s->println(F(" ms por grado"));
}
// La lista para llevar al chat: los mismos nombres que tiene el programa (.ino) mas las ordenes equivalentes.
void calExportar() {
  Stream* s = canalActual;
  s->println(F("=== CALIBRACION DE ROLI (llevala al chat) ==="));
  s->print(F("programa: NIVEL ")); s->print(NIVEL); s->print(F(" MAPA ")); s->print(MAPA_PINES); s->println(F(" calibrar-v1"));
  calLinea(F("VEL_IZQ_INICIAL"), velIzq);
  calLinea(F("VEL_DER_INICIAL"), velDer);
  calLinea(F("KICK_VEL"), kickVel);
  calLinea(F("KICK_MS"), kickMs);
  calLinea(F("ENDEREZAR_GOLPES"), enderN);
  calLinea(F("ENDEREZAR_FUERZA"), enderFuerza);
  calLinea(F("ENDEREZAR_MS"), enderMs);
  calLinea(F("ENDEREZAR_PAUSA_MS"), enderPausaMs);
  calLinea(F("ZIG_DELTA"), zigDelta);
  calLinea(F("ZIG_PULSO"), zigPulso);
  calLinea(F("GIRO_MS_POR_GRADO"), giroMs);
  s->println(F("para volver a poner estos valores sin cargar el programa:"));
  s->print(F("calibrar velocidad ")); s->print(velIzq); s->print(F(" ")); s->println(velDer);
  s->print(F("calibrar kick ")); s->print(kickVel); s->print(F(" ")); s->println((int)kickMs);
  s->print(F("calibrar ender ")); s->print((int)enderN); s->print(F(" ")); s->print(enderFuerza); s->print(F(" ")); s->println((int)enderMs);
  s->print(F("calibrar zigzag ")); s->print(zigDelta); s->print(F(" ")); s->println(zigPulso);
  s->print(F("calibrar giro ")); s->println(giroMs);
  s->println(F("calibrar guardar"));
  s->println(F("=== FIN ==="));
}
// Lee un numero entero dentro de un rango; si no sirve, lo dice y devuelve false.
bool calNum(const char* t, byte i, int &v) {
  if (!esNumero(t)) return false;
  long n = atol(t);
  if (!calValido(i, n)) {
    canalActual->println(F("ese valor esta fuera de lo permitido (proba: calibrar ver)"));
    return false;
  }
  v = (int)n;
  return true;
}
void calibrar(char* a1, char* p) {
  Stream* s = canalActual;
  char* a2 = tomar(&p);
  char* a3 = tomar(&p);
  int v, w, x;
  if (!a1 || !strcmp(a1, "ver")) { calVer(); }
  else if (!strcmp(a1, "velocidad")) {
    if (calNum(a2, 0, v) && calNum(a3, 1, w)) { velIzq = v; velDer = w; aplicarMotores(); calVer(); }
    else s->println(F("Usa: calibrar velocidad 90 84   (izq der)"));
  }
  else if (!strcmp(a1, "kick")) {
    if (calNum(a2, 2, v)) { kickVel = v; if (esNumero(a3) && calNum(a3, 3, w)) kickMs = w; calVer(); }
    else s->println(F("Usa: calibrar kick 160   o   calibrar kick 160 150  (fuerza, ms)"));
  }
  else if (!strcmp(a1, "ender")) {
    char* a4 = tomar(&p);
    if (calNum(a2, 4, v)) {
      enderN = v;
      if (esNumero(a3) && calNum(a3, 5, w)) enderFuerza = w;
      if (esNumero(a4) && calNum(a4, 6, x)) enderMs = x;
      calVer();
    } else s->println(F("Usa: calibrar ender 4   o   calibrar ender 4 160 60  (golpes, fuerza, ms; 0 = sin golpes)"));
  }
  else if (!strcmp(a1, "zigzag")) {
    if (calNum(a2, 8, v)) { zigDelta = v; if (esNumero(a3) && calNum(a3, 9, w)) zigPulso = w; calVer(); }
    else s->println(F("Usa: calibrar zigzag 12   o   calibrar zigzag 12 45  (diferencia, golpe)"));
  }
  else if (!strcmp(a1, "giro")) {
#if NIVEL >= 6
    if (a2 && !strcmp(a2, "mas") && giroMs < 30) giroMs++;
    else if (a2 && !strcmp(a2, "menos") && giroMs > 1) giroMs--;
    else if (calNum(a2, 10, v)) giroMs = v;
    else { s->println(F("Usa: calibrar giro mas | menos | 8   (probalo con: girar der 90)")); return; }
    s->print(F("giro ")); s->print(giroMs); s->println(F(" ms por grado. Probalo: girar der 90"));
#else
    s->println(F("El giro se calibra desde el nivel 6."));
#endif
  }
  else if (!strcmp(a1, "recto")) {            // prueba guiada: avanza 2 segundos y te pide que le cuentes
    char t[] = "adelante 2";
    ejecutar(t, false);
    s->println(F("Fue derecho? Si se fue a la izquierda: desvio izq"));
    s->println(F("Si se fue a la derecha: desvio der. Si fue derecho: calibrar guardar"));
  }
  else if (!strcmp(a1, "guardar")) { calGuardar(); s->println(F("calibracion guardada en el robot")); calVer(); }
  else if (!strcmp(a1, "cero")) { calCero(); aplicarMotores(); s->println(F("vuelvo al cero de fabrica")); calVer(); }
  else if (!strcmp(a1, "exportar")) { calExportar(); }
  else s->println(F("Usa: calibrar ver | recto | velocidad | kick | ender | zigzag | giro | guardar | exportar | cero"));
}
// "desvio izq": Roli se fue hacia la izquierda, asi que su rueda izquierda rinde menos: le sube un poco la fuerza.
void desvio(char* a1, char* p) {
  Stream* s = canalActual;
  char* a2 = tomar(&p);
  int n = esNumero(a2) ? constrain(atoi(a2), 1, 20) : 2;
  bool izq = a1 && a1[0] == 'i', der = a1 && a1[0] == 'd';
  if (!izq && !der) { s->println(F("Usa: desvio izq  o  desvio der   (hacia donde se fue; opcional: cuanto, 1 a 20)")); return; }
  int &vel = izq ? velIzq : velDer;
  vel = constrain(vel + n, 60, 255);
  aplicarMotores();
  s->print(F("velocidad izq=")); s->print(velIzq); s->print(F(" der=")); s->println(velDer);
  s->println(F("Probalo de nuevo (calibrar recto). Si va derecho: calibrar guardar"));
}
#endif

#if NIVEL >= 6
// ---------- EXPLORAR ----------
// Avanza sin parar mientras el sensor barre de un lado a otro. Si algo queda cerca
// frena, mira alrededor (7 direcciones) y se va hacia donde ve MAS LEJOS.
// Tambien mide hacia atras (sensor trasero): si ahi hay mas lugar, da media vuelta.
const int BARRIDO_ABRE = 30;       // el sensor barre +-30 grados mientras avanza
const int BARRIDO_PASO = 15;
const int MARGEN_TRAS_FRENO = 10;  // cm extra que exige para reanudar despues de frenar
enum { EX_AVANZA, EX_ESPERA };
byte exFase = EX_AVANZA;
int exAng = 0;                     // hacia donde mira el sensor ahora (+ = izquierda)
int exDir = 1;
bool exListo = false;              // el servo ya tuvo tiempo de llegar
unsigned long exT = 0;
unsigned long exLimite = 0;        // 0 = sin limite
const int IZQ_SIGNO = (SERVO_IZQ >= SERVO_FRENTE) ? 1 : -1;

void girarGrados(bool izq, int grados) {
  mover(izq ? 'L' : 'R', (float)grados * giroMs / 1000.0);   // giroMs: calibralo con  calibrar giro
}

// Mira de izquierda a derecha (y hacia atras si hay sensor trasero) y anota cuanto ve
// en cada direccion. Las direcciones van en grados: + = izquierda, - = derecha, 180 = atras.
int exOff[9]; long exD[9]; byte exN = 0;

void mirarTodo() {
  Stream* s = canalActual;
  int span = abs(SERVO_IZQ - SERVO_FRENTE);
  int paso = span / 3; if (paso < 5) paso = 5;
  exN = 0;
  for (int off = span; off >= -span; off -= paso) {
    servoRapido(SERVO_FRENTE + IZQ_SIGNO * off);
    long d1 = distanciaCm(), d2 = distanciaCm();
    long d = (d1 == 0) ? d2 : (d2 == 0 ? d1 : (d1 < d2 ? d1 : d2));
    if (d == 0) d = 400;                    // sin eco = camino libre
    s->print(off > 0 ? F("izq ") : (off < 0 ? F("der ") : F("frente "))); s->print(abs(off));
    s->print(F(": ")); s->println(d);
    if (exN < 8) { exOff[exN] = off; exD[exN] = d; exN++; }
  }
  servoRapido(SERVO_FRENTE);
  if (HAY_SENSOR_TRASERO) {
    long d1 = distanciaAtrasCm(), d2 = distanciaAtrasCm();
    long d = (d1 == 0) ? d2 : (d2 == 0 ? d1 : (d1 < d2 ? d1 : d2));
    if (d == 0) d = 400;
    s->print(F("atras: ")); s->println(d);
    exOff[exN] = 180; exD[exN] = d; exN++;
  }
}

// La direccion con mas lugar entre las que ven al menos 'minimo' cm. Si empatan, la mas
// derecha (y atras solo si es estrictamente mejor). Devuelve 999 si ninguna alcanza.
int elegirDireccion(long minimo, long &dElegida) {
  int mejorOff = 999; dElegida = -1;
  for (byte i = 0; i < exN; i++) {
    if (exD[i] < minimo) continue;
    if (exD[i] > dElegida || (exD[i] == dElegida && abs(exOff[i]) < abs(mejorOff))) {
      dElegida = exD[i]; mejorOff = exOff[i];
    }
  }
  return mejorOff;
}

void explorarFin(const __FlashStringHelper* motivo);

void explorarDecidir() {
  Stream* s = canalActual;
  long uEx = (umbral > 0) ? umbral : 20;
  if (reaccion[0]) {                        // regla propia: cuando obstaculo <orden>
    char tmp[PASO_LEN];
    strcpy(tmp, reaccion);
    ejecutar(tmp, true);
    exFase = EX_ESPERA;
    return;
  }
  s->println(F("obstaculo! miro alrededor..."));
  mirarTodo();
  // Tras frenar exige MAS espacio que el normal (MARGEN_TRAS_FRENO) para volver a andar;
  // si ninguna direccion lo da, se conforma con el minimo.
  long dEl;
  int off = elegirDireccion(uEx + MARGEN_TRAS_FRENO, dEl);
  if (off == 999) {
    off = elegirDireccion(uEx, dEl);
    if (off != 999) s->println(F("poco espacio, pero paso"));
  }
  if (off == 999) {                         // todo bloqueado
    if (HAY_SENSOR_TRASERO) { explorarFin(F("atrapado: todo esta cerca, me detengo")); return; }
    s->println(F("sin salida: media vuelta"));
    girarGrados(false, 180);
    exFase = EX_ESPERA;
    return;
  }
  if (off == 180) {
    s->print(F("mejor camino: ATRAS, media vuelta (veo ")); s->print(dEl); s->println(F(" cm)"));
    girarGrados(false, 180);
  } else if (abs(off) < 10) {
    s->print(F("sigo derecho (veo ")); s->print(dEl); s->println(F(" cm)"));
  } else {
    s->print(F("giro ")); s->print(off > 0 ? F("izq ") : F("der ")); s->print(abs(off));
    s->print(F(" grados (veo ")); s->print(dEl); s->println(F(" cm)"));
    girarGrados(off > 0, abs(off));
  }
  exFase = EX_ESPERA;
}

void explorarFin(const __FlashStringHelper* motivo) {
  explorando = false;
  detener();
  servoRapido(SERVO_FRENTE);
  canalActual->println(motivo);
}

void tickExplorar() {
  if (!explorando) return;
  unsigned long ahora = millis();
  if (exLimite && ahora - exploraInicio > exLimite) { explorarFin(F("fin de explorar (tiempo)")); return; }

  if (exFase == EX_ESPERA) {                // esperando que termine el giro
    if (mov != 'S') return;
    exFase = EX_AVANZA; exAng = 0; exDir = 1; exListo = false;
  }

  // EX_AVANZA: sigue derecho y barre
  if (mov != 'F') mover('F', 0);
  if (ahora - exT < 40) return;
  exT = ahora;
  servoPulso(SERVO_FRENTE + IZQ_SIGNO * exAng);
  if (!exListo) { exListo = true; return; } // este turno solo mueve; el siguiente mide
  exListo = false;
  long uEx = (umbral > 0) ? umbral : 20;
  long lim = (abs(exAng) <= BARRIDO_PASO) ? uEx : (uEx * 7 / 10);   // a los costados, mas tolerante
  long d = distanciaCm();
  exAng += exDir * BARRIDO_PASO;
  if (exAng >= BARRIDO_ABRE)       { exAng = BARRIDO_ABRE;  exDir = -1; }
  else if (exAng <= -BARRIDO_ABRE) { exAng = -BARRIDO_ABRE; exDir = 1; }
  if (d > 0 && d < lim) { detener(); explorarDecidir(); }
}
#endif

#if NIVEL >= 4
void tickPrograma() {
  if (!progEjecutando || mov != 'S') return;
  if ((long)(millis() - progEsperaHasta) < 0) return;
  if (progIdx >= progN) {
    if (--progVeces > 0) {
      progIdx = 0;
    } else {
      progEjecutando = false;
      canalActual->println(F("programa terminado"));
      return;
    }
  }
  char tmp[PASO_LEN];
  strcpy(tmp, prog[progIdx]);
  progIdx++;
  canalActual->print(F("-> ")); canalActual->println(tmp);
  ejecutar(tmp, true);
}
#endif

void ejecutar(char* l, bool enPrograma) {
  Stream* s = canalActual;

  // "di ..." repite lo que sigue
  if (strncmp(l, "di ", 3) == 0) { s->println(l + 3); return; }

  char* p = l;
  const char* pal = tomar(&p);
  if (!pal) return;

#if NIVEL >= 2
  if (pal[1] == 0) {               // atajos de una letra
    switch (pal[0]) {
      case 'd': pal = "adelante";  break;
      case 'a': pal = "atras";     break;
      case 'i': pal = "izquierda"; break;
      case 'e': pal = "derecha";   break;
      case 'r': pal = "parar";     break;
    }
  }
#endif

  char* a1 = tomar(&p);

  if (!strcmp(pal, "hola")) {
    s->println(F("Hola! Soy Roli, el robot de Yacko y Kala."));
    s->println(F("Escribe ayuda para ver mis palabras."));
  }
  else if (!strcmp(pal, "bateria")) {
    reportarBateria();
  }
  else if (!strcmp(pal, "info")) {
    s->print(F("Roli | NIVEL ")); s->print(NIVEL);
    s->print(F(" | MAPA ")); s->println(MAPA_PINES);
    if (HAY_ENCODERS) {               // 18-nov: girar una rueda con la mano y mirar cuanto cuenta
      noInterrupts(); unsigned long ti = ticsIzq, td = ticsDer; interrupts();
      s->print(F("Ruedas (agujeros contados): izq ")); s->print((long)ti);
      s->print(F(" | der ")); s->println((long)td);
    }
    if (HAY_MEDIDOR_BATERIA) reportarBateria();
    pitido(80);
  }
#if NIVEL >= 2
  else if (!strcmp(pal, "probar")) {
    if (!enPrograma) { detener(); probarRuedas(); }
  }
#endif
  else if (!strcmp(pal, "ayuda")) {
    ayuda();
  }
  else if (!strcmp(pal, "led")) {
    if (a1 && a1[0] == '1')      { digitalWrite(LED, HIGH); ok("led encendido"); }
    else if (a1 && a1[0] == '0') { digitalWrite(LED, LOW);  ok("led apagado"); }
    else s->println(F("Usa: led 1  o  led 0"));
  }
  else if (!strcmp(pal, "parpadear")) {
    int n = esNumero(a1) ? atoi(a1) : 3;
    n = constrain(n, 1, 20);
    for (int i = 0; i < n; i++) {
      digitalWrite(LED, HIGH); delay(200);
      digitalWrite(LED, LOW);  delay(200);
    }
    ok("parpadear");
  }
#if NIVEL >= 2
  else if (movimientoDe(pal) != 0) {
    char m = movimientoDe(pal);
    float seg = 0;
#if NIVEL >= 3
    if (esNumero(a1)) seg = constrain(atof(a1), 0.1, 20.0);
    else if (enPrograma) seg = 1;      // en un programa, sin numero = 1 segundo
#endif
    if (!enPrograma) { progEjecutando = false; explorando = false; }
#if NIVEL >= 5
    if (m == 'F' && umbral > 0) {      // no arranca si ya hay algo cerca
      long d = distanciaCm();
      if (d > 0 && d < umbral) {
        s->print(F("No avanzo: obstaculo a ")); s->print(d); s->println(F(" cm"));
        return;
      }
    }
#endif
    mover(m, seg);
    if (!enPrograma) ok(pal);
  }
  else if (!strcmp(pal, "parar")) {
#if NIVEL >= 6
    bool estabaExplorando = explorando;
#endif
    if (!enPrograma) { progEjecutando = false; explorando = false; }
    detener();
#if NIVEL >= 6
    if (estabaExplorando && !enPrograma) servoRapido(SERVO_FRENTE);
#endif
    if (!enPrograma) ok("parar");
  }
#endif
#if NIVEL >= 3
  else if (!strcmp(pal, "zigzag")) {
    if (a1 && a1[0] == '0')      zigzagOn = false;
    else if (a1 && a1[0] == '1') zigzagOn = true;
    else { s->println(F("Usa: zigzag 1  o  zigzag 0")); return; }
    pulsoHasta = 0; aplicarMotores();
    s->println(zigzagOn ? F("zigzag encendido") : F("zigzag apagado"));
  }
  else if (!strcmp(pal, "velocidad")) {
    char* a2 = tomar(&p);
    if (a1 && !strcmp(a1, "izq") && esNumero(a2))      velIzq = constrain(atoi(a2), 60, 255);
    else if (a1 && !strcmp(a1, "der") && esNumero(a2)) velDer = constrain(atoi(a2), 60, 255);
    else if (esNumero(a1)) { velIzq = velDer = constrain(atoi(a1), 60, 255); }
    else { s->println(F("Usa: velocidad 150")); return; }
    aplicarMotores();
    s->print(F("velocidad izq=")); s->print(velIzq);
    s->print(F(" der="));         s->println(velDer);
  }
  else if (!strcmp(pal, "calibrar")) {
    if (!enPrograma) { progEjecutando = false; explorando = false; detener(); calibrar(a1, p); }
  }
  else if (!strcmp(pal, "desvio")) {
    if (!enPrograma) desvio(a1, p);
  }
#endif
#if NIVEL >= 4
  else if (!strcmp(pal, "esperar")) {
    float seg = esNumero(a1) ? constrain(atof(a1), 0.1, 20.0) : 1;
    if (enPrograma) progEsperaHasta = millis() + (unsigned long)(seg * 1000.0);
    else s->println(F("esperar va dentro de un programa"));
  }
  else if (!strcmp(pal, "programa") || !strcmp(pal, "nuevo")) {
    if (enPrograma) return;
    progEjecutando = false; explorando = false; detener();
    progN = 0; modoGrabar = true;
    s->println(F("Grabando. Escribe los pasos."));
    s->println(F("Cuando termines escribe: fin"));
  }
  else if (!strcmp(pal, "listar")) {
    if (progN == 0) s->println(F("(programa vacio)"));
    for (byte i = 0; i < progN; i++) {
      s->print(i + 1); s->print(F(": ")); s->println(prog[i]);
    }
  }
  else if (!strcmp(pal, "borrar")) {
    progN = 0; progEjecutando = false;
    ok("programa borrado");
  }
  else if (!strcmp(pal, "ejecutar")) {
    if (enPrograma) return;
    if (progN == 0) { s->println(F("No hay programa. Escribe: programa")); return; }
    byte veces = esNumero(a1) ? constrain(atoi(a1), 1, 9) : 1;
    explorando = false; detener();
    progIdx = 0; progVeces = veces; progEsperaHasta = 0; progEjecutando = true;
    s->print(F("ejecutando ")); s->print(veces); s->println(F(" vez/veces"));
  }
#endif
#if NIVEL >= 5
  else if (!strcmp(pal, "distancia")) {
    bool atras = (a1 && !strcmp(a1, "atras"));
    if (atras && !HAY_SENSOR_TRASERO) { s->println(F("no hay sensor trasero (HAY_SENSOR_TRASERO)")); }
    else {
      long d = atras ? distanciaAtrasCm() : distanciaCm();
      if (d == 0) s->println(F("no veo nada (muy lejos)"));
      else { s->print(atras ? F("atras: ") : F("distancia: ")); s->print(d); s->println(F(" cm")); }
    }
  }
  else if (!strcmp(pal, "proteccion")) {
    if (esNumero(a1)) umbral = constrain(atoi(a1), 0, 100);
    if (umbral == 0) s->println(F("proteccion apagada"));
    else { s->print(F("freno a ")); s->print(umbral); s->println(F(" cm")); }
  }
  else if (!strcmp(pal, "mirar")) {
    int ang = SERVO_FRENTE;
    if (a1 && !strcmp(a1, "izq")) ang = SERVO_IZQ;
    else if (a1 && !strcmp(a1, "der")) ang = SERVO_DER;
    else if (esNumero(a1)) ang = atoi(a1);
    servoIr(ang);
    ok("mirar");
  }
  else if (!strcmp(pal, "escanear")) {
    servoIr(SERVO_IZQ);   long dl = distanciaCm();
    servoIr(SERVO_FRENTE); long df = distanciaCm();
    servoIr(SERVO_DER);   long dr = distanciaCm();
    servoIr(SERVO_FRENTE);
    s->print(F("izq=")); s->print(dl);
    s->print(F(" frente=")); s->print(df);
    s->print(F(" der=")); s->println(dr);
  }
#endif
#if NIVEL >= 6
  else if (!strcmp(pal, "cuando")) {
    if (a1 && !strcmp(a1, "obstaculo")) {
      while (*p == ' ') p++;
      if (!*p || !strcmp(p, "nada")) {
        reaccion[0] = 0;
        s->println(F("sin regla: decido mirando"));
      } else {
        strncpy(reaccion, p, PASO_LEN - 1);
        reaccion[PASO_LEN - 1] = 0;
        s->print(F("regla: obstaculo -> ")); s->println(reaccion);
      }
    } else {
      s->println(F("Usa: cuando obstaculo izquierda 1"));
    }
  }
  else if (!strcmp(pal, "explorar")) {
    if (umbral == 0) umbral = 20;
    progEjecutando = false;
    exLimite = esNumero(a1) ? (unsigned long)constrain(atoi(a1), 1, 3600) * 1000UL : EXPLORAR_MAX_MS;
    exFase = EX_AVANZA; exAng = 0; exDir = 1; exListo = false;
    servoRapido(SERVO_FRENTE);
    explorando = true;
    exploraInicio = millis();
    s->println(F("Explorando sin parar! (parar me detiene)"));
  }
  else if (!strcmp(pal, "girar")) {         // para calibrar: girar der 90
    char* a2 = tomar(&p);
    if (a1 && esNumero(a2) && (!strcmp(a1, "izq") || !strcmp(a1, "der"))) {
      if (!enPrograma) { progEjecutando = false; explorando = false; }
      girarGrados(!strcmp(a1, "izq"), constrain(atoi(a2), 1, 360));
      if (!enPrograma) ok("girar");
    } else s->println(F("Usa: girar der 90  o  girar izq 90"));
  }
#endif
  else {
    s->print(F("No se esa palabra (todavia): "));
    s->println(pal);
  }
}

// ---------- Lectura de lineas (USB y Bluetooth) ----------
void procesarLinea(char* l) {
  for (char* q = l; *q; q++) {
    if (*q == ',') *q = '.';
    *q = tolower((unsigned char)*q);
  }
  while (*l == ' ') l++;
  size_t largo = strlen(l);
  while (largo && l[largo - 1] == ' ') l[--largo] = 0;
  if (!*l) return;
#if NIVEL >= 4
  if (modoGrabar) { grabarPaso(l); return; }
#endif
  ejecutar(l, false);
}

void leerCanal(Stream &s, Linea &l) {
  while (s.available()) {
    char c = s.read();
    l.t = millis();
    if (c == '\n' || c == '\r') {
      if (l.n) { l.b[l.n] = 0; l.n = 0; canalActual = &s; procesarLinea(l.b); }
    } else if (l.n < LINEA_MAX - 1) {
      l.b[l.n++] = c;
    }
  }
  // Sin salto de linea (por ejemplo una app con botones): procesa tras 250 ms
  if (l.n && millis() - l.t > 250) {
    l.b[l.n] = 0; l.n = 0; canalActual = &s; procesarLinea(l.b);
  }
}

// ---------- Programa principal ----------
void setup() {
  Serial.begin(9600);
  miBT.begin(9600);
  pinMode(LED, OUTPUT);
  if (HAY_ZUMBADOR) { pinMode(ZUMBADOR, OUTPUT); digitalWrite(ZUMBADOR, HIGH); }
  if (HAY_ENCODERS) {
    pinMode(ENC_IZQ, INPUT); pinMode(ENC_DER, INPUT);
    attachInterrupt(digitalPinToInterrupt(ENC_IZQ), ticIzq, RISING);
    attachInterrupt(digitalPinToInterrupt(ENC_DER), ticDer, RISING);
  }
#if NIVEL >= 2
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
#if MAPA_PINES != 1
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
#endif
  detener();
#endif
#if NIVEL >= 3
  bool hayCal = calCargar();               // lo guardado con "calibrar guardar"
#endif
#if NIVEL >= 5
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT);
  if (HAY_SENSOR_TRASERO) { pinMode(TRIG2, OUTPUT); pinMode(ECHO2, INPUT); }
  if (HAY_MEDIDOR_BATERIA) pinMode(PIN_BATERIA, INPUT);
  pinMode(SERVO_PIN, OUTPUT);
  servoIr(SERVO_FRENTE);
#endif
  Serial.print(F("Roli listo. NIVEL "));
  Serial.print(NIVEL);
  Serial.print(F(" MAPA "));
  Serial.println(MAPA_PINES);
#if NIVEL >= 3
  Serial.println(hayCal ? F("Calibracion guardada: cargada") : F("Calibracion: el cero de fabrica"));
#endif
  Serial.println(F("Escribe: hola"));
  pitido(120); delay(80); pitido(120);     // Roli se despierta: dos pitidos
}

void loop() {
  leerCanal(Serial, lUSB);
  leerCanal(miBT, lBT);
#if NIVEL >= 2
  tickMovimiento();
#endif
#if NIVEL >= 4
  tickPrograma();
#endif
#if NIVEL >= 5
  tickProteccion();
#endif
#if NIVEL >= 6
  tickExplorar();
#endif
}