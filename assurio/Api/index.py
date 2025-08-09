from app.main import app  # Import FastAPI app from your actual code

def handler(environ, start_response):
    from mangum import Mangum
    asgi_handler = Mangum(app)
    return asgi_handler(environ, start_response)
