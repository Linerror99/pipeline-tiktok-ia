import React from 'react';
import PropTypes from 'prop-types';

const VideoGenerationProgress = ({ progress, message, detail, isComplete, hasError }) => {
  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* En-tête */}
      <div className="mb-4">
        <h3 className={`text-lg font-semibold ${
          hasError ? 'text-red-600' : 
          isComplete ? 'text-green-600' : 
          'text-blue-600'
        }`}>
          {message}
        </h3>
        {detail && (
          <p className="text-sm text-gray-600 mt-1">{detail}</p>
        )}
      </div>

      {/* Barre de progression */}
      <div className="relative w-full h-4 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ease-out ${
            hasError ? 'bg-red-500' :
            isComplete ? 'bg-green-500' :
            'bg-blue-500 animate-pulse'
          }`}
          style={{ width: `${progress}%` }}
        />
        
        {/* Animation de progression pour les états en cours */}
        {!isComplete && !hasError && (
          <div className="absolute top-0 left-0 h-full w-full overflow-hidden">
            <div className="h-full w-1/3 bg-white opacity-30 animate-slide" />
          </div>
        )}
      </div>

      {/* Pourcentage */}
      <div className="mt-2 text-right">
        <span className={`text-sm font-medium ${
          hasError ? 'text-red-600' :
          isComplete ? 'text-green-600' :
          'text-blue-600'
        }`}>
          {Math.round(progress)}%
        </span>
      </div>

      {/* Icône de statut */}
      <div className="mt-4 flex items-center justify-center">
        {isComplete ? (
          <div className="flex items-center space-x-2 text-green-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="font-medium">Terminé !</span>
          </div>
        ) : hasError ? (
          <div className="flex items-center space-x-2 text-red-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span className="font-medium">Échec</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-blue-600">
            <svg className="animate-spin w-6 h-6" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span className="font-medium">En cours...</span>
          </div>
        )}
      </div>
    </div>
  );
};

VideoGenerationProgress.propTypes = {
  progress: PropTypes.number.isRequired,
  message: PropTypes.string.isRequired,
  detail: PropTypes.string,
  isComplete: PropTypes.bool,
  hasError: PropTypes.bool
};

VideoGenerationProgress.defaultProps = {
  detail: null,
  isComplete: false,
  hasError: false
};

export default VideoGenerationProgress;
