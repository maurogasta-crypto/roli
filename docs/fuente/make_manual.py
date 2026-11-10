#!/usr/bin/env python3
"""Manual de Roli para Yacko y Kala."""
import sys
sys.path.insert(0, "/home/claude/pdfsrc")
from make_pdf import *  # estilos y ayudantes
from reportlab.platypus import Image as RLImage
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from PIL import Image as PILImage

IMG = "/home/claude/manual/img/"


def img(name, w=None, h=None):
    pw, ph = PILImage.open(IMG + name).size
    if w and not h:
        h = w * ph / pw
    elif h and not w:
        w = h * pw / ph
    return RLImage(IMG + name, width=w, height=h)


big = ParagraphStyle("big", parent=body, fontSize=11, leading=16)
kid = ParagraphStyle("kid", parent=body, fontSize=11, leading=16)
kidb = ParagraphStyle("kidb", parent=kid, fontName="Sans-B")
cmd = ParagraphStyle("cmd", parent=body, fontName="Mono-B", fontSize=11, leading=14, textColor=TEAL_D)
tiny = ParagraphStyle("tiny", parent=body, fontSize=8, leading=10.5, textColor=colors.HexColor("#6B7A83"))


def pie2(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 8)
    canvas.setFillColor(colors.HexColor("#6B7A83"))
    canvas.drawString(M, 1.1 * cm, "Roli · el manual de Yacko y Kala")
    canvas.drawRightString(W - M, 1.1 * cm, f"{doc.page}")
    canvas.restoreState()


def banner(texto, sub=None, bg=TEAL):
    inner = [Paragraph(texto, white_b)]
    if sub:
        inner += [Spacer(1, 2), Paragraph(sub, white)]
    t = Table([[inner]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LEFTPADDING", (0, 0), (-1, -1), 12),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 9),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    return t


def ficha(foto, w_foto, titulo, que_es, como_lo_uso, nombre_roli=None):
    """Una pieza: foto a la izquierda, texto simple a la derecha."""
    txt = [Paragraph(titulo, ParagraphStyle("ft", parent=kidb, fontSize=12.5, textColor=TEAL_D)), Spacer(1, 2)]
    if nombre_roli:
        txt.append(Paragraph(nombre_roli, ParagraphStyle("nr", parent=label, fontSize=9.5)))
        txt.append(Spacer(1, 2))
    txt.append(Paragraph(que_es, ParagraphStyle("q", parent=kid, fontSize=10, leading=14)))
    txt.append(Spacer(1, 3))
    txt.append(Paragraph("<b>En Roli:</b> " + como_lo_uso, ParagraphStyle("c", parent=kid, fontSize=9.4, leading=13, textColor=colors.HexColor("#3A4850"))))
    t = Table([[img(foto, w_foto), txt]], colWidths=[w_foto + 10, CW - w_foto - 10])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8F9")),
                           ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD3D8")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return KeepTogether([t, Spacer(1, 6)])


def mision(num, titulo, texto, ordenes=None, estrellas=1, pista=None):
    estr = "★" * estrellas
    filas = [[Paragraph(f"MISIÓN {num}", ParagraphStyle("mn", parent=white, fontName="Sans-B", fontSize=9.5)),
              Paragraph(estr, ParagraphStyle("me", parent=white_b, alignment=2, fontSize=12, textColor=colors.HexColor("#FFD27A")))],
             [Paragraph(titulo, white_b), ""]]
    h = Table(filas, colWidths=[CW * 0.7, CW * 0.3])
    h.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ORANGE), ("SPAN", (0, 1), (1, 1)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                           ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
                           ("TOPPADDING", (0, 1), (-1, 1), 1), ("BOTTOMPADDING", (0, 1), (-1, 1), 8)]))
    f = [h, Spacer(1, 5), Paragraph(texto, kid)]
    if ordenes:
        f += [Spacer(1, 4), codebox(ordenes, "ESCRIBÍ")]
    if pista:
        f += [Spacer(1, 4), Paragraph("<b>Pista:</b> " + pista, ParagraphStyle("pi", parent=small, textColor=colors.HexColor("#6B5A2A")))]
    f.append(Spacer(1, 10))
    return [KeepTogether(f)]


