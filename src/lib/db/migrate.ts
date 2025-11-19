import fs from 'fs';
import path from 'path';
import pool from './postgres';

/**
 * تطبيق Schema على قاعدة البيانات
 * ملاحظة: إذا واجهت مشكلة "multiple statements"، يمكن تطبيق schema.sql مباشرة عبر psql:
 * psql $DATABASE_URL -f src/lib/db/schema.sql
 */
export async function migrate() {
  const client = await pool.connect();
  try {
    console.log('🔄 Starting database migration...');
    
    // قراءة ملف Schema
    const schemaPath = path.join(process.cwd(), 'src/lib/db/schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf-8');
    
    console.log('📝 Executing schema.sql (without transaction to allow CREATE EXTENSION)...');
    // Note: CREATE EXTENSION cannot run inside a transaction block
    await client.query(schema);
    
    console.log('✅ Database migration completed successfully!');
    return true;
  } catch (error: any) {
    console.error('❌ Database migration failed:', error.message);
    console.error('💡 Alternative: Run manually with: psql $DATABASE_URL -f src/lib/db/schema.sql');
    throw error;
  } finally {
    client.release();
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
