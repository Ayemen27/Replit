import admin from "firebase-admin";

let isInitialized = false;
let initializationError: Error | null = null;

function validateCredentials() {
  const projectId = process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_ADMIN_CLIENT_EMAIL;
  const privateKey = process.env.FIREBASE_ADMIN_PRIVATE_KEY;

  const missing: string[] = [];

  if (!projectId) {
    missing.push('NEXT_PUBLIC_FIREBASE_PROJECT_ID');
  }
  if (!clientEmail) {
    missing.push('FIREBASE_ADMIN_CLIENT_EMAIL');
  }
  if (!privateKey) {
    missing.push('FIREBASE_ADMIN_PRIVATE_KEY');
  }

  if (missing.length > 0) {
    const errorMessage = `Firebase Admin SDK: Missing required environment variables: ${missing.join(', ')}. Please check your Replit Secrets or .env file.`;
    console.error('❌ ' + errorMessage);
    throw new Error(errorMessage);
  }

  return {
    projectId: projectId!,
    clientEmail: clientEmail!,
    privateKey: privateKey!.replace(/\\n/g, '\n'),
  };
}

function tryParseJSONCredentials(): admin.ServiceAccount | null {
  const credentialsJSON = process.env.FIREBASE_ADMIN_CREDENTIALS_JSON;
  
  if (!credentialsJSON) {
    return null;
  }

  try {
    const parsed = JSON.parse(credentialsJSON);
    console.log('✅ Firebase Admin SDK: Using JSON credentials payload');
    return parsed as admin.ServiceAccount;
  } catch (error) {
    console.error('❌ Firebase Admin SDK: Failed to parse FIREBASE_ADMIN_CREDENTIALS_JSON:', error);
    return null;
  }
}

function initializeFirebaseAdmin() {
  if (isInitialized) {
    console.log('ℹ️ Firebase Admin SDK: Already initialized, skipping...');
    return;
  }

  if (admin.apps.length > 0) {
    console.log('✅ Firebase Admin SDK: Already initialized (existing app found)');
    isInitialized = true;
    return;
  }

  try {
    const jsonCredentials = tryParseJSONCredentials();
    
    if (jsonCredentials) {
      admin.initializeApp({
        credential: admin.credential.cert(jsonCredentials),
        databaseURL: `https://${jsonCredentials.projectId}.firebaseio.com`,
      });
      console.log(`✅ Firebase Admin SDK: Initialized successfully for project: ${jsonCredentials.projectId}`);
    } else {
      const credentials = validateCredentials();
      
      admin.initializeApp({
        credential: admin.credential.cert({
          projectId: credentials.projectId,
          clientEmail: credentials.clientEmail,
          privateKey: credentials.privateKey,
        }),
        databaseURL: `https://${credentials.projectId}.firebaseio.com`,
      });
      console.log(`✅ Firebase Admin SDK: Initialized successfully for project: ${credentials.projectId}`);
    }

    isInitialized = true;
  } catch (error) {
    initializationError = error as Error;
    console.error('❌ Firebase Admin SDK: Initialization failed:', error);
    throw error;
  }
}

try {
  initializeFirebaseAdmin();
} catch (error) {
  console.error('⚠️ Firebase Admin SDK: Will not be available. Admin-dependent routes will fail.');
}

export function isAdminInitialized(): boolean {
  return isInitialized;
}

export function getInitializationError(): Error | null {
  return initializationError;
}

export const adminAuth = isInitialized ? admin.auth() : null;
export const firestore = isInitialized ? admin.firestore() : null;
