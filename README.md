# Simulation Copilot

A prototype to explore a possibility to handle simulation scenario generation using the conversational UI.

## Milestones

- [x] Generate a single component of the scenario with Python code (calendars)
- [x] Generate a single component of the scenario with LLM (calendars)
- [x] Generate the resource model with Python code
- [x] Generate the resource model with LLM
- [ ] Generate a simple scenario with Python code
- [ ] Generate a simple scenario with LLM using the Python code as a "tool"
- [ ] Provide a simple scenario and ask LLM to apply some changes
- [ ] Increase complexity: add more components of the simulation scenario or more adjustments

## Outputs

<details>
<summary>Generating calendars</summary>

Prompt to the agent:

```python
"input": "generate a calendar for a resource that works 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
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

Prompt to the agent:

```python
"input": "generate a resource profile for the resource Operator with a quantity of 4, cost 20 EUR per hour who works on activities A, B, and C."
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

<details>
<summary>Generating the full resource model</summary>

Prompt to the agent:

```python
"""
Generate a resource model with 2 resource profiles and 2 calendars. 
Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
Resource model has 2 resource profiles, 'Busy' and 'Normal'.
Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
"""
```

Output:

```shell
python simulation_copilot/resource_model_agent.py 


> Entering new AgentExecutor chain...

Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': '08:00', 'end_time': '21:00'}, {'start_day': 'Saturday', 'end_day': 'Saturday', 'start_time': '09:00', 'end_time': '17:00'}, {'start_day': 'Sunday', 'end_day': 'Sunday', 'start_time': '10:00', 'end_time': '16:00'}]}`


id='c9d97e17b09a432fbec1e7f6af46f3ef' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]
Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': '09:00', 'end_time': '17:00'}, {'start_day': 'Saturday', 'end_day': 'Sunday', 'start_time': '10:00', 'end_time': '16:00'}]}`


id='c65451b7340b47b2b781ab275eaa6f8c' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]
Invoking: `generate_resource_model` with `{'calendars': [{'id': 'c9d97e17b09a432fbec1e7f6af46f3ef', 'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': {'hour': 8, 'minute': 0}, 'end_time': {'hour': 21, 'minute': 0}}, {'start_day': 'Saturday', 'end_day': 'Saturday', 'start_time': {'hour': 9, 'minute': 0}, 'end_time': {'hour': 17, 'minute': 0}}, {'start_day': 'Sunday', 'end_day': 'Sunday', 'start_time': {'hour': 10, 'minute': 0}, 'end_time': {'hour': 16, 'minute': 0}}]}, {'id': 'c65451b7340b47b2b781ab275eaa6f8c', 'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': {'hour': 9, 'minute': 0}, 'end_time': {'hour': 17, 'minute': 0}}, {'start_day': 'Saturday', 'end_day': 'Sunday', 'start_time': {'hour': 10, 'minute': 0}, 'end_time': {'hour': 16, 'minute': 0}}]}], 'resource_profiles': [{'id': '1', 'resources': [{'id': '1', 'name': 'Junior', 'amount': 5, 'cost_per_hour': 10, 'calendar_id': 'c9d97e17b09a432fbec1e7f6af46f3ef', 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'Uniform', 'parameters': [1, 10]}}, {'activity_id': 'B', 'distribution': {'name': 'Normal', 'parameters': [5, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'Exponential', 'parameters': [0.5]}}]}, {'id': '2', 'name': 'Senior', 'amount': 3, 'cost_per_hour': 20, 'calendar_id': 'c9d97e17b09a432fbec1e7f6af46f3ef', 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'Uniform', 'parameters': [1, 10]}}, {'activity_id': 'B', 'distribution': {'name': 'Normal', 'parameters': [5, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'Exponential', 'parameters': [0.5]}}]}]}, {'id': '2', 'resources': [{'id': '3', 'name': 'Junior', 'amount': 1, 'cost_per_hour': 10, 'calendar_id': 'c65451b7340b47b2b781ab275eaa6f8c', 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'Uniform', 'parameters': [1, 10]}}, {'activity_id': 'B', 'distribution': {'name': 'Normal', 'parameters': [5, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'Exponential', 'parameters': [0.5]}}]}, {'id': '4', 'name': 'Senior', 'amount': 1, 'cost_per_hour': 20, 'calendar_id': 'c65451b7340b47b2b781ab275eaa6f8c', 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'Uniform', 'parameters': [1, 10]}}, {'activity_id': 'B', 'distribution': {'name': 'Normal', 'parameters': [5, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'Exponential', 'parameters': [0.5]}}]}]}]}`


