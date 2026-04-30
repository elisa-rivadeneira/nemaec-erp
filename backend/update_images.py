#!/usr/bin/env python3
"""
Script para agregar imágenes de muestra a las comisarías que no las tienen.
Las URLs son de imágenes genéricas de comisarías peruanas.
"""

import sqlite3
import os

# Lista de URLs de imágenes de muestra de comisarías peruanas
# Estas son imágenes públicas de comisarías reales
SAMPLE_IMAGES = [
    # Imágenes de comisarías reales de Lima
    "https://portal.andina.pe/EDPfotografia3/Thumbnail/2019/05/31/000597607W.jpg",  # Comisaría moderna
    "https://portal.andina.pe/EDPfotografia3/Thumbnail/2019/11/21/000638851W.jpg",  # Comisaría nueva
    "https://portal.andina.pe/EDPfotografia3/Thumbnail/2020/06/17/000688926W.jpg",  # Comisaría PNP
    "https://elperuano.pe/fotografia//thumbnail/2021/10/27/000189289M.jpg",         # Comisaría Lima
    "https://elperuano.pe/fotografia//thumbnail/2021/02/18/000158959M.jpg",         # Comisaría remodelada
    "https://larepublica.pe/resizer/sRj2r-zG7MvQZK0HqiG-L0RKzXI=/1200x660/top/cloudfront-us-east-1.images.arcpublishing.com/gruporepublica/YYVMQXC4KFFDNJ7YVJUPMDQRK4.jpg",
    "https://gestion.pe/resizer/P1vJ6ZQ8VVV1dYvGZQnD6bTzH6g=/1200x675/smart/filters:format(jpeg):quality(75)/cloudfront-us-east-1.images.arcpublishing.com/elcomercio/V5WLZQMEPNFOHHMTVPFM5UJGVM.jpg",
    "https://www.gob.pe/uploads/document/file/2673745/standard_Comisaria_San_Borja.jpg",
    "https://portal.andina.pe/EDPfotografia3/Thumbnail/2021/03/18/000756489W.jpg",
    "https://portal.andina.pe/EDPfotografia3/Thumbnail/2022/01/17/000824845W.jpg"
]

def update_comisaria_images():
    """Actualiza las imágenes de las comisarías que no tienen una."""

    db_path = '/home/oem/Projects/nemaec-erp/backend/data/nemaec_erp.db'

    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Primero, obtener todas las comisarías sin imagen
    cursor.execute("SELECT id, nombre FROM comisarias WHERE foto_url IS NULL OR foto_url = ''")
    comisarias_sin_imagen = cursor.fetchall()

    print(f"📊 Se encontraron {len(comisarias_sin_imagen)} comisarías sin imagen")

    if comisarias_sin_imagen:
        # Asignar imágenes de forma circular
        for i, (comisaria_id, nombre) in enumerate(comisarias_sin_imagen):
            # Usar una imagen diferente para cada comisaría (rotar si se acaban)
            imagen_url = SAMPLE_IMAGES[i % len(SAMPLE_IMAGES)]

            cursor.execute(
                "UPDATE comisarias SET foto_url = ? WHERE id = ?",
                (imagen_url, comisaria_id)
            )
            print(f"✅ Actualizada imagen para: {nombre}")

        # Guardar cambios
        conn.commit()
        print(f"\n🎉 Se actualizaron {len(comisarias_sin_imagen)} comisarías con imágenes de muestra")
    else:
        print("✨ Todas las comisarías ya tienen imagen")

    # Mostrar resumen final
    cursor.execute("SELECT COUNT(*) FROM comisarias WHERE foto_url IS NOT NULL AND foto_url != ''")
    total_con_imagen = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM comisarias")
    total_comisarias = cursor.fetchone()[0]

    print(f"\n📈 Resumen final:")
    print(f"   - Total de comisarías: {total_comisarias}")
    print(f"   - Comisarías con imagen: {total_con_imagen}")
    print(f"   - Porcentaje con imagen: {(total_con_imagen/total_comisarias)*100:.1f}%")

    conn.close()

if __name__ == "__main__":
    update_comisaria_images()