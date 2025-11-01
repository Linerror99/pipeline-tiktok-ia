import React from 'react';
import { BarChart3, TrendingUp, Clock, Video } from 'lucide-react';

const Dashboard = () => {
  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-primary to-pink-600 bg-clip-text text-transparent">
        Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Stats Cards */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Total Vidéos</p>
              <p className="text-3xl font-bold">0</p>
            </div>
            <Video className="w-12 h-12 text-primary opacity-50" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">En cours</p>
              <p className="text-3xl font-bold">0</p>
            </div>
            <Clock className="w-12 h-12 text-yellow-500 opacity-50" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Terminées</p>
              <p className="text-3xl font-bold">0</p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-500 opacity-50" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Taux de succès</p>
              <p className="text-3xl font-bold">0%</p>
            </div>
            <BarChart3 className="w-12 h-12 text-secondary opacity-50" />
          </div>
        </div>
      </div>

      {/* Coming Soon Message */}
      <div className="card text-center py-16">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-primary to-pink-600 rounded-full mb-6 opacity-50">
          <BarChart3 className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-2xl font-bold mb-4 text-gray-300">Dashboard en construction</h2>
        <p className="text-gray-400 max-w-md mx-auto">
          Cette fonctionnalité sera bientôt disponible. Vous pourrez visualiser des statistiques détaillées, 
          des graphiques et des analyses de vos vidéos générées.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
