# Python Era Frontend

Next.js frontend for Python Era learning platform.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Deployment on Vercel

1. Connect your GitHub repository to Vercel
2. Set environment variable:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL (Render)
3. Deploy automatically on push to main branch

## Build

```bash
npm run build
npm start
```

