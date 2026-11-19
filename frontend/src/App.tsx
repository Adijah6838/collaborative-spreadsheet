import { useEffect, useState, useRef } from 'react';

const ROWS = 10;
const COLS = 10;
const SPREADSHEET_ID = 1;

function App() {
  const [grid, setGrid] = useState<string[][]>(
    Array(ROWS).fill(null).map(() => Array(COLS).fill(""))
  );
  
  const [connectionStatus, setConnectionStatus] = useState("Disconnected");
  const [activeUsers, setActiveUsers] = useState(0);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = 'ws://localhost:8001/ws/' + SPREADSHEET_ID;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setConnectionStatus("Connected");
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === "cell_updated") {
        setGrid((prevGrid) => {
          const newGrid = [...prevGrid.map(row => [...row])];
          newGrid[message.row][message.col] = message.value;
          return newGrid;
        });
      } else if (message.type === "user_count") {
        setActiveUsers(message.count);
      }
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    ws.current.onclose = () => setConnectionStatus("Disconnected");

    return () => ws.current?.close();
  }, []);

  const handleCellChange = (row: number, col: number, value: string) => {
    setGrid((prevGrid) => {
      const newGrid = [...prevGrid.map(r => [...r])];
      newGrid[row][col] = value;
      return newGrid;
    });

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: "edit_cell", row, col, value }));
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <div className="max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Collaborative Spreadsheet</h1>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={connectionStatus === 'Connected' ? 'w-3 h-3 rounded-full bg-green-500' : 'w-3 h-3 rounded-full bg-red-500'}></div>
              <span className="text-sm font-medium text-gray-600">{connectionStatus}</span>
            </div>
            
            <div className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
              {activeUsers} Active User{activeUsers !== 1 ? 's' : ''}
            </div>

            <button 
              onClick={() => window.open('http://localhost:8001/export/1', '_blank')}
              className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-1.5 rounded transition-colors"
            >
              Export CSV
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="bg-gray-100 border border-gray-300 w-12 h-10"></th>
                {Array(COLS).fill(null).map((_, colIndex) => (
                  <th key={colIndex} className="bg-gray-100 border border-gray-300 w-24 h-10 text-sm text-gray-600">
                    {String.fromCharCode(65 + colIndex)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array(ROWS).fill(null).map((_, rowIndex) => (
                <tr key={rowIndex}>
                  <td className="bg-gray-100 border border-gray-300 text-center text-sm text-gray-600 font-medium">
                    {rowIndex + 1}
                  </td>
                  {Array(COLS).fill(null).map((_, colIndex) => (
                    <td key={colIndex} className="border border-gray-300 p-0">
                      <input
                        type="text"
                        value={grid[rowIndex][colIndex]}
                        onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
                        className="w-full h-10 px-2 outline-none focus:ring-2 focus:ring-blue-500 focus:bg-blue-50"
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;