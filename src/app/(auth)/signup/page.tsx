
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FiEye, FiEyeOff, FiMail, FiLock, FiUser, FiGithub, FiChrome, FiApple, FiCheckCircle } from 'react-icons/fi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useTranslate } from '@/lib/i18n/hooks';

export default function SignupPage() {
  const { t } = useTranslate('auth');
  const { t: tValidation } = useTranslate('validation');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const getPasswordStrength = (pass: string) => {
    if (pass.length === 0) return { strength: 0, label: '', color: '' };
    if (pass.length < 8) return { strength: 1, label: t('signup.password.weak'), color: 'bg-red-500' };
    if (pass.length < 12) return { strength: 2, label: t('signup.password.medium'), color: 'bg-yellow-500' };
    if (pass.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/)) {
      return { strength: 3, label: t('signup.password.strong'), color: 'bg-green-500' };
    }
    return { strength: 2, label: t('signup.password.medium'), color: 'bg-yellow-500' };
  };

  const passwordStrength = getPasswordStrength(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!acceptTerms) {
      setError(tValidation('terms.required'));
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError(tValidation('password.mismatch'));
      setLoading(false);
      return;
    }

    if (password.length < 8) {
      setError(tValidation('password.tooShort'));
      setLoading(false);
      return;
    }

    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || 'فشل في إنشاء الحساب');
      }

      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="flex relative overflow-hidden bg-gradient-to-br from-purple-50 via-pink-50 to-red-50">
      {/* خلفية متحركة احترافية */}
      <div className="absolute inset-0">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      {/* القسم الأيسر - النموذج */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8 py-12 lg:py-16 relative z-10">
        <div className="w-full max-w-md">
          {/* بطاقة طائرة مع ظلال */}
          <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 sm:p-10 space-y-6 border border-white/20 transform transition-all duration-300 hover:shadow-3xl hover:-translate-y-1">
            {/* الشعار والعنوان */}
            <div className="text-center space-y-2">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 text-white text-xl font-bold mb-3 shadow-lg">
              K2
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              {t('signup.title')}
            </h1>
            <p className="text-gray-600 text-sm">
              {t('signup.subtitle')}
            </p>
          </div>

          {/* رسائل الخطأ */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg animate-in slide-in-from-top-2">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="mr-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* نموذج التسجيل */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <User className="w-4 h-4" />
                  {t('signup.name.label')}
                </Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder={t('signup.name.placeholder')}
                  className="h-12 text-base transition-all focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {t('signup.email.label')}
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="example@email.com"
                  className="h-12 text-base transition-all focus:ring-2 focus:ring-purple-500"
                  dir="ltr"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  {t('signup.password.label')}
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={8}
                    placeholder="••••••••"
                    className="h-12 text-base pr-12 transition-all focus:ring-2 focus:ring-purple-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {password && (
                  <div className="space-y-1">
                    <div className="flex gap-1">
                      {[1, 2, 3].map((level) => (
                        <div
                          key={level}
                          className={`h-1 flex-1 rounded-full transition-all ${
                            level <= passwordStrength.strength ? passwordStrength.color : 'bg-gray-200'
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-gray-600">{passwordStrength.label}</p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  {t('signup.confirmPassword.label')}
                </Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    placeholder="••••••••"
                    className="h-12 text-base pr-12 transition-all focus:ring-2 focus:ring-purple-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <input
                type="checkbox"
                id="terms"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="w-4 h-4 mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="terms" className="text-sm text-gray-600">
                {t('signup.terms.text')}{' '}
                <Link href="/terms" className="text-purple-600 hover:text-purple-700 font-medium">
                  {t('signup.terms.terms')}
                </Link>{' '}
                {t('signup.terms.and')}{' '}
                <Link href="/privacy" className="text-purple-600 hover:text-purple-700 font-medium">
                  {t('signup.terms.privacy')}
                </Link>
              </label>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 text-base font-semibold bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-lg"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {t('signup.submitting')}
                </div>
              ) : (
                t('signup.submit')
              )}
            </Button>
          </form>

          {/* فاصل */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">{t('signup.orSignupWith')}</span>
            </div>
          </div>

          {/* تسجيل الدخول الاجتماعي */}
          <div className="grid grid-cols-3 gap-3">
            <button
              type="button"
              className="flex items-center justify-center h-12 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all transform hover:scale-105 active:scale-95"
            >
              <Chrome className="w-5 h-5 text-gray-700" />
            </button>
            <button
              type="button"
              className="flex items-center justify-center h-12 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all transform hover:scale-105 active:scale-95"
            >
              <Github className="w-5 h-5 text-gray-700" />
            </button>
            <button
              type="button"
              className="flex items-center justify-center h-12 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all transform hover:scale-105 active:scale-95"
            >
              <Apple className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          {/* رابط تسجيل الدخول */}
          <div className="text-center text-sm">
            <span className="text-gray-600">{t('signup.hasAccount')} </span>
            <Link href="/login" className="text-purple-600 hover:text-purple-700 font-semibold transition-colors">
              {t('signup.loginLink')}
            </Link>
          </div>
          </div>
        </div>
      </div>

      {/* القسم الأيمن - المميزات (مخفي على الموبايل) */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-purple-600 via-pink-600 to-red-600 items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]" />
        <div className="relative z-10 text-white space-y-6 max-w-md">
          <h2 className="text-4xl font-bold">
            {t('signup.rightPanel.title')}
          </h2>
          <p className="text-xl text-pink-100">
            {t('signup.rightPanel.subtitle')}
          </p>
          <div className="space-y-4 pt-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-white" />
              <span>{t('signup.rightPanel.feature1')}</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-white" />
              <span>{t('signup.rightPanel.feature2')}</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-white" />
              <span>{t('signup.rightPanel.feature3')}</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-white" />
              <span>{t('signup.rightPanel.feature4')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
