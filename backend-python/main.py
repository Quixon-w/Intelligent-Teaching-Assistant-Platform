import time
import subprocess
import threading

start_time = time.time()

import argparse
from typing import Union, Sequence


def get_args(args: Union[Sequence[str], None] = None):
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group(title="server arguments")
    group.add_argument(
        "--port",
        type=int,
        default=8001,
        help="port to run the server on (default: 8001)",
    )
    group.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="host to run the server on (default: 127.0.0.1)",
    )
    group = parser.add_argument_group(title="mode arguments")
    group.add_argument(
        "--webui",
        action="store_true",
        help="whether to enable WebUI (default: False)",
    )
    group.add_argument(
        "--rwkv.cpp",
        action="store_true",
        help="whether to use rwkv.cpp (default: False)",
    )
    group.add_argument(
        "--webgpu",
        action="store_true",
        help="whether to use webgpu (default: False)",
    )
    args = parser.parse_args(args)

    return args


if __name__ == "__main__":
    args = get_args()


import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import psutil
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.rwkv import *
from utils.torch import *
from utils.ngrok import *
from utils.log import log_middleware
from routes import completion, config, state_cache, upload, qa, create, exercise, download, session_routes, knowledge
import global_var
from config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    yield


app = FastAPI(lifespan=lifespan, dependencies=[Depends(log_middleware)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(completion.router)
app.include_router(config.router)
app.include_router(state_cache.router)
app.include_router(upload.router)
app.include_router(qa.router)
app.include_router(create.router)
app.include_router(exercise.router)
app.include_router(download.router)
app.include_router(session_routes.router)
app.include_router(knowledge.router)


@app.post("/exit", tags=["Root"])
def exit():
    settings = get_settings()
    if settings.DEPLOY_MODE:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    parent_pid = os.getpid()
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()


try:
    if (
        "RWKV_RUNNER_PARAMS" in os.environ
        and "--webui" in os.environ["RWKV_RUNNER_PARAMS"].split(" ")
    ) or args.webui:
        from webui_server import webui_server

        app.mount("/", webui_server)
except NameError:
    pass


@app.get("/", tags=["Root"])
def read_root():
    return {"Hello": "World!"}


def init():
    global_var.init()
    cmd_params = os.environ["RWKV_RUNNER_PARAMS"]
    global_var.set(
        global_var.Args, get_args(cmd_params.split(" ") if cmd_params else None)
    )

    state_cache.init()

    set_torch()

    if os.environ.get("ngrok_token") is not None:
        ngrok_connect()

def start_chromadb_server():
    """启动ChromaDB服务器"""
    settings = get_settings()
    
    print(f"🚀 正在启动ChromaDB服务器...")
    print(f"   主机: {settings.CHROMADB_HOST}")
    print(f"   端口: {settings.CHROMADB_PORT}")
    
    try:
        # 启动ChromaDB服务器
        cmd = [
            "chroma", "run", 
            "--host", settings.CHROMADB_HOST,
            "--port", str(settings.CHROMADB_PORT),
            "--path", "/tmp/chromadb"  # 数据存储路径
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        # 启动ChromaDB服务器
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ ChromaDB服务器启动成功！")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ ChromaDB服务器启动失败:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 启动ChromaDB服务器时出错: {e}")
        return None


# Function to trigger the curl command after the server starts
def load_model():
    settings = get_settings()
    model_config = settings.get_model_config()
    
    curl_command = [
        "curl", "-X", "POST", f"http://{settings.HOST}:{settings.PORT}/switch-model",
        "-H", "Content-Type: application/json",
        "-d", f'''{{
            "model": "{model_config['model']}", 
            "strategy": "{model_config['strategy']}", 
            "tokenizer": "{model_config['tokenizer']}", 
            "customCuda": {str(model_config['customCuda']).lower()}, 
            "deploy": {str(model_config['deploy']).lower()}
        }}'''
    ]
    subprocess.run(curl_command)


if __name__ == "__main__":
    os.environ["RWKV_RUNNER_PARAMS"] = " ".join(sys.argv[1:])
    print("--- %s seconds ---" % (time.time() - start_time))
    
    # 获取配置
    settings = get_settings()
    
    # 启动ChromaDB服务器
    chromadb_process = start_chromadb_server()
    if not chromadb_process:
        print("❌ ChromaDB服务器启动失败，但继续启动主服务器...")
    
    # Run the server in a background thread
    def run_server():
        uvicorn.run("main:app", port=settings.PORT, host=settings.HOST, workers=1)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Wait for the server to be ready (you can adjust the timing if necessary)
    time.sleep(5)  # Wait 5 seconds before loading the model

    # Load the model after the server has started
    load_model()

    # Optionally, you can also join the thread to keep the main process alive
    server_thread.join()
