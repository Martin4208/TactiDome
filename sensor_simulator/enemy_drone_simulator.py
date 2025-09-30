import requests
import time
import random
import math
import datetime
import json

class EnemyDrone:
    tokyo_station_lat = 35.681236
    tokyo_station_lon = 139.767125
    def __init__(self):
        self.angle = random.randint(0, 360)
        self.altitude = 0
        self.speed = 50.0
        self.appear_rad_lat = 7 / 111
        self.appear_rad_lon = 7 / 91
        self.lat = self.tokyo_station_lat + self.appear_rad_lat * math.cos(math.radians(self.angle))
        self.lon = self.tokyo_station_lon + self.appear_rad_lon * math.sin(math.radians(self.angle))
        self.target_lat = self.tokyo_station_lat
        self.target_lon = self.tokyo_station_lon
        
        
    def calculate_position(self):
        diff_lat = self.target_lat - self.lat
        diff_lon = self.target_lon - self.lon
        
        distance = math.sqrt(diff_lat**2 + diff_lon**2)
        print(f"基地までの距離: {distance:.6f}")
        
        if distance < 0.0001:
            self.speed = 0.0
            print("爆破されました。")
        else:
            step = min(0.001, distance/2)
            self.lat += step * (diff_lat / distance)
            self.lon += step * (diff_lon / distance)


    def create_data(self):
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        direction = int(math.degrees(self.angle) % 360)
            
        data = {
            "drone_stats": {
                "id": "E0001",
                "battery": 0,           # ← 追加（敵なので0）
                "condition": "enemy",   # ← 追加（敵識別用）
                "timestamp": timestamp
            },
            "location": {
                "latitude": self.lat,
                "longitude": self.lon,
                "altitude": 30
            },
            "movement": {
                "speed": self.speed,
                "direction": direction
            }
        }
        
        return data


    def POST(self):
        data = self.create_data()
        
        # ← データを確認（最初の1回だけ）
        if not hasattr(self, '_printed'):
            print("=== 送信データ ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=================")
            self._printed = True
        
        try: 
            response = requests.post(
                url="http://localhost:8000/sensor-data",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"[E0001] 敵ドローン発見")
            else:
                print(f"[E0001] エラー {response.status_code}")
                print(f"エラー内容: {response.json()}")
        except Exception as e:
            print(f"送信エラー: {e}")



def main():
    enemy = EnemyDrone()
    
    while enemy.speed > 0:
        enemy.calculate_position()
        enemy.POST()
        time.sleep(0.001)
    
    print("敵ドローン消滅")
        
        
if __name__ == "__main__":
    main()