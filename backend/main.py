from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from sqlmodel import Field, SQLModel, Session, create_engine, select

# Database setup - Using PostgreSQL for scalability
DATABASE_URL = "postgresql://user:password@host:port/dbname" # TODO: Replace with actual PostgreSQL connection string
engine = create_engine(DATABASE_URL)


class StockBase(SQLModel):
    symbol: str = Field(index=True, unique=True, max_length=10)
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Stock(StockBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class StockCreate(StockBase):
    pass


class StockPublic(StockBase):
    id: int


app = FastAPI()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/api/stocks/", response_model=StockPublic)
def create_stock(*, stock: StockCreate):
    with Session(engine) as session:
        db_stock = Stock.model_validate(stock)
        session.add(db_stock)
        session.commit()
        session.refresh(db_stock)
        return db_stock


@app.get("/api/stocks/", response_model=List[StockPublic])
def read_stocks():
    with Session(engine) as session:
        stocks = session.exec(select(Stock)).all()
        return stocks


@app.get("/api/stocks/{stock_symbol}", response_model=StockPublic)
def read_stock_by_symbol(*, stock_symbol: str):
    with Session(engine) as session:
        stock = session.exec(select(Stock).where(Stock.symbol == stock_symbol)).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        return stock


@app.put("/api/stocks/{stock_symbol}", response_model=StockPublic)
def update_stock(
    *, stock_symbol: str, stock: StockCreate
):
    with Session(engine) as session:
        db_stock = session.exec(select(Stock).where(Stock.symbol == stock_symbol)).first()
        if not db_stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        stock_data = stock.model_dump(exclude_unset=True)
        db_stock.sqlmodel_update(stock_data)
        session.add(db_stock)
        session.commit()
        session.refresh(db_stock)
        return db_stock


@app.delete("/api/stocks/{stock_symbol}")
def delete_stock(*, stock_symbol: str):
    with Session(engine) as session:
        stock = session.exec(select(Stock).where(Stock.symbol == stock_symbol)).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        session.delete(stock)
        session.commit()
        return {"message": "Stock deleted successfully"}
