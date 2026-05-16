# Supabase email templates

Source of truth for the auth email content shown to TrainedGut users.
Supabase doesn't auto-sync templates from a repo — these files are tracked
in git so changes are reviewable, but **must be pasted manually** into the
Supabase dashboard to take effect.

## How to apply

1. Open Supabase dashboard → **Authentication** → **Email Templates**
2. Pick the template (mapping below)
3. Replace the **Subject** with the one from the file header
4. Replace the **Body (HTML)** with the file contents (everything below the
   `<!-- … -->` header comment)
5. Save

Changes take effect on the next email Supabase sends — no deploy needed.

## File ↔ Supabase template mapping

| File                          | Supabase template name      | When sent                                     |
|-------------------------------|------------------------------|-----------------------------------------------|
| `confirm-signup.html`         | Confirm signup               | New email/password signup (email verify)      |
| `reset-password.html`         | Reset Password               | "Forgot password" flow                        |
| _(not built)_ `magic-link.html`    | Magic Link                   | If magic-link auth ever enabled (we don't use it) |
| _(not built)_ `invite.html`        | Invite user                  | Admin invites a user                          |
| _(not built)_ `change-email.html`  | Change Email Address         | User changes their email                      |
| _(not built)_ `reauthentication.html` | Reauthentication          | Re-confirm sensitive action                   |

## Template variables

Supabase substitutes these at send time:

| Variable                  | What it is                                      |
|---------------------------|-------------------------------------------------|
| `{{ .ConfirmationURL }}`  | The action link (confirm / reset / etc.)        |
| `{{ .Email }}`            | The recipient's email                           |
| `{{ .SiteURL }}`          | The Site URL from `Authentication → URL Configuration` |
| `{{ .Token }}`            | The raw 6-digit OTP code (if you want to show it) |

## Design conventions

- **Single column, max 560px wide** for mobile readability
- **Cream background (`#F5F0E8`), white card, dark text (`#1A1A14`)** — matches the landing page
- **Orange accent (`#E8521A`)** on the top border and CTA button — brand colour
- **System fonts only** (`-apple-system, BlinkMacSystemFont, …`) — email clients strip web fonts unreliably; Bebas Neue won't render in most inboxes
- **Inline styles only** — Gmail and Outlook strip `<style>` blocks
- **Table-based layout** — required for Outlook compatibility
- **No images** — keeps the email lightweight and avoids broken-image placeholders if Supabase's CDN ever moves

## Adding a new template later

1. Copy `confirm-signup.html` as a starting point
2. Update the header comment (Subject + Supabase template name)
3. Rewrite the headline + body for the new flow
4. Update the table above

## Custom SMTP note

By default Supabase sends from `noreply@mail.app.supabase.io`. To send from
`join@trainedgut.com`:

Supabase dashboard → **Authentication** → **SMTP Settings** → enable custom SMTP,
plug in WebSupport's SMTP credentials (or Resend, Postmark, etc.). Once enabled,
all templates above are sent from your domain instead of Supabase's.
