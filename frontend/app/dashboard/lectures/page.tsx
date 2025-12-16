'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Calendar, Plus, Trash2 } from 'lucide-react'

interface Lecture {
  lecture_id: string
  course_id: string
  date: string
  time: string
  created_at?: string
}

export default function LecturesPage() {
  const [showAddModal, setShowAddModal] = useState(false)
  const [lectures, setLectures] = useState<Lecture[]>([])
  const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState({
    courseId: '',
    lectureId: '',
    date: '',
    time: ''
  })

  const fetchLectures = async () => {
    try {
      // For now, show empty state since we don't have lectures API yet
      setLectures([])
    } catch (error) {
      console.error('Failed to fetch lectures:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLectures()
  }, [])

  const handleAddLecture = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.courseId || !formData.lectureId || !formData.date || !formData.time) {
      alert('Please fill all fields')
      return
    }

    try {
      // Create lecture object
      const newLecture: Lecture = {
        lecture_id: formData.lectureId,
        course_id: formData.courseId,
        date: formData.date,
        time: formData.time,
        created_at: new Date().toISOString()
      }

      // Add to local state (in real app, would call API)
      setLectures([...lectures, newLecture])

      alert(`Lecture ${formData.lectureId} scheduled successfully for ${formData.courseId}!`)

      // Reset form
      setFormData({ courseId: '', lectureId: '', date: '', time: '' })
      setShowAddModal(false)
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  const handleDeleteLecture = async (lectureId: string) => {
    if (!confirm(`Delete lecture ${lectureId}?`)) return

    try {
      setLectures(lectures.filter(l => l.lecture_id !== lectureId))
      alert('Lecture deleted successfully')
    } catch (error: any) {
      alert('Error: ' + error.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Lectures Management</h1>
          <p className="text-muted-foreground mt-1">Schedule and manage lecture sessions</p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Schedule Lecture
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Scheduled Lectures</CardTitle>
          <CardDescription>All scheduled lecture sessions</CardDescription>
        </CardHeader>
        <CardContent>
          {lectures.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Lectures Scheduled</h3>
              <p className="text-muted-foreground mb-4">
                Start by scheduling your first lecture session
              </p>
              <Button onClick={() => setShowAddModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Schedule Lecture
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {lectures.map((lecture) => (
                <div
                  key={lecture.lecture_id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div>
                    <p className="font-semibold">{lecture.lecture_id}</p>
                    <p className="text-sm text-muted-foreground">
                      Course: {lecture.course_id} • Date: {lecture.date} • Time: {lecture.time}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteLecture(lecture.lecture_id)}
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Schedule New Lecture</CardTitle>
              <CardDescription>Enter lecture details</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddLecture} className="space-y-4">
                <div className="space-y-2">
                  <Label>Course ID</Label>
                  <Input
                    required
                    value={formData.courseId}
                    onChange={(e) => setFormData({ ...formData, courseId: e.target.value })}
                    placeholder="e.g., CS101"
                  />
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
                <div className="space-y-2">
                  <Label>Time</Label>
                  <Input
                    type="time"
                    required
                    value={formData.time}
                    onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                  />
                </div>
                <div className="flex gap-2 pt-4">
                  <Button type="submit" className="flex-1">
                    Schedule Lecture
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
    </div>
  )
}
