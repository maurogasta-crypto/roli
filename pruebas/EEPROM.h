// EEPROM de mentira para el banco de pruebas: una memoria de 1 KB en RAM.
#pragma once
#include <cstdint>
struct EEPROMClass {
  uint8_t m[1024];
  EEPROMClass() { for (int i = 0; i < 1024; i++) m[i] = 0xFF; }
  uint8_t read(int a) { return m[a]; }
  void write(int a, uint8_t v) { m[a] = v; }
  void update(int a, uint8_t v) { if (m[a] != v) m[a] = v; }
};
static EEPROMClass EEPROM;
