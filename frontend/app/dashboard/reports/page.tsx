'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { FileSpreadsheet, FileText, Download, Table } from 'lucide-react'

export default function ReportsPage() {
  const [excelForm, setExcelForm] = useState({ courseId: '', startDate: '', endDate: '' })
  const [pdfForm, setPdfForm] = useState({ courseId: '', startDate: '', endDate: '' })
  const [csvForm, setCsvForm] = useState({ courseId: '', startDate: '', endDate: '' })
  const [excelLoading, setExcelLoading] = useState(false)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [csvLoading, setCsvLoading] = useState(false)

  const handleExcelReport = async () => {
    if (!excelForm.courseId) {
      alert('Please enter Course ID')
      return
    }

    setExcelLoading(true)
    try {
      // Call reporting service (port 5009)
      const url = `http://localhost:5009/api/reports/course/${excelForm.courseId}?format=excel`
      window.open(url, '_blank')

      alert('Excel report is being generated and downloaded!')
    } catch (error: any) {
      alert('Error: ' + error.message)
    } finally {
      setExcelLoading(false)
    }
  }

  const handlePdfReport = async () => {
    if (!pdfForm.courseId) {
      alert('Please enter Course ID')
      return
    }

    setPdfLoading(true)
    try {
      // Call reporting service (port 5009)
      const url = `http://localhost:5009/api/reports/course/${pdfForm.courseId}?format=pdf`
      window.open(url, '_blank')

      alert('PDF report is being generated and downloaded!')
    } catch (error: any) {
      alert('Error: ' + error.message)
    } finally {
      setPdfLoading(false)
    }
  }

  const handleCsvReport = async () => {
    if (!csvForm.courseId) {
      alert('Please enter Course ID')
      return
    }

    setCsvLoading(true)
    try {
      // Strategy Pattern + Reflection: CSV format!
      const url = `http://localhost:5009/api/reports/course/${csvForm.courseId}?format=csv`
      window.open(url, '_blank')

      alert('CSV report is being generated and downloaded!')
    } catch (error: any) {
      alert('Error: ' + error.message)
    } finally {
      setCsvLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reports & Export</h1>
        <p className="text-muted-foreground mt-1">
          Generate and export attendance reports
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5 text-green-600" />
              Excel Report
            </CardTitle>
            <CardDescription>Export attendance data to Excel format</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Course ID</Label>
              <Input
                placeholder="e.g., CS101"
                value={excelForm.courseId}
                onChange={(e) => setExcelForm({ ...excelForm, courseId: e.target.value })}
              />
            </div>
            <Button
              className="w-full"
              onClick={handleExcelReport}
              disabled={excelLoading}
            >
              <Download className="w-4 h-4 mr-2" />
              {excelLoading ? 'Generating...' : 'Generate Excel Report'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-red-600" />
              PDF Report
            </CardTitle>
            <CardDescription>Export attendance report as PDF</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Course ID</Label>
              <Input
                placeholder="e.g., CS101"
                value={pdfForm.courseId}
                onChange={(e) => setPdfForm({ ...pdfForm, courseId: e.target.value })}
              />
            </div>
            <Button
              className="w-full"
              onClick={handlePdfReport}
              disabled={pdfLoading}
            >
              <Download className="w-4 h-4 mr-2" />
              {pdfLoading ? 'Generating...' : 'Generate PDF Report'}
            </Button>
          </CardContent>
        </Card>

        <Card className="border-2 border-primary/20 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Table className="w-5 h-5 text-blue-600" />
              CSV Report
              <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">New!</span>
            </CardTitle>
            <CardDescription>Export as CSV (Strategy Pattern Demo)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Course ID</Label>
              <Input
                placeholder="e.g., CS101"
                value={csvForm.courseId}
                onChange={(e) => setCsvForm({ ...csvForm, courseId: e.target.value })}
              />
            </div>
            <Button
              className="w-full"
              onClick={handleCsvReport}
              disabled={csvLoading}
            >
              <Download className="w-4 h-4 mr-2" />
              {csvLoading ? 'Generating...' : 'Generate CSV Report'}
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Report Contents</CardTitle>
          <CardDescription>What's included in the reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="font-semibold">Excel Report Features:</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Student attendance percentage per course
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Detailed attendance records by date
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Summary statistics and charts
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Exportable to Excel/CSV format
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Ready for further analysis
                </li>
              </ul>
            </div>
            <div className="space-y-3">
              <h3 className="font-semibold">PDF Report Features:</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Professional formatting
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  University branding and headers
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Attendance summary tables
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Print-ready format
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Shareable and archivable
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
