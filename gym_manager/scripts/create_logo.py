from PIL import Image, ImageDraw
import os

def create_logo():
    # Crear una imagen de 200x200 píxeles con fondo transparente
    img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Color azul similar al de la imagen
    blue_color = (33, 150, 243, 255)  # RGB + Alpha
    
    # Dibujar la barra central
    draw.rectangle([40, 90, 160, 110], fill=blue_color)
    
    # Dibujar los círculos
    def draw_circle(x, y, r):
        draw.ellipse([x-r, y-r, x+r, y+r], fill=blue_color)
    
    # Círculos principales
    draw_circle(30, 100, 24)
    draw_circle(170, 100, 24)
    
    # Barras laterales
    draw.rectangle([10, 94, 50, 106], fill=blue_color)
    draw.rectangle([150, 94, 190, 106], fill=blue_color)
    
    # Guardar la imagen
    script_dir = os.path.dirname(os.path.dirname(__file__))
    png_path = os.path.join(script_dir, 'assets', 'logo.png')
    
    # Asegurarse de que el directorio assets existe
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    
    img.save(png_path, 'PNG')

if __name__ == "__main__":
    create_logo() 