import streamlit as st
import re
from fpdf import FPDF
import base64

# DICCIONARIO DE CODIGOS
comentarios_por_lenguaje = {
    'c': {
        'line': re.compile(r'^\s*//'),
        'block_start': re.compile(r'^\s*/\*'),
        'block_end': re.compile(r'\*/')
    },
    'python': {
        'line': re.compile(r'^\s*#'),
        'block_start': None,
        'block_end': None
    },
    'java': {
        'line': re.compile(r'^\s*//'),
        'block_start': re.compile(r'^\s*/\*'),
        'block_end': re.compile(r'\*/')
    },
   
}

def detectar_lenguaje(codigo):
    if re.search(r'^\s*#', codigo, re.MULTILINE):
        return 'python'
    elif re.search(r'^\s*//', codigo, re.MULTILINE) or re.search(r'^\s*/\*', codigo, re.MULTILINE):
        if re.search(r'\*/', codigo):
            return 'c'
        return 'java'
    else:
        return 'c'  

def contar_lineas(codigo, lenguaje):
    patrones = comentarios_por_lenguaje[lenguaje]
    lineas = codigo.split('\n')
    loc = len(lineas)
    eloc = 0
    cloc = 0
    bloc = 0
    en_comentario_bloque = False

    for linea in lineas:
        linea_strip = linea.strip()
        if len(linea_strip) == 0:
            bloc += 1
        elif en_comentario_bloque:
            cloc += 1
            if patrones['block_end'] and patrones['block_end'].search(linea_strip):
                en_comentario_bloque = False
        elif patrones['line'] and patrones['line'].search(linea_strip):
            cloc += 1
        elif patrones['block_start'] and patrones['block_start'].search(linea_strip):
            cloc += 1
            en_comentario_bloque = True
        else:
            eloc += 1

    ccr = cloc / eloc if eloc != 0 else 0
    ncloc = loc - cloc

    return {
        'LOC': loc,
        'ELOC': eloc,
        'CLOC': cloc,
        'CCR': ccr,
        'NCLOC': ncloc,
        'BLOC': bloc
    }

def generar_reporte(metricas):
    reporte = (
        f"Lines of Code (LOC): {metricas['LOC']}\n"
        f"Executable Lines of Code (ELOC): {metricas['ELOC']}\n"
        f"Comment Lines of Code (CLOC): {metricas['CLOC']}\n"
        f"Comment to Code Ratio (CCR): {metricas['CCR']:.2f}\n"
        f"Non-Comment Lines of Code (NCLOC): {metricas['NCLOC']}\n"
        f"Blank Lines of Code (BLOC): {metricas['BLOC']}\n"
    )
    return reporte

