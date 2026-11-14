#include <Arduino.h>
#include <SoftwareSerial.h>
#include <cstdio>
#include <deque>
#include <string>
#include <cassert>
static unsigned long T = 0;
unsigned long millis() { return T; }
void delay(unsigned long ms) { T += ms; }
void delayMicroseconds(unsigned int us) { static unsigned long a = 0; a += us; T += a / 1000; a %= 1000; }
int pins[20];
void pinMode(byte, byte) {}
void digitalWrite(byte p, byte v) { pins[p] = v ? 256 : 0; }
void analogWrite(byte p, int v) { pins[p] = v; }
int lecturaFalsa = 800;
int analogRead(byte) { return lecturaFalsa; }
long distSim = 100;
unsigned long pulseIn(byte, byte, unsigned long) { return distSim == 0 ? 0 : distSim * 58; }
std::string cap; bool capturando = false;
void sal(const char* s) { fputs(s, stdout); if (capturando) cap += s; }
size_t Print::print(const char* s) { sal(s); return 0; }
size_t Print::print(const __FlashStringHelper* s) { sal((const char*)s); return 0; }
size_t Print::print(int v) { char b[16]; snprintf(b, 16, "%d", v); sal(b); return 0; }
size_t Print::print(double v, int d) { printf("%.*f", d, v); return 0; }
size_t Print::print(unsigned int v) { char b[16]; snprintf(b, 16, "%u", v); sal(b); return 0; }
size_t Print::print(long v) { char b[24]; snprintf(b, 24, "%ld", v); sal(b); return 0; }
size_t Print::println(const char* s) { sal(s); sal("\n"); return 0; }
size_t Print::println(const __FlashStringHelper* s) { sal((const char*)s); sal("\n"); return 0; }
size_t Print::println(int v) { print(v); sal("\n"); return 0; }
size_t Print::println(long v) { print(v); sal("\n"); return 0; }
std::deque<char> inUSB, inBT;
void HardwareSerial::begin(long) {}
int HardwareSerial::available() { return inUSB.size(); }
int HardwareSerial::read() { char c = inUSB.front(); inUSB.pop_front(); return c; }
HardwareSerial Serial;
void SoftwareSerial::begin(long) {}
int SoftwareSerial::available() { return inBT.size(); }
int SoftwareSerial::read() { char c = inBT.front(); inBT.pop_front(); return c; }
#include SKETCH
void feed(const char* s) { for (; *s; s++) inUSB.push_back(*s); inUSB.push_back('\n'); }
void run(unsigned ms) { unsigned long e = T + ms; while (T < e) { loop(); T += 5; } }
int fallos = 0;
#define CHECK(c, msg) do { if (c) printf("  ok   %s\n", msg); else { printf("  MAL  %s\n", msg); fallos++; } } while (0)
bool contiene(const char* t) { return cap.find(t) != std::string::npos; }
// muestrea los pines cada 5 ms y cuenta los golpes de enderezado (una rueda fuerte, la otra parada)
struct Muestra { int golpes, kick, maxPausa; bool unaParada; };
Muestra mirarArranque(int pa, int pb, unsigned ms) {   // pa/pb: pines de avance de la izq y la der
  Muestra m = {0, 0, 0, false}; bool enGolpe = false;
  unsigned long e = T + ms;
  while (T < e) {
    loop(); T += 5;
    int a = pins[pa], b = pins[pb];
    bool golpe = (a == 160 && b == 0) || (a == 0 && b == 160);
    if (golpe && !enGolpe) m.golpes++;
    enGolpe = golpe;
    if (a == 160 && b == 149) m.kick++;
    if (a == 0 || b == 0) m.unaParada = true;
  }
  return m;
}
int main() {
  setup();
  printf("\n### el cero\n");
  CHECK(velIzq == 90 && velDer == 84, "velocidad de fabrica 90 / 84");
  CHECK(kickVel == 160 && enderN == 4, "kick 160 y 4 golpes de enderezado");
  CHECK(contiene("") , "arranca");

  printf("\n### arranque hacia adelante: parte de cero, empujon, golpes, crucero\n");
  CHECK(pins[5] == 0 && pins[9] == 0, "antes de moverse las ruedas estan en cero");
  feed("adelante");
  Muestra m = mirarArranque(5, 9, 1200);
  CHECK(m.kick > 0, "empujon de 160 (der proporcional 149)");
  CHECK(m.golpes == 4, "cuatro golpes de enderezado");
  CHECK(pins[5] >= 78 && pins[5] <= 102 && pins[9] >= 72 && pins[9] <= 96, "despues anda a crucero 90/84 con el zigzag suave");
  feed("parar"); run(30);
  CHECK(pins[5] == 0 && pins[9] == 0, "parar deja las ruedas en cero");

  printf("\n### hacia atras: lo mismo, por las patas de retroceso\n");
  feed("atras");
  Muestra mb = mirarArranque(6, 10, 1200);
  CHECK(mb.kick > 0 && mb.golpes == 4, "atras tambien: empujon y cuatro golpes");
  feed("parar"); run(30);

  printf("\n### un giro lleva el empujon pero NO los golpes\n");
  feed("izquierda 1"); run(10);
  CHECK(pins[6] == 160 && pins[9] == 149, "giro: empujon 160/149 (izq atras, der adelante)");
  bool algunaParada = false; for (int i = 0; i < 60; i++) { run(10); if (pins[6] == 0 || pins[9] == 0) algunaParada = true; }
  CHECK(!algunaParada, "el giro no tiene golpes de enderezado");
  feed("parar"); run(30);

  printf("\n### calibrar sin cargar el programa\n");
  feed("calibrar velocidad 100 90"); run(10);
  CHECK(velIzq == 100 && velDer == 90, "calibrar velocidad 100 90");
  feed("calibrar velocidad 30 90"); run(10);
  CHECK(velIzq == 100 && velDer == 90, "un valor fuera de rango se rechaza y no cambia nada");
  feed("calibrar kick 180 200"); feed("calibrar ender 3 150 50"); feed("calibrar zigzag 8 30"); feed("calibrar giro mas"); run(10);
  CHECK(kickVel == 180 && kickMs == 200 && enderN == 3 && enderFuerza == 150 && enderMs == 50 && zigDelta == 8 && zigPulso == 30 && giroMs == 9, "kick, ender, zigzag y giro");
  feed("desvio izq"); feed("desvio der 5"); run(10);
  CHECK(velIzq == 102 && velDer == 95, "desvio izq suma 2 a la izquierda; desvio der 5 suma 5 a la derecha");
  feed("desvio arriba"); run(10);
  CHECK(velIzq == 102 && velDer == 95, "un desvio que no es izq ni der no cambia nada");
  for (int i = 0; i < 40; i++) feed("desvio izq 20"); run(10);
  CHECK(velIzq == 255, "el desvio no pasa de 255");

  printf("\n### guardar, apagar y volver a prender\n");
  feed("calibrar velocidad 91 85"); feed("calibrar guardar"); run(10);
  velIzq = 1; velDer = 2; kickVel = 3; giroMs = 99;            // como si se hubiera apagado
  CHECK(calCargar() && velIzq == 91 && velDer == 85 && kickVel == 180 && giroMs == 9, "lo guardado vuelve al prender");
  EEPROM.write(5, EEPROM.read(5) ^ 0xFF);                       // un byte roto
  velIzq = 50;
  CHECK(!calCargar() && velIzq == 50, "memoria rota: se ignora y no pisa nada");
  EEPROM.write(5, EEPROM.read(5) ^ 0xFF);
  calGuardar(); EEPROM.update(2, 10);                           // un valor imposible con la suma al dia
  EEPROM.update(2 + CAL_N * 2, calSuma());
  CHECK(!calCargar(), "un valor fuera de rango en la memoria se rechaza aunque la suma cierre");

  printf("\n### exportar: la lista para llevar al chat\n");
  calCero(); calGuardar(); feed("calibrar velocidad 92 86"); run(10);
  cap.clear(); capturando = true; feed("calibrar exportar"); run(10); capturando = false;
  CHECK(contiene("=== CALIBRACION DE ROLI") && contiene("=== FIN ==="), "empieza y termina con marcas");
  CHECK(contiene("VEL_IZQ_INICIAL 92\n") && contiene("VEL_DER_INICIAL 86\n"), "VEL_IZQ_INICIAL 92 / VEL_DER_INICIAL 86 con los nombres del programa");
  CHECK(contiene("KICK_VEL 160\n") && contiene("KICK_MS 150\n") && contiene("ENDEREZAR_GOLPES 4\n") && contiene("ENDEREZAR_FUERZA 160\n") && contiene("ENDEREZAR_MS 60\n") && contiene("ENDEREZAR_PAUSA_MS 60\n") && contiene("ZIG_DELTA 12\n") && contiene("ZIG_PULSO 45\n") && contiene("GIRO_MS_POR_GRADO 8\n"), "todos los valores");
  CHECK(contiene("calibrar velocidad 92 86\n") && contiene("calibrar kick 160 150\n") && contiene("calibrar ender 4 160 60\n") && contiene("calibrar zigzag 12 45\n") && contiene("calibrar guardar\n"), "y las ordenes para volver a ponerlos");

  printf("\n### el cero\n");
  feed("calibrar cero"); run(10);
  CHECK(velIzq == 90 && velDer == 84 && kickVel == 160 && enderN == 4 && giroMs == 8, "calibrar cero vuelve a fabrica");
  CHECK(!calCargar(), "y borra lo guardado (al prender vuelve al cero)");

  printf("\n### enderezar 0 apaga los golpes\n");
  feed("calibrar ender 0"); run(10);
  feed("adelante"); Muestra z = mirarArranque(5, 9, 800);
  CHECK(z.golpes == 0 && !z.unaParada, "sin golpes");
  feed("parar"); run(30);

  printf("\n### no se calibra desde un programa\n");
  feed("programa"); feed("calibrar velocidad 200 200"); feed("fin"); feed("ejecutar"); run(200);
  CHECK(velIzq == 90, "un programa no puede calibrar");

  printf("\n%s\n", fallos ? "HAY FALLOS" : "TODO BIEN");
  return fallos ? 1 : 0;
}
