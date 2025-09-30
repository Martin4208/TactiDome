import React from "react";
import { MapContainer, TileLayer, Marker } from "react-leaflet"
import "leaflet/dist/leaflet.css"

// 型定義を追加
interface DroneStats {
  id: string;
  battery: number;
  condition: string;
  timestamp: string;
}

interface Location {
  latitude: number;
  longitude: number;
  altitude: number;
}

interface Movement {
  speed: number;
  direction: number;
}

interface Discovery {
  found: string;
  object?: string;
  danger?: string;
}

interface DroneData {
  drone_stats: DroneStats;
  location: Location;
  movement: Movement;
  discovery?: Discovery;
}

// Props の型定義
interface DroneMapProps {
  drones: DroneData[];
}

const tokyo_station_lat = 35.681236
const tokyo_station_lon = 139.767125
const position: [number, number] = [tokyo_station_lat, tokyo_station_lon]
const zoom_level = 14

// カスタムアイコンを作成
const createIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background-color: ${color};
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid white;
    "></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

const DroneMap: React.FC<DroneMapProps> = ({ drones }) => {
    return (
        <MapContainer 
            center={position} 
            zoom={zoom_level} 
            style={{height: "100%", width: "100%"}} 
            scrollWheelZoom={false}
        >
            <TileLayer 
                attribution="&copy; <a href=https://www.openstreetmap.org/copyright>OpenStreetMap</a> contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {drones.map((drone) => {
                // ← { } で囲む
                const markerColor = drone.drone_stats.condition === "enemy" ? "red" : "blue";
                
                return (
                    <Marker 
                        key={drone.drone_stats.id}
                        position={[drone.location.latitude, drone.location.longitude]}
                        icon={createIcon(markerColor)}
                    />
                );
            })}
        </MapContainer>
    );
};

export default DroneMap;
