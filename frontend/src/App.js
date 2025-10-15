import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/stocks/')
      .then(response => response.json())
      .then(data => setStocks(data))
      .catch(error => console.error('Error fetching stocks:', error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Monitor</h1>


        <div>
          <h2>Current Stocks</h2>
          {stocks.length > 0 ? (
            <ul>
              {stocks.map(stock => (
                <li key={stock.id}>
                  {stock.symbol}: ${stock.price} (Last updated: {new Date(stock.timestamp).toLocaleString()})
                </li>
              ))}
            </ul>
          ) : (
            <p>No stocks to display. Add some using the backend API.</p>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
