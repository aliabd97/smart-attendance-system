'use client'

import { useEffect, useRef } from 'react'
import { Chart, ChartConfiguration, registerables } from 'chart.js'

Chart.register(...registerables)

interface AttendanceChartProps {
  data: {
    labels: string[]
    present: number[]
    absent: number[]
  }
}

export function AttendanceChart({ data }: AttendanceChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null)
  const chartInstance = useRef<Chart | null>(null)

  useEffect(() => {
    if (!chartRef.current) return

    // Destroy previous chart instance
    if (chartInstance.current) {
      chartInstance.current.destroy()
    }

    const ctx = chartRef.current.getContext('2d')
    if (!ctx) return

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Present',
            data: data.present,
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'Absent',
            data: data.absent,
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Attendance Trends',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    }

    chartInstance.current = new Chart(ctx, config)

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy()
      }
    }
  }, [data])

  return (
    <div className="w-full h-[300px]">
      <canvas ref={chartRef} />
    </div>
  )
}
