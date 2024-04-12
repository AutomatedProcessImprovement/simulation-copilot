"""Relational simulation model that is compatible with Prosimos."""

from .base import _Base as Base

# Import all other dependent models to properly initialize Base
from .calendar import *
from .case_arrival import *
from .distribution import *
from .gateway import *
from .resource_profile import *
from .simulation_model import *
