import pyproj


class Point_OLD:

    def __init__(self, longitude, latitude, precision=1):
        """
        Implements the methods for reporting a UTM or UPS grid location as described in the following document:
        http://earth-info.nga.mil/GandG/publications/NGA_STND_0037_2_0_0_GRIDS/NGA.STND.0037_2.0.0_GRIDS.pdf
        :param longitude: float
        :param latitude: float
        :param precision: int, default=1, desired precision of the grid reference
        """

        self.zone_number = None
        self.zone_letter = None
        self.k100_id = None
        self.grid_coords = None
        self.utm_e = None
        self.utm_n = None
        self.grid_reference = self.get_grid_reference()

        self.set_zone_number(longitude)
        self.set_zone_letter(latitude)

        if self.zone_number and self.zone_letter:
            self.lonlat_to_utm(longitude, latitude)
            self.set_100k_id()
            self.set_grid_coords(precision)

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
        self.utm_e, self.utm_n = p(longitude.values, latitude.values)

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

    def set_100k_id(self):
        """
        Implements the logic for determining the 100,000 meter grid ID in steps B-6.c through B-6.f of page B-2.
        """
        reduced_e = self.reduce_to_100k(self.utm_e)
        reduced_n = self.reduce_to_100k(self.reduce_by_2mill(self.utm_n))
        first_letter = self.set_100k_first_letter(reduced_e)
        second_letter = self.set_100k_second_letter(reduced_n)
        self.k100_id = first_letter + second_letter

    def set_grid_coords(self, precision):
        """
        Determines grid coordinates for the given point using the specified level of precision.
        The default setting is the highest level of precision: 1 meter.
        If the given precision falls between two precision levels, the lower precision level is chosen.
        Examples:
            1 -> 1
            2 -> 10
        :param precision: int
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

    def get_grid_reference(self):
        """
        Reports the grid reference for the given point using the specified level of precision.
        :return: string
        """
        if self.zone_number and self.zone_letter:
            return '{:02}{}{}{}'.format(self.zone_number, self.zone_letter, self.k100_id, self.grid_coords)
        else:
            return None


class Point:

    def __init__(self, dataframe, precision=1):

        self.df = dataframe
        self.df1 = dataframe

        self.set_gzd()
        self.set_utm()

        print(self.df)
        print('-' * 30)

    def set_gzd(self):

        try:
            self.df['znum'] = self.df.iloc[:, 1].apply(self.set_zone_number)
            self.df['zlet'] = self.df.iloc[:, 0].apply(self.set_zone_letter)
            self.df['gzd'] = self.df['znum'] + self.df['zlet']
        except TypeError:
            self.df = None

    @staticmethod
    def set_zone_number(longitude):
        """
        Determines the number of a point's grid zone designation using the logic in chapters 2 and 3.
        :param longitude: float
        """
        if -180 <= longitude <= 180:
            number = int(longitude / 6 + 31)
            # Adjust for the valid input of 180 degrees longitude
            if number == 61:
                number = 1
            return str(number)
        else:
            # todo deal with exceptions in V and X
            return None

    @staticmethod
    def set_zone_letter(latitude):
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
            return letter[index]
        else:
            # todo deal with polar coordinates
            return None

    def set_utm(self):

        try:
            self.df['utm'] = self.df.apply(self.set_proj4, axis=1)

        except AttributeError:
            # This deals with NoneTypes return from set_gzd
            self.df = None

    @staticmethod
    def lonlat_to_utm(zone_number, zone_letter, longitude, latitude):
        """
        Converts a given latitude and longitude to its UTM coordinate value.
        :param zone_number: string
        :param zone_letter: string
        :param longitude: float
        :param latitude: float
        """
        proj4 = '+proj=utm +zone={} +datum=WGS84 +units=m +no_defs'.format(zone_number)
        if zone_letter < 'N':
            proj4 += ' +south'
        p = pyproj.Proj(proj4)
        return p(longitude.values, latitude.values)

    @staticmethod
    def set_proj4(row):

        proj4 = '+proj=utm +zone={} +datum=WGS84 +units=m +no_defs'.format(row['znum'])
        try:
            if row['zlet'] < 'N':
                proj4 += ' +south'
            p = pyproj.Proj(proj4)
            return p(row[0], row[1])
        except TypeError:
            # This deals with NoneTypes in empty rows
            return None
