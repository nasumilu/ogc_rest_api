from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1030asF!@192.168.124.235/geodatabase"

# just raw queries for now
engine = create_engine(SQLALCHEMY_DATABASE_URL)
