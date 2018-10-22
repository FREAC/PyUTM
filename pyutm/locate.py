# For compatibility between Python 2.x and 3.x
try:
    from builtins import range
except ImportError:
    import __builtin__ as builtins

import pyproj


class Point:

    def __init__(self, longitude, latitude, precision=1):
        """
        Implements the methods for reporting a UTM or UPS grid location as described in the following document:
        http://earth-info.nga.mil/GandG/publications/NGA_STND_0037_2_0_0_GRIDS/NGA.STND.0037_2.0.0_GRIDS.pdf
        :param longitude: float, longitude of point in decimal degrees
        :param latitude: float, latitude of point in decimal degrees
        :param precision: int, default=1, desired precision of the grid reference
        """
        self.zone_number = None
        self.zone_letter = None
        self.k100_id = None
        self.grid_coords = None
        self.utm_e = None
        self.utm_n = None

        # Compute the zone information
        try:
            self.set_zone_number(longitude)
            self.set_zone_letter(latitude)
        except TypeError:
            pass

        print(self.zone_number)
        print(self.zone_letter)


        # Only continue if the zone information can be computed
        if self.zone_number and self.zone_letter:
            self.lonlat_to_utm(longitude, latitude)
            self.set_100k_id()
            self.set_grid_coords(precision)

        self.grid_ref = self.get_grid_reference()

    def set_zone_number(self, longitude):
        """
        Determines the number of a point's grid zone designation using the logic in chapters 2 and 3.
        :param longitude: float, longitude of point in decimal degrees
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
        :param latitude: float, latitude of point in decimal degrees
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

    # TODO This should be broken out and run on either the entire dataset at once or on the separate
    # zone numbers and hemispheres
    def lonlat_to_utm(self, longitude, latitude):
        """
        Converts a given latitude and longitude to its UTM coordinate value.
        :param longitude: float, longitude of point in decimal degrees
        :param latitude: float, latitude of point in decimal degrees
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
        :param number: float, UTM coordinate
        :return: int, simplified UTM coordinate
        """
        return int(number / 100000) * 100000

    @staticmethod
    def reduce_by_2mill(number):
        """
        Removes multiples of 2,000,000 from the given coordinate until less than 2,000,000.
        :param number: float, UTM coordinate
        :return: int, simplified UTM coordinate
        """
        while number >= 2000000:
            number -= 2000000
        return number

    def set_100k_first_letter(self, reduced_e):
        """
        Determines the first letter of the 100,000 meter grid ID using the method described on page B-2.
        :param reduced_e: int, simplified UTM easting coordinate
        :return: string, first letter of the 100k meter grid ID
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
        :param reduced_n: int, simplified UTM northing coordinate
        :return: string, second letter of the 100k meter grid ID
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
        :param precision: int, desired precision of grid reference
        """
        utm_e = str(int(self.utm_e))
        utm_n = str(int(self.utm_n))

        if precision <= 1:
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
        Reports the properly formatted grid reference for the given point.
        :return: string, formatted grid reference
        """
        if self.zone_number and self.zone_letter:
            return '{:02}{}{}{}'.format(self.zone_number, self.zone_letter, self.k100_id, self.grid_coords)
        else:
            return None


class UID:

    def __init__(self, grid_refs, prefix, prefix_column, gzd, k100, delimiter):
        """
        Creates a Unique ID (UID) for each grid reference by modifying it
        with a suffix, optional prefixes, and delimiters.
        :param grid_refs: dataframe, grid references to be modified
        :param prefix: string, characters added to beginning of UID
        :param prefix_column: Pandas Series, characters added to beginning of UID
        :param gzd: boolean, whether the Grid Zone Designation should be included in the UID
        :param k100: boolean, whether the 100k meter grid reference should be included in the UID
        :param delimiter: string, delimiter of the UID
        """
        self.uids = grid_refs
        self.prefix = prefix
        self.prefix_column = prefix_column
        self.gzd = gzd
        self.k100 = k100
        self.delimiter = delimiter

        self.set_base_uid()
        self.set_prefix()
        self.set_uid()

    def set_base_uid(self):
        """
        Creates the base UID for each grid reference to which prefixes and suffixes will be added.
        """
        gzd = self.uids.str[:3]
        k100 = self.uids.str[3:5]
        delimiter = self.delimiter
        # If no coords, use an empty delimiter
        sample_coord = self.uids.iloc[0][5:]
        if sample_coord == '':
            delimiter = ''
        # Divide the coords
        mid = 5 + int(len(sample_coord) / 2)
        coords = self.uids.str[5:mid] + delimiter + self.uids.str[mid:]

        if not self.k100:
            self.uids = coords
        elif not self.gzd:
            self.uids = k100 + delimiter + coords
        else:
            self.uids = gzd + self.delimiter + k100 + delimiter + coords

    def set_prefix(self):
        """
        Adds a prefix to the base UID if provided. If a prefix column is specified, the prefix parameter is not used.
        """
        try:
            if self.prefix_column is not None:
                self.uids = self.prefix_column.str.cat(self.uids, self.delimiter)
            elif self.prefix:
                self.uids = '{}{}'.format(self.prefix, self.delimiter) + self.uids.astype(str)
        except AttributeError as e:
            print(e)

    def set_uid(self):
        """
        Adds a unique number (1, 2, 3,...) to the base UID.
        """
        start = 1
        duplicate = self.uids.duplicated(keep=False)
        unique_suffix = [str(start)] * self.uids[-duplicate].size
        self.uids[-duplicate] = self.uids[-duplicate].str.cat(unique_suffix, sep=self.delimiter)

        # TODO Fix: this is SLOW
        duplicate_uids = set(self.uids[duplicate])
        for uid in duplicate_uids:
            df = self.uids[self.uids == uid]
            unique_suffixes = [str(suffix) for suffix in range(start, start + df.size)]
            self.uids[self.uids == uid] = df.str.cat(unique_suffixes, sep=self.delimiter)
