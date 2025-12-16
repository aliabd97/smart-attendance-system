'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Server, RefreshCw, CheckCircle, XCircle, Loader2 } from 'lucide-react'

interface ServiceStatus {
  name: string
  url: string
  port: number
  status: 'running' | 'down' | 'checking'
}

export default function SystemPage() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'API Gateway', url: 'http://localhost:5000/health', port: 5000, status: 'checking' },
    { name: 'Student Service', url: 'http://localhost:5001', port: 5001, status: 'checking' },
    { name: 'Course Service', url: 'http://localhost:5002', port: 5002, status: 'checking' },
    { name: 'Bubble Sheet Generator', url: 'http://localhost:5003', port: 5003, status: 'checking' },
    { name: 'PDF Processing', url: 'http://localhost:5004', port: 5004, status: 'checking' },
    { name: 'Attendance Service', url: 'http://localhost:5005', port: 5005, status: 'checking' },
    { name: 'Auth Service', url: 'http://localhost:5007', port: 5007, status: 'checking' },
    { name: 'Service Registry', url: 'http://localhost:5008', port: 5008, status: 'checking' },
    { name: 'Reporting Service', url: 'http://localhost:5009', port: 5009, status: 'checking' },
  ])
  const [checking, setChecking] = useState(false)

  const checkServices = async () => {
    setChecking(true)
    const updatedServices = await Promise.all(
      services.map(async (service) => {
        try {
          const controller = new AbortController()
          const timeoutId = setTimeout(() => controller.abort(), 3000) // 3 second timeout

          const response = await fetch(service.url, {
            method: 'GET',
            signal: controller.signal,
          })

          clearTimeout(timeoutId)

          if (response.ok) {
            return { ...service, status: 'running' as const }
          } else {
            return { ...service, status: 'down' as const }
          }
        } catch (error) {
          return { ...service, status: 'down' as const }
        }
      })
    )
    setServices(updatedServices)
    setChecking(false)
  }

  useEffect(() => {
    checkServices()
  }, [])

  const runningCount = services.filter((s) => s.status === 'running').length
  const downCount = services.filter((s) => s.status === 'down').length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">System Status</h1>
          <p className="text-muted-foreground mt-1">Monitor all microservices health</p>
        </div>
        <Button onClick={checkServices} disabled={checking}>
          <RefreshCw className={`w-4 h-4 mr-2 ${checking ? 'animate-spin' : ''}`} />
          Check Services
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Services
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{services.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Microservices</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Running
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{runningCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Services online</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Down</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">{downCount}</div>
            <p className="text-xs text-muted-foreground mt-1">Services offline</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Services Health</CardTitle>
          <CardDescription>Real-time status of all microservices</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {services.map((service) => (
              <div
                key={service.port}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  {service.status === 'checking' ? (
                    <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                  ) : service.status === 'running' ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                  <div>
                    <p className="font-medium">{service.name}</p>
                    <p className="text-sm text-muted-foreground">
                      Port {service.port} • {service.url}
                    </p>
                  </div>
                </div>
                <div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      service.status === 'running'
                        ? 'bg-green-100 text-green-800'
                        : service.status === 'down'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {service.status === 'running'
                      ? 'Running'
                      : service.status === 'down'
                      ? 'Down'
                      : 'Checking...'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Architecture Overview</CardTitle>
          <CardDescription>System architecture and patterns</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h3 className="font-semibold">Microservices Architecture</h3>
              <p className="text-sm text-muted-foreground">
                9 independent services communicating via HTTP
              </p>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">Design Patterns</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Circuit Breaker</li>
                <li>• Breaking Foreign Keys</li>
                <li>• Adapter Pattern</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">Technologies</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Flask (Python)</li>
                <li>• SQLite Database</li>
                <li>• JWT Authentication</li>
                <li>• OpenCV for OMR</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">Frontend</h3>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Next.js 14</li>
                <li>• TypeScript</li>
                <li>• Tailwind CSS</li>
                <li>• shadcn/ui</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
