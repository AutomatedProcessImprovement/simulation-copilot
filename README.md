# Simulation Copilot

A prototype to explore a possibility to handle simulation scenario generation using the conversational UI.

## Milestones

- [x] Generate a single component of the scenario with Python code (calendars)
- [x] Generate a single component of the scenario with LLM (calendars)
- [ ] Generate the resource model with Python code
- [ ] Generate the resource model with LLM
- [ ] Generate a simple scenario with Python code
- [ ] Generate a simple scenario with LLM using the Python code as a "tool"
- [ ] Provide a simple scenario and ask LLM to apply some changes
- [ ] Increase complexity: add more components of the simulation scenario or more adjustments

## Outputs

<details>
<summary>Generating calendars</summary>

Python code calling the agent:

```python
agent_executor.invoke(
    {
        "input": "generate a calendar for a resource that works 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
    }
)
```

Output:

```shell
python simulation_copilot/demo_agent_calendar.py


> Entering new AgentExecutor chain...

Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Wednesday', 'start_time': '08:30', 'end_time': '19:30'}, {'start_day': 'Thursday', 'end_day': 'Friday', 'start_time': '11:00', 'end_time': '21:00'}, {'start_day': 'Saturday', 'end_day': 'Sunday', 'start_time': '09:00', 'end_time': '17:00'}]}`


id='34e802feda8c4c6fa691b5b39025b259' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.WEDNESDAY: 'Wednesday'>, start_time=Time(hour=8, minute=30), end_time=Time(hour=19, minute=30)), CalendarInterval(start_day=<Day.THURSDAY: 'Thursday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=11, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0))]

The calendar for the resource is as follows:
- Monday to Wednesday: 8:30 AM to 7:30 PM
- Thursday and Friday: 11:00 AM to 9:00 PM
- Saturday and Sunday: 9:00 AM to 5:00 PM

This calendar defines the working hours for the resource across different days of the week.

> Finished chain.
{'input': 'generate a calendar for a resource that works 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday.', 'output': 'The calendar for the resource is as follows:\n- Monday to Wednesday: 8:30 AM to 7:30 PM\n- Thursday and Friday: 11:00 AM to 9:00 PM\n- Saturday and Sunday: 9:00 AM to 5:00 PM\n\nThis calendar defines the working hours for the resource across different days of the week.'}
```

</details>

<details>
<summary>Generating resource profiles</summary>

Python code calling the agent:

```python
agent_executor.invoke(
    {
        "input": "generate a resource profile for the resource Operator with a quantity of 4, cost 20 EUR per hour who works on activities A, B, and C."
    }
)
```

Output:

```shell
python simulation_copilot/generating_calendars.py 


> Entering new AgentExecutor chain...

Invoking: `generate_resource_profile` with `{'resources': [{'resource_name': 'Operator', 'amount': 4, 'cost_per_hour': 20, 'calendar_id': 'calendar_1', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 3]}}, {'activity_id': 'B', 'distribution': {'name': 'normal', 'parameters': [2, 1]}}, {'activity_id': 'C', 'distribution': {'name': 'exponential', 'parameters': [0.5]}}]}]}`


id='a0295575ba574ce38ade560ca74430b1' resources=[Resource(id='309d3635626647689db9f316c90dee62', name='Operator', amount=4, cost_per_hour=20.0, calendar_id='calendar_1', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 3.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='normal', parameters=[2.0, 1.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='exponential', parameters=[0.5]))])]

I have generated a resource profile for the resource "Operator" with a quantity of 4, cost of 20 EUR per hour. The resource works on activities A, B, and C with the following distributions:
- Activity A: Uniform distribution with parameters [1, 3]
- Activity B: Normal distribution with parameters [2, 1]
- Activity C: Exponential distribution with parameter 0.5

The resource profile has been created successfully.

> Finished chain.
{'input': 'generate a resource profile for the resource Operator with a quantity of 4, cost 20 EUR per hour who works on activities A, B, and C.', 'output': 'I have generated a resource profile for the resource "Operator" with a quantity of 4, cost of 20 EUR per hour. The resource works on activities A, B, and C with the following distributions:\n- Activity A: Uniform distribution with parameters [1, 3]\n- Activity B: Normal distribution with parameters [2, 1]\n- Activity C: Exponential distribution with parameter 0.5\n\nThe resource profile has been created successfully.'}
```

</details>
