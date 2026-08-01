from fastapi import FastAPI

app = FastAPI(title="Camel Up API")


@app.get("/")
def root():
    return {"message": "Camel Up API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}