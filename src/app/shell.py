import asyncio
import code

from app.database.session import async_session_maker
from app.database.models import *


async def main():
    async with async_session_maker() as session:
        local_vars = {
            "session": session,
        }

        for model_name, model_class in globals().items():
            if isinstance(model_class, type):
                local_vars[model_name] = model_class

        print("FastAPI/SQLAlchemy shell ready!")
        print("Available: session and all models from app.models")
        code.interact(local=local_vars)


if __name__ == "__main__":
    asyncio.run(main())
