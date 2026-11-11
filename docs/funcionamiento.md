# Funcionamiento y archivos

## 1. Convertir imágenes en SVG halftone

Los dos programas gráficos leen una imagen JPG o PNG y la convierten en una trama de puntos. En lugar de dibujar cada píxel como un color plano, calculan valores de gris por zonas y generan figuras vectoriales de distinto tamaño. El conjunto reproduce las luces y sombras de la imagen original.

### Conversor principal

[`halftone_gui_converter.py`](../halftone_gui_converter.py)

- Interfaz gráfica con Tkinter.
- Importación de imágenes desde cualquier ubicación del equipo.
- Análisis automático de brillo, contraste, bordes y variaciones locales para sugerir parámetros.
- Ajustes manuales de tamaño de trabajo, borde, detalle, espaciado y color.
- Generación del SVG con Cairo.
- Vista previa PNG y archivos intermedios de procesamiento.

### Variante artística

[`halftone_gui_art_converter.py`](../halftone_gui_art_converter.py)

Parte del mismo conversor, pero añade funciones para **detectar el estilo visual** de la imagen, proponer un perfil y dibujar distintas formas de trama. Por tanto, no es simplemente un duplicado con otro nombre.

Ambos archivos conservan referencias a la versión 0.1 y al autor original en sus cabeceras. No se ha intentado reconstruir un historial de versiones que no esté documentado en el repositorio.

## 2. Carpetas de trabajo

Los scripts utilizan rutas relativas a la **ubicación de sus propios archivos**, no a una carpeta fija en el escritorio.

| Carpeta | Contenido |
| --- | --- |
| `IMAGE/` | Imagen importada y vista previa PNG de la trama SVG. |
| `SAVE FOLDER/` | Archivos auxiliares, incluida la imagen procesada en escala de grises. |
| `JSON/` | Datos intermedios y parámetros utilizados en la conversión. |
| `SVG/` | SVG generados por los conversores gráficos y entrada para las conversiones 3D. |
| `SCAD/` | Modelos intermedios de OpenSCAD. |
| `STL/` | STL renderizados desde SCAD. |
| `STL_3D/` | STL generados directamente desde SVG. |

Las cuatro primeras carpetas se crean al iniciar los conversores gráficos. Los programas 3D crean sus propias carpetas de entrada/salida si faltan.

## 3. Ruta 3D con OpenSCAD

### SVG → SCAD

[`scad_converter.py`](../scad_converter.py)

Recorre los archivos SVG pendientes de `SVG/`, interpreta su geometría de puntos y escribe un archivo SCAD por imagen en `SCAD/`. Representa los puntos como cilindros con una altura calculada mediante una curva de contraste.

Después de procesar un SVG, lo renombra añadiendo `_converted.svg`.

### SCAD → STL

[`scad_to_stl_randerer.py`](../scad_to_stl_randerer.py)

Busca modelos SCAD pendientes y llama a OpenSCAD desde Python para renderizar las mallas STL. Los guarda en `STL/` y renombra los SCAD tratados con `_converted.scad`.

La constante `OPENSCAD_CMD` apunta a `C:\Program Files\OpenSCAD\openscad.exe`. Es una ruta de Windows: puede requerir un cambio manual. El nombre `randerer` es el original del archivo.

## 4. Ruta 3D directa

[`svg_to_stl_converter.py`](../svg_to_stl_converter.py)

Alternativa que utiliza **NumPy y Trimesh** para generar el relieve STL directamente. El código contempla puntos descritos como elementos `circle` y como trazados `path` de Cairo. Ajusta dimensiones y alturas teniendo en cuenta los radios y la densidad local de puntos.

- Entrada: `SVG/`.
- Salida: `STL_3D/`.
- Los SVG procesados también se renombran con `_converted.svg`.

**Las dos rutas 3D comparten la misma carpeta de entrada y la misma convención de renombrado.** Si quieres comparar resultados, duplica previamente los SVG o restaura sus nombres antes de usar la otra ruta.

## 5. Preparación e instalación

[`create_halftone_folders.py`](../create_halftone_folders.py) crea `SAVE FOLDER`, `JSON`, `SVG`, `IMAGE` y `PYTHON`. Esta última carpeta la prepara el auxiliar, pero los scripts principales permanecen en la raíz del repositorio.

[`install_halftone_dependencies.py`](../install_halftone_dependencies.py) ejecuta `pip install --upgrade` para cinco paquetes. **No verifica de forma completa todas las dependencias** y puede continuar tras un fallo individual. Para preparar el entorno, consulta el comando de instalación del README.

## 6. Cuestiones a tener en cuenta

- El botón para abrir `SVG/` utiliza `os.startfile`, propio de Windows.
- Los SVG de entrada deben ajustarse a la geometría que esperan los conversores; los archivos SVG arbitrarios pueden no funcionar.
- La creación de modelos tridimensionales puede ser lenta o consumir mucha memoria si la trama contiene muchísimos puntos.
- Ejecutar las herramientas puede crear carpetas, generar archivos y **renombrar SVG o SCAD originales**.
- La licencia y la atribución al trabajo de DE Hammer deben mantenerse al reutilizar el proyecto.
- Esta guía describe el código disponible. No se ha comprobado su ejecución integral en una instalación nueva.
