import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { SUPPORTED_LOCALES, type SupportedLocale } from './lib/i18n/constants';
import { resolveLocale } from './lib/i18n/locale-utils';

const LOCALE_COOKIE_NAME = 'NEXT_LOCALE';

function i18nMiddleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.startsWith('/static') ||
    pathname.includes('.') ||
    pathname.startsWith('/fonts') ||
    pathname.startsWith('/images') ||
    pathname === '/404' ||
    pathname === '/500'
  ) {
    return NextResponse.next();
  }

  const pathSegments = pathname.split('/').filter(Boolean);
  const firstSegment = pathSegments[0];
  const hasLocaleInPath = SUPPORTED_LOCALES.includes(firstSegment as SupportedLocale);

  let locale: SupportedLocale;
  let pathWithoutLocale: string;

  if (hasLocaleInPath) {
    locale = firstSegment as SupportedLocale;
    pathWithoutLocale = '/' + pathSegments.slice(1).join('/');
    if (!pathWithoutLocale || pathWithoutLocale === '/') {
      pathWithoutLocale = '/';
    }
  } else {
    const cookieLocale = request.cookies.get(LOCALE_COOKIE_NAME)?.value;
    const acceptLanguage = request.headers.get('accept-language');
    
    locale = resolveLocale({
      cookie: cookieLocale,
      acceptLanguage,
    });
    
    pathWithoutLocale = pathname;
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-locale', locale);

  let response: NextResponse;

  if (hasLocaleInPath) {
    const url = request.nextUrl.clone();
    url.pathname = pathWithoutLocale;
    
    response = NextResponse.rewrite(url, {
      request: { headers: requestHeaders },
    });
  } else {
    response = NextResponse.next({
      request: { headers: requestHeaders },
    });
  }
  
  response.cookies.set(LOCALE_COOKIE_NAME, locale, {
    path: '/',
    maxAge: 31536000,
    sameSite: 'lax',
    httpOnly: false,
  });

  return response;
}

export default withAuth(
  function middleware(request: NextRequest) {
    return i18nMiddleware(request);
  },
  {
    pages: {
      signIn: '/login',
    },
    callbacks: {
      authorized: ({ token, req }) => {
        const { pathname } = req.nextUrl;
        const pathSegments = pathname.split('/').filter(Boolean);
        const firstSegment = pathSegments[0];
        const hasLocaleInPath = SUPPORTED_LOCALES.includes(firstSegment as SupportedLocale);
        const actualPath = hasLocaleInPath ? '/' + pathSegments.slice(1).join('/') : pathname;
        
        const protectedPaths = ['/dashboard', '/profile', '/replView', '/workspace'];
        const adminPaths = ['/admin'];
        
        const isProtectedPath = protectedPaths.some(path => actualPath.startsWith(path));
        const isAdminPath = adminPaths.some(path => actualPath.startsWith(path));
        
        // Public paths
        if (!isProtectedPath && !isAdminPath) return true;
        
        // Protected paths require token
        if (!token) return false;
        
        // Admin paths require admin role
        if (isAdminPath && token.role !== 'admin') {
          return false;
        }
        
        return true;
      },
    },
  }
);

export const config = {
  matcher: [
    '/((?!_next|api|static|.*\\..*|fonts|images).*)',
  ],
};
