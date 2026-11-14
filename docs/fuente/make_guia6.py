#!/usr/bin/env python3
"""Guía de actividades del nivel 6 de Roli: ver, girar justo y decidir solo. (14-nov-2026)

Misma letra, mismos estilos y mismas ayudas que la guía del nivel 3 (make_guia3.py). Todo lo que se escribe en la
consola sale de la ayuda del firmware (firmware/roli_programa.ino, NIVEL 6): si cambia una palabra allá, cambia acá.
Para regenerar:  python3 make_guia6.py ../Roli_guia_nivel6.pdf
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_guia3 import *  # estilos, banner, mision, tabla_vacia, etc.


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=1.6 * cm, bottomMargin=1.7 * cm,
                          title="Roli - Guía de actividades del nivel 6", author="Mauro")
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 1.7 * cm, CW, H - 3.3 * cm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=pie2)])
    s = []

    # ---------- Portada + lo nuevo ----------
    cover = Table([[[Paragraph("Nivel 6", ParagraphStyle("t", parent=white_b, fontSize=34, leading=38)),
                     Paragraph("Roli mira, gira justo y decide solo", ParagraphStyle("st", parent=white_b, fontSize=16, leading=21)),
                     Spacer(1, 6),
                     Paragraph("Guía de actividades para Yacko y Kala (y quien quiera jugar con ellos)", ParagraphStyle("st2", parent=white, fontSize=12, leading=16))]]], colWidths=[CW])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL), ("LEFTPADDING", (0, 0), (-1, -1), 16),
                               ("TOPPADDING", (0, 0), (-1, -1), 16), ("BOTTOMPADDING", (0, 0), (-1, -1), 16)]))
    s += [cover, Spacer(1, 10)]

    s.append(P("Lo nuevo de este nivel", h2))
    s.append(Paragraph("Hasta ahora ustedes le decían a Roli cada paso. Ahora Roli <b>mira el mundo</b> con sus dos ojos (uno adelante, que gira con el cuello, y otro atrás) "
                       "y <b>decide solo</b> qué hacer. Ustedes le dan <b>reglas</b>; Roli las aplica.", kid))
    s.append(Spacer(1, 6))
    tarjeta = Table([
        [Paragraph("distancia", cmd), Paragraph("Dice qué tan lejos está lo que tiene adelante", kid)],
        [Paragraph("distancia atras", cmd), Paragraph("Lo mismo, pero con el ojo de atrás", kid)],
        [Paragraph("escanear", cmd), Paragraph("Mira de lado a lado y anota qué ve en cada dirección", kid)],
        [Paragraph("mirar izq", cmd), Paragraph("Gira el cuello (también: der, frente)", kid)],
        [Paragraph("proteccion 20", cmd), Paragraph("Frena solo si hay algo a menos de 20 cm (0 la apaga)", kid)],
        [Paragraph("girar der 90", cmd), Paragraph("Gira los grados que le digan (también: izq)", kid)],
        [Paragraph("explorar", cmd), Paragraph("Anda solo esquivando (explorar 60 = durante 60 segundos)", kid)],
        [Paragraph("cuando obstaculo izquierda 1", cmd), Paragraph("Su propia regla: “si ves algo, hacé esto”", kid)],
        [Paragraph("teclado", cmd), Paragraph("Se maneja con las flechas y aun así se cuida solo", kid)],
    ], colWidths=[CW * 0.40, CW * 0.60])
    tarjeta.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.2, TEAL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2FAF8")),
                                 ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#BBD9D3")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    s += [tarjeta, Spacer(1, 6)]
    s.append(callout("ROLI TODAVÍA ESTÁ APRENDIENDO A VER",
                     "Los ojos y el cuello se están terminando de ajustar. Si Roli dice “no veo nada” con la mano adelante, no es culpa de ustedes: anótenlo en la bitácora y avísenle a Mauro.", bg=SAND))
    s.append(Spacer(1, 6))

    s.append(P("Para el adulto: dejar a Roli listo para el nivel 6", h2))
    s += numbered([
        "Abrí <b>roli_programa.ino</b>, poné <font face='Mono'>#define NIVEL 6</font> (con <font face='Mono'>MAPA_PINES 1</font>) y subilo con el USB. Desconectalo, encendé las baterías y abrí <font face='Mono'>./roli.sh</font>. <b>ayuda</b> tiene que mostrar <i>explorar</i> y <i>girar</i>.",
        "<b>Calibren primero</b> (10 minutos, todos juntos): en la consola escriban <font face='Mono-B'>sesion</font>. Roli se corrige para ir derecho, arranca bien y, como estamos en el nivel 6, <b>calibra el giro de 90°</b>. Al final se guarda en Roli y se copia la lista para pegarla en el sitio.",
        "Materiales: <b>cajas de cartón</b> (para paredes y obstáculos), <b>cinta de papel</b>, cinta métrica, la bitácora de la última página y un piso liso de unos 3 × 3 metros, sin escaleras ni mascotas.",
        "Baterías cargadas: con las baterías flojas el giro y el arranque cambian. Si algo cambió mucho, vuelvan a escribir <font face='Mono'>sesion</font>.",
    ])
    s.append(PageBreak())

    # ---------- Parte 1 · Los ojos ----------
    s.append(banner("Parte 1 · Los ojos de Roli", "Adelante, atrás y frenar solo", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(1, "¿Qué ve adelante?",
                "Pongan la mano a 10 cm del ojo de adelante y escriban <b>distancia</b>. Alejen la mano de a 10 cm y vuelvan a escribirlo. ¿Dice lo que ustedes miden con la cinta? ¿Hasta qué distancia ve bien?",
                ["distancia", "distancia", "distancia"], 1, "Una cosa blanda (una remera, un almohadón) devuelve peor el sonido que una caja de cartón. ¡Pruébenlo!")
    s += mision(2, "El mapa de Roli",
                "Pongan tres cajas: una a la izquierda, una al frente y una a la derecha, a distintas distancias. Escriban <b>escanear</b>. ¿Roli “dibuja” bien dónde están? Después usen <b>mirar izq</b>, <b>mirar der</b> y <b>mirar frente</b>.",
                ["escanear", "mirar izq", "distancia", "mirar frente"], 2, "Dibujen en una hoja lo que dijo Roli y comparen con la mesa de verdad.")
    s += mision(3, "¿Y atrás?",
                "Roli tiene un segundo ojo que mira hacia atrás, fijo. Pongan la mano detrás y escriban <b>distancia atras</b>. Después prueben <b>atras</b> hacia una caja: ¿se frena solo antes de chocar?",
                ["distancia atras", "atras"], 2, "Frenar al ir hacia atrás sólo funciona porque ese ojo lo avisa. Sin él, Roli iría a ciegas.")
    s += mision(4, "Frenar solo",
                "Escriban <b>proteccion 20</b> y mandenlo <b>adelante</b> hacia una caja. ¿A qué distancia se frena? Cambien el 20 por 40 y por 10 y comparen. Con <b>proteccion 0</b> se apaga: ¡no lo usen cerca de nada que se rompa!",
                ["proteccion 20", "adelante", "proteccion 40", "adelante"], 1,
                "¿Qué número es mejor para un piso resbaloso? ¿Y para ir despacio?")
    s.append(Spacer(1, 8))

    # ---------- Parte 2 · Girar justo ----------
    s.append(banner("Parte 2 · Girar justo", "Con grados, no con segundos", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(5, "Un cuarto de vuelta",
                "Marquen con cinta una L en el piso. Escriban <b>girar der 90</b> y miren si Roli queda alineado con la cinta. Si gira de menos, escriban <b>calibrar giro mas</b>; si se pasa, <b>calibrar giro menos</b>. Repitan hasta que quede justo y después <b>calibrar guardar</b>.",
                ["girar der 90", "calibrar giro mas", "girar der 90", "calibrar guardar"], 2,
                "En el nivel 3 giraban con <b>derecha 0,5</b> (segundos). Ahora le dicen los grados y Roli hace la cuenta. ¡Es más fácil!")
    s += mision(6, "Media vuelta",
                "Sin cambiar nada, escriban <b>girar izq 180</b>. ¿Queda mirando para el otro lado? ¿Y <b>girar izq 360</b>: da una vuelta entera? Anoten cuánto se desvía.",
                ["girar izq 180", "girar izq 360"], 2, "Si se desvía más cuanto más gira, hay que volver a calibrar el giro.")
    s += mision(7, "El cuadrado perfecto",
                "Con <b>girar der 90</b> y el tiempo que ya midieron para avanzar, que Roli dibuje un cuadrado: avanzar, girar, cuatro veces. ¿Vuelve al punto de salida? ¿A cuántos centímetros quedó? ¿Mejor o peor que en el nivel 3?",
                ["adelante 1,5", "girar der 90", "adelante 1,5", "girar der 90", "(y así hasta cerrar)"], 2,
                "Para repetirlo solo, pueden guardar los pasos con <b>programa … fin</b> (nivel 4) y usar <b>ejecutar 4</b>.")
    s.append(Spacer(1, 6))
    s.append(callout("¿POR QUÉ NO GIRA SIEMPRE LO MISMO?",
                     "Roli calcula el giro por <b>tiempo</b>: sabe cuántos milisegundos tarda en girar un grado. Pero las baterías, el piso y la rueda loca cambian ese número. "
                     "Para un giro exacto de verdad haría falta un sensor de giro (giroscopio): es una de las mejoras del manual.", bg=MINT, color=TEAL))
    s.append(Spacer(1, 8))

    # ---------- Parte 3 · Decidir solo ----------
    s.append(banner("Parte 3 · Roli decide solo", "Reglas, laberintos y trabajo en equipo", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(8, "Explorar",
                "Armen con cajas un laberinto sencillo (un pasillo con una curva). Escriban <b>explorar</b> y no toquen nada. Roli avanza, mira de lado a lado y, si algo queda cerca, frena, mira siete direcciones (y atrás) y se va por donde ve más lejos. ¿Sale del laberinto? Para frenarlo, <b>parar</b>.",
                ["explorar", "(mirar sin tocar)", "parar"], 2,
                "Si todo está cerca, Roli se detiene y lo dice: “atrapado”. ¡Es una decisión inteligente!")
    s += mision(9, "Mi propia regla",
                "Con <b>cuando obstaculo izquierda 1</b> le enseñan a Roli qué hacer cuando ve algo: girar a la izquierda durante 1 segundo. Escriban la regla y después <b>explorar</b>. ¿Hace lo que ustedes pensaron? Cambien la regla (<b>derecha 2</b>, <b>atras 1</b>) y comparen. <b>cuando obstaculo nada</b> la borra.",
                ["cuando obstaculo izquierda 1", "explorar", "cuando obstaculo derecha 2", "explorar"], 2,
                "Una regla tonta puede dar un resultado gracioso. Es parte de aprender: probar, mirar y cambiar UNA cosa.")
    s += mision(10, "Control remoto con red de seguridad",
                "En la consola escriban <b>teclado</b>. Con las flechas o con W A S D, una persona maneja a Roli. ¿Qué pasa si lo llevan hacia una pared? Roli se frena solo. ¿Quién decide: la persona o Roli?",
                ["teclado"], 1, "Para salir del teclado, la tecla que dice la pantalla.")
    s.append(Spacer(1, 6))
    s.append(banner("Desafío final: el laberinto del equipo", "Todos juntos, con roles que se rotan", bg=TEAL_D))
    s.append(Spacer(1, 6))
    s.append(Paragraph("Armen un laberinto con cajas y saquen a Roli del otro lado <b>primero guiándolo y después programándolo</b>. Nadie compite: el equipo entero junta estrellas. "
                       "Cada ronda se reparten tres lugares y <b>se rotan</b>:", kid))
    s += bullets([
        "<b>Operador:</b> el único que escribe en la consola. Teclea lo que le dicen, ni una letra más.",
        "<b>Navegante:</b> mira a Roli y dice en voz alta qué hacer, paso a paso. No toca el teclado.",
        "<b>Constructor del terreno:</b> arma y cambia las cajas y la cinta entre un intento y otro, y ayuda a medir.",
    ])
    s.append(Paragraph("En el sitio de Roli, <b>▶ A jugar con Roli</b> lleva la cuenta de las rondas, los roles y las estrellas (hace falta entrar con la cuenta).", small))
    s.append(PageBreak())

    # ---------- Bitácora ----------
    s.append(banner("Bitácora de Roli · nivel 6", "Fotocopiala y anotá todo lo que midan", bg=TEAL_D))
    s.append(Spacer(1, 8))
    s.append(P("Los ojos (misiones 1 a 4)", h2))
    s.append(tabla_vacia(["Mano a (cm)", "Dice distancia…", "Dice distancia atras…", "¿Bien?"], [["10", "", "", ""], ["20", "", "", ""], ["40", "", "", ""], ["80", "", "", ""]], [CW * 0.22, CW * 0.26, CW * 0.3, CW * 0.22]))
    s.append(Spacer(1, 4))
    s.append(tabla_vacia(["proteccion", "Se frenó a (cm)", "Notas"], [["10", "", ""], ["20", "", ""], ["40", "", ""]], [CW * 0.25, CW * 0.3, CW * 0.45]))
    s.append(Spacer(1, 8))
    s.append(P("El giro (misiones 5 a 7)", h2))
    s.append(tabla_vacia(["Prueba", "calibrar giro…", "¿Quedó justo?"], [["girar der 90", "", ""], ["girar der 90", "", ""], ["girar izq 180", "", ""], ["Cuadrado: a cuántos cm volvió", "", ""]], [CW * 0.4, CW * 0.3, CW * 0.3]))
    s.append(Spacer(1, 8))
    s.append(P("Explorar y mis reglas (misiones 8 y 9)", h2))
    s.append(tabla_vacia(["Regla o laberinto", "¿Salió?", "Qué hizo Roli"], [["explorar solo", "", ""], ["cuando obstaculo ______", "", ""], ["cuando obstaculo ______", "", ""]], [CW * 0.4, CW * 0.15, CW * 0.45]))
    s.append(Spacer(1, 8))
    s.append(P("Mi calibración", h2))
    s.append(tabla_vacia(["Qué es", "Valor"], [["Fecha de la sesión de calibración", ""], ["Cuántas veces corregí con desvio", ""], ["¿Cuánto giró el primer girar der 90?", ""], ["Algo raro que notamos", ""]], [CW * 0.65, CW * 0.35]))
    s.append(PageBreak())

    # ---------- Para el adulto ----------
    s.append(banner("Para el adulto: qué aprenden y cómo acompañar", bg=TEAL_D))
    s.append(Spacer(1, 8))
    s.append(P("Qué se aprende en este nivel", h2))
    s += bullets([
        "<b>Sensores:</b> un robot mide el mundo, y ninguna medida es perfecta (una remera “se ve” distinto que una caja).",
        "<b>Umbrales:</b> “si está a menos de 20 cm, frená”. Un número decide una acción.",
        "<b>Reglas (condicionales):</b> <i>cuando obstaculo…</i> es un “si pasa esto, entonces hago aquello”, la base de casi todo programa.",
        "<b>Unidades:</b> pasar de segundos a grados facilita la tarea, pero esconde una cuenta: ¿quién la hace ahora?",
        "<b>Calibrar:</b> medir, corregir y guardar. El mismo robot se comporta distinto con otras baterías o en otro piso.",
        "<b>Trabajo en equipo:</b> quien escribe, quien mira y quien prepara el terreno dependen unos de otros.",
    ])
    s.append(Spacer(1, 8))
    s.append(P("Preguntas para conversar con ellos", h2))
    s += bullets([
        "¿Por qué Roli frena a veces antes y a veces después de lo que dijimos? ¿Qué podría estar fallando: el ojo, la superficie, la batería?",
        "Si tuvieras que explicarle a Roli cómo salir de un laberinto con una sola regla, ¿cuál sería?",
        "¿Cuándo preferís manejarlo vos y cuándo dejar que decida Roli?",
        "¿Qué tendría que tener Roli para girar exacto siempre? (pista: el manual habla de un giroscopio)",
    ])
    s.append(Spacer(1, 8))
    s.append(P("Cómo acompañar", h2))
    s += bullets([
        "Empiecen siempre con <b>sesion</b>: una calibración hecha hace dos días no vale con otras baterías.",
        "Rotar los lugares en cada ronda: nadie hace siempre lo mismo.",
        "Cuando falle, cambiar <b>una sola cosa</b> y volver a probar. Anotarlo en la bitácora.",
        "Al terminar, llevar la calibración al sitio (la consola la copia sola) y, si midieron algo (segundos por metro, giro), anotarlo en la partida del sitio: sirve para ajustar a Roli.",
    ])
    s.append(Spacer(1, 8))
    s.append(callout("¿Y DESPUÉS?",
                     "Cuando puedan explicar cómo decide Roli en <b>explorar</b> y hayan inventado una regla propia, están listos para las <b>mejoras</b> del manual: el cuentavueltas (para avanzar y girar exacto) y el seguidor de línea.", bg=MINT, color=TEAL))
    s.append(Spacer(1, 8))
    s.append(callout("SEGURIDAD", "<b>parar</b> funciona en cualquier momento, también en <b>explorar</b> y en el <b>teclado</b>. Mantengan el espacio libre de personas, mascotas y escaleras mientras anda, y no usen <b>proteccion 0</b> cerca de cosas que se rompan.", bg=colors.HexColor("#FDE7E4"), color=RED))

    doc.build(s)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "guia6.pdf")
