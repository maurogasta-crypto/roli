// Simulador minimo de Arduino, solo para comprobar que el sketch compila.
#pragma once
#define A0 14
#define A1 15
#define A2 16
#define A3 17
#define A4 18
#define A5 19
#include <cstring>
#include <cstdlib>
#include <cctype>
#include <cstdint>
typedef uint8_t byte;
#define HIGH 1
#define LOW 0
#define OUTPUT 1
#define INPUT 0
#define constrain(amt, low, high) ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))
class __FlashStringHelper;
#define F(x) (reinterpret_cast<const __FlashStringHelper*>(x))
void pinMode(byte, byte);
void digitalWrite(byte, byte);
void analogWrite(byte, int);
int analogRead(byte);
unsigned long millis();
void delay(unsigned long);
void delayMicroseconds(unsigned int);
unsigned long pulseIn(byte, byte, unsigned long);
class Print {
 public:
  size_t print(const char*);
  size_t print(const __FlashStringHelper*);
  size_t print(int);
  size_t print(double, int);
  size_t print(unsigned int);
  size_t print(long);
  size_t println(const char*);
  size_t println(const __FlashStringHelper*);
  size_t println(int);
  size_t println(long);
};
class Stream : public Print {
 public:
  virtual int available() = 0;
  virtual int read() = 0;
};
class HardwareSerial : public Stream {
 public:
  void begin(long);
  int available() override;
  int read() override;
};
extern HardwareSerial Serial;
