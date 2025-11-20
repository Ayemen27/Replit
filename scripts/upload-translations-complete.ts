#!/usr/bin/env tsx

import * as fs from 'fs';
import * as path from 'path';
import FormData from 'form-data';

const apiUrl = process.env.NEXT_PUBLIC_TOLGEE_API_URL || process.env.TOLGEE_API_URL;
const apiKey = process.env.NEXT_PUBLIC_TOLGEE_API_KEY || process.env.TOLGEE_API_KEY;
const projectId = process.env.NEXT_PUBLIC_TOLGEE_PROJECT_ID || process.env.TOLGEE_PROJECT_ID;

async function deleteExistingImport() {
  console.log('🗑️  حذف أي Import سابق...\n');
  try {
    const response = await fetch(`${apiUrl}/v2/projects/${projectId}/import`, {
      method: 'DELETE',
      headers: { 'X-API-Key': apiKey! },
    });
    if (response.ok) {
      console.log('   ✅ تم حذف Import السابق\n');
    }
  } catch (error) {
    console.log('   ℹ️  لا يوجد Import سابق\n');
  }
}

async function uploadAllFiles() {
  console.log('📤 رفع جميع ملفات الترجمة...\n');

  const localesPath = path.join(process.cwd(), 'public', 'locales');
  const languages = [
    { code: 'ar', name: 'Arabic' },
    { code: 'en', name: 'English' },
  ];

  const formData = new FormData();
  const fileMapping: Array<{ lang: string; file: string; index: number }> = [];
  let fileIndex = 0;

  for (const lang of languages) {
    const langPath = path.join(localesPath, lang.code);
    
    if (fs.existsSync(langPath)) {
      const files = fs.readdirSync(langPath).filter(f => f.endsWith('.json'));
      
      for (const file of files) {
        const filePath = path.join(langPath, file);
        const fileStream = fs.createReadStream(filePath);
        formData.append('files', fileStream, `${lang.code}/${file}`);
        
        fileMapping.push({
          lang: lang.code,
          file: file,
          index: fileIndex++,
        });
        
        console.log(`   📄 ${lang.code}/${file}`);
      }
    }
  }

  console.log(`\n   📊 إجمالي: ${fileIndex} ملف\n`);

  const response = await fetch(`${apiUrl}/v2/projects/${projectId}/import`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey!,
      ...formData.getHeaders(),
    },
    body: formData as any,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`فشل رفع الملفات: ${response.status} - ${errorText}`);
  }

  console.log('   ✅ تم رفع الملفات بنجاح\n');
  return fileMapping;
}

async function getImportResult() {
  const response = await fetch(`${apiUrl}/v2/projects/${projectId}/import/result`, {
    method: 'GET',
    headers: { 'X-API-Key': apiKey! },
  });

  if (!response.ok) {
    throw new Error(`فشل جلب Import Result: ${response.status}`);
  }

  return await response.json();
}

async function getExistingLanguages() {
  const response = await fetch(`${apiUrl}/v2/projects/${projectId}/languages`, {
    method: 'GET',
    headers: { 'X-API-Key': apiKey! },
  });

  if (!response.ok) {
    throw new Error(`فشل جلب اللغات: ${response.status}`);
  }

  return await response.json();
}

async function selectExistingLanguage(importLangId: number, existingLangId: number) {
  try {
    const response = await fetch(
      `${apiUrl}/v2/projects/${projectId}/import/result/languages/${importLangId}/select-existing/${existingLangId}`,
      {
        method: 'PUT',
        headers: { 'X-API-Key': apiKey! },
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`      ❌ Error selecting language: ${response.status} - ${errorText}`);
      return false;
    }

    return true;
  } catch (error) {
    console.error(`      ❌ Exception selecting language: ${error}`);
    return false;
  }
}

