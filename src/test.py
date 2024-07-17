from sqlalchemy import create_engine

def get_db_engine():
    return create_engine('postgresql://swabber:swabber@postgres:5432/swabberdb')

db_engine = get_db_engine().connect()
db_engine.execute("SELECT * FROM agents")
db_engine.close()