def generar_mensaje_evaluacion(metricas):
    if metricas['CLOC'] == 0:
        mensaje = (
            f"Cuadro 1: Evaluación de métricas LOC del archivo de código. La fórmula para calcular la Comment to Code Ratio "
            f"(CCR) se define como el cociente entre las líneas de comentario (CLOC) y las líneas ejecutables de código (ELOC), "
            f"proporcionando una medida de la proporción de comentarios respecto al código ejecutable.\n"
            f"Las métricas LOC nos proporcionan información valiosa sobre el tamaño y la estructura del código. El número total "
            f"de líneas de código (LOC) es {metricas['LOC']}, mientras que las líneas ejecutables (ELOC) son {metricas['ELOC']}. "
            f"Es notable que no hay líneas de comentarios (CLOC), lo que resulta en una relación de comentarios por línea de código (CCR) de 0. "
            f"Esto sugiere que el código puede carecer de documentación interna, lo cual puede dificultar su mantenibilidad y comprensión por parte de otros desarrolladores.\n"
            f"Además, el número de líneas en blanco (BLOC) es {metricas['BLOC']}, lo cual indica que hay una cantidad mínima de espacios en blanco, "
            f"posiblemente afectando la legibilidad."
        )
    else:
        if metricas['BLOC'] > 0.4 * metricas['LOC']:
            mensaje = (
                f"Cuadro 1: Evaluación de métricas LOC del archivo de código. La fórmula para calcular la Comment to Code Ratio "
                f"(CCR) se define como el cociente entre las líneas de comentario (CLOC) y las líneas ejecutables de código (ELOC), "
                f"proporcionando una medida de la proporción de comentarios respecto al código ejecutable.\n"
                f"Las métricas LOC nos proporcionan información valiosa sobre el tamaño y la estructura del código. El número total "
                f"de líneas de código (LOC) es {metricas['LOC']}, mientras que las líneas ejecutables (ELOC) son {metricas['ELOC']}. "
                f"Es notable que hay líneas de comentarios (CLOC), lo que resulta en una relación de comentarios por línea de código (CCR) de {metricas['CCR']:.2f}. "
                f"Esto ayuda a la documentación interna, facilitando su mantenibilidad y comprensión por parte de otros desarrolladores.\n"
                f"Además, el número de líneas en blanco (BLOC) es {metricas['BLOC']}, lo cual indica que hay una cantidad mayor al formato de un código aceptable de espacios en blanco, "
                f"posiblemente afectando la legibilidad."
            )
        elif metricas['BLOC'] < 0.2 * metricas['LOC']:
            mensaje = (
                f"Cuadro 1: Evaluación de métricas LOC del archivo de código. La fórmula para calcular la Comment to Code Ratio "
                f"(CCR) se define como el cociente entre las líneas de comentario (CLOC) y las líneas ejecutables de código (ELOC), "
                f"proporcionando una medida de la proporción de comentarios respecto al código ejecutable.\n"
                f"Las métricas LOC nos proporcionan información valiosa sobre el tamaño y la estructura del código. El número total "
                f"de líneas de código (LOC) es {metricas['LOC']}, mientras que las líneas ejecutables (ELOC) son {metricas['ELOC']}. "
                f"Es notable que hay líneas de comentarios (CLOC), lo que resulta en una relación de comentarios por línea de código (CCR) de {metricas['CCR']:.2f}. "
                f"Esto ayuda a la documentación interna, facilitando su mantenibilidad y comprensión por parte de otros desarrolladores.\n"
                f"Además, el número de líneas en blanco (BLOC) es {metricas['BLOC']}, lo cual indica que hay una cantidad mínima de espacios en blanco, "
                f"posiblemente afectando la legibilidad."
            )
        else:
            mensaje = (
                f"Cuadro 1: Evaluación de métricas LOC del archivo de código. La fórmula para calcular la Comment to Code Ratio "
                f"(CCR) se define como el cociente entre las líneas de comentario (CLOC) y las líneas ejecutables de código (ELOC), "
                f"proporcionando una medida de la proporción de comentarios respecto al código ejecutable.\n"
                f"Las métricas LOC nos proporcionan información valiosa sobre el tamaño y la estructura del código. El número total "
                f"de líneas de código (LOC) es {metricas['LOC']}, mientras que las líneas ejecutables (ELOC) son {metricas['ELOC']}. "
                f"Es notable que hay líneas de comentarios (CLOC), lo que resulta en una relación de comentarios por línea de código (CCR) de {metricas['CCR']:.2f}. "
                f"Esto ayuda a la documentación interna, facilitando su mantenibilidad y comprensión por parte de otros desarrolladores.\n"
                f"Además, el número de líneas en blanco (BLOC) es {metricas['BLOC']}, lo cual indica que hay una cantidad aceptable de espacios en blanco, "
                f"lo que facilita la legibilidad."
            )
    return mensaje


