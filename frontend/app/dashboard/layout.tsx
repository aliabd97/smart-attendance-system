'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { auth } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  GraduationCap,
  LayoutDashboard,
  Users,
  BookOpen,
  ClipboardCheck,
  Calendar,
  FileText,
  Camera,
  BarChart3,
  LogOut,
  Server,
  UserPlus,
} from 'lucide-react'

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Students', href: '/dashboard/students', icon: Users },
  { name: 'Courses', href: '/dashboard/courses', icon: BookOpen },
  { name: 'Enrollments', href: '/dashboard/enrollments', icon: UserPlus },
  { name: 'Lectures', href: '/dashboard/lectures', icon: Calendar },
  { name: 'Attendance', href: '/dashboard/attendance', icon: ClipboardCheck },
  { name: 'Bubble Sheets', href: '/dashboard/bubble-sheets', icon: FileText },
  { name: 'OMR Processing', href: '/dashboard/omr', icon: Camera },
  { name: 'Reports', href: '/dashboard/reports', icon: BarChart3 },
  { name: 'System Status', href: '/dashboard/system', icon: Server },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const token = auth.getToken()
    const currentUser = auth.getCurrentUser()

    if (!token || !currentUser) {
      router.push('/')
      return
    }

    setUser(currentUser)
  }, [router])

  const handleLogout = () => {
    auth.logout()
    router.push('/')
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <GraduationCap className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="font-bold text-lg">Smart Attendance</h2>
              <p className="text-xs text-muted-foreground">OMR System</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <Icon className="w-4 h-4" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* User & Logout */}
        <div className="p-4 border-t">
          <div className="mb-2 px-3 py-2 text-sm">
            <p className="font-medium">{user.username}</p>
            <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start gap-3"
            onClick={handleLogout}
          >
            <LogOut className="w-4 h-4" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}
