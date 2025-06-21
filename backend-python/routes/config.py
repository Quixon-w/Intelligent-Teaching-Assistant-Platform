import pathlib
from utils.log import quick_log

from fastapi import APIRouter, HTTPException, Request, Response, status as Status
from pydantic import BaseModel
from utils.rwkv import *
from utils.torch import *
import global_var
import torch

router = APIRouter()


class SwitchModelBody(BaseModel):
    model: str
    strategy: str
    tokenizer: Union[str, None] = None
    customCuda: bool = False
    deploy: bool = Field(
        False,
        description="Deploy mode. If success, will disable /switch-model, /exit and other dangerous APIs (state cache APIs, part of midi APIs)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "model": "models/RWKV-4-World-3B-v1-20230619-ctx4096.pth",
                "strategy": "cuda fp16",
                "tokenizer": "",
                "customCuda": False,
                "deploy": False,
            }
        }
    }


@router.post("/switch-model", tags=["Configs"])
def switch_model(body: SwitchModelBody, response: Response, request: Request):
    if global_var.get(global_var.Deploy_Mode) is True:
        raise HTTPException(Status.HTTP_403_FORBIDDEN)

    if global_var.get(global_var.Model_Status) is global_var.ModelStatus.Loading:
        response.status_code = Status.HTTP_304_NOT_MODIFIED
        return

    global_var.set(global_var.Model_Status, global_var.ModelStatus.Offline)
    global_var.set(global_var.Model, None)
    torch_gc()

    if body.model == "":
        return "success"

    devices = set(
        [
            x.strip().split(" ")[0].replace("cuda:0", "cuda")
            for x in body.strategy.split("->")
        ]
    )
    print(f"Strategy Devices: {devices}")
    # if len(devices) > 1:
    #     state_cache.disable_state_cache()
    # else:
    try:
        state_cache.enable_state_cache()
    except HTTPException:
        pass

    os.environ["RWKV_CUDA_ON"] = "1" if body.customCuda else "0"

    global_var.set(global_var.Model_Status, global_var.ModelStatus.Loading)
    try:
        global_var.set(
            global_var.Model,
            RWKV(model=body.model, strategy=body.strategy, tokenizer=body.tokenizer),
        )
    except Exception as e:
        print(e)
        import traceback

        print(traceback.format_exc())

        quick_log(request, body, f"Exception: {e}")
        global_var.set(global_var.Model_Status, global_var.ModelStatus.Offline)
        raise HTTPException(
            Status.HTTP_500_INTERNAL_SERVER_ERROR, f"failed to load: {e}"
        )

    if body.deploy:
        global_var.set(global_var.Deploy_Mode, True)

    saved_model_config = global_var.get(global_var.Model_Config)
    init_model_config = get_rwkv_config(global_var.get(global_var.Model))
    if saved_model_config is not None:
        merge_model(init_model_config, saved_model_config)
    global_var.set(global_var.Model_Config, init_model_config)
    global_var.set(global_var.Model_Status, global_var.ModelStatus.Working)

    return "success"


def merge_model(to_model: BaseModel, from_model: BaseModel):
    from_model_fields = [x for x in from_model.dict().keys()]
    to_model_fields = [x for x in to_model.dict().keys()]

    for field_name in from_model_fields:
        if field_name in to_model_fields:
            from_value = getattr(from_model, field_name)

            if from_value is not None:
                setattr(to_model, field_name, from_value)


@router.post("/update-config", tags=["Configs"])
def update_config(body: ModelConfigBody):
    """
    Will not update the model config immediately, but set it when completion called to avoid modifications during generation
    """

    model_config = global_var.get(global_var.Model_Config)
    if model_config is None:
        model_config = ModelConfigBody()
        global_var.set(global_var.Model_Config, model_config)
    merge_model(model_config, body)
    exception = load_rwkv_state(
        global_var.get(global_var.Model), model_config.state, True
    )
    if exception is not None:
        raise exception
    print("Updated Model Config:", model_config)

    return "success"


@router.get("/status", tags=["Configs"])
def status():
    device_name = "CPU"
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
    
    model_path = None
    model = global_var.get(global_var.Model)
    if model:
        model_path = model.model_path  # 假设RWKV模型对象有 model_path 属性，保存了当前模型路径
    
    return {
        "status": global_var.get(global_var.Model_Status),
        "pid": os.getpid(),
        "device_name": device_name,
        "model_path": model_path  # 返回模型路径
    }

