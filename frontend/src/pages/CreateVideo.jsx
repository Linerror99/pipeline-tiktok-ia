import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, CheckCircle, AlertCircle, Key } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { subscribeToVideoStatus, getStatusMessage } from '../services/videoStatus';
import VideoGenerationProgress from '../components/VideoGenerationProgress';

const CreateVideo = () => {
  const { refreshUser } = useAuth();
  const [theme, setTheme] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [videoId, setVideoId] = useState(null);
  const [error, setError] = useState(null);
  const [videoStatus, setVideoStatus] = useState(null);
  const [statusInfo, setStatusInfo] = useState(null);

  const exampleThemes = [
    "Les mystères des pyramides de Bosnie",
    "Technologies impossibles des anciens Égyptiens",
    "Le triangle des Bermudes - découverte 2024",
    "Les secrets du château de Versailles",
    "L'intelligence artificielle va-t-elle dominer le monde?"
  ];

  // Écouter les changements d'état en temps réel
  useEffect(() => {
    if (!videoId) return;

    console.log('🔄 Abonnement aux changements pour:', videoId);
    
    const unsubscribe = subscribeToVideoStatus(videoId, (data) => {
      console.log('📊 Nouveau statut reçu:', data);
      setVideoStatus(data);
      
      if (data) {
        const info = getStatusMessage(data);
        setStatusInfo(info);
        
        // Arrêter le chargement si terminé ou erreur
        if (info.isComplete || info.hasError) {
          setIsGenerating(false);
          refreshUser(); // Rafraîchir le quota
        }
      }
    });

    return () => {
      console.log('🛑 Désabonnement des changements');
      unsubscribe();
    };
  }, [videoId, refreshUser]);

  const stages = [
    { id: 1, name: 'Script', icon: '📝', description: 'Génération du scénario' },
    { id: 2, name: 'Audio', icon: '🎙️', description: 'Création de la voix off' },
    { id: 3, name: 'Vidéo', icon: '🎬', description: 'Génération des clips' },
    { id: 4, name: 'Assemblage', icon: '🎞️', description: 'Montage final' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!theme.trim() || !accessCode.trim()) return;

    setIsGenerating(true);
    setError(null);
    setVideoId(null);
    setVideoStatus(null);
    setStatusInfo({ message: 'Démarrage de la génération...', progress: 5, isComplete: false, hasError: false });

    try {
      const apiUrl = import.meta.env.VITE_API_URL || '/api';
      const response = await axios.post(`${apiUrl}/videos/create`, {
        theme: theme,
        access_code: accessCode
      });

      const newVideoId = response.data.video_id;
      console.log('✅ Vidéo créée:', newVideoId);
      setVideoId(newVideoId);
      
      // Le useEffect va automatiquement commencer à écouter les changements
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de la génération');
      setIsGenerating(false);
      setStatusInfo(null);
    }
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
          {/* Access Code Input */}
          <div>
            <label className="flex items-center text-sm font-semibold mb-3 text-gray-300">
              <Key className="w-4 h-4 mr-2 text-primary" />
              🔐 Code d'accès
            </label>
            <input
              type="text"
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
              placeholder="ABC12345"
              className="input-field text-center text-xl font-mono tracking-wider"
              disabled={isGenerating}
              maxLength={8}
              minLength={8}
              required
            />
            <p className="text-xs text-gray-500 mt-2">
              🔄 Le code change toutes les heures. Contactez l'admin pour l'obtenir.
            </p>
          </div>

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
            disabled={!theme.trim() || !accessCode.trim() || accessCode.length !== 8 || isGenerating}
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
      {isGenerating && statusInfo && (
        <VideoGenerationProgress
          progress={statusInfo.progress}
          message={statusInfo.message}
          detail={statusInfo.detail}
          isComplete={statusInfo.isComplete}
          hasError={statusInfo.hasError}
        />
      )}

      {/* Success Display with Video Info */}
      {statusInfo?.isComplete && videoStatus && (
        <div className="card border-green-700 bg-green-900/20 mt-6">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500 mt-1" />
            <div className="flex-1">
              <h4 className="font-semibold text-green-400 mb-1">Vidéo générée avec succès !</h4>
              <p className="text-sm text-gray-300 mb-3">ID: {videoId}</p>
              <div className="flex space-x-3">
                <a
                  href="/my-videos"
                  className="btn-primary text-sm"
                >
                  Voir mes vidéos
                </a>
                <button
                  onClick={() => {
                    setVideoId(null);
                    setVideoStatus(null);
                    setStatusInfo(null);
                    setTheme('');
                  }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors"
                >
                  Créer une autre vidéo
                </button>
              </div>
            </div>
          </div>
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
