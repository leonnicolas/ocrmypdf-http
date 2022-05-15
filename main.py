#!/usr/bin/env python

import uvicorn


def main():
    uvicorn.run("app:app", reload=False, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
