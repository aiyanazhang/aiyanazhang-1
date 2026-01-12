'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Terminal, Server, X, Plus, History, Settings, Loader2 } from 'lucide-react'

interface SSHConnection {
  id: string
  host: string
  port: number
  username: string
  status: 'connected' | 'disconnected' | 'connecting'
  connectedAt?: Date
}

interface TerminalLine {
  type: 'input' | 'output' | 'error' | 'system'
  content: string
  timestamp: Date
}

export default function SSHConnectionPage() {
  const [connections, setConnections] = useState<SSHConnection[]>([])
  const [activeConnectionId, setActiveConnectionId] = useState<string | null>(null)
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>([])
  const [currentInput, setCurrentInput] = useState('')
  const [isConnecting, setIsConnecting] = useState(false)
  const terminalRef = useRef<HTMLDivElement>(null)

  // Connection form state
  const [formData, setFormData] = useState({
    host: '',
    port: '22',
    username: '',
    password: '',
  })

  const activeConnection = connections.find(c => c.id === activeConnectionId)

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [terminalLines])

  const addTerminalLine = (type: TerminalLine['type'], content: string) => {
    setTerminalLines(prev => [...prev, { type, content, timestamp: new Date() }])
  }

  const handleConnect = async () => {
    if (!formData.host || !formData.username || !formData.password) {
      addTerminalLine('error', 'Error: Please fill in all required fields')
      return
    }

    setIsConnecting(true)
    addTerminalLine('system', `Connecting to ${formData.username}@${formData.host}:${formData.port}...`)

    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 1500))

    const newConnection: SSHConnection = {
      id: `conn-${Date.now()}`,
      host: formData.host,
      port: parseInt(formData.port),
      username: formData.username,
      status: 'connected',
      connectedAt: new Date(),
    }

    setConnections(prev => [...prev, newConnection])
    setActiveConnectionId(newConnection.id)
    setIsConnecting(false)

    addTerminalLine('system', `Connected to ${formData.host}`)
    addTerminalLine('system', `Last login: ${new Date().toLocaleString()}`)
    addTerminalLine('output', `[${formData.username}@${formData.host.split('.')[0]} ~]$ `)

    // Clear form
    setFormData(prev => ({ ...prev, password: '' }))
  }

  const handleDisconnect = (connectionId: string) => {
    const conn = connections.find(c => c.id === connectionId)
    if (conn) {
      addTerminalLine('system', `Disconnected from ${conn.host}`)
    }
    setConnections(prev => prev.filter(c => c.id !== connectionId))
    if (activeConnectionId === connectionId) {
      const remaining = connections.filter(c => c.id !== connectionId)
      setActiveConnectionId(remaining.length > 0 ? remaining[0].id : null)
    }
  }

  const handleTerminalInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && currentInput.trim()) {
      const cmd = currentInput.trim()
      addTerminalLine('input', `$ ${cmd}`)

      // Simulate command responses
      if (cmd === 'ls') {
        addTerminalLine('output', 'Desktop  Documents  Downloads  Music  Pictures  Videos')
      } else if (cmd === 'pwd') {
        addTerminalLine('output', `/home/${activeConnection?.username || 'user'}`)
      } else if (cmd === 'whoami') {
        addTerminalLine('output', activeConnection?.username || 'user')
      } else if (cmd === 'date') {
        addTerminalLine('output', new Date().toString())
      } else if (cmd === 'uname -a') {
        addTerminalLine('output', 'Linux server 5.15.0-generic #1 SMP x86_64 GNU/Linux')
      } else if (cmd === 'clear') {
        setTerminalLines([])
      } else if (cmd === 'exit') {
        if (activeConnectionId) {
          handleDisconnect(activeConnectionId)
        }
      } else if (cmd.startsWith('echo ')) {
        addTerminalLine('output', cmd.substring(5))
      } else if (cmd === 'help') {
        addTerminalLine('output', 'Available commands: ls, pwd, whoami, date, uname -a, echo, clear, exit, help')
      } else {
        addTerminalLine('error', `bash: ${cmd}: command not found (mock terminal)`)
      }

      addTerminalLine('output', `[${activeConnection?.username || 'user'}@${activeConnection?.host.split('.')[0] || 'server'} ~]$ `)
      setCurrentInput('')
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Terminal className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-xl font-bold">SSH Terminal</h1>
                <p className="text-sm text-muted-foreground">Remote Connection Manager</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon">
                <History className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <Settings className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Connection Form & Sessions */}
          <div className="lg:col-span-1 space-y-6">
            {/* New Connection Card */}
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  New Connection
                </CardTitle>
                <CardDescription>Enter SSH connection details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Host</label>
                  <Input
                    placeholder="192.168.1.100 or hostname"
                    value={formData.host}
                    onChange={e => setFormData(prev => ({ ...prev, host: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Port</label>
                  <Input
                    type="number"
                    placeholder="22"
                    value={formData.port}
                    onChange={e => setFormData(prev => ({ ...prev, port: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Username</label>
                  <Input
                    placeholder="root"
                    value={formData.username}
                    onChange={e => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">Password</label>
                  <Input
                    type="password"
                    placeholder="Enter password"
                    value={formData.password}
                    onChange={e => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  />
                </div>
                <Button
                  className="w-full"
                  onClick={handleConnect}
                  disabled={isConnecting}
                >
                  {isConnecting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Server className="mr-2 h-4 w-4" />
                      Connect
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Active Sessions */}
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">Active Sessions</CardTitle>
                <CardDescription>
                  {connections.length} connection{connections.length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {connections.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No active connections
                  </p>
                ) : (
                  <div className="space-y-2">
                    {connections.map(conn => (
                      <div
                        key={conn.id}
                        className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${
                          activeConnectionId === conn.id
                            ? 'border-primary bg-primary/5'
                            : 'hover:bg-muted/50'
                        }`}
                        onClick={() => setActiveConnectionId(conn.id)}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${
                            conn.status === 'connected' ? 'bg-green-500' : 'bg-gray-400'
                          }`} />
                          <div>
                            <p className="text-sm font-medium">{conn.username}@{conn.host}</p>
                            <p className="text-xs text-muted-foreground">:{conn.port}</p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={e => {
                            e.stopPropagation()
                            handleDisconnect(conn.id)
                          }}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Main Terminal Area */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-200px)] flex flex-col">
              <CardHeader className="pb-2 border-b">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Terminal className="h-5 w-5" />
                    <CardTitle className="text-lg">
                      {activeConnection
                        ? `${activeConnection.username}@${activeConnection.host}`
                        : 'Terminal'}
                    </CardTitle>
                  </div>
                  {activeConnection && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">
                        Connected: {activeConnection.connectedAt?.toLocaleTimeString()}
                      </span>
                      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="flex-1 p-0 flex flex-col">
                {/* Terminal Output */}
                <div
                  ref={terminalRef}
                  className="flex-1 bg-zinc-900 text-green-400 font-mono text-sm p-4 overflow-y-auto"
                >
                  {!activeConnection ? (
                    <div className="text-zinc-500">
                      <p>Welcome to SSH Terminal</p>
                      <p>Enter connection details and click "Connect" to start a session.</p>
                    </div>
                  ) : (
                    terminalLines.map((line, index) => (
                      <div
                        key={index}
                        className={`whitespace-pre-wrap ${
                          line.type === 'error'
                            ? 'text-red-400'
                            : line.type === 'system'
                            ? 'text-yellow-400'
                            : line.type === 'input'
                            ? 'text-cyan-400'
                            : 'text-green-400'
                        }`}
                      >
                        {line.content}
                      </div>
                    ))
                  )}
                </div>

                {/* Terminal Input */}
                {activeConnection && (
                  <div className="border-t bg-zinc-800 p-2">
                    <div className="flex items-center gap-2">
                      <span className="text-green-400 font-mono text-sm">$</span>
                      <input
                        type="text"
                        value={currentInput}
                        onChange={e => setCurrentInput(e.target.value)}
                        onKeyDown={handleTerminalInput}
                        className="flex-1 bg-transparent text-green-400 font-mono text-sm outline-none"
                        placeholder="Enter command..."
                        autoFocus
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
