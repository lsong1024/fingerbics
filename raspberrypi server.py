from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import subprocess

app = FastAPI()

origins = [
    "http://192.168.50.10:8001/",
    "http://192.168.50.87:8001/",
#본인 ip 추가해야해요
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/execute-script")
async def execute_script():
    try:

        python_script_path = '/home/pi/camera_caputre_led3.py'

        result = subprocess.run(['python3', python_script_path], check=True, capture_output=True, text=True)

        return JSONResponse(content={"message": "python OK", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        error_message = f"python error: {e}\n{e.stderr.decode()}"
        return JSONResponse(content={"error": error_message}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)