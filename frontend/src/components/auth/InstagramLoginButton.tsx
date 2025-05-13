// src/components/auth/InstagramLoginButton.tsx
const INSTAGRAM_CLIENT_ID = '1248900693235950';
const REDIRECT_URI = 'http://localhost:8000/auth/instagram/callback';
const SCOPES = 'instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement';

const INSTAGRAM_AUTH_URL = `https://www.facebook.com/v19.0/dialog/oauth?client_id=${INSTAGRAM_CLIENT_ID}&redirect_uri=${encodeURIComponent(
  REDIRECT_URI
)}&scope=${SCOPES}&response_type=code`;

export const InstagramLoginButton = () => (
  <button
    onClick={() => window.location.href = INSTAGRAM_AUTH_URL}
    className="flex items-center justify-center gap-2 px-4 py-2 border rounded hover:bg-gray-50"
  >
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 24 24">
      <path fill="currentColor" d="M7.5 2h9A5.5 5.5 0 0122 7.5v9a5.5 5.5 0 01-5.5 5.5h-9A5.5 5.5 0 012 16.5v-9A5.5 5.5 0 017.5 2zm9 1.5h-9A4 4 0 003.5 7.5v9a4 4 0 004 4h9a4 4 0 004-4v-9a4 4 0 00-4-4zm-4.5 3A5.5 5.5 0 1017.5 12 5.5 5.5 0 0012 6.5zm0 9A3.5 3.5 0 1115.5 12 3.5 3.5 0 0112 15.5zm5.75-9.5a1.25 1.25 0 11-1.25-1.25A1.25 1.25 0 0117.75 6z"/>
    </svg>
    Login with Instagram
  </button>
);
