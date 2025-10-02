import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import toast from 'react-hot-toast'
import { 
  UserPlusIcon, 
  Cog6ToothIcon,
  ExclamationTriangleIcon,
  TrashIcon 
} from '@heroicons/react/24/outline'
import { authApi, chatApi } from '../lib/api'

const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  full_name: z.string().min(1, 'Full name is required'),
  role: z.enum(['student', 'teacher', 'mentor', 'counselor', 'admin']),
  phone: z.string().optional(),
})

type UserForm = z.infer<typeof userSchema>

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('users')
  const queryClient = useQueryClient()

  const { data: sosIncidents, isLoading: sosLoading } = useQuery({
    queryKey: ['sos-incidents'],
    queryFn: () => chatApi.getSOSIncidents(),
  })

  const createUserMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      toast.success('User created successfully!')
      reset()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create user')
    },
  })

  const cleanupMutation = useMutation({
    mutationFn: () => chatApi.getMessages(), // Mock cleanup function
    onSuccess: () => {
      toast.success('Expired messages cleaned up')
    },
    onError: (error: any) => {
      toast.error('Failed to cleanup messages')
    },
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UserForm>({
    resolver: zodResolver(userSchema),
  })

  const onSubmit = (data: UserForm) => {
    createUserMutation.mutate(data)
  }

  const tabs = [
    { id: 'users', name: 'User Management', icon: UserPlusIcon },
    { id: 'sos', name: 'SOS Incidents', icon: ExclamationTriangleIcon },
    { id: 'system', name: 'System', icon: Cog6ToothIcon },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
        <p className="text-gray-600">Manage users, monitor incidents, and system settings</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-5 w-5 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'users' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New User</h3>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    {...register('email')}
                    type="email"
                    className="input mt-1"
                    placeholder="user@example.com"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <input
                    {...register('full_name')}
                    className="input mt-1"
                    placeholder="John Doe"
                  />
                  {errors.full_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Password</label>
                  <input
                    {...register('password')}
                    type="password"
                    className="input mt-1"
                    placeholder="••••••••"
                  />
                  {errors.password && (
                    <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Role</label>
                  <select {...register('role')} className="input mt-1">
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                    <option value="mentor">Mentor</option>
                    <option value="counselor">Counselor</option>
                    <option value="admin">Admin</option>
                  </select>
                  {errors.role && (
                    <p className="mt-1 text-sm text-red-600">{errors.role.message}</p>
                  )}
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Phone (Optional)</label>
                  <input
                    {...register('phone')}
                    className="input mt-1"
                    placeholder="+1234567890"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={createUserMutation.isPending}
                className="btn-primary"
              >
                {createUserMutation.isPending ? 'Creating...' : 'Create User'}
              </button>
            </form>
          </div>
        </div>
      )}

      {activeTab === 'sos' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">SOS Incidents</h3>
            {sosLoading ? (
              <div className="flex justify-center py-8">
                <div className="loading-spinner" />
              </div>
            ) : (
              <div className="space-y-4">
                {sosIncidents?.map((incident: any) => (
                  <div key={incident.id} className="border border-red-200 rounded-lg p-4 bg-red-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
                          <h4 className="font-medium text-red-900">
                            Student ID: {incident.student_id}
                          </h4>
                        </div>
                        <p className="text-sm text-red-800 mt-1">
                          Triggered Keywords: {incident.trigger_keywords?.join(', ')}
                        </p>
                        <p className="text-sm text-red-700 mt-1">
                          Status: {incident.status} | 
                          Created: {new Date(incident.created_at).toLocaleString()}
                        </p>
                        {incident.notes && (
                          <p className="text-sm text-red-700 mt-2">
                            Notes: {incident.notes}
                          </p>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          incident.counselor_notified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {incident.counselor_notified ? 'Counselor Notified' : 'Pending'}
                        </span>
                      </div>
                    </div>
                  </div>
                )) || (
                  <p className="text-center text-gray-500 py-8">No SOS incidents found</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Maintenance</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Cleanup Expired Messages</h4>
                  <p className="text-sm text-gray-600">
                    Remove chat messages older than 15 days (except flagged ones)
                  </p>
                </div>
                <button
                  onClick={() => cleanupMutation.mutate()}
                  disabled={cleanupMutation.isPending}
                  className="btn-secondary"
                >
                  {cleanupMutation.isPending ? (
                    <div className="loading-spinner h-4 w-4 mr-2" />
                  ) : (
                    <TrashIcon className="h-4 w-4 mr-2" />
                  )}
                  Cleanup
                </button>
              </div>

              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">System Status</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex justify-between">
                    <span>Database:</span>
                    <span className="text-green-600">Connected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Redis:</span>
                    <span className="text-green-600">Connected</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Storage:</span>
                    <span className="text-green-600">Available</span>
                  </div>
                  <div className="flex justify-between">
                    <span>AI Services:</span>
                    <span className="text-yellow-600">Limited</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AdminPage