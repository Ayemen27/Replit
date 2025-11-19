import Link from 'next/link';

interface SanityHomeData {
  title?: string;
  sections?: Array<{
    _type: string;
    _key: string;
    title?: string;
    subtitle?: string;
    heading?: string;
    description?: string;
    buttons?: Array<{
      text: string;
      link: string;
      variant?: string;
    }>;
    items?: Array<{
      title: string;
      description: string;
      icon?: string;
    }>;
    stats?: Array<{
      value: string;
      label: string;
      icon?: string;
    }>;
  }>;
}

interface HomeSanityContentProps {
  data: SanityHomeData;
}

export function HomeSanityContent({ data }: HomeSanityContentProps) {
  if (!data || !data.sections) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {data.sections.map((section) => {
        // Hero Section
        if (section._type === 'heroSection') {
          return (
            <div
              key={section._key}
              className="bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 text-white"
            >
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
                <div className="text-center">
                  <h1 className="text-5xl md:text-6xl font-bold mb-6">
                    {section.title || 'Build software faster'}
                  </h1>
                  {section.subtitle && (
                    <p className="text-2xl md:text-3xl mb-4 text-white font-semibold">
                      {section.subtitle}
                    </p>
                  )}
                  <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
                    {section.description ||
                      'The collaborative browser-based IDE'}
                  </p>
                  <div className="flex flex-wrap items-center justify-center gap-4">
                    {section.buttons && section.buttons.length > 0 ? (
                      section.buttons.map((button, idx) => (
                        <Link
                          key={idx}
                          href={button.link || '/signup'}
                          className={
                            idx === 0
                              ? 'px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg'
                              : 'px-8 py-4 bg-blue-700 text-white rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-400'
                          }
                        >
                          {button.text}
                        </Link>
                      ))
                    ) : (
                      <>
                        <Link
                          href="/signup"
                          className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg"
                        >
                          ابدأ البناء مجاناً
                        </Link>
                        <Link
                          href="/gallery"
                          className="px-8 py-4 bg-blue-700 text-white rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-400"
                        >
                          استكشف المشاريع
                        </Link>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        }

        // Features Grid Section
        if (section._type === 'valuePropGridSection') {
          return (
            <div key={section._key} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
              {section.heading && (
                <h2 className="text-3xl font-bold text-gray-900 text-center mb-4">
                  {section.heading}
                </h2>
              )}
              {section.description && (
                <p className="text-xl text-gray-600 text-center mb-12 max-w-3xl mx-auto">
                  {section.description}
                </p>
              )}
              {section.items && section.items.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {section.items.map((item, idx) => (
                    <div key={idx} className="p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
                      {item.icon && (
                        <div className="text-4xl mb-4">{item.icon}</div>
                      )}
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        {item.title}
                      </h3>
                      <p className="text-gray-600">{item.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        }

        // Stats Section
        if (section._type === 'statsSection') {
          return (
            <div key={section._key} className="bg-white border-t border-gray-200">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                {section.heading && (
                  <h2 className="text-3xl font-bold text-gray-900 text-center mb-4">
                    {section.heading}
                  </h2>
                )}
                {section.description && (
                  <p className="text-xl text-gray-600 text-center mb-12 max-w-3xl mx-auto">
                    {section.description}
                  </p>
                )}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                  {section.stats && section.stats.length > 0 ? (
                    section.stats.map((stat, idx) => (
                      <div key={idx} className="p-6">
                        {stat.icon && (
                          <div className="text-4xl mb-3">{stat.icon}</div>
                        )}
                        <div className="text-4xl font-bold mb-2 text-blue-600">
                          {stat.value}
                        </div>
                        <div className="text-gray-600">{stat.label}</div>
                      </div>
                    ))
                  ) : (
                    <>
                      <div className="p-6">
                        <div className="text-4xl font-bold text-blue-600 mb-2">
                          10M+
                        </div>
                        <div className="text-gray-600">
                          مطور يبني على K2Panel Ai
                        </div>
                      </div>
                      <div className="p-6">
                        <div className="text-4xl font-bold text-purple-600 mb-2">
                          50M+
                        </div>
                        <div className="text-gray-600">مشروع تم إنشاؤه</div>
                      </div>
                      <div className="p-6">
                        <div className="text-4xl font-bold text-pink-600 mb-2">
                          100+
                        </div>
                        <div className="text-gray-600">
                          لغة برمجة مدعومة
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        }

        // CTA Band Section
        if (section._type === 'ctaBandSection') {
          return (
            <div key={section._key} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
                <h2 className="text-3xl font-bold mb-4">
                  {section.title || 'Ready to start building?'}
                </h2>
                <p className="text-xl mb-8 text-blue-100">
                  {section.description ||
                    'Join millions of developers creating amazing things'}
                </p>
                {section.buttons && section.buttons.length > 0 && (
                  <div className="flex flex-wrap items-center justify-center gap-4">
                    {section.buttons.map((button, idx) => (
                      <Link
                        key={idx}
                        href={button.link || '/signup'}
                        className={
                          idx === 0
                            ? 'inline-block px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors shadow-lg'
                            : 'inline-block px-8 py-4 bg-blue-700 text-white rounded-lg font-semibold hover:bg-blue-800 transition-colors border border-blue-400'
                        }
                      >
                        {button.text}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        }

        return null;
      })}
    </div>
  );
}
