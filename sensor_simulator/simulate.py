import requests
import time
import random
import math
import datetime

class Drone:
    tokyo_station_lat = 35.681236
    tokyo_station_lon = 139.767125
    patrol_radius = 2
    battery_decline_rate = 0.1
    detect_rate = 0.03
    def __init__(self):
        self.angle = 0
        self.altitude = 0
        self.battery = 100
        self.flying_stats = "patrol"
        self.speed = 0.0
        self.lat = self.tokyo_station_lat
        self.lon = self.tokyo_station_lon
        
        
    def calculate_position(self):
        if self.flying_stats == "patrol":
            # 大まかな変換（東京周辺）
            # 緯度1度 ≈ 111km
            # 経度1度 ≈ 91km（東京の緯度では）

            lat_per_km = 1 / 111  # 緯度の1kmあたりの度数
            lon_per_km = 1 / 91   # 経度の1kmあたりの度数
            
            radius_lat = self.patrol_radius * lat_per_km
            radius_lon = self.patrol_radius * lon_per_km
            
            self.lat = self.tokyo_station_lat + radius_lat * math.cos(self.angle)
            self.lon = self.tokyo_station_lon + radius_lon * math.sin(self.angle)
            
            # 20分 = 1200秒
            # 3秒ごとに更新 = 1200 ÷ 3 = 400回の更新
            # 1周360度 ÷ 400回 = 0.9度ずつ進む

            # 速度 = 12.57km ÷ 20分 = 約37.7km/h
            self.angle += math.radians(0.9)
            
            self.speed = 37.7
            
            self.battery -= self.battery_decline_rate
        
            if self.battery < 0:
                self.battery = 0
                
            if self.battery <= 15:
                self.flying_stats = "return"
    
    
    def create_data(self):
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        direction = int(math.degrees(self.angle) % 360)
        
        if random.random() < self.detect_rate:
            objects = ["car", "person", "military_vehicle", "suspicious"]
            discovery = {
                "found": "yes",
                "object": random.choice(objects),
                "danger": random.choice(["yes", "no"])
            }
        else:
            discovery = None
            
        data = {
            "drone_stats": {
                "id": "D0001",
                "battery": int(self.battery),
                "condition": "normal",
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
        
        if discovery is not None:
            data["discovery"] = discovery
        
        return data
    
    
    def flying_stats_check(self):
        if self.flying_stats == "patrol":
            pass
        elif self.flying_stats == "return":
            print(f"帰還モード開始 - 現在位置: ({self.lat:.6f}, {self.lon:.6f})")
            
            target_lat = self.tokyo_station_lat
            target_lon = self.tokyo_station_lon
            
            diff_lat = target_lat - self.lat
            diff_lon = target_lon - self.lon
            
            distance = math.sqrt(diff_lat**2 + diff_lon**2)
            print(f"基地までの距離: {distance:.6f}")
            
            if distance < 0.001:
                self.flying_stats = "stop"
                self.speed = 0.0
                print("基地に到着しました。任務完了。")
            else:
                step = 0.001
                self.lat += step * (diff_lat / distance)
                self.lon += step * (diff_lon / distance)
                self.speed = 60.0
                print(f"基地に向かって移動中...")


    def POST(self):
        data = self.create_data()
        
        try: 
            response = requests.post(
                url="http://localhost:8000/sensor-data",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print(f"[D0001] データ送信成功 - バッテリー:{self.battery:.1f}%")
            else:
                print(f"[D0001] 送信失敗: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"送信エラー: {e}")



def main():
    drone = Drone()
    
    try:
        while drone.flying_stats != "stop":
            drone.calculate_position()
            drone.POST()
            drone.flying_stats_check()
            time.sleep(0.001)
        print("プログラム終了")
    except KeyboardInterrupt:
        print("Ctrl+Cで停止されました")
        
        
if __name__ == "__main__":
    main()