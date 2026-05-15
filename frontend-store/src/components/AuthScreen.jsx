import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { supabase } from '../supabase'

export default function AuthScreen() {
  return (
    <div className="auth-shell">
      <header className="auth-header">
        <span className="store-logo">Trained<span>Gut</span></span>
      </header>

      <main className="auth-main">
        <div className="auth-card">
          <h1 className="auth-title">Sign in</h1>
          <p className="auth-subtitle">
            Log in to access your gut training plan and log session feedback.
          </p>

          <Auth
            supabaseClient={supabase}
            providers={['google']}
            redirectTo={window.location.origin}
            appearance={{
              theme: ThemeSupa,
              variables: {
                default: {
                  colors: {
                    brand: '#da5222',
                    brandAccent: '#c9431a',
                    brandButtonText: '#ffffff',
                    inputBackground: '#1a1a14',
                    inputBorder: 'rgba(255,255,255,0.12)',
                    inputBorderHover: 'rgba(255,255,255,0.3)',
                    inputBorderFocus: '#da5222',
                    inputText: '#ffffff',
                    inputLabelText: 'rgba(255,255,255,0.5)',
                    inputPlaceholder: 'rgba(255,255,255,0.25)',
                    messageText: 'rgba(255,255,255,0.7)',
                    anchorTextColor: 'rgba(255,255,255,0.5)',
                    anchorTextHoverColor: '#da5222',
                  },
                  fonts: {
                    bodyFontFamily: "'DM Sans', sans-serif",
                    buttonFontFamily: "'DM Sans', sans-serif",
                    inputFontFamily: "'DM Sans', sans-serif",
                    labelFontFamily: "'DM Sans', sans-serif",
                  },
                },
              },
            }}
            theme="dark"
          />
        </div>
      </main>
    </div>
  )
}
