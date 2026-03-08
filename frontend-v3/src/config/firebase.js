import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyDSqTfHzJxUh9PZb3qZT5yKqJxN8gRJqFo',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'pipeline-video-ia.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'pipeline-video-ia',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'pipeline-video-ia.appspot.com',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '354616212471',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:354616212471:web:abc123def456',
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const googleProvider = new GoogleAuthProvider()

export default app
