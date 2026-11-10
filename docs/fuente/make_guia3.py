#!/usr/bin/env python3
"""Guía de actividades del nivel 3 de Roli."""
import sys
sys.path.insert(0, "/home/claude/manual")
from make_manual import *  # estilos, banner, mision, img, etc.


def tabla_vacia(cabeceras, filas, anchos, alto=0.85 * cm):
    datos = [[Paragraph(f"<b>{c}</b>", ParagraphStyle("th", parent=white_b, fontSize=9)) for c in cabeceras]]
    datos += [[Paragraph(str(c), ParagraphStyle("td", parent=body, fontSize=9.5)) if c else "" for c in fila] for fila in filas]
    t = Table(datos, colWidths=anchos, rowHeights=[0.75 * cm] + [alto] * len(filas))
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#9FB3BA")),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 6),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8F9")])]))
    return t


def build(path):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=1.6 * cm, bottomMargin=1.7 * cm,
                          title="Roli - Guía de actividades del nivel 3", author="Mauro")
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 1.7 * cm, CW, H - 3.3 * cm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=pie2)])
    s = []

    # ---------- Portada + antes de empezar ----------
    cover = Table([[[Paragraph("Nivel 3", ParagraphStyle("t", parent=white_b, fontSize=34, leading=38)),
                     Paragraph("Roli aprende a medir el tiempo y la velocidad", ParagraphStyle("st", parent=white_b, fontSize=16, leading=21)),
                     Spacer(1, 6),
                     Paragraph("Guía de actividades para Yacko y Kala", ParagraphStyle("st2", parent=white, fontSize=12, leading=16))]]], colWidths=[CW])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL), ("LEFTPADDING", (0, 0), (-1, -1), 16),
                               ("TOPPADDING", (0, 0), (-1, -1), 16), ("BOTTOMPADDING", (0, 0), (-1, -1), 16)]))
    s += [cover, Spacer(1, 10)]

    s.append(P("Lo nuevo de este nivel", h2))
    s.append(Paragraph("Hasta ahora Roli avanzaba hasta que escribían <b>parar</b> (o hasta que se frenaba solo a los 4 segundos). "
                       "Ahora le pueden decir <b>cuánto tiempo</b> moverse y <b>qué tan rápido</b>. Eso es darle un <b>dato</b> a la orden.", kid))
    s.append(Spacer(1, 6))
    tarjeta = Table([
        [Paragraph("adelante 2", cmd), Paragraph("Avanza 2 segundos y se frena solo", kid)],
        [Paragraph("atras 1,5", cmd), Paragraph("Retrocede un segundo y medio (la coma sirve)", kid)],
        [Paragraph("izquierda 0,5", cmd), Paragraph("Gira medio segundo a la izquierda", kid)],
        [Paragraph("derecha 0,5", cmd), Paragraph("Gira medio segundo a la derecha", kid)],
        [Paragraph("velocidad 150", cmd), Paragraph("Las dos ruedas a velocidad 150 (de 60 a 255)", kid)],
        [Paragraph("velocidad izq 120", cmd), Paragraph("Solo la rueda izquierda (también: velocidad der 120)", kid)],
        [Paragraph("parar", cmd), Paragraph("¡Frena YA! (siempre funciona)", kid)],
    ], colWidths=[CW * 0.32, CW * 0.68])
    tarjeta.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.2, TEAL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2FAF8")),
                                 ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#BBD9D3")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    s += [tarjeta, Spacer(1, 6)]
    s.append(Paragraph("Roli puede moverse entre <b>0,1 y 20 segundos</b> por orden. Cada vez que se enciende, arranca en <b>velocidad 90</b>. "
                       "En el modo <font face='Mono'>teclado</font>, las teclas <b>+</b> y <b>−</b> cambian la velocidad.", small))
    s.append(Spacer(1, 8))

    s.append(P("Para el adulto: preparar el nivel 3", h2))
    s += numbered([
        "Abrí <b>roli_programa.ino</b> y cambiá la línea <font face='Mono'>#define NIVEL 2</font> por <font face='Mono'>#define NIVEL 3</font>. Dejá <font face='Mono'>MAPA_PINES 1</font>.",
        "Subilo con el USB. Desconectalo, encendé las baterías y abrí <font face='Mono'>./roli.sh</font>. Escribí <b>ayuda</b>: tienen que verse las palabras de velocidad.",
        "Materiales: <b>cinta de papel</b> (para marcar la salida y la llegada en el piso), <b>cinta métrica</b>, hojas y lápiz para anotar, y un lugar liso y despejado de unos 3 metros.",
        "Baterías cargadas: los resultados cambian si están flojas. Si tienen el medidor armado, anoten con <b>bateria</b> cuánto tenían al empezar.",
    ])
    s.append(Spacer(1, 4))
    s.append(callout("COMO CIENTÍFICOS", "Un buen experimento cambia <b>una sola cosa</b> a la vez. Usen siempre la misma salida marcada con cinta, el mismo piso y las baterías parecidas. Anoten <b>todo</b> en la bitácora (última página).", bg=SAND))
    s.append(PageBreak())

    # ---------- Misiones medir ----------
    s.append(banner("Parte 1 · Medir a Roli", "Cuánto avanza en cada tiempo y a cada velocidad", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(1, "¿Cuánto avanza en 1 segundo?",
                "Marcá la salida con cinta. Escribí <b>adelante 1</b> y medí con la cinta métrica cuánto avanzó. Repetí con 2 y con 3 segundos. Anotá todo en la bitácora.",
                ["adelante 1", "adelante 2", "adelante 3"], 1,
                "Medí siempre desde el mismo punto de Roli, por ejemplo desde la punta de adelante.")
    s += mision(2, "Adivinar la distancia",
                "Con lo que midieron, <b>calculen</b> cuántos segundos hacen falta para que Roli avance exactamente 1 metro. Después prueben y vean si acertaron. ¿Cuánto se equivocaron?",
                ["adelante (el número que calcularon)"], 2,
                "Si 2 segundos son una cierta distancia, ¿qué pasa con 4 segundos? ¿Y con 1?")
    s += mision(3, "Lento, medio y rápido",
                "Dejen el tiempo fijo en <b>2 segundos</b> y cambien la velocidad: 90, 150 y 220. Antes de probar, <b>adivinen</b> cuál llega más lejos. Midan y anoten.",
                ["velocidad 90", "adelante 2", "velocidad 150", "adelante 2", "velocidad 220", "adelante 2"], 1,
                "Con velocidad muy baja (cerca de 60) Roli puede no tener fuerza para moverse. ¡Es un resultado válido, anótenlo!")
    s += mision(4, "La carrera de precisión",
                "Pongan una cinta de llegada a 1,5 metros. Cada uno elige <b>un tiempo y una velocidad</b> y gana el que deje a Roli más cerca de la cinta <b>sin pasarse</b>. Tienen 3 intentos.",
                None, 2, "Anoten qué tiempo y qué velocidad usó cada intento. ¡Aprender del intento anterior es la clave!")
    s.append(Spacer(1, 8))

    # ---------- Misiones calibrar ----------
    s.append(banner("Parte 2 · Ajustar y girar", "Hacer que Roli vaya derecho y gire justo", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(5, "Que vaya derecho",
                "Hagan avanzar a Roli 2 metros marcando una línea de cinta. ¿Se va para un costado? Es normal: las ruedas no son iguales. "
                "Frenen una rueda un poquito con <b>velocidad izq</b> o <b>velocidad der</b> y prueben otra vez hasta que vaya derecho.",
                ["velocidad izq 90", "velocidad der 100", "adelante 3"], 2,
                "Si se desvía a la derecha, la rueda izquierda va más rápida o la derecha más lenta. Cambien de a 5 en 5.")
    s += mision(6, "El giro exacto",
                "¿Cuánto tiempo hay que escribir en <b>derecha</b> para que Roli gire un cuarto de vuelta (como una esquina)? Prueben con 0,3, 0,4, 0,5… hasta encontrarlo. Anoten el tiempo ganador. ¿Y para media vuelta?",
                ["derecha 0,4", "derecha 0,5", "derecha 0,6"], 2,
                "Pongan una cinta en el piso en forma de L y miren si Roli queda alineado.")
    s += mision(7, "El cuadrado",
                "Con los tiempos de las misiones 1 y 6, hagan que Roli dibuje un <b>cuadrado</b> en el piso: avanzar, girar, avanzar, girar… cuatro veces. Marquen la salida con cinta. ¿Vuelve al mismo lugar? ¿A cuántos centímetros quedó?",
                ["adelante 1,5", "derecha 0,5", "adelante 1,5", "derecha 0,5", "(y así hasta cerrar el cuadrado)"], 2,
                "Escriban primero los pasos en una hoja. Si el cuadrado no cierra, ajusten UN número y vuelvan a probar.")
    s.append(Spacer(1, 8))

    # ---------- Misiones creativas ----------
    s.append(banner("Parte 3 · Crear recorridos", "Planificar primero, probar después", bg=ORANGE))
    s.append(Spacer(1, 8))
    s += mision(8, "Plan primero, Roli después",
                "Armen un camino con cinta en el piso (una S, una U, un laberinto sencillo). <b>Escriban en una hoja</b> todos los pasos que van a darle a Roli. Después los escriben uno por uno en la consola. ¿Llegó al final? Cuenten cuántas órdenes usaron.",
                None, 2, "Cuando falle, ¿fue un error del plan o de un número? Corregir se llama <b>depurar</b>.")
    s += mision(9, "Frenar justo antes",
                "Pongan una caja de cartón a 1 metro. Que Roli llegue lo más cerca posible <b>sin tocarla</b>. Prueben primero con velocidad baja y después con alta. ¿Cuál es más fácil de controlar?",
                None, 2, "Con velocidad alta Roli avanza mucho en poco tiempo: cualquier error de tiempo se nota más.")
    s += mision(10, "Roli bailarín",
                "Inventen un baile: giros, avances y retrocesos con tiempos distintos y velocidades distintas. Dibújenlo antes en una hoja con flechas. Después, que Roli lo baile. ¡Pueden ponerle música!",
                ["velocidad 150", "derecha 0,5", "atras 0,5", "izquierda 1", "adelante 1"], 1)
    s += mision(11, "Desafío final: la ruta del tesoro",
                "Escondan un objeto a más de 2 metros, con una esquina en el medio. El otro jugador escribe <b>solo una orden por vez</b> sin ver el plan del compañero. Tienen que llegar al tesoro con la menor cantidad de órdenes. ¿Cuántas usaron?",
                None, 2)
    s.append(PageBreak())

    # ---------- Bitácora ----------
    s.append(banner("Bitácora de Roli", "Fotocopiala y anotá todo lo que midan", bg=TEAL_D))
    s.append(Spacer(1, 8))
    s.append(P("Tiempo y distancia (misiones 1 y 2)", h2))
    s.append(tabla_vacia(["Orden", "Velocidad", "Distancia (cm)", "Batería"], [["adelante 1", "", "", ""], ["adelante 2", "", "", ""], ["adelante 3", "", "", ""], ["adelante ___", "", "", ""]], [CW * 0.28, CW * 0.2, CW * 0.28, CW * 0.24]))
    s.append(Spacer(1, 8))
    s.append(P("Velocidad (misión 3)", h2))
    s.append(tabla_vacia(["Velocidad", "Tiempo", "Mi predicción (cm)", "Distancia real (cm)"], [["90", "2 s", "", ""], ["150", "2 s", "", ""], ["220", "2 s", "", ""]], [CW * 0.2, CW * 0.18, CW * 0.31, CW * 0.31]))
    s.append(Spacer(1, 8))
    s.append(P("Ir derecho y girar (misiones 5 y 6)", h2))
    s.append(tabla_vacia(["Prueba", "velocidad izq", "velocidad der", "¿Fue derecho?"], [["1", "", "", ""], ["2", "", "", ""], ["3", "", "", ""], ["4", "", "", ""]], [CW * 0.16, CW * 0.28, CW * 0.28, CW * 0.28]))
    s.append(Spacer(1, 6))
    s.append(tabla_vacia(["Giro", "Tiempo que funcionó", "Notas"], [["Un cuarto de vuelta", "", ""], ["Media vuelta", "", ""]], [CW * 0.3, CW * 0.3, CW * 0.4]))
    s.append(Spacer(1, 8))
    s.append(P("Mis números mágicos de Roli", h2))
    s.append(Paragraph("Anoten acá los valores que descubrieron. ¡Les van a servir en el nivel 4!", small))
    s.append(Spacer(1, 4))
    s.append(tabla_vacia(["Qué es", "Valor"], [["Avance de 1 segundo a velocidad 90", ""], ["Velocidad izquierda para ir derecho", ""], ["Velocidad derecha para ir derecho", ""], ["Tiempo del giro de un cuarto de vuelta", ""]], [CW * 0.65, CW * 0.35]))
    s.append(PageBreak())

    # ---------- Para el adulto ----------
    s.append(banner("Para el adulto: qué aprenden y cómo acompañar", bg=TEAL_D))
    s.append(Spacer(1, 8))
    s.append(P("Qué se aprende en este nivel", h2))
    s += bullets([
        "<b>Parámetros:</b> una orden puede llevar un dato (“adelante <b>2</b>”). Es la base de casi toda la programación.",
        "<b>Variables:</b> la velocidad es un valor guardado que se puede cambiar y que Roli recuerda hasta que se apaga.",
        "<b>Medir y estimar:</b> proporcionalidad (el doble de tiempo, el doble de distancia, más o menos), unidades, tablas.",
        "<b>Calibrar:</b> el mundo real no es exacto. Las ruedas, el piso y las baterías cambian los resultados, y se ajusta probando.",
        "<b>Planificar antes de ejecutar:</b> escribir los pasos en papel y después probarlos.",
        "<b>Depurar:</b> cuando algo falla, cambiar una sola cosa y volver a probar.",
    ])
    s.append(Spacer(1, 8))
    s.append(P("Preguntas para conversar con ellos", h2))
    s += bullets([
        "¿Por qué crees que no avanzó lo mismo las dos veces que escribimos lo mismo?",
        "¿Qué pasa si las baterías están casi vacías? ¿Cómo lo podríamos comprobar?",
        "Si tuvieras que decirle a un amigo cómo llegar a la cocina, ¿qué órdenes usarías?",
        "¿Preferís ir lento y exacto o rápido y aproximado? ¿Cuándo conviene cada uno?",
    ])
    s.append(Spacer(1, 8))
    s.append(P("Cómo acompañar", h2))
    s += bullets([
        "Dejen que prueben y se equivoquen. Preguntar “¿qué podrías cambiar?” ayuda más que dar la respuesta.",
        "Rotar los turnos: uno escribe, el otro mide y anota.",
        "El mejor orden de las misiones: 1, 2, 3 · 5, 6, 7 · 8, 9, 10. La 4 y la 11 son juegos para cerrar.",
        "Las <b>cuatro</b> medidas que anotaron en “Mis números mágicos” se pueden usar directamente en el nivel 4.",
    ])
    s.append(Spacer(1, 8))
    s.append(callout("¿CUÁNDO PASAR AL NIVEL 4?",
                     "Cuando hayan hecho el cuadrado (misión 7) y puedan explicar con sus palabras para qué sirve el número que va después de <b>adelante</b>. "
                     "En el nivel 4 Roli aprende a <b>guardar una lista de pasos</b> y repetirla solo: justo lo que hicieron a mano en las misiones 7 y 8.", bg=MINT, color=TEAL))
    s.append(Spacer(1, 8))
    s.append(callout("SEGURIDAD", "Roli siempre se frena al terminar el tiempo y <b>parar</b> funciona en cualquier momento. Aun así, mantengan el espacio libre de personas, mascotas y escaleras mientras anda.", bg=colors.HexColor("#FDE7E4"), color=RED))

    doc.build(s)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "guia3.pdf")
