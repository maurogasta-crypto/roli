# Cómo se regeneran los PDFs

`make_manual.py` arma `Roli_manual_Yacko_y_Kala.pdf` y `make_guia3.py` arma `Roli_guia_nivel3.pdf`, los dos con `reportlab` y la tipografía DejaVu. `make_pdf.py` trae los estilos y ayudas que comparten. `img/` son las fotos de Roli que usa el manual.

`make_guia6.py` arma `Roli_guia_nivel6.pdf` (ver, girar justo y decidir solo), con los mismos estilos que la del nivel 3.

Regenerar (desde esta carpeta, sin tocar rutas; hace falta `reportlab`, `Pillow` y la letra DejaVu, y si la computadora no trae la cursiva se usa la recta):

```
python3 make_manual.py ../Roli_manual_Yacko_y_Kala.pdf
python3 make_guia3.py  ../Roli_guia_nivel3.pdf
python3 make_guia6.py  ../Roli_guia_nivel6.pdf
```

**Al día con el firmware del 18-nov-2026** (el cableado nuevo: servo en el 7 y al 5V del L298N, encoders en 2 y 3, zumbador en 8, medidor de batería; la guía de armado es `docs/CABLEADO.md`; antes, el 14-nov: sensor trasero, zigzag, empujón y enderezado, `explorar`, `girar`, `calibrar`, `desvio` y la `sesion` de la consola). Lo que se escribe en la consola sale de la ayuda de `firmware/roli_programa.ino`: si cambia una palabra allá, hay que cambiar el texto acá y regenerar los PDF.
