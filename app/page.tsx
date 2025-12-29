'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function Home() {
  const [randomNumber, setRandomNumber] = useState<number | null>(null)
  const [minValue, setMinValue] = useState<number>(1)
  const [maxValue, setMaxValue] = useState<number>(100)
  const [isAnimating, setIsAnimating] = useState(false)

  const generateRandomNumber = () => {
    setIsAnimating(true)
    
    let counter = 0
    const interval = setInterval(() => {
      const temp = Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue
      setRandomNumber(temp)
      counter++
      
      if (counter >= 20) {
        clearInterval(interval)
        setIsAnimating(false)
        const finalNumber = Math.floor(Math.random() * (maxValue - minValue + 1)) + minValue
        setRandomNumber(finalNumber)
      }
    }, 50)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Random Number Generator
          </CardTitle>
          <CardDescription>
            Generate random numbers within your specified range
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-center h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg">
            <div className={`text-6xl font-bold ${isAnimating ? 'text-gray-400' : 'bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent'} transition-colors`}>
              {randomNumber !== null ? randomNumber : '?'}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Min Value</label>
              <input
                type="number"
                value={minValue}
                onChange={(e) => setMinValue(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isAnimating}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Max Value</label>
              <input
                type="number"
                value={maxValue}
                onChange={(e) => setMaxValue(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isAnimating}
              />
            </div>
          </div>

          <Button 
            onClick={generateRandomNumber} 
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-6 text-lg"
            disabled={isAnimating || minValue >= maxValue}
          >
            {isAnimating ? 'Generating...' : 'Generate Random Number'}
          </Button>

          {minValue >= maxValue && (
            <p className="text-sm text-red-500 text-center">
              Min value must be less than max value
            </p>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
