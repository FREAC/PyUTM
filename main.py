import csv
import pyproj
import shapefile

import fiona
import shapely
from osgeo import ogr


class Point:
    """
    Implements the methods for reporting a UTM or UPS grid location as described in the following document:
    http://earth-info.nga.mil/GandG/publications/NGA_STND_0037_2_0_0_GRIDS/NGA.STND.0037_2.0.0_GRIDS.pdf
    """
    def __init__(self, longitude, latitude, precision=1):

        self.zone_number = None
        self.zone_letter = None
        self.grid_id = None
        self.grid_coords = None
        self.utm_e = None
        self.utm_n = None

        self.set_zone_number(longitude)
        self.set_zone_letter(latitude)

        if self.zone_number and self.zone_letter:
            self.lonlat_to_utm(longitude, latitude)
            self.set_100k_grid_id()
            self.set_grid_coords(precision)

        self.grid_reference()

    def set_zone_number(self, longitude):
        """
        Determines the number of a point's grid zone designation using the logic in chapters 2 and 3.
        :param longitude: float
        """
        if -180 <= longitude <= 180:
            number = int(longitude / 6 + 31)
            # Adjust for the valid input of 180 degrees longitude
            if number == 61:
                number = 1
            self.zone_number = number
        else:
            # todo deal with exceptions in V and X
            pass

    def set_zone_letter(self, latitude):
        """
        Determines the letter of a point's grid zone designation using the logic in chapters 2 and 3.
        :param latitude: float
        """
        if -80 <= latitude <= 84:
            letter = 'CDEFGHJKLMNPQRSTUVWX'
            index = int(latitude / 8 + 10)
            # Adjust for the valid inputs 80 <= latitude <= 84
            if index == 20:
                index = 19
            self.zone_letter = letter[index]
        else:
            # todo deal with polar coordinates
            pass

    def lonlat_to_utm(self, longitude, latitude):
        """
        Converts a given latitude and longitude to its UTM coordinate value.
        :param longitude: float
        :param latitude: float
        """
        proj4 = '+proj=utm +zone={} +datum=WGS84 +units=m +no_defs'.format(self.zone_number)
        if self.zone_letter < 'N':
            proj4 += ' +south'
        p = pyproj.Proj(proj4)
        self.utm_e, self.utm_n = p(longitude, latitude)

    @staticmethod
    def reduce_to_100k(number):
        """
        Reduces the given coordinate to the nearest 100,000 meters.
        Examples:
            100,000.0 -> 100,000
            123,456.7 -> 100,000
            199,999.9 -> 100,000
            1,123,456.7 -> 1,100,000
        :param number: float
        :return: int
        """
        return int(number / 100000) * 100000

    @staticmethod
    def reduce_by_2mill(number):
        """
        Removes multiples of 2,000,000 from the given coordinate until less than 2,000,000.
        :param number: float
        :return: int
        """
        while number >= 2000000:
            number -= 2000000
        return number

    def set_100k_first_letter(self, reduced_e):
        """
        Determines the first letter of the 100,000 meter grid ID using the method described on page B-2.
        :param reduced_e: int
        :return: string
        """
        letter = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        set1 = range(1, 60, 3)
        set2 = range(2, 60, 3)
        index = int(reduced_e / 100000 - 1)

        if self.zone_number in set1:
            return letter[index]
        elif self.zone_number in set2:
            return letter[index + 8]
        else:
            return letter[index + 16]

    def set_100k_second_letter(self, reduced_n):
        """
        Determines the second letter of the 100,000 meter grid ID using the method described on page B-2.
        :param reduced_n: int
        :return: string
        """
        if self.zone_number % 2 == 0:
            letter = 'FGHJKLMNPQRSTUVABCDE'
        else:
            letter = 'ABCDEFGHJKLMNPQRSTUV'

        index = int(reduced_n / 100000)
        return letter[index]

    def set_100k_grid_id(self):
        """
        Implements the logic for determining the 100,000 meter grid ID in steps B-6.c through B-6.f of page B-2.
        """
        reduced_e = self.reduce_to_100k(self.utm_e)
        reduced_n = self.reduce_to_100k(self.reduce_by_2mill(self.utm_n))
        first_letter = self.set_100k_first_letter(reduced_e)
        second_letter = self.set_100k_second_letter(reduced_n)
        self.grid_id = first_letter + second_letter

    def set_grid_coords(self, precision):
        """
        Determines grid coordinates for the given point using the specified level of precision.
        The default setting is the highest level of precision: 1 meter.
        If the given precision falls between two precision levels, the lower precision level is chosen.
        Examples:
            1 -> 1
            2 -> 10
        :param precision: int, default=1
        """
        utm_e = str(int(self.utm_e))
        utm_n = str(int(self.utm_n))

        if precision == 1:
            self.grid_coords = utm_e[-5:] + utm_n[-5:]
        elif precision <= 10:
            self.grid_coords = utm_e[-5:-1] + utm_n[-5:-1]
        elif precision <= 100:
            self.grid_coords = utm_e[-5:-2] + utm_n[-5:-2]
        elif precision <= 1000:
            self.grid_coords = utm_e[-5:-3] + utm_n[-5:-3]
        elif precision <= 10000:
            self.grid_coords = utm_e[-5:-4] + utm_n[-5:-4]
        else:
            self.grid_coords = ''

    def grid_reference(self):
        """
        Reports the grid reference for the given point using the specified level of precision.
        :return: string
        """
        if self.zone_number and self.zone_letter:
            return '{:02}{}{}{}'.format(self.zone_number, self.zone_letter, self.grid_id, self.grid_coords)
        else:
            return None


