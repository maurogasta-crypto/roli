#!/bin/bash
# Corre todo el banco del firmware: compila los 6 niveles y los 3 mapas de pines, corre las simulaciones
# y comprueba que firmware/calibracion_cero.txt diga lo mismo que el .ino.   bash pruebas/correr.sh
cd "$(dirname "$0")" || exit 1
mal=0
for n in 1 2 3 4 5 6; do
  sed "s/#define NIVEL [0-9]/#define NIVEL $n/" ../firmware/roli_programa.ino > /tmp/roli_t.ino
  g++ -fsyntax-only -Wall -x c++ -I. -include Arduino.h /tmp/roli_t.ino 2>&1 | head -5
  [ "${PIPESTATUS[0]}" = 0 ] && echo "  ok   compila el nivel $n" || { echo "  MAL  nivel $n"; mal=1; }
done
for m in 2 3; do
  sed "s/#define MAPA_PINES 1/#define MAPA_PINES $m/" ../firmware/roli_programa.ino > /tmp/roli_t.ino
  g++ -fsyntax-only -x c++ -I. -include Arduino.h /tmp/roli_t.ino 2>&1 | head -5
  [ "${PIPESTATUS[0]}" = 0 ] && echo "  ok   compila el mapa de pines $m" || { echo "  MAL  mapa $m"; mal=1; }
done
sed "s/#define NIVEL [0-9]/#define NIVEL 6/" ../firmware/roli_programa.ino > /tmp/roli_sk.ino
for s in sim sim_ex sim_zig sim_kick sim_probar sim_bat sim_calibrar; do
  g++ -x c++ -I. $s.cpp -o /tmp/roli_$s -DSKETCH='"/tmp/roli_sk.ino"' 2>&1 | head -3
  /tmp/roli_$s > /tmp/roli_$s.out 2>&1; r=$?
  [ $r = 0 ] && echo "  ok   corre $s" || { echo "  MAL  $s (salio con $r)"; mal=1; }
done
grep -q "TODO BIEN" /tmp/roli_sim_calibrar.out && echo "  ok   sim_calibrar: todo bien" || { echo "  MAL  sim_calibrar"; grep MAL /tmp/roli_sim_calibrar.out; mal=1; }
python3 calibracion_test.py > /tmp/roli_cal.out 2>&1 && echo "  ok   la consola: lista de calibracion (8+4 casos)" || { echo "  MAL  calibracion_test.py"; tail -5 /tmp/roli_cal.out; mal=1; }
# el archivo del cero tiene que decir lo mismo que el programa
for k in VEL_IZQ_INICIAL VEL_DER_INICIAL KICK_VEL KICK_MS ENDEREZAR_GOLPES ENDEREZAR_FUERZA ENDEREZAR_MS ENDEREZAR_PAUSA_MS ZIG_DELTA ZIG_PULSO GIRO_MS_POR_GRADO; do
  ino=$(grep -oE "(^|[ ,])$k = [0-9]+" ../firmware/roli_programa.ino | head -1 | grep -oE "[0-9]+$")
  txt=$(grep -E "^$k [0-9]+$" ../firmware/calibracion_cero.txt | awk '{print $2}')
  [ -n "$ino" ] && [ "$ino" = "$txt" ] || { echo "  MAL  calibracion_cero.txt: $k dice '$txt' y el .ino '$ino'"; mal=1; }
done
[ $mal = 0 ] && echo "  ok   calibracion_cero.txt coincide con el .ino"
[ $mal = 0 ] && echo "TODO BIEN" || echo "HAY FALLOS"
exit $mal
