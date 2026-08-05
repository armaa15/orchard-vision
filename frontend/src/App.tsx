import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL;

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
  const [section, setSection] = useState('')
  const [rowNumber, setRowNumber] = useState('')
  const [positionInRow, setPositionInRow] = useState('')
  const [variety, setVariety] = useState('')
  const [plantingYear, setPlantingYear] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/trees`)
      .then((response) => response.json())
      .then((data) => setTrees(data))
  }, [])

  const handleSubmit = async () => {
    const newTree = {
      orchard_id: 1,
      section: section,
      row_number: Number(rowNumber),
      position_in_row: Number(positionInRow),
      variety: variety || null,
      planting_year: plantingYear ? Number(plantingYear) : null,
      notes: notes || null,
    }

    const response = await fetch(`${API_URL}/trees`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newTree),
    })

    const createdTree = await response.json()
    setTrees([...trees, createdTree])

    setSection('')
    setRowNumber('')
    setPositionInRow('')
    setVariety('')
    setPlantingYear('')
    setNotes('')
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-green-700">Orchard Vision</h1>

      <div className="flex flex-col gap-2 max-w-xs mt-4">
        <input className="border p-2" placeholder="Section"
          value={section} onChange={(e) => setSection(e.target.value)} />
        <input className="border p-2" placeholder="Row number"
          value={rowNumber} onChange={(e) => setRowNumber(e.target.value)} />
        <input className="border p-2" placeholder="Position in row"
          value={positionInRow} onChange={(e) => setPositionInRow(e.target.value)} />
        <input className="border p-2" placeholder="Variety"
          value={variety} onChange={(e) => setVariety(e.target.value)} />
        <input className="border p-2" placeholder="Planting year"
          value={plantingYear} onChange={(e) => setPlantingYear(e.target.value)} />
        <input className="border p-2" placeholder="Notes"
          value={notes} onChange={(e) => setNotes(e.target.value)} />  
        <button className="bg-green-700 text-white p-2" onClick={handleSubmit}>
          Add tree
        </button>
      </div>

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