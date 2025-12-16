# Smart Attendance System - Next.js Frontend Setup

## Prerequisites

تأكد أن Backend شغال أولاً!

```powershell
# في terminal منفصل
cd c:\Users\HP\smart-attendance-system
.\START.ps1
```

## Frontend Installation

### 1. Install Node.js
إذا لم يكن مثبت، حمّل من: https://nodejs.org/ (LTS version)

### 2. Install Dependencies
```powershell
cd c:\Users\HP\smart-attendance-system\frontend
npm install
```

هذا سيثبت:
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Chart.js
- Lucide React icons
- و المزيد...

### 3. Run Development Server
```powershell
npm run dev
```

سيفتح على: **http://localhost:3000**

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Login page
│   ├── globals.css        # Global styles
│   └── dashboard/         # Dashboard pages
│       ├── layout.tsx     # Dashboard layout
│       ├── page.tsx       # Overview
│       ├── students/      # Students management
│       ├── courses/       # Courses management
│       ├── attendance/    # Attendance records
│       ├── lectures/      # Lectures management
│       ├── bubble-sheets/ # Bubble sheets generator
│       ├── omr/           # OMR processing
│       └── reports/       # Reports & export
├── components/            # Reusable components
│   ├── ui/               # shadcn/ui components
│   ├── dashboard/        # Dashboard-specific
│   └── auth/             # Authentication
├── lib/                  # Utilities
│   ├── api.ts           # API client
│   ├── utils.ts         # Helper functions
│   └── types.ts         # TypeScript types
└── public/              # Static assets

## Features

✅ **Modern UI** - shadcn/ui components
✅ **TypeScript** - Type safety
✅ **Dark Mode** - next-themes
✅ **Charts** - Chart.js integration
✅ **Forms** - react-hook-form + zod validation
✅ **API Integration** - Connected to Flask backend
✅ **Responsive** - Mobile-first design

## API Configuration

Backend proxy configured in `next.config.js`:
```javascript
/api/* → http://localhost:5000/api/*
```

All API calls go through Next.js, which proxies to Flask backend.

## Development Commands

```powershell
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Backend Must Be Running!

⚠️ **Important:** Make sure Flask backend is running before starting frontend.

Check backend health:
```powershell
# في terminal منفصل
cd c:\Users\HP\smart-attendance-system
.\check-services.ps1
```

All 9 services should show ✓ Running.

## Login Credentials

```
Username: admin
Password: admin123
```

## Troubleshooting

### Port 3000 already in use
```powershell
# Kill process on port 3000
npx kill-port 3000

# Or use different port
PORT=3001 npm run dev
```

### Backend not responding
```powershell
# Restart backend
cd c:\Users\HP\smart-attendance-system
.\STOP.ps1
.\START.ps1
```

### npm install errors
```powershell
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

1. ✅ Start backend (if not already running)
2. ✅ Install dependencies: `npm install`
3. ✅ Start frontend: `npm run dev`
4. ✅ Open browser: http://localhost:3000
5. ✅ Login and explore!

---

**Ready to build! 🚀**
