#include <Arduino.h>
#include <SoftwareSerial.h>
#include <cstdio>
#include <deque>
static unsigned long T = 0;
unsigned long millis() { return T; }
void delay(unsigned long ms) { T += ms; }
unsigned int lastUs=1500;
void delayMicroseconds(unsigned int us) { if(us>=500&&us<=2500) lastUs=us; static unsigned long a = 0; a += us; T += a / 1000; a %= 1000; }
int pins[20];
void pinMode(byte, byte) {}
void digitalWrite(byte p, byte v) { pins[p] = v ? 256 : 0; }
void analogWrite(byte p, int v) { pins[p] = v; }
int lecturaFalsa = 800;
int analogRead(byte) { return lecturaFalsa; }
long distSim = 100; int mundo = 0;
int rearD = 100;
unsigned long pulseIn(byte pin, byte, unsigned long) {
  if (pin == A4) return rearD * 58;
  long d = distSim;
  if (mundo == 1) { int ang = (lastUs-544)*180/1856; d = (ang >= 120) ? 200 : 15; }
  if (mundo == 2) d = 12;
  if (mundo == 3) { int ang = (lastUs-544)*180/1856; d = (ang >= 120) ? 25 : 15; }
  return d == 0 ? 0 : d * 58; }
size_t Print::print(const char* s) { fputs(s, stdout); return 0; }
size_t Print::print(const __FlashStringHelper* s) { fputs((const char*)s, stdout); return 0; }
size_t Print::print(int v) { printf("%d", v); return 0; }
size_t Print::print(double v, int d) { printf("%.*f", d, v); return 0; }
size_t Print::print(unsigned int v) { printf("%u", v); return 0; }
size_t Print::print(long v) { printf("%ld", v); return 0; }
size_t Print::println(const char* s) { printf("%s\n", s); return 0; }
size_t Print::println(const __FlashStringHelper* s) { printf("%s\n", (const char*)s); return 0; }
size_t Print::println(int v) { printf("%d\n", v); return 0; }
size_t Print::println(long v) { printf("%ld\n", v); return 0; }
std::deque<char> inUSB, inBT;
void HardwareSerial::begin(long) {}
int HardwareSerial::available() { return inUSB.size(); }
int HardwareSerial::read() { char c = inUSB.front(); inUSB.pop_front(); return c; }
HardwareSerial Serial;
void SoftwareSerial::begin(long) {}
int SoftwareSerial::available() { return inBT.size(); }
int SoftwareSerial::read() { char c = inBT.front(); inBT.pop_front(); return c; }
#include SKETCH
void feed(const char* s, bool nl = true) { for (; *s; s++) inUSB.push_back(*s); if (nl) inUSB.push_back('\n'); }
void run(unsigned ms) { unsigned long e = T + ms; while (T < e) { loop(); T += 5; } }
void say(const char* t) { printf("\n### %s\n", t); }
void motores() { printf("   [t=%lu pines5..10 = %d %d %d %d %d %d]\n", T, pins[5], pins[6], pins[7], pins[8], pins[9], pins[10]); }
int main() {
  setup();
  feed("explorar"); mundo = 0; run(800); motores();
  say("pared de frente y derecha, izquierda libre, atras libre"); mundo = 1; rearD = 100; run(600); motores();
  mundo = 0; run(2500); motores();
  say("callejon: adelante y costados cerrados, atras libre 150"); mundo = 2; rearD = 150; run(2500); motores(); mundo = 0; run(1500); motores();
  say("todo bloqueado"); mundo = 2; rearD = 12; run(2500); motores();
  say("margen: izq 25 cm (<20+10), atras 15"); mundo = 3; rearD = 15; feed("explorar"); run(2500); motores();
  return 0;
}