def diagrama_bloques():
    d = Drawing(CW, 235)

    def caja(x, y, w, h, t, fill, tc=colors.white, fs=9):
        d.add(Rect(x, y, w, h, rx=6, ry=6, fillColor=fill, strokeColor=None))
        lines = t.split("\n")
        for i, ln in enumerate(lines):
            d.add(String(x + w / 2, y + h / 2 + (len(lines) - 1) * 5 - i * 11 - 3.5, ln, fontName="Sans-B", fontSize=fs, fillColor=tc, textAnchor="middle"))

    def lin(x1, y1, x2, y2, c=INK, w=1.6):
        d.add(Line(x1, y1, x2, y2, strokeColor=c, strokeWidth=w))

    def txt(x, y, t, c=INK, fs=7.8, anchor="middle"):
        d.add(String(x, y, t, fontName="Sans", fontSize=fs, fillColor=c, textAnchor=anchor))

    GR = colors.HexColor("#2E7D4F")
    # baterias
    caja(0, 165, 105, 55, "Baterías\n18650 (2)", colors.HexColor("#444B50"))
    # L298N
    caja(155, 150, 120, 85, "L298N\n(los músculos)", colors.HexColor("#B83232"))
    lin(105, 200, 155, 200, RED, 2.2)
    txt(130, 207, "7-8 V", RED)
    # motores
    caja(335, 190, 100, 38, "Motor izq.", colors.HexColor("#E3B100"), INK)
    caja(335, 140, 100, 38, "Motor der.", colors.HexColor("#E3B100"), INK)
    lin(275, 209, 335, 209); lin(275, 159, 335, 159)
    txt(305, 214, "OUT1/2"); txt(305, 164, "OUT3/4")
    # arduino
    caja(155, 20, 120, 78, "Arduino UNO\n(el cerebro)", colors.HexColor("#1B6FA8"))
    lin(215, 98, 215, 150, RED, 2.2)
    txt(219, 119, "VIN", RED, anchor="start")
    lin(185, 98, 185, 150)
    lin(245, 98, 245, 150)
    txt(180, 119, "5 6", INK, 7, "end")
    txt(251, 119, "9 10", INK, 7, "start")
    # BLE
    caja(340, 62, 95, 34, "Bluetooth BLE", colors.HexColor("#5B3FA0"), fs=8.5)
    lin(275, 80, 340, 80)
    txt(308, 86, "11 / 12")
    # sensor
    caja(340, 20, 95, 34, "Sensor HC-SR04", colors.HexColor("#0E5E6F"), fs=8.5)
    lin(275, 36, 340, 36)
    txt(308, 42, "A0 / A1")
    # servo
    caja(0, 20, 100, 34, "Servo SG90", colors.HexColor("#3F7FBF"), fs=8.5)
    lin(100, 36, 155, 36)
    txt(128, 42, "3")
    return d


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=1.6 * cm, bottomMargin=1.7 * cm,
                          title="Roli - el manual de Yacko y Kala", author="Mauro",
                          subject="Programar al robot Roli con Arduino")
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 1.7 * cm, CW, H - 3.3 * cm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=pie2)])
    s = []

    # ============ PORTADA ============
    cover = Table([[[Paragraph("Roli", ParagraphStyle("t", parent=white_b, fontSize=56, leading=60)),
                     Paragraph("el manual de Yacko y Kala", ParagraphStyle("st", parent=white_b, fontSize=20, leading=25)),
                     Spacer(1, 8),
                     Paragraph("Cómo hablarle a un robot, hacer que se mueva, que vea y que piense… y cómo hacerlo cada vez más inteligente.",
                               ParagraphStyle("st2", parent=white, fontSize=12, leading=17))]]], colWidths=[CW])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL), ("LEFTPADDING", (0, 0), (-1, -1), 18),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 18), ("TOPPADDING", (0, 0), (-1, -1), 20), ("BOTTOMPADDING", (0, 0), (-1, -1), 20)]))
    s += [cover, Spacer(1, 12)]
    foto = img("roli_arriba.jpg", h=15.2 * cm)
    pie_foto = [Paragraph("Este es <b>Roli</b>.", ParagraphStyle("pf", parent=kidb, fontSize=15, leading=20, textColor=TEAL_D)), Spacer(1, 6),
                Paragraph("Lo armaron Mauro, Yacko y Kala. Tiene cerebro, oídos, ojos, cuello, músculos y ruedas.", kid), Spacer(1, 8),
                Paragraph("<b>Hoy</b> aprende a obedecer palabras que escriben en la laptop.", kid), Spacer(1, 6),
                Paragraph("<b>Más adelante</b> va a aprender a medir distancias, esquivar paredes y hasta a decidir solo.", kid), Spacer(1, 6),
                Paragraph("<b>Y después</b> lo van a mejorar ustedes con piezas nuevas.", kid)]
    portada = Table([[foto, pie_foto]], colWidths=[foto.drawWidth + 12, CW - foto.drawWidth - 12])
    portada.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0),
                                 ("LEFTPADDING", (1, 0), (1, 0), 12)]))
    s += [portada, Spacer(1, 10)]
    s.append(callout("PARA EMPEZAR MAÑANA",
                     "Las páginas 2 a 5 son para conocer a Roli. La página 6 es para que el adulto lo deje listo. "
                     "Las <b>misiones 1 a 6</b> (páginas 8 y 9) se pueden hacer directamente mañana con los comandos más fáciles. "
                     "El resto del manual es para cuando estén listos.", bg=SAND))
    s.append(PageBreak())

    # ============ CONOCÉ A ROLI ============
    s.append(banner("Conocé a Roli", "Mirá la foto de arriba y buscá cada número"))
    s.append(Spacer(1, 8))
    foto2 = img("roli_numerado.jpg", h=13.2 * cm)
    leyenda = [["", "Pieza", "Para qué sirve"],
               ["1", "<b>Arduino UNO</b>", "El cerebro. Piensa y manda las órdenes."],
               ["2", "<b>Puente H L298N</b>", "Los músculos. Le da fuerza a los motores."],
               ["3", "<b>Módulo Bluetooth</b>", "Los oídos. Escucha lo que escribimos en la laptop."],
               ["4", "<b>Sensor ultrasónico</b>", "Los ojos. Mide qué tan lejos está una pared."],
               ["5", "<b>Servo</b>", "El cuello. Gira el sensor para mirar a los lados."],
               ["6", "<b>Placa de conexiones</b>", "Donde se juntan varios cables."],
               ["7 y 8", "<b>Ruedas</b>", "Con un motor amarillo cada una."]]
    rest = CW - foto2.drawWidth - 12
    lt = table(leyenda, [1.1 * cm, 2.9 * cm, rest - 4.3 * cm])
    lado = Table([[foto2, [lt, Spacer(1, 10),
                           Paragraph("Y por abajo (no se ve en esta foto): las <b>baterías</b> (la comida de Roli), la <b>rueda loca</b> de adelante y dos <b>discos negros</b> con agujeritos pegados a las ruedas.", kid)]]],
                 colWidths=[foto2.drawWidth + 12, CW - foto2.drawWidth - 12])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0)]))
    s += [lado, Spacer(1, 8)]
    s.append(callout("ADIVINANZA", "Si Roli fuera una persona: ¿cuál sería su cerebro? ¿Y sus ojos? ¿Y sus piernas? Señalalos en la foto con el dedo.", bg=MINT, color=TEAL))
    s.append(PageBreak())

    # ============ LAS PIEZAS ============
    s.append(banner("Las piezas de Roli (1)", "Las fotos son de Roli de verdad"))
    s.append(Spacer(1, 8))
    s.append(ficha("arduino.jpg", 4.3 * cm, "Arduino UNO · el cerebro",
                   "Es una placa chiquita que guarda el programa y da las órdenes. Todo lo que hace Roli lo decide esta placa. Tiene filas de agujeritos (pines) donde se conectan los cables, y cada pin tiene un número.",
                   "recibe lo que escribimos, lo entiende y manda corriente a los motores. Se conecta a la laptop con el cable USB azul.",
                   "PIEZA 1"))
    s.append(ficha("bluetooth.jpg", 4.3 * cm, "Módulo Bluetooth · los oídos",
                   "Escucha mensajes que viajan por el aire, sin cables, y se los pasa al cerebro. Tiene una lucecita roja que parpadea cuando espera que alguien se conecte.",
                   "conecta la laptop con Roli. En la computadora dice “HC-06”, pero en realidad es un Bluetooth de los nuevos (BLE). Si la luz queda fija, ya hay alguien conectado (por ejemplo el celular).",
                   "PIEZA 3"))
    s.append(ficha("l298n.jpg", 4.3 * cm, "Puente H L298N · los músculos",
                   "El Arduino es muy suave para mover motores, así que le pasa la orden al L298N y este usa la fuerza de las baterías. También decide si cada motor gira para adelante o para atrás. La parte con aletas negras es un disipador: se calienta un poco.",
                   "tiene 4 bornes verdes con tornillos: dos para las baterías y dos para cada motor.",
                   "PIEZA 2"))
    s.append(ficha("motor.jpg", 3.6 * cm, "Motor amarillo y rueda",
                   "Cuando le llega electricidad, el motor gira. Dentro tiene engranajes que lo hacen más fuerte y más lento. Si la corriente entra al revés, gira al revés.",
                   "hay uno a cada lado. Para girar, una rueda va para adelante y la otra para atrás.",
                   "PIEZAS 7 y 8"))
    s.append(PageBreak())

    s.append(banner("Las piezas de Roli (2)"))
    s.append(Spacer(1, 8))
    s.append(ficha("sensor.jpg", 4.8 * cm, "Sensor ultrasónico HC-SR04 · los ojos",
                   "Tiene dos “ojos” redondos: uno grita un sonido muy agudo que no escuchamos y el otro espera el eco. Si el eco vuelve rápido, hay algo cerca. Como los murciélagos.",
                   "mide hasta unos 4 metros. Lo vamos a usar en el nivel 5 para que Roli frene antes de chocar.",
                   "PIEZA 4"))
    s.append(ficha("servo.jpg", 2.7 * cm, "Servo SG90 · el cuello",
                   "Es un motor chiquito azul que no gira en círculos: se mueve hasta el ángulo que le pedimos y se queda ahí. Con él el sensor puede mirar a la izquierda, al frente o a la derecha.",
                   "mueve el sensor. Se maneja con tres cables: marrón (−), rojo (+) y naranja (la orden).",
                   "PIEZA 5"))
    s.append(ficha("baterias.jpg", 5.3 * cm, "Baterías · la comida de Roli",
                   "Dos pilas recargables 18650 dentro de la caja negra. Juntas dan casi 8 voltios. Son de litio: <b>las toca y las carga solo un adulto</b>.",
                   "alimentan a los motores y, a través del L298N, a todo lo demás. Tienen un interruptor: es el botón para apagar a Roli.",
                   "ABAJO"))
    s.append(ficha("rueda_loca.jpg", 4.6 * cm, "Rueda loca",
                   "Una bolita que gira para todos lados. Roli no la mueve: solo se apoya en ella para no caerse de nariz.",
                   "está adelante, debajo del cuerpo.", "ABAJO"))
    s.append(ficha("discos.jpg", 4.6 * cm, "Los discos con agujeritos · ¡ya están!",
                   "Alguien (¡ustedes!) pegó discos con ranuras en las ruedas. Todavía no hacen nada, pero con una pieza nueva van a servir para <b>contar cuántas vueltas dio cada rueda</b>. Eso viene en el camino de mejoras.",
                   "esperando el cuentavueltas.", "ABAJO"))
    s.append(PageBreak())

    # ============ CÓMO ESTÁ CONECTADO ============
    s.append(banner("Cómo está conectado Roli hoy", "Para el adulto (y para los chicos que quieran seguir los cables)"))
    s.append(Spacer(1, 6))
    s.append(diagrama_bloques())
    s.append(Paragraph("Rojo = baterías (7-8 V: al L298N y, en paralelo, al VIN del Arduino) · Negro = cables de señal (los números son pines del Arduino). El − de las baterías, el GND del L298N y el GND del Arduino van unidos.", tiny))
    s.append(Spacer(1, 4))
    s.append(P("Tabla de conexiones (como está Roli hoy)", h2))
    s.append(table([
        ["Pieza", "Cable de la pieza", "Va al Arduino"],
        ["Bluetooth (BLE)", "TXD  ·  RXD", "pin 11  ·  pin 12 (con divisor de 2 resistencias)"],
        ["Motor izquierdo (L298N)", "IN1  ·  IN2", "pin 5  ·  pin 6"],
        ["Motor derecho (L298N)", "IN3  ·  IN4", "pin 9  ·  pin 10"],
        ["L298N: ENA y ENB", "puentes (jumpers) puestos", "no van al Arduino"],
        ["Sensor HC-SR04", "Trig  ·  Echo", "A0  ·  A1 (pines analógicos, confirmado en las fotos)"],
        ["Servo SG90", "señal (naranja)", "pin 3"],
        ["Electricidad hoy", "Baterías: borne 12V y GND del L298N", "en paralelo, al pin <b>VIN</b> y GND del Arduino. El Arduino saca de ahí sus 5 V para el Bluetooth, el sensor y el servo. El borne 5V del L298N queda libre"],
        ["Masa común", "GND del L298N", "GND del Arduino"],
    ], [CW * 0.28, CW * 0.26, CW * 0.46]))
    s.append(Spacer(1, 6))
    s.append(callout("OJO CON ESTAS TRES COSAS",
                     "<b>1.</b> Los puentecitos (jumpers) de ENA y ENB del L298N <b>se dejan puestos</b>, mientras los cables vayan a IN1-IN4 como hoy. "
                     "<b>2.</b> Las baterías ya entran al <b>VIN</b> del Arduino: está bien así. No conectes además el borne 5V del L298N al pin 5V (dos reguladores peleándose). Roli funciona sin USB; con el USB puesto también es seguro. "
                     "<b>3.</b> Si Roli se reinicia solo al mover el servo, ponerle un capacitor de 470 µF entre 5V y GND, cerca del servo.",
                     bg=colors.HexColor("#FDE7E4"), color=RED))
    s.append(Spacer(1, 4))
    s.append(Paragraph("En las fotos los números de pin no se llegan a leer. Los pines de los motores salen de las pruebas que ya funcionaron (5, 6, 9 y 10) y de la foto del L298N. El programa trae una <b>prueba de ruedas</b> (la orden <b>probar</b>) y tres “mapas” de pines por si algo no coincide.", small))
    s.append(PageBreak())

    # ============ ADULTO: ESTA NOCHE ============
    s.append(banner("Para el adulto: dejar a Roli listo esta noche", "Unos 20 minutos", bg=TEAL_D))
    s.append(Spacer(1, 8))
    s += numbered([
        "Abrí <b>roli_programa.ino</b> en el Arduino IDE. Ya viene con <font face='Mono'>NIVEL 2</font> y <font face='Mono'>MAPA_PINES 1</font> (los pines de la tabla anterior). No hace falta tocar nada.",
        "Conectá el Arduino por USB. <b>Placa: Arduino Uno</b>. Puerto: el que aparece (en tu laptop fue <b>/dev/ttyUSB0</b>).",
        "Apretá <b>Verificar</b> y después <b>Subir</b>. Abrí el Monitor Serie (9600, Nueva línea): tiene que decir <b>“Roli listo. NIVEL 2 MAPA 1”</b>.",
        "Escribí <b>hola</b> en el Monitor: contesta “Hola! Soy Roli…”. Escribí <b>info</b>: muestra nivel y mapa.",
        "<b>Cerrá el Monitor Serie</b> (si queda abierto, reinicia la placa y molesta la conexión Bluetooth).",
        "Poné a Roli <b>sobre una caja, con las ruedas en el aire</b>, y encendé las baterías. Escribí <b>probar</b> en el Monitor (antes de cerrarlo) o desde la consola: gira cada rueda un poquito adelante y atrás.",
        "Mirá el resultado de <b>probar</b> en la tabla de abajo y corregí si hace falta.",
        "Desconectá el USB. Encendé a Roli. En la laptop, <font face='Mono'>./roli.sh</font> (o <font face='Mono'>~/ble-env/bin/python consola_robot.py</font>). Escribí <b>hola</b>: si contesta, <b>listo para mañana</b>.",
    ])
    s.append(Spacer(1, 6))
    s.append(table([
        ["Lo que pasó con probar", "Qué hacer"],
        ["Las dos ruedas giran: adelante y atrás, bien", "Nada. ¡Todo listo!"],
        ["Una rueda gira al revés (adelante va para atrás)", "En el programa, poné <font face='Mono'>INVERTIR_IZQ = true</font> (o INVERTIR_DER) y volvé a subir."],
        ["No gira ninguna rueda", "Baterías encendidas y cargadas · GND común · cambiá a <font face='Mono'>MAPA_PINES 2</font> y probá de nuevo (solo si los cables de ENA y ENB van al Arduino y se sacaron los puentes)."],
        ["Gira solo una rueda", "Revisá los cables de esa rueda (IN1-IN2 la izquierda, IN3-IN4 la derecha) en los bornes y en el Arduino. Si ninguno de los mapas coincide con tu cableado, usá <font face='Mono'>MAPA_PINES 3</font> y escribí tus números en ese bloque."],
        ["El robot se reinicia al arrancar", "Baterías flojas (menos de unos 7 V el regulador del Arduino no alcanza), o el servo pide mucha corriente: agregar el capacitor de 470 µF cerca del servo."],
    ], [CW * 0.38, CW * 0.62]))
    s.append(Spacer(1, 6))
    s.append(callout("SI LA CONSOLA NO ENCUENTRA A ROLI", "Celular desconectado del módulo (acepta un solo aparato) · Roli encendido · luz del módulo parpadeando. Si el Bluetooth de la laptop se traba (la antena se prende y apaga), reiniciá la laptop.", bg=SAND))
    s.append(PageBreak())

    # ============ HABLARLE A ROLI ============
    s.append(banner("Cómo hablarle a Roli", "Con la laptop y sin cables"))
    s.append(Spacer(1, 8))
    s += numbered([
        "Encendé a Roli (interruptor de las baterías). La lucecita del Bluetooth parpadea.",
        "Pedile a un adulto que abra la terminal y escriba: <font face='Mono'>./roli.sh</font>",
        "Esperá a que diga <b>Conectado</b>. Aparece <font face='Mono-B'>roli&gt;</font>.",
        "Escribí una palabra y apretá <b>Enter</b>. Roli contesta en la pantalla.",
        "Para terminar escribí <b>salir</b>.",
    ])
    s.append(Spacer(1, 8))
    s.append(P("Reglas del idioma de Roli", h2))
    s += bullets([
        "Se escribe <b>sin tilde</b>: <b>atras</b>, no atrás.",
        "Da igual si es mayúscula o minúscula.",
        "Roli solo entiende las palabras de la tarjeta. Si inventás una, te contesta <i>“No se esa palabra (todavia)”</i>. ¡No es un error grave! Es como cuando alguien no entiende un idioma.",
        "Si se pierde, escribí <b>ayuda</b>.",
    ])
    s.append(Spacer(1, 8))
    s.append(P("Tarjeta de comandos (recortala)", h2))
    tarjeta = Table([
        [Paragraph("hola", cmd), Paragraph("Saluda", kid), Paragraph("adelante", cmd), Paragraph("Avanza (se frena solo en 4 s)", kid)],
        [Paragraph("ayuda", cmd), Paragraph("Dice las palabras que sabe", kid), Paragraph("atras", cmd), Paragraph("Retrocede", kid)],
        [Paragraph("di hola", cmd), Paragraph("Repite lo que escribas", kid), Paragraph("izquierda", cmd), Paragraph("Gira a la izquierda", kid)],
        [Paragraph("led 1", cmd), Paragraph("Prende la luz de la placa", kid), Paragraph("derecha", cmd), Paragraph("Gira a la derecha", kid)],
        [Paragraph("led 0", cmd), Paragraph("La apaga", kid), Paragraph("parar", cmd), Paragraph("¡Frena YA!", kid)],
        [Paragraph("parpadear 5", cmd), Paragraph("Parpadea 5 veces", kid), Paragraph("d · a · i · e · r", cmd), Paragraph("Atajos de una letra", kid)],
        [Paragraph("info", cmd), Paragraph("Dice quién es y su nivel", kid), Paragraph("probar", cmd), Paragraph("Prueba cada rueda (con adulto)", kid)],
    ], colWidths=[CW * 0.18, CW * 0.30, CW * 0.2, CW * 0.32])
    tarjeta.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.2, TEAL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2FAF8")),
                                 ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#BBD9D3")),
                                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    s += [tarjeta, Spacer(1, 8)]
    s.append(callout("REGLA DE ORO", "Roli siempre se frena solo a los <b>4 segundos</b>. Y <b>parar</b> frena siempre, pase lo que pase. Pero igual: ¡no lo dejen andar cerca de escaleras ni de mascotas!", bg=colors.HexColor("#FDE7E4"), color=RED))
    s.append(PageBreak())

    # ============ MISIONES 1-6 ============
    s.append(banner("Misiones para mañana", "Con lo que Roli ya sabe (nivel 2). ★ = fácil · ★★ = desafío", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(1, "Saludar a Roli", "Escribí <b>hola</b>. ¿Qué te contesta? Ahora hacé que Roli diga tu nombre y el de tu hermano o hermana.",
                ["hola", "di hola Yacko", "di hola Kala"], 1, "Después de <b>di</b> podés escribir lo que quieras.")
    s += mision(2, "La luz de Roli", "En la placa hay una lucecita. Prendela, apagala y hacela parpadear.",
                ["led 1", "led 0", "parpadear 5"], 1)
    s += mision(3, "¡Que se mueva!", "<b>Antes de empezar:</b> un adulto pone a Roli en un lugar libre, lejos de escaleras. "
                "Escribí <b>adelante</b> y esperá. ¿Qué pasa a los 4 segundos? Después probá <b>atras</b>.",
                ["adelante", "atras"], 1, "Cuando quieras que frene antes, escribí <b>parar</b>.")
    s += mision(4, "El semáforo", "Un jugador dice “verde” o “rojo”. El otro escribe la letra: <b>d</b> para verde (avanza) y <b>r</b> para rojo (frena). Después cambien de lugar.",
                ["d", "r"], 1)
    s += mision(5, "Girar y girar", "Escribí <b>derecha</b>, esperá un poquito y escribí <b>parar</b>. ¿Cuánto giró? Probá con <b>izquierda</b>. "
                "¿Se puede dar una vuelta completa? ¿Cuántas veces hay que escribir <b>derecha</b> y <b>parar</b>?",
                ["derecha", "parar", "izquierda", "parar"], 2)
    s += mision(6, "El camino a la silla", "Pongan una silla a 2 metros. Lleven a Roli hasta la silla usando solo estas palabras: "
                "<b>adelante, atras, izquierda, derecha, parar</b>. Cuenten cuántas órdenes necesitaron. "
                "¿Lo pueden hacer con menos?", ["adelante", "parar", "derecha", "parar", "adelante"], 2,
                "Anoten cuántas órdenes usaron. En el nivel 4 Roli va a poder repetir un camino él solo.")
    s.append(callout("¿POR QUÉ SE DETIENE SOLO?", "Roli todavía no sabe cuántos segundos mover. Por eso es mucho más seguro que se frene solo. En el <b>nivel 3</b> van a poder escribir <font face='Mono'>adelante 2</font> y Roli avanza exactamente 2 segundos.", bg=MINT, color=TEAL))
    s.append(PageBreak())

    # ============ CAMINO ============
    s.append(banner("El camino de Roli: cada vez más inteligente", "Cada nivel es el mismo programa con más palabras desbloqueadas"))
    s.append(Spacer(1, 6))
    s.append(P("Para subir de nivel, el adulto cambia el número de <font face='Mono'>#define NIVEL</font> y vuelve a subir el programa. "
               "Los niveles 1 a 6 <b>no necesitan piezas nuevas</b>: el sensor y el servo ya están puestos en Roli. Las mejoras de hardware vienen después.", big))
    s.append(Spacer(1, 6))
    s.append(table([
        ["Nivel", "Roli aprende…", "Palabras nuevas", "Pieza nueva"],
        ["1", "A hablar", "hola · di · led · parpadear · ayuda", "—"],
        ["<b>2 (hoy)</b>", "A moverse", "adelante · atras · izquierda · derecha · parar · probar", "—"],
        ["3", "Tiempo y velocidad", "adelante 2 · velocidad 150 · velocidad izq 140", "—"],
        ["4", "A guardar programas", "programa … fin · listar · ejecutar 3 · esperar · borrar", "—"],
        ["5", "A ver", "distancia · escanear · mirar izq · proteccion 20", "Sensor y servo (¡ya están!)"],
        ["6", "A decidir solo", "cuando obstaculo izquierda 1 · explorar", "—"],
    ], [CW * 0.11, CW * 0.2, CW * 0.45, CW * 0.24]))
    s.append(Spacer(1, 10))
    s.append(P("Las misiones de cada nivel", h2))
    s.append(table([
        ["Nivel", "Ejemplo de misión", "Qué se aprende"],
        ["3", "Hacer que Roli avance exactamente hasta la pared de enfrente. Probar velocidad 100 y velocidad 220: ¿cuál llega primero?", "Un número cambia lo que hace una orden (parámetro y variable)."],
        ["3", "Calibrar: si Roli se desvía, bajarle la velocidad a una rueda hasta que vaya derecho.", "Medir y ajustar."],
        ["4", "Programar “el baile”: derecha, izquierda, esperar, y repetirlo 4 veces con <b>ejecutar 4</b>.", "Secuencia y repetición."],
        ["4", "El cuadrado: avanzar y girar 90°, repetido 4 veces, hasta que vuelva al punto de salida.", "Corregir errores (depurar)."],
        ["5", "Poner la mano delante del sensor y leer <b>distancia</b>. Después, una pared de cartón: Roli no avanza si está a menos de 20 cm.", "Un sensor mide el mundo y un umbral decide."],
        ["6", "<b>explorar</b> en un laberinto de cajas. Después inventar una regla propia con <b>cuando obstaculo …</b>.", "“Si pasa esto, entonces hago aquello.”"],
    ], [CW * 0.09, CW * 0.58, CW * 0.33]))
    s.append(Spacer(1, 8))
    s.append(callout("CONTROL REMOTO DESDE LA LAPTOP",
                     "Cuando llegan al nivel 6, en la consola escriban <b>teclado</b>: Roli se maneja con las flechas o con W A S D, "
                     "y aun así frena solo si hay una pared. La persona maneja y Roli se cuida a sí mismo.", bg=SAND))
    s.append(PageBreak())

    # ============ MEJORAS ============
    s.append(banner("Las mejoras de Roli: piezas nuevas", "Cada pieza le da a Roli un superpoder y nuevas palabras", bg=TEAL_D))
    s.append(Spacer(1, 6))
    s.append(P("Estas piezas son baratas y se consiguen en cualquier tienda de electrónica. Las conexiones sugeridas usan pines que Roli todavía tiene libres; "
               "las instalan juntos, con un adulto y con Roli apagado. Orden sugerido: de más fácil a más difícil.", big))
    s.append(Spacer(1, 6))

    def mejora(num, nombre, que, poder, conexion, comandos, dificultad):
        cab = Paragraph(f"<b>{num}. {nombre}</b>", ParagraphStyle("mh", parent=kid, fontSize=12.5, textColor=TEAL_D))
        dif = Paragraph(dificultad, ParagraphStyle("md", parent=label, alignment=2))
        t = Table([[cab, dif],
                   [[Paragraph(que, ParagraphStyle("mq", parent=kid, fontSize=10, leading=14)), Spacer(1, 3),
                     Paragraph("<b>Superpoder:</b> " + poder, ParagraphStyle("mp", parent=kid, fontSize=10, leading=14)), Spacer(1, 3),
                     Paragraph("<b>Conexión (adulto):</b> " + conexion, ParagraphStyle("mc", parent=small, fontSize=8.8, leading=12.5)), Spacer(1, 2),
                     Paragraph("<b>Palabras nuevas:</b> " + comandos, ParagraphStyle("mw", parent=small, fontSize=8.8, leading=12.5))], ""]],
                  colWidths=[CW * 0.72, CW * 0.28])
        t.setStyle(TableStyle([("SPAN", (0, 1), (1, 1)), ("BACKGROUND", (0, 0), (-1, 0), MINT), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#9CC7BF")),
                               ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                               ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        return KeepTogether([t, Spacer(1, 6)])

    s.append(mejora(1, "Bocina (buzzer)", "Una piecita redonda que hace “bip”.", "Roli puede avisar con sonidos: arranca con un bip y hace una alarma cuando ve un obstáculo.",
                    "Un cable al pin <b>13</b> (o <b>A5</b> si se quiere liberar el led de la placa) y el otro a GND. Buzzer activo de 5 V.",
                    "<font face='Mono'>bip 2</font> · <font face='Mono'>alarma</font>", "FÁCIL"))
    s.append(mejora(2, "Luces de colores (LEDs)", "Tres LEDs (rojo, amarillo, verde) con una resistencia de 220 Ω cada uno.", "Un semáforo en Roli: verde cuando avanza, rojo cuando frena. Se ve desde lejos.",
                    "Tres pines libres (por ejemplo <b>2, 4 y 7</b>), cada LED con su resistencia a GND.",
                    "<font face='Mono'>luz rojo</font> · <font face='Mono'>luz verde</font> · el programa puede cambiar de color solo", "FÁCIL"))
    s.append(mejora(3, "Cuentavueltas (sensor de ranura LM393)", "Una horquilla que “ve” pasar los agujeritos del disco. ¡Los discos ya están pegados a las ruedas!", "Roli sabe cuántas vueltas dio cada rueda. Puede avanzar <b>exactamente 50 cm</b> y girar <b>exactamente 90°</b>, sin depender del tiempo ni de la batería.",
                    "Uno por rueda: señal a dos pines libres (por ejemplo <b>A2</b> y <b>A3</b>, con interrupciones de cambio de pin), 5 V y GND. Se calibra cuántos pulsos hay en una vuelta.",
                    "<font face='Mono'>avanzar 50</font> (cm) · <font face='Mono'>girar 90</font> (grados)", "MEDIO"))
    s.append(mejora(4, "Seguidor de línea (2 sensores TCRT5000)", "Sensores infrarrojos mirando al piso: distinguen una línea negra sobre el piso claro.", "Roli sigue una pista dibujada con cinta aisladora negra, sin que nadie lo maneje.",
                    "Dos módulos debajo del chasis, adelante: señales a dos pines libres. 5 V y GND.",
                    "<font face='Mono'>seguir linea</font>", "MEDIO"))
    s.append(mejora(5, "Pantalla OLED de 0,96\"", "Una pantallita con letras e ícono, que va por I2C (dos cables).", "Roli muestra en su propia cara qué está pensando: “Obstáculo a 18 cm”, “Estoy explorando”.",
                    "SDA a <b>A4</b> y SCL a <b>A5</b> (los pines I2C del UNO), 5 V y GND. Si se usa, el cuentavueltas pasa a otros pines.",
                    "<font face='Mono'>pantalla hola</font>", "MEDIO"))
    s.append(mejora(6, "Medidor de batería (2 resistencias)", "Dos resistencias iguales (por ejemplo 10 kΩ) que “achican” la tensión de las pilas para que el Arduino la pueda leer.", "Roli te dice cuánta batería le queda: <b>bateria</b> contesta, por ejemplo, “7.8 V (aprox. 68%)” y avisa cuando hay que cargarla.",
                    "Del pin <b>VIN</b> a <b>A2</b> una resistencia de 10 kΩ, y de <b>A2</b> a <b>GND</b> otra de 10 kΩ. Después, en el programa, cambiar <font face='Mono'>HAY_MEDIDOR_BATERIA</font> a <font face='Mono'>true</font> y volver a subirlo.",
                    "<font face='Mono'>bateria</font>", "FÁCIL"))
    s.append(Spacer(1, 2))
    s.append(callout("¿CUÁNTOS PINES QUEDAN?", "Roli usa el 3 (servo), 5, 6, 9 y 10 (motores), 11 y 12 (Bluetooth) y A0 y A1 (sensor). "
                     "Quedan libres el <b>2, 4, 7, 8, 13</b> y los <b>A2 a A5</b>: 9 pines. Las seis mejoras juntas piden unos 11, así que <b>casi entran todas</b>: hay que elegir bien o sumar un expansor de pines más adelante. "
                     "Eso también es aprender: planificar qué pieza va en cada pin antes de conectar. (La pantalla usa A4 y A5 sí o sí.)", bg=SAND))
    s.append(PageBreak())

    s.append(banner("Después: programar la laptop y el celular", "Los chicos pasan de usar el programa a escribir sus propios programas", bg=TEAL_D))
    s.append(Spacer(1, 8))
    s.append(table([
        ["Etapa", "Idea", "Qué hacen"],
        ["A. Python con Roli", "La laptop también se programa.", "Con un programita en Python mandar una lista de órdenes a Roli (por ejemplo, un cuadrado) y esperar la respuesta de cada una."],
        ["B. Roli que informa", "Los datos importan.", "Roli manda la distancia y la laptop dibuja un gráfico simple. ¿Qué forma tiene la habitación que midió?"],
        ["C. Control con el celular", "Otra forma de manejarlo.", "Con la app <b>Serial Bluetooth Terminal</b> (modo BLE) mandar las mismas palabras desde el celular. Recordar: el módulo acepta un solo aparato a la vez."],
        ["D. Nuevas palabras", "Ellos diseñan el idioma.", "Entre todos inventan una palabra nueva (por ejemplo <b>bailar</b>) y el adulto la agrega al programa. ¿Qué pasos tiene que hacer?"],
        ["E. Concurso", "Competir con Roli.", "Cada uno programa un recorrido en el laberinto con un límite de órdenes. Gana el que menos usó y llegó sin chocar."],
    ], [CW * 0.22, CW * 0.24, CW * 0.54]))
    s.append(Spacer(1, 12))
    s.append(P("Palabras de programador", h2))
    s.append(table([
        ["Palabra", "Qué quiere decir"],
        ["Programa", "Una lista de instrucciones para que una máquina haga algo."],
        ["Comando", "Una palabra que Roli entiende, como <b>adelante</b>."],
        ["Argumento", "El dato que acompaña al comando, como el <b>2</b> de “adelante 2”."],
        ["Variable", "Un valor guardado que puede cambiar, como la <b>velocidad</b>."],
        ["Secuencia", "Pasos que se hacen uno después del otro."],
        ["Bucle", "Repetir los mismos pasos varias veces (<b>ejecutar 4</b>)."],
        ["Condición", "“Si pasa esto, entonces hago aquello”."],
        ["Sensor", "Una pieza que mide algo del mundo, como la distancia."],
        ["Calibrar", "Medir y ajustar hasta que algo funcione bien."],
        ["Bug", "Algo que no sale como esperábamos. Buscarlo y arreglarlo se llama <b>depurar</b>."],
    ], [CW * 0.22, CW * 0.78]))
    s.append(Spacer(1, 10))
    s.append(callout("ARCHIVOS DE ESTE MANUAL",
                     "<b>roli_programa.ino</b>: el programa del Arduino. <b>consola_robot.py</b> y <b>roli.sh</b>: la consola Bluetooth para la laptop.", bg=SAND))

    doc.build(s)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "roli.pdf")
