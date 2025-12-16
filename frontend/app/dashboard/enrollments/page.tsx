'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { enrollments, students, courses } from '@/lib/api'
import { Plus, Trash2, Loader2, UserPlus } from 'lucide-react'

export default function EnrollmentsPage() {
  const [enrollmentsList, setEnrollmentsList] = useState<any[]>([])
  const [studentsList, setStudentsList] = useState<any[]>([])
  const [coursesList, setCoursesList] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [formData, setFormData] = useState({
    studentId: '',
    courseId: '',
  })

  useEffect(() => {
    fetchEnrollments()
    fetchStudents()
    fetchCourses()
  }, [])

  const fetchEnrollments = async () => {
    try {
      const data = await enrollments.getAll()
      setEnrollmentsList(data || [])
    } catch (error) {
      console.error('Failed to fetch enrollments:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStudents = async () => {
    try {
      const response = await students.getAll()
      setStudentsList(response.students || [])
    } catch (error) {
      console.error('Failed to fetch students:', error)
    }
  }

  const fetchCourses = async () => {
    try {
      const response = await courses.getAll()
      setCoursesList(response.courses || [])
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    }
  }

  const handleEnroll = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await enrollments.enroll(formData.courseId, formData.studentId)
      setShowAddModal(false)
      setFormData({ studentId: '', courseId: '' })
      fetchEnrollments()
      alert('Student enrolled successfully!')
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  const handleUnenroll = async (courseId: string, studentId: string) => {
    if (!confirm('Remove this enrollment?')) return
    try {
      await enrollments.unenroll(courseId, studentId)
      fetchEnrollments()
      alert('Enrollment removed successfully!')
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Course Enrollments</h1>
          <p className="text-muted-foreground mt-1">
            Manage student course enrollments
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          Enroll Student
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Enrollments</CardTitle>
          <CardDescription>
            View and manage all student course enrollments
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : enrollmentsList.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No enrollments found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">Student ID</th>
                    <th className="text-left p-4 font-semibold">Student Name</th>
                    <th className="text-left p-4 font-semibold">Course Code</th>
                    <th className="text-left p-4 font-semibold">Course Name</th>
                    <th className="text-left p-4 font-semibold">Enrolled Date</th>
                    <th className="text-left p-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {enrollmentsList.map((enrollment, index) => (
                    <tr key={`${enrollment.course_id}-${enrollment.student_id}-${index}`} className="border-b hover:bg-accent/50">
                      <td className="p-4 font-medium">{enrollment.student_id}</td>
                      <td className="p-4">{enrollment.student_name || 'N/A'}</td>
                      <td className="p-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {enrollment.course_id}
                        </span>
                      </td>
                      <td className="p-4">{enrollment.course_name || 'N/A'}</td>
                      <td className="p-4 text-sm text-muted-foreground">
                        {enrollment.enrolled_at
                          ? new Date(enrollment.enrolled_at).toLocaleDateString()
                          : 'N/A'}
                      </td>
                      <td className="p-4">
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() =>
                            handleUnenroll(enrollment.course_id, enrollment.student_id)
                          }
                        >
                          <Trash2 className="w-4 h-4" />
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

      {/* Add Enrollment Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Enroll Student in Course</CardTitle>
              <CardDescription>Select student and course</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleEnroll} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="studentId">Select Student</Label>
                  <select
                    id="studentId"
                    required
                    value={formData.studentId}
                    onChange={(e) => setFormData({ ...formData, studentId: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">-- Select Student --</option>
                    {studentsList.map((student) => (
                      <option key={student.id} value={student.id}>
                        {student.id} - {student.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="courseId">Select Course</Label>
                  <select
                    id="courseId"
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
                </div>
                <div className="flex gap-2 pt-4">
                  <Button type="submit" className="flex-1">
                    Enroll Student
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowAddModal(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
