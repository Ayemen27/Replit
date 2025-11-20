

import fs from 'fs';
import path from 'path';

const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL || process.env.TOLGEE_API_URL;
const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY || process.env.TOLGEE_API_KEY;
const projectId = process.env.NEXT_PUBLIC_TOLGEE_PROJECT_ID || process.env.TOLGEE_PROJECT_ID;

interface Translation {
  key: string;
  translations: {
    [lang: string]: string;
  };
}

function flattenObject(obj: any, prefix = ''): { [key: string]: string } {
  const result: { [key: string]: string } = {};

  for (const [key, value] of Object.entries(obj)) {
    const newKey = prefix ? `${prefix}.${key}` : key;

    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      Object.assign(result, flattenObject(value, newKey));
    } else if (typeof value === 'string') {
      result[newKey] = value;
    }
  }

  return result;
}

async function getOrCreateKey(keyName: string): Promise<number | null> {
  try {
    // Try to get existing key
    const getResponse = await fetch(
      `${apiUrl}/v2/projects/${projectId}/keys?filterKeyName=${encodeURIComponent(keyName)}`,
      {
        headers: { 'X-API-Key': apiKey! },
      }
    );

    if (getResponse.ok) {
      const data = await getResponse.json();
      if (data._embedded?.keys?.length > 0) {
        return data._embedded.keys[0].id;
      }
    }

    // Create new key
    const createResponse = await fetch(`${apiUrl}/v2/projects/${projectId}/keys`, {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: keyName }),
    });

    if (createResponse.ok) {
      const data = await createResponse.json();
      return data.id;
    } else if (createResponse.status === 409) {
      // Key exists but we couldn't find it, try again
      await new Promise(resolve => setTimeout(resolve, 100));
      return getOrCreateKey(keyName);
    }

    return null;
  } catch (error) {
    console.error(`Error with key ${keyName}:`, error);
    return null;
  }
}

async function setTranslation(keyId: number, languageTag: string, text: string): Promise<boolean> {
  try {
    const response = await fetch(
      `${apiUrl}/v2/projects/${projectId}/translations`,
      {
        method: 'PUT',
        headers: {
          'X-API-Key': apiKey!,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          key: keyId,
          languageTag,
          text,
        }),
      }
    );

    return response.ok;
  } catch (error) {
    console.error(`Error setting translation for key ${keyId}:`, error);
    return false;
  }
}

async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 رفع الترجمات المباشر إلى Tolgee');
  console.log('='.repeat(60));
  console.log();

  if (!apiUrl || !apiKey || !projectId) {
    console.error('❌ متغيرات البيئة غير موجودة');
    process.exit(1);
  }

  const localesDir = path.join(process.cwd(), 'public', 'locales');
  const languages = ['ar', 'en'];
  const namespaces = ['admin', 'auth', 'cms', 'common', 'dashboard', 'errors', 'layout', 'marketing', 'validation'];

  const translations: Translation[] = [];

  // Read all translation files
  console.log('📖 قراءة ملفات الترجمة...\n');

  for (const namespace of namespaces) {
    const translationMap: { [key: string]: { [lang: string]: string } } = {};

    for (const lang of languages) {
      const filePath = path.join(localesDir, lang, `${namespace}.json`);
      
      if (!fs.existsSync(filePath)) {
        console.log(`   ⚠️  الملف غير موجود: ${filePath}`);
        continue;
      }

      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);
      const flattened = flattenObject(data);

      for (const [key, value] of Object.entries(flattened)) {
        const fullKey = `${namespace}.${key}`;
        
        if (!translationMap[fullKey]) {
          translationMap[fullKey] = {};
        }
        
        translationMap[fullKey][lang] = value;
      }
    }

    // Convert to array
    for (const [key, langs] of Object.entries(translationMap)) {
      translations.push({ key, translations: langs });
    }

    console.log(`   ✅ ${namespace}: ${Object.keys(translationMap).length} مفتاح`);
  }

  console.log(`\n📊 إجمالي المفاتيح: ${translations.length}\n`);
  console.log('='.repeat(60));
  console.log();

  let success = 0;
  let failed = 0;

  for (let i = 0; i < translations.length; i++) {
    const { key, translations: trans } = translations[i];
    
    if ((i + 1) % 10 === 0 || i === 0) {
      console.log(`\n📝 معالجة المفتاح ${i + 1}/${translations.length}: ${key}`);
    }

    // Get or create key
    const keyId = await getOrCreateKey(key);
    
    if (!keyId) {
      console.error(`   ❌ فشل إنشاء/جلب المفتاح: ${key}`);
      failed++;
      continue;
    }

    // Set translations for each language
    let keySuccess = true;
    for (const [lang, text] of Object.entries(trans)) {
      const result = await setTranslation(keyId, lang, text);
      
      if (!result) {
        console.error(`   ❌ فشل تعيين الترجمة: ${key} [${lang}]`);
        keySuccess = false;
      }
    }

    if (keySuccess) {
      success++;
      if ((i + 1) % 10 === 0) {
        console.log(`   ✅ تم رفع ${success} مفتاح بنجاح`);
      }
    } else {
      failed++;
    }

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  console.log();
  console.log('='.repeat(60));
  console.log('📊 النتائج النهائية:');
  console.log(`   ✅ نجح: ${success}`);
  console.log(`   ❌ فشل: ${failed}`);
  console.log(`   📈 معدل النجاح: ${((success / translations.length) * 100).toFixed(1)}%`);
  console.log('='.repeat(60));
  console.log();
}

main().catch(console.error);
