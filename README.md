# IMG to SVG Converter — Halftone y modelos 3D

Herramientas en Python para convertir imágenes **JPG/PNG** en ilustraciones vectoriales **SVG con efecto halftone** (una trama de puntos que reproduce luces y sombras). También incluye dos formas de transformar esos SVG en relieves **STL** para trabajar con modelos 3D.

El conversor gráfico parte del trabajo original de **DE Hammer** ([publicación original en Thingiverse](https://www.thingiverse.com/thing:5183381)). El repositorio conserva las adaptaciones y herramientas posteriores atribuidas a **Avtomat Agentics (2025)**.

## Qué incluye

| Archivo | Función |
| --- | --- |
| [`halftone_gui_converter.py`](halftone_gui_converter.py) | Conversor gráfico de JPG/PNG a SVG halftone. Sugiere parámetros según el análisis de la imagen. |
| [`halftone_gui_art_converter.py`](halftone_gui_art_converter.py) | Variante gráfica que añade detección del estilo de imagen y perfiles para dibujar distintos patrones. |
| [`create_halftone_folders.py`](create_halftone_folders.py) | Crea las carpetas auxiliares de trabajo. |
| [`install_halftone_dependencies.py`](install_halftone_dependencies.py) | Instalador auxiliar de algunos paquetes; **no cubre todas las dependencias** de los programas. |
| [`scad_converter.py`](scad_converter.py) | Convierte los SVG de la carpeta `SVG` en modelos `.scad` de OpenSCAD. |
| [`scad_to_stl_randerer.py`](scad_to_stl_randerer.py) | Renderiza los modelos `.scad` en `.stl` utilizando OpenSCAD. El nombre del archivo conserva su errata original. |
| [`svg_to_stl_converter.py`](svg_to_stl_converter.py) | Alternativa directa de SVG a STL mediante Trimesh, sin pasar por OpenSCAD. |

## Instalación

Se recomienda Python 3.8 o posterior. La aplicación gráfica usa **Tkinter**, que debe estar disponible en la instalación de Python.

Desde la carpeta del repositorio:

```bash
python -m pip install pillow pycairo svglib reportlab rlPyCairo opencv-python numpy trimesh
```

Estas son las bibliotecas externas identificadas en los scripts. La instalación puede variar según el sistema operativo y la versión de Python. El script `install_halftone_dependencies.py` instala o actualiza `pip`, `pycairo`, `svglib`, `reportlab` y `Pillow`, pero **no instala OpenCV, NumPy ni Trimesh**, por lo que no sustituye al comando anterior.

Para la ruta `SCAD → STL` hace falta además instalar **OpenSCAD**. El script tiene configurada la ruta de Windows `C:\Program Files\OpenSCAD\openscad.exe`; si se instala en otra ubicación, hay que ajustar `OPENSCAD_CMD` dentro de `scad_to_stl_randerer.py`.

## Uso básico: imagen a SVG

1. Ejecuta uno de los conversores gráficos:
   ```bash
   python halftone_gui_converter.py
   ```
   o bien:
   ```bash
   python halftone_gui_art_converter.py
   ```
2. Importa una imagen JPG o PNG.
3. Revisa las sugerencias automáticas de tamaño, detalle y espaciado; puedes cambiarlas.
4. Elige el modo de color. En la variante artística también puedes probar los estilos de trama.
5. Pulsa **Convert Image**.
6. El SVG resultante se guarda en `SVG/`. La aplicación genera además imágenes auxiliares y una vista previa en `IMAGE/`.

Los conversores crean automáticamente las carpetas básicas `IMAGE`, `SAVE FOLDER`, `JSON` y `SVG` junto a los scripts. También puedes prepararlas con:

```bash
python create_halftone_folders.py
```

**Nota sobre compatibilidad:** el botón que abre la carpeta SVG usa `os.startfile`, una función específica de Windows. El resto del programa no queda automáticamente garantizado en otros sistemas.

## Pasar el SVG a un modelo 3D

Hay **dos rutas alternativas**, no dos pasos obligatorios:

**Ruta A — con OpenSCAD**

```bash
python scad_converter.py
python scad_to_stl_randerer.py
```

Lee `SVG/`, genera archivos en `SCAD/` y después renderiza STL en `STL/`.

**Ruta B — directa con Python**

```bash
python svg_to_stl_converter.py
```

Lee `SVG/` y guarda los STL directamente en `STL_3D/` mediante Trimesh.

**Atención:** los conversores 3D cambian el nombre de los archivos procesados añadiendo `_converted` para no repetirlos. No ejecutes ambas rutas sobre los mismos SVG sin preparar copias: la primera ruta puede marcarlos como procesados y la segunda omitirlos.

Para ver las carpetas, los detalles y las limitaciones, consulta la [guía de funcionamiento](docs/funcionamiento.md).

## Estado y limitaciones

- Se conserva el código original y su estructura; no se ha realizado una refactorización.
- Los archivos `IMAGE/IMPORT IMAGE.png` y `IMAGE/SVG IMAGE.png` son salidas generadas por la aplicación, **no imágenes de ejemplo incluidas** en GitHub.
- La conversión 3D está orientada a SVG con tramas de puntos; no es un conversor universal de cualquier SVG.
- No se han ejecutado pruebas completas de conversión ni de impresión 3D.
- Los resultados STL deben comprobarse en un visor o laminador antes de imprimir.

## Créditos y licencia

**Autor original:** [DE Hammer](https://www.thingiverse.com/dehammer) — [proyecto original](https://www.thingiverse.com/thing:5183381).

**Adaptaciones, herramientas y documentación:** Avtomat Agentics (2025), según los créditos del repositorio.

Licencia conservada: [Creative Commons Attribution–ShareAlike 4.0 International](LICENSE.txt) (CC BY-SA 4.0).
