import React from 'react'
import ChatBox from './ChatBox'

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white flex flex-col items-center justify-center p-6">
      <div className="max-w-3xl w-full bg-gray-900/60 backdrop-blur-md border border-gray-700 shadow-lg rounded-2xl p-6">
        <h1 className="text-3xl font-extrabold text-center mb-6 bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 text-transparent bg-clip-text animate-pulse">
          🤖 AI Research Mentor
        </h1>
        <ChatBox />
      </div>
      <footer className="mt-8 text-gray-400 text-sm">
        Built by <span className="text-purple-400 font-semibold">Saurabh Singh</span> 🚀
      </footer>
    </div>
  )
}
