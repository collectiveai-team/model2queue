model2queue
==============================

A library to expose an api with a queue for batch predictions

The model2queue is a library designed to simplify the execution of heavy functions such as model predictions by queuing tasks in a queue. The library provides an easy-to-use API to queue tasks and define the function to consume a task item.

![Pylint Score](https://img.shields.io/badge/Pylint%20Score-9.85%2F10-brightgreen)
PyLint Score: 0

## Installation
You can install the Queued Function Executor using pip:

```python
pip install model2queue
```

## Usage
The model2queue can be used to execute heavy functions such as model predictions in the background, allowing your main application to continue running without being blocked. The library is particularly useful for long-running tasks that may take several minutes or even hours to complete.

Here is an example of how to use the model2queue to queue a task:

```python
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

```

# Development
## Jupyterlab container
There is jupyterlab container images to run the notebooks
### Build
```make jupyter-build```

### Run
with gpu capabilities:

```make jupyter-run```

or cpu only

```make jupyter-run-cpu```

Project Organization
------------

```
.
├── build                                   -> Docker building files & utils
│   ├── core
│   └── jupyter
├── notebooks                               -> Notebooks with experimentes and examples
│   └── ...
├── reports                                 -> Reports generated by results from experiments
│   └── ...
├── resources                               -> general resources: models, datasets, cache, etc
│   ├── cache
│   ├── models
│   ├── datasets
│   └── ...
├── scripts                                 -> utils
└── src                                     -> main root of packages
    └── model2queue                             -> main package
```


<p><small>Project based on the <a target="_blank" href="https://github.collective.com/DataScience/project-scaffolding/">cookiecutter data science collective template</a>. #cookiecutterdatasciencecollective</small></p>
