from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
from pydantic import BaseModel
from fastapi import Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
import secrets
from datetime import datetime
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import time

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="SMART_BIKE_LOCK_2026"
)
security = HTTPBasic()
gps_data = {
    "latitude": 0,
    "longitude": 0
}

templates = Jinja2Templates(directory="templates")

# =========================
# Database
# =========================
LOCK_STATUS = "LOCKED"
EMERGENCY_UNLOCK = False
DATA_DIR = "/data"

os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(
    DATA_DIR,
    "users.json"
)
DELETE_FILE = os.path.join(
    DATA_DIR,
    "delete_queue.json"
)
SETTINGS_FILE = os.path.join(
    DATA_DIR,
    "settings.json"
)
EMERGENCY_FILE = os.path.join(
    DATA_DIR,
    "emergency.json"
)
STATUS_FILE = os.path.join(
    DATA_DIR,
    "esp_status.json"
)
WIFI_FILE = os.path.join(
    DATA_DIR,
    "wifi_status.json"
)
if not os.path.exists(STATUS_FILE):
    
    with open(
        STATUS_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "last_seen": 0
            },
            f
        )
if not os.path.exists(WIFI_FILE):

    with open(
        WIFI_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "wifi": "Disconnected",
                "backup": False,
                "reconnect": False
            },
            f
        )
if not os.path.exists(EMERGENCY_FILE):

    with open(
        EMERGENCY_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "unlock": False
            },
            f
        )
# Tạo file nếu chưa tồn tại
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
if not os.path.exists(DELETE_FILE):
    with open(DELETE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
if not os.path.exists(SETTINGS_FILE):
    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "username": "admin",
                "password": "123456"
            },
            f,
            indent=4
        )
def load_status():

    with open(
        STATUS_FILE,
        "r"
    ) as f:

        return json.load(f)


def save_status(data):

    with open(
        STATUS_FILE,
        "w"
    ) as f:

        json.dump(data, f)
        
def load_wifi():

    with open(
        WIFI_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_wifi(data):

    with open(
        WIFI_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )
def load_emergency():
    try:
        with open(
            EMERGENCY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)
    except:
        return {
            "unlock": False
        }


def save_emergency(data):
    with open(
        EMERGENCY_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            indent=4
        )
def load_settings():

    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


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
def load_delete_queue():
    try:
        with open(DELETE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_delete_queue(data):
    with open(DELETE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )
def load_settings():

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {
            "username": "admin",
            "password": "123456"
        }


def save_settings(data):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )
# mật khẩu
def verify_admin(
    credentials: HTTPBasicCredentials = Depends(security)
):

    settings = load_settings()

    correct_username = secrets.compare_digest(
        credentials.username,
        settings["username"]
    )

    correct_password = secrets.compare_digest(
        credentials.password,
        settings["password"]
    )

    if not (
        correct_username
        and
        correct_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Sai tài khoản",
            headers={
                "WWW-Authenticate": "Basic"
            }
        )

    return True

# =========================
# Dashboard
# =========================

@app.get("/")
async def dashboard(
    request: Request
):

    if "user" not in request.session:

        return RedirectResponse(
            "/login",
            status_code=303
        )

    users = load_users()
    status_data = load_status()
    emergency = load_emergency()
    esp_online = False

    if (
    time.time()
    -
    status_data["last_seen"]
    )   < 60:

        esp_online = True   

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "status": "ONLINE",
            "lock": "LOCKED",
            "users": users,
            "logs": UNLOCK_LOG,
            "esp_online": esp_online,
            "emergency_unlock": emergency["unlock"]
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


@app.post("/emergency_done")
async def emergency_done():

    save_emergency(
        {
            "unlock": False
        }
    )

    return {
        "success": True
    }
@app.post("/add_user")
async def add_user(
    request: Request,
    id: int = Form(...),
    name: str = Form(...)
):

    users = load_users()

    for u in users:

        if u["id"] == id:

            return templates.TemplateResponse(
                request=request,
                name="dashboard.html",
                context={
                    "status": "ONLINE",
                    "lock": LOCK_STATUS,
                    "users": users,
                    "logs": UNLOCK_LOG,
                    "error": f"ID {id} đã tồn tại"
                  
                }
            )

    users.append(
        {
            "id": id,
            "name": name,
            "status": "waiting"
        }
    )

    save_users(users)

    return RedirectResponse(
        "/",
        status_code=303
    )

# =========================
# Delete User
# =========================

@app.post("/delete_user")
async def delete_user(
    id: int = Form(...)
):

    queue = load_delete_queue()

    queue.append({
        "id": id
    })

    save_delete_queue(queue)

    return RedirectResponse(
        url="/",
        status_code=303
    )
@app.get("/api/delete_pending")
async def delete_pending():

    return load_delete_queue()

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
class GPSRequest(BaseModel):
    latitude: float
    longitude: float
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
            "name": name,
            "time": datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        }
    )

    return {
        "success": True
    }
@app.get("/api/unlock_logs")
async def get_unlock_logs():

    return UNLOCK_LOG

@app.post("/delete_success")
async def delete_success(request: Request):

    data = await request.json()

    uid = int(data["id"])

    users = load_users()

    users = [
        u for u in users
        if u["id"] != uid
    ]

    save_users(users)

    queue = load_delete_queue()

    queue = [
        q for q in queue
        if q["id"] != uid
    ]

    save_delete_queue(queue)


    return {
        "success": True
    }
@app.post("/change_password")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...)
):

    settings = load_settings()

    if old_password != settings["password"]:

        return RedirectResponse(
            url="/?error=password",
            status_code=303
        )

    settings["password"] = new_password

    save_settings(settings)

    return RedirectResponse(
        url="/",
        status_code=303
    )
@app.get("/login")
async def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )
@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    settings = load_settings()

    if (
        username == settings["username"]
        and
        password == settings["password"]
    ):

        request.session["user"] = username

        return RedirectResponse(
            "/",
            status_code=303
        )

    return RedirectResponse(
        "/login",
        status_code=303
    )
@app.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        "/login",
        status_code=303
    )
@app.post("/heartbeat")
async def heartbeat():

    save_status(
        {
            "last_seen": time.time()
        }
    )

    return {
        "success": True
    }
@app.post("/lock_status")
async def lock_status(
    request: Request
):
    global LOCK_STATUS

    data = await request.json()

    LOCK_STATUS = data["status"]

    return {
        "success": True
    }
@app.get("/api/lock_status")
async def api_lock_status():

    return {
        "status": LOCK_STATUS
    }

@app.post("/emergency_unlock")
async def emergency_unlock():

    data = load_emergency()

    unlock = data["unlock"]

    new_state = not unlock

    print("Emergency =", new_state)

    save_emergency(
        {
            "unlock": new_state
        }
    )

    print(load_emergency())

    return RedirectResponse(
        "/",
        status_code=303
    )
@app.get("/api/emergency_unlock")
async def api_emergency_unlock():

    return load_emergency()

@app.post("/wifi_status")
async def wifi_status(request: Request):

    incoming = await request.json()

    data = load_wifi()

    data["wifi"] = incoming.get(
        "wifi",
        "Disconnected"
    )

    data["backup"] = incoming.get(
        "backup",
        False
    )

    save_wifi(data)

    return {
        "success": True
    }

    return {
        "success": True
    }
@app.get("/api/current_wifi")
async def current_wifi():

    return load_wifi()
@app.post("/reconnect_primary")
async def reconnect_primary():

    data =load_wifi()

    data["reconnect"] = True

    save_wifi(data)

    return RedirectResponse(
        "/",
        status_code=303
    )
@app.get("/api/reconnect_primary")
async def api_reconnect_primary():

    data =load_wifi()

    return {
        "reconnect":
            data.get(
                "reconnect",
                False
            )
    }
@app.post("/reconnect_primary_done")
async def reconnect_primary_done():

    data =load_wifi()

    data["reconnect"] = False

    save_wifi(data)

    return {
        "success": True
    }
@app.post("/gps")
async def update_gps(data: GPSRequest):
    global gps_data

    gps_data["latitude"] = data.latitude
    gps_data["longitude"] = data.longitude

    print(
        "GPS:",
        gps_data["latitude"],
        gps_data["longitude"]
    )

    return {
        "success": True
    }
@app.get("/gps")
async def get_gps():
    return gps_data
