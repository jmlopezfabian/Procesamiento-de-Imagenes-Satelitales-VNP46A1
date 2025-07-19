import numpy as np

def aumentar_imagen(image_matrix, factor_escala):
    return np.kron(image_matrix, np.ones((factor_escala, factor_escala)))

def recortar_imagen(image_matrix, coordenadas_municipio, upper_left, factor_escala):
    resolucion_x = 10 / image_matrix.shape[1]
    resolucion_y = 10 / image_matrix.shape[0]
    x_pixels = (coordenadas_municipio[:, 0] - upper_left[0]) / resolucion_x
    y_pixels = (upper_left[1] - coordenadas_municipio[:, 1]) / resolucion_y
    recorte_y = (np.ceil(y_pixels.min()).astype(int)-1, np.ceil(y_pixels.max()).astype(int)+1)
    recorte_x = (np.ceil(x_pixels.min()).astype(int)-1, np.ceil(x_pixels.max()).astype(int)+1)
    image_matrix_recortada = image_matrix[recorte_y[0]:recorte_y[1], recorte_x[0]:recorte_x[1]]
    if factor_escala == 1:
        imagen_aumentada = image_matrix_recortada
    else:
        imagen_aumentada = aumentar_imagen(image_matrix_recortada, factor_escala)
    nuevos_x_pixels = (x_pixels - recorte_x[0]) * factor_escala
    nuevos_y_pixels = (y_pixels - recorte_y[0]) * factor_escala
    return imagen_aumentada, nuevos_x_pixels, nuevos_y_pixels 