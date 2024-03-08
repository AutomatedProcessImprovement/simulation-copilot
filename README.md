# Simulation Copilot

A prototype to explore a possibility to handle simulation scenario generation using conversational UI.

## Approaches

- Agent-based using tools
  - Basic using Python functions for composing BPS models
  - Using storage to make incremental changes (SQL)
- Extractors
- Multi-agent

## Milestones

- [x] Generate a single component of the scenario with Python code (calendars)
- [x] Generate a single component of the scenario with LLM (calendars)
- [x] Generate the resource model with Python code
- [x] Generate the resource model with LLM
- [x] Generate a simple scenario with Python code
- [x] Generate a simple scenario with LLM using the Python code as a "tool"
- [x] Provide a simple scenario and ask LLM to apply some changes
- [ ] Try storing the simulation model in a SQL format and query with `pandas.sql`
- [ ] Increase complexity: add more components of the simulation scenario or more adjustments
- [ ] Change average activity duration by N hours (models should change the mean value of the distribution of a certain activity)

## SQL-based approach outputs

<details><summary>Creating a calendar</summary>

```shell
> Entering new AgentExecutor chain...

Invoking: `run_sql` with `{'sql': 'INSERT INTO calendars DEFAULT VALUES;'}`


<sqlalchemy.engine.cursor.CursorResult object at 0x14b324640>
Invoking: `run_sql` with `{'sql': 'SELECT id FROM calendars ORDER BY id DESC LIMIT 1;'}`


<sqlalchemy.engine.cursor.CursorResult object at 0x14b1951c0>
Invoking: `run_sql` with `{'sql': "INSERT INTO calendar_intervals (start_day, end_day, start_time_hour, start_time_minute, end_time_hour, end_time_minute, calendar_id) VALUES ('Monday', 'Wednesday', 8, 30, 19, 30, '1'), ('Thursday', 'Friday', 11, 0, 21, 0, '1'), ('Saturday', 'Sunday', 9, 0, 17, 0, '1');"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x12ef92340>The calendar has been created successfully, and the ID of the calendar is **1**.

> Finished chain.
{'input': 'Using the SQL tool, create a calendar with the following intervals and give me back the ID of the calendar: 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday.', 'output': 'The calendar has been created successfully, and the ID of the calendar is **1**.'}
```

</details>

<details><summary>Modifying a calendar</summary>

```shell
> Entering new AgentExecutor chain...

Invoking: `run_sql` with `{'sql': "UPDATE calendar_intervals SET start_time_hour = 14, start_time_minute = 0, end_time_hour = 21, end_time_minute = 0 WHERE calendar_id = '1' AND (start_day = 'Saturday' OR start_day = 'Sunday')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x1473f2460>The weekend working hours for the calendar with ID = 1 have been successfully updated to be from 2pm to 9pm.

> Finished chain.
{'input': 'Modify calendar with ID = 1 the week-end working hours, make it from 2pm to 9pm.', 'output': 'The weekend working hours for the calendar with ID = 1 have been successfully updated to be from 2pm to 9pm.'}
```

</details>

<details><summary>Create a resource profile with resources, calendars, and assigned activities distributions</summary>

```shell
python simulation_copilot/simulation_model_agent_sql.py

Instructions: You are an assistant who helps with preparing of a business process simulation model.
The model is represented by a set of tables in a SQL database.
Reuse calendars for resources if possible.

Below are the SQL schemas for available models.

Note: In activity distributions, the distribution name is the name of the distribution
and the parameters is a list of parameters for this specific distribution serialized as a string joined with a comma.

Note: Always use full column qualifiers in the SQL statement.

Note: If you you are lacking some information, you can query the database given the table schemas below.
Always try to figure out the information from the database first before asking the user.

CREATE TABLE calendar_intervals (
	id INTEGER NOT NULL,
	start_day VARCHAR(9) NOT NULL,
	end_day VARCHAR(9) NOT NULL,
	start_time_hour INTEGER NOT NULL,
	start_time_minute INTEGER NOT NULL,
	end_time_hour INTEGER NOT NULL,
	end_time_minute INTEGER NOT NULL,
	calendar_id VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(calendar_id) REFERENCES calendars (id)
)


CREATE TABLE calendars (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
)


CREATE TABLE activities (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	resource_id VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(resource_id) REFERENCES resources (id)
)


CREATE TABLE distribution_parameters (
	id INTEGER NOT NULL,
	activity_distribution_id VARCHAR NOT NULL,
	parameter_name VARCHAR NOT NULL,
	parameter_value FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(activity_distribution_id) REFERENCES activity_distributions (id)
)


CREATE TABLE activity_distributions (
	id INTEGER NOT NULL,
	resource_id VARCHAR NOT NULL,
	activity_id VARCHAR NOT NULL,
	distribution_name VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(resource_id) REFERENCES resources (id),
	FOREIGN KEY(activity_id) REFERENCES activities (id)
)


CREATE TABLE resources (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	amount INTEGER NOT NULL,
	cost_per_hour FLOAT NOT NULL,
	calendar_id VARCHAR NOT NULL,
	profile_id VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(calendar_id) REFERENCES calendars (id),
	FOREIGN KEY(profile_id) REFERENCES resource_profiles (id)
)


CREATE TABLE resource_profiles (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	PRIMARY KEY (id)
)




> Entering new AgentExecutor chain...

Invoking: `run_sql` with `{'sql': "INSERT INTO resource_profiles (id, name) VALUES (1, 'Basic')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b7c100>
Invoking: `run_sql` with `{'sql': 'INSERT INTO calendars (id) VALUES (1)'}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b7c640>
Invoking: `run_sql` with `{'sql': "INSERT INTO calendar_intervals (id, start_day, end_day, start_time_hour, start_time_minute, end_time_hour, end_time_minute, calendar_id) VALUES (1, 'Monday', 'Friday', 9, 0, 12, 0, '1'), (2, 'Monday', 'Friday', 13, 0, 17, 0, '1')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b53760>
Invoking: `run_sql` with `{'sql': "INSERT INTO resources (id, name, amount, cost_per_hour, calendar_id, profile_id) VALUES (1, 'Junior', 3, 20.0, '1', '1'), (2, 'Senior', 2, 30.0, '1', '1')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b7c1c0>
Invoking: `run_sql` with `{'sql': "INSERT INTO activities (id, name, resource_id) VALUES (1, 'A', '1'), (2, 'B', '2')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b7c4c0>
Invoking: `run_sql` with `{'sql': "INSERT INTO activity_distributions (id, resource_id, activity_id, distribution_name) VALUES ('1', '1', '1', 'Normal'), ('2', '2', '2', 'Normal')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b7cc40>
Invoking: `run_sql` with `{'sql': "INSERT INTO distribution_parameters (id, activity_distribution_id, parameter_name, parameter_value) VALUES (1, '1', 'mean', 60.0), (2, '1', 'stddev', 2.0), (3, '2', 'mean', 15.0), (4, '2', 'stddev', 3.0)"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x127b7c940>I have created a basic resource profile named 'Basic' with two resources: 'Junior' and 'Senior'. They work from 9 am to 5 pm Monday to Friday with a 1-hour lunch break. There are 3 Juniors at $20/hour and 2 Seniors at $30/hour. The Junior is assigned to activity 'A' with a normal distribution (mean 60, standard deviation 2), and the Senior is assigned to activity 'B' with a normal distribution (mean 15, standard deviation 3).

> Finished chain.
{'input': "\nCreate a basic resource profile with two resources with names 'Junior' and 'Senior'\nwho work from 9am to 5pm Monday to Friday with a 1-hour lunch break.\nThere're 3 Juniors and 2 Seniors.\nThe Juniors cost $20/hour and the Seniors cost $30/hour.\nThe Junior is assigned to activity 'A' with a normal distribution with mean 60 and standard deviation 2.\nThe Senior is assigned to activity 'B' with a normal distribution with mean 15 and standard deviation 3.\n", 'output': "I have created a basic resource profile named 'Basic' with two resources: 'Junior' and 'Senior'. They work from 9 am to 5 pm Monday to Friday with a 1-hour lunch break. There are 3 Juniors at $20/hour and 2 Seniors at $30/hour. The Junior is assigned to activity 'A' with a normal distribution (mean 60, standard deviation 2), and the Senior is assigned to activity 'B' with a normal distribution (mean 15, standard deviation 3)."}
```

</details>

<details><summary>Modifying a the mean distribution parameter for the 'Junior'
resource's activity 'A'</summary>

```shell
python simulation_copilot/simulation_model_agent_sql.py
Instructions: You are an assistant who helps with preparing of a business process simulation model.
The model is represented by a set of tables in a SQL database.
Reuse calendars for resources if possible.

Below are the SQL schemas for available models.

Note: In activity distributions, the distribution name is the name of the distribution
and the parameters is a list of parameters for this specific distribution serialized as a string joined with a comma.

Note: Always use full column qualifiers in the SQL statement.

Note: If you you are lacking some information, you can query the database given the table schemas below.
Always try to figure out the information from the database first before asking the user.

CREATE TABLE calendar_intervals (
	id INTEGER NOT NULL,
	start_day VARCHAR(9) NOT NULL,
	end_day VARCHAR(9) NOT NULL,
	start_time_hour INTEGER NOT NULL,
	start_time_minute INTEGER NOT NULL,
	end_time_hour INTEGER NOT NULL,
	end_time_minute INTEGER NOT NULL,
	calendar_id VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(calendar_id) REFERENCES calendars (id)
)


CREATE TABLE calendars (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
)


CREATE TABLE activities (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	resource_id VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(resource_id) REFERENCES resources (id)
)


CREATE TABLE distribution_parameters (
	id INTEGER NOT NULL,
	activity_distribution_id VARCHAR NOT NULL,
	parameter_name VARCHAR NOT NULL,
	parameter_value FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(activity_distribution_id) REFERENCES activity_distributions (id)
)


CREATE TABLE activity_distributions (
	id INTEGER NOT NULL,
	resource_id VARCHAR NOT NULL,
	activity_id VARCHAR NOT NULL,
	distribution_name VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(resource_id) REFERENCES resources (id),
	FOREIGN KEY(activity_id) REFERENCES activities (id)
)


CREATE TABLE resources (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	amount INTEGER NOT NULL,
	cost_per_hour FLOAT NOT NULL,
	calendar_id VARCHAR NOT NULL,
	profile_id VARCHAR NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(calendar_id) REFERENCES calendars (id),
	FOREIGN KEY(profile_id) REFERENCES resource_profiles (id)
)


CREATE TABLE resource_profiles (
	id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	PRIMARY KEY (id)
)




> Entering new AgentExecutor chain...

Invoking: `run_sql` with `{'sql': "SELECT activity_distributions.id, distribution_parameters.id AS param_id, distribution_parameters.parameter_name FROM activities JOIN activity_distributions ON activities.id = activity_distributions.activity_id JOIN distribution_parameters ON activity_distributions.id = distribution_parameters.activity_distribution_id WHERE activities.name = 'A' AND distribution_parameters.parameter_name = 'mean'"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x13c0bc160>
Invoking: `run_sql` with `{'sql': "SELECT resources.id FROM resources WHERE resources.name = 'Junior'"}`
responded: I have identified the distribution parameter related to the mean time for activity 'A'. However, to accurately update the distribution for the "Junior" resource, I need to identify the specific distribution associated with the "Junior" resource. Let me proceed to find that information.

<sqlalchemy.engine.cursor.CursorResult object at 0x13c095580>
Invoking: `run_sql` with `{'sql': "SELECT activity_distributions.id, distribution_parameters.id AS param_id FROM activities JOIN activity_distributions ON activities.id = activity_distributions.activity_id JOIN distribution_parameters ON activity_distributions.id = distribution_parameters.activity_distribution_id JOIN resources ON activity_distributions.resource_id = resources.id WHERE activities.name = 'A' AND distribution_parameters.parameter_name = 'mean' AND resources.name = 'Junior'"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x13c0bc640>
Invoking: `run_sql` with `{'sql': "UPDATE distribution_parameters SET parameter_value = 90 WHERE id = (SELECT distribution_parameters.id FROM activities JOIN activity_distributions ON activities.id = activity_distributions.activity_id JOIN distribution_parameters ON activity_distributions.id = distribution_parameters.activity_distribution_id JOIN resources ON activity_distributions.resource_id = resources.id WHERE activities.name = 'A' AND distribution_parameters.parameter_name = 'mean' AND resources.name = 'Junior')"}`


<sqlalchemy.engine.cursor.CursorResult object at 0x13c0bc9a0>The mean time for activity 'A' associated with the "Junior" resource has been successfully updated to 90 minutes. If there's anything more you need, feel free to ask!

> Finished chain.
{'input': "\nThe mean time for activity 'A' has increased to 90 minutes.\nUpdate the distribution for the Junior resource.\n", 'output': 'The mean time for activity \'A\' associated with the "Junior" resource has been successfully updated to 90 minutes. If there\'s anything more you need, feel free to ask!'}
```

</details>

## Pure Python approach outputs

<details>
<summary>Generating calendars</summary>

Prompt to the agent (model: gpt-3.5-turbo):

```python
"generate a calendar for a resource that works 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
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

Prompt to the agent (model: gpt-3.5-turbo):

```python
"generate a resource profile for the resource Operator with a quantity of 4, cost 20 EUR per hour who works on activities A, B, and C."
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

Prompt to the agent (model: gpt-3.5-turbo):

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

<details>
<summary>Generating a simplified simulation model</summary>

Prompt to the agent (model: gpt-4-0125-preview):

```python
"""
Generate a simulation model with a resource model with 2 resource profiles, which has 2 calendars, and gateway probabilties.
Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
Resource model has 2 resource profiles, 'Busy' and 'Normal'.
Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
Also, add gateway probabilities for the gateways 'Gateway1' and 'Gateway2' with the outgoing sequence flows 'SequenceFlow1' and 'SequenceFlow2' with the probabilities 0.3 and 0.7 for 'Gateway1' and 0.6 and 0.4 for 'Gateway2'.
"""
```

Output:

```shell
python simulation_copilot/resource_model_agent.py


> Entering new AgentExecutor chain...

Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': '08:00', 'end_time': '21:00'}, {'start_day': 'Saturday', 'end_day': 'Saturday', 'start_time': '09:00', 'end_time': '17:00'}, {'start_day': 'Sunday', 'end_day': 'Sunday', 'start_time': '10:00', 'end_time': '16:00'}]}`


id='5bc04daf74e04ab7baaacdaab28f0825' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]
Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': '09:00', 'end_time': '17:00'}, {'start_day': 'Saturday', 'end_day': 'Sunday', 'start_time': '10:00', 'end_time': '16:00'}]}`


id='7dfc52f1ccc841a7814be943a8557266' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]
Invoking: `generate_resource_profile` with `{'resources': [{'resource_name': 'Busy', 'amount': 5, 'cost_per_hour': 10.0, 'calendar_id': '5bc04daf74e04ab7baaacdaab28f0825', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}]}, {'resource_name': 'Senior', 'amount': 3, 'cost_per_hour': 20.0, 'calendar_id': '5bc04daf74e04ab7baaacdaab28f0825', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}]}]}`


id='d318a9e4b1904d5a9a2880d9e59747e5' resources=[Resource(id='d2923b6b20e64055a39ac4e9cd45a512', name='Busy', amount=5, cost_per_hour=10.0, calendar_id='5bc04daf74e04ab7baaacdaab28f0825', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))]), Resource(id='6dcb2e32e5a2445c80eaaaf5243f7b36', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='5bc04daf74e04ab7baaacdaab28f0825', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))])]
Invoking: `generate_resource_profile` with `{'resources': [{'resource_name': 'Normal', 'amount': 1, 'cost_per_hour': 10.0, 'calendar_id': '7dfc52f1ccc841a7814be943a8557266', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}]}, {'resource_name': 'Senior', 'amount': 1, 'cost_per_hour': 20.0, 'calendar_id': '7dfc52f1ccc841a7814be943a8557266', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}]}]}`


