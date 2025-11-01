import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Sparkles, 
  Video, 
  LayoutDashboard, 
  FileText,
  Film
} from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/create', icon: Sparkles, label: 'Créer' },
    { path: '/my-videos', icon: Video, label: 'Mes Vidéos' },
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/logs', icon: FileText, label: 'Logs' },
  ];

  const isActive = (path) => location.pathname === path || (path === '/create' && location.pathname === '/');

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50 shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="bg-gradient-to-r from-primary to-pink-600 p-2 rounded-xl shadow-lg group-hover:shadow-primary/50 transition-all duration-300">
                <Film className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-pink-600 bg-clip-text text-transparent">
                  Pipeline Vidéo IA
                </h1>
                <p className="text-xs text-gray-400">TikTok Generator</p>
              </div>
            </Link>

            {/* Navigation */}
            <nav className="flex space-x-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                      isActive(item.path)
                        ? 'bg-primary text-white shadow-lg shadow-primary/50'
                        : 'text-gray-400 hover:text-white hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 border-t border-gray-800 py-6">
        <div className="container mx-auto px-4 text-center text-gray-400">
          <p className="text-sm">
            Propulsé par <span className="text-primary font-semibold">Gemini 2.5 Pro</span> • 
            <span className="text-secondary font-semibold"> Veo 3.0</span> • 
            <span className="text-pink-500 font-semibold"> Google Cloud</span>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