async function applyImport() {
  const response = await fetch(`${apiUrl}/v2/projects/${projectId}/import/apply`, {
    method: 'PUT',
    headers: { 'X-API-Key': apiKey! },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`فشل تطبيق Import: ${response.status} - ${errorText}`);
  }

  return response.ok;
}

async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 رفع الترجمات إلى Tolgee - السكريبت الكامل');
  console.log('='.repeat(60));
  console.log();

  if (!apiUrl || !apiKey || !projectId) {
    console.error('❌ متغيرات البيئة غير موجودة');
    process.exit(1);
  }

  console.log('📋 معلومات الاتصال:');
  console.log(`  - API URL: ${apiUrl}`);
  console.log(`  - Project ID: ${projectId}`);
  console.log('='.repeat(60));
  console.log();

  try {
    await deleteExistingImport();

    const fileMapping = await uploadAllFiles();

    console.log('📥 جلب بيانات Import...\n');
    const importResult = await getImportResult();
    const existingLanguages = await getExistingLanguages();

    const importLangs = importResult._embedded?.languages || [];
    const existingLangs = existingLanguages._embedded?.languages || [];

    console.log(`   ℹ️  Import Languages: ${importLangs.length}`);
    console.log(`   ℹ️  Existing Languages: ${existingLangs.length}`);
    
    // Log existing languages for debugging
    existingLangs.forEach(lang => {
      console.log(`   📌 Existing: ${lang.name} (${lang.tag}) - ID: ${lang.id}`);
    });
    console.log();

    console.log('🔗 ربط اللغات...\n');

    // Create language map from existing languages
    const langMap: { [key: string]: number } = {};
    for (const lang of existingLangs) {
      langMap[lang.tag] = lang.id;
      console.log(`   📍 Language Map: ${lang.tag} → ${lang.id}`);
    }
    console.log();

    // Track which import languages we've already processed
    const processedImportIds = new Set<number>();

    for (const importLang of importLangs) {
      // Skip if we've already processed this import language
      if (processedImportIds.has(importLang.id)) {
        continue;
      }

      const fileName = importLang.importFileName || '';
      let langCode = 'en'; // default

      // Determine language from filename
      if (fileName.includes('/ar/') || fileName.startsWith('ar-') || fileName.includes('ar/')) {
        langCode = 'ar';
      } else if (fileName.includes('/en/') || fileName.startsWith('en-') || fileName.includes('en/')) {
        langCode = 'en';
      } else {
        // Try to match with file mapping
        const fileMatch = fileMapping.find(f => fileName.includes(f.file));
        if (fileMatch) {
          langCode = fileMatch.lang;
        }
      }

      const existingLangId = langMap[langCode];

      if (existingLangId) {
        console.log(`   🔗 ${fileName} → ${langCode} (Import ID: ${importLang.id}, Existing ID: ${existingLangId})`);
        const success = await selectExistingLanguage(importLang.id, existingLangId);
        
        if (success) {
          processedImportIds.add(importLang.id);
        } else {
          console.error(`   ❌ فشل ربط ${fileName}`);
        }
      } else {
        console.error(`   ⚠️  لم يتم العثور على لغة موجودة: ${langCode} للملف ${fileName}`);
      }
    }

    console.log('\n✅ تم ربط جميع اللغات\n');

    console.log('='.repeat(60));
    console.log('📤 تطبيق Import...\n');

    const applied = await applyImport();

    if (applied) {
      console.log('='.repeat(60));
      console.log('🎉 النتيجة النهائية');
      console.log('='.repeat(60));
      console.log('✅ تم رفع وتطبيق جميع الترجمات بنجاح!');
      console.log('📊 عدد الملفات المرفوعة:', fileMapping.length);
      console.log('📊 عدد اللغات:', existingLangs.length);
      console.log('='.repeat(60));
      console.log('\n✨ اكتملت العملية بنجاح!\n');
    }

  } catch (error) {
    console.error('\n❌ حدث خطأ:', error);
    process.exit(1);
  }
}

main();
