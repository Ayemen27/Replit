import { NextRequest, NextResponse } from 'next/server';
import bcrypt from 'bcrypt';
import { query } from '@/lib/db/postgres';

export async function POST(req: NextRequest) {
  try {
    const { name, email, password } = await req.json();
    
    // Validation
    if (!name || !email || !password) {
      return NextResponse.json(
        { message: 'جميع الحقول مطلوبة' },
        { status: 400 }
      );
    }
    
    if (password.length < 8) {
      return NextResponse.json(
        { message: 'كلمة المرور يجب أن تكون 8 أحرف على الأقل' },
        { status: 400 }
      );
    }
    
    // Check if user exists
    const existing = await query(
      'SELECT id FROM users WHERE email = $1',
      [email]
    );
    
    if (existing.length > 0) {
      return NextResponse.json(
        { message: 'البريد الإلكتروني مستخدم بالفعل' },
        { status: 409 }
      );
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Create user
    const result = await query(
      `INSERT INTO users (name, email, password)
       VALUES ($1, $2, $3)
       RETURNING id, name, email`,
      [name, email, hashedPassword]
    );
    
    return NextResponse.json(
      { 
        message: 'تم إنشاء الحساب بنجاح',
        user: result[0]
      },
      { status: 201 }
    );
    
  } catch (error) {
    console.error('Signup error:', error);
    return NextResponse.json(
      { message: 'حدث خطأ في الخادم' },
      { status: 500 }
    );
  }
}
