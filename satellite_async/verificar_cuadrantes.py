import json
from utils import load_coord_data
from config import PIXELES_MUNICIPIOS

def verificar_cuadrantes():
    """Verifica los cuadrantes de los municipios"""
    
    municipios = ["azcapotzalco", "iztapalapa"]
    
    print("🔍 Verificando cuadrantes de municipios...")
    
    for municipio in municipios:
        try:
            coord_data = load_coord_data(municipio, PIXELES_MUNICIPIOS)
            print(f"✅ {municipio}: {coord_data.cuadrante}")
        except Exception as e:
            print(f"❌ {municipio}: Error - {e}")
    
    # También verificar todos los municipios en el JSON
    print(f"\n📊 Verificando todos los municipios en el JSON...")
    
    try:
        with open(PIXELES_MUNICIPIOS, 'r') as f:
            data = json.load(f)
        
        cuadrantes = {}
        for nombre_municipio, municipio_data in data.items():
            nombre = municipio_data['nombre']
            cuadrante = municipio_data['cuadrante']
            
            if cuadrante not in cuadrantes:
                cuadrantes[cuadrante] = []
            cuadrantes[cuadrante].append(nombre)
        
        print(f"📈 Distribución por cuadrantes:")
        for cuadrante, municipios_list in cuadrantes.items():
            print(f"  - {cuadrante}: {len(municipios_list)} municipios")
            if len(municipios_list) <= 5:
                print(f"    Municipios: {', '.join(municipios_list)}")
            else:
                print(f"    Municipios: {', '.join(municipios_list[:3])}... y {len(municipios_list)-3} más")
        
    except Exception as e:
        print(f"❌ Error leyendo JSON: {e}")

if __name__ == "__main__":
    verificar_cuadrantes() 