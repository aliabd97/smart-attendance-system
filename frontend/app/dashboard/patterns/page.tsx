'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AlertCircle, CheckCircle, XCircle, Activity, MessageSquare, Code, Zap } from 'lucide-react'

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
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('circuit-breaker')

  // Fetch Circuit Breaker state
  const fetchCBState = async () => {
    try {
      const res = await fetch('http://localhost:5004/api/pdf/cb-status')
      const data = await res.json()
      setCbState(data.circuit_breaker)
    } catch (error) {
      console.error('Failed to fetch CB state:', error)
    }
  }

  // Add log entry
  const addLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message
    }
    setLogs(prev => [newLog, ...prev].slice(0, 50))
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
    } catch (error) {
      addLog('error', `❌ Reset failed: ${error}`)
    }
  }

  // Auto-refresh CB state
  useEffect(() => {
    fetchCBState()
    const interval = setInterval(fetchCBState, 2000)
    return () => clearInterval(interval)
  }, [])

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
            <div className="grid gap-4 md:grid-cols-2">
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
                <CardTitle>Live Logs</CardTitle>
                <CardDescription>
                  Real-time Circuit Breaker activity logs
                </CardDescription>
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
                      No logs yet. Click "Test Circuit Breaker" to start...
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Other tabs - Coming soon */}
        {activeTab === 'strategy' && (
          <Card>
            <CardHeader>
              <CardTitle>Strategy Pattern + Reflection</CardTitle>
              <CardDescription>Coming soon...</CardDescription>
            </CardHeader>
          </Card>
        )}

        {activeTab === 'choreography' && (
          <Card>
            <CardHeader>
              <CardTitle>Choreography Pattern (RabbitMQ)</CardTitle>
              <CardDescription>Coming soon...</CardDescription>
            </CardHeader>
          </Card>
        )}

        {activeTab === 'auth' && (
          <Card>
            <CardHeader>
              <CardTitle>JWT Authentication</CardTitle>
              <CardDescription>Coming soon...</CardDescription>
            </CardHeader>
          </Card>
        )}
      </div>
    </div>
  )
}
