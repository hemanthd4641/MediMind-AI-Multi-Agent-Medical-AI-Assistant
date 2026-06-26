from fastapi.middleware.cors import CORSMiddleware

class cors_middleware(CORSMiddleware):
    def __init__(self, app):
        super().__init__(
            app,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
