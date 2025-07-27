import numpy as np
from typing import Tuple, List
from utils import distancia_puntos, polygon_centroid, es_borde

def aumentar_imagen(image_matrix: np.ndarray, factor_escala: int) -> np.ndarray:
    """Aumenta el tamaño de una imagen por un factor de escala"""
    imagen_aumentada = np.kron(image_matrix, np.ones((factor_escala, factor_escala)))
    return imagen_aumentada

def recortar_imagen(image_matrix: np.ndarray, coordenadas_municipio: np.ndarray, 
                   upper_left: Tuple[float, float], factor_escala: int = 1) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Recorta una imagen según las coordenadas del municipio y aplica factor de escala.
    
    Args:
        image_matrix: Matriz de la imagen original
        coordenadas_municipio: Coordenadas del municipio
        upper_left: Coordenadas de la esquina superior izquierda
        factor_escala: Factor de escala para aumentar la imagen
        
    Returns:
        Tuple con (imagen_aumentada, nuevos_x_pixels, nuevos_y_pixels)
    """
    # 1. Calcular resolución en la imagen original
    resolucion_x = 10 / image_matrix.shape[1]
    resolucion_y = 10 / image_matrix.shape[0]

    # 2. Convertir coordenadas a píxeles
    x_pixels = (coordenadas_municipio[:, 0] - upper_left[0]) / resolucion_x
    y_pixels = (upper_left[1] - coordenadas_municipio[:, 1]) / resolucion_y

    # 3. Definir área de recorte
    recorte_y = (np.ceil(y_pixels.min()).astype(int)-1, np.ceil(y_pixels.max()).astype(int)+1)
    recorte_x = (np.ceil(x_pixels.min()).astype(int)-1, np.ceil(x_pixels.max()).astype(int)+1)

    # 4. Recortar la imagen original
    image_matrix_recortada = image_matrix[recorte_y[0]:recorte_y[1], recorte_x[0]:recorte_x[1]]

    # 5. Aumentar imagen recortada
    if factor_escala == 1:
        imagen_aumentada = image_matrix_recortada
    else:
        imagen_aumentada = aumentar_imagen(image_matrix_recortada, factor_escala)

    # 6. Ajustar las coordenadas de los bordes según el factor de escala
    nuevos_x_pixels = (x_pixels - recorte_x[0]) * factor_escala
    nuevos_y_pixels = (y_pixels - recorte_y[0]) * factor_escala
    return imagen_aumentada, nuevos_x_pixels, nuevos_y_pixels

def completar_bordes(nuevos_x_pixels: np.ndarray, nuevos_y_pixels: np.ndarray) -> List[Tuple[int, int]]:
    """
    Completa los bordes del polígono interpolando puntos entre vértices distantes.
    
    Args:
        nuevos_x_pixels: Coordenadas X de los píxeles
        nuevos_y_pixels: Coordenadas Y de los píxeles
        
    Returns:
        Lista de coordenadas completas del borde
    """
    coordenadas_bordes = list()
    
    for i in range(len(nuevos_x_pixels) - 1):
        if not (nuevos_x_pixels[i], nuevos_y_pixels[i]) in coordenadas_bordes:
            coordenadas_bordes.append((int(nuevos_x_pixels[i]), int(nuevos_y_pixels[i])))
        
        distancia = distancia_puntos((nuevos_x_pixels[i], nuevos_y_pixels[i]), 
                                   (nuevos_x_pixels[i+1], nuevos_y_pixels[i+1]))
        
        if distancia > 1:
            pendiente = (nuevos_y_pixels[i+1] - nuevos_y_pixels[i]) / (nuevos_x_pixels[i+1] - nuevos_x_pixels[i])
            recta = lambda x: pendiente * (x - nuevos_x_pixels[i]) + nuevos_y_pixels[i]
            x = np.linspace(nuevos_x_pixels[i], nuevos_x_pixels[i+1], 100)
            y = recta(x)
            
            for j in range(len(x)):
                if not (nuevos_x_pixels[i], nuevos_y_pixels[i]) in coordenadas_bordes:
                    coordenadas_bordes.append((int(x[j]), int(y[j])))

    if not (nuevos_x_pixels[-1], nuevos_y_pixels[-1]) in coordenadas_bordes:
        coordenadas_bordes.append((int(nuevos_x_pixels[-1]), int(nuevos_y_pixels[-1])))

    return list(coordenadas_bordes)

def get_pixeles(imagen: np.ndarray, centroide: Tuple[float, float], 
                bordes: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Obtiene todos los píxeles dentro del polígono usando flood fill desde el centroide.
    
    Args:
        imagen: Matriz de la imagen
        centroide: Coordenadas del centroide del polígono
        bordes: Lista de coordenadas que forman el borde del polígono
        
    Returns:
        Lista de coordenadas de píxeles dentro del polígono
    """
    x_centroide, y_centroide = centroide
    
    matriz_visitados = np.zeros(imagen.shape, dtype=bool)
    matriz_visitados[int(y_centroide), int(x_centroide)] = True
    pixeles_imagen = [(int(x_centroide), int(y_centroide))]

    queue = [(int(x_centroide), int(y_centroide))]
    while queue:
        x, y = queue.pop(0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x_nuevo = x + dx
            y_nuevo = y + dy
            if (0 <= x_nuevo < imagen.shape[1] and
                0 <= y_nuevo < imagen.shape[0] and
                not matriz_visitados[y_nuevo, x_nuevo] and
                not es_borde(x_nuevo, y_nuevo, bordes)):
                matriz_visitados[y_nuevo, x_nuevo] = True
                queue.append((x_nuevo, y_nuevo))
                pixeles_imagen.append((x_nuevo, y_nuevo))
    
    return pixeles_imagen 