import json
from utils import load_coord_data
from config import PIXELES_MUNICIPIOS

def debug_coordenadas_multiples():
    """Debuggea las coordenadas de múltiples municipios"""
    
    municipios = ["azcapotzalco", "iztapalapa", "coyoacan"]
    
    print("🔍 Verificando coordenadas de múltiples municipios...")
    
    coordenadas_municipios = {}
    
    for municipio in municipios:
        try:
            coord_data = load_coord_data(municipio, PIXELES_MUNICIPIOS)
            coordenadas_municipios[municipio] = {
                'cuadrante': coord_data.cuadrante,
                'coordenadas': coord_data.coordenadas_pixeles,
                'total': len(coord_data.coordenadas_pixeles)
            }
            print(f"✅ {municipio}: {coord_data.cuadrante} - {len(coord_data.coordenadas_pixeles)} coordenadas")
        except Exception as e:
            print(f"❌ {municipio}: Error - {e}")
    
    # Verificar si hay coordenadas duplicadas
    print(f"\n🔍 Verificando coordenadas duplicadas...")
    
    for i, municipio1 in enumerate(municipios):
        for municipio2 in municipios[i+1:]:
            if municipio1 in coordenadas_municipios and municipio2 in coordenadas_municipios:
                coords1 = set(map(tuple, coordenadas_municipios[municipio1]['coordenadas']))
                coords2 = set(map(tuple, coordenadas_municipios[municipio2]['coordenadas']))
                
                # Calcular intersección
                interseccion = coords1.intersection(coords2)
                porcentaje1 = len(interseccion) / len(coords1) * 100
                porcentaje2 = len(interseccion) / len(coords2) * 100
                
                print(f"📊 {municipio1} vs {municipio2}:")
                print(f"   - {municipio1}: {len(coords1)} coordenadas")
                print(f"   - {municipio2}: {len(coords2)} coordenadas")
                print(f"   - Intersección: {len(interseccion)} coordenadas")
                print(f"   - Porcentaje {municipio1}: {porcentaje1:.1f}%")
                print(f"   - Porcentaje {municipio2}: {porcentaje2:.1f}%")
                
                if len(interseccion) > 0:
                    print(f"   - Primeras 5 coordenadas compartidas: {list(interseccion)[:5]}")
                
                if len(interseccion) == len(coords1) and len(interseccion) == len(coords2):
                    print(f"   ⚠️ ¡ADVERTENCIA! Las coordenadas son IDÉNTICAS")
                elif len(interseccion) > 0:
                    print(f"   ⚠️ Hay coordenadas compartidas")
                else:
                    print(f"   ✅ No hay coordenadas compartidas")
                print()
    
    # Mostrar algunas coordenadas de ejemplo
    print(f"📋 Ejemplos de coordenadas:")
    for municipio in municipios:
        if municipio in coordenadas_municipios:
            coords = coordenadas_municipios[municipio]['coordenadas']
            print(f"   - {municipio}: {coords[:5]}... (total: {len(coords)})")

if __name__ == "__main__":
    debug_coordenadas_multiples() 