import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { PaperAirplaneIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { chatApi } from '../lib/api'
import { useAuthStore } from '../stores/authStore'
import toast from 'react-hot-toast'

interface MessageForm {
  message: string
}

const ChatPage = () => {
  const { user } = useAuthStore()
  const [isPrivateMode, setIsPrivateMode] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  const { data: messages, isLoading } = useQuery({
    queryKey: ['chat-messages'],
    queryFn: () => chatApi.getMessages(50),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const sendMutation = useMutation({
    mutationFn: ({ message, isPrivate }: { message: string; isPrivate: boolean }) =>
      chatApi.sendMessage(message, isPrivate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-messages'] })
      reset()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to send message')
    },
  })

  const { register, handleSubmit, reset, watch } = useForm<MessageForm>()

  const messageValue = watch('message', '')

  const onSubmit = (data: MessageForm) => {
    if (!data.message.trim()) return
    sendMutation.mutate({ message: data.message, isPrivate: isPrivateMode })
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Check for potential safety keywords in real-time
  const checkSafetyKeywords = (text: string) => {
    const safetyKeywords = ['harm myself', 'suicide', 'kill myself', 'hurt myself', 'want to die']
    return safetyKeywords.some(keyword => 
      text.toLowerCase().includes(keyword.toLowerCase())
    )
  }

  const hasSafetyKeywords = checkSafetyKeywords(messageValue)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="loading-spinner" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Private Chat</h1>
          <p className="text-gray-600">Safe space to share your thoughts and concerns</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="private-mode"
              checked={isPrivateMode}
              onChange={(e) => setIsPrivateMode(e.target.checked)}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="private-mode" className="ml-2 text-sm text-gray-700">
              Private Mode (auto-delete in 15 days)
            </label>
          </div>
        </div>
      </div>

      {/* Safety Notice */}
      <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start">
          <ExclamationTriangleIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-3" />
          <div className="text-sm text-blue-800">
            <p className="font-medium">Your safety matters</p>
            <p>If you're experiencing thoughts of self-harm, please reach out for help immediately. Our counselors are here to support you.</p>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 bg-white rounded-lg border border-gray-200 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages?.map((message: any) => (
            <div
              key={message.id}
              className={`flex ${message.user_id === user?.id ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.user_id === user?.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                } ${message.flagged_for_sos ? 'ring-2 ring-red-500' : ''}`}
              >
                <p className="text-sm">{message.message}</p>
                <div className="flex items-center justify-between mt-1">
                  <p className="text-xs opacity-75">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </p>
                  {message.flagged_for_sos && (
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                  )}
                </div>
              </div>
            </div>
          )) || (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">No messages yet. Start a conversation!</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t border-gray-200 p-4">
          {hasSafetyKeywords && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mt-0.5 mr-2" />
                <div className="text-sm text-red-800">
                  <p className="font-medium">Safety Alert</p>
                  <p>Your message contains concerning content. A counselor will be notified to provide support.</p>
                </div>
              </div>
            </div>
          )}
          
          <form onSubmit={handleSubmit(onSubmit)} className="flex space-x-3">
            <div className="flex-1">
              <input
                {...register('message', { required: true })}
                type="text"
                placeholder="Type your message..."
                className="input"
                disabled={sendMutation.isPending}
              />
            </div>
            <button
              type="submit"
              disabled={!messageValue.trim() || sendMutation.isPending}
              className="btn-primary"
            >
              {sendMutation.isPending ? (
                <div className="loading-spinner h-4 w-4" />
              ) : (
                <PaperAirplaneIcon className="h-5 w-5" />
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Help Resources */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-900 mb-2">Need immediate help?</h3>
        <div className="text-sm text-gray-600 space-y-1">
          <p>• School Counselor: counselor@school.edu</p>
          <p>• Crisis Hotline: 988 (Suicide & Crisis Lifeline)</p>
          <p>• Emergency: 911</p>
        </div>
      </div>
    </div>
  )
}

export default ChatPage