id='569fa1445f784a0c9f938479eb5fb42a' resources=[Resource(id='35ffd459fb194734b3a973690c9d6363', name='Normal', amount=1, cost_per_hour=10.0, calendar_id='7dfc52f1ccc841a7814be943a8557266', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))]), Resource(id='1b0c922ff46042ff8ada7f88d9b86223', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='7dfc52f1ccc841a7814be943a8557266', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))])]
Invoking: `generate_gateway_probabilities` with `{'gateway_settings': [{'gateway_id': 'Gateway1', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.3}, {'path_id': 'SequenceFlow2', 'probability': 0.7}]}, {'gateway_id': 'Gateway2', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.6}, {'path_id': 'SequenceFlow2', 'probability': 0.4}]}]}`


[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])]
Invoking: `generate_bps_model` with `{'gateway_probabilities': [{'gateway_id': 'Gateway1', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.3}, {'path_id': 'SequenceFlow2', 'probability': 0.7}]}, {'gateway_id': 'Gateway2', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.6}, {'path_id': 'SequenceFlow2', 'probability': 0.4}]}], 'resource_model': {'calendars': [{'id': '5bc04daf74e04ab7baaacdaab28f0825', 'intervals': [{'end_day': 'Friday', 'end_time': {'hour': 21, 'minute': 0}, 'start_day': 'Monday', 'start_time': {'hour': 8, 'minute': 0}}, {'end_day': 'Saturday', 'end_time': {'hour': 17, 'minute': 0}, 'start_day': 'Saturday', 'start_time': {'hour': 9, 'minute': 0}}, {'end_day': 'Sunday', 'end_time': {'hour': 16, 'minute': 0}, 'start_day': 'Sunday', 'start_time': {'hour': 10, 'minute': 0}}]}, {'id': '7dfc52f1ccc841a7814be943a8557266', 'intervals': [{'end_day': 'Friday', 'end_time': {'hour': 17, 'minute': 0}, 'start_day': 'Monday', 'start_time': {'hour': 9, 'minute': 0}}, {'end_day': 'Sunday', 'end_time': {'hour': 16, 'minute': 0}, 'start_day': 'Saturday', 'start_time': {'hour': 10, 'minute': 0}}]}], 'profiles': [{'id': 'd318a9e4b1904d5a9a2880d9e59747e5', 'resources': [{'amount': 5, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}], 'calendar_id': '5bc04daf74e04ab7baaacdaab28f0825', 'cost_per_hour': 10.0, 'id': 'd2923b6b20e64055a39ac4e9cd45a512', 'name': 'Busy'}, {'amount': 3, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}], 'calendar_id': '5bc04daf74e04ab7baaacdaab28f0825', 'cost_per_hour': 20.0, 'id': '6dcb2e32e5a2445c80eaaaf5243f7b36', 'name': 'Senior'}]}, {'id': '569fa1445f784a0c9f938479eb5fb42a', 'resources': [{'amount': 1, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}], 'calendar_id': '7dfc52f1ccc841a7814be943a8557266', 'cost_per_hour': 10.0, 'id': '35ffd459fb194734b3a973690c9d6363', 'name': 'Normal'}, {'amount': 1, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [2, 3]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [3, 4]}}], 'calendar_id': '7dfc52f1ccc841a7814be943a8557266', 'cost_per_hour': 20.0, 'id': '1b0c922ff46042ff8ada7f88d9b86223', 'name': 'Senior'}]}]}}`


