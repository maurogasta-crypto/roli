#!/bin/bash
# Habla con Roli. Doble clic o:  ./roli.sh
# Antes: Roli encendido y el celular desconectado del modulo Bluetooth.
cd "$(dirname "$0")"
# Si el Bluetooth de la laptop quedo apagado o bloqueado, lo enciende.
rfkill unblock bluetooth 2>/dev/null
bluetoothctl power on >/dev/null 2>&1
sleep 1
exec ~/ble-env/bin/python consola_robot.py 2C:4C:8D:D7:61:C4
