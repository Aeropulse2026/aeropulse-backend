# Next.js cookie authentication

Copy `middleware.ts` to the root of the Next.js project and `api-client.ts` to `lib/api-client.ts`.

Install the verifier:

```bash
npm install jose
```

Set these values in the Next.js `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
JWT_SIGNING_KEY=the-same-value-as-the-Django-JWT_SIGNING_KEY
```

`JWT_SIGNING_KEY` is server-only. Never name it `NEXT_PUBLIC_JWT_SIGNING_KEY`.

The browser sends the `aeropulse_access` and `aeropulse_refresh` HttpOnly cookies automatically when `credentials: "include"` is set. Browser JavaScript never reads the refresh token. The middleware validates the short-lived access JWT before allowing protected page routes; Django still validates every protected API request.
