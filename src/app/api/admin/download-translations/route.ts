
import { NextResponse } from 'next/server';
import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import archiver from 'archiver';
import { Readable } from 'stream';

export async function GET() {
  try {
    const localesPath = join(process.cwd(), 'public', 'locales');
    const languages = ['ar', 'en'];
    
    const archive = archiver('zip', {
      zlib: { level: 9 }
    });

    const chunks: Uint8Array[] = [];
    
    archive.on('data', (chunk) => {
      chunks.push(chunk);
    });

    const archivePromise = new Promise<Buffer>((resolve, reject) => {
      archive.on('end', () => {
        resolve(Buffer.concat(chunks));
      });
      archive.on('error', reject);
    });

    for (const lang of languages) {
      const langPath = join(localesPath, lang);
      
      try {
        const files = await readdir(langPath);
        
        for (const file of files) {
          if (file.endsWith('.json')) {
            const filePath = join(langPath, file);
            const content = await readFile(filePath);
            archive.append(content, { name: `${lang}/${file}` });
          }
        }
      } catch (error) {
        console.error(`Error reading ${lang} directory:`, error);
      }
    }

    await archive.finalize();
    const buffer = await archivePromise;

    return new NextResponse(buffer, {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="translations-${Date.now()}.zip"`
      }
    });

  } catch (error: any) {
    console.error('Download error:', error);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
