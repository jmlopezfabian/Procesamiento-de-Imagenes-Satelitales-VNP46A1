import numpy as np
import re

def left_right_coords(hdf_file):
    dataset_path = "HDFEOS INFORMATION/StructMetadata.0"
    metadata = hdf_file[dataset_path][()].tobytes().decode("utf-8")
    upper_left_match = re.search(r"UpperLeftPointMtrs=\\(([-\\d.]+),([-.]+)\\)", metadata)
    lower_right_match = re.search(r"LowerRightMtrs=\\(([-\\d.]+),([-.]+)\\)", metadata)
    conversion = 1_000_000
    if upper_left_match and lower_right_match:
        upper_left_coords = (
            float(upper_left_match.group(1)) / conversion,
            float(upper_left_match.group(2)) / conversion,
        )
        lower_right_coords = (
            float(lower_right_match.group(1)) / conversion,
            float(lower_right_match.group(2)) / conversion,
        )
        return upper_left_coords, lower_right_coords
    print("No se pudieron extraer las coordenadas.")
    return None, None

def polygon_centroid(vertices):
    n = len(vertices)
    A = 0
    Cx = 0
    Cy = 0
    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        A += cross
        Cx += (x0 + x1) * cross
        Cy += (y0 + y1) * cross
    A *= 0.5
    Cx /= (6 * A)
    Cy /= (6 * A)
    return (Cx, Cy) 