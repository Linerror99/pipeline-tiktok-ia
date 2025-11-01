import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import CreateVideo from './pages/CreateVideo';
import MyVideos from './pages/MyVideos';
import Dashboard from './pages/Dashboard';
import Logs from './pages/Logs';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<CreateVideo />} />
          <Route path="/create" element={<CreateVideo />} />
          <Route path="/my-videos" element={<MyVideos />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