class Grid:

    def __init__(self, data, col1=None, col2=None, epsg=4326):

        self.data = data
        self.col1 = col1
        self.col2 = col2
        self.epsg = epsg
        self.xs = None
        self.ys = None

        self.set_coords()
        if self.epsg != 4326 and (self.xs and self.ys):
            self.transform_coords()

        print(self.xs)
        print(self.ys)

    def set_coords(self):

        if isinstance(self.data, (tuple, list)) and (len(self.data) > 1):
            self.get_coords_from_list()
        else:
            try:
                if self.data.endswith('.csv'):
                    self.get_coords_from_csv()
                elif self.data.endswith('.shp'):
                    self.get_coords_from_shapefile()
                else:
                    raise AttributeError
            except AttributeError:
                self.error('Invalid parameters: Grid(data={}, col1={}, col2={}, epsg={})'.format(
                    repr(self.data), self.col1, self.col2, self.epsg))

    def get_coords_from_list(self):

        coords = ()
        try:
            # Grab the column containing coordinates if applicable
            if self.col1 is not None:
                coords = tuple(zip(*self.data))[self.col1]
            else:
                if not isinstance(self.data[0], (tuple, list)) and not isinstance(self.data[1], (tuple, list)):
                    coords = [(self.data[0], self.data[1])]
                else:
                    coords = self.data
            self.xs = tuple(coord[0] for coord in coords)
            self.ys = tuple(coord[1] for coord in coords)
        except (TypeError, IndexError):
            self.error('Invalid coordinates: {}'.format(coords))

    def get_coords_from_csv(self):

        try:
            with open(self.data) as csvfile:
                reader = csv.DictReader(csvfile)
                data = tuple(zip(*((float(row[self.col1]), float(row[self.col2])) for row in reader)))
                self.xs = data[0]
                self.ys = data[1]
        except (FileNotFoundError, KeyError, csv.Error) as e:
            if type(e).__name__ == 'KeyError':
                self.error('Invalid column names: col1={}, col2={}'.format(self.col1, self.col2))
            else:
                self.error(e)

    def get_coords_from_shapefile(self):

        try:
            sf = shapefile.Reader(self.data)
            shapes = sf.shapes()
            # Only accept Point, PointZ and PointM geometries
            if shapes[0].shapeType in (1, 11, 21):
                self.xs = tuple(shape.points[0][0] for shape in shapes)
                self.ys = tuple(shape.points[0][1] for shape in shapes)
        except shapefile.ShapefileException as e:
            self.error(e)

    def transform_coords(self):

        try:
            p = pyproj.Proj(init='epsg:{}'.format(self.epsg))
            self.xs, self.ys = p(self.xs, self.ys, inverse=True)
        except RuntimeError:
            self.error('EPSG:{} not found'.format(self.epsg))

    def error(self, message):

        preamble = 'Error creating Grid object:'
        self.xs = None
        self.ys = None
        print('{} {}'.format(preamble, message))


if __name__ == "__main__":

    pass
    # lat = 25.49225455501417
    # lon = -80.62948251805712
    # c = Point(lon, lat)
    # print(c.grid_reference())

lonlats = [(-34.907587535813704, 50.58441270574641), (108.93083026662671, 32.38153601114477),
           (-36.69218329018642, -45.06991972863084), (43.97154480746007, -46.140677181254475)]
lonlats2 = [[(-34.907587535813704, 50.58441270574641), True, [1, 2], 1, 'a'],
            [(108.93083026662671, 32.38153601114477), False, [3, 4], 2, 'b'],
            [(-36.69218329018642, -45.06991972863084), False, [5, 6], 3, 'c'],
            [(43.97154480746007, -46.140677181254475), True, [7, 8], 4, 'd']]
lonlats3 = [((-34.907587535813704, 50.58441270574641), 1), ((108.93083026662671, 32.38153601114477), 2),
            ((-36.69218329018642, -45.06991972863084), 3), ((43.97154480746007, -46.140677181254475), 4)]

g = Grid(lonlats)
g = Grid(lonlats2, 0)
g = Grid(lonlats3, 0)
g = Grid('points.csv', 'POINT_X', 'POINT_Y')
g = Grid('points.shp')
g = Grid('points.shp', epsg=3086)

# These possibilities are done
# print('Grid(True)')
# g = Grid(True)
# print('Grid(0)')
# g = Grid(0)
# print('Grid(1)')
# g = Grid(1)
# print('Grid(2)')
# g = Grid(2)
# print('Grid("i")')
# g = Grid('i')
# print('Grid("ijeg")')
# g = Grid('ijeg')
# print('Grid(0.123456)')
# g = Grid(0.123456)
# print('Grid([])')
# g = Grid([])
# print('Grid(())')
# g = Grid(())
# print('Grid([1])')
# g = Grid([1])
# print('Grid((1,))')
# g = Grid((1,))
# print('Grid((1))')
# g = Grid((1))
# g = Grid('points1.shp')
# g = Grid('points.shp', epsg=45673086)
# g = Grid('points.csv', 'POINT_X', 'POINT')
# g = Grid('points.csv', 'POINT_X')
# g = Grid('points1.csv', 'POINT_X', 'B')
# print('Grid([1, 2])')
# g = Grid([1, 2])
# print('Grid((1, 2))')
# g = Grid((1, 2))
# print('Grid(lonlats2, 1)')
# g = Grid(lonlats2, 1)
# print('Grid(lonlats2, 2)')
# g = Grid(lonlats2, 2)
# print('Grid(lonlats2, 3)')
# g = Grid(lonlats2, 3)
# print('Grid(lonlats2, 4)')
# g = Grid(lonlats2, 4)
# print('Grid(lonlats2, 5)')
# g = Grid(lonlats2, 5)
# g = Grid(lonlats3)