"""Prosimos simulation API.

simulation_model.py is the main module with the BPSModel class for constructing simulation models
which can be converted to a Prosimos-compatible JSON file.

Typical usage example:

model = BPSModel()
model.process_model = ...
...
json.dump(model.to_prosimos_format(), file)
"""
