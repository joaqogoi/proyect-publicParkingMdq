import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, MultiLineString, Point

# Carga del archivo Shape con el mapa de la localidad
shapefile_path = "C:\Programacion\Python\municipio_mdq_shape\calles.shp"
shapefile_gdf = gpd.read_file(shapefile_path)

#Limit border creation of the actionArea

def setActionArea(geo_date_frame,*limit_streets_ids):
    selected_segments = []
    limit_streets_ids_padded = [str(code).zfill(5) for code in limit_streets_ids]
    for street_code in limit_streets_ids_padded:
        #Filtrar calles por codigo
        street_data = geo_date_frame[geo_date_frame['COD_CALLES'] == street_code]
        #Comprobacion de coincidencia
        if len(street_data) > 0:
            #Creacion de la lista que contiene todos los segmentos LineString correspondientes al cod de calle
            street_segments = [geom for geom in street_data['geometry']]
            #Verificacion de intersecciones con otras calles
            for segment in street_segments:
                for street_code2 in limit_streets_ids_padded:
                    #Filtro de calles diferentes
                    if street_code2 != street_code:
                        street_data2 = geo_date_frame[geo_date_frame['COD_CALLES'] == street_code2]
                        if len(street_code2) > 0:
                            street_segments2 = [geom for geom in street_data2['geometry']]
                            for segment2 in street_segments2:
                                #Verificacion de intersecciones mediante el metodo .intersects() de la biblioteca Shapely
                                #Si se verifica que el segmento de la calle actual tiene intersecciones con otros segmentos se lo considera parte del area de accion
                                if segment.intersects(segment2):
                                    selected_segments.append(segment)
                                    break
    #Combinacion de los segmentos seleccionados en un obj geoespacial no segmentado    
    action_area = MultiLineString(selected_segments)
    #Creacion de un Poligono como una entidad geoespacial cerrada
    action_polygon = Polygon(action_area.convex_hull)
    #Remocion del exceso en el area del poligono
    action_polygon = removeExcessAreas(action_polygon,selected_segments)
    #Final de la funcion
    return action_polygon

def removeExcessAreas(polygon, lines):
    excess_polygon_area = polygon
    for line in lines:
        print("area antes:", excess_polygon_area)
        excess_polygon_area = excess_polygon_area.difference(line)
        print("line: ", line)
        print("area despues: ", excess_polygon_area)
    return excess_polygon_area


def filterStreetsWithinActionPolygon(geo_data_frame, action_polygon):
    streets_whithin_polygon = []
    for i, street in geo_data_frame.iterrows():
        if street['geometry'].within(action_polygon):
            streets_whithin_polygon.append(street)
    streets_whithin_polygon_gdf = gpd.GeoDataFrame(streets_whithin_polygon, crs=geo_data_frame.crs)
    print(streets_whithin_polygon_gdf)
    return streets_whithin_polygon_gdf


action_area = setActionArea(shapefile_gdf, 298, 717, 465, 425, 560, 826)
print(action_area)

polygonMappingArea = filterStreetsWithinActionPolygon(shapefile_gdf, action_area)

#Creacion del GDF del poligono
action_polygon_gdf = gpd.GeoDataFrame(geometry=[action_area])

#Creacion de una Figura y los ejes de plt
fig, ax = plt.subplots()
action_polygon_gdf.plot(ax=ax, color='red', label='Action Area')
shapefile_gdf.plot(ax=ax, color='blue')
polygonMappingArea.plot(ax=ax, color='green', label='Action Area')
for index, street in polygonMappingArea.iterrows():
    ax.annotate(street['NOM_COMPLE'], xy=(street['geometry'].centroid.x, street['geometry'].centroid.y))
ax.legend()
plt.show()





""" vamos a intentar cambiar la logica para crear el poligono, con los codigos de las calles vamos
a filtrar las calles correspondientes (debemos investigar que calles tienen informacion completa y cuales no)
una vez que obtenemos cada una de las calles como objetos que pueden ser mas obj que calles debido a que
cada calle dependiendo de su longitud puede estar compuesta de varios linestring, para filtrar esto nos
vamos a concentrar en las intersecciones de las calles es decir solamente seleccionaremos los linestring
que contengan cordenadas que sean iguales al menos a alguna otro linestring de otra calle es decir que 
los fragmentos que no tengas coincidencias dentro del area de accion no seran seleccionados"""

"""una vez que obtenemos cada interseccion creamos un poligono a partir de estas intersecciones y no de 
las calles en si, para generalizar y enfocar el proceso, de esta manera es aplicable a cualquier tipo de
mapa sin importar su complejidad"""

'''
Interacion Implicita:
La expresión "geom for geom" crea un bucle de iteracion IMPLICITO 
ya que no esta formalmente declarado como un bucle for por ejemplo,
en el contexto de la logica en nuestro codigo la expresión crea un
bucle donde la variable geom no tiene un valor declarado inicial
si no que itera sobre los segementos LineString obtenidos del GDF
street_data mediante la expresión street_data['geometry'] creando
como resultado una lista de segmentos LineString correspondientes
a una misma calle del GDF
'''
