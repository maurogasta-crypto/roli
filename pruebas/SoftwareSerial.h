#pragma once
#include <Arduino.h>
class SoftwareSerial : public Stream {
 public:
  SoftwareSerial(byte, byte) {}
  void begin(long);
  int available() override;
  int read() override;
};
