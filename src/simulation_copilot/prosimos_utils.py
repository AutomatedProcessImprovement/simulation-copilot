"""Prosimos simulator utilities, e.g., for running simulations, handling the performance report."""
import json
import tempfile
from pathlib import Path

from prosimos.simulation_engine import run_simulation as run_prosimos_simulation

from simulation_copilot.database import get_session
from simulation_copilot.relational_to_prosimos_adapter import create_simulation_model_from_relational_data


def get_resource_utilization_and_overall_statistics(report: str) -> str:
    """
    Extracts only the resource utilization and overall simulation statistics sections.
    """
    utilization, statistics = split_prosimos_report(report)
    return f"{utilization.strip()}\n{statistics.strip()}"


def split_prosimos_report(report: str) -> tuple[str, str]:
    """
    Splits the performance report into separate documents because the initial report is composed of 3 CSV tables
    in one text file separated by `""`.
    """
    # report has 4 sections: start and end times; resource utilization, task statistics, simulation statistics
    sections = report.split('""')
    resource_utilization = sections[1]
    overall_statistics = sections[3]
    return resource_utilization, overall_statistics


def run_prosimos(model_id: int, process_path: Path) -> str:
    """
    Runs the simulation with the given model ID. Returns the simulation performance report.
    """
    with get_session() as session:
        bps_model = create_simulation_model_from_relational_data(session, model_id)
        simulation_attributes = bps_model.to_prosimos_format(process_model=process_path)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            # save the simulation model to a temporary file
            json.dump(simulation_attributes, f)
            f.flush()  # otherwise, the file content is truncated
            simulation_report_path = Path(f.name).with_suffix(".csv")

            # run simulation
            run_prosimos_simulation(
                bpmn_path=process_path,
                json_path=f.name,
                total_cases=100,
                stat_out_path=simulation_report_path,
            )
            with open(simulation_report_path, "r", encoding="utf-8") as report_file:
                report = report_file.read()
    return report
