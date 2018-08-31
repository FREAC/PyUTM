import pandas


def from_list(data):

    try:
        import numpy
        df = None
        error = None
        dim = numpy.array(data, ndmin=2).shape
        if dim[1] == 2:
            if dim[0] == 1:
                df = pandas.DataFrame({0: [data]})
            elif not isinstance(data[0][0], (tuple, list)):
                df = pandas.DataFrame({0: data})
            else:
                df = pandas.DataFrame.from_records(data)
        else:
            df = pandas.DataFrame.from_records(data)
    except AssertionError as e:
        df = None
        error = e
    finally:
        return df, error


def from_list2(data, columns):

    try:
        df = None
        error = None
        if columns:
            # all nested lists are columns
            df = pandas.DataFrame.from_records(data)
        else:
            # if there is no column, it is not a nested list
            pass

        if dim[1] == 2:
            if dim[0] == 1:
                df = pandas.DataFrame({0: [data]})
            elif not isinstance(data[0][0], (tuple, list)):
                df = pandas.DataFrame({0: data})
            else:
                df = pandas.DataFrame.from_records(data)
        else:
            df = pandas.DataFrame.from_records(data)
    except AssertionError as e:
        df = None
        error = e
    finally:
        return df, error


def from_csv(data, columns):
    # Input CSV cannot have 0 as a column name
    try:
        df = None
        error = None
        df = pandas.read_csv(data)

        if len(columns) == 1:
            print('here')
            df.insert(0, 0, df[columns[0]])
        else:
            df.insert(0, 0, tuple(zip(df[columns[0]], df[columns[1]])))
    except (FileNotFoundError, KeyError, IndexError, ValueError) as e:
        df = None
        if type(e).__name__ == 'KeyError':
            err_message = 'Column error: {}'
            if str(e) == '':
                error = err_message.format('Must be integer, tuple or list')
            else:
                error = err_message.format(e)
        else:
            error = e
    finally:
        return df, error


def from_shapefile(data):

    try:
        import shapefile
        df = None
        error = None
        sf = shapefile.Reader(data)
        # Only accept Point, PointZ and PointM geometries
        if sf.shapes()[0].shapeType in (1, 11, 21):
            fields = [attribute[0] for attribute in sf.fields[1:]]
            records = sf.records()
            geometry = [shape.points[0] for shape in sf.shapes()]
            df = pandas.DataFrame(columns=fields, data=records)
            df.insert(0, 0, geometry)
    except (AttributeError, shapefile.ShapefileException) as e:
        df = None
        error = e
    finally:
        return df, error
