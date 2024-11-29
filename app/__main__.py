import uvicorn

from app import ENV, HOST, PORT

uvicorn.run("app.main:api", host=HOST, port=PORT, reload=ENV == "development")
