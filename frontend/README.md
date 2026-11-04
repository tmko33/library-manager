# Biblioteca — frontend

React + TypeScript SPA for the [Library Manager API](../README.md).

## Features

- Catalogue search, book detail & availability.
- Authentication with redirect-back and demo accounts.
- Borrow, renew, return and reserve from the UI.
- Account page with profile and fines.
- **Staff panel** (librarian/admin): books, authors, publishers, branches,
  copies, members, loans and fines.
- Typed API client with JWT and RFC 7807 error handling.
- Query invalidation after mutations keeps availability in sync.

## Stack

- **React 19** + **Vite**
- **TypeScript**
- **TanStack Query** for server state (cache, invalidation, retries)
- **React Router** for routing
- **Tailwind CSS v4**
- Native `fetch` wrapped in `src/api/client.ts` (no Axios)

## Structure

```text
src/
├── api/          client (fetch + JWT), endpoints, types
├── auth/         AuthProvider, context, useAuth
├── components/   layout, form controls, badges, pagination
├── lib/          formatting and error helpers
├── pages/        catalogue, book detail, loans, reservations, account
│   └── staff/    books, authors, publishers, branches, copies, members, loans, fines
├── App.tsx       routes
└── main.tsx      providers
```

Data flow: a page calls `useQuery`/`useMutation` → `src/api/endpoints.ts` →
`src/api/client.ts` → the API. Mutations invalidate the affected query keys so
the UI refreshes automatically.

## Local development

The API must be running on `http://localhost:8000`:

```bash
# from the repository root
uvicorn app.main:app --reload

# from frontend/
npm install
npm run dev
```

Vite proxies `/api` to `http://localhost:8000`, so there is no CORS setup in
development. To point the proxy at another backend:

```bash
VITE_PROXY_TARGET=https://library-manager-api-ueba.onrender.com npm run dev
```

To call the API directly (no proxy), create `.env.local`:

```bash
VITE_API_URL=https://library-manager-api-ueba.onrender.com
```

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Development server with HMR |
| `npm run build` | Type-check and build to `dist/` |
| `npm run preview` | Serve the production build |
| `npm run lint` | Oxlint |

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Member | `member@library.dev` | `library12345` |
| Librarian | `librarian@library.dev` | `library12345` |
| Admin | `admin@library.dev` | `library12345` |

## Deployment

`render.yaml` defines a static site that builds this folder and rewrites every
route to `index.html`. Set `VITE_API_URL` to the public API URL at build time.
