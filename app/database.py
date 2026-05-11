from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

Base = declarative_base()
engine = create_engine("sqlite:///articles.db")
Session = sessionmaker(bind=engine)

class Article(Base):
    __tablename__ = "articles"
    id = Column(String, primary_key=True)
    title = Column(String)
    source = Column(String)
    url = Column(String)
    summary = Column(Text)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(engine)
print("✅ Database ready!")