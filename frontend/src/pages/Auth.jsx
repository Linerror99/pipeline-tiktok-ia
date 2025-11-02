import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Sparkles, Lock, Mail, Key, AlertCircle, CheckCircle } from 'lucide-react';

const Auth = () => {
  const navigate = useNavigate();
  const { verifyCode, register, login } = useAuth();
  
  const [activeTab, setActiveTab] = useState('login'); // 'login' ou 'register'
  const [step, setStep] = useState('code'); // 'code' ou 'form' (pour les deux)
  
  // Formulaire
  const [accessCode, setAccessCode] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // États
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await verifyCode(accessCode);
      const successMessage = activeTab === 'register' 
        ? '✅ Code valide ! Vous pouvez vous inscrire.'
        : '✅ Code valide ! Vous pouvez vous connecter.';
      setSuccess(successMessage);
      setStep('form');
    } catch (err) {
      setError(err.response?.data?.detail || 'Code invalide. Il change toutes les heures.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(email, password, accessCode);
      navigate('/create');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/create');
    } catch (err) {
      setError(err.response?.data?.detail || 'Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  const switchToRegister = () => {
    setActiveTab('register');
    setStep('code');
    setError('');
    setSuccess('');
    setEmail('');
    setPassword('');
    setAccessCode('');
  };

  const switchToLogin = () => {
    setActiveTab('login');
    setStep('code');
    setError('');
    setSuccess('');
    setEmail('');
    setPassword('');
    setAccessCode('');
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-4 shadow-lg shadow-primary/50">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-pink-600 bg-clip-text text-transparent">
            Pipeline Vidéo IA
          </h1>
          <p className="text-gray-400 mt-2">Créez des vidéos TikTok automatiquement</p>
        </div>

        {/* Card */}
        <div className="bg-gray-800 border border-gray-700 rounded-2xl shadow-xl overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            <button
              onClick={switchToLogin}
              className={`flex-1 py-4 text-center font-semibold transition-colors ${
                activeTab === 'login'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Connexion
            </button>
            <button
              onClick={switchToRegister}
              className={`flex-1 py-4 text-center font-semibold transition-colors ${
                activeTab === 'register'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              Inscription
            </button>
          </div>

          {/* Content */}
          <div className="p-8">
            {/* Erreur */}
            {error && (
              <div className="mb-6 p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-200">{error}</p>
              </div>
            )}

            {/* Succès */}
            {success && (
              <div className="mb-6 p-4 bg-green-900/30 border border-green-500/50 rounded-lg flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-green-200">{success}</p>
              </div>
            )}

            {/* LOGIN */}
            {activeTab === 'login' && (
              <>
                {/* Étape 1 : Vérifier le code */}
                {step === 'code' && (
                  <form onSubmit={handleVerifyCode} className="space-y-6">
                    <div className="text-center mb-6">
                      <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/20 rounded-full mb-3">
                        <Key className="w-6 h-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold text-white">Code d'accès requis</h3>
                      <p className="text-sm text-gray-400 mt-1">
                        Entrez le code d'accès pour vous connecter. Le code change toutes les heures.
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Code d'accès
                      </label>
                      <input
                        type="text"
                        value={accessCode}
                        onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg text-center text-2xl font-mono tracking-wider focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500"
                        placeholder="ABC12345"
                        required
                        maxLength={8}
                        minLength={8}
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={loading || accessCode.length !== 8}
                      className="w-full bg-gradient-to-r from-primary to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-primary-dark hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                    >
                      {loading ? 'Vérification...' : 'Vérifier le code'}
                    </button>
                  </form>
                )}

                {/* Étape 2 : Formulaire de connexion */}
                {step === 'form' && (
                  <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Email
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500"
                          placeholder="votre@email.com"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Mot de passe
                      </label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500"
                          placeholder="••••••••"
                          required
                          minLength={8}
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-primary to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-primary-dark hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                    >
                      {loading ? 'Connexion...' : 'Se connecter'}
                    </button>

                    <button
                      type="button"
                      onClick={() => setStep('code')}
                      className="w-full text-sm text-gray-400 hover:text-gray-200"
                    >
                      ← Changer de code
                    </button>
                  </form>
                )}
              </>
            )}

            {/* REGISTER */}
            {activeTab === 'register' && (
              <>
                {/* Étape 1 : Vérifier le code */}
                {step === 'code' && (
                  <form onSubmit={handleVerifyCode} className="space-y-6">
                    <div className="text-center mb-6">
                      <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/20 rounded-full mb-3">
                        <Key className="w-6 h-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold text-white">Code d'accès requis</h3>
                      <p className="text-sm text-gray-400 mt-1">
                        Le code change toutes les heures. Demandez-le à l'administrateur.
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Code d'accès
                      </label>
                      <input
                        type="text"
                        value={accessCode}
                        onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                        className="w-full px-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg text-center text-2xl font-mono tracking-wider focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500"
                        placeholder="ABC12345"
                        required
                        maxLength={8}
                        minLength={8}
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={loading || accessCode.length !== 8}
                      className="w-full bg-gradient-to-r from-primary to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-primary-dark hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                    >
                      {loading ? 'Vérification...' : 'Vérifier le code'}
                    </button>
                  </form>
                )}

                {/* Étape 2 : Formulaire d'inscription */}
                {step === 'form' && (
                  <form onSubmit={handleRegister} className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Email
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500"
                          placeholder="votre@email.com"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Mot de passe
                      </label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 text-white rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent placeholder-gray-500"
                          placeholder="••••••••"
                          required
                          minLength={8}
                        />
                      </div>
                      <p className="text-xs text-gray-400 mt-1">Minimum 8 caractères</p>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-primary to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-primary-dark hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary/30"
                    >
                      {loading ? 'Inscription...' : 'Créer mon compte'}
                    </button>

                    <button
                      type="button"
                      onClick={() => setStep('code')}
                      className="w-full text-sm text-gray-400 hover:text-gray-200"
                    >
                      ← Changer de code
                    </button>
                  </form>
                )}
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-400 mt-6">
          {activeTab === 'login' ? (
            <>
              Pas encore de compte ?{' '}
              <button onClick={switchToRegister} className="text-primary hover:text-primary-dark font-semibold">
                S'inscrire
              </button>
            </>
          ) : (
            <>
              Déjà un compte ?{' '}
              <button onClick={switchToLogin} className="text-primary hover:text-primary-dark font-semibold">
                Se connecter
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
};

export default Auth;
