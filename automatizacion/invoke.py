import json
import boto3
import base64

LAMBDA_NAME = "post-proyectos-portafolio-lambda"

def invoke_lambda():
    lambda_client = boto3.client("lambda", region_name="us-east-1")

    # Cargar el event.json
    with open("event.json", "r") as f:
        payload = json.load(f)

    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        Payload=json.dumps(payload),
        LogType="Tail"
    )

    # Logs decodificados
    if "LogResult" in response:
        logs = base64.b64decode(response["LogResult"]).decode("utf-8")
        print("📄 Logs:")
        print(logs)

    print("\n📥 Respuesta:")
    print(response["Payload"].read().decode("utf-8"))

if __name__ == "__main__":
    invoke_lambda()
