from sqlalchemy.ext.declarative import declarative_base

# _Base is package-private here to discourage its import from the base module.
# Instead, the Base class should be imported from the __init__.py module.
_Base = declarative_base()
