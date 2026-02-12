import { db } from '../config/firebase';
import { doc, getDoc, onSnapshot } from 'firebase/firestore';

/**
 * Récupère l'état d'une vidéo depuis Firestore
 * @param {string} videoId - L'ID de la vidéo (ex: "theme_123456")
 * @returns {Promise<Object|null>} - Les données de video_status ou null
 */
export const getVideoStatus = async (videoId) => {
  try {
    const docRef = doc(db, 'video_status', videoId);
    const docSnap = await getDoc(docRef);
    
    if (docSnap.exists()) {
      return docSnap.data();
    } else {
      return null;
    }
  } catch (error) {
    console.error('Error fetching video status:', error);
    return null;
  }
};

/**
 * Écoute les changements d'état d'une vidéo en temps réel
 * @param {string} videoId - L'ID de la vidéo
 * @param {Function} callback - Fonction appelée à chaque changement (data) => {}
 * @returns {Function} - Fonction pour arrêter l'écoute
 */
export const subscribeToVideoStatus = (videoId, callback) => {
  const docRef = doc(db, 'video_status', videoId);
  
  return onSnapshot(docRef, (docSnap) => {
    if (docSnap.exists()) {
      callback(docSnap.data());
    } else {
      callback(null);
    }
  }, (error) => {
    console.error('Error listening to video status:', error);
    callback(null);
  });
};

/**
 * Calcule un message lisible basé sur le statut
 * @param {Object} videoStatus - Les données de video_status
 * @returns {Object} - { message, progress, isComplete, hasError }
 */
export const getStatusMessage = (videoStatus) => {
  if (!videoStatus) {
    return {
      message: "Recherche de la vidéo...",
      progress: 0,
      isComplete: false,
      hasError: false
    };
  }

  const { status, completed_clips, total_clips } = videoStatus;
  const progress = total_clips > 0 ? (completed_clips / total_clips) * 100 : 0;

  switch (status) {
    case 'processing':
      return {
        message: `Génération des clips vidéo (${completed_clips}/${total_clips})...`,
        progress: Math.round(progress * 0.7), // 70% pour la génération
        isComplete: false,
        hasError: false,
        detail: `${completed_clips} clips prêts sur ${total_clips}`
      };
    
    case 'assembling':
    case 'assembling_partial':
      return {
        message: "Assemblage de la vidéo finale...",
        progress: 85,
        isComplete: false,
        hasError: false,
        detail: "Ajout de l'audio et des sous-titres"
      };
    
    case 'completed':
      return {
        message: "✅ Vidéo générée avec succès !",
        progress: 100,
        isComplete: true,
        hasError: false,
        detail: "Prête à être téléchargée"
      };
    
    case 'completed_with_errors':
      return {
        message: "⚠️ Vidéo générée avec quelques clips manquants",
        progress: 100,
        isComplete: true,
        hasError: false,
        detail: `${completed_clips}/${total_clips} clips disponibles`
      };
    
    case 'failed':
    case 'assembly_failed':
      return {
        message: "❌ Erreur lors de la génération",
        progress: 0,
        isComplete: false,
        hasError: true,
        detail: "Veuillez réessayer"
      };
    
    default:
      return {
        message: "Préparation...",
        progress: 10,
        isComplete: false,
        hasError: false
      };
  }
};

/**
 * Récupère l'URL de téléchargement de la vidéo finale
 * @param {string} videoId - L'ID de la vidéo
 * @returns {Promise<string|null>} - URL signée ou null
 */
export const getVideoDownloadUrl = async (videoId) => {
  try {
    const response = await fetch(`/api/videos/${videoId}/download`);
    if (response.ok) {
      const data = await response.json();
      return data.url;
    }
    return null;
  } catch (error) {
    console.error('Error getting download URL:', error);
    return null;
  }
};
