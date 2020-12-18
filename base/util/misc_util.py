# -------------------------------------------------------------------------------- #
#                     OPTIONAL ANALYSIS FUNCTION FOR THE TRIPS                     #
# -------------------------------------------------------------------------------- #
from base.util.trips_util import extract_trips
from common.util.common_util import s_print, create_dir


def route_analysis(trip_ids=None):
    """
    Args:
        trip_ids:
        plot the full route based on the locations provided in shapes.txt file
    """
    if trip_ids is None:
        trip_ids = []
    trips = extract_trips()
    for trip in trips:
        if trip.trip_id in trip_ids:
            plot_route_in_map(trip.route.start_pos.lat_lon(),
                              trip.route.end_pos.lat_lon(),
                              trip.route.locations, trip_id=trip.trip_id)


def route_analysis_sect():
    """
      Analysis the route which has less than 600 seconds duration for trip
    """
    trips = extract_trips()
    trip_ids = []
    for trip in trips:
        if trip.duration.time_in_seconds < 600:
            trip_ids.append(trip.trip_id)
            s_print("{},{},{}".format(str(trip.trip_id), str(trip.duration.time_in_seconds),
                                      str(trip.route.distance)))

    s_print(str(len(trip_ids)))
    route_analysis(trip_ids)


def plot_route_in_map(point_first, point_second, _coordinates, trip_id="", _route_count=0):
    """
    Args:
        point_first: origin of the route
        point_second: destination of the route
        _coordinates: list of coordinates
        trip_id: specific trip id
        _route_count: if multiple route exists with same start and end, this will used to differentiate
    """
    import folium

    pf_lat, pf_lon = point_first.split(",")
    pf_lat = round(float(pf_lat), 5)
    pf_lon = round(float(pf_lon), 5)
    pf = [pf_lat, pf_lon]
    ps_lat, ps_lon = point_second.split(",")
    ps_lat = round(float(ps_lat), 5)
    ps_lon = round(float(ps_lon), 5)
    ps = [ps_lat, ps_lon]
    some_map = folium.Map(location=pf, zoom_start=15)
    folium.Marker(location=pf, icon=folium.Icon(color='red'), tooltip=str(pf)).add_to(some_map)
    folium.Marker(location=ps, icon=folium.Icon(color='green'), tooltip=str(ps)).add_to(some_map)
    for coordinate in _coordinates:
        folium.Marker(location=coordinate, fill_color='blue', radius=3, tooltip=str(coordinate)).add_to(some_map)
    if trip_id == "":
        map_file_directory = 'data/maps/' + point_first + point_second
        map_file_directory = map_file_directory.replace(".", "_")
        map_file_directory = map_file_directory.replace("-", "NE")
        map_file_directory = map_file_directory.replace(",", "__")
    else:
        map_file_directory = 'data/maps/' + trip_id
    create_dir(map_file_directory)
    some_map.save(map_file_directory + '/missing_routes' + '_' + str(_route_count) + '.html')
