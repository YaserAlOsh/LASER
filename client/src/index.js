// Importing necessary components and modules from React and other dependencies
import { Suspense } from 'react';
import ReactDOM from 'react-dom';
import "./index.css";
import './config';
import { Home, Login, Account, NotFound, Register } from './pages';
import Tool from './pages/Tool';

import * as serviceWorker from './serviceWorker';
// Importing routing components from 'react-router-dom'
import { BrowserRouter, Route, Routes } from 'react-router-dom';

// Main App component that defines the routing structure of the application
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Define routes for different pages in the application */}
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/account" element={<Account />} />
        <Route path="/notfound" element={<NotFound />} />
        <Route path="/tool" element={<Tool />} />
      </Routes>
    </BrowserRouter>
  );
}

// Rendering the App component inside a Suspense boundary to handle async loading
ReactDOM.createRoot(document.getElementById('root')).render(
  <Suspense fallback={<div>Loading...</div>}>
    <App />
  </Suspense>
);

serviceWorker.unregister();