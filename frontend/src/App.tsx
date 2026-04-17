import { useState } from 'react'

function App() {
  const [url, setUrl] = useState('')

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-blue-500">
        Streamdown
      </h1>
      <p className="text-lg text-gray-400 mb-8">Download your favorite music instantly.</p>
      
      <div className="flex w-full max-w-md bg-gray-800 rounded-lg overflow-hidden shadow-xl border border-gray-700">
        <input 
          type="text" 
          placeholder="Paste URL here..." 
          className="w-full bg-transparent px-4 py-3 outline-none text-gray-200"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button className="bg-blue-600 hover:bg-blue-500 px-6 py-3 font-semibold transition-colors">
          Fetch
        </button>
      </div>
    </div>
  )
}

export default App
