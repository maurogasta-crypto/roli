#!/usr/bin/env python3
"""Genera la guia PDF 'Mi Robot Explorador'."""
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle,
                                KeepTogether, CondPageBreak)

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-I", FD + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("Sans-BI", FD + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B", FD + "DejaVuSansMono-Bold.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono", boldItalic="Mono-B")

TEAL = colors.HexColor("#0E5E6F")
TEAL_D = colors.HexColor("#0A4351")
ORANGE = colors.HexColor("#E8761A")
SAND = colors.HexColor("#FFF3DE")
MINT = colors.HexColor("#E2F3EF")
GRAY = colors.HexColor("#EEF1F3")
INK = colors.HexColor("#1F2A30")
RED = colors.HexColor("#B3261E")
WHITE = colors.white

W, H = A4
M = 1.8 * cm
CW = W - 2 * M

body = ParagraphStyle("body", fontName="Sans", fontSize=9.6, leading=14, textColor=INK, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=body, fontSize=8.4, leading=12)
cell = ParagraphStyle("cell", parent=body, fontSize=9, leading=12.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Sans-B")
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=2, spaceAfter=2)
h1 = ParagraphStyle("h1", parent=body, fontName="Sans-B", fontSize=19, leading=23, textColor=TEAL_D, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=body, fontName="Sans-B", fontSize=12, leading=15, textColor=TEAL, spaceBefore=10, spaceAfter=4)
label = ParagraphStyle("label", parent=body, fontName="Sans-B", fontSize=9, leading=12, textColor=ORANGE)
code = ParagraphStyle("code", fontName="Mono", fontSize=9, leading=12.5, textColor=INK)
white_b = ParagraphStyle("white_b", parent=body, fontName="Sans-B", fontSize=15, leading=19, textColor=WHITE)
white = ParagraphStyle("white", parent=body, textColor=WHITE, fontSize=9.5, leading=13)


def P(t, s=body):
    return Paragraph(t, s)


def bullets(items, style=bullet):
    return [Paragraph(t, style, bulletText="•") for t in items]


def numbered(items):
    return [Paragraph(t, bullet, bulletText=f"{i}.") for i, t in enumerate(items, 1)]


def box(flow, bg=GRAY, pad=8, border=None):
    t = Table([[flow]], colWidths=[CW])
    st = [("BACKGROUND", (0, 0), (-1, -1), bg),
          ("LEFTPADDING", (0, 0), (-1, -1), pad + 2), ("RIGHTPADDING", (0, 0), (-1, -1), pad + 2),
          ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad)]
    if border:
        st.append(("BOX", (0, 0), (-1, -1), 0.8, border))
    t.setStyle(TableStyle(st))
    return t


def codebox(lines, title=None):
    inner = []
    if title:
        inner.append(Paragraph(title, label))
        inner.append(Spacer(1, 3))
    inner.append(Preformatted("\n".join(lines), code))
    return box(inner, bg=colors.HexColor("#E9EEF1"), pad=7)