def generar_pdf(codigo, metricas, mensaje_evaluacion, semestre, grupo):
    pdf = FPDF()
    
    margen_superior = 25
    margen_inferior = 25
    margen_izquierdo = 25
    margen_derecho = 25

    pdf.set_margins(left=margen_izquierdo, top=margen_superior, right=margen_derecho)
    pdf.set_auto_page_break(auto=True, margin=margen_inferior)
    
    pdf.add_page()

    pdf.set_font("Arial", size=16)
    
    ancho_pagina = pdf.w
    
    posicion_y = (pdf.h - pdf.font_size) / 2.0  

    pdf.multi_cell(ancho_pagina, 10, txt="Facultad de Ingeniería Estadística e Informática                               ", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 10)  

    pdf.multi_cell(ancho_pagina, 10, txt="Escuela Profesional de Ingeniería Estadística e Informática", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 10)  

    pdf.set_xy((pdf.w - 40) / 2, pdf.get_y())  
    pdf.image('una.png', x=pdf.get_x(), y=pdf.get_y(), w=40)
    pdf.ln(50)
    pdf.set_font("Arial", size=14)
    pdf.multi_cell(ancho_pagina, 10, txt="Lenguajes de Programación I                               ", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 10)  

    pdf.set_font("Arial", size=20)
    pdf.multi_cell(ancho_pagina, 10, txt="Evaluación del Código Fuente", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 15)  

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(ancho_pagina, 10, txt="Profesor: Fred Torres Cruz", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 10)  
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(ancho_pagina, 10, txt="Estudiante: Roberth Carlos Gonzales Mauricio", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 10)  #

    pdf.multi_cell(ancho_pagina, 10, txt=f"Fecha: 20 de junio de 2024", border=0, align='C')
    pdf.set_xy(0, pdf.get_y() + 10)  # 

    pdf.multi_cell(ancho_pagina, 10, txt=f"Semestre: {semestre}  Grupo: {grupo}", border=0, align='C')
    pdf.ln(20)  

   
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    
    pdf.multi_cell(0, 10, "Introducción a la Evaluación del Código Fuente\n"
                        "Se realizó la evaluación del código fuente de un archivo utilizando las métricas de Lines of Code (LOC). "
                        "Estas métricas nos permiten evaluar la calidad y mantenibilidad del código.")
    pdf.ln(10)
    
   
    pdf.multi_cell(0, 10, "Evaluación del Código Fuente\n"
                        "Para evaluar el tamaño y la calidad del código fuente desarrollado, hemos aplicado métricas de Lines of Code (LOC). "
                        "A continuación, presentamos una tabla con los resultados obtenidos del archivo de código evaluado.")
    pdf.ln(10)

 
    pdf.multi_cell(0, 10, mensaje_evaluacion)
    pdf.ln(100)  

   
    pdf.multi_cell(0, 10, "Métricas de Código Fuente")
    pdf.multi_cell(0, 10, generar_reporte(metricas))
    pdf.ln(10)

    
    pdf.multi_cell(0, 10, "Código Fuente")
    pdf.set_font("Courier", size=10)
    pdf.multi_cell(0, 10, codigo)
    
    return pdf

def descargar_pdf(pdf):
    pdf_output = pdf.output(dest="S").encode("latin1")
    b64_pdf = base64.b64encode(pdf_output).decode("utf-8")
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="reporte_codigo.pdf">Descargar reporte en PDF</a>'
    return href

def main():
    st.title("Evaluación de Código Fuente")

    archivo = st.file_uploader("Selecciona un archivo de código fuente", type=['py', 'c', 'h', 'java', 'cpp', 'js', 'html', 'css'])
    semestre = "3ro"
    grupo = "B"
    
    if archivo is not None:
        codigo = archivo.read().decode('utf-8')
        lenguaje = detectar_lenguaje(codigo)
        if lenguaje is None:
            st.error("Lenguaje no soportado o no reconocido.")
        else:
            metricas = contar_lineas(codigo, lenguaje)
            reporte = generar_reporte(metricas)
            mensaje_evaluacion = generar_mensaje_evaluacion(metricas)
            
            st.text_area("Código Fuente", codigo, height=300)

            st.subheader("Introducción a la Evaluación del Código Fuente")
            st.write("""
            Se realizó la evaluación del código fuente de un archivo utilizando las métricas de Lines of Code (LOC). Estas métricas nos permiten evaluar la calidad y mantenibilidad del código.
            """)

            st.subheader("Evaluación del Código Fuente")
            st.write("""
            Para evaluar el tamaño y la calidad del código fuente desarrollado, hemos aplicado métricas de Lines of Code (LOC). A continuación, presentamos una tabla con los resultados obtenidos del archivo de código evaluado.
            """)
            
            st.subheader("Cuadro 1: Evaluación de métricas LOC")
            st.text(mensaje_evaluacion)

            st.subheader("Métricas de Código Fuente")
            st.text(reporte)

            pdf = generar_pdf(codigo, metricas, mensaje_evaluacion, semestre, grupo)
            st.markdown(descargar_pdf(pdf), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
