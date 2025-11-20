#!/usr/bin/env node
/**
 * سكريبت لبدء Next.js مع قراءة PORT من .env.local
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '..', '.env.local');

let port = '5000';

if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  const portMatch = envContent.match(/^PORT=(.+)$/m);
  if (portMatch) {
    port = portMatch[1].trim();
  }
}

console.log(`🚀 بدء Next.js على البورت: ${port}`);

process.env.PORT = port;

try {
  execSync('next dev -H 0.0.0.0', {
    stdio: 'inherit',
    env: { ...process.env, PORT: port }
  });
} catch (error) {
  process.exit(1);
}
