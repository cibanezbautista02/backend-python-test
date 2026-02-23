from fastapi import FastAPI
import uuid
import requests
import os
from fastapi import HTTPException, status
from record import RequestBody, ResponseCreated, NotificationStatus, SendProcessingRequest, StatusResponse

provider_url = "http://localhost:3001/v1/notify"
bbdd_path = "storage/bbdd.json"
headers = {"X-API-Key": "test-dev-2026"}

os.makedirs("storage", exist_ok=True)

app = FastAPI(title="Notification Service")

bbdd = {}
def send_to_bbdd(notification_id, data_dict):
    """Función para almacenar en la bbdd
    Esto seria ineficiente pero es 
    para simular donde almacenariamos en la bbdd"""
    with open(bbdd_path, "a") as f:
        f.write(f"{notification_id}: {data_dict}\n")

@app.post("/v1/requests", status_code=status.HTTP_201_CREATED) 
async def request_notification(body: RequestBody):
    """En este endpoint registramos la notificación
    y almacenamos en la base de datos simulada (bbdd) 
    con un id único generado por uuid4.
    Además tomamos el 201 como código de respuesta para 
    indicar que se ha creado correctamente."""

    notification_id = str(uuid.uuid4())
    if notification_id in bbdd and body != None:
        raise HTTPException(status_code=400, detail="Notification already exists")

    bbdd[notification_id] = {
        "id": notification_id,
        "to": body.to,
        "message": body.message,
        "type": body.type,
        "status": NotificationStatus.queued
    }
    send_to_bbdd(notification_id, bbdd[notification_id])

    return ResponseCreated(id=notification_id)



@app.post("/v1/requests/{id}/process")
def process_notification(id: str):
    """En este endpoint procesamos la notificación,
     cambiamos su estado a 'processing' y enviamos al proveedor."""

    if id not in bbdd:
        raise HTTPException(status_code=404, detail="Notification not found")

    if id is not None and bbdd[id]["status"] == NotificationStatus.queued:
        bbdd[id]["status"] = NotificationStatus.processing
        payload_object = SendProcessingRequest(id=id, message=bbdd[id]["message"], to=bbdd[id]["to"])
        payload = payload_object.model_dump()
        
        try:
            response = requests.post(provider_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                bbdd[id]["status"] = NotificationStatus.sent
            else:
                bbdd[id]["status"] = NotificationStatus.failed
        except Exception as e:
            bbdd[id]["status"] = NotificationStatus.failed
            raise HTTPException(status_code=500, detail="Error processing notification")

    return {"message": "Notification processing finished"}

@app.get("/v1/requests/{id}")
async def get_notification(id: str):
    """En este endpoint obtenemos el estado de la notificación"""

    if id not in bbdd:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    current_status = bbdd[id].get("status", NotificationStatus.queued)
    return StatusResponse(id=id, status=current_status)
