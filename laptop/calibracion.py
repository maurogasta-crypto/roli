"""La lista de calibracion de Roli: sacarla de lo que contesta el robot y guardarla en un archivo de texto.

Es la parte de la consola que no necesita Bluetooth, para poder probarla sola (pruebas/calibracion_test.py).
El robot contesta a «calibrar exportar» con un bloque entre dos marcas; aca se lo reconoce, se lo guarda en
laptop/calibraciones/ y se lo puede llevar al chat para reajustar el programa del robot por USB.
"""
import asyncio
import os
import time

INICIO = "=== CALIBRACION DE ROLI"
FIN = "=== FIN ==="
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibraciones")
# las palabras que CAMBIAN la calibracion (ver, recto y exportar no)
CAMBIAN = ("velocidad", "kick", "ender", "zigzag", "giro", "cero", "guardar")


def extraer(buffer):
    """Busca un bloque completo en el texto recibido. Devuelve (bloque o None, lo que sobra despues)."""
    i = buffer.find(INICIO)
    if i < 0:
        return None, buffer[-200:]            # sin inicio: se descarta casi todo, que no crezca
    j = buffer.find(FIN, i)
    if j < 0:
        return None, buffer[i:]               # empezo y todavia no termino: se espera el resto
    fin = j + len(FIN)
    bloque = buffer[i:fin].replace("\r", "")
    return bloque.strip() + "\n", buffer[fin:]


def cambia_calibracion(linea):
    """¿Esta orden cambia la calibracion del robot? (para saber si al salir hay algo para guardar)."""
    p = linea.strip().lower().replace(",", ".").split()
    if not p:
        return False
    if p[0] == "desvio":
        return len(p) > 1 and p[1][:1] in ("i", "d")
    if p[0] == "calibrar":
        return len(p) > 1 and p[1] in CAMBIAN
    return False


def nombre_archivo(ahora=None):
    t = time.localtime(ahora if ahora is not None else time.time())
    return time.strftime("roli-calibracion-%Y%m%d-%H%M%S.txt", t)


def guardar(bloque, carpeta=CARPETA, ahora=None):
    """Escribe el bloque en un archivo nuevo y devuelve su ruta (nunca pisa uno anterior)."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre_archivo(ahora))
    base, ext = os.path.splitext(ruta)
    n = 1
    while os.path.exists(ruta):
        n += 1
        ruta = f"{base}-{n}{ext}"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(bloque)
    return ruta


def valores(bloque):
    """{'VEL_IZQ_INICIAL': 90, ...} a partir del bloque (las lineas «NOMBRE numero»)."""
    out = {}
    for linea in bloque.splitlines():
        partes = linea.split()
        if len(partes) == 2 and partes[0].isupper() and "_" in partes[0] and partes[1].lstrip("-").isdigit():
            out[partes[0]] = int(partes[1])
    return out


class Recibido:
    """Junta lo que contesta el robot y avisa cuando llega una lista completa."""

    def __init__(self):
        self.buffer = ""
        self.guardadas = []

    def agregar(self, texto, carpeta=CARPETA, ahora=None):
        """Devuelve la ruta del archivo si con este trozo se completo una lista; si no, None."""
        self.buffer += texto
        self.buffer = self.buffer[-20000:]
        bloque, self.buffer = extraer(self.buffer)
        if bloque is None:
            return None
        ruta = guardar(bloque, carpeta, ahora)
        self.guardadas.append(ruta)
        return ruta


PREGUNTA = "Cambiaste la calibracion de Roli. ¿Guardo la lista para llevarla al chat? [S/n] "


async def ofrecer(robot, recibido, estado, pedir=None, espera=0.25, intentos=40):
    """Al final de la sesion: si se cambio la calibracion, propone guardar la lista para llevarla al chat.
    `robot` tiene `await enviar(texto)`; `pedir(pregunta)` lee la respuesta (por defecto, input()).
    Devuelve 'nada' (no habia cambios), 'no' (la persona dijo que no), 'guardada' o 'incompleta'."""
    if not estado.get("cambio"):
        return "nada"
    try:
        if pedir is None:
            resp = await asyncio.get_running_loop().run_in_executor(None, input, PREGUNTA)
        else:
            resp = pedir(PREGUNTA)
    except EOFError:
        resp = "s"
    if resp.strip().lower().startswith("n"):
        print("Bien. (Si no lo guardaste en el robot con  calibrar guardar , se pierde al apagarlo.)")
        return "no"
    antes = len(recibido.guardadas)
    try:
        await robot.enviar("calibrar exportar")
    except Exception:
        print("No pude pedirle la lista a Roli: se corto la conexion.")
        return "incompleta"
    for _ in range(intentos):                            # el robot la manda de a trozos
        await asyncio.sleep(espera)
        if len(recibido.guardadas) > antes:
            estado["cambio"] = False
            return "guardada"
    print("\nNo llego la lista completa. Proba de nuevo con:  calibrar exportar")
    return "incompleta"