resource_model=ResourceModel(profiles=[ResourceProfile(id='d318a9e4b1904d5a9a2880d9e59747e5', resources=[Resource(id='d2923b6b20e64055a39ac4e9cd45a512', name='Busy', amount=5, cost_per_hour=10.0, calendar_id='5bc04daf74e04ab7baaacdaab28f0825', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))]), Resource(id='6dcb2e32e5a2445c80eaaaf5243f7b36', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='5bc04daf74e04ab7baaacdaab28f0825', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))])]), ResourceProfile(id='569fa1445f784a0c9f938479eb5fb42a', resources=[Resource(id='35ffd459fb194734b3a973690c9d6363', name='Normal', amount=1, cost_per_hour=10.0, calendar_id='7dfc52f1ccc841a7814be943a8557266', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))]), Resource(id='1b0c922ff46042ff8ada7f88d9b86223', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='7dfc52f1ccc841a7814be943a8557266', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))])])], calendars=[Calendar(id='5bc04daf74e04ab7baaacdaab28f0825', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='7dfc52f1ccc841a7814be943a8557266', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]) gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])]


> Finished chain.
{'input': "\nGenerate a simulation model with a resource model with 2 resource profiles, which has 2 calendars, and gateway probabilties.\nCalendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.\nCalendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.\nResource model has 2 resource profiles, 'Busy' and 'Normal'.\nProfile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.\nProfile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.\nAlso, add gateway probabilities for the gateways 'Gateway1' and 'Gateway2' with the outgoing sequence flows 'SequenceFlow1' and 'SequenceFlow2' with the probabilities 0.3 and 0.7 for 'Gateway1' and 0.6 and 0.4 for 'Gateway2'.\n", 'output': SimulationModel(resource_model=ResourceModel(profiles=[ResourceProfile(id='d318a9e4b1904d5a9a2880d9e59747e5', resources=[Resource(id='d2923b6b20e64055a39ac4e9cd45a512', name='Busy', amount=5, cost_per_hour=10.0, calendar_id='5bc04daf74e04ab7baaacdaab28f0825', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))]), Resource(id='6dcb2e32e5a2445c80eaaaf5243f7b36', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='5bc04daf74e04ab7baaacdaab28f0825', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))])]), ResourceProfile(id='569fa1445f784a0c9f938479eb5fb42a', resources=[Resource(id='35ffd459fb194734b3a973690c9d6363', name='Normal', amount=1, cost_per_hour=10.0, calendar_id='7dfc52f1ccc841a7814be943a8557266', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))]), Resource(id='1b0c922ff46042ff8ada7f88d9b86223', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='7dfc52f1ccc841a7814be943a8557266', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[2.0, 3.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[3.0, 4.0]))])])], calendars=[Calendar(id='5bc04daf74e04ab7baaacdaab28f0825', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='7dfc52f1ccc841a7814be943a8557266', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]), gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])])}
```

**NOTE:** The output above confuses resource names with profile names. It creates `Resource(name="Busy")` and `Resource(name="Senior")`. Also, internally, ResourceProfile doesn't have the `name` field but the profile name is given in the description. The LLM is expected to omit arguments it cannot use.

Introducing the `name` field to `ResourceProfile` removed the confusion in the next run.

<details>
<summary>Better result</summary>

```shell
> Entering new AgentExecutor chain...

Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': '08:00', 'end_time': '21:00'}, {'start_day': 'Saturday', 'end_day': 'Saturday', 'start_time': '09:00', 'end_time': '17:00'}, {'start_day': 'Sunday', 'end_day': 'Sunday', 'start_time': '10:00', 'end_time': '16:00'}]}`


