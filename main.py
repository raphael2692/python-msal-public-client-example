# main.py
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from msal_handler import MicrosoftAuth, AuthResult
import os
from typing import Optional, Union
from decouple import config

app = FastAPI()
templates = Jinja2Templates(directory="templates") 

CLIENT_ID = os.environ.get("MSAL_CLIENT_ID", config("CLIENT_ID"))
TENANT_ID = config('TENANT_ID')
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8000/auth_callback" # Deve essere Azure App Register

msal_auth = MicrosoftAuth(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    redirect_uri=REDIRECT_URI
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    user_full_name: Optional[str] = request.cookies.get("user_full_name")
    user_email: Optional[str] = request.cookies.get("user_email")
    return templates.TemplateResponse("index.html", {"request": request, "user_full_name": user_full_name, "user_email": user_email})

@app.get("/login")
async def login() -> RedirectResponse:
    auth_url = msal_auth.get_auth_url(random_code=os.urandom(16).hex())
    return RedirectResponse(auth_url, status_code=302)

@app.get("/logout")
async def logout() -> RedirectResponse:
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_full_name")
    response.delete_cookie("user_email")
    return response

@app.get("/auth_callback", response_model=None) # Add response_model=None here
async def auth_callback(request: Request, code: Optional[str] = None) -> Union[HTMLResponse, RedirectResponse]:
    if not code:
        return HTMLResponse("Authentication failed: No authorization code provided", status_code=401)
    result: Optional[AuthResult] = msal_auth.process_callback(code=code)
    if result and result.user:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("user_full_name", result.user.name)
        response.set_cookie("user_email", result.user.email)
        return response
    return HTMLResponse("Authentication failed", status_code=401)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)