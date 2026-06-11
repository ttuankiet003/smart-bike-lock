from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
from pydantic import BaseModel
from fastapi import Body


app = FastAPI()

templates = Jinja2Templates(directory="templates")

# =========================
# Database
# =========================

DATA_DIR = "/data"

os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(
    DATA_DIR,
    "users.json"
)

# Tạo file nếu chưa tồn tại
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            users,
            f,
            ensure_ascii=False,
            indent=4
        )


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
# API USERS
# =========================

@app.get("/api/users")
async def api_users():

    users = load_users()

    return JSONResponse(content=users)


# =========================
# Add User
# =========================

@app.post("/add_user")
async def add_user(
    id: int = Form(...),
    name: str = Form(...)
):

    users = load_users()

    # Không cho trùng ID
    for u in users:
        if u["id"] == id:
            return RedirectResponse(
                url="/",
                status_code=303
            )

    users.append({
        "id": id,
        "name": name,
        "status": "waiting"
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

@app.get("/api/pending_users")
async def pending_users():

    users = load_users()

    waiting_users = [
        u for u in users
        if u.get("status") == "waiting"
    ]

    return JSONResponse(content=waiting_users)

class EnrollRequest(BaseModel):
    id: int
@app.post("/enroll_success")
async def enroll_success(request: Request):

    data = await request.json()

    uid = int(data["id"])

    users = load_users()

    found = False

    for u in users:
        if u["id"] == uid:
            u["status"] = "enrolled"
            found = True
            break

    if not found:
        return {
            "success": False,
            "message": f"ID {uid} không tồn tại"
        }

    save_users(users)

    return {
        "success": True,
        "id": uid
    }
# =========================
# Unlock Log
# =========================

UNLOCK_LOG = []

@app.post("/unlock")
async def unlock(request: Request):

    data = await request.json()

    uid = int(data["id"])

    users = load_users()

    name = "Unknown"

    for u in users:
        if u["id"] == uid:
            name = u["name"]
            break

    UNLOCK_LOG.insert(
        0,
        {
            "id": uid,
            "name": name
        }
    )

    return {
        "success": True
    }
@app.get("/api/unlock_logs")
async def get_unlock_logs():

    return UNLOCK_LOG