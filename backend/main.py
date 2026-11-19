from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import database, models
from ws_manager import manager
from fastapi.responses import StreamingResponse
import io
import csv

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Collaborative Spreadsheet API is running!"}

@app.websocket("/ws/{spreadsheet_id}")
async def websocket_endpoint(websocket: WebSocket, spreadsheet_id: int, db: AsyncSession = Depends(database.get_db)):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "edit_cell":
                row = data["row"]
                col = data["col"]
                value = data["value"]
                
                result = await db.execute(
                    select(models.Cell).where(
                        models.Cell.spreadsheet_id == spreadsheet_id,
                        models.Cell.row == row,
                        models.Cell.col == col
                    )
                )
                cell = result.scalars().first()
                
                if cell:
                    old_value = cell.value
                    cell.value = value
                else:
                    old_value = ""
                    cell = models.Cell(spreadsheet_id=spreadsheet_id, row=row, col=col, value=value)
                    db.add(cell)
                    
                await db.commit()
                await db.refresh(cell)
                
                history_entry = models.CellHistory(
                    cell_id=cell.id,
                    old_value=old_value,
                    new_value=value,
                    edited_by="User"
                )
                db.add(history_entry)
                await db.commit()

                await manager.broadcast({
                    "type": "cell_updated",
                    "row": row,
                    "col": col,
                    "value": value,
                    "updated_by": "User"
                })
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@app.get("/export/{spreadsheet_id}")
async def export_csv(spreadsheet_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(
        select(models.Cell).where(models.Cell.spreadsheet_id == spreadsheet_id)
    )
    cells = result.scalars().all()

    grid = [["" for _ in range(10)] for _ in range(10)]
    for cell in cells:
        if cell.row < 10 and cell.col < 10:
            grid[cell.row][cell.col] = cell.value

    output = io.StringIO()
    writer = csv.writer(output)
    for row in grid:
        writer.writerow(row)
    
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=spreadsheet_{spreadsheet_id}.csv"}
    )

@app.get("/history/{spreadsheet_id}/{row}/{col}")
async def get_cell_history(spreadsheet_id: int, row: int, col: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(
        select(models.Cell).where(
            models.Cell.spreadsheet_id == spreadsheet_id,
            models.Cell.row == row,
            models.Cell.col == col
        )
    )
    cell = result.scalars().first()
    
    if not cell:
        return {"history": []}

    history_result = await db.execute(
        select(models.CellHistory)
        .where(models.CellHistory.cell_id == cell.id)
        .order_by(models.CellHistory.edited_at.desc())
    )
    history = history_result.scalars().all()
    
    return {"history": history}