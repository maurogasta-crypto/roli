# Cómo se regeneran los PDFs

`make_manual.py` arma `Roli_manual_Yacko_y_Kala.pdf` y `make_guia3.py` arma `Roli_guia_nivel3.pdf`, los dos con `reportlab` y la tipografía DejaVu. `make_pdf.py` trae los estilos y ayudas que comparten. `img/` son las fotos de Roli que usa el manual.

Los scripts se escribieron con rutas de la sesión donde se hicieron (`/home/claude/pdfsrc`, `/home/claude/manual/img/`). Para regenerar, hay que cambiar esas rutas por las de esta carpeta.

**Los PDFs están atrasados respecto del firmware.** No mencionan el sensor trasero, `explorar` con barrido y elección del camino más largo, `girar`, `zigzag` ni el empujón de arranque, y el manual dice que hay 9 pines libres. Si se regeneran, actualizar primero el texto.
