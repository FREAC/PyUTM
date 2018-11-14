import pyutm.main as main


def test_0_0():

    lonlat = (0.0, 0.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[0.0, 0.0, '31NAA66020000']]


def test_rounding():

    lonlat = (-93.0, 44.99995)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[-93.0, 44.99995, '15TWK00008294']]


def test_coords():

    lonlat = (-77.043, 38.894)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[-77.043, 38.894, '18SUJ22820699']]


def test_long_coords():

    lonlat = (-93.12456789, 44.876000000000005)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[-93.12456789, 44.876000000000005, '15TVK90166918']]


def test_invalid_lon():

    lonlat = (267.11, 45.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[267.11, 45.0, None]]


def test_invalid_lat():

    lonlat = (15.0, 92.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[15.0, 92.0, None]]


def test_utm_ref_en():

    lonlat = (40.0, 70.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[40.0, 70.0, '37WET38166618']]


def test_utm_ref_es():

    lonlat = (40.0, -70.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[40.0, -70.0, '37DEC38163381']]


def test_utm_ref_wn():

    lonlat = (-40.0, 70.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[-40.0, 70.0, '24WVC61836618']]


def test_utm_ref_ws():

    lonlat = (-40.0, -70.0)
    g = main.Grid(lonlat)
    refs = g.write_refs()
    assert refs == [[-40.0, -70.0, '24DVH61833381']]


def test_utm_coord():

    lonlat = (-79.387139, 43.642567)
    g = main.Grid(lonlat)
    refs = g.write_utms()
    assert refs == [[-79.387139, 43.642567, '17T 0630084 4833438']]


# def test_ups_ref_en():
#
#     lonlat = (40.0, 84.1)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[40.0, 84.1, 'ZGB21409778']]
#
#
# def test_ups_ref_es():
#
#     lonlat = (40.0, -80.1)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[40.0, -80.1, 'BKW08204400']]
#
#
# def test_ups_ref_wn():
#
#     lonlat = (-40.0, 84.1)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[-40.0, 84.1, 'YTB78599778']]
#
#
# def test_ups_ref_ws():
#
#     lonlat = (-40.0, -80.1)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[-40.0, -80.1, 'AQW91794400']]
#
#
# def test_ups_ref_en2():
#
#     lonlat = (40.0, 88.0)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[40.0, 88.0, 'ZBF42742988']]
#
#
# def test_ups_ref_es2():
#
#     lonlat = (40.0, -88.0)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[40.0, -88.0, 'BBP42747011']]
#
#
# def test_ups_ref_wn2():
#
#     lonlat = (-40.0, 88.0)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[-40.0, 88.0, 'YYF57252988']]
#
#
# def test_ups_ref_ws2():
#
#     lonlat = (-40.0, -88.0)
#     g = main.Grid(lonlat)
#     refs = g.write_refs()
#     assert refs == [[-40.0, -88.0, 'AYP57257011']]
