#!/usr/bin/env python3
"""Consola de Roli (el robot de Yacko y Kala) por Bluetooth Low Energy (BLE) para Linux.

Hace dos cosas:
  1) CONSOLA: escribis una orden ("adelante 2"), Enter, y ves lo que contesta
     el robot en la pantalla.
  2) TECLADO: escribi  teclado  y manejas el robot con las flechas o WASD.

Uso:
    ~/ble-env/bin/python consola_robot.py                  # MAC por defecto
    ~/ble-env/bin/python consola_robot.py 2C:4C:8D:D7:61:C4

Antes: robot encendido y celular desconectado del modulo (acepta una sola
conexion a la vez).
"""
import asyncio
import codecs
import os
import subprocess
import sys
import termios
import time
import tty

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakBluetoothNotAvailableError

MAC_POR_DEFECTO = "2C:4C:8D:D7:61:C4"
UUID_FFE1 = "0000ffe1-0000-1000-8000-00805f9b34fb"
TROZO = 20            # un paquete BLE lleva hasta 20 bytes utiles

AYUDA_TECLADO = """
=== MODO TECLADO ===
  W o flecha arriba ... adelante      S o flecha abajo .... atras
  A o flecha izquierda  izquierda     D o flecha derecha .. derecha
  ESPACIO o X ......... parar         + / - ............... velocidad
  M ................... distancia      E ................... explorar
  Q ................... volver a la consola
(mantene apretada una tecla para seguir avanzando)
"""


def elegir_caracteristica(client):
    """Devuelve la caracteristica FFE1; si no esta, la primera escribible."""
    candidata = None
    for servicio in client.services:
        for car in servicio.characteristics:
            if car.uuid.lower() == UUID_FFE1:
                return car
            if candidata is None and (
                "write" in car.properties or "write-without-response" in car.properties
            ):
                candidata = car
    return candidata


def trocear(datos, n=TROZO):
    """Parte un mensaje en paquetes de hasta n bytes."""
    return [datos[i:i + n] for i in range(0, len(datos), n)]


def interpretar_tecla(datos):
    """Convierte los bytes que llegan del teclado en un nombre de accion."""
    if datos[:3] == b"\x1b[A":
        return "adelante"
    if datos[:3] == b"\x1b[B":
        return "atras"
    if datos[:3] == b"\x1b[C":
        return "derecha"
    if datos[:3] == b"\x1b[D":
        return "izquierda"
    tecla = datos[:1].lower()
    return {
        b"w": "adelante", b"s": "atras", b"a": "izquierda", b"d": "derecha",
        b" ": "parar", b"x": "parar", b"+": "mas", b"-": "menos",
        b"m": "distancia", b"e": "explorar", b"q": "salir",
    }.get(tecla)


class Robot:
    def __init__(self, client, caracteristica):
        self.client = client
        self.car = caracteristica
        self.sin_respuesta = "write-without-response" in caracteristica.properties

    async def enviar(self, texto):
        datos = (texto.strip() + "\n").encode("ascii", "ignore")
        for trozo in trocear(datos):
            await self.client.write_gatt_char(self.car, trozo, response=not self.sin_respuesta)
            await asyncio.sleep(0.03)


async def modo_teclado(robot):
    """Control remoto con el teclado (lee teclas sin esperar Enter)."""
    fd = sys.stdin.fileno()
    guardado = termios.tcgetattr(fd)
    loop = asyncio.get_running_loop()
    cola = asyncio.Queue()
    velocidad = 150
    ultimo = ("", 0.0)

    print(AYUDA_TECLADO)
    tty.setcbreak(fd)
    loop.add_reader(fd, lambda: cola.put_nowait(os.read(fd, 8)))
    try:
        while robot.client.is_connected:
            accion = interpretar_tecla(await cola.get())
            if accion is None:
                continue
            if accion == "salir":
                await robot.enviar("parar")
                break
            if accion == "mas":
                velocidad = min(255, velocidad + 20)
                accion = f"velocidad {velocidad}"
            elif accion == "menos":
                velocidad = max(60, velocidad - 20)
                accion = f"velocidad {velocidad}"
            ahora = time.monotonic()
            if accion == ultimo[0] and ahora - ultimo[1] < 0.25:
                continue          # evita inundar al robot al mantener una tecla
            ultimo = (accion, ahora)
            await robot.enviar(accion)
    finally:
        loop.remove_reader(fd)
        termios.tcsetattr(fd, termios.TCSADRAIN, guardado)
    print("\nVolviste a la consola.")


