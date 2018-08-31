import pyproj

import data
import locate


class Grid:

    def __init__(self, data, columns=None, epsg=4326):

        self.input_data = data
        self.data = None
        self.columns = columns
        self.epsg = epsg
        self.error = None
        self.grid_references = []

        self.set_coords()

        print(type(self.data))
        print(self.data)

        if self.error:
            self.set_error(self.error)
        elif self.epsg != 4326:
            self.transform_coords()

    def set_coords(self):

        if isinstance(self.input_data, (tuple, list)) and (len(self.input_data) > 1):
            self.data, self.error = data.from_list(self.input_data)
        else:
            try:
                if self.input_data.endswith('.csv'):
                    self.data, self.error = data.from_csv(self.input_data, self.columns)
                elif self.input_data.endswith('.shp'):
                    self.data, self.error = data.from_shapefile(self.input_data)
                else:
                    raise AttributeError
            except AttributeError:
                self.set_error('Invalid parameters: Grid(data={}, columns={}, epsg={})'.format(
                    repr(self.input_data), self.columns, self.epsg))

    def transform_coords(self):

        try:
            p = pyproj.Proj(init='epsg:{}'.format(self.epsg))
            self.xs, self.ys = p(self.data[0][0], self.data[0][1], inverse=True)
        except RuntimeError:
            self.error('EPSG:{} not found'.format(self.epsg))

    def get_grid_refs(self):

        for x, y in zip(self.xs, self.ys):
            print(x, y)
            self.grid_references.append(locate.Point(x, y).get_grid_reference())

    def write_references(self, fname=None, col='GRID_REFS'):

        if fname is None:
            fname = self.data
        self.get_grid_refs()

    def set_error(self, message):

        preamble = 'Error creating Grid object:'
        self.error = ('{} {}'.format(preamble, message))
        print(self.error)


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
    g = Grid([(-34.907587535813704, 50.58441270574641), (108.93083026662671, 32.38153601114477)])
    g = Grid(lonlats)
    g = Grid(lonlats2)
    g = Grid(lonlats3)
    g = Grid('./tests/data/points.csv', ['POINT_X', 'POINT_Y'])
    g = Grid('./tests/data/points.csv', ['POINT_X', 0])
    g = Grid('./tests/data/points.csv', 'POINT_X')
    g = Grid('./tests/data/points.csv')
    #
    g = Grid('./tests/data/points.shp')
    # g = Grid('../tests/data/points.shp', epsg=3086)

    # g = Grid('./tests/data/good_crimes.csv', ('Longitude', 'Latitude'))

    # g = Grid('./tests/data/chicago_crimes_2016.csv', ('Longitude', 'Latitude'))

    # print(g.grid_refs)

    # These are the desired method calls
    # g = Grid('myassets.csv', 'Lon', 'Lat', epsg=3086)
    # g.write_refs('myassets.shp', 'MY_OFFICIAL_GRID_REFERENCES')
    # g.write_assets('myassets.shp', 'MY_UNIQUE_ASSET_NAMES',
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
