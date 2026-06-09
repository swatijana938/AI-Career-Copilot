from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
DATABASE_URL = "mysql+pymysql://36pfuHtaDQeeB22.root:90w8tFlmBRvf7bsh@gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com:4000/test?ssl_ca=<CA_PATH>&ssl_verify_cert=true&ssl_verify_identity=true"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {}
          }
        
)

sessionLocal = sessionmaker(bind=engine)
Base = declarative_base()