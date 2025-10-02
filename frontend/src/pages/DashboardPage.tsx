import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '../stores/authStore'
import { studentsApi, riskApi } from '../lib/api'
import { 
  AcademicCapIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon,
  ClockIcon 
} from '@heroicons/react/24/outline'

const DashboardPage = () => {
  const { user } = useAuthStore()

  // Student dashboard data
  const { data: studentProfile, isLoading: profileLoading } = useQuery({
    queryKey: ['student-profile'],
    queryFn: studentsApi.getMyProfile,
    enabled: user?.role === 'student',
  })

  // Risk dashboard summary for teachers/admins
  const { data: riskSummary, isLoading: riskLoading } = useQuery({
    queryKey: ['risk-summary'],
    queryFn: riskApi.getDashboardSummary,
    enabled: user?.role !== 'student',
  })

  if (user?.role === 'student') {
    return <StudentDashboard profile={studentProfile} isLoading={profileLoading} />
  }

  return <TeacherDashboard riskSummary={riskSummary} isLoading={riskLoading} />
}

const StudentDashboard = ({ profile, isLoading }: any) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="loading-spinner" />
      </div>
    )
  }

  const riskColor = profile?.current_risk_score?.risk_level === 'red' ? 'text-red-600' :
                   profile?.current_risk_score?.risk_level === 'amber' ? 'text-yellow-600' : 'text-green-600'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Welcome back, {profile?.user?.full_name}!</h1>
        <p className="text-gray-600">Here's your academic overview</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <AcademicCapIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Submissions</p>
              <p className="text-2xl font-bold text-gray-900">
                {profile?.recent_submissions?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Attendance</p>
              <p className="text-2xl font-bold text-gray-900">
                {profile?.recent_attendance?.filter((a: any) => a.present).length || 0}/
                {profile?.recent_attendance?.length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className={`h-8 w-8 ${riskColor}`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Risk Level</p>
              <p className={`text-2xl font-bold capitalize ${riskColor}`}>
                {profile?.current_risk_score?.risk_level || 'Unknown'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pending Fees</p>
              <p className="text-2xl font-bold text-gray-900">
                {profile?.pending_fees?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Submissions */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Submissions</h3>
          <div className="space-y-3">
            {profile?.recent_submissions?.slice(0, 5).map((submission: any) => (
              <div key={submission.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{submission.file_name}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(submission.submitted_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  {submission.grade ? (
                    <span className="text-sm font-medium text-green-600">
                      {submission.grade}%
                    </span>
                  ) : (
                    <span className="text-xs text-gray-500">Pending</span>
                  )}
                </div>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No recent submissions</p>
            )}
          </div>
        </div>

        {/* Recent Tests */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Test Scores</h3>
          <div className="space-y-3">
            {profile?.recent_tests?.slice(0, 5).map((test: any) => (
              <div key={test.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{test.test_name}</p>
                  <p className="text-xs text-gray-500">{test.subject}</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-900">
                    {test.score}/{test.max_score}
                  </span>
                  <p className="text-xs text-gray-500">
                    {Math.round((test.score / test.max_score) * 100)}%
                  </p>
                </div>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No recent tests</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const TeacherDashboard = ({ riskSummary, isLoading }: any) => {
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
        <h1 className="text-2xl font-bold text-gray-900">Risk Dashboard</h1>
        <p className="text-gray-600">Monitor student risk levels and take action</p>
      </div>

      {/* Risk Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-green-50 border-green-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-500 rounded-full" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-green-800">Low Risk</p>
              <p className="text-2xl font-bold text-green-900">
                {riskSummary?.risk_counts?.green || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-yellow-50 border-yellow-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-500 rounded-full" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-yellow-800">Medium Risk</p>
              <p className="text-2xl font-bold text-yellow-900">
                {riskSummary?.risk_counts?.amber || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-red-500 rounded-full" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-red-800">High Risk</p>
              <p className="text-2xl font-bold text-red-900">
                {riskSummary?.risk_counts?.red || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* High Risk Students */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">High Risk Students</h3>
        <div className="space-y-3">
          {riskSummary?.high_risk_students?.map((student: any) => (
            <div key={student.student_id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
              <div>
                <p className="text-sm font-medium text-gray-900">{student.student_name}</p>
                <p className="text-xs text-gray-500">
                  Score: {student.overall_score?.toFixed(2)} | 
                  Updated: {new Date(student.calculated_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="badge-red">High Risk</span>
              </div>
            </div>
          )) || (
            <p className="text-sm text-gray-500">No high-risk students at this time</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage