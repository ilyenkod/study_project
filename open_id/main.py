from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware


GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)

app = FastAPI()

oauth = OAuth(starlette_config)

app.add_middleware(SessionMiddleware, secret_key=GOOGLE_CLIENT_SECRET)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
)



@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return JSONResponse(user)
    return '<a href="/login">Login with Google</a>'


@app.get('/login')
async def login(request: Request):
    redirect_uri = 'https://127.0.0.1:8000/auth/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri=redirect_uri)


@app.get('/auth/callback')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    print(token)
    user = await oauth.google.parse_id_token(request, token)

    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'main:app',
        host="127.0.0.1",
        port=8000,
        reload=True,
        ssl_keyfile="./localhost.key",
        ssl_certfile="./localhost.crt"
    )


# user_info = await oauth.google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
# user = user_info.json()
# oauth.register(
#     name='google',
#     authorize_url='https://accounts.google.com/o/oauth2/auth',
#     authorize_params=None,
#     access_token_url='https://oauth2.googleapis.com/token',
#     access_token_params=None,
#     refresh_token_url=None,
#     redirect_uri=None,
#     client_kwargs={
#         'scope': 'email profile',
#         'token_endpoint_auth_method': 'client_secret_post'
#     }
# )
