# Banco de pruebas del firmware (Arduino simulado)

`Arduino.h` y `SoftwareSerial.h` son una cabecera mínima que deja compilar el `.ino` con `g++` en cualquier computadora. Los `sim_*.cpp` lo corren con un reloj falso y un sensor falso.

## Compilar sólo la sintaxis (niveles 1 a 6 y los tres mapas de pines)

```
for n in 1 2 3 4 5 6; do
  sed "s/#define NIVEL [0-9]/#define NIVEL $n/" ../firmware/roli_programa.ino > /tmp/t.ino
  g++ -fsyntax-only -Wall -x c++ -I. -include Arduino.h /tmp/t.ino
done
for m in 2 3; do
  sed "s/#define MAPA_PINES 1/#define MAPA_PINES $m/" ../firmware/roli_programa.ino > /tmp/t.ino
  g++ -fsyntax-only -x c++ -I. -include Arduino.h /tmp/t.ino
done
```

## Correr una simulación

```
sed "s/#define NIVEL [0-9]/#define NIVEL 6/" ../firmware/roli_programa.ino > sk.ino
g++ -x c++ -I. sim_zig.cpp -o sim_zig -DSKETCH='"sk.ino"' && ./sim_zig
```

| Archivo | Qué prueba |
|---|---|
| `sim.cpp` | recorrido general: niveles 1 a 6, programas, protección, regla de obstáculo |
| `sim_ex.cpp` | `explorar`: pared al frente y a la derecha, callejón con salida atrás, todo bloqueado, margen tras frenar |
| `sim_kick.cpp` | empujón de arranque al retroceder y al girar (y que adelante no lo lleva) |
| `sim_zig.cpp` | zigzag y golpes de potencia al avanzar, y `zigzag 0` |
| `sim_bat.cpp` | medidor de batería (porcentaje por celda) |
| `sim_probar.cpp` | el comando `probar` de las ruedas |

El sensor falso devuelve la distancia que se le fija (`distSim`, `mundo`, `rearD`). Esto prueba la lógica, no el hardware: la medición real del sensor, el servo y el efecto del zigzag se comprueban en el robot.
