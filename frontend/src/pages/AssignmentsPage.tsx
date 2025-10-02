import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { PlusIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline'
import { useAuthStore } from '../stores/authStore'
import { assignmentsApi, ocrApi } from '../lib/api'

const assignmentSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  class_name: z.string().min(1, 'Class name is required'),
  due_date: z.string().optional(),
})

type AssignmentForm = z.infer<typeof assignmentSchema>

const AssignmentsPage = () => {
  const { user } = useAuthStore()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [submissionAssignmentId, setSubmissionAssignmentId] = useState<number | null>(null)
  const [quizResults, setQuizResults] = useState<any>(null)
  
  const queryClient = useQueryClient()

  const { data: assignments, isLoading } = useQuery({
    queryKey: ['assignments'],
    queryFn: assignmentsApi.getAssignments,
  })

  const createMutation = useMutation({
    mutationFn: assignmentsApi.createAssignment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
      setShowCreateForm(false)
      toast.success('Assignment created successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create assignment')
    },
  })

  const submitMutation = useMutation({
    mutationFn: ({ assignmentId, file }: { assignmentId: number; file: File }) =>
      assignmentsApi.submitAssignment(assignmentId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assignments'] })
      setSelectedFile(null)
      setSubmissionAssignmentId(null)
      toast.success('Assignment submitted successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to submit assignment')
    },
  })

  const ocrMutation = useMutation({
    mutationFn: ocrApi.processImageToQuiz,
    onSuccess: (data) => {
      setQuizResults(data)
      toast.success('Quiz generated successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to process image')
    },
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AssignmentForm>({
    resolver: zodResolver(assignmentSchema),
  })

  const onCreateSubmit = (data: AssignmentForm) => {
    createMutation.mutate(data)
    reset()
  }

  const handleFileSubmission = (assignmentId: number) => {
    if (!selectedFile) {
      toast.error('Please select a file')
      return
    }
    submitMutation.mutate({ assignmentId, file: selectedFile })
  }

  const handleOCRProcessing = () => {
    if (!selectedFile) {
      toast.error('Please select an image file')
      return
    }
    ocrMutation.mutate(selectedFile)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="loading-spinner" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Assignments</h1>
          <p className="text-gray-600">
            {user?.role === 'student' ? 'View and submit your assignments' : 'Manage class assignments'}
          </p>
        </div>
        {user?.role !== 'student' && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Assignment
          </button>
        )}
      </div>

      {/* Create Assignment Form */}
      {showCreateForm && user?.role !== 'student' && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Assignment</h3>
          <form onSubmit={handleSubmit(onCreateSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Title</label>
              <input
                {...register('title')}
                className="input mt-1"
                placeholder="Assignment title"
              />
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                {...register('description')}
                rows={3}
                className="input mt-1"
                placeholder="Assignment description"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Class</label>
              <input
                {...register('class_name')}
                className="input mt-1"
                placeholder="Class name"
              />
              {errors.class_name && (
                <p className="mt-1 text-sm text-red-600">{errors.class_name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Due Date</label>
              <input
                {...register('due_date')}
                type="datetime-local"
                className="input mt-1"
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="btn-primary"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Assignment'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* OCR & Quiz Generator */}
      {user?.role === 'student' && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">AI Study Helper</h3>
          <p className="text-sm text-gray-600 mb-4">
            Upload an image of your notes to generate practice quiz questions
          </p>
          
          <div className="space-y-4">
            <div>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
            </div>
            
            <button
              onClick={handleOCRProcessing}
              disabled={!selectedFile || ocrMutation.isPending}
              className="btn-primary"
            >
              {ocrMutation.isPending ? 'Processing...' : 'Generate Quiz'}
            </button>
          </div>

          {/* Quiz Results */}
          {quizResults && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-3">Generated Quiz Questions</h4>
              <div className="space-y-4">
                {quizResults.questions?.map((question: any, index: number) => (
                  <div key={index} className="bg-white p-4 rounded-md">
                    <p className="font-medium text-gray-900 mb-2">
                      {index + 1}. {question.question}
                    </p>
                    <div className="space-y-1">
                      {question.options?.map((option: string, optIndex: number) => (
                        <p key={optIndex} className="text-sm text-gray-700">{option}</p>
                      ))}
                    </div>
                    <p className="text-sm text-green-600 mt-2">
                      Correct: {question.correct_answer}
                    </p>
                    {question.explanation && (
                      <p className="text-sm text-gray-600 mt-1">{question.explanation}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Assignments List */}
      <div className="grid gap-6">
        {assignments?.map((assignment: any) => (
          <div key={assignment.id} className="card">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900">{assignment.title}</h3>
                {assignment.description && (
                  <p className="text-gray-600 mt-1">{assignment.description}</p>
                )}
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span>Class: {assignment.class_name}</span>
                  {assignment.due_date && (
                    <span>Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                  )}
                </div>
              </div>

              {user?.role === 'student' && (
                <div className="ml-4">
                  {submissionAssignmentId === assignment.id ? (
                    <div className="space-y-2">
                      <input
                        type="file"
                        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                        className="block w-full text-sm text-gray-500"
                      />
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleFileSubmission(assignment.id)}
                          disabled={!selectedFile || submitMutation.isPending}
                          className="btn-primary text-sm"
                        >
                          {submitMutation.isPending ? 'Submitting...' : 'Submit'}
                        </button>
                        <button
                          onClick={() => {
                            setSubmissionAssignmentId(null)
                            setSelectedFile(null)
                          }}
                          className="btn-secondary text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setSubmissionAssignmentId(assignment.id)}
                      className="btn-primary"
                    >
                      <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
                      Submit
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        )) || (
          <div className="text-center py-12">
            <p className="text-gray-500">No assignments found</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AssignmentsPage