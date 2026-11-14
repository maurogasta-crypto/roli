"""Banco de laptop/calibracion.py (sin Bluetooth ni nada instalado):  python3 pruebas/calibracion_test.py"""
import asyncio
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "laptop"))
import calibracion as C

LISTA = ("=== CALIBRACION DE ROLI (llevala al chat) ===\nprograma: NIVEL 6 MAPA 1 calibrar-v1\nVEL_IZQ_INICIAL 92\n"
         "VEL_DER_INICIAL 86\nKICK_VEL 160\nGIRO_MS_POR_GRADO 8\npara volver a poner estos valores:\n"
         "calibrar velocidad 92 86\ncalibrar guardar\n=== FIN ===\n")


class Banco(unittest.TestCase):
    def test_reconoce_la_lista_llegando_en_trozos_de_20_bytes(self):
        r, tmp = C.Recibido(), tempfile.mkdtemp()
        rutas = [x for x in (r.agregar(LISTA[i:i + 20], tmp) for i in range(0, len(LISTA), 20)) if x]
        self.assertEqual(len(rutas), 1)
        txt = open(rutas[0], encoding="utf-8").read()
        self.assertTrue(txt.startswith(C.INICIO) and txt.rstrip().endswith(C.FIN))
        self.assertEqual(C.valores(txt)["VEL_DER_INICIAL"], 86)

    def test_no_guarda_nada_si_la_lista_no_termino(self):
        r, tmp = C.Recibido(), tempfile.mkdtemp()
        self.assertIsNone(r.agregar(LISTA[:120], tmp))
        self.assertEqual(os.listdir(tmp), [])
        self.assertIsNotNone(r.agregar(LISTA[120:], tmp))

    def test_ignora_la_charla_de_antes_y_de_despues(self):
        r, tmp = C.Recibido(), tempfile.mkdtemp()
        ruta = r.agregar("ok guardar\nhola\n" + LISTA + "ok parar\n", tmp)
        txt = open(ruta, encoding="utf-8").read()
        self.assertNotIn("ok parar", txt)
        self.assertNotIn("ok guardar", txt)
        self.assertEqual(r.buffer.strip(), "ok parar")

    def test_dos_listas_seguidas_son_dos_archivos_y_nunca_se_pisan(self):
        r, tmp = C.Recibido(), tempfile.mkdtemp()
        r.agregar(LISTA, tmp, ahora=1000)
        r.agregar(LISTA, tmp, ahora=1000)
        self.assertEqual(len(os.listdir(tmp)), 2)

    def test_el_buffer_no_crece_sin_limite_con_charla_comun(self):
        r = C.Recibido()
        for _ in range(500):
            r.agregar("ok adelante\n" * 5, tempfile.mkdtemp())
        self.assertLess(len(r.buffer), 400)

    def test_que_ordenes_cambian_la_calibracion(self):
        for si in ("calibrar velocidad 90 84", "CALIBRAR kick 160", "calibrar guardar", "calibrar cero", "desvio izq", "desvio der 5", "calibrar giro mas", "calibrar ender 0"):
            self.assertTrue(C.cambia_calibracion(si), si)
        for no in ("calibrar ver", "calibrar exportar", "calibrar recto", "calibrar", "desvio", "desvio arriba", "adelante 2", "hola", ""):
            self.assertFalse(C.cambia_calibracion(no), no)

    def test_nombre_de_archivo_con_fecha_y_hora(self):
        self.assertRegex(C.nombre_archivo(0), r"^roli-calibracion-\d{8}-\d{6}\.txt$")

    def test_valores_lee_solo_las_lineas_de_numeros(self):
        v = C.valores(LISTA)
        self.assertEqual(v, {"VEL_IZQ_INICIAL": 92, "VEL_DER_INICIAL": 86, "KICK_VEL": 160, "GIRO_MS_POR_GRADO": 8})


class RobotFalso:
    """Un Roli de mentira: al pedirle la lista, la contesta de a trozos de 20 bytes, como el Bluetooth."""
    def __init__(self, recibido, tmp, contesta=True):
        self.recibido, self.tmp, self.contesta, self.pedidos = recibido, tmp, contesta, []

    async def enviar(self, texto):
        self.pedidos.append(texto)
        if self.contesta and texto == "calibrar exportar":
            for i in range(0, len(LISTA), 20):
                self.recibido.agregar(LISTA[i:i + 20], self.tmp)


class AlSalir(unittest.TestCase):
    def correr(self, cambio, resp, contesta=True):
        tmp = tempfile.mkdtemp()
        rec = C.Recibido()
        robot, estado = RobotFalso(rec, tmp, contesta), {"cambio": cambio}
        r = asyncio.run(C.ofrecer(robot, rec, estado, pedir=lambda _: resp, espera=0.001, intentos=5))
        return r, robot, rec, estado, tmp

    def test_sin_cambios_no_pregunta_ni_pide_nada(self):
        r, robot, *_ = self.correr(False, "s")
        self.assertEqual(r, "nada"); self.assertEqual(robot.pedidos, [])

    def test_con_cambios_y_un_si_pide_la_lista_y_la_guarda(self):
        r, robot, rec, estado, tmp = self.correr(True, "")        # Enter = si
        self.assertEqual(r, "guardada"); self.assertEqual(robot.pedidos, ["calibrar exportar"])
        self.assertEqual(len(os.listdir(tmp)), 1); self.assertFalse(estado["cambio"])

    def test_con_un_no_no_pide_nada(self):
        r, robot, *_ = self.correr(True, "no")
        self.assertEqual(r, "no"); self.assertEqual(robot.pedidos, [])

    def test_si_el_robot_no_contesta_lo_dice_y_no_inventa_un_archivo(self):
        r, robot, rec, estado, tmp = self.correr(True, "s", contesta=False)
        self.assertEqual(r, "incompleta"); self.assertEqual(os.listdir(tmp), []); self.assertTrue(estado["cambio"])



class FalsoRobot:
    """Anota lo que se le manda; si le piden la lista, «contesta» con ella."""
    def __init__(self, recibido, tmp):
        self.enviado, self.recibido, self.tmp = [], recibido, tmp

    async def enviar(self, texto):
        self.enviado.append(texto)
        if texto == "calibrar exportar":
            self.recibido.agregar(LISTA, self.tmp)


def correr_sesion(respuestas, copiar=None, abrir=None):
    rec, tmp, estado = C.Recibido(), tempfile.mkdtemp(), {"cambio": False}
    robot, res, dicho, copiado, abierto = FalsoRobot(rec, tmp), list(respuestas), [], [], []

    async def pedir(_):
        if not res:
            raise AssertionError("la sesion pregunto de mas")
        return res.pop(0)

    async def nada(_):
        return None

    resultado = asyncio.run(C.sesion_guiada(
        robot, rec, estado, pedir, nada,
        copiar or (lambda t: copiado.append(t) or "wl-copy"), abrir or (lambda u: abierto.append(u) or True), dicho.append))
    return resultado, robot.enviado, estado, copiado, abierto, dicho, res


class Sesion(unittest.TestCase):
    def test_sesion_completa_corrige_el_desvio_guarda_y_lleva_la_lista_al_sitio(self):
        # se fue a la izquierda, despues derecho; arranque bien; sin giro; guardar
        r, env, estado, copiado, abierto, _, sobra = correr_sesion(["i", "d", "s", "n", "s"])
        self.assertEqual(r, "guardada"); self.assertEqual(sobra, [])
        self.assertEqual(env, ["calibrar ver", "calibrar recto", "desvio izq", "calibrar recto", "calibrar guardar", "calibrar exportar"])
        self.assertFalse(estado["cambio"])
        self.assertEqual(len(copiado), 1); self.assertIn("VEL_DER_INICIAL 86", copiado[0]); self.assertEqual(abierto, [C.SITIO])

    def test_mas_golpes_menos_golpes_y_el_giro(self):
        r, env, *_ = correr_sesion(["d", "m", "m", "s", "s", "m", "j", "s"])
        self.assertEqual(r, "guardada")
        self.assertIn("calibrar ender 6", env); self.assertIn("calibrar ender 8", env)
        self.assertEqual(env[env.index("girar der 90") + 1], "calibrar giro mas")
        r, env, *_ = correr_sesion(["d", "p", "s", "n", "n"])
        self.assertIn("calibrar ender 2", env); self.assertNotIn("calibrar guardar", env)

    def test_cortar_con_x_no_guarda_nada_en_el_robot(self):
        r, env, estado, copiado, abierto, *_ = correr_sesion(["d", "x"])
        self.assertEqual(r, "cortada"); self.assertNotIn("calibrar guardar", env); self.assertEqual(copiado, []); self.assertEqual(abierto, [])

    def test_no_guardar_deja_el_aviso_y_los_cambios_marcados(self):
        r, env, estado, copiado, _, dicho, _ = correr_sesion(["r", "d", "s", "n", "n"])
        self.assertEqual(r, "sin_guardar"); self.assertTrue(estado["cambio"]); self.assertEqual(copiado, [])
        self.assertTrue(any("sin guardar" in x.lower() for x in dicho))

    def test_una_respuesta_rara_se_vuelve_a_preguntar(self):
        r, env, _, _, _, dicho, sobra = correr_sesion(["q", "d", "s", "n", "s"])
        self.assertEqual(r, "guardada"); self.assertEqual(sobra, []); self.assertTrue(any("elegi una de" in x for x in dicho))

    def test_ver_recto_y_exportar_no_cuentan_como_cambio(self):
        r, env, estado, *_ = correr_sesion(["d", "s", "n", "n"])
        self.assertTrue(r == "sin_guardar" and not estado["cambio"])


class LlevarAlSitio(unittest.TestCase):
    def test_copia_y_abre(self):
        dicho = []
        self.assertEqual(C.llevar_al_sitio(LISTA, True, lambda t: "xclip", lambda u: True, dicho.append), (True, True))
        self.assertTrue(any("Calibraciones" in x for x in dicho))

    def test_sin_herramienta_de_copiado_muestra_la_lista_para_copiarla_a_mano(self):
        dicho = []
        self.assertEqual(C.llevar_al_sitio(LISTA, False, lambda t: None, lambda u: True, dicho.append), (False, False))
        self.assertIn(LISTA, dicho)

    def test_sin_lista_no_hace_nada(self):
        dicho = []
        self.assertEqual(C.llevar_al_sitio("  ", True, lambda t: self.fail(), lambda u: self.fail(), dicho.append), (False, False))

    def test_elige_la_primera_herramienta_que_hay(self):
        llamadas = []
        hay = lambda n: n == "xclip"
        ej = lambda cmd, **kw: llamadas.append((cmd, kw["input"]))
        self.assertEqual(C.copiar_al_portapapeles("hola", hay, ej), "xclip"); self.assertEqual(llamadas[0][1], b"hola")
        self.assertIsNone(C.copiar_al_portapapeles("hola", lambda n: False, ej))


if __name__ == "__main__":
    unittest.main(verbosity=1)
