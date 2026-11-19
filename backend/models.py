from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Spreadsheet(Base):
    __tablename__ = "spreadsheets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Cell(Base):
    __tablename__ = "cells"
    id = Column(Integer, primary_key=True, index=True)
    spreadsheet_id = Column(Integer, ForeignKey("spreadsheets.id"))
    row = Column(Integer, index=True)
    col = Column(Integer, index=True)
    value = Column(Text, default="")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class CellHistory(Base):
    __tablename__ = "cell_history"
    id = Column(Integer, primary_key=True, index=True)
    cell_id = Column(Integer, ForeignKey("cells.id"))
    old_value = Column(Text)
    new_value = Column(Text)
    edited_by = Column(String)
    edited_at = Column(DateTime(timezone=True), server_default=func.now())