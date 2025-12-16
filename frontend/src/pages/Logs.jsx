import React from 'react';
import { FileText, Activity } from 'lucide-react';

const Logs = () => {
  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-primary to-pink-600 bg-clip-text text-transparent">
        Logs & Monitoring
      </h1>

      {/* Coming Soon Message */}
      <div className="card text-center py-16">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-primary to-pink-600 rounded-full mb-6 opacity-50">
          <Activity className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-2xl font-bold mb-4 text-gray-300">Monitoring en construction</h2>
        <p className="text-gray-400 max-w-md mx-auto mb-8">
          Cette fonctionnalité permettra de suivre en temps réel l'exécution de la pipeline, 
          visualiser les logs détaillés et débugger les erreurs.
        </p>
        
        {/* Preview Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto text-left">
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <FileText className="w-8 h-8 text-primary mb-3" />
            <h3 className="font-semibold mb-2">Logs en temps réel</h3>
            <p className="text-sm text-gray-400">
              Visualisez les logs de chaque agent Cloud Function
            </p>
          </div>
          
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <Activity className="w-8 h-8 text-green-500 mb-3" />
            <h3 className="font-semibold mb-2">Suivi Pipeline</h3>
            <p className="text-sm text-gray-400">
              Suivez l'état de chaque étape de génération
            </p>
          </div>
          
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <div className="text-3xl mb-3">🔍</div>
            <h3 className="font-semibold mb-2">Debugging</h3>
            <p className="text-sm text-gray-400">
              Identifiez et résolvez les problèmes rapidement
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Logs;
