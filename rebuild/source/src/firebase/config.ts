import { initializeApp, getApps, getApp, FirebaseApp } from "firebase/app";
import { getAuth, Auth } from "firebase/auth";
import { getFirestore, Firestore } from "firebase/firestore";

const firebaseConfig = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
    measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

let app: FirebaseApp | undefined;
let auth: Auth | undefined;
let db: Firestore | undefined;

function getFirebaseApp() {
    if (typeof window === 'undefined') {
        return undefined;
    }
    
    if (!app) {
        app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
    }
    return app;
}

function getFirebaseAuth() {
    if (typeof window === 'undefined') {
        return undefined;
    }
    
    const firebaseApp = getFirebaseApp();
    if (!firebaseApp) {
        return undefined;
    }
    
    if (!auth) {
        auth = getAuth(firebaseApp);
    }
    return auth;
}

function getFirebaseDb() {
    if (typeof window === 'undefined') {
        return undefined;
    }
    
    const firebaseApp = getFirebaseApp();
    if (!firebaseApp) {
        return undefined;
    }
    
    if (!db) {
        db = getFirestore(firebaseApp);
    }
    return db;
}

export { getFirebaseAuth as auth, getFirebaseDb as db };