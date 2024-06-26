"""
This file has been initially copied from Simod.

Ideally, this API should be part of the PIX framework, but it is part of Simod for now.
Additionally, this module includes new helper functions not present in the Simod's version, e.g.,
the `BPSModel.from_prosimos_format` function helps to read the Prosimos JSON parameters and create a BPSModel object.
"""

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from pix_framework.discovery.case_arrival import CaseArrivalModel
from pix_framework.discovery.gateway_probabilities import GatewayProbabilities
from pix_framework.discovery.resource_calendar_and_performance.fuzzy.resource_calendar import FuzzyResourceCalendar
from pix_framework.discovery.resource_model import ResourceModel
from pix_framework.io.bpmn import get_activities_ids_by_name_from_bpmn

from simulation_copilot.prosimos_model.batching import BatchingRule
from simulation_copilot.prosimos_model.case_attribute import CaseAttribute
from simulation_copilot.prosimos_model.extraneous import ExtraneousDelay
from simulation_copilot.prosimos_model.prioritization import PrioritizationRule

# Keys for serialization
PROCESS_MODEL_KEY = "process_model"
GATEWAY_PROBABILITIES_KEY = "gateway_branching_probabilities"
CASE_ARRIVAL_DISTRIBUTION_KEY = "arrival_time_distribution"
CASE_ARRIVAL_CALENDAR_KEY = "arrival_time_calendar"
RESOURCE_PROFILES_KEY = "resource_profiles"
RESOURCE_CALENDARS_KEY = "resource_calendars"
RESOURCE_ACTIVITY_PERFORMANCE_KEY = "task_resource_distribution"
EXTRANEOUS_DELAYS_KEY = "event_distribution"
CASE_ATTRIBUTES_KEY = "case_attributes"
PRIORITIZATION_RULES_KEY = "prioritisation_rules"
BATCHING_RULES_KEY = "batch_processing"


