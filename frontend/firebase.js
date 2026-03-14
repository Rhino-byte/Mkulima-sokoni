// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDEX2PIAw5ZhSp84OiZgRK35WfGhTeT-0E",
  authDomain: "agriculture-43eaf.firebaseapp.com",
  projectId: "agriculture-43eaf",
  storageBucket: "agriculture-43eaf.firebasestorage.app",
  messagingSenderId: "340310533875",
  appId: "1:340310533875:web:54c8b2d5e28bf32d437986",
  measurementId: "G-9W1C0JWRYN"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);