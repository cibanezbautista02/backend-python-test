from pydantic import BaseModel
from enum import Enum

class NotificationType(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"

class NotificationStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    sent = "sent"
    failed = "failed"

"""clases(records) necesarios para el endpoint número 1
RequestBody es el cuerpo en JSON, y el ReponseCreated confirma con 
el id del registro creado"""

class RequestBody(BaseModel):
    to: str
    message: str
    type: NotificationType

class ResponseCreated(BaseModel):
    id: str


"""Records necesarios para el endpoint número 2,
"""
class SendProcessingRequest(BaseModel):
    id: str
    message: str
    to: str


"""Records necesarios para el endpoint número 3,
donde status response es el que muestra el estado del proceso 
de la notificación"""

class StatusResponse(BaseModel):
    id: str
    status: NotificationStatus