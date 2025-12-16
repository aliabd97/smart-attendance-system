'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FileText, Download, Loader2 } from 'lucide-react'
import { courses } from '@/lib/api'

export default function BubbleSheetsPage() {
  const [coursesList, setCoursesList] = useState<any[]>([])
  const [generatedFiles, setGeneratedFiles] = useState<any[]>([])
  const [formData, setFormData] = useState({
    courseId: '',
    lectureId: '',
    date: '',
  })
  const [generating, setGenerating] = useState(false)
  const [loadingCourses, setLoadingCourses] = useState(true)

  useEffect(() => {
    fetchCourses()
    fetchGeneratedFiles()
  }, [])

  const fetchCourses = async () => {
    try {
      const response = await courses.getAll()
      setCoursesList(response.courses || [])
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    } finally {
      setLoadingCourses(false)
    }
  }

  const fetchGeneratedFiles = async () => {
    try {
      const response = await fetch('http://localhost:5003/api/sheets')
      if (response.ok) {
        const data = await response.json()
        setGeneratedFiles(data.sheets || [])
      }
    } catch (error) {
      console.error('Failed to fetch generated files:', error)
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setGenerating(true)

    try {
      const token = localStorage.getItem('token')
      if (!token) throw new Error('Not authenticated')

      // Fetch course data
      const courseResponse = await fetch(`/api/courses/${formData.courseId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!courseResponse.ok) throw new Error('Course not found')
      const courseData = await courseResponse.json()

      // Fetch students enrolled in the course
      const studentsResponse = await fetch(`/api/courses/${formData.courseId}/students`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (!studentsResponse.ok) throw new Error('Failed to fetch students')
      const enrollmentData = await studentsResponse.json()

      // Get student IDs from enrollments
      const studentIds = enrollmentData.student_ids || []

      if (studentIds.length === 0) {
        throw new Error('No students enrolled in this course. Please enroll students first.')
      }

      // Fetch full student data for each student
      const studentsPromises = studentIds.map((studentId: string) =>
        fetch(`/api/students/${studentId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(res => res.json())
      )

      const studentsFullData = await Promise.all(studentsPromises)

      // Prepare request body
      const requestBody = {
        course_id: courseData.id,
        course_name: courseData.name,
        department: courseData.department || 'N/A',
        date: formData.date,
        lecture_number: formData.lectureId,
        students: studentsFullData.map((s: any) => ({
          id: s.id || s.student_id,
          name: s.name || `Student ${s.id || s.student_id}`
        }))
      }

      // Generate bubble sheet (direct call to port 5003)
      const response = await fetch('http://localhost:5003/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to generate bubble sheet')
      }

      const result = await response.json()

      // Download the generated PDF
      window.open(`http://localhost:5003/api/download/${result.lecture_id}`, '_blank')

      alert(`Success! Bubble sheet generated.\nLecture ID: ${result.lecture_id}\nStudents: ${result.total_students}\nPages: ${result.total_pages}`)

      // Reset form
      setFormData({ courseId: '', lectureId: '', date: '' })

      // Refresh generated files list
      fetchGeneratedFiles()
    } catch (error: any) {
      alert('Error: ' + error.message)
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = (lectureId: string) => {
    window.open(`http://localhost:5003/api/download/${lectureId}`, '_blank')
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Bubble Sheets Generator</h1>
        <p className="text-muted-foreground mt-1">
          Generate OMR attendance bubble sheets with QR codes
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Generate Bubble Sheet</CardTitle>
            <CardDescription>Create attendance sheet for a lecture</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div className="space-y-2">
                <Label>Course</Label>
                {loadingCourses ? (
                  <div className="flex items-center gap-2 px-3 py-2 border rounded-md">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm text-muted-foreground">Loading courses...</span>
                  </div>
                ) : (
                  <select
                    required
                    value={formData.courseId}
                    onChange={(e) => setFormData({ ...formData, courseId: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">-- Select Course --</option>
                    {coursesList.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.code} - {course.name}
                      </option>
                    ))}
                  </select>
                )}
              </div>
              <div className="space-y-2">
                <Label>Lecture ID</Label>
                <Input
                  required
                  value={formData.lectureId}
                  onChange={(e) => setFormData({ ...formData, lectureId: e.target.value })}
                  placeholder="e.g., L001"
                />
              </div>
              <div className="space-y-2">
                <Label>Date</Label>
                <Input
                  type="date"
                  required
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                />
              </div>
              <Button type="submit" className="w-full" disabled={generating}>
                <FileText className="w-4 h-4 mr-2" />
                {generating ? 'Generating...' : 'Generate PDF'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>⚠️ Important: Course Setup Required</CardTitle>
            <CardDescription>Before generating bubble sheets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="font-semibold text-yellow-900">Prerequisites:</p>
              <ol className="text-sm text-yellow-800 space-y-1 list-decimal list-inside">
                <li>Add students to the system (Dashboard → Students)</li>
                <li>Create the course (Dashboard → Courses)</li>
                <li><strong>Enroll students in the course</strong> (Dashboard → Enrollments)</li>
              </ol>
              <p className="text-xs text-yellow-700 mt-2">
                Without enrolled students, bubble sheet generation will fail!
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Features</CardTitle>
            <CardDescription>What's included in the bubble sheet</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium">QR Code Integration</p>
                  <p className="text-sm text-muted-foreground">
                    Each sheet contains lecture metadata in QR code
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium">Student ID Bubbles</p>
                  <p className="text-sm text-muted-foreground">
                    Students mark their ID number
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium">Attendance Bubbles</p>
                  <p className="text-sm text-muted-foreground">
                    Present/Absent marking options
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium">Calibration Points</p>
                  <p className="text-sm text-muted-foreground">
                    For accurate OMR detection
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div>
                  <p className="font-medium">Print-Ready PDF</p>
                  <p className="text-sm text-muted-foreground">
                    Optimized for A4 paper printing
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Generated Sheets History</CardTitle>
          <CardDescription>Previously generated bubble sheets</CardDescription>
        </CardHeader>
        <CardContent>
          {generatedFiles.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No sheets generated yet
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">Lecture ID</th>
                    <th className="text-left p-4 font-semibold">Course</th>
                    <th className="text-left p-4 font-semibold">Date</th>
                    <th className="text-left p-4 font-semibold">Students</th>
                    <th className="text-left p-4 font-semibold">Pages</th>
                    <th className="text-left p-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {generatedFiles.map((file) => (
                    <tr key={file.lecture_id} className="border-b hover:bg-accent/50">
                      <td className="p-4 font-medium">{file.lecture_id}</td>
                      <td className="p-4">{file.course_name}</td>
                      <td className="p-4">{file.date}</td>
                      <td className="p-4">{file.total_students}</td>
                      <td className="p-4">{file.total_pages}</td>
                      <td className="p-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDownload(file.lecture_id)}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
