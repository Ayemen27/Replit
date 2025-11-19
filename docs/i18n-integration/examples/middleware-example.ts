// مثال: Middleware لاكتشاف اللغة
import { NextRequest, NextResponse } from 'next/server';

const SUPPORTED_LOCALES = ['ar', 'en'];
const DEFAULT_LOCALE = 'ar';

export function middleware(request: NextRequest) {
  // 1. التحقق من اللغة في URL
  const pathname = request.nextUrl.pathname;
  const pathnameLocale = SUPPORTED_LOCALES.find(
    locale => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameLocale) {
    // حفظ في Cookie
    const response = NextResponse.next();
    response.cookies.set('locale', pathnameLocale, { path: '/', maxAge: 31536000 });
    return response;
  }

  // 2. التحقق من Cookie
  let locale = request.cookies.get('locale')?.value;
  
  // 3. التحقق من Accept-Language header
  if (!locale) {
    const acceptLang = request.headers.get('accept-language');
    locale = acceptLang?.split(',')[0]?.split('-')[0];
  }

  // 4. Fallback للغة الافتراضية
  if (!SUPPORTED_LOCALES.includes(locale || '')) {
    locale = DEFAULT_LOCALE;
  }

  // إعادة التوجيه إلى URL مع اللغة
  const response = NextResponse.redirect(
    new URL(`/${locale}${pathname}`, request.url)
  );
  response.cookies.set('locale', locale, { path: '/', maxAge: 31536000 });
  
  return response;
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
