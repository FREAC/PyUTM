import fiona
import shapely
import pyproj

from osgeo import ogr
import shapefile as pyshp


# Implements http://earth-info.nga.mil/GandG/publications/NGA_STND_0037_2_0_0_GRIDS/NGA.STND.0037_2.0.0_GRIDS.pdf


def get_lonlat(epsg, easting, northing):

    p = pyproj.Proj(init='epsg:{}'.format(epsg))

    return p(easting, northing, inverse=True)


def lonlat_to_utm(zone_number, zone_letter, longitude, latitude):

    proj4 = '+proj=utm +zone={} +datum=WGS84 +units=m +no_defs'.format(zone_number)
    if zone_letter < 'N':
        proj4 += ' +south'

    p = pyproj.Proj(proj4)

    return p(longitude, latitude)


def get_zone_number(longitude):

    if -180 <= longitude <= 180:

        number = int(longitude / 6 + 31)
        # Adjust for the valid input of 180 degrees longitude
        if number == 61:
            number = 1
        return number

    else:
        # todo deal with exceptions in V and X
        return None


def get_zone_letter(latitude):

    if -80 <= latitude <= 84:

        letter = 'CDEFGHJKLMNPQRSTUVWX'
        ref = int(latitude / 8 + 10)
        # Adjust for the valid inputs 80 <= latitude <= 84
        if ref == 20:
            ref = 19
        return letter[ref]

    else:
        # todo deal with polar coordinates
        return None


def get_grid_zone_designation(longitude, latitude):

    return get_zone_number(longitude), get_zone_letter(latitude)


def reduce_to_100k(number):

    return int(number / 100000) * 100000


def reduce_by_2mill(number):

    while number >= 2000000:
        number -= 2000000
    return number


def get_100k_first_letter(zone_number, utm_e):

    letter = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    set1 = range(1, 60, 3)
    set2 = range(2, 60, 3)

    index = int(utm_e / 100000 - 1)

    if zone_number in set1:
        return letter[index]
    elif zone_number in set2:
        return letter[index + 8]
    else:
        return letter[index + 16]


def get_100k_second_letter(zone_number, utm_n):

    if zone_number % 2 == 0:
        letter = 'FGHJKLMNPQRSTUVABCDE'
    else:
        letter = 'ABCDEFGHJKLMNPQRSTUV'

    index = int(utm_n / 100000)

    return letter[index]


def get_100k_grid_id(zone_number, utm_e, utm_n):

    reduced_e = reduce_to_100k(utm_e)
    reduced_n = reduce_to_100k(reduce_by_2mill(utm_n))

    first_letter = get_100k_first_letter(zone_number, reduced_e)
    second_letter = get_100k_second_letter(zone_number, reduced_n)

    return first_letter + second_letter


def get_grid_coords(utm_e, utm_n, precision=1):

    utm_e = str(int(utm_e))
    utm_n = str(int(utm_n))

    if precision == 1:
        return utm_e[-5:] + utm_n[-5:]
    elif precision <= 10:
        return utm_e[-5:-1] + utm_n[-5:-1]
    elif precision <= 100:
        return utm_e[-5:-2] + utm_n[-5:-2]
    elif precision <= 1000:
        return utm_e[-5:-3] + utm_n[-5:-3]
    elif precision <= 10000:
        return utm_e[-5:-4] + utm_n[-5:-4]
    else:
        return ''


# if __name__ == "__main__":

    # shp = pyshp.Reader('points.shp')
    # for shape in shp.shapes():
    #     lon = shape.points[0][0]
    #     lat = shape.points[0][1]
    #
    #     letter = get_zone_letter(lat)
    #     number = get_zone_number(lon)

epsg = 3086
e_o = 607963.016
n_o = 587856.725

e_o = 287415.307
n_o = 709443.787

e_o = 738392.773
n_o = 170039.367

lon, lat = get_lonlat(epsg, e_o, n_o)

zone_num, zone_lett = get_grid_zone_designation(lon, lat)
e, n = lonlat_to_utm(zone_num, zone_lett, lon, lat)
grid_letters = get_100k_grid_id(zone_num, e, n)

print('Coords:', e_o, n_o)
print('Lon/Lat:', lon, lat)
print('UTM:', e, n)
print('Grid Reference: {}{}{}'.format(zone_num, zone_lett, grid_letters))
print()

lon, lat = -37.076989, -60.823739
zone_num, zone_lett = get_grid_zone_designation(lon, lat)
e, n = lonlat_to_utm(zone_num, zone_lett, lon, lat)
grid_letters = get_100k_grid_id(zone_num, e, n)

print('Lon/Lat:', lon, lat)
print('UTM:', e, n)
print('Grid Reference: {}{}{}'.format(zone_num, zone_lett, grid_letters))

coords = get_grid_coords(e, n)
print(coords)