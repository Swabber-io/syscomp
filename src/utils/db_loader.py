from sqlalchemy import create_engine
import csv
import os
import random
from datetime import datetime
from utils.impl_config import State, AgeGroup, Gender, SexualOrientation, PairingType, PairOnSystem, PartnerCount

def fetch_db_data():
        """Fetch data from the database."""
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_user = os.getenv('DB_USER')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME')
        return create_engine(f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}').connect()



def fetch_csv_data(file_path: str, num_agents: int) -> dict:
    """Fetch data from a CSV file and return a shuffled subset as a dictionary."""
    agents = []
    with open(file_path, 'r', newline='', encoding='utf-8') as agents_file:
        reader = csv.DictReader(agents_file)
        for row in reader:
            agent_data = {
                'agent_id': row['agent_id'],
                'age_group': AgeGroup.YOUNG if int(row['age']) < 18 else (AgeGroup.ADULT if int(row['age']) < 50 else AgeGroup.SENIOR),
                'gender': Gender(row['gender']),
                'sexual_orientation': SexualOrientation(row['sexual_orientation']),
                'last_sti_test_date': datetime.strptime(row['last_STI_test_date'], '%m/%d/%Y'),
                'sti_status': State(row['STI_status']),
                'partnering_type': PairingType(row['partnering_type']),
                'partner_count': PartnerCount(row['partner_count']),
                'loc': row['loc'],
                'pair_on_system': PairOnSystem(row['pair_on_system'])
            }
            agents.append(agent_data)
    
    random.shuffle(agents)
    return agents[:num_agents]


                
