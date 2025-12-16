'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { courses, students } from '@/lib/api'
import { Plus, Trash2, Loader2, Search, Users, UserPlus } from 'lucide-react'

export default function CoursesPage() {
  const [coursesList, setCoursesList] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEnrollModal, setShowEnrollModal] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [allStudents, setAllStudents] = useState<any[]>([])
  const [enrolledStudents, setEnrolledStudents] = useState<string[]>([])
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    instructor: '',
    department: '',
  })

  useEffect(() => {
    fetchCourses()
    fetchAllStudents()
  }, [])

  const fetchCourses = async () => {
    try {
      const response = await courses.getAll()
      setCoursesList(response.courses || [])
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAllStudents = async () => {
    try {
      const response = await students.getAll()
      setAllStudents(response.students || [])
    } catch (error) {
      console.error('Failed to fetch students:', error)
    }
  }

  const handleAddCourse = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await courses.create({
        id: formData.code,
        code: formData.code,
        name: formData.name,
        instructor: formData.instructor,
        department: formData.department,
      })
      setShowAddModal(false)
      setFormData({ code: '', name: '', instructor: '', department: '' })
      fetchCourses()
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  const handleDeleteCourse = async (id: string) => {
    if (!confirm(`Delete course ${id}?`)) return
    try {
      await courses.delete(id)
      fetchCourses()
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  const openEnrollModal = async (course: any) => {
    setSelectedCourse(course)
    setShowEnrollModal(true)

    // Fetch enrolled students
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/courses/${course.id}/students`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setEnrolledStudents(data.student_ids || [])
      }
    } catch (error) {
      console.error('Failed to fetch enrollments:', error)
    }
  }

  const handleEnrollStudent = async (studentId: string) => {
    if (!selectedCourse) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/courses/${selectedCourse.id}/enroll`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ student_id: studentId })
      })

      if (response.ok) {
        setEnrolledStudents([...enrolledStudents, studentId])
        alert(`Student ${studentId} enrolled successfully!`)
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to enroll student')
      }
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  const handleUnenrollStudent = async (studentId: string) => {
    if (!selectedCourse) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/courses/${selectedCourse.id}/unenroll`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ student_id: studentId })
      })

      if (response.ok) {
        setEnrolledStudents(enrolledStudents.filter(id => id !== studentId))
        alert(`Student ${studentId} unenrolled successfully!`)
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to unenroll student')
      }
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  const filteredCourses = coursesList.filter(
    (course) =>
      course.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.instructor?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Courses Management</h1>
          <p className="text-muted-foreground mt-1">Manage course offerings and enrollments</p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Course
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search courses..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : filteredCourses.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">No courses found</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">Course Code</th>
                    <th className="text-left p-4 font-semibold">Course Name</th>
                    <th className="text-left p-4 font-semibold">Instructor</th>
                    <th className="text-left p-4 font-semibold">Department</th>
                    <th className="text-left p-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCourses.map((course) => (
                    <tr key={course.id} className="border-b hover:bg-accent/50">
                      <td className="p-4 font-medium">{course.code}</td>
                      <td className="p-4">{course.name}</td>
                      <td className="p-4 text-sm">{course.instructor || 'N/A'}</td>
                      <td className="p-4">
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          {course.department || 'N/A'}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openEnrollModal(course)}
                          >
                            <Users className="w-4 h-4 mr-1" />
                            Manage Students
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeleteCourse(course.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add Course Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <h2 className="text-xl font-bold">Add New Course</h2>
              <p className="text-sm text-muted-foreground">Enter course information</p>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddCourse} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="courseCode">Course Code</Label>
                  <Input
                    id="courseCode"
                    required
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    placeholder="e.g., CS101"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="courseName">Course Name</Label>
                  <Input
                    id="courseName"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., Introduction to Programming"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="instructor">Instructor</Label>
                  <Input
                    id="instructor"
                    value={formData.instructor}
                    onChange={(e) => setFormData({ ...formData, instructor: e.target.value })}
                    placeholder="e.g., Dr. Sarah Ahmed"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    placeholder="e.g., Computer Science"
                  />
                </div>
                <div className="flex gap-2 pt-4">
                  <Button type="submit" className="flex-1">
                    Add Course
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowAddModal(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Enroll Students Modal */}
      {showEnrollModal && selectedCourse && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 overflow-y-auto">
          <Card className="w-full max-w-2xl my-8">
            <CardHeader>
              <h2 className="text-xl font-bold">Manage Students - {selectedCourse.code}</h2>
              <p className="text-sm text-muted-foreground">{selectedCourse.name}</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                <p className="font-semibold">
                  Enrolled Students: {enrolledStudents.length}
                </p>
                {allStudents.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    No students available. Please add students first.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {allStudents.map((student) => {
                      const studentId = student.id || student.student_id
                      const isEnrolled = enrolledStudents.includes(studentId)
                      return (
                        <div
                          key={studentId}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div>
                            <p className="font-medium">{student.name}</p>
                            <p className="text-sm text-muted-foreground">{studentId}</p>
                          </div>
                          {isEnrolled ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleUnenrollStudent(studentId)}
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Remove
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleEnrollStudent(studentId)}
                            >
                              <UserPlus className="w-4 h-4 mr-1" />
                              Enroll
                            </Button>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
              <div className="flex justify-end gap-2 pt-4 mt-4 border-t">
                <Button onClick={() => setShowEnrollModal(false)}>
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