id='c81ead98cd894ae39b90efe129d496c9' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]
Invoking: `generate_calendar` with `{'intervals': [{'start_day': 'Monday', 'end_day': 'Friday', 'start_time': '09:00', 'end_time': '17:00'}, {'start_day': 'Saturday', 'end_day': 'Sunday', 'start_time': '10:00', 'end_time': '16:00'}]}`


id='3b474c4e76184526b3b91f67540045d4' intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]
Invoking: `generate_resource_profile` with `{'name': 'Busy', 'resources': [{'resource_name': 'Junior', 'amount': 5, 'cost_per_hour': 10, 'calendar_id': 'c81ead98cd894ae39b90efe129d496c9', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}]}, {'resource_name': 'Senior', 'amount': 3, 'cost_per_hour': 20, 'calendar_id': 'c81ead98cd894ae39b90efe129d496c9', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}]}]}`


id='5bb14ad39ac44a42b95e7e97c40cba75' name='Busy' resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]
Invoking: `generate_resource_profile` with `{'name': 'Normal', 'resources': [{'resource_name': 'Junior', 'amount': 1, 'cost_per_hour': 10, 'calendar_id': '3b474c4e76184526b3b91f67540045d4', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}]}, {'resource_name': 'Senior', 'amount': 1, 'cost_per_hour': 20, 'calendar_id': '3b474c4e76184526b3b91f67540045d4', 'activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}]}]}`


