# PyUTM

PyUTM is a Python package that creates UTM (and UPS) grid references for point data.
It can also use those grid references to create spatially meaningful unique identifiers for tasks such as asset naming.

### What is a UTM grid reference?

The *Universal Transverse Mercator* (UTM) projection and grid allows any location in the world to be described by a
string of up to 15 characters. The precision of a location increases as characters are added to its description and
decreases as characters are removed.

The first three characters of a UTM grid reference describe its *Grid Zone Designation* (GZD). With some exceptions in
the northern latitudes, the GZD describes an area encompassing 6° of longitude and 8° of latitude.

The next two characters of a UTM grid reference describe its 100 kilometer square within the GZD.

The final characters of a UTM grid reference describe its distance in meters from the lower left corner
of the 100km square. The first set of digits describes the location's distance east of the lower left corner
(its *Easting*); the second set describes the location's distance north of the lower left corner
(its *Northing*). The number of digits used in a set determines the number of meters that the digits
represent: as the number of digits increases, so does the precision with which a location can be established. 

<center>

Number of Digits | Number of Meters | Location Precision
:---: | :---: | :---:
One | 10 000 | Local Area
Two | 1 000 | Neighborhood
Three | 100 | Football Field
Four | 10 | House
Five | 1 | Bath towel

</center>


## Installation
To install PyUTM, use PyPI:
```
pip install pyutm
```
*N.B. Python 2.7 users must install the
[Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
before using this package.*
##Examples
