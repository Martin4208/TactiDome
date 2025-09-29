import 'leaflet/dist/leaflet.css';
import './App.css'
import DroneMap from "./components/DroneMap"
import { useState, useEffect } from "react";

// 型定義（ここに追加）
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

const App = () => {
  const [drones, setDrones] = useState<DroneData[]>([]);

  useEffect(() => {
    // 1. WebSocket接続を作成
    const ws = new WebSocket("ws://localhost:8000/ws")

    // 2. 接続成功時
    ws.onopen = () => {
      console.log("WebSocket接続成功");
    }

    // 3. メッセージ受信時
    ws.onmessage = (event) => {
      const newDroneData: DroneData = JSON.parse(event.data);
      console.log('受信データ:', newDroneData);

      setDrones(prevDrones => {
        const existingIndex = prevDrones.findIndex(
          d => d.drone_stats.id === newDroneData.drone_stats.id
        );
        
        if (existingIndex >= 0) {
          // 既存ドローンを更新
          const updated = [...prevDrones];
          updated[existingIndex] = newDroneData;
          return updated;
        } else {
          // 新しいドローンを追加
          return [...prevDrones, newDroneData];
        }
      })
    }

    // 4. エラー時
    ws.onerror = (error) => {
      console.error("WebSocketエラー：", error);
    };

    // 5. クリーンアップ（コンポーネント削除時）
    return () => {
      ws.close();
    };
  },[]); // 空配列 = 初回のみ実行

  return (
    <div className="app-container">
      {/* ツールバー */}
      <div className="toolbar">
        ツールバー
      </div>
        
      {/* メインコンテンツ（ドローン一覧 ＋ 地図） */}
      <div className="main-content">
        <div className="drone-list">
          ドローン一覧
        </div>
        <div className="map-container">
          <DroneMap drones={drones}/>
        </div>
      </div>
    </div>
  )
}

export default App
