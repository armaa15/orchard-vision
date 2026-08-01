import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-green-700">Orchard Vision</h1>
      <button
        type="button"
        className="mt-4 rounded bg-green-700 px-4 py-2 text-white"
        onClick={() => setCount((count) => count + 1)}
      >
        Count is {count}
      </button>
    </div>
  )
}

export default App
