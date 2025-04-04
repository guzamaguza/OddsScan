import os

class Config:
    # Add your PostgreSQL URI here, either the internal or external connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://odds_db_p_user:OpPKdTCSCL6klAW12bpahexoQdiabrRH@dpg-cvn96b3uibrs73bb4910-a.oregon-postgres.render.com/odds_db_p'
    
    # Additional configuration options for SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disables Flask-SQLAlchemy modification tracking (optional but recommended)



