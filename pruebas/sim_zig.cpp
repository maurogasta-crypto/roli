#include <Arduino.h>
#include <SoftwareSerial.h>
#include <cstdio>
#include <deque>
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
  feed("adelante"); 
  for (int k=0;k<40;k++){ run(40); motores(); }
  feed("zigzag 0"); run(100); motores(); run(400); motores(); feed("parar"); run(20); motores();
  return 0;
}
