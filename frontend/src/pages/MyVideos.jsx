import React, { useState, useEffect } from 'react';
import { Video, Download, Play, Clock, Loader2, RefreshCw } from 'lucide-react';
import axios from 'axios';
import VideoModal from '../components/VideoModal';

const MyVideos = () => {
  const [videos, setVideos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVideo, setSelectedVideo] = useState(null);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/api/videos');
      setVideos(response.data.videos || []);
    } catch (err) {
      setError('Erreur lors du chargement des vidéos');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayVideo = async (video) => {
    try {
      // Récupérer l'URL de streaming
      const response = await axios.get(`http://localhost:8000/api/videos/${video.id}/stream`);
      setSelectedVideo({
        ...video,
        stream_url: response.data.stream_url
      });
    } catch (err) {
      console.error('Erreur lors de la récupération du stream:', err);
      alert('Impossible de charger la vidéo');
    }
  };

  const handleDownloadVideo = async (video) => {
    try {
      // Récupérer l'URL de téléchargement
      const response = await axios.get(`http://localhost:8000/api/videos/${video.id}/download`);
      
      // Ouvrir l'URL dans un nouvel onglet pour déclencher le téléchargement
      window.open(response.data.download_url, '_blank');
    } catch (err) {
      console.error('Erreur lors du téléchargement:', err);
      alert('Impossible de télécharger la vidéo');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { color: 'bg-green-500', text: 'Terminée', icon: '✅' },
      processing: { color: 'bg-yellow-500', text: 'En cours', icon: '⏳' },
      failed: { color: 'bg-red-500', text: 'Échouée', icon: '❌' },
    };

    const config = statusConfig[status] || statusConfig.processing;

    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-semibold ${config.color} text-white`}>
        <span>{config.icon}</span>
        <span>{config.text}</span>
      </span>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Chargement de vos vidéos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card border-red-700 bg-red-900/20 max-w-2xl mx-auto">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={fetchVideos} className="btn-primary">
            <RefreshCw className="w-4 h-4 mr-2 inline" />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-pink-600 bg-clip-text text-transparent">
            Mes Vidéos
          </h1>
          <p className="text-gray-400">
            {videos.length} vidéo{videos.length > 1 ? 's' : ''} générée{videos.length > 1 ? 's' : ''}
          </p>
        </div>
        <button onClick={fetchVideos} className="btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2 inline" />
          Actualiser
        </button>
      </div>

      {/* Videos Grid */}
      {videos.length === 0 ? (
        <div className="card text-center py-16">
          <Video className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2 text-gray-300">
            Aucune vidéo pour le moment
          </h3>
          <p className="text-gray-400 mb-6">
            Créez votre première vidéo TikTok avec l'IA !
          </p>
          <a href="/create" className="btn-primary inline-block">
            Créer une vidéo
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div key={video.id} className="card group hover:shadow-2xl transition-all duration-300">
              {/* Video Thumbnail */}
              <div className="relative aspect-[9/16] bg-gray-900 rounded-xl overflow-hidden mb-4">
                {video.thumbnail_url ? (
                  <img
                    src={video.thumbnail_url}
                    alt={video.theme}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <Video className="w-16 h-16 text-gray-600" />
                  </div>
                )}
                
                {/* Play Overlay */}
                {video.status === 'completed' && (
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                    <button className="bg-primary rounded-full p-4 transform scale-75 group-hover:scale-100 transition-transform duration-300">
                      <Play className="w-8 h-8 text-white" fill="white" />
                    </button>
                  </div>
                )}

                {/* Status Badge */}
                <div className="absolute top-3 right-3">
                  {getStatusBadge(video.status)}
                </div>
              </div>

              {/* Video Info */}
              <div className="space-y-3">
                <h3 className="font-semibold text-lg line-clamp-2 text-gray-100">
                  {video.theme}
                </h3>

                <div className="flex items-center text-sm text-gray-400">
                  <Clock className="w-4 h-4 mr-1" />
                  {formatDate(video.created_at)}
                </div>

                {video.duration && (
                  <div className="text-sm text-gray-400">
                    Durée : {video.duration}s
                  </div>
                )}

                {/* Actions */}
                {video.status === 'completed' && (
                  <div className="flex space-x-2 pt-2">
                    <button 
                      onClick={() => handlePlayVideo(video)}
                      className="flex-1 bg-primary hover:bg-pink-600 text-white text-sm font-semibold py-2 rounded-lg transition-all duration-200"
                    >
                      <Play className="w-4 h-4 inline mr-1" />
                      Voir
                    </button>
                    <button 
                      onClick={() => handleDownloadVideo(video)}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-sm font-semibold py-2 rounded-lg transition-all duration-200"
                    >
                      <Download className="w-4 h-4 inline mr-1" />
                      Télécharger
                    </button>
                  </div>
                )}

                {video.status === 'processing' && (
                  <div className="pt-2">
                    <div className="bg-gray-700 rounded-full h-2 overflow-hidden">
                      <div className="bg-primary h-full animate-pulse" style={{ width: '60%' }}></div>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Génération en cours...</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>

    {/* Video Modal */}
    {selectedVideo && (
      <VideoModal 
        video={selectedVideo} 
        onClose={() => setSelectedVideo(null)} 
      />
    )}
  </>
  );
};

export default MyVideos;