def encender_bluetooth():
    """Desbloquea y enciende el adaptador de la laptop (no necesita sudo)."""
    for cmd in (["rfkill", "unblock", "bluetooth"], ["bluetoothctl", "power", "on"]):
        try:
            subprocess.run(cmd, capture_output=True, timeout=10)
        except Exception:
            pass
    time.sleep(1.5)


async def sesion(mac):
    """Una conexion con Roli. Devuelve 'salir', 'caida', 'no_encontrado' o 'sin_adaptador'."""
    decodificador = codecs.getincrementaldecoder("utf-8")(errors="replace")

    def al_recibir(_, datos):
        print(decodificador.decode(bytes(datos)), end="", flush=True)

    print(f"Buscando {mac} ... (el celular debe estar desconectado del modulo)")
    try:
        dispositivo = await BleakScanner.find_device_by_address(mac, timeout=15)
    except BleakBluetoothNotAvailableError:
        return "sin_adaptador"
    except Exception as error:
        print(f"(Problema con el Bluetooth de la laptop: {error})")
        return "sin_adaptador"
    if dispositivo is None:
        return "no_encontrado"

    try:
        async with BleakClient(dispositivo) as client:
            car = elegir_caracteristica(client)
            if car is None:
                print("No encontre ninguna caracteristica escribible.")
                return "salir"
            robot = Robot(client, car)
            try:
                await client.start_notify(car, al_recibir)
            except Exception as error:  # el modulo podria no avisar respuestas
                print(f"(No pude escuchar al robot: {error}. Igual podes mandarle ordenes.)")
            print("Conectado. Escribi una orden y Enter. Probá: hola   |  ayuda  |  teclado  |  salir")

            loop = asyncio.get_running_loop()
            while client.is_connected:
                try:
                    texto = await loop.run_in_executor(None, input, "roli> ")
                except EOFError:
                    return "salir"
                texto = texto.strip()
                if texto.lower() in ("salir", "exit", "quit"):
                    return "salir"
                if texto.lower() == "teclado":
                    await modo_teclado(robot)
                    continue
                if texto:
                    try:
                        await robot.enviar(texto)
                    except Exception:
                        return "caida"
                    await asyncio.sleep(0.3)      # tiempo para que llegue la respuesta
            return "caida"
    except Exception:
        return "caida"


async def main(mac):
    """Conecta y, si la conexion se corta, vuelve a conectar sola (hasta 5 veces)."""
    intentos = 0
    while True:
        resultado = await sesion(mac)
        if resultado == "salir":
            break
        intentos += 1
        if intentos > 5:
            print("\nNo logre reconectar. Revisa a Roli (baterias, luz del modulo) y")
            print("el Bluetooth de la laptop, y volve a abrir la consola.")
            break
        if resultado == "caida":
            print("\n[Se corto la conexion con Roli. Reconectando...]")
        elif resultado == "sin_adaptador":
            print("\n[El Bluetooth de la laptop estaba apagado. Lo enciendo...]")
        else:
            print("\nNo lo encuentro. Revisa que el robot este encendido y que la luz")
            print("del modulo parpadee (si esta fija, hay otro aparato conectado). Reintento...")
        encender_bluetooth()
        await asyncio.sleep(2)
    print("Desconectado.")


if __name__ == "__main__":
    try:
        asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else MAC_POR_DEFECTO))
    except KeyboardInterrupt:
        print("\nInterrumpido.")
