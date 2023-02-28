from fastapi import Depends, FastAPI
from sklearn.neural_network import MLPClassifier

from model2queue import api_task_consumer, api_task_producer

app = FastAPI()

X = [[0.0, 0.0], [1.0, 1.0]]
y = [0, 1]
clf = MLPClassifier(
    solver="lbfgs", alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1
)

clf.fit(X, y)


@api_task_consumer()
def predict_input(input):
    print(f"input: {input}")
    print(f"preds: {clf.predict(input)}")


@api_task_producer()
def preprocess_request(x: int) -> int:
    return [[x, x]]


def process_request(x: int) -> str:
    return "ok"


app.post("/predict", dependencies=[Depends(preprocess_request)])(process_request)
