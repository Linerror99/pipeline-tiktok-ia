import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyDPQ-Inb5R-pWuomNIZHCvOL60ylWBi36w',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'reetik-project.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'reetik-project',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'reetik-project.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '838433433731',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:838433433731:web:b055ef2a639363a71f53b6',
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const googleProvider = new GoogleAuthProvider()

export default app
