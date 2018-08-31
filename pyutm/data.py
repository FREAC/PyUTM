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


def from_csv(data, columns):

    try:
        df = None
        error = None
        df = pandas.read_csv(data)
        if isinstance(columns, (tuple, list)):
            # Input CSV cannot have 0 as a column name
            df.insert(0, 0, tuple(zip(df[columns[0]], df[columns[1]])))
        else:
            raise KeyError
    except (FileNotFoundError, KeyError, IndexError, ValueError) as e:
        df = None
        if type(e).__name__ == 'KeyError':
            err_message = 'Column error: {}'
            if str(e) == '':
                error = err_message.format(columns)
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
