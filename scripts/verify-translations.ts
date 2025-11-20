#!/usr/bin/env tsx

async function verifyTranslations() {
  const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL || process.env.TOLGEE_API_URL;
  const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY || process.env.TOLGEE_API_KEY;
  const projectId = process.env.NEXT_PUBLIC_TOLGEE_PROJECT_ID || process.env.TOLGEE_PROJECT_ID;

  console.log('\n🔍 التحقق من الترجمات في Tolgee...\n');

  if (!apiUrl || !apiKey || !projectId) {
    console.error('❌ متغيرات البيئة غير موجودة');
    process.exit(1);
  }

  try {
    const languages = ['ar', 'en'];
    
    // جلب جميع المفاتيح أولاً
    console.log('📋 جلب قائمة المفاتيح...');
    const keysResponse = await fetch(`${apiUrl}/v2/projects/${projectId}/keys?size=1000`, {
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json',
      },
    });

    let allKeys: any[] = [];
    if (keysResponse.ok) {
      const keysData = await keysResponse.json();
      allKeys = keysData._embedded?.keys || [];
      console.log(`✅ عدد المفاتيح الكلي: ${allKeys.length}\n`);
    }
    
    for (const lang of languages) {
      console.log(`🌐 فحص الترجمات للغة: ${lang === 'ar' ? 'العربية' : 'English'} (${lang})`);
      
      // عد المفاتيح المترجمة لهذه اللغة
      let translatedCount = 0;
      let untranslatedCount = 0;
      const sampleTranslations: { key: string; value: string }[] = [];
      
      for (const key of allKeys) {
        const translation = key.translations?.[lang];
        if (translation && translation.text) {
          translatedCount++;
          if (sampleTranslations.length < 5) {
            sampleTranslations.push({
              key: key.name,
              value: translation.text
            });
          }
        } else {
          untranslatedCount++;
        }
      }
      
      console.log(`   ✅ مفاتيح مترجمة: ${translatedCount}`);
      console.log(`   ⚠️  مفاتيح غير مترجمة: ${untranslatedCount}`);
      
      if (sampleTranslations.length > 0) {
        console.log('   📝 أمثلة على الترجمات:');
        sampleTranslations.forEach(({ key, value }) => {
          const displayValue = value.substring(0, 50) + (value.length > 50 ? '...' : '');
          console.log(`      - ${key}: "${displayValue}"`);
        });
      }
      console.log();
    }

    // جلب إحصائيات المشروع
    console.log('\n📊 إحصائيات المشروع:');
    const statsResponse = await fetch(`${apiUrl}/v2/projects/${projectId}`, {
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json',
      },
    });

    if (statsResponse.ok) {
      const project = await statsResponse.json();
      console.log(`   - عدد المفاتيح: ${project.keyCount}`);
      console.log(`   - عدد اللغات: ${project.languageCount}`);
      console.log(`   - نسبة الترجمة: ${project.translatedPercentage || 'N/A'}`);
      console.log(`   - نسبة المراجعة: ${project.reviewedPercentage || 'N/A'}`);
      
      if (project.languageStats) {
        console.log('\n   📈 تفاصيل اللغات:');
        project.languageStats.forEach((lang: any) => {
          console.log(`      ${lang.languageFlagEmoji} ${lang.languageName} (${lang.languageTag}):`);
          console.log(`         - مفاتيح مترجمة: ${lang.translatedKeyCount}`);
          console.log(`         - كلمات مترجمة: ${lang.translatedWordCount}`);
        });
      }
    }

    console.log('\n✨ اكتمل التحقق!\n');
  } catch (error) {
    console.error('\n❌ خطأ:', error);
  }
}

verifyTranslations();
