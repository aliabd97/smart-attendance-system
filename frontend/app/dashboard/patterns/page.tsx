'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, CheckCircle, XCircle, Activity, MessageSquare, Code, Zap, Lock, Key, Shield, User } from 'lucide-react'

interface CircuitBreakerState {
  name: string
  state: 'closed' | 'open' | 'half_open'
  failure_count: number
  failure_threshold: number
  success_count: number
  timeout_seconds: number
  time_until_retry: number
}

interface LogEntry {
  timestamp: string
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
}

export default function PatternsPage() {
  const [cbState, setCbState] = useState<CircuitBreakerState | null>(null)
  const [libraryCbState, setLibraryCbState] = useState<any>(null)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [libraryLoading, setLibraryLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('circuit-breaker')
  const [lastLogCount, setLastLogCount] = useState(0)

  // Strategy Pattern state
  const [strategyInfo, setStrategyInfo] = useState<any>(null)
  const [selectedFormat, setSelectedFormat] = useState('excel')
  const [strategyLoading, setStrategyLoading] = useState(false)
  const [strategyLogs, setStrategyLogs] = useState<LogEntry[]>([])
  const [reportType, setReportType] = useState<'student' | 'course'>('student')
  const [studentId, setStudentId] = useState('STU001')
  const [courseId, setCourseId] = useState('CS101')

  // Choreography Pattern state
  const [rabbitmqEvents, setRabbitmqEvents] = useState<any[]>([])
  const [rabbitmqConnected, setRabbitmqConnected] = useState(false)
  const [publishLoading, setPublishLoading] = useState(false)
  const [choreographyLogs, setChoreographyLogs] = useState<LogEntry[]>([])

  // JWT Auth state
  const [jwtUsername, setJwtUsername] = useState('admin')
  const [jwtPassword, setJwtPassword] = useState('admin123')
  const [jwtToken, setJwtToken] = useState<string | null>(null)
  const [decodedToken, setDecodedToken] = useState<any>(null)
  const [jwtLoading, setJwtLoading] = useState(false)
  const [jwtLogs, setJwtLogs] = useState<LogEntry[]>([])
  const [protectedData, setProtectedData] = useState<any>(null)

  // Fetch Circuit Breaker state and logs
  const fetchCBState = async () => {
    try {
      const res = await fetch('http://localhost:5004/api/pdf/cb-status')
      const data = await res.json()
      setCbState(data.circuit_breaker)
      if (data.circuit_breaker_library) {
        setLibraryCbState(data.circuit_breaker_library)
      }
    } catch (error) {
      console.error('Failed to fetch CB state:', error)
    }
  }

  // Fetch Circuit Breaker logs from backend
  const fetchCBLogs = async () => {
    try {
      const res = await fetch('http://localhost:5004/api/pdf/cb-logs')
      const data = await res.json()
      const backendLogs = data.logs || []

      // Only update if we have new logs
      if (backendLogs.length > lastLogCount) {
        // Convert backend logs to LogEntry format
        const formattedLogs = backendLogs.map((log: any) => ({
          timestamp: log.timestamp,
          type: log.type === 'success' ? 'success' :
                log.type === 'error' ? 'error' :
                log.type === 'warning' ? 'warning' : 'info',
          message: `[${log.state.toUpperCase()}] ${log.message}`
        }))

        // Reverse to show newest first
        setLogs(formattedLogs.reverse().slice(0, 100))
        setLastLogCount(backendLogs.length)
      }
    } catch (error) {
      console.error('Failed to fetch CB logs:', error)
    }
  }

  // Add local log entry (for UI actions)
  const addLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message
    }
    setLogs(prev => [newLog, ...prev].slice(0, 100))
  }

  // Test Circuit Breaker
  const testCircuitBreaker = async () => {
    setLoading(true)
    addLog('info', '🔄 Testing Circuit Breaker...')

    try {
      const res = await fetch('http://localhost:5004/api/pdf/test-cb', { method: 'POST' })
      const data = await res.json()

      if (res.ok) {
        addLog('success', `✅ ${data.result}`)
      } else {
        addLog('error', `❌ ${data.result}`)
      }

      setCbState(data.circuit_breaker)
    } catch (error) {
      addLog('error', `❌ Request failed: ${error}`)
    } finally {
      setLoading(false)
      fetchCBState()
      fetchCBLogs()
    }
  }

  // Reset Circuit Breaker
  const resetCircuitBreaker = async () => {
    addLog('warning', '🔄 Resetting Circuit Breaker...')

    try {
      const res = await fetch('http://localhost:5004/api/pdf/cb-reset', { method: 'POST' })
      const data = await res.json()
      addLog('success', `✅ ${data.message}`)
      setCbState(data.circuit_breaker)
      fetchCBLogs()
    } catch (error) {
      addLog('error', `❌ Reset failed: ${error}`)
    }
  }

  // Clear logs
  const clearLogs = async () => {
    try {
      await fetch('http://localhost:5004/api/pdf/cb-logs', { method: 'DELETE' })
      setLogs([])
      setLastLogCount(0)
    } catch (error) {
      console.error('Failed to clear logs:', error)
    }
  }

  // Test Library Circuit Breaker
  const testLibraryCB = async () => {
    setLibraryLoading(true)
    addLog('info', '📚 Testing Library CB (pybreaker)...')

    try {
      const res = await fetch('http://localhost:5004/api/pdf/test-library-cb', { method: 'POST' })
      const data = await res.json()

      if (res.ok) {
        addLog('success', `✅ [LIBRARY] ${data.result}`)
      } else {
        addLog('error', `❌ [LIBRARY] ${data.result}`)
      }

      setLibraryCbState(data.circuit_breaker)
    } catch (error) {
      addLog('error', `❌ [LIBRARY] Request failed: ${error}`)
    } finally {
      setLibraryLoading(false)
    }
  }

  // ==================== Strategy Pattern Functions ====================

  // Fetch Strategy Pattern info
  const fetchStrategyInfo = async () => {
    try {
      const res = await fetch('http://localhost:5009/api/reports/strategy-info')
      const data = await res.json()
      setStrategyInfo(data)
    } catch (error) {
      console.error('Failed to fetch strategy info:', error)
    }
  }

  // Add Strategy log
  const addStrategyLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message
    }
    setStrategyLogs(prev => [newLog, ...prev].slice(0, 50))
  }

  // Generate report using Strategy Pattern
  const generateReport = async () => {
    setStrategyLoading(true)
    addStrategyLog('info', `🔄 Generating ${selectedFormat.toUpperCase()} report using ${selectedFormat}Strategy...`)

    try {
      let url = ''
      if (reportType === 'student') {
        url = `http://localhost:5009/api/reports/student/${studentId}?course_id=${courseId}&format=${selectedFormat}`
      } else {
        url = `http://localhost:5009/api/reports/course/${courseId}?format=${selectedFormat}`
      }

      addStrategyLog('info', `📡 Calling: ${url}`)
      addStrategyLog('info', `🏭 Factory creating strategy: "${selectedFormat}" → ${selectedFormat.charAt(0).toUpperCase() + selectedFormat.slice(1)}ReportStrategy`)

      const res = await fetch(url)

      if (res.ok) {
        // Download the file
        const blob = await res.blob()
        const downloadUrl = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = downloadUrl
        a.download = `report_${reportType}_${selectedFormat}.${selectedFormat === 'excel' ? 'xlsx' : selectedFormat}`
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(downloadUrl)

        addStrategyLog('success', `✅ Report generated successfully using ${selectedFormat.toUpperCase()} Strategy!`)
        addStrategyLog('success', `📥 File downloaded: report_${reportType}.${selectedFormat === 'excel' ? 'xlsx' : selectedFormat}`)
      } else {
        const error = await res.json()
        addStrategyLog('error', `❌ Failed: ${error.error || 'Unknown error'}`)
      }
    } catch (error) {
      addStrategyLog('error', `❌ Request failed: ${error}`)
    } finally {
      setStrategyLoading(false)
    }
  }

  // Fetch strategy info when tab changes
  useEffect(() => {
    if (activeTab === 'strategy') {
      fetchStrategyInfo()
    }
  }, [activeTab])

  // ==================== Choreography Pattern Functions ====================

  // Add Choreography log
  const addChoreographyLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message
    }
    setChoreographyLogs(prev => [newLog, ...prev].slice(0, 50))
  }

  // Fetch RabbitMQ events from Course Service
  const fetchRabbitmqEvents = async () => {
    try {
      const res = await fetch('http://localhost:5002/api/courses/attendance-events')
      const data = await res.json()
      setRabbitmqEvents(data.events || [])
      setRabbitmqConnected(true)
    } catch (error) {
      setRabbitmqConnected(false)
    }
  }

  // Publish test attendance event
  const publishTestEvent = async () => {
    setPublishLoading(true)
    addChoreographyLog('info', '📤 Publishing attendance event to RabbitMQ...')

    try {
      const testAttendance = {
        student_id: `STU${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
        course_id: 'CS101',
        date: new Date().toISOString().split('T')[0],
        status: 'present'
      }

      addChoreographyLog('info', `📝 Event: student=${testAttendance.student_id}, status=${testAttendance.status}`)

      const res = await fetch('http://localhost:5005/api/attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testAttendance)
      })

      if (res.ok) {
        addChoreographyLog('success', '✅ Event published to RabbitMQ!')
        addChoreographyLog('info', '📥 Course Service will consume the event...')

        // Wait a moment and refresh events
        setTimeout(() => {
          fetchRabbitmqEvents()
          addChoreographyLog('success', '✅ Event consumed by Course Service!')
        }, 1000)
      } else {
        const error = await res.json()
        addChoreographyLog('error', `❌ Failed: ${error.error || 'Unknown error'}`)
      }
    } catch (error) {
      addChoreographyLog('error', `❌ Attendance Service not available: ${error}`)
    } finally {
      setPublishLoading(false)
    }
  }

  // Fetch events when choreography tab is active
  useEffect(() => {
    if (activeTab === 'choreography') {
      fetchRabbitmqEvents()
      const interval = setInterval(fetchRabbitmqEvents, 2000)
      return () => clearInterval(interval)
    }
  }, [activeTab])

  // ==================== JWT Authentication Functions ====================

  // Add JWT log
  const addJwtLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message
    }
    setJwtLogs(prev => [newLog, ...prev].slice(0, 50))
  }

  // Decode JWT token (base64)
  const decodeJwt = (token: string) => {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) return null
      const payload = JSON.parse(atob(parts[1]))
      return payload
    } catch {
      return null
    }
  }

  // Login and get JWT token
  const jwtLogin = async () => {
    setJwtLoading(true)
    addJwtLog('info', `🔐 Attempting login: username="${jwtUsername}"`)

    try {
      const res = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: jwtUsername, password: jwtPassword })
      })

      const data = await res.json()

      if (res.ok && data.token) {
        setJwtToken(data.token)
        const decoded = decodeJwt(data.token)
        setDecodedToken(decoded)

        addJwtLog('success', '✅ Login successful!')
        addJwtLog('info', `📋 Token received (${data.token.length} chars)`)
        addJwtLog('info', `👤 User: ${decoded?.username}, Role: ${decoded?.role}`)
        addJwtLog('info', `⏰ Expires: ${decoded?.exp ? new Date(decoded.exp * 1000).toLocaleString() : 'N/A'}`)
      } else {
        addJwtLog('error', `❌ Login failed: ${data.error || 'Invalid credentials'}`)
      }
    } catch (error) {
      addJwtLog('error', `❌ Auth Service not available: ${error}`)
    } finally {
      setJwtLoading(false)
    }
  }

  // Test protected endpoint
  const testProtectedEndpoint = async () => {
    if (!jwtToken) {
      addJwtLog('warning', '⚠️ No token! Login first.')
      return
    }

    addJwtLog('info', '🔒 Testing protected endpoint...')
    addJwtLog('info', `📤 Header: Authorization: Bearer ${jwtToken.substring(0, 20)}...`)

    try {
      const res = await fetch('http://localhost:5000/api/students', {
        headers: { 'Authorization': `Bearer ${jwtToken}` }
      })

      if (res.ok) {
        const data = await res.json()
        setProtectedData(data)
        addJwtLog('success', '✅ Access granted! Protected data received.')
        addJwtLog('info', `📊 Received ${Array.isArray(data) ? data.length : 1} record(s)`)
      } else {
        const error = await res.json()
        addJwtLog('error', `❌ Access denied: ${error.error || res.status}`)
      }
    } catch (error) {
      addJwtLog('error', `❌ Request failed: ${error}`)
    }
  }

  // Test without token
  const testWithoutToken = async () => {
    addJwtLog('info', '🚫 Testing WITHOUT token...')

    try {
      const res = await fetch('http://localhost:5000/api/students')

      if (res.ok) {
        addJwtLog('warning', '⚠️ Endpoint accessible without token (should not happen)')
      } else {
        const error = await res.json()
        addJwtLog('success', `✅ Correctly rejected: ${error.error || '401 Unauthorized'}`)
      }
    } catch (error) {
      addJwtLog('error', `❌ Request failed: ${error}`)
    }
  }

  // Logout
  const jwtLogout = () => {
    setJwtToken(null)
    setDecodedToken(null)
    setProtectedData(null)
    addJwtLog('info', '👋 Logged out - Token cleared')
  }

  // Track previous events count to detect new events
  const [prevEventsCount, setPrevEventsCount] = useState(0)

  // Auto-log when new events arrive
  useEffect(() => {
    if (rabbitmqEvents.length > prevEventsCount && prevEventsCount > 0) {
      const newEvents = rabbitmqEvents.slice(prevEventsCount)
      newEvents.forEach(event => {
        addChoreographyLog('info', `📤 Event published: ${event.event}`)
        addChoreographyLog('success', `📥 Consumed: student=${event.student_id}, status=${event.status}`)
      })
    }
    setPrevEventsCount(rabbitmqEvents.length)
  }, [rabbitmqEvents])

  // Auto-refresh CB state and logs
  useEffect(() => {
    fetchCBState()
    fetchCBLogs()
    const stateInterval = setInterval(fetchCBState, 2000)
    const logsInterval = setInterval(fetchCBLogs, 1000) // Poll logs every second
    return () => {
      clearInterval(stateInterval)
      clearInterval(logsInterval)
    }
  }, [lastLogCount])

  const getStateColor = (state: string) => {
    switch (state) {
      case 'closed': return 'bg-green-500'
      case 'open': return 'bg-red-500'
      case 'half_open': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getStateIcon = (state: string) => {
    switch (state) {
      case 'closed': return <CheckCircle className="h-5 w-5" />
      case 'open': return <XCircle className="h-5 w-5" />
      case 'half_open': return <AlertCircle className="h-5 w-5" />
      default: return <Activity className="h-5 w-5" />
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Design Patterns Demo</h1>
        <p className="text-muted-foreground">
          Interactive demonstration of design patterns for academic presentation
        </p>
      </div>

      {/* Simple Tabs */}
      <div className="space-y-4">
        <div className="flex gap-2 border-b">
          <button
            onClick={() => setActiveTab('circuit-breaker')}
            className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'circuit-breaker'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Zap className="h-4 w-4" />
            Circuit Breaker
          </button>
          <button
            onClick={() => setActiveTab('strategy')}
            className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'strategy'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Code className="h-4 w-4" />
            Strategy Pattern
          </button>
          <button
            onClick={() => setActiveTab('choreography')}
            className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'choreography'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            Choreography
          </button>
          <button
            onClick={() => setActiveTab('auth')}
            className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'auth'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Activity className="h-4 w-4" />
            JWT Auth
          </button>
        </div>

        {/* Circuit Breaker Tab */}
        {activeTab === 'circuit-breaker' && (
          <div className="space-y-4">
            {/* Comparison Header */}
            <div className="bg-muted/50 p-4 rounded-lg border">
              <h3 className="font-semibold text-lg mb-2">Manual vs Library Implementation</h3>
              <p className="text-sm text-muted-foreground">
                Both implement the same Circuit Breaker pattern with 3 states (CLOSED → OPEN → HALF_OPEN).
                <br />
                <strong>Manual:</strong> Full control, custom logging. <strong>Library (pybreaker):</strong> Less code, proven solution.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {/* State Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {cbState && getStateIcon(cbState.state)}
                    Circuit Breaker State
                  </CardTitle>
                  <CardDescription>
                    State Pattern - Manual Implementation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {cbState ? (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Current State:</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${getStateColor(cbState.state)}`}>
                          {cbState.state.toUpperCase().replace('_', '-')}
                        </span>
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Failures:</span>
                          <span className="font-mono">{cbState.failure_count} / {cbState.failure_threshold}</span>
                        </div>

                        {cbState.state === 'half_open' && (
                          <div className="flex justify-between">
                            <span>Success Count:</span>
                            <span className="font-mono">{cbState.success_count}</span>
                          </div>
                        )}

                        {cbState.state === 'open' && (
                          <div className="flex justify-between">
                            <span>Retry in:</span>
                            <span className="font-mono">{cbState.time_until_retry}s</span>
                          </div>
                        )}

                        <div className="flex justify-between">
                          <span>Timeout:</span>
                          <span className="font-mono">{cbState.timeout_seconds}s</span>
                        </div>
                      </div>

                      <div className="pt-4 space-y-2">
                        <Button
                          onClick={testCircuitBreaker}
                          disabled={loading}
                          className="w-full"
                        >
                          {loading ? 'Testing...' : 'Test Circuit Breaker'}
                        </Button>

                        <Button
                          onClick={resetCircuitBreaker}
                          variant="outline"
                          className="w-full"
                        >
                          Reset to CLOSED
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      Loading Circuit Breaker state...
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Library CB Card */}
              <Card className="border-blue-200 dark:border-blue-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {libraryCbState && getStateIcon(libraryCbState.state)}
                    Library CB (pybreaker)
                  </CardTitle>
                  <CardDescription>
                    Using pybreaker library - Same pattern, less code
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {libraryCbState ? (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Current State:</span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${getStateColor(libraryCbState.state)}`}>
                          {libraryCbState.state.toUpperCase().replace('_', '-')}
                        </span>
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Failures:</span>
                          <span className="font-mono">{libraryCbState.fail_counter || 0}</span>
                        </div>

                        <div className="flex justify-between">
                          <span>Implementation:</span>
                          <span className="font-mono text-xs">{libraryCbState.implementation}</span>
                        </div>
                      </div>

                      <div className="pt-4">
                        <Button
                          onClick={testLibraryCB}
                          disabled={libraryLoading}
                          className="w-full"
                          variant="secondary"
                        >
                          {libraryLoading ? 'Testing...' : 'Test Library CB'}
                        </Button>
                      </div>

                      <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                        📚 This uses the pybreaker library - same behavior as manual implementation but with less custom code.
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <p className="mb-4">Library CB not initialized yet</p>
                      <Button
                        onClick={testLibraryCB}
                        disabled={libraryLoading}
                        variant="secondary"
                      >
                        Initialize & Test
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Instructions Card */}
              <Card>
                <CardHeader>
                  <CardTitle>How to Demo</CardTitle>
                  <CardDescription>
                    Steps to demonstrate Circuit Breaker pattern
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">1</span>
                      <div>
                        <p className="font-medium">Stop Attendance Service</p>
                        <code className="text-xs bg-muted px-2 py-1 rounded block mt-1">
                          .\STOP_ONE_SERVICE.ps1 5005
                        </code>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">2</span>
                      <div>
                        <p className="font-medium">Click "Test Circuit Breaker" 3 times</p>
                        <p className="text-muted-foreground">Watch failures count increase</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">3</span>
                      <div>
                        <p className="font-medium">State changes to OPEN</p>
                        <p className="text-muted-foreground">Requests rejected immediately</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">4</span>
                      <div>
                        <p className="font-medium">Wait 15 seconds</p>
                        <p className="text-muted-foreground">State → HALF_OPEN</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">5</span>
                      <div>
                        <p className="font-medium">Restart Attendance Service</p>
                        <code className="text-xs bg-muted px-2 py-1 rounded block mt-1">
                          cd attendance-service && python app.py
                        </code>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0">6</span>
                      <div>
                        <p className="font-medium">Test again → CLOSED</p>
                        <p className="text-muted-foreground">Service recovered!</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Logs Card */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Live Logs</CardTitle>
                    <CardDescription>
                      Real-time Circuit Breaker activity - shows all state transitions
                    </CardDescription>
                  </div>
                  <Button
                    onClick={clearLogs}
                    variant="outline"
                    size="sm"
                  >
                    Clear Logs
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-96 overflow-y-auto">
                  {logs.length > 0 ? (
                    logs.map((log, idx) => (
                      <div key={idx} className="mb-1">
                        <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                        <span className={
                          log.type === 'error' ? 'text-red-400' :
                          log.type === 'success' ? 'text-green-400' :
                          log.type === 'warning' ? 'text-yellow-400' :
                          'text-blue-400'
                        }>
                          {log.message}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-500 text-center py-8">
                      No logs yet. Test CB or upload PDF from OMR Processing to see logs...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Strategy Pattern Tab */}
        {activeTab === 'strategy' && (
          <div className="space-y-4">
            {/* Description */}
            <div className="bg-muted/50 p-4 rounded-lg border">
              <h3 className="font-semibold text-lg mb-2">Strategy Pattern + Factory + Reflection</h3>
              <p className="text-sm text-muted-foreground">
                Allows runtime selection of report generation algorithms without modifying client code.
                <br />
                <strong>Factory:</strong> Creates strategy from string name. <strong>Reflection:</strong> Loads class dynamically at runtime.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {/* Strategy Selection Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="h-5 w-5" />
                    Generate Report
                  </CardTitle>
                  <CardDescription>
                    Select format to use different Strategy
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Report Type */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Report Type:</label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setReportType('student')}
                        className={`px-3 py-1 rounded text-sm ${reportType === 'student' ? 'bg-primary text-white' : 'bg-muted'}`}
                      >
                        Student
                      </button>
                      <button
                        onClick={() => setReportType('course')}
                        className={`px-3 py-1 rounded text-sm ${reportType === 'course' ? 'bg-primary text-white' : 'bg-muted'}`}
                      >
                        Course
                      </button>
                    </div>
                  </div>

                  {/* IDs */}
                  {reportType === 'student' && (
                    <div>
                      <label className="text-sm font-medium mb-1 block">Student ID:</label>
                      <input
                        type="text"
                        value={studentId}
                        onChange={(e) => setStudentId(e.target.value)}
                        className="w-full px-3 py-2 border rounded text-sm"
                        placeholder="STU001"
                      />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-1 block">Course ID:</label>
                    <input
                      type="text"
                      value={courseId}
                      onChange={(e) => setCourseId(e.target.value)}
                      className="w-full px-3 py-2 border rounded text-sm"
                      placeholder="CS101"
                    />
                  </div>

                  {/* Format Selection */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Output Format (Strategy):</label>
                    <div className="grid grid-cols-3 gap-2">
                      {['excel', 'pdf', 'csv'].map((format) => (
                        <button
                          key={format}
                          onClick={() => setSelectedFormat(format)}
                          className={`px-3 py-2 rounded text-sm font-medium border transition-colors ${
                            selectedFormat === format
                              ? 'bg-primary text-white border-primary'
                              : 'bg-background hover:bg-muted'
                          }`}
                        >
                          {format.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Generate Button */}
                  <Button
                    onClick={generateReport}
                    disabled={strategyLoading}
                    className="w-full"
                  >
                    {strategyLoading ? 'Generating...' : `Generate ${selectedFormat.toUpperCase()} Report`}
                  </Button>
                </CardContent>
              </Card>

              {/* Current Strategy Info */}
              <Card className="border-blue-200 dark:border-blue-800">
                <CardHeader>
                  <CardTitle>Active Strategy</CardTitle>
                  <CardDescription>
                    Currently selected strategy implementation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary mb-1">
                        {selectedFormat.charAt(0).toUpperCase() + selectedFormat.slice(1)}ReportStrategy
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {strategyInfo?.strategies?.[selectedFormat]?.description || 'Loading...'}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Extension:</span>
                      <span className="font-mono">{strategyInfo?.strategies?.[selectedFormat]?.extension || '...'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Factory:</span>
                      <span className="font-mono text-xs">StrategyFactory</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Method:</span>
                      <span className="font-mono text-xs">Reflection</span>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded font-mono">
                    factory.create_strategy("{selectedFormat}")
                    <br />
                    → {selectedFormat.charAt(0).toUpperCase() + selectedFormat.slice(1)}ReportStrategy()
                  </div>
                </CardContent>
              </Card>

              {/* How It Works */}
              <Card>
                <CardHeader>
                  <CardTitle>How It Works</CardTitle>
                  <CardDescription>Strategy Pattern flow</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-start gap-2">
                      <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">1</span>
                      <span>User selects format: <code className="bg-muted px-1 rounded">{selectedFormat}</code></span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">2</span>
                      <span>Factory uses Reflection to load class</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">3</span>
                      <span>Strategy instance created dynamically</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs shrink-0">4</span>
                      <span>Same interface, different implementation</span>
                    </div>
                  </div>

                  <div className="mt-4 p-3 bg-muted/50 rounded text-xs font-mono">
                    <div className="text-muted-foreground"># Without Strategy (bad):</div>
                    <div>if format == 'excel': ...</div>
                    <div>elif format == 'pdf': ...</div>
                    <div className="mt-2 text-muted-foreground"># With Strategy (good):</div>
                    <div className="text-green-600">strategy = factory.create(format)</div>
                    <div className="text-green-600">strategy.generate_report()</div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Strategy Logs */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Strategy Pattern Logs</CardTitle>
                    <CardDescription>Watch the Strategy Pattern in action</CardDescription>
                  </div>
                  <Button onClick={() => setStrategyLogs([])} variant="outline" size="sm">
                    Clear Logs
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">
                  {strategyLogs.length > 0 ? (
                    strategyLogs.map((log, idx) => (
                      <div key={idx} className="mb-1">
                        <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                        <span className={
                          log.type === 'error' ? 'text-red-400' :
                          log.type === 'success' ? 'text-green-400' :
                          log.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                        }>
                          {log.message}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-500 text-center py-8">
                      Select a format and click "Generate Report" to see Strategy Pattern in action...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Choreography Pattern Tab */}
        {activeTab === 'choreography' && (
          <div className="space-y-4">
            {/* Description */}
            <div className="bg-muted/50 p-4 rounded-lg border">
              <h3 className="font-semibold text-lg mb-2">Choreography Pattern (Event-Driven)</h3>
              <p className="text-sm text-muted-foreground">
                Services communicate through events via RabbitMQ message broker without a central coordinator.
                <br />
                <strong>Producer:</strong> Attendance Service publishes events. <strong>Consumer:</strong> Course Service receives events independently.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {/* Producer Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    Producer
                  </CardTitle>
                  <CardDescription>
                    Attendance Service → RabbitMQ
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-2">Service</div>
                    <div className="text-lg font-bold">Attendance Service</div>
                    <div className="text-xs text-muted-foreground">Port 5005</div>
                  </div>

                  <div className="p-3 bg-muted/50 rounded text-sm">
                    <div className="font-semibold mb-2">How to trigger:</div>
                    <ol className="text-xs text-muted-foreground space-y-1 list-decimal list-inside">
                      <li>Go to <strong>OMR Processing</strong></li>
                      <li>Upload a PDF with attendance</li>
                      <li>Attendance records → publish events</li>
                      <li>Events appear here automatically</li>
                    </ol>
                  </div>

                  <div className="text-xs text-muted-foreground">
                    Event: attendance_recorded
                  </div>
                </CardContent>
              </Card>

              {/* RabbitMQ Card */}
              <Card className="border-orange-200 dark:border-orange-800">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-orange-500" />
                    RabbitMQ
                  </CardTitle>
                  <CardDescription>
                    Message Broker (Queue)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-orange-50 dark:bg-orange-950 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-2">Queue</div>
                    <div className="text-lg font-bold font-mono">attendance_events</div>
                    <div className={`text-xs mt-2 ${rabbitmqConnected ? 'text-green-600' : 'text-red-600'}`}>
                      {rabbitmqConnected ? '● Connected' : '○ Disconnected'}
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Delivery Mode:</span>
                      <span className="font-mono">Persistent</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Events Received:</span>
                      <span className="font-mono">{rabbitmqEvents.length}</span>
                    </div>
                  </div>

                  <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                    Messages persist until acknowledged by consumer
                  </div>
                </CardContent>
              </Card>

              {/* Consumer Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    Consume Events
                  </CardTitle>
                  <CardDescription>
                    RabbitMQ → Course Service
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-muted/50 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground mb-2">Consumer</div>
                    <div className="text-lg font-bold">Course Service</div>
                    <div className="text-xs text-muted-foreground">Port 5002</div>
                  </div>

                  <Button
                    onClick={fetchRabbitmqEvents}
                    variant="outline"
                    className="w-full"
                  >
                    🔄 Refresh Events
                  </Button>

                  <div className="text-xs text-muted-foreground">
                    Listens independently - no direct coupling to Attendance Service
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Event Flow Diagram */}
            <Card>
              <CardHeader>
                <CardTitle>Event Flow</CardTitle>
                <CardDescription>How Choreography Pattern works</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center gap-4 p-4 bg-muted/30 rounded-lg overflow-x-auto">
                  <div className="text-center p-3 bg-blue-100 dark:bg-blue-900 rounded-lg min-w-[120px]">
                    <div className="font-bold">Attendance</div>
                    <div className="text-xs">Service</div>
                  </div>
                  <div className="text-2xl">→</div>
                  <div className="text-center p-3 bg-orange-100 dark:bg-orange-900 rounded-lg min-w-[120px]">
                    <div className="font-bold">RabbitMQ</div>
                    <div className="text-xs">publish</div>
                  </div>
                  <div className="text-2xl">→</div>
                  <div className="text-center p-3 bg-green-100 dark:bg-green-900 rounded-lg min-w-[120px]">
                    <div className="font-bold">Course</div>
                    <div className="text-xs">consume</div>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-muted/50 rounded">
                    <div className="font-semibold mb-1">Why Choreography?</div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• No central coordinator</li>
                      <li>• Services are loosely coupled</li>
                      <li>• Asynchronous communication</li>
                    </ul>
                  </div>
                  <div className="p-3 bg-muted/50 rounded">
                    <div className="font-semibold mb-1">Benefits</div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• If Course is down, Attendance still works</li>
                      <li>• Events queue until consumed</li>
                      <li>• Easy to add more consumers</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Events List and Logs */}
            <div className="grid gap-4 md:grid-cols-2">
              {/* Received Events */}
              <Card>
                <CardHeader>
                  <CardTitle>Received Events</CardTitle>
                  <CardDescription>Events consumed by Course Service</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted/50 rounded-lg h-64 overflow-y-auto p-2">
                    {rabbitmqEvents.length > 0 ? (
                      rabbitmqEvents.slice().reverse().map((event, idx) => (
                        <div key={idx} className="p-2 mb-2 bg-background rounded border text-xs">
                          <div className="flex justify-between">
                            <span className="font-semibold">{event.event}</span>
                            <span className="text-muted-foreground">{event.date}</span>
                          </div>
                          <div className="text-muted-foreground mt-1">
                            Student: {event.student_id} | Status: {event.status}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-muted-foreground py-8">
                        No events yet. Upload PDF from OMR Processing to see events...
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Choreography Logs */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Live Logs</CardTitle>
                      <CardDescription>Real-time event flow</CardDescription>
                    </div>
                    <Button onClick={() => setChoreographyLogs([])} variant="outline" size="sm">
                      Clear
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">
                    {choreographyLogs.length > 0 ? (
                      choreographyLogs.map((log, idx) => (
                        <div key={idx} className="mb-1">
                          <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                          <span className={
                            log.type === 'error' ? 'text-red-400' :
                            log.type === 'success' ? 'text-green-400' :
                            log.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                          }>
                            {log.message}
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="text-gray-500 text-center py-8">
                        Upload PDF from OMR Processing to see events flow...
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'auth' && (
          <div className="space-y-4">
            {/* Description */}
            <div className="bg-muted/50 p-4 rounded-lg border">
              <h3 className="font-semibold text-lg mb-2">JWT Authentication (JSON Web Token)</h3>
              <p className="text-sm text-muted-foreground">
                Token-based authentication for secure, stateless authentication across microservices.
                <br />
                <strong>Auth Service:</strong> Generates JWT tokens. <strong>API Gateway:</strong> Validates tokens and forwards user info.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {/* Login Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lock className="h-5 w-5" />
                    1. Login
                  </CardTitle>
                  <CardDescription>
                    Authenticate to get JWT token
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Username:</label>
                    <input
                      type="text"
                      value={jwtUsername}
                      onChange={(e) => setJwtUsername(e.target.value)}
                      className="w-full px-3 py-2 border rounded text-sm"
                      placeholder="admin"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Password:</label>
                    <input
                      type="password"
                      value={jwtPassword}
                      onChange={(e) => setJwtPassword(e.target.value)}
                      className="w-full px-3 py-2 border rounded text-sm"
                      placeholder="admin123"
                    />
                  </div>

                  <Button
                    onClick={jwtLogin}
                    disabled={jwtLoading}
                    className="w-full"
                  >
                    {jwtLoading ? 'Logging in...' : 'Login'}
                  </Button>

                  {jwtToken && (
                    <Button
                      onClick={jwtLogout}
                      variant="outline"
                      className="w-full"
                    >
                      Logout
                    </Button>
                  )}

                  <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                    Default: admin / admin123
                  </div>
                </CardContent>
              </Card>

              {/* Token Info Card */}
              <Card className={jwtToken ? 'border-green-200 dark:border-green-800' : ''}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    2. JWT Token
                  </CardTitle>
                  <CardDescription>
                    Decoded token payload
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {decodedToken ? (
                    <>
                      <div className="p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="font-semibold text-green-700 dark:text-green-300">Token Active</span>
                        </div>
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>User ID:</span>
                          <span className="font-mono">{decodedToken.user_id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Username:</span>
                          <span className="font-mono">{decodedToken.username}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Role:</span>
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            decodedToken.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                            decodedToken.role === 'teacher' ? 'bg-blue-100 text-blue-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {decodedToken.role}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Expires:</span>
                          <span className="font-mono text-xs">
                            {new Date(decodedToken.exp * 1000).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>

                      <div className="text-xs bg-muted/50 p-2 rounded font-mono break-all max-h-20 overflow-y-auto">
                        {jwtToken?.substring(0, 50)}...
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">
                      <Lock className="h-12 w-12 mx-auto mb-2 opacity-20" />
                      <p>No token yet</p>
                      <p className="text-xs">Login to get JWT token</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Test Protected Endpoint */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    3. Test Access
                  </CardTitle>
                  <CardDescription>
                    Test protected API endpoints
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button
                    onClick={testProtectedEndpoint}
                    disabled={!jwtToken}
                    className="w-full"
                  >
                    🔓 Access WITH Token
                  </Button>

                  <Button
                    onClick={testWithoutToken}
                    variant="outline"
                    className="w-full"
                  >
                    🚫 Access WITHOUT Token
                  </Button>

                  {protectedData && (
                    <div className="p-3 bg-green-50 dark:bg-green-950 rounded text-sm">
                      <div className="font-semibold text-green-700 dark:text-green-300 mb-1">
                        ✅ Data Received!
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {Array.isArray(protectedData) ? `${protectedData.length} records` : 'Data object'}
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-muted-foreground">
                    The API Gateway validates token before forwarding request to services
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* JWT Flow Diagram */}
            <Card>
              <CardHeader>
                <CardTitle>JWT Authentication Flow</CardTitle>
                <CardDescription>How token-based authentication works</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center gap-2 p-4 bg-muted/30 rounded-lg overflow-x-auto text-sm">
                  <div className="text-center p-3 bg-blue-100 dark:bg-blue-900 rounded-lg min-w-[100px]">
                    <User className="h-6 w-6 mx-auto mb-1" />
                    <div className="font-bold">Client</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="text-xs text-muted-foreground">login</div>
                    <div className="text-lg">→</div>
                  </div>
                  <div className="text-center p-3 bg-purple-100 dark:bg-purple-900 rounded-lg min-w-[100px]">
                    <Lock className="h-6 w-6 mx-auto mb-1" />
                    <div className="font-bold">Auth</div>
                    <div className="text-xs">5007</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="text-xs text-muted-foreground">JWT</div>
                    <div className="text-lg">→</div>
                  </div>
                  <div className="text-center p-3 bg-blue-100 dark:bg-blue-900 rounded-lg min-w-[100px]">
                    <User className="h-6 w-6 mx-auto mb-1" />
                    <div className="font-bold">Client</div>
                    <div className="text-xs">stores</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="text-xs text-muted-foreground">Bearer</div>
                    <div className="text-lg">→</div>
                  </div>
                  <div className="text-center p-3 bg-orange-100 dark:bg-orange-900 rounded-lg min-w-[100px]">
                    <Shield className="h-6 w-6 mx-auto mb-1" />
                    <div className="font-bold">Gateway</div>
                    <div className="text-xs">validates</div>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="text-xs text-muted-foreground">headers</div>
                    <div className="text-lg">→</div>
                  </div>
                  <div className="text-center p-3 bg-green-100 dark:bg-green-900 rounded-lg min-w-[100px]">
                    <CheckCircle className="h-6 w-6 mx-auto mb-1" />
                    <div className="font-bold">Service</div>
                  </div>
                </div>

                {/* Token Structure */}
                <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                  <div className="font-semibold mb-2">JWT Token Structure:</div>
                  <div className="flex gap-2 text-xs font-mono">
                    <span className="px-2 py-1 bg-red-100 dark:bg-red-900 rounded">Header</span>
                    <span>.</span>
                    <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900 rounded">Payload</span>
                    <span>.</span>
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 rounded">Signature</span>
                  </div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    <div><span className="text-red-600">Header:</span> Algorithm (HS256)</div>
                    <div><span className="text-purple-600">Payload:</span> user_id, username, role, exp</div>
                    <div><span className="text-blue-600">Signature:</span> HMAC(header + payload, secret)</div>
                  </div>
                </div>

                {/* Benefits */}
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-muted/50 rounded">
                    <div className="font-semibold mb-1">Why JWT?</div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Stateless - No server session</li>
                      <li>• Self-contained - Carries user info</li>
                      <li>• Signed - Cannot be tampered</li>
                    </ul>
                  </div>
                  <div className="p-3 bg-muted/50 rounded">
                    <div className="font-semibold mb-1">Security Features</div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Expiration (24 hours)</li>
                      <li>• Role-based access</li>
                      <li>• Cryptographic signature</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* JWT Logs */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Authentication Logs</CardTitle>
                    <CardDescription>Watch JWT authentication in action</CardDescription>
                  </div>
                  <Button onClick={() => setJwtLogs([])} variant="outline" size="sm">
                    Clear Logs
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">
                  {jwtLogs.length > 0 ? (
                    jwtLogs.map((log, idx) => (
                      <div key={idx} className="mb-1">
                        <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                        <span className={
                          log.type === 'error' ? 'text-red-400' :
                          log.type === 'success' ? 'text-green-400' :
                          log.type === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                        }>
                          {log.message}
                        </span>
                      </div>
                    ))
                  ) : (
                    <div className="text-gray-500 text-center py-8">
                      Click "Login" to see JWT authentication flow...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
