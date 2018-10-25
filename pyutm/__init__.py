from pkg_resources import get_distribution

__version__ = get_distribution('pyutm').version

from main import Grid

