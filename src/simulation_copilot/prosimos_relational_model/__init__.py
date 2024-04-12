"""Relational simulation model that is compatible with Prosimos.

Relational model allows to store and retrieve simulation models from a relational database
rather than a JSON file or in-memory data structure.
"""

from .base import _Base as Base

# Import all other dependent models to properly initialize Base
from .calendar import *
from .case_arrival import *
from .distribution import *
from .gateway import *
from .resource_profile import *
from .simulation_model import *
