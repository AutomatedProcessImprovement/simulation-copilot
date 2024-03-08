
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

