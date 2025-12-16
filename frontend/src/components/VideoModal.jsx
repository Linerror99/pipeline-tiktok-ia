import React from 'react';
import { X } from 'lucide-react';

const VideoModal = ({ video, onClose }) => {
  if (!video) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="relative bg-gray-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h3 className="text-lg font-semibold text-white truncate pr-4">
            {video.theme}
          </h3>
          <button
            onClick={onClose}
            className="flex-shrink-0 text-gray-400 hover:text-white transition-colors p-2 hover:bg-gray-800 rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Video Player */}
        <div className="relative bg-black aspect-[9/16] flex items-center justify-center">
          <video
            key={video.stream_url}
            controls
            autoPlay
            className="w-full h-full object-contain"
            controlsList="nodownload"
          >
            <source src={video.stream_url} type="video/mp4" />
            Votre navigateur ne supporte pas la lecture de vidéos.
          </video>
        </div>

        {/* Footer Info */}
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>Format 9:16 (TikTok/Shorts)</span>
            <span>ID: {video.id}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoModal;
