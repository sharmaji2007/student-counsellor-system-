import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  ExclamationTriangleIcon, 
  ArrowPathIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline'
import { riskApi } from '../lib/api'
import toast from 'react-hot-toast'

const RiskDashboardPage = () => {
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: riskSummary, isLoading: summaryLoading } = useQuery({
    queryKey: ['risk-summary'],
    queryFn: riskApi.getDashboardSummary,
  })

  const { data: riskScores, isLoading: scoresLoading } = useQuery({
    queryKey: ['risk-scores', selectedRiskLevel],
    queryFn: () => riskApi.getRiskScores(selectedRiskLevel),
  })

  const calculateAllMutation = useMutation({
    mutationFn: riskApi.calculateAllRiskScores,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['risk-summary'] })
      queryClient.invalidateQueries({ queryKey: ['risk-scores'] })
      toast.success(`Calculated risk scores for ${data.calculated_count} students`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to calculate risk scores')
    },
  })

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'red': return 'text-red-600 bg-red-100 border-red-200'
      case 'amber': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      case 'green': return 'text-green-600 bg-green-100 border-green-200'
      default: return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'red': return <ExclamationTriangleIcon className="h-5 w-5" />
      case 'amber': return <ExclamationTriangleIcon className="h-5 w-5" />
      case 'green': return <ChartBarIcon className="h-5 w-5" />
      default: return <ChartBarIcon className="h-5 w-5" />
    }
  }

  if (summaryLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Risk Dashboard</h1>
          <p className="text-gray-600">Monitor student risk levels and intervention needs</p>
        </div>
        
        <button
          onClick={() => calculateAllMutation.mutate()}
          disabled={calculateAllMutation.isPending}
          className="btn-primary"
        >
          {calculateAllMutation.isPending ? (
            <div className="loading-spinner h-4 w-4 mr-2" />
          ) : (
            <ArrowPathIcon className="h-5 w-5 mr-2" />
          )}
          Recalculate All
        </button>
      </div>

      {/* Risk Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-gray-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Students</p>
              <p className="text-2xl font-bold text-gray-900">
                {riskSummary?.total_students || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-green-50 border-green-200">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <ChartBarIcon className="h-5 w-5 text-white" />
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
            <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-white" />
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
            <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-white" />
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

      {/* Filter */}
      <div className="flex items-center space-x-4">
        <label className="text-sm font-medium text-gray-700">Filter by risk level:</label>
        <select
          value={selectedRiskLevel}
          onChange={(e) => setSelectedRiskLevel(e.target.value)}
          className="input w-48"
        >
          <option value="">All Levels</option>
          <option value="green">Low Risk</option>
          <option value="amber">Medium Risk</option>
          <option value="red">High Risk</option>
        </select>
      </div>

      {/* Risk Scores Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Student Risk Scores</h3>
          {scoresLoading && <div className="loading-spinner" />}
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Overall Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Attendance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Academic
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fees
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Behavior
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {riskScores?.map((score: any) => (
                <tr key={score.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      Student {score.student_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(score.risk_level)}`}>
                      {getRiskIcon(score.risk_level)}
                      <span className="ml-1 capitalize">{score.risk_level}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(score.overall_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(score.attendance_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(score.test_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(score.fee_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(score.chat_score * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(score.calculated_at).toLocaleDateString()}
                  </td>
                </tr>
              )) || (
                <tr>
                  <td colSpan={8} className="px-6 py-4 text-center text-sm text-gray-500">
                    {scoresLoading ? 'Loading...' : 'No risk scores found'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* High Priority Students */}
      {riskSummary?.high_risk_students?.length > 0 && (
        <div className="card bg-red-50 border-red-200">
          <h3 className="text-lg font-medium text-red-900 mb-4 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            Immediate Attention Required
          </h3>
          <div className="space-y-3">
            {riskSummary.high_risk_students.map((student: any) => (
              <div key={student.student_id} className="bg-white p-4 rounded-lg border border-red-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{student.student_name}</p>
                    <p className="text-sm text-gray-600">
                      Risk Score: {(student.overall_score * 100).toFixed(1)}% | 
                      Last Updated: {new Date(student.calculated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span className="badge-red">High Risk</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default RiskDashboardPage