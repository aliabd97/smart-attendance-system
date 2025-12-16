'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Camera, Upload, CheckCircle } from 'lucide-react'

export default function OMRPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [processing, setProcessing] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleProcess = async () => {
    if (!selectedFile) return
    setProcessing(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('send_to_attendance', 'true')

      // Call OMR processing service (port 5004)
      const response = await fetch('http://localhost:5004/api/process', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to process bubble sheet')
      }

      const result = await response.json()

      alert(
        `OMR Processing Complete!\n\n` +
        `Job ID: ${result.job_id}\n` +
        `Lecture ID: ${result.lecture_id}\n` +
        `Total Students: ${result.total_students}\n` +
        `Present: ${result.present}\n` +
        `Absent: ${result.absent}\n` +
        `Attendance: ${result.attendance_percentage}%\n` +
        `Status: ${result.status}`
      )

      // Reset file selection
      setSelectedFile(null)
    } catch (error: any) {
      alert('Error: ' + error.message)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">OMR Processing</h1>
        <p className="text-muted-foreground mt-1">
          Process scanned bubble sheets using OpenCV
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Upload Scanned Sheet</CardTitle>
            <CardDescription>
              Upload scanned bubble sheet (PDF or image)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
              <Camera className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground mb-4">
                {selectedFile
                  ? `Selected: ${selectedFile.name}`
                  : 'Drag and drop or click to upload'}
              </p>
              <input
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <Button variant="outline" asChild>
                  <span>
                    <Upload className="w-4 h-4 mr-2" />
                    Select File
                  </span>
                </Button>
              </label>
            </div>

            <Button
              className="w-full"
              disabled={!selectedFile || processing}
              onClick={handleProcess}
            >
              {processing ? 'Processing...' : 'Process Bubble Sheet'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processing Pipeline</CardTitle>
            <CardDescription>How OMR processing works</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">1. Image Preprocessing</p>
                  <p className="text-sm text-muted-foreground">
                    Convert to grayscale, threshold, denoise
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">2. QR Code Detection</p>
                  <p className="text-sm text-muted-foreground">
                    Extract lecture metadata from QR code
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">3. Calibration Points</p>
                  <p className="text-sm text-muted-foreground">
                    Detect and align using calibration marks
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">4. Bubble Detection</p>
                  <p className="text-sm text-muted-foreground">
                    Check each bubble for fill percentage (60% threshold)
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">5. Data Extraction</p>
                  <p className="text-sm text-muted-foreground">
                    Extract student ID and attendance status
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">6. Save to Database</p>
                  <p className="text-sm text-muted-foreground">
                    Store attendance records in system
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Processing Results</CardTitle>
          <CardDescription>Results from recent OMR processing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No processing results yet. Upload a scanned sheet to begin.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
