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
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "status": "ONLINE",
            "lock": "LOCKED"
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

# =========================
# Fingerprint Manager
# =========================
@app.get("/fingerprints", response_class=HTMLResponse)
async def fingerprints():

    users = load_users()

    rows = ""

    for u in users:
        rows += f"""
        <tr>
            <td>{u['id']}</td>
            <td>{u['name']}</td>

            <td>
                <form action="/delete_user" method="post">
                    <input type="hidden" name="id" value="{u['id']}">
                    <button style="background:red;color:white;">
                        Xóa
                    </button>
                </form>
            </td>
        </tr>
        """

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Quản lý vân tay</title>

        <style>

            body {{
                font-family: Arial;
                margin: 30px;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
            }}

            th {{
                background: #f2f2f2;
            }}

            .add-box {{
                margin-bottom: 20px;
            }}

            input {{
                padding: 8px;
            }}

            button {{
                padding: 8px 15px;
                cursor: pointer;
            }}

        </style>

    </head>

    <body>

        <h1>🔐 Quản lý vân tay</h1>

        <div class="add-box">

            <form action="/add_user" method="post">

                <input
                    type="number"
                    name="id"
                    placeholder="ID vân tay"
                    required>

                <input
                    type="text"
                    name="name"
                    placeholder="Tên người dùng"
                    required>

                <button type="submit">
                    ➕ Thêm
                </button>

            </form>

        </div>

        <table>

            <tr>
                <th>ID</th>
                <th>Tên</th>
                <th>Hành động</th>
            </tr>

            {rows}

        </table>

        <br>

        <a href="/">
            ⬅ Quay về Dashboard
        </a>

    </body>

    </html>
    """)

# =========================
# Add User
# =========================
@app.post("/add_user")
async def add_user(
    id: int = Form(...),
    name: str = Form(...)
):

    users = load_users()

    # tránh trùng ID
    for u in users:
        if u["id"] == id:
            return RedirectResponse(
                url="/fingerprints",
                status_code=303
            )

    users.append({
        "id": id,
        "name": name
    })

    save_users(users)

    return RedirectResponse(
        url="/fingerprints",
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
        url="/fingerprints",
        status_code=303
    )