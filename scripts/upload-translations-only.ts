#!/usr/bin/env tsx

import * as fs from 'fs';
import * as path from 'path';

const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL || process.env.TOLGEE_API_URL;
const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY || process.env.TOLGEE_API_KEY;
const projectId = process.env.NEXT_PUBLIC_TOLGEE_PROJECT_ID || process.env.TOLGEE_PROJECT_ID;

interface FlatTranslations {
  [key: string]: string;
}

// تحويل الكائن المتداخل إلى مفاتيح مسطحة
function flattenObject(obj: any, prefix = ''): FlatTranslations {
  const flattened: FlatTranslations = {};
  
  for (const key in obj) {
    const value = obj[key];
    const newKey = prefix ? `${prefix}.${key}` : key;
    
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      Object.assign(flattened, flattenObject(value, newKey));
    } else {
      flattened[newKey] = String(value);
    }
  }
  
  return flattened;
}

// قراءة جميع ملفات JSON في مجلد
function readLocaleFiles(localePath: string): { [namespace: string]: FlatTranslations } {
  const namespaces: { [namespace: string]: FlatTranslations } = {};
  const files = fs.readdirSync(localePath).filter(f => f.endsWith('.json'));
  
  for (const file of files) {
    const namespace = path.basename(file, '.json');
    const content = JSON.parse(fs.readFileSync(path.join(localePath, file), 'utf-8'));
    namespaces[namespace] = flattenObject(content);
  }
  
  return namespaces;
}

async function uploadTranslationsOnly() {
  console.log('\n📤 بدء رفع الترجمات إلى Tolgee...\n');

  if (!apiUrl || !apiKey || !projectId) {
    console.error('❌ متغيرات البيئة غير موجودة');
    process.exit(1);
  }

  console.log('📋 معلومات الاتصال:');
  console.log(`  - API URL: ${apiUrl}`);
  console.log(`  - Project ID: ${projectId}`);
  console.log();

  const localesPath = path.join(process.cwd(), 'public', 'locales');
  const languages = ['ar', 'en'];
  
  // قراءة جميع الترجمات
  const allTranslations: { [lang: string]: { [namespace: string]: FlatTranslations } } = {};
  
  for (const lang of languages) {
    const langPath = path.join(localesPath, lang);
    if (fs.existsSync(langPath)) {
      allTranslations[lang] = readLocaleFiles(langPath);
      console.log(`✅ تم قراءة ترجمات ${lang}`);
    }
  }

  console.log();

  // جمع جميع المفاتيح الفريدة
  const allKeys = new Set<string>();
  const translationsMap = new Map<string, { [lang: string]: string }>();

  for (const lang of languages) {
    for (const namespace in allTranslations[lang]) {
      for (const key in allTranslations[lang][namespace]) {
        const fullKey = `${namespace}.${key}`;
        allKeys.add(fullKey);
        
        if (!translationsMap.has(fullKey)) {
          translationsMap.set(fullKey, {});
        }
        translationsMap.get(fullKey)![lang] = allTranslations[lang][namespace][key];
      }
    }
  }

  console.log(`📊 إحصائيات:`);
  console.log(`  - عدد المفاتيح: ${allKeys.size}`);
  console.log(`  - عدد اللغات: ${languages.length}`);
  console.log();

  let successCount = 0;
  let failedCount = 0;

  console.log('📤 رفع الترجمات...\n');

  // رفع كل ترجمة
  for (const fullKey of allKeys) {
    const translations = translationsMap.get(fullKey)!;
    
    console.log(`   🔑 ${fullKey}:`);
    
    for (const lang of languages) {
      if (translations[lang]) {
        try {
          const response = await fetch(`${apiUrl}/v2/projects/${projectId}/translations`, {
            method: 'POST',
            headers: {
              'X-API-Key': apiKey!,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              keyName: fullKey,
              languageTag: lang,
              text: translations[lang],
            }),
          });

          if (response.ok || response.status === 200) {
            const displayText = translations[lang].substring(0, 50);
            console.log(`      ✅ ${lang}: "${displayText}${translations[lang].length > 50 ? '...' : ''}"`);
            successCount++;
          } else {
            const error = await response.text();
            console.error(`      ❌ ${lang}: فشل - ${response.status} - ${error.substring(0, 80)}`);
            failedCount++;
          }
          
          // تأخير صغير
          await new Promise(resolve => setTimeout(resolve, 30));
        } catch (error) {
          console.error(`      ❌ ${lang}: خطأ -`, error);
          failedCount++;
        }
      }
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('📊 النتائج النهائية:');
  console.log('='.repeat(60));
  console.log(`✅ الترجمات المرفوعة بنجاح: ${successCount}`);
  console.log(`❌ الفشل: ${failedCount}`);
  console.log(`📈 النسبة: ${((successCount / (successCount + failedCount)) * 100).toFixed(2)}%`);
  console.log('='.repeat(60));
  console.log('\n✨ اكتملت العملية!\n');
}

uploadTranslationsOnly();
