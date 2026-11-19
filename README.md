# Real-Time Collaborative Spreadsheet

A full-stack, real-time collaborative spreadsheet application built with Python, FastAPI, WebSockets, PostgreSQL, React, and TypeScript.

## Features
- **Real-Time Syncing**: Multiple users can edit cells simultaneously and see updates instantly.
- **Active User Tracking**: Broadcasts the current number of connected users in real-time.
- **Database Persistence**: All cell data and edit histories are saved to PostgreSQL.
- **Edit History**: Every cell change is tracked in a `cell_history` table.
- **CSV Export**: Download the spreadsheet data as a CSV file.

## Tech Stack
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (Async), WebSockets.
- **Database**: PostgreSQL 15.
- **Frontend**: React, TypeScript, Vite, TailwindCSS.
- **Infrastructure**: Docker & Docker Compose.

## Quick Start
1. `docker-compose up -d` (Start Database)
2. `cd backend && uvicorn main:app --reload --port 8001` (Start Backend)
3. `cd frontend && npm run dev` (Start Frontend)

## Success Criteria Met
- ✅ Multiple simultaneous users.
- ✅ Live updates via WebSockets.
- ✅ Data persistence.