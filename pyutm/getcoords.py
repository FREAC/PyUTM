def from_list(data, col):

    coords = ()
    xs = None
    ys = None
    error = None
    try:
        # Grab the column containing coordinates if applicable
        if col is not None:
            coords = tuple(zip(*data))[col]
        else:
            if not isinstance(data[0], (tuple, list)) and not isinstance(data[1], (tuple, list)):
                coords = [(data[0], data[1])]
            else:
                coords = data
        xs = tuple(coord[0] for coord in coords)
        ys = tuple(coord[1] for coord in coords)
    except (TypeError, IndexError):
        error = 'Invalid coordinates: {}'.format(coords)
    finally:
        return xs, ys, error


def from_csv(data, col1, col2):

    import pandas
    xs = None
    ys = None
    error = None
    try:
        df = pandas.read_csv(data)
        xs = df[col1].values
        ys = df[col2].values
    except (FileNotFoundError, KeyError) as e:
        if type(e).__name__ == 'KeyError':
            error = 'Invalid column names: col1={}, col2={}'.format(col1, col2)
        else:
            error = e
    finally:
        return xs, ys, error


def from_shapefile(data):

    import shapefile
    xs = None
    ys = None
    error = None
    try:
        sf = shapefile.Reader(data)
        shapes = sf.shapes()
        # Only accept Point, PointZ and PointM geometries
        if shapes[0].shapeType in (1, 11, 21):
            xs = tuple(shape.points[0][0] for shape in shapes)
            ys = tuple(shape.points[0][1] for shape in shapes)
    except shapefile.ShapefileException as e:
        error = e
    finally:
        return xs, ys, error
