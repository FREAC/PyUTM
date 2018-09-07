import sys

import pyproj

import data
import locate
import setrefs


class Grid:

    def __init__(self, data, columns=None, epsg=4326):

        self.input_data = data
        self.input_columns = columns
        self.input_datatype = None
        self.data = None
        self.columns = None
        self.epsg = epsg
        self.error_message = None
        self.grid_references = []

        self.set_columns()
        self.set_data()

        if self.epsg != 4326:
            self.transform_coords()
        if self.error_message:
            self.error(self.error_message)

    def set_data(self):

        if isinstance(self.input_data, (tuple, list)) and (len(self.input_data) > 1):
            self.input_datatype = 0
            self.data, self.error_message = data.from_list(self.input_data)
        else:
            try:
                if self.input_data.endswith('.csv') and self.columns:
                    self.input_datatype = 1
                    self.data, self.error_message = data.from_csv(self.input_data, self.columns)
                elif self.input_data.endswith('.shp'):
                    self.input_datatype = 2
                    self.data, self.error_message = data.from_shapefile(self.input_data)
                else:
                    raise AttributeError
            except AttributeError:
                self.error_message = 'Invalid parameter(s): Grid(data={}, columns={}, epsg={})'.format(
                    repr(self.input_data), repr(self.input_columns), self.epsg)

    def transform_coords(self):

        try:
            p = pyproj.Proj(init='epsg:{}'.format(self.epsg))
            self.data[0], self.data[1] = p(self.data[0].values, self.data[1].values, inverse=True)
        except RuntimeError:
            self.error_message = 'EPSG:{} not found'.format(self.epsg)

    def get_grid_refs(self, column, precision):

        try:
            self.data[column] = [locate.Point(coord[0], coord[1], precision).get_grid_reference()
                                 for coord in self.data.values]
        except (KeyError, ValueError):
            self.error('Invalid column name')

    def set_columns(self):

        if isinstance(self.input_columns, (tuple, list)):
            if len(self.input_columns) == 2:
                self.columns = tuple(self.input_columns)
            else:
                self.columns = None

    @staticmethod
    def error(message):

        print('Error creating Grid object: {}'.format(message))
        sys.exit(1)

    def write_references(self, fname=None, column='GRID_REFS', precision=1):

        self.get_grid_refs(column, precision)

        if self.input_datatype == 0:
            return setrefs.to_list(self.data)
        elif self.input_datatype == 1:
            setrefs.to_csv(fname, self.input_data, self.data, column)
            return None
        else:
            pass


if __name__ == "__main__":

    lonlats = [(-34.907587535813704, 50.58441270574641),
               (108.93083026662671, 32.38153601114477),
               (-36.69218329018642, -45.06991972863084),
               (43.97154480746007, -46.140677181254475)]

    lonlats2 = [[(-34.907587535813704, 50.58441270574641), True, [1, 2], 1, 'a'],
                [(108.93083026662671, 32.38153601114477), False, [3, 4], 2, 'b'],
                [(-36.69218329018642, -45.06991972863084), False, [5, 6], 3, 'c'],
                [(43.97154480746007, -46.140677181254475), True, [7, 8], 4, 'd']]

    lonlats3 = [((-34.907587535813704, 50.58441270574641), 1), ((108.93083026662671, 32.38153601114477), 2),
                ((-36.69218329018642, -45.06991972863084), 3), ((43.97154480746007, -46.140677181254475), 4)]

    g = Grid((-34.907587535813704, 50.58441270574641))
    g_output = g.write_references(precision=10)
    print(g_output)
    h = Grid([(-34.907587535813704, 50.58441270574641), (108.93083026662671, 32.38153601114477)])
    h_output = h.write_references()
    print(h_output)
    # g = Grid([(7, (-34.907587535813704, 50.58441270574641)), (8, (108.93083026662671, 32.38153601114477)),
    #           (9, (43.97154480746007, -46.140677181254475))], 1)
    i = Grid(lonlats)
    i_output = i.write_references()
    print(i_output)
    j = Grid(lonlats2)
    j_output = j.write_references()
    print(j_output)
    # g = Grid(lonlats3)
    # #
    # print()
    # print('g = Grid(lonlats2, 0)')
    # g = Grid(lonlats2, 0)
    # #
    # print()
    # print('g = Grid(lonlats2, (3, 10))')
    # g = Grid(lonlats2, (3, 10))
    # #
    # print()
    # print('g = Grid(lonlats3, 0)')
    # g = Grid(lonlats3, 0)
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'])")
    g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'])
    csv_output = g.write_references(fname=r'D:\Projects\USNG\test.csv')
    csv_output = g.write_references()

    # print()
    # print("g = Grid('./tests/data/points.csv', ['POINT_X', 0])")
    # g = Grid('./tests/data/points.csv', ['POINT_X', 0])
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', ['POINT_X', 'PNT'])")
    # g = Grid('./tests/data/points.csv', ['POINT_X', 'PNT'])
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', 'POINT_X')")
    # g = Grid('./tests/data/points.csv', 'POINT_X')
    #
    # print()
    # print("g = Grid('./tests/data/points.csv', [])")
    # g = Grid('./tests/data/points.csv', [])
    #
    # print()
    # print("g = Grid('./tests/data/points.csv')")
    # g = Grid('./tests/data/points.csv')

    j = Grid('./tests/data/points.shp')
    j_output = j.write_references()
    print(j_output)

    x = Grid('./tests/data/points.shp', epsg=3086)
    x_output = x.write_references(column='Grid ID')
    print(x_output)

    # import time
    #
    # start = time.time()
    # b = Grid('./tests/data/good_crimes.csv', ('Longitude', 'Latitude'))
    # b.write_references()
    # print(time.time() - start)
    #
    # start = time.time()
    # c = Grid('./tests/data/chicago_crimes_2016.csv', ('Longitude', 'Latitude'))
    # test3 = c.write_references()
    # print(test3)
    # print(time.time() - start)

    # print(g.grid_refs)

    # These are the desired method calls
    # g = Grid('myassets.csv', ['Lon', 'Lat'], epsg=3086)
    # g.write_refs('myassets.shp', 'MY_OFFICIAL_GRID_REFERENCES', precision=100)
    # g.write_assets('myassets.shp', 'MY_UNIQUE_ASSET_NAMES', precision=100,
    # prefix='H', col=None, gzd=False, k100=False, delimiter='-')


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
# print("g = Grid('./tests/data/points.shp', epsg=45673086)")
# g = Grid('./tests/data/points.shp', epsg=45673086)
# print("g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT'])")
# g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT'])
# print("g = Grid('points.csv', ['POINT_X', 'POINT_Y'])")
# g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'], 26910)
#
# print("g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'], 'B')")
# g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'], 'B')
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
