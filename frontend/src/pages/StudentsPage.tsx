import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { 
  MagnifyingGlassIcon, 
  UserIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'
import { studentsApi } from '../lib/api'

const StudentsPage = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRisk, setSelectedRisk] = useState<string>('')

  const { data: students, isLoading } = useQuery({
    queryKey: ['students'],
    queryFn: studentsApi.getStudents,
  })

  const filteredStudents = students?.filter((student: any) => {
    const matchesSearch = student.user?.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.student_id?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRisk = !selectedRisk || student.current_risk_score?.risk_level === selectedRisk
    return matchesSearch && matchesRisk
  })

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'red': return 'text-red-600 bg-red-100'
      case 'amber': return 'text-yellow-600 bg-yellow-100'
      case 'green': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Students</h1>
        <p className="text-gray-600">Monitor and manage student profiles</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
        
        <div className="sm:w-48">
          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
            className="input"
          >
            <option value="">All Risk Levels</option>
            <option value="green">Low Risk</option>
            <option value="amber">Medium Risk</option>
            <option value="red">High Risk</option>
          </select>
        </div>
      </div>

      {/* Students Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredStudents?.map((student: any) => (
          <Link
            key={student.id}
            to={`/students/${student.user_id}`}
            className="card hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <UserIcon className="h-6 w-6 text-primary-600" />
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">
                    {student.user?.full_name}
                  </h3>
                  <p className="text-sm text-gray-500">ID: {student.student_id}</p>
                  <p className="text-sm text-gray-500">Class: {student.class_name}</p>
                </div>
              </div>
              
              <div className="flex flex-col items-end space-y-2">
                {student.current_risk_score && (
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(student.current_risk_score.risk_level)}`}>
                    {student.current_risk_score.risk_level === 'red' && <ExclamationTriangleIcon className="h-3 w-3 mr-1" />}
                    {student.current_risk_score.risk_level.charAt(0).toUpperCase() + student.current_risk_score.risk_level.slice(1)} Risk
                  </span>
                )}
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mt-4 grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {student.recent_attendance?.filter((a: any) => a.present).length || 0}
                </p>
                <p className="text-xs text-gray-500">Attendance</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {student.recent_tests?.length || 0}
                </p>
                <p className="text-xs text-gray-500">Tests</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {student.pending_fees?.length || 0}
                </p>
                <p className="text-xs text-gray-500">Pending Fees</p>
              </div>
            </div>
          </Link>
        )) || (
          <div className="col-span-full text-center py-12">
            <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No students found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || selectedRisk ? 'Try adjusting your filters' : 'No students have been added yet'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default StudentsPage