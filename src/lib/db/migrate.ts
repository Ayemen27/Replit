import fs from 'fs';
import path from 'path';
import pool from './postgres';

/**
 * تطبيق Schema على قاعدة البيانات
 */
export async function migrate() {
  try {
    console.log('🔄 Starting database migration...');
    
    // قراءة ملف Schema
    const schemaPath = path.join(process.cwd(), 'src/lib/db/schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf-8');
    
    // تطبيق Schema
    await pool.query(schema);
    
    console.log('✅ Database migration completed successfully!');
    return true;
  } catch (error) {
    console.error('❌ Database migration failed:', error);
    throw error;
  }
}

/**
 * التحقق من حالة قاعدة البيانات
 */
export async function checkDatabase() {
  try {
    const result = await pool.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `);
    
    console.log('📊 Database tables:', result.rows.map((r: any) => r.table_name));
    return result.rows;
  } catch (error) {
    console.error('❌ Database check failed:', error);
    throw error;
  }
}

// تنفيذ Migration إذا تم استدعاء الملف مباشرة
if (require.main === module) {
  migrate()
    .then(() => checkDatabase())
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}
