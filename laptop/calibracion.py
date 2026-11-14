"""La lista de calibracion de Roli: sacarla de lo que contesta el robot y guardarla en un archivo de texto.

Es la parte de la consola que no necesita Bluetooth, para poder probarla sola (pruebas/calibracion_test.py).
El robot contesta a «calibrar exportar» con un bloque entre dos marcas; aca se lo reconoce, se lo guarda en
laptop/calibraciones/ y se lo puede llevar al chat para reajustar el programa del robot por USB.
"""
import asyncio
import os
import shutil
import subprocess
import time
import webbrowser

INICIO = "=== CALIBRACION DE ROLI"
FIN = "=== FIN ==="
CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibraciones")
SITIO = "https://maurogasta-crypto.github.io/roli/#calibraciones"
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
        self.ultimo = ""          # el texto de la ultima lista completa (para copiarla al sitio)

    def agregar(self, texto, carpeta=CARPETA, ahora=None):
        """Devuelve la ruta del archivo si con este trozo se completo una lista; si no, None."""
        self.buffer += texto
        self.buffer = self.buffer[-20000:]
        bloque, self.buffer = extraer(self.buffer)
        if bloque is None:
            return None
        ruta = guardar(bloque, carpeta, ahora)
        self.ultimo = bloque
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


# ───────────── Llevar la lista al sitio (14-nov-2026) ─────────────
# El sitio de Roli (index.html, detras de un login) tiene «Calibraciones»: se pega la lista y se guarda en la base.
# La consola no tiene ninguna clave del sitio: copia la lista al portapapeles y abre la pagina; pegar y guardar
# lo hace la persona, con su propia cuenta.
COPIADORES = (("wl-copy",), ("xclip", "-selection", "clipboard"), ("xsel", "--clipboard", "--input"))


def copiar_al_portapapeles(texto, hay=shutil.which, ejecutar=subprocess.run):
    """Copia `texto` con lo que tenga la laptop (Wayland o X11). Devuelve el nombre de la herramienta, o None."""
    for cmd in COPIADORES:
        if hay(cmd[0]):
            try:
                ejecutar(list(cmd), input=texto.encode("utf-8"), timeout=5, check=True)
                return cmd[0]
            except Exception:
                continue
    return None


def llevar_al_sitio(texto, abrir_pagina=True, copiar=copiar_al_portapapeles, abrir=webbrowser.open, decir=print):
    """Copia la lista y (si se pide) abre el sitio. Siempre dice que hacer a continuacion. Devuelve (copiado, abierto)."""
    if not texto.strip():
        decir("Todavia no hay ninguna lista: pedila con  calibrar exportar.")
        return False, False
    herramienta = copiar(texto)
    abierto = False
    if abrir_pagina:
        try:
            abierto = bool(abrir(SITIO))
        except Exception:
            abierto = False
    if herramienta:
        decir("Copie la lista. En el sitio: entra, abri «Calibraciones», pega (Ctrl+V) y toca «Guardar».")
    else:
        decir("No pude copiarla sola (falta wl-copy, xclip o xsel). Abri el archivo, copia todo y pegalo en el sitio:")
        decir(texto)
    if abrir_pagina and not abierto:
        decir("El sitio: " + SITIO)
    return bool(herramienta), abierto


# ───────────── La sesion de calibracion guiada ─────────────
INTRO = """
=== SESION DE CALIBRACION ===
Roli sobre el piso, con 2 metros libres adelante y alguien al lado para mirarlo.
Se prueba que vaya derecho, que arranque bien y (si tiene el nivel 6) que gire justo.
Al final se guarda en el robot y se lleva la lista al sitio. En cualquier pregunta:  x  para cortar.
"""
CERO_GOLPES = 4


async def sesion_guiada(robot, recibido, estado, pedir=None, esperar=None, copiar=copiar_al_portapapeles, abrir=webbrowser.open, decir=print):
    """Guia una calibracion completa. `robot.enviar(texto)`; `pedir(pregunta)` es una corrutina que lee una letra
    (por defecto input() en un hilo); `esperar(segundos)` tambien. Devuelve 'guardada', 'sin_guardar' o 'cortada'."""
    loop = asyncio.get_running_loop()
    if pedir is None:
        async def pedir(p):
            return await loop.run_in_executor(None, input, p)
    if esperar is None:
        esperar = asyncio.sleep

    async def preguntar(p, validas):
        while True:
            try:
                r = (await pedir(p)).strip().lower()
            except EOFError:
                return "x"
            if r[:1] in validas or r[:1] == "x":
                return r[:1]
            decir("  (elegi una de: " + ", ".join(validas) + ", o x para cortar)")

    async def mandar(orden, pausa=0.6):
        await robot.enviar(orden)
        if orden.split()[0] in ("calibrar", "desvio") and orden.split()[1:2] not in (["ver"], ["recto"], ["exportar"]):
            estado["cambio"] = True
        await esperar(pausa)

    decir(INTRO)
    await mandar("calibrar ver", 1.5)

    # 1 · derecho
    for _ in range(8):
        await mandar("calibrar recto", 3.5)
        r = await preguntar("¿Como fue?  [d] derecho  [i] se fue a la izquierda  [r] se fue a la derecha  [o] otra vez  > ", "dirso")
        if r == "x":
            return "cortada"
        if r == "d":
            break
        if r == "i":
            await mandar("desvio izq")
        elif r == "r":
            await mandar("desvio der")
        # «o»: se repite sin cambiar nada

    # 2 · arranque (la rueda loca)
    golpes = CERO_GOLPES
    for _ in range(4):
        r = await preguntar("¿Arranca con la rueda loca derecha?  [s] si  [m] hacer mas golpes  [p] menos golpes  > ", "smp")
        if r == "x":
            return "cortada"
        if r == "s":
            break
        golpes = min(10, golpes + 2) if r == "m" else max(0, golpes - 2)
        await mandar(f"calibrar ender {golpes}")
        await mandar("calibrar recto", 3.5)

    # 3 · giro (opcional: hace falta el nivel 6)
    r = await preguntar("¿Calibrar el giro de 90 grados? (hace falta el nivel 6)  [s] si  [n] no  > ", "sn")
    if r == "x":
        return "cortada"
    if r == "s":
        for _ in range(6):
            await mandar("girar der 90", 2.5)
            r = await preguntar("¿Giro justo?  [j] justo  [m] giro de menos de 90  [p] se paso  > ", "jmp")
            if r == "x":
                return "cortada"
            if r == "j":
                break
            await mandar("calibrar giro mas" if r == "m" else "calibrar giro menos")

    # 4 · guardar en el robot y llevar la lista al sitio
    r = await preguntar("¿Guardo esta calibracion en el robot (sobrevive al apagado)?  [s] si  [n] no  > ", "sn")
    if r in ("x", "n"):
        decir("Quedo sin guardar: si apagas a Roli, vuelve a lo de antes.")
        return "sin_guardar"
    await mandar("calibrar guardar", 1.0)
    antes = len(recibido.guardadas)
    await robot.enviar("calibrar exportar")
    for _ in range(40):
        await esperar(0.25)
        if len(recibido.guardadas) > antes:
            break
    else:
        decir("No llego la lista completa. Proba despues con:  calibrar exportar")
        return "guardada"
    estado["cambio"] = False
    llevar_al_sitio(recibido.ultimo, True, copiar, abrir, decir)
    return "guardada"
