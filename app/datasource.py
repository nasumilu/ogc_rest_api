from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:<password_here>!@localhost/geodatabase"

# just raw queries for now
engine = create_engine(SQLALCHEMY_DATABASE_URL)
