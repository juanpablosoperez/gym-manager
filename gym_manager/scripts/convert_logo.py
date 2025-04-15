from cairosvg import svg2png
import os

def convert_logo():
    script_dir = os.path.dirname(os.path.dirname(__file__))
    svg_path = os.path.join(script_dir, 'assets', 'logo.svg')
    png_path = os.path.join(script_dir, 'assets', 'logo.png')
    
    # Asegurarse de que el directorio assets existe
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    
    # Convertir SVG a PNG
    with open(svg_path, 'rb') as svg_file:
        svg2png(file_obj=svg_file, write_to=png_path, output_width=200, output_height=200)

if __name__ == "__main__":
    convert_logo() 