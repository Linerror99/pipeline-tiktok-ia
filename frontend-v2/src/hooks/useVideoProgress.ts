import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, VideoStatus } from '../services/api';

export function useVideoProgress(videoId: string | null) {
  const [status, setStatus] = useState<VideoStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (!videoId) return;

    try {
      const ws = apiService.createWebSocket(videoId);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setStatus(data);
          
          // Si vidéo complétée ou en erreur, fermer WebSocket
          if (data.status === 'completed' || data.status === 'failed') {
            ws.close();
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('Connection error');
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        setIsConnected(false);
        wsRef.current = null;

        // Tentative de reconnexion si pas complété
        if (status?.status !== 'completed' && status?.status !== 'failed') {
          if (reconnectAttemptsRef.current < 5) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
            console.log(`Reconnecting in ${delay}ms...`);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptsRef.current++;
              connect();
            }, delay);
          } else {
            setError('Max reconnection attempts reached');
          }
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError(err instanceof Error ? err.message : 'Connection failed');
    }
  }, [videoId, status?.status]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Fallback: polling si WebSocket ne fonctionne pas
  useEffect(() => {
    if (!videoId || isConnected) return;

    const interval = setInterval(async () => {
      try {
        const currentStatus = await apiService.getVideoStatus(videoId);
        setStatus(currentStatus);

        // Arrêter polling si terminé
        if (currentStatus.status === 'completed' || currentStatus.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 3000); // Poll toutes les 3 secondes

    return () => clearInterval(interval);
  }, [videoId, isConnected]);

  // Connect on mount
  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return {
    status,
    isConnected,
    error,
    reconnect: connect,
    disconnect,
  };
}
