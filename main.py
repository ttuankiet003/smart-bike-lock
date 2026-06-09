from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# =========================
# Dashboard
# =========================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):

    users = load_users()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "status": "ONLINE",
            "lock": "LOCKED",
            "users": users
        }
    )

# =========================
# User Database
# =========================
os.makedirs("data", exist_ok=True)

USERS_FILE = "data/users.json"

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)



@app.post("/add_user")
async def add_user(
    id: int = Form(...),
    name: str = Form(...)
):

    users = load_users()

    for u in users:
        if u["id"] == id:
            return RedirectResponse(
                url="/",
                status_code=303
            )

    users.append({
        "id": id,
        "name": name
    })

    save_users(users)

    return RedirectResponse(
        url="/",
        status_code=303
    )
# =========================
# Delete User
# =========================
@app.post("/delete_user")
async def delete_user(
    id: int = Form(...)
):

    users = load_users()

    users = [
        u for u in users
        if u["id"] != id
    ]

    save_users(users)

    return RedirectResponse(
        url="/",
        status_code=303
    )