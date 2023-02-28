import numpy as np
import tensorflow as tf
from fastapi import Depends, FastAPI, UploadFile

from model2queue.helper import get_logger
from model2queue import api_task_producer, start_api_task_consumer

app = FastAPI()
logger = get_logger(__name__)


def predict_input(input):
    img = tf.keras.preprocessing.image.load_img(
        input["image_path"], target_size=(224, 224)
    )
    img = np.array(img)
    preprocees_input = tf.keras.applications.vgg16.preprocess_input(
        img, data_format=None
    )
    logger.info(f"preprocees_input_shape: {preprocees_input.shape}")


@api_task_producer()
def preprocess_request(file: UploadFile) -> dict:
    file_location = f"/tmp/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"image_path": file_location}


async def create_file(file: UploadFile) -> dict:
    return {"status": "ok"}


app.post("/predict", dependencies=[Depends(preprocess_request)])(create_file)

start_api_task_consumer(predict_input)
