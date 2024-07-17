CREATE SCHEMA swabber;

CREATE TABLE swabber.agents (
    agent_id SERIAL PRIMARY KEY,
    age INT NOT NULL,
    gender VARCHAR(255) NOT NULL,
    sexual_orientation VARCHAR(255) NOT NULL,
    last_STI_test_date DATE NOT NULL,
    STI_status VARCHAR(255) NOT NULL,
    partnering_type VARCHAR(255) NOT NULL,
    partner_count VARCHAR(255) NOT NULL,
    loc VARCHAR(255) NOT NULL,
    pair_on_system BOOLEAN NOT NULL
);

\copy swabber.agents FROM '/csv/user_list.csv' DELIMITER ',' CSV HEADER;