@dataclass
class BPSModel:
    """
    BPS model class containing all the components to simulate a business process model.
    """

    # pylint: disable=too-many-instance-attributes

    process_model: Optional[Path] = None  # A path to the model for now, in future the loaded BPMN model
    gateway_probabilities: Optional[List[GatewayProbabilities]] = None
    case_arrival_model: Optional[CaseArrivalModel] = None
    resource_model: Optional[ResourceModel] = None
    extraneous_delays: Optional[List[ExtraneousDelay]] = None
    case_attributes: Optional[List[CaseAttribute]] = None
    prioritization_rules: Optional[List[PrioritizationRule]] = None
    batching_rules: Optional[List[BatchingRule]] = None
    calendar_granularity: Optional[int] = None

    @staticmethod
    def from_prosimos_format(attributes: dict, process_model: Optional[Path] = None) -> "BPSModel":
        """
        Constructs a BPSModel object from the Prosimos JSON parameters.
        """
        if not process_model:
            process_model = Path(attributes.get(PROCESS_MODEL_KEY))
        gateway_probabilities = [
            GatewayProbabilities.from_dict(gateway_probability)
            for gateway_probability in attributes.get(GATEWAY_PROBABILITIES_KEY, [])
        ]
        case_arrival_model = CaseArrivalModel.from_dict(
            {
                CASE_ARRIVAL_DISTRIBUTION_KEY: attributes.get(CASE_ARRIVAL_DISTRIBUTION_KEY),
                CASE_ARRIVAL_CALENDAR_KEY: attributes.get(CASE_ARRIVAL_CALENDAR_KEY),
            }
        )
        resource_model = ResourceModel.from_dict(
            {
                RESOURCE_PROFILES_KEY: attributes.get(RESOURCE_PROFILES_KEY),
                RESOURCE_CALENDARS_KEY: attributes.get(RESOURCE_CALENDARS_KEY),
                RESOURCE_ACTIVITY_PERFORMANCE_KEY: attributes.get(RESOURCE_ACTIVITY_PERFORMANCE_KEY),
            }
        )
        extraneous_delays = [
            ExtraneousDelay.from_dict(extraneous_delay)
            for extraneous_delay in attributes.get(EXTRANEOUS_DELAYS_KEY, [])
        ]
        case_attributes = [
            CaseAttribute.from_dict(case_attribute) for case_attribute in attributes.get(CASE_ATTRIBUTES_KEY, [])
        ]
        prioritization_rules = [
            PrioritizationRule.from_prosimos(priority_rule)
            for priority_rule in attributes.get(PRIORITIZATION_RULES_KEY, [])
        ]
        activities_ids_by_name = get_activities_ids_by_name_from_bpmn(process_model)
        activities_names_by_id = {v: k for k, v in activities_ids_by_name.items()}
        batching_rules = [
            BatchingRule.from_prosimos(batching_rule, activities_names_by_id)
            for batching_rule in attributes.get(BATCHING_RULES_KEY, [])
        ]
        calendar_granularity = attributes.get("granule_size", {}).get("value")

        return BPSModel(
            process_model=process_model,
            gateway_probabilities=gateway_probabilities,
            case_arrival_model=case_arrival_model,
            resource_model=resource_model,
            extraneous_delays=extraneous_delays,
            case_attributes=case_attributes,
            prioritization_rules=prioritization_rules,
            batching_rules=batching_rules,
            calendar_granularity=calendar_granularity,
        )

    def to_prosimos_format(self, process_model: Optional[Path] = None) -> dict:
        """
        Converts the BPSModel object to the Prosimos dictionary which can be saved as JSON file for Prosimos use.
        """
        if process_model:
            self.process_model = process_model

        # Get map activity label -> node ID
        activity_label_to_id = get_activities_ids_by_name_from_bpmn(self.process_model)

        attributes = {}
        if self.process_model is not None:
            attributes[PROCESS_MODEL_KEY] = str(self.process_model)
        if self.gateway_probabilities is not None:
            attributes[GATEWAY_PROBABILITIES_KEY] = [
                gateway_probability.to_dict() for gateway_probability in self.gateway_probabilities
            ]
        if self.case_arrival_model is not None:
            attributes |= self.case_arrival_model.to_dict()
        if self.resource_model is not None:
            attributes |= self.resource_model.to_dict()
        if self.extraneous_delays is not None:
            attributes[EXTRANEOUS_DELAYS_KEY] = [
                extraneous_delay.to_dict() for extraneous_delay in self.extraneous_delays
            ]
        if self.case_attributes is not None:
            attributes[CASE_ATTRIBUTES_KEY] = [case_attribute.to_prosimos() for case_attribute in self.case_attributes]
        if self.prioritization_rules is not None:
            attributes[PRIORITIZATION_RULES_KEY] = [
                priority_rule.to_prosimos() for priority_rule in self.prioritization_rules
            ]
        if self.batching_rules is not None:
            attributes[BATCHING_RULES_KEY] = [
                batching_rule.to_prosimos(activity_label_to_id) for batching_rule in self.batching_rules
            ]
        if isinstance(self.resource_model.resource_calendars[0], FuzzyResourceCalendar):
            attributes["model_type"] = "FUZZY"
        else:
            attributes["model_type"] = "CRISP"
        attributes["granule_size"] = {"value": self.calendar_granularity, "time_unit": "MINUTES"}

        return attributes

    def deep_copy(self) -> "BPSModel":
        """Creates a deep copy of the BPSModel object."""
        return copy.deepcopy(self)

    def replace_activity_names_with_ids(self):
        """
        Updates activity labels with activity IDs from the current (BPMN) process model.

        In BPSModel, the activities are referenced by their name, Prosimos uses IDs instead from the BPMN model.
        """
        # Get map activity label -> node ID
        activity_label_to_id = get_activities_ids_by_name_from_bpmn(self.process_model)
        # Update activity labels in resource profiles
        if self.resource_model.resource_profiles is not None:
            for resource_profile in self.resource_model.resource_profiles:
                for resource in resource_profile.resources:
                    resource.assigned_tasks = [
                        activity_label_to_id[activity_label] for activity_label in resource.assigned_tasks
                    ]
        # Update activity labels in activity-resource performance
        if self.resource_model.activity_resource_distributions is not None:
            for activity_resource_distributions in self.resource_model.activity_resource_distributions:
                activity_resource_distributions.activity_id = activity_label_to_id[
                    activity_resource_distributions.activity_id
                ]
