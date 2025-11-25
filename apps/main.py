import logging

import uvicorn

from api.app import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
