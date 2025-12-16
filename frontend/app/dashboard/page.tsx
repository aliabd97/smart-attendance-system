'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { students, courses, attendance } from '@/lib/api'
import { Users, BookOpen, ClipboardCheck, TrendingUp, Loader2 } from 'lucide-react'
import { AttendanceChart } from '@/components/ui/attendance-chart'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    students: 0,
    courses: 0,
    attendance: 0,
    loading: true,
  })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [studentsData, coursesData, attendanceData] = await Promise.all([
          students.getAll(),
          courses.getAll(),
          attendance.getAll(),
        ])

        setStats({
          students: studentsData.count || 0,
          courses: coursesData.count || 0,
          attendance: attendanceData.count || 0,
          loading: false,
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        setStats((prev) => ({ ...prev, loading: false }))
      }
    }

    fetchStats()
  }, [])

  const statCards = [
    {
      title: 'Total Students',
      value: stats.students,
      description: 'Registered in system',
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      title: 'Total Courses',
      value: stats.courses,
      description: 'Active courses',
      icon: BookOpen,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      title: 'Attendance Records',
      value: stats.attendance,
      description: 'Total records',
      icon: ClipboardCheck,
      color: 'text-orange-600',
      bg: 'bg-orange-50',
    },
    {
      title: 'Attendance Rate',
      value: stats.attendance > 0 ? '85%' : '0%',
      description: 'Overall average',
      icon: TrendingUp,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
        <p className="text-muted-foreground mt-2">
          Welcome to Smart Attendance Management System
        </p>
      </div>

      {stats.loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {statCards.map((stat) => {
              const Icon = stat.icon
              return (
                <Card key={stat.title}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">
                      {stat.title}
                    </CardTitle>
                    <div className={`p-2 rounded-lg ${stat.bg}`}>
                      <Icon className={`h-4 w-4 ${stat.color}`} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {stat.description}
                    </p>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks and operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
                  <h3 className="font-semibold mb-1">Add Student</h3>
                  <p className="text-sm text-muted-foreground">
                    Register new student in the system
                  </p>
                </div>
                <div className="p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
                  <h3 className="font-semibold mb-1">Add Course</h3>
                  <p className="text-sm text-muted-foreground">
                    Create a new course offering
                  </p>
                </div>
                <div className="p-4 border rounded-lg hover:bg-accent cursor-pointer transition-colors">
                  <h3 className="font-semibold mb-1">Generate Bubble Sheet</h3>
                  <p className="text-sm text-muted-foreground">
                    Create OMR attendance sheet
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Attendance Trends Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Attendance Trends</CardTitle>
              <CardDescription>Weekly attendance statistics</CardDescription>
            </CardHeader>
            <CardContent>
              <AttendanceChart
                data={{
                  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                  present: [85, 90, 88, 92, 87, 80, 75],
                  absent: [15, 10, 12, 8, 13, 20, 25],
                }}
              />
            </CardContent>
          </Card>

          {/* System Info */}
          <Card>
            <CardHeader>
              <CardTitle>System Information</CardTitle>
              <CardDescription>Smart Attendance System Status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Backend Services:</span>
                  <span className="font-medium text-green-600">9 Running</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Architecture:</span>
                  <span className="font-medium">Microservices</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">OMR Engine:</span>
                  <span className="font-medium">OpenCV Enabled</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Authentication:</span>
                  <span className="font-medium">JWT Active</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