profiles=[ResourceProfile(id='1', resources=[Resource(id='1', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c9d97e17b09a432fbec1e7f6af46f3ef', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='Uniform', parameters=[1.0, 10.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='Normal', parameters=[5.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='Exponential', parameters=[0.5]))]), Resource(id='2', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c9d97e17b09a432fbec1e7f6af46f3ef', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='Uniform', parameters=[1.0, 10.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='Normal', parameters=[5.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='Exponential', parameters=[0.5]))])]), ResourceProfile(id='2', resources=[Resource(id='3', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='c65451b7340b47b2b781ab275eaa6f8c', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='Uniform', parameters=[1.0, 10.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='Normal', parameters=[5.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='Exponential', parameters=[0.5]))]), Resource(id='4', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='c65451b7340b47b2b781ab275eaa6f8c', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='Uniform', parameters=[1.0, 10.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='Normal', parameters=[5.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='Exponential', parameters=[0.5]))])])] calendars=[Calendar(id='c9d97e17b09a432fbec1e7f6af46f3ef', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='c65451b7340b47b2b781ab275eaa6f8c', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]I have generated the resource model with the following details:

### Resource Profiles:
1. **Profile 'Busy'**:
   - **Resources**:
     - Junior: Quantity 5, Cost per Hour 10 EUR, Assigned Activities A, B, C, Calendar 'BusyHours'
     - Senior: Quantity 3, Cost per Hour 20 EUR, Assigned Activities A, B, C, Calendar 'BusyHours'

2. **Profile 'Normal'**:
   - **Resources**:
     - Junior: Quantity 1, Cost per Hour 10 EUR, Assigned Activities A, B, C, Calendar 'NormalHours'
     - Senior: Quantity 1, Cost per Hour 20 EUR, Assigned Activities A, B, C, Calendar 'NormalHours'

### Calendars:
1. **Calendar 'BusyHours'**:
   - Working Hours:
     - Monday to Friday: 8:00 am to 9:00 pm
     - Saturday: 9:00 am to 5:00 pm
     - Sunday: 10:00 am to 4:00 pm

2. **Calendar 'NormalHours'**:
   - Working Hours:
     - Monday to Friday: 9:00 am to 5:00 pm
     - Saturday and Sunday: 10:00 am to 4:00 pm

This resource model includes the specified resource profiles, resources, assigned activities, and working hours for each calendar.

> Finished chain.
{'input': "\nGenerate a resource model with 2 resource profiles and 2 calendars. \nCalendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.\nCalendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.\nResource model has 2 resource profiles, 'Busy' and 'Normal'.\nProfile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.\nProfile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.\n", 'output': "I have generated the resource model with the following details:\n\n### Resource Profiles:\n1. **Profile 'Busy'**:\n   - **Resources**:\n     - Junior: Quantity 5, Cost per Hour 10 EUR, Assigned Activities A, B, C, Calendar 'BusyHours'\n     - Senior: Quantity 3, Cost per Hour 20 EUR, Assigned Activities A, B, C, Calendar 'BusyHours'\n\n2. **Profile 'Normal'**:\n   - **Resources**:\n     - Junior: Quantity 1, Cost per Hour 10 EUR, Assigned Activities A, B, C, Calendar 'NormalHours'\n     - Senior: Quantity 1, Cost per Hour 20 EUR, Assigned Activities A, B, C, Calendar 'NormalHours'\n\n### Calendars:\n1. **Calendar 'BusyHours'**:\n   - Working Hours:\n     - Monday to Friday: 8:00 am to 9:00 pm\n     - Saturday: 9:00 am to 5:00 pm\n     - Sunday: 10:00 am to 4:00 pm\n\n2. **Calendar 'NormalHours'**:\n   - Working Hours:\n     - Monday to Friday: 9:00 am to 5:00 pm\n     - Saturday and Sunday: 10:00 am to 4:00 pm\n\nThis resource model includes the specified resource profiles, resources, assigned activities, and working hours for each calendar."}
```

</details>