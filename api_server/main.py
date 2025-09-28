from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError, Field
import logging
import datetime
from typing import Optional, Literal
import json

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DroneStats(BaseModel):
    id: str
    battery: float = Field(ge=0, le=100)
    condition: Literal["normal", "warning", "error"]
    timestamp: str


class Location(BaseModel):
    latitude: float = Field(ge=35.66, le=35.70)
    longitude: float = Field(ge=139.74, le=139.79)
    altitude:  float = Field(ge=0.0, le=50.0)


class Movement(BaseModel):
    speed: float = Field(ge=0.0, le=65.0)
    direction: int = Field(ge=0, le=359)


class Discovery(BaseModel):
    found: Literal["yes", "no"]
    object: Optional[Literal["car", "person", "military_vehicle", "suspicious"]] = None
    danger: Optional[Literal["yes", "no"]] = None


class SensorData(BaseModel):
    drone_stats: DroneStats
    location: Location
    movement: Movement
    discovery: Optional[Discovery] = None
    
    
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        
        
    def add_connection(self, websocket):
        self.active_connections.append(websocket)
        
    def remove_connection(self, websocket):
        self.active_connections.remove(websocket)
        
    async def broadcast_to_all(self, data):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except WebSocketDisconnect:
                disconnected.append(connection)
                
        for conn in disconnected:
            self.remove_connection(conn)


@app.post("/sensor-data")
async def send_data(request_data: dict):
    drone_id = request_data.get("drone_stats", {}).get("id", "UNKNOWN")
    
    try:
        data = SensorData(**request_data)
        logger.info(f"[{drone_id}] 正常受信 - バッテリー:{data.drone_stats.battery}% 位置:({data.location.latitude}, {data.location.longitude})")
        await manager.broadcast_to_all(json.dumps(request_data))
        return {"status": "success"}
    except ValidationError as e:
        errors = e.errors()
        
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        logger.error(f"[{drone_id}] 検証エラー ({now}): {len(errors)}件のエラー")
        
        details = []
        for error in errors:
            field = error['loc'][-1]
            value = error.get('input')
            msg = error['msg']
            details.append({"field": field, "value": value, "message": msg})
            
        raise HTTPException(
            status_code=400,
            detail={
                "error": "validation_failed", 
                "details": details
            }
        )


manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    manager.add_connection(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            manager.broadcast_to_all(data)
    except WebSocketDisconnect:
        print("WebSocket接続が切断されました")
        manager.remove_connection(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
