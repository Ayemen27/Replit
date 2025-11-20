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

// إنشاء مفتاح في Tolgee (بدون namespace لأنه معطّل في المشروع)
async function createKey(keyName: string): Promise<boolean> {
  try {
    const response = await fetch(`${apiUrl}/v2/projects/${projectId}/keys`, {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: keyName,
      }),
    });

    if (response.ok) {
      return true;
    } else if (response.status === 409) {
      // Key already exists
      console.log(`   ⚠️  المفتاح موجود بالفعل: ${keyName}`);
      return true;
    } else {
      const error = await response.text();
      console.error(`   ❌ فشل إنشاء المفتاح ${keyName}: ${response.status} - ${error.substring(0, 100)}`);
      return false;
    }
  } catch (error) {
    console.error(`   ❌ خطأ في إنشاء المفتاح ${keyName}:`, error);
    return false;
  }
}

// رفع الترجمات لمفتاح معين (الطريقة الصحيحة)
async function uploadTranslation(keyName: string, languageTag: string, translation: string): Promise<boolean> {
  try {
    const response = await fetch(`${apiUrl}/v2/projects/${projectId}/translations`, {
      method: 'POST',
      headers: {
        'X-API-Key': apiKey!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        keyName: keyName,
        languageTag: languageTag,
        text: translation,
      }),
    });

    if (response.ok || response.status === 200) {
      return true;
    } else {
      const error = await response.text();
      console.error(`   ❌ فشل رفع الترجمة ${keyName} (${languageTag}): ${response.status} - ${error.substring(0, 100)}`);
      return false;
    }
  } catch (error) {
    console.error(`   ❌ خطأ في رفع الترجمة ${keyName} (${languageTag}):`, error);
    return false;
  }
}

// رفع الترجمات باستخدام batch endpoint
async function uploadTranslationsBatch(translations: any[]): Promise<boolean> {
  try {
    const response = await fetch(`${apiUrl}/v2/projects/${projectId}/translations`, {
      method: 'PUT',
      headers: {
        'X-API-Key': apiKey!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ translations }),
    });

    if (response.ok || response.status === 200) {
      return true;
    } else {
      const error = await response.text();
      console.error(`   ❌ فشل رفع الترجمات: ${response.status} - ${error.substring(0, 200)}`);
      return false;
    }
  } catch (error) {
    console.error(`   ❌ خطأ في رفع الترجمات:`, error);
    return false;
  }
}

async function uploadKeysToTolgee() {
  console.log('\n🚀 بدء رفع المفاتيح إلى Tolgee...\n');

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
  const keyNamespaces = new Map<string, string>();

  for (const lang of languages) {
    for (const namespace in allTranslations[lang]) {
      for (const key in allTranslations[lang][namespace]) {
        const fullKey = `${namespace}.${key}`;
        allKeys.add(fullKey);
        keyNamespaces.set(fullKey, namespace);
      }
    }
  }

  console.log(`📊 إحصائيات:`);
  console.log(`  - عدد اللغات: ${languages.length}`);
  console.log(`  - عدد المفاتيح الفريدة: ${allKeys.size}`);
  console.log();

  let createdCount = 0;
  let failedCount = 0;
  let uploadedCount = 0;

  console.log('🔑 1. إنشاء المفاتيح في Tolgee...\n');

  // إنشاء جميع المفاتيح أولاً (بدون namespace)
  for (const fullKey of allKeys) {
    const keyName = fullKey;
    
    console.log(`   📝 إنشاء: ${keyName}`);
    const success = await createKey(keyName);
    
    if (success) {
      createdCount++;
    } else {
      failedCount++;
    }
    
    // تأخير صغير لتجنب rate limiting
    await new Promise(resolve => setTimeout(resolve, 50));
  }

  console.log(`\n✅ تم إنشاء ${createdCount} مفتاح`);
  if (failedCount > 0) {
    console.log(`⚠️  فشل ${failedCount} مفتاح`);
  }

  console.log('\n📤 2. رفع الترجمات...\n');

  // رفع الترجمات لكل مفتاح
  for (const fullKey of allKeys) {
    const [namespace, ...keyParts] = fullKey.split('.');
    const key = keyParts.join('.');
    
    console.log(`   🌐 ${fullKey}:`);
    
    for (const lang of languages) {
      if (allTranslations[lang][namespace] && allTranslations[lang][namespace][key]) {
        const translation = allTranslations[lang][namespace][key];
        const success = await uploadTranslation(fullKey, lang, translation);
        
        if (success) {
          console.log(`      ✅ ${lang}: "${translation.substring(0, 50)}${translation.length > 50 ? '...' : ''}"`);
          uploadedCount++;
        } else {
          failedCount++;
        }
        
        // تأخير صغير
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('📊 النتائج النهائية:');
  console.log('='.repeat(60));
  console.log(`✅ المفاتيح المنشأة: ${createdCount}`);
  console.log(`✅ الترجمات المرفوعة: ${uploadedCount}`);
  if (failedCount > 0) {
    console.log(`❌ الفشل: ${failedCount}`);
  }
  console.log('='.repeat(60));
  console.log('\n✨ اكتملت العملية!\n');
}

uploadKeysToTolgee();
