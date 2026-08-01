import { useState, useEffect } from 'react'

type Tree = {
    id: number
    orchard_id: number
    section: string
    row_number: number
    position_in_row: number
    variety: string | null
    planting_year: number | null
    status: string
    notes: string | null
  }
function App() {
  const [trees, setTrees] = useState<Tree[]>([])

  useEffect(() => {
    fetch('orchard-vision-production.up.railway.app')
      .then((response) => response.json())
      .then((data) => setTrees(data))
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-green-700">Orchard Vision</h1>
      <ul className="mt-4">
        {trees.map((tree) => (
          <li key={tree.id}>
            #{tree.id} — {tree.variety}, {tree.section} row {tree.row_number}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default App