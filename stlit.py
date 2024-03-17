from tesspy import Tessellation, tessellation_functions
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from shapely import intersects
import mercantile
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import streamlit as st

# Load shapefiles
gdf_all = gpd.read_file("files/departments/all_deps.shp")
gdf_all.crs = "epsg:4326"

gdf_periurban = gpd.read_file("files/periurban/periurban.shp")
gdf_periurban.crs = "epsg:4326"

gdf_urban = gpd.read_file("files/urban/urban.shp")
gdf_urban.crs = "epsg:4326"

LARGE_ZOOM_LEVEL = 13
MEDIUM_ZOOM_LEVEL = 14
SMALL_ZOOM_LEVEL = 15

MIN_THRESHOLD_ALL = dict(rural=2, periurban=2, urban=1)
MIN_THRESHOLD_4G = dict(rural=3, periurban=2, urban=1)
MIN_THRESHOLD_5G = dict(rural=3, periurban=2, urban=1)


@st.cache_resource
def plot_map(boundary_threshold=0.5):

    # boundary_threshold = 0.5

    deps = Tessellation(gdf_all)

    # deps.get_polygon().plot(figsize=(10, 10)).set_axis_off()

    deps_large = tessellation_functions.get_squares_polyfill(deps.area_gdf, LARGE_ZOOM_LEVEL)


    gdf_periurban = gpd.read_file("files/periurban/periurban.shp")
    gdf_periurban.crs = "epsg:4326"

    df_measurements = pd.read_csv("files/measurements.csv", delimiter=";")
    
    large_tiles_periurban = deps_large[deps_large.apply(intersects_filter, axis=1)[0]]

    deps_large['index_copy'] = deps_large.index
    gdf_joined = gpd.overlay(gdf_periurban, deps_large, how = 'intersection')
    gdf_joined.set_index('index_copy', inplace=True)
    large_tiles_periurban['periurban_area_proportion'] = gdf_joined.to_crs(epsg=4326).area / deps_large.to_crs(epsg=4326).area
    large_tiles_periurban_filtered = large_tiles_periurban[large_tiles_periurban['periurban_area_proportion'] >= boundary_threshold]

    medium_tiles = get_tiles_for_level(large_tiles_periurban_filtered, MEDIUM_ZOOM_LEVEL)

    gdf_urban = gpd.read_file("files/urban/urban.shp")
    gdf_urban.crs = "epsg:4326"

    tiles_with_counts = gpd.read_file('files/tiles_counts/tiles_with_counts.shp')

    all_mesures = tiles_with_counts[~tiles_with_counts.meandbm_to.isnull()][['geometry', 'meandbm_to']]
    _4g_mesures = tiles_with_counts[~tiles_with_counts.meandbm_4g.isnull()][['geometry', 'meandbm_4g']]
    _5g_mesures = tiles_with_counts[~tiles_with_counts.meandbm_5g.isnull()][['geometry', 'meandbm_5g']]


    # Define your ranges and corresponding colors in a dictionary
    color_map = {
        (-85, -41): 'green',
        (-105, -86): 'orange',
        (-141, -106): 'red'
    }

    # Function to map each value in the float column to its corresponding color based on the defined ranges
    def map_to_color(value):
        for range_, color in color_map.items():
            if range_[0] <= value < range_[1]:
                return color
        return 'black'  # Default color if no range matches

    # Apply the mapping function to the float column to create a new column containing colors
    all_mesures['color'] = all_mesures['meandbm_to'].apply(lambda x: map_to_color(x))
    _4g_mesures['color'] = tiles_with_counts['meandbm_4g'].apply(lambda x: map_to_color(x))
    _5g_mesures['color'] = tiles_with_counts['meandbm_5g'].apply(lambda x: map_to_color(x))
    
    large_tiles_urban = deps_large[deps_large.apply(urban_intersects_filter, axis=1)[0]]

    deps_large['index_copy'] = deps_large.index
    gdf_joined_urban = gpd.overlay(gdf_urban, deps_large, how = 'intersection')
    gdf_joined_urban.set_index('index_copy', inplace=True)
    large_tiles_urban['urban_area_proportion'] = gdf_joined_urban.to_crs(epsg=4326).area / deps_large.to_crs(epsg=4326).area
    large_tiles_urban_filtered = large_tiles_urban[large_tiles_urban['urban_area_proportion'] >= boundary_threshold]
    

    small_tiles = get_tiles_for_level(large_tiles_urban_filtered, SMALL_ZOOM_LEVEL)

    # gdf for all mesurments points
    gdf_measurements_all = gpd.GeoDataFrame(
    df_measurements, geometry=gpd.points_from_xy(df_measurements.X, df_measurements.Y)
    )
    gdf_measurements_all.crs = "epsg:2154"  # lambert 93
    gdf_measurements_all = gdf_measurements_all.to_crs("epsg:4326")
    
    deps_large_map = deps_large.explore(name='Rural Tiles', layer_control=True)
    medium_tiles_map = medium_tiles.explore(m=deps_large_map, color="red", name='Peri-Urban Tiles', layer_control=True)
    small_tiles_map = small_tiles.explore(m=medium_tiles_map, color="purple", name='Urban Tiles', layer_control=True)
    gdf_urban_map = gdf_urban.explore(m=small_tiles_map, color="black", name='Contours Urbains', layer_control=True)
    m = gdf_periurban.explore(m=gdf_urban_map, color="black", name='Contours Peri-Urbains', layer_control=True)
    m = _4g_mesures.explore(m=m, color='color', name='4G average')
    m = _5g_mesures.explore(m=m, color='color', name='5G average')
    m = all_mesures.explore(m=m, color='color', name='All average')
    folium.LayerControl().add_to(m)
    return m

    # st.pyplot(f)
def intersects_filter(row):
  return intersects(row['geometry'], gdf_periurban['geometry'])

def urban_intersects_filter(row):
  return intersects(row['geometry'], gdf_urban['geometry'])

def split_tile_to_zoom(tile_row, zoom_level):
  rows = []
  bbox = tile_row.geometry.bounds
  medium_tiles = mercantile.tiles(bbox[0], bbox[1], bbox[2], bbox[3], zoom_level)
  for tile in medium_tiles:
    square = box(*mercantile.bounds(tile))
    rows.append(square)
  return rows

def get_tiles_for_level(base_tiles_df, zoom_level):
  new_rows = []
  for row in base_tiles_df.apply(lambda row: split_tile_to_zoom(row, zoom_level), axis=1):
    new_rows.extend(row)
  new_df = pd.DataFrame(new_rows, columns=['geometry'])
  return gpd.GeoDataFrame(new_df, geometry='geometry', crs='epsg:4326')

st.title('PathFinder Dashboard')

boundary_threshold = st.slider('Select Boundary Threshold:', 0.0, 1.0, 0.5, 0.01)
folium_map = plot_map(boundary_threshold)
folium_static(folium_map)