id='d8ac0d1650d54dc4aaedd4cfa3172190' name='Normal' resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]
Invoking: `generate_gateway_probabilities` with `{'gateway_settings': [{'gateway_id': 'Gateway1', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.3}, {'path_id': 'SequenceFlow2', 'probability': 0.7}]}, {'gateway_id': 'Gateway2', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.6}, {'path_id': 'SequenceFlow2', 'probability': 0.4}]}]}`


[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])]
Invoking: `generate_bps_model` with `{'gateway_probabilities': [{'gateway_id': 'Gateway1', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.3}, {'path_id': 'SequenceFlow2', 'probability': 0.7}]}, {'gateway_id': 'Gateway2', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.6}, {'path_id': 'SequenceFlow2', 'probability': 0.4}]}], 'resource_model': {'calendars': [{'id': 'c81ead98cd894ae39b90efe129d496c9', 'intervals': [{'end_day': 'Friday', 'end_time': {'hour': 21, 'minute': 0}, 'start_day': 'Monday', 'start_time': {'hour': 8, 'minute': 0}}, {'end_day': 'Saturday', 'end_time': {'hour': 17, 'minute': 0}, 'start_day': 'Saturday', 'start_time': {'hour': 9, 'minute': 0}}, {'end_day': 'Sunday', 'end_time': {'hour': 16, 'minute': 0}, 'start_day': 'Sunday', 'start_time': {'hour': 10, 'minute': 0}}]}, {'id': '3b474c4e76184526b3b91f67540045d4', 'intervals': [{'end_day': 'Friday', 'end_time': {'hour': 17, 'minute': 0}, 'start_day': 'Monday', 'start_time': {'hour': 9, 'minute': 0}}, {'end_day': 'Sunday', 'end_time': {'hour': 16, 'minute': 0}, 'start_day': 'Saturday', 'start_time': {'hour': 10, 'minute': 0}}]}], 'profiles': [{'id': '5bb14ad39ac44a42b95e7e97c40cba75', 'name': 'Busy', 'resources': [{'amount': 5, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}], 'calendar_id': 'c81ead98cd894ae39b90efe129d496c9', 'cost_per_hour': 10, 'id': '79e2bfd841a841e6a9122f01c2f1192e', 'name': 'Junior'}, {'amount': 3, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}], 'calendar_id': 'c81ead98cd894ae39b90efe129d496c9', 'cost_per_hour': 20, 'id': '5f2bb5de72cb42d5ad06e188f0f8a9df', 'name': 'Senior'}]}, {'id': 'd8ac0d1650d54dc4aaedd4cfa3172190', 'name': 'Normal', 'resources': [{'amount': 1, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}], 'calendar_id': '3b474c4e76184526b3b91f67540045d4', 'cost_per_hour': 10, 'id': 'da6f7a698f4943348a6eb998a98854a6', 'name': 'Junior'}, {'amount': 1, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1, 2]}}], 'calendar_id': '3b474c4e76184526b3b91f67540045d4', 'cost_per_hour': 20, 'id': '6cc6686fdc4546e48ca41f0cec183d6f', 'name': 'Senior'}]}]}}`


resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]) gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])]


> Finished chain.
{'input': "\nGenerate a simulation model with a resource model with 2 resource profiles, which has 2 calendars, and gateway probabilties.\nCalendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.\nCalendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.\nResource model has 2 resource profiles, 'Busy' and 'Normal'.\nProfile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.\nProfile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.\nAlso, add gateway probabilities for the gateways 'Gateway1' and 'Gateway2' with the outgoing sequence flows 'SequenceFlow1' and 'SequenceFlow2' with the probabilities 0.3 and 0.7 for 'Gateway1' and 0.6 and 0.4 for 'Gateway2'.\n", 'output': SimulationModel(resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]), gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])])}
```

</details>

</details>

<details>
<summary>Modifying a parameter in the simulation model</summary>

Prompt to the agent (model: gpt-4-0125-preview):

```python
Given the following simulation model set the number of 'Junior' resources in the 'Busy' profile to 10:

SimulationModel(resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]), gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])])
```

Output:

```shell
python simulation_copilot/simulation_model_agent.py


> Entering new AgentExecutor chain...

Invoking: `generate_bps_model` with `{'gateway_probabilities': [{'gateway_id': 'Gateway1', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.3}, {'path_id': 'SequenceFlow2', 'probability': 0.7}]}, {'gateway_id': 'Gateway2', 'outgoing_paths': [{'path_id': 'SequenceFlow1', 'probability': 0.6}, {'path_id': 'SequenceFlow2', 'probability': 0.4}]}], 'resource_model': {'calendars': [{'id': 'c81ead98cd894ae39b90efe129d496c9', 'intervals': [{'end_day': 'Friday', 'end_time': {'hour': 21, 'minute': 0}, 'start_day': 'Monday', 'start_time': {'hour': 8, 'minute': 0}}, {'end_day': 'Saturday', 'end_time': {'hour': 17, 'minute': 0}, 'start_day': 'Saturday', 'start_time': {'hour': 9, 'minute': 0}}, {'end_day': 'Sunday', 'end_time': {'hour': 16, 'minute': 0}, 'start_day': 'Sunday', 'start_time': {'hour': 10, 'minute': 0}}]}, {'id': '3b474c4e76184526b3b91f67540045d4', 'intervals': [{'end_day': 'Friday', 'end_time': {'hour': 17, 'minute': 0}, 'start_day': 'Monday', 'start_time': {'hour': 9, 'minute': 0}}, {'end_day': 'Sunday', 'end_time': {'hour': 16, 'minute': 0}, 'start_day': 'Saturday', 'start_time': {'hour': 10, 'minute': 0}}]}], 'profiles': [{'id': '5bb14ad39ac44a42b95e7e97c40cba75', 'name': 'Busy', 'resources': [{'amount': 10, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}], 'calendar_id': 'c81ead98cd894ae39b90efe129d496c9', 'cost_per_hour': 10.0, 'id': '79e2bfd841a841e6a9122f01c2f1192e', 'name': 'Junior'}, {'amount': 3, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}], 'calendar_id': 'c81ead98cd894ae39b90efe129d496c9', 'cost_per_hour': 20.0, 'id': '5f2bb5de72cb42d5ad06e188f0f8a9df', 'name': 'Senior'}]}, {'id': 'd8ac0d1650d54dc4aaedd4cfa3172190', 'name': 'Normal', 'resources': [{'amount': 1, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}], 'calendar_id': '3b474c4e76184526b3b91f67540045d4', 'cost_per_hour': 10.0, 'id': 'da6f7a698f4943348a6eb998a98854a6', 'name': 'Junior'}, {'amount': 1, 'assigned_activities': [{'activity_id': 'A', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'B', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}, {'activity_id': 'C', 'distribution': {'name': 'uniform', 'parameters': [1.0, 2.0]}}], 'calendar_id': '3b474c4e76184526b3b91f67540045d4', 'cost_per_hour': 20.0, 'id': '6cc6686fdc4546e48ca41f0cec183d6f', 'name': 'Senior'}]}]}}`


resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=10, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]) gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])]


> Finished chain.
{'input': "\nGiven the following simulation model set the number of 'Junior' resources in the 'Busy' profile to 10: \n\nSimulationModel(resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]), gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])])\n", 'output': SimulationModel(resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=10, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]), gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])])}
```