def callout(titulo, texto, bg=SAND, color=ORANGE):
    t = Table([[[Paragraph(titulo, ParagraphStyle("ct", parent=label, textColor=color)), Spacer(1, 2),
                 Paragraph(texto, cell)]]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def table(rows, widths, header=True, zebra=True, fs=None):
    data = []
    for i, r in enumerate(rows):
        st = cellb if (header and i == 0) else cell
        data.append([Paragraph(str(c), ParagraphStyle("c", parent=st, textColor=WHITE if (header and i == 0) else INK)) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD3D8"))]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), TEAL))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F6F8F9")))
    t.setStyle(TableStyle(st))
    return t


def etapa(num, titulo, nivel, idea, pasos, probar, m7, m10, deberia, falla, extra=None):
    """Una pagina (o poco mas) por etapa."""
    f = []
    head = Table([[Paragraph(f"ETAPA {num}", ParagraphStyle("e", parent=white, fontName="Sans-B", fontSize=9.5)),
                   Paragraph(f"Programa del Arduino: {nivel}", ParagraphStyle("n", parent=white, fontName="Sans-B", fontSize=9, alignment=2))],
                  [Paragraph(titulo, white_b), ""]], colWidths=[CW * 0.55, CW * 0.45])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL), ("SPAN", (0, 1), (1, 1)),
                              ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                              ("TOPPADDING", (0, 0), (-1, 0), 9), ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
                              ("TOPPADDING", (0, 1), (-1, 1), 2), ("BOTTOMPADDING", (0, 1), (-1, 1), 10)]))
    f.append(head)
    f.append(Spacer(1, 8))
    f.append(callout("LA IDEA DE PROGRAMACIÓN", idea, bg=MINT, color=TEAL))
    f.append(P("Pasos", h2))
    f += numbered(pasos)
    if probar:
        f.append(Spacer(1, 4))
        f.append(codebox(probar, "ESCRIBÍ ESTAS ÓRDENES"))
    if extra:
        f.append(Spacer(1, 6))
        f += extra
    f.append(P("Misiones", h2))
    mis = Table([[Paragraph("Para el de 7 años", ParagraphStyle("m7", parent=cellb, textColor=WHITE)),
                  Paragraph("Para el de 10 años", ParagraphStyle("m10", parent=cellb, textColor=WHITE))],
                 [[Paragraph(t, bullet, bulletText="•") for t in m7],
                  [Paragraph(t, bullet, bulletText="•") for t in m10]]],
                colWidths=[CW / 2, CW / 2])
    mis.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), ORANGE), ("BACKGROUND", (1, 0), (1, 0), TEAL),
                             ("BACKGROUND", (0, 1), (0, 1), SAND), ("BACKGROUND", (1, 1), (1, 1), MINT),
                             ("VALIGN", (0, 0), (-1, -1), "TOP"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    f.append(mis)
    f.append(Spacer(1, 8))
    ok_t = Table([[[P("✓ DEBERÍA PASAR", ParagraphStyle("o", parent=label, textColor=TEAL)), Spacer(1, 2)] + bullets(deberia, ParagraphStyle("b2", parent=bullet, fontSize=9, leading=12.5)),
                   [P("SI NO FUNCIONA", ParagraphStyle("o2", parent=label, textColor=RED)), Spacer(1, 2)] + bullets(falla, ParagraphStyle("b3", parent=bullet, fontSize=9, leading=12.5))]],
                 colWidths=[CW / 2, CW / 2])
    ok_t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.8, TEAL), ("BOX", (1, 0), (1, 0), 0.8, RED),
                              ("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                              ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    f.append(ok_t)
    f.append(PageBreak())
    return f


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 8)
    canvas.setFillColor(colors.HexColor("#6B7A83"))
    canvas.drawString(M, 1.1 * cm, "Mi Robot Explorador · guía de programación paso a paso")
    canvas.drawRightString(W - M, 1.1 * cm, f"{doc.page}")
    canvas.restoreState()


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=1.6 * cm, bottomMargin=1.7 * cm,
                          title="Mi Robot Explorador - guía de programación paso a paso",
                          author="Mauro", subject="Robot Arduino para chicos de 7 y 10 años")
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 1.7 * cm, CW, H - 3.3 * cm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=pie)])
    s = []

    # ---------------- PORTADA ----------------
    cover = Table([[[Paragraph("Mi Robot<br/>Explorador", ParagraphStyle("t", parent=white_b, fontSize=34, leading=39)),
                     Spacer(1, 6),
                     Paragraph("Guía para aprender a programar paso a paso", ParagraphStyle("st", parent=white, fontSize=13, leading=17)),
                     Spacer(1, 10),
                     Paragraph("Un robot con Arduino que se maneja con palabras: desde el cable USB hasta el control remoto desde la laptop, "
                               "con un sensor que lo hace frenar y decidir solo. Pensada para hacer en familia, con chicos de 7 y 10 años y un adulto al lado.", white)]]],
                  colWidths=[CW])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL), ("LEFTPADDING", (0, 0), (-1, -1), 18),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 18), ("TOPPADDING", (0, 0), (-1, -1), 22), ("BOTTOMPADDING", (0, 0), (-1, -1), 22)]))
    s += [cover, Spacer(1, 14), P("El camino: 9 etapas", h1)]
    camino = [["Etapa", "Qué hacen", "Qué aprenden", "Programa"],
              ["0 · Hola, placa", "Cable USB, compilar y subir un programa", "Qué es programar", "NIVEL 1"],
              ["1 · Hablar con el robot", "Mandarle palabras desde el teclado", "Comandos y errores", "NIVEL 1"],
              ["2 · Las ruedas", "Hacerlo mover (con las ruedas en el aire)", "Causa y efecto, parar", "NIVEL 2"],
              ["3 · Sin cable", "Manejarlo por Bluetooth desde la laptop", "Comunicación inalámbrica", "NIVEL 2"],
              ["4 · Tiempo y velocidad", "“adelante 2”, “velocidad 150”, medir y calibrar", "Parámetros y variables", "NIVEL 3"],
              ["5 · Mis programas", "Grabar un recorrido y repetirlo", "Secuencias y repeticiones", "NIVEL 4"],
              ["6 · Los ojos", "Medir distancias y frenar solo", "Sensores y umbrales", "NIVEL 5"],
              ["7 · Decidir solo", "Reglas “cuando obstáculo… entonces…”", "Condiciones y eventos", "NIVEL 6"],
              ["8 · Control remoto", "Teclado + respuestas automáticas del robot", "Control compartido", "NIVEL 6"]]
    s.append(table(camino, [CW * 0.24, CW * 0.38, CW * 0.24, CW * 0.14]))
    s.append(Spacer(1, 10))
    s.append(callout("CÓMO USAR ESTA GUÍA",
                     "Una etapa por sesión (20 a 40 minutos). Cada etapa tiene la idea de programación, los pasos, "
                     "órdenes para probar y misiones separadas para cada edad. No hace falta terminar todas las misiones: "
                     "cuando un chico se enganche con una, dejalo explorar y repetirla."))
    s.append(PageBreak())

    # ---------------- ANTES DE EMPEZAR ----------------
    s.append(P("Antes de empezar (para el adulto)", h1))
    s.append(P("Reglas de oro de seguridad", h2))
    s += bullets([
        "<b>Primero con las ruedas en el aire.</b> Las pruebas con cable USB se hacen con el robot apoyado sobre una caja o un libro, sin tocar el piso.",
        "<b>Un adulto siempre cerca del interruptor de las baterías.</b> Es el botón de pánico de verdad.",
        "<b>Baterías de litio 18650:</b> cargarlas con un adulto, no cortocircuitar, no perforar, y sacarlas si se calientan o se hinchan.",
        "El programa frena solo a los <b>4 segundos</b> si no le das un tiempo (“parada de seguridad”), y la orden <b>parar</b> siempre manda.",
        "El modo <b>explorar</b> dura como máximo 30 segundos y se corta con <b>parar</b>.",
    ])
    s.append(P("Qué lleva el robot", h2))
    s.append(table([
        ["Pieza", "Para qué sirve"],
        ["Arduino UNO", "El cerebro: recibe las órdenes y activa motores, sensor y servo."],
        ["Módulo Bluetooth (dice “HC-06”)", "Recibe las órdenes por el aire. <b>Es un módulo BLE</b> (servicio FFE0, tipo HM-10): no se empareja ni se usa con rfcomm; se maneja con el script consola_robot.py."],
        ["Puente H L298N", "Da fuerza a los motores y cambia el sentido de giro."],
        ["Chasis 2WD", "Dos motorreductores amarillos y una rueda loca."],
        ["2 baterías 18650 en serie", "Unos 7,4 a 8,4 V para el L298N."],
        ["Sensor ultrasónico HC-SR04", "Los “ojos”: mide la distancia con un eco de sonido."],
        ["Servo SG90", "El “cuello”: gira el sensor a izquierda y derecha."],
    ], [CW * 0.3, CW * 0.7]))
    s.append(P("Energía (igual en los dos cableados)", h2))
    s += bullets([
        "Baterías <b>+</b> → borne <b>12V</b> del L298N · baterías <b>−</b> → borne <b>GND</b> del L298N.",
        "<b>Masa común obligatoria:</b> un cable del GND del L298N a un GND del Arduino.",
        "El borne <b>5V</b> del L298N alimenta al Arduino, al módulo Bluetooth, al sensor y al servo.",
    ])
    s.append(Spacer(1, 4))
    s.append(callout("OJO: ESE 5V VA AL PIN “5V” DEL ARDUINO, NO AL “VIN”",
                     "El pin VIN espera entre 7 y 12 V porque tiene su propio regulador. Si le llegan solo 5 V, el Arduino queda con menos de 5 V "
                     "y se reinicia o se porta raro. Además, el regulador del L298N deja de sostener los 5 V cuando las baterías bajan de unos 7 V: "
                     "si el robot se reinicia solo, cargá las baterías primero.", bg=colors.HexColor("#FDE7E4"), color=RED))
    s.append(PageBreak())

    # ---------------- CABLEADO ----------------
    s.append(P("¿Cuál es tu cableado? Elegí el mapa de pines", h1))
    s.append(P("Las pruebas anteriores del robot funcionaron con los motores en los pines 5, 6, 9 y 10, mientras que la lista de conexiones "
               "indica otros pines (ENA, ENB, 4 y 2). El programa soporta <b>los dos cableados</b>: se elige cambiando <b>un número</b>."))
    s.append(Spacer(1, 6))
    s.append(table([
        ["Conexión", "MAPA 1", "MAPA 2"],
        ["Módulo BLE: TXD / RXD", "pin 11 / pin 12", "pin 11 / pin 12"],
        ["Motor izquierdo", "IN1 = 5, IN2 = 6<br/>(puentes ENA y ENB puestos)", "ENA = 10 (velocidad)<br/>IN1 = 9, IN2 = 8"],
        ["Motor derecho", "IN3 = 9, IN4 = 10", "ENB = 5 (velocidad)<br/>IN3 = 7, IN4 = 6"],
        ["Sensor HC-SR04: Trig / Echo", "pin 7 / pin 8", "pin 4 / pin 2"],
        ["Servo SG90 (señal)", "pin 3", "pin 3"],
    ], [CW * 0.32, CW * 0.34, CW * 0.34]))
    s.append(Spacer(1, 8))
    s.append(P("Cómo saber cuál tenés", h2))
    s += numbered([
        "Con el robot apagado, mirá el L298N. Si en <b>ENA y ENB</b> hay un puentecito (jumper) puesto y no sale ningún cable de ahí, es el <b>MAPA 1</b>.",
        "Si en ENA y ENB hay un cable que va al Arduino (a los pines 10 y 5), es el <b>MAPA 2</b>.",
        "Si no estás seguro, probá con el MAPA 1: es el que funcionó con las pruebas anteriores. La Etapa 2 incluye una prueba de cableado que lo confirma.",
    ])
    s.append(Spacer(1, 6))
    s.append(codebox(["#define MAPA_PINES 1     // cambiá a 2 si tu cableado es el del mapa 2",
                      "const bool INVERTIR_IZQ = false;   // true si la rueda izquierda gira al revés",
                      "const bool INVERTIR_DER = false;   // true si la rueda derecha gira al revés"],
                     "AL PRINCIPIO DEL PROGRAMA robot_didactico.ino"))
    s.append(Spacer(1, 6))
    s.append(callout("BLUETOOTH: DIVISOR EN EL PIN 12",
                     "El módulo Bluetooth trabaja con 3,3 V en su entrada RXD, pero el Arduino manda 5 V por el pin 12. Lo recomendable es un divisor "
                     "con dos resistencias (por ejemplo 1 kΩ del pin 12 al RXD y 2 kΩ del RXD a GND). Si ya anda sin divisor, funciona, pero con algo de riesgo para el módulo."))
    s.append(Spacer(1, 6))
    s.append(callout("POR QUÉ NO SE USA LA LIBRERÍA SERVO",
                     "En un Arduino UNO la librería Servo desactiva el control de velocidad (PWM) de los pines 9 y 10. Por eso este programa "
                     "mueve el servo con pulsos propios y no usa esa librería: así funciona con cualquiera de los dos mapas."))
    s.append(PageBreak())

    # ---------------- PREPARAR LA LAPTOP ----------------
    s.append(P("Preparar la laptop (una sola vez)", h1))
    s.append(P("Cargar un nivel en el Arduino", h2))
    s += numbered([
        "Conectá el Arduino a la laptop con el cable USB.",
        "Abrí <b>robot_didactico.ino</b> en el Arduino IDE (si pregunta si crea una carpeta, aceptá).",
        "En <b>Herramientas → Placa</b> elegí <b>Arduino Uno</b> y en <b>Herramientas → Puerto</b> el puerto USB (en tu laptop apareció <b>/dev/ttyUSB0</b>).",
        "Cambiá el número de la línea <b>#define NIVEL</b> por el nivel de la etapa (y revisá <b>MAPA_PINES</b>).",
        "Apretá el botón <b>✓ Verificar</b> (compila) y después <b>→ Subir</b>. Al terminar dice “Subido”.",
        "Abrí el <b>Monitor Serie</b> (la lupa), poné <b>9600 baudios</b> y <b>Nueva línea</b> abajo a la derecha. Tiene que aparecer “Robot listo. NIVEL …”.",
    ])
    s.append(Spacer(1, 4))
    s.append(callout("UN DETALLE QUE CONFUNDE", "Cada vez que se abre el Monitor Serie el Arduino se reinicia solo. Es normal, y por eso un programa pierde lo que tenía en memoria RAM."))
    s.append(P("La consola Bluetooth de la laptop", h2))
    s += numbered([
        "Poné <b>consola_robot.py</b> en una carpeta (por ejemplo <b>~/Robot</b>). El entorno de Python con bleak ya está instalado en <b>~/ble-env</b>.",
        "Encendé el robot y <b>desconectá el celular</b> del módulo (acepta una sola conexión a la vez).",
        "En una terminal: <font face='Mono'>cd ~/Robot</font> y después <font face='Mono'>~/ble-env/bin/python consola_robot.py</font>",
        "Cuando diga “Conectado”, aparece el prompt <b>robot&gt;</b>. Escribí una orden y Enter: lo que contesta el robot aparece en pantalla.",
        "Para salir, escribí <b>salir</b>.",
    ])
    s.append(Spacer(1, 4))
    s.append(callout("NO USES rfcomm, screen NI “EMPAREJAR” CON ESTE MÓDULO",
                     "Como es BLE, no existe el puerto /dev/rfcomm0. Los intentos anteriores fallaban por eso. Si el Bluetooth de la laptop se traba "
                     "(la antena se enciende y se apaga en bucle), reiniciá la laptop: es lo que lo arregla."))
    s.append(P("Las órdenes se escriben así", h2))
    s += bullets([
        "<b>Sin tildes</b> (atras, no atrás) y da igual mayúsculas o minúsculas.",
        "Los números pueden llevar coma o punto: <font face='Mono'>adelante 0,5</font>.",
        "El robot siempre contesta por el mismo camino por el que le hablaste: si escribís por USB contesta en el Monitor Serie; por Bluetooth, en la consola.",
        "Si no conoce una palabra dice “No se esa palabra (todavía)”. Es <b>a propósito</b>: las palabras nuevas se desbloquean subiendo de nivel.",
    ])
    s.append(PageBreak())

    # ---------------- ETAPAS ----------------
    s += etapa(0, "Hola, placa", "NIVEL 1",
               "<b>Programar es escribir instrucciones y cargarlas en una máquina.</b> Primero se escribe (código), después se <b>compila</b> "
               "(la compu lo traduce) y por último se <b>sube</b> al Arduino por el cable.",
               ["Seguí el recuadro “Cargar un nivel en el Arduino” con <b>NIVEL 1</b>.",
                "Mirá el led pequeño de la placa y el Monitor Serie: tiene que decir “Robot listo. NIVEL 1”.",
                "Buscá en el código la línea que dice <font face='Mono'>Serial.println(F(\"Escribe: hola\"));</font> y cambiá el texto por otro (por ejemplo, el nombre del robot).",
                "Volvé a compilar y subir. Reabrí el Monitor Serie y leé el mensaje nuevo."],
               None,
               ["Elegir entre todos el nombre del robot y verlo aparecer en la pantalla.",
                "Contar cuántas veces se prende el led de la placa al reiniciar."],
               ["Cambiar el mensaje y explicar con palabras los 3 pasos: escribir, compilar, subir.",
                "Provocar un error a propósito (borrar un punto y coma) y leer qué dice el IDE abajo."],
               ["El IDE muestra “Compilación terminada” y después “Subido”.", "El Monitor Serie muestra tu mensaje nuevo."],
               ["El puerto no aparece: probá otro cable USB (algunos solo cargan, no pasan datos).",
                "Error al subir: revisá que la placa elegida sea Arduino Uno y el puerto el correcto."])

    s += etapa(1, "Hablar con el robot", "NIVEL 1",
               "<b>Un comando es una palabra que el robot entiende</b>, a veces con un dato al lado (un <b>argumento</b>, como el 5 de “parpadear 5”). "
               "Si la palabra no es exacta, el robot no adivina: eso es un <b>error</b>, y encontrarlo es parte de programar.",
               ["Con el cable USB puesto y el Monitor Serie abierto (9600 baudios, Nueva línea), escribí una orden y Enter.",
                "Probá cada orden de la lista. Mirá qué contesta el robot.",
                "Escribí una palabra inventada y leé la respuesta. ¿Qué te está diciendo?",
                "Escribí <b>ayuda</b> para ver todas las palabras que conoce en este nivel."],
               ["hola", "di hola, soy un robot", "led 1", "led 0", "parpadear 5", "ayuda", "bailar"],
               ["Encender y apagar el led de la placa con <b>led 1</b> y <b>led 0</b>.",
                "Hacer que el robot “diga” su nombre y una frase graciosa con <b>di …</b>."],
               ["Descubrir qué pasa con mayúsculas, espacios de más y números con coma.",
                "Explicar con sus palabras la diferencia entre el comando (<b>parpadear</b>) y el argumento (<b>5</b>)."],
               ["Cada orden contesta “ok …” o un texto.", "Con una palabra inventada dice “No se esa palabra (todavía)”."],
               ["No contesta nada: revisá que abajo del Monitor diga <b>Nueva línea</b> y 9600 baudios.",
                "Salen símbolos raros: la velocidad del Monitor no es 9600."])

    s += etapa(2, "Las ruedas", "NIVEL 2",
               "<b>Causa y efecto:</b> una orden produce una acción en el mundo real. Y la orden más importante de un robot es la que lo <b>detiene</b>.",
               ["Cambiá <b>#define NIVEL</b> a <b>2</b>, revisá <b>MAPA_PINES</b> y subí el programa (recuadro “Cargar un nivel”).",
                "Apoyá el robot <b>sobre una caja con las ruedas en el aire</b>, con el cable USB conectado y las baterías <b>encendidas</b>.",
                "Mandá <b>adelante</b> y mirá las dos ruedas. Después <b>parar</b>.",
                "<b>Prueba de cableado:</b> las dos ruedas tienen que girar hacia adelante. Si no se mueve ninguna, probá <b>MAPA_PINES 2</b>. Si una gira al revés, poné <b>true</b> en INVERTIR_IZQ o INVERTIR_DER.",
                "Probá <b>atras</b>, <b>izquierda</b> y <b>derecha</b>. Después las abreviaturas: <b>d a i e r</b>.",
                "Mandá <b>adelante</b> y no hagas nada: a los 4 segundos el robot se detiene solo."],
               ["adelante", "parar", "atras", "izquierda", "derecha", "d", "r"],
               ["Jugar al “semáforo”: <b>d</b> es verde, <b>r</b> es rojo. El adulto dice el color y el chico escribe la letra.",
                "Adivinar hacia dónde va cada rueda antes de escribir la orden."],
               ["Encontrar qué dos órdenes hacen que el robot gire <i>sin avanzar</i> (cada rueda para un lado).",
                "Cambiar <b>SEGURIDAD_MS</b> de 4000 a 2000 en el código, subir de nuevo y comprobar qué cambió."],
               ["Adelante: ambas ruedas giran hacia el mismo lado, hacia adelante.", "“parada de seguridad” a los 4 segundos sin orden."],
               ["No se mueve nada: baterías apagadas o descargadas, o MAPA_PINES equivocado.",
                "Gira muy despacio o vibra: la velocidad inicial es 150; subila en la Etapa 4.",
                "Se reinicia al arrancar: baterías flojas (ver el recuadro de energía)."])

    s += etapa(3, "Sin cable", "NIVEL 2 (el mismo de la etapa anterior)",
               "<b>Comunicación inalámbrica:</b> las órdenes viajan por el aire. El robot contesta “ok”, así sabemos que recibió el mensaje. "
               "Eso es un <b>protocolo</b>: un acuerdo sobre cómo hablar.",
               ["Desconectá el cable USB. Con el robot <b>apagado</b>, ponelo en el piso en un espacio despejado.",
                "Encendelo (la luz del módulo parpadea) y verificá que el celular no esté conectado al módulo.",
                "Abrí la consola (ver “La consola Bluetooth de la laptop”). Escribí <b>hola</b>: <b>si el robot contesta, todo el camino por Bluetooth funciona</b>.",
                "Mandá <b>adelante</b>, <b>izquierda</b>, <b>parar</b>… y manejalo por el living.",
                "Probá apagar la consola con Ctrl+C mientras avanza: ¿qué pasa a los 4 segundos? (la seguridad)."],
               ["hola", "adelante", "izquierda", "adelante", "parar"],
               ["Llevar el robot de la puerta hasta una silla dando una orden por vez.",
                "Jugar al “robot ciego”: uno da las órdenes sin mirar la pantalla y otro dice si llegó."],
               ["Armar un circuito con cinta en el piso y recorrerlo con la menor cantidad de órdenes.",
                "Cronometrar cuánto tarda desde que escribe la orden hasta que el robot se mueve (la <b>demora</b>)."],
               ["Aparece “Conectado” y el robot contesta “Hola! Soy tu robot”.", "Cada orden recibe su “ok”."],
               ["“No lo encuentro”: luz del módulo fija = otro aparato conectado (el celular). Apagá y prendé el robot.",
                "Conecta pero el robot no contesta: el programa del Arduino no es de esta guía (subilo de nuevo) o el pin 11/12 del módulo está cruzado.",
                "Bluetooth de la laptop trabado: reiniciar la laptop."])

    s += etapa(4, "Tiempo y velocidad", "NIVEL 3",
               "<b>Parámetros y variables:</b> una misma orden cambia según el número que lleva. <b>velocidad</b> es una <b>variable</b>: un valor guardado que se puede cambiar. "
               "Y para que el robot vaya derecho hay que <b>medir y calibrar</b>.",
               ["Cambiá <b>#define NIVEL</b> a <b>3</b> y subí el programa. Después manejalo por Bluetooth.",
                "Probá <b>adelante 2</b>: avanza 2 segundos y se detiene solo. También sirven los decimales: <b>adelante 0,5</b>.",
                "Mirá si se desvía. Si tira para la izquierda, <b>bajale</b> velocidad a la rueda izquierda o <b>subile</b> a la derecha. Probá valores hasta que vaya derecho.",
                "Anotá en la hoja de calibración (final de la guía) cuánto avanza en 1, 2 y 3 segundos.",
                "Medí el tiempo que necesita para un <b>cuarto de vuelta</b> (<b>derecha 0,6</b> es un buen punto de partida)."],
               ["adelante 2", "adelante 0,5", "velocidad 200", "velocidad izq 140", "velocidad der 160", "derecha 0,6"],
               ["Comparar: ¿qué llega más lejos, <b>adelante 1</b> o <b>adelante 3</b>?",
                "Carrera lenta contra rápida: <b>velocidad 90</b> contra <b>velocidad 220</b>."],
               ["Llenar la tabla de tiempo contra distancia con una cinta métrica y ver si el doble de tiempo es el doble de distancia.",
                "Encontrar el <b>valor exacto</b> que da un giro de 90 grados y comprobarlo con una escuadra de cartón."],
               ["Avanza el tiempo pedido y se detiene solo.", "Después de calibrar, avanza 2 metros sin desviarse más de una mano."],
               ["No arranca con velocidad baja: debajo de unos 70 los motores no tienen fuerza (el programa no deja bajar de 60).",
                "Sigue desviándose: probá diferencias más grandes entre izq y der, de a 10."])

    s += etapa(5, "Mis programas", "NIVEL 4",
               "<b>Secuencia y repetición:</b> un programa es una lista de pasos que se ejecutan en orden, y se puede <b>repetir</b> (un <b>bucle</b>). "
               "Si algo sale mal, se <b>depura</b>: se mira paso a paso dónde está el error.",
               ["Cambiá <b>#define NIVEL</b> a <b>4</b> y subí el programa.",
                "Escribí <b>programa</b>. A partir de ahí lo que escribas no se ejecuta: se <b>guarda</b> como un paso. Terminá con <b>fin</b>.",
                "Mirá lo guardado con <b>listar</b> y corrélo con <b>ejecutar</b>. Con un número se repite: <b>ejecutar 4</b>.",
                "Dentro de un programa, una orden sin número dura 1 segundo. <b>esperar</b> hace una pausa.",
                "Con <b>borrar</b> se vacía la memoria. Entran hasta <b>12 pasos</b>: ¡los robots tienen poca memoria!"],
               ["programa", "adelante 1", "derecha 0,6", "fin", "listar", "ejecutar 4"],
               ["<b>El baile:</b> <i>derecha 0,5, izquierda 0,5, esperar 1</i> y repetir.",
                "Programar un recorrido hasta la heladera con 3 o 4 pasos."],
               ["<b>El cuadrado:</b> el programa de 2 pasos de arriba, repetido 4 veces. Ajustar el giro hasta que cierre.",
                "Dibujar un recorrido en papel, pasarlo a pasos, ejecutarlo y corregir lo que falle (depurar)."],
               ["Cada paso aparece como “-> adelante 1” mientras corre.", "Al final dice “programa terminado”."],
               ["“Memoria llena”: son 12 pasos como máximo, escribí <b>fin</b>.",
                "No hace caso a una orden: se escribió con tilde o con una palabra del nivel siguiente.",
                "Un movimiento manual (adelante…) o <b>parar</b> cancela el programa."])

    s += etapa(6, "Los ojos", "NIVEL 5",
               "<b>Sensores y umbrales:</b> el robot mide el mundo (la distancia) y compara con un número límite, el <b>umbral</b>. "
               "Si la distancia es menor que el umbral, frena. Es la base de la seguridad de las máquinas.",
               ["Apagá el robot. Conectá el sensor y el servo según tu mapa de pines (ver la tabla de cableado): VCC a 5V, GND a GND, Trig, Echo y la señal del servo.",
                "Cambiá <b>#define NIVEL</b> a <b>5</b> y subí el programa. Al encender, el servo mira al frente.",
                "Acercá una mano al sensor y escribí <b>distancia</b> varias veces.",
                "Probá <b>escanear</b> (mira a la izquierda, al frente y a la derecha) y <b>mirar izq</b>. Si mira al revés, intercambiá SERVO_IZQ y SERVO_DER en el código.",
                "Ponele una pared de cartón adelante y mandá <b>adelante</b>. El robot no arranca si hay algo a menos de 20 cm; si ya viene avanzando, frena.",
                "Cambiá el umbral: <b>proteccion 10</b>, <b>proteccion 40</b>, <b>proteccion 0</b> (apagada)."],
               ["distancia", "escanear", "mirar izq", "mirar frente", "proteccion 30", "adelante"],
               ["<b>Frío y caliente:</b> acercar y alejar la mano y adivinar si el número sube o baja.",
                "Ver cómo el robot “se asusta” de la pared y frena antes de chocar."],
               ["Medir una distancia conocida con la cinta (20, 50, 100 cm) y comparar con lo que dice el sensor. ¿Cuánto se equivoca?",
                "Encontrar el mejor umbral para que frene sin chocar a velocidad 150 y a velocidad 220 (¡a más velocidad hace falta más margen!)."],
               ["distancia da números razonables (en cm).", "Dice “OBSTACULO a … cm” y los motores se detienen."],
               ["Siempre da 0 o “no veo nada”: Trig y Echo cruzados, o el cableado no coincide con el mapa elegido.",
                "El Arduino se reinicia cuando se mueve el servo: la alimentación de 5 V no alcanza; probá con baterías cargadas o un capacitor de 470 µF entre 5V y GND.",
                "El servo no se mueve: revisá el pin 3 y que el cable rojo vaya a 5V."])

    s += etapa(7, "Decidir solo", "NIVEL 6",
               "<b>Condiciones y eventos:</b> “<i>cuando</i> pasa esto, <i>entonces</i> hago aquello”. El robot ya no solo obedece: <b>reacciona</b> a lo que pasa a su alrededor.",
               ["Cambiá <b>#define NIVEL</b> a <b>6</b> y subí el programa.",
                "Armá en el piso una zona con cajas y paredes de cartón. Un adulto siempre cerca.",
                "Escribí <b>explorar</b>. El robot avanza solo; cuando ve un obstáculo, <b>mira a los lados y gira hacia donde hay más lugar</b>. Se corta con <b>parar</b> o a los 30 segundos.",
                "Ahora poné <b>tu propia regla</b>: <b>cuando obstaculo izquierda 1</b>. Volvé a escribir <b>explorar</b> y mirá la diferencia.",
                "Probá reglas distintas y compará cuál sale mejor del laberinto. Para volver a que decida solo: <b>cuando obstaculo nada</b>."],
               ["explorar", "cuando obstaculo izquierda 1", "cuando obstaculo atras 1", "cuando obstaculo nada", "parar"],
               ["Mirar al robot explorar y contar cuántas veces gira.",
                "Armar la “casa del robot” con cajas y ver si encuentra la salida."],
               ["Inventar tres reglas distintas y hacer una tabla: cuál tarda menos en salir del laberinto.",
                "Explicar con sus palabras la diferencia entre el robot que <i>obedece</i> (etapa 3) y el que <i>decide</i> (esta etapa)."],
               ["El robot avanza, frena al ver un obstáculo y gira.", "Con tu regla gira siempre igual; sin regla decide mirando."],
               ["Gira siempre para el lado contrario al que dice: intercambiá SERVO_IZQ y SERVO_DER.",
                "Se queda dando vueltas en un rincón: es normal si no hay salida cerca; probá una regla con <b>atras 1</b> o un giro más largo."])

    s += etapa(8, "Control remoto desde la laptop", "NIVEL 6 (el mismo)",
               "<b>Control compartido:</b> la persona decide adónde ir y el robot se protege solo. Quien maneja da órdenes y el robot <b>responde automáticamente</b> (frena, avisa). "
               "Así funcionan los autos con asistencia de frenado.",
               ["Dejá el robot con el programa del nivel 6 y el sensor conectado. Abrí la consola Bluetooth.",
                "Escribí <b>teclado</b>. Pasa a modo control remoto: <b>W A S D</b> o las flechas mueven al robot, <b>espacio</b> frena, <b>+</b> y <b>-</b> cambian la velocidad.",
                "<b>M</b> pide la distancia, <b>E</b> activa explorar y <b>Q</b> vuelve a la consola.",
                "Mantené apretada una tecla para seguir avanzando; al soltarla, el robot se detiene solo a los 4 segundos.",
                "Manejalo hacia una pared: aunque sigas apretando <b>W</b>, el robot frena y avisa “OBSTACULO”."],
               None,
               ["Una pista con cinta y una “garage” de cajas: estacionar el robot sin tocar las paredes.",
                "Turnarse con un hermano: uno maneja, el otro cronometra."],
               ["Carrera contra reloj por un circuito, con la protección apagada (<b>proteccion 0</b>) y después encendida. ¿Qué cambia?",
                "Explicar quién decide cada cosa: ¿qué piensa la laptop y qué piensa el robot?"],
               ["Los movimientos responden a las teclas.", "Frena solo antes de chocar y la consola muestra el aviso."],
               ["El modo teclado no responde: hay que estar con la ventana de la terminal activa.",
                "Se pierde la conexión: apagá y prendé el robot, y volvé a abrir la consola."],
               extra=[callout("¿Y DESPUÉS?",
                              "El siguiente paso natural es que los chicos programen <b>la laptop</b>: un pequeño programa en Python que mande una lista de órdenes al robot "
                              "(un recorrido completo) y espere las respuestas. Es el mismo concepto de programa, pero ahora corre en la compu.", bg=SAND)])

    # ---------------- APENDICES ----------------
    s.append(P("Tabla de comandos por nivel", h1))
    s.append(table([
        ["Palabra", "Nivel", "Qué hace", "Ejemplo"],
        ["hola · ayuda", "1", "Saluda · lista las palabras del nivel", "hola"],
        ["di &lt;texto&gt;", "1", "Repite lo que sigue", "di hola mundo"],
        ["led 1 · led 0", "1", "Enciende o apaga el led de la placa", "led 1"],
        ["parpadear n", "1", "Parpadea n veces (1 a 20)", "parpadear 5"],
        ["adelante · atras", "2", "Avanza o retrocede (frena solo a los 4 s)", "adelante"],
        ["izquierda · derecha", "2", "Gira en el lugar", "derecha"],
        ["parar", "2", "Detiene todo, también programas y explorar", "parar"],
        ["d · a · i · e · r", "2", "Atajos de una letra (adelante, atras, izquierda, derecha, parar)", "d"],
        ["adelante n (y las demás)", "3", "Se mueve n segundos y se detiene (0,1 a 20)", "adelante 2"],
        ["velocidad n", "3", "Velocidad de las dos ruedas (60 a 255)", "velocidad 180"],
        ["velocidad izq n · der n", "3", "Velocidad de una sola rueda (para calibrar)", "velocidad izq 140"],
        ["programa … fin", "4", "Graba pasos (hasta 12) hasta escribir fin", "programa"],
        ["listar · borrar", "4", "Muestra o vacía el programa", "listar"],
        ["ejecutar n", "4", "Corre el programa n veces (1 a 9)", "ejecutar 4"],
        ["esperar n", "4", "Pausa de n segundos dentro de un programa", "esperar 1"],
        ["distancia", "5", "Mide la distancia en cm", "distancia"],
        ["escanear", "5", "Mide izquierda, frente y derecha", "escanear"],
        ["mirar izq|der|frente|grados", "5", "Gira el servo", "mirar izq"],
        ["proteccion n", "5", "Frena al ver algo a menos de n cm (0 = apagada)", "proteccion 25"],
        ["cuando obstaculo &lt;orden&gt;", "6", "Define qué hacer al ver un obstáculo (“nada” = decide solo)", "cuando obstaculo izquierda 1"],
        ["explorar", "6", "Avanza solo y esquiva obstáculos (máx. 30 s)", "explorar"],
    ], [CW * 0.28, CW * 0.08, CW * 0.40, CW * 0.24]))
    s.append(PageBreak())

    s.append(P("Palabras de programador (para los chicos)", h1))
    s.append(table([
        ["Palabra", "Qué quiere decir"],
        ["Programa", "Una lista de instrucciones para que una máquina haga algo."],
        ["Comando", "Una palabra que el robot entiende, como <b>adelante</b>."],
        ["Argumento", "El dato que acompaña al comando, como el <b>2</b> de “adelante 2”."],
        ["Compilar", "Traducir lo que escribimos al idioma de la placa."],
        ["Subir", "Mandar el programa traducido al Arduino por el cable."],
        ["Variable", "Un valor guardado que puede cambiar, como la <b>velocidad</b>."],
        ["Secuencia", "Pasos que se hacen uno después del otro, en orden."],
        ["Bucle", "Repetir los mismos pasos varias veces (<b>ejecutar 4</b>)."],
        ["Condición", "“Si pasa esto, entonces hago aquello” (<b>cuando obstaculo …</b>)."],
        ["Sensor", "Una pieza que mide algo del mundo, como la distancia."],
        ["Umbral", "El número límite a partir del cual el robot decide algo (los 20 cm del freno)."],
        ["Calibrar", "Ajustar números midiendo, hasta que algo funcione bien (que vaya derecho)."],
        ["Error (bug)", "Algo que no sale como esperábamos. Buscarlo y arreglarlo se llama <b>depurar</b>."],
    ], [CW * 0.22, CW * 0.78]))
    s.append(Spacer(1, 12))

    s.append(P("Hoja de calibración", h1))
    s.append(P("1. ¿Cuánto avanza el robot? (velocidad ______)", h2))
    s.append(table([["Tiempo", "Distancia (cm)", "Se desvió hacia…"], ["1 s", "", ""], ["2 s", "", ""], ["3 s", "", ""]], [CW * 0.25, CW * 0.35, CW * 0.40]))
    s.append(P("2. ¿Cuánto tarda en girar un cuarto de vuelta?", h2))
    s.append(table([["Orden", "¿Giró 90 grados? (más / menos / justo)"], ["derecha 0,5", ""], ["derecha 0,6", ""], ["derecha 0,7", ""]], [CW * 0.35, CW * 0.65]))
    s.append(P("3. ¿Qué tan bien mide el sensor?", h2))
    s.append(table([["Distancia real (cm)", "Dice el sensor (cm)", "Diferencia"], ["20", "", ""], ["50", "", ""], ["100", "", ""]], [CW * 0.33, CW * 0.33, CW * 0.34]))
    s.append(PageBreak())

    s.append(P("Solución de problemas", h1))
    s.append(table([
        ["Problema", "Qué probar"],
        ["El IDE no ve el puerto USB", "Cambiar el cable (que sea de datos). Si /dev/ttyUSB0 aparece pero da “permiso denegado”: <font face='Mono'>sudo usermod -aG dialout $USER</font> y reiniciar la sesión."],
        ["Error al subir el programa", "Placa = Arduino Uno y el puerto correcto. Cerrar el Monitor Serie y la consola Bluetooth. Desenchufar y volver a enchufar el USB."],
        ["La consola no encuentra el robot", "Robot encendido, celular desconectado del módulo, luz del módulo parpadeando. Si la luz está fija hay otro aparato conectado."],
        ["Bluetooth de la laptop trabado (la antena se enciende y apaga)", "Reiniciar la laptop. Evitar reiniciar el servicio bluetooth o descargar el módulo btusb a mano."],
        ["“No se esa palabra (todavía)”", "Escribirla sin tildes, o subir el nivel que la incluye (ver la tabla de comandos)."],
        ["Las ruedas no se mueven", "Baterías encendidas y cargadas, masa común entre L298N y Arduino, y MAPA_PINES correcto."],
        ["Una rueda gira al revés", "Poner <b>true</b> en INVERTIR_IZQ o INVERTIR_DER y volver a subir."],
        ["Se desvía al avanzar", "Calibrar con <b>velocidad izq</b> y <b>velocidad der</b>."],
        ["Se reinicia al arrancar o al mover el servo", "Baterías bajas, el 5 V del L298N conectado al VIN en vez de al pin 5V, o falta un capacitor de 470 µF en la alimentación del servo."],
        ["El sensor siempre da 0", "Revisar Trig y Echo y los 5 V. Si hay objetos a menos de 2 cm tampoco los ve."],
        ["El servo mira al revés", "Intercambiar los valores de SERVO_IZQ y SERVO_DER en el código."],
        ["No lee las órdenes largas por Bluetooth", "Las órdenes tienen un máximo de 39 letras y cada paso de programa, 21. Acortalas."],
    ], [CW * 0.32, CW * 0.68]))
    s.append(Spacer(1, 10))
    s.append(callout("ARCHIVOS DE ESTA GUÍA",
                     "<b>robot_didactico.ino</b>: el programa del Arduino (cambiá NIVEL y MAPA_PINES). "
                     "<b>consola_robot.py</b>: la consola Bluetooth con modo teclado para la laptop."))

    doc.build(s)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "guia.pdf")
