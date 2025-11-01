import React, { useState } from 'react';
import { Sparkles, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const CreateVideo = () => {
  const [theme, setTheme] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [error, setError] = useState(null);

  const exampleThemes = [
    "Les mystères des pyramides de Bosnie",
    "Technologies impossibles des anciens Égyptiens",
    "Le triangle des Bermudes - découverte 2024",
    "Les secrets du château de Versailles",
    "L'intelligence artificielle va-t-elle dominer le monde?"
  ];

  const stages = [
    { id: 1, name: 'Script', icon: '📝', description: 'Génération du scénario' },
    { id: 2, name: 'Audio', icon: '🎙️', description: 'Création de la voix off' },
    { id: 3, name: 'Vidéo', icon: '🎬', description: 'Génération des clips' },
    { id: 4, name: 'Assemblage', icon: '🎞️', description: 'Montage final' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!theme.trim()) return;

    setIsGenerating(true);
    setError(null);
    setStatus({ stage: 1, message: 'Démarrage de la génération...' });

    try {
      // TODO: Remplacer par votre URL Cloud Function
      const response = await axios.post('http://localhost:8000/api/videos/create', {
        theme: theme
      });

      setVideoId(response.data.video_id);
      
      // Simuler la progression (à remplacer par un vrai polling)
      simulateProgress();
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la génération');
      setIsGenerating(false);
    }
  };

  const simulateProgress = () => {
    let currentStage = 1;
    const interval = setInterval(() => {
      currentStage++;
      if (currentStage <= 4) {
        setStatus({ 
          stage: currentStage, 
          message: `${stages[currentStage - 1].description} en cours...` 
        });
      } else {
        setStatus({ stage: 5, message: 'Vidéo générée avec succès !' });
        setIsGenerating(false);
        clearInterval(interval);
      }
    }, 5000);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Page Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-primary to-pink-600 rounded-full mb-6 shadow-2xl shadow-primary/50">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-primary to-pink-600 bg-clip-text text-transparent">
          Créer une Vidéo TikTok
        </h1>
        <p className="text-gray-400 text-lg">
          Entrez un thème captivant et laissez l'IA créer une vidéo virale en quelques minutes
        </p>
      </div>

      {/* Main Form Card */}
      <div className="card mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Theme Input */}
          <div>
            <label className="block text-sm font-semibold mb-3 text-gray-300">
              🎯 Thème de votre vidéo
            </label>
            <textarea
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="Ex: Les secrets cachés du château de Versailles..."
              className="input-field h-32 resize-none"
              disabled={isGenerating}
            />
            <p className="text-xs text-gray-500 mt-2">
              💡 Conseil : Soyez spécifique et intriguant pour un meilleur résultat
            </p>
          </div>

          {/* Example Themes */}
          <div>
            <p className="text-sm font-semibold mb-3 text-gray-300">
              ✨ Exemples de thèmes viraux :
            </p>
            <div className="flex flex-wrap gap-2">
              {exampleThemes.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setTheme(example)}
                  className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-2 rounded-lg transition-all duration-200"
                  disabled={isGenerating}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!theme.trim() || isGenerating}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {isGenerating ? (
              <span className="flex items-center justify-center">
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Génération en cours...
              </span>
            ) : (
              <span className="flex items-center justify-center">
                <Sparkles className="w-5 h-5 mr-2" />
                Générer ma vidéo TikTok
              </span>
            )}
          </button>
        </form>
      </div>

      {/* Progress Display */}
      {isGenerating && status && (
        <div className="card">
          <h3 className="text-xl font-bold mb-6 flex items-center">
            <Loader2 className="w-6 h-6 mr-2 animate-spin text-primary" />
            Pipeline en cours d'exécution
          </h3>

          {/* Progress Steps */}
          <div className="space-y-4">
            {stages.map((stage) => (
              <div
                key={stage.id}
                className={`flex items-center space-x-4 p-4 rounded-lg transition-all duration-300 ${
                  status.stage === stage.id
                    ? 'bg-primary/20 border border-primary'
                    : status.stage > stage.id
                    ? 'bg-green-900/20 border border-green-700'
                    : 'bg-gray-700/50 border border-gray-700'
                }`}
              >
                <div className="text-3xl">{stage.icon}</div>
                <div className="flex-1">
                  <h4 className="font-semibold">{stage.name}</h4>
                  <p className="text-sm text-gray-400">{stage.description}</p>
                </div>
                {status.stage === stage.id && (
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                )}
                {status.stage > stage.id && (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                )}
              </div>
            ))}
          </div>

          {status.stage === 5 && (
            <div className="mt-6 p-4 bg-green-900/20 border border-green-700 rounded-lg">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-500" />
                <div>
                  <p className="font-semibold text-green-400">Vidéo générée avec succès !</p>
                  <p className="text-sm text-gray-400">ID: {videoId}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="card border-red-700 bg-red-900/20">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-red-500 mt-1" />
            <div>
              <h4 className="font-semibold text-red-400 mb-1">Erreur de génération</h4>
              <p className="text-sm text-gray-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Info Section */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
          <div className="text-2xl mb-2">⏱️</div>
          <h4 className="font-semibold mb-1">Durée</h4>
          <p className="text-sm text-gray-400">64-80 secondes</p>
        </div>
        <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
          <div className="text-2xl mb-2">📱</div>
          <h4 className="font-semibold mb-1">Format</h4>
          <p className="text-sm text-gray-400">9:16 (TikTok/Shorts)</p>
        </div>
        <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
          <div className="text-2xl mb-2">🤖</div>
          <h4 className="font-semibold mb-1">IA</h4>
          <p className="text-sm text-gray-400">Gemini + Veo 3.0</p>
        </div>
      </div>
    </div>
  );
};

export default CreateVideo;
