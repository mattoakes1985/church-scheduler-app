# Church Scheduler App

A Flask-based web application for scheduling services, managing volunteers, teams, and roles for a church. Inspired by commercial tools like Planning Center, but built entirely on open-source tools.

## Features
- Volunteer management
- Team and role assignments (many-to-many relationships)
- Admin panel using Flask-Admin with custom views and logic
- Dashboard with network graph (Plotly + NetworkX)
- SQLite + SQLAlchemy
- Dark mode theme (in progress)

## Key Models
- `Volunteer`
- `Team`
- `Role`
- `TeamRole` (links Team <-> Role)
- `VolunteerTeamRole` (links Volunteer <-> TeamRole, includes `is_lead` flag)

## Visualisation
An interactive dashboard using Plotly shows relationships between people, teams, and roles.

## Stack
- Python 3.13
- Flask
- Flask-Admin
- SQLAlchemy
- Plotly
- NetworkX
- SQLite (stored at `instance/church.db`)

## Dev Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py
