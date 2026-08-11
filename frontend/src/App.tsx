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

type Observation = {
  id: number
  tree_id: number
  observed_on: string
  notes: string | null
  created_at: string
  photo_path: string | null
  predicted_disease: string | null
  confidence: number | null
}

function App() {
  const [trees, setTrees] = useState<Tree[]>([])
  const [selectedTreeId, setSelectedTreeId] = useState<number | null>(null)
  const [observations, setObservations] = useState<Observation[]>([])
  const [section, setSection] = useState('')
  const [rowNumber, setRowNumber] = useState('')
  const [positionInRow, setPositionInRow] = useState('')
  const [variety, setVariety] = useState('')
  const [plantingYear, setPlantingYear] = useState('')
  const [notes, setNotes] = useState('')
  const [treeError, setTreeError] = useState<string | null>(null)
  const [observedOn, setObservedOn] = useState('')
  const [observationNotes, setObservationNotes] = useState('')
  const [photo, setPhoto] = useState<File | null>(null)
  const [observationError, setObservationError] = useState<string | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/trees`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load trees (${response.status}).`)
        }
        return response.json()
      })
      .then((data) => setTrees(data))
      .catch(() => setLoadError('Could not load trees.'))
  }, [])

  useEffect(() => {
    if (selectedTreeId === null) {
      setObservations([])
      return
    }
    fetch(`${API_URL}/trees/${selectedTreeId}/observations`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load observations (${response.status}).`)
        }
        return response.json()
      })
      .then((data) => setObservations(data))
      .catch(() => setObservationError('Could not load observations.'))
  }, [selectedTreeId])

  const handleSubmit = async () => {
    setTreeError(null)

    if (!section.trim()) {
      setTreeError('Section is required.')
      return
    }
    if (!Number.isInteger(Number(rowNumber)) || rowNumber.trim() === '') {
      setTreeError('Row number must be a whole number.')
      return
    }
    if (!Number.isInteger(Number(positionInRow)) || positionInRow.trim() === '') {
      setTreeError('Position in row must be a whole number.')
      return
    }
    if (plantingYear && !Number.isInteger(Number(plantingYear))) {
      setTreeError('Planting year must be a whole number.')
      return
    }

    const newTree = {
      orchard_id: 1,
      section: section,
      row_number: Number(rowNumber),
      position_in_row: Number(positionInRow),
      variety: variety || null,
      planting_year: plantingYear ? Number(plantingYear) : null,
      notes: notes || null,
    }

    try {
      const response = await fetch(`${API_URL}/trees`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTree),
      })

      if (!response.ok) {
        setTreeError(`Could not save tree (${response.status}).`)
        return
      }

      const createdTree = await response.json()
      setTrees([...trees, createdTree])
      setSection('')
      setRowNumber('')
      setPositionInRow('')
      setVariety('')
      setPlantingYear('')
      setNotes('')
    } catch {
      setTreeError('Could not reach the server.')
    }
  }

  const handleObservationSubmit = async () => {
    setObservationError(null)

    if (selectedTreeId === null) {
      return
    }
    if (!observedOn) {
      setObservationError('A date is required.')
      return
    }

    const formData = new FormData()
    formData.append('tree_id', String(selectedTreeId))
    formData.append('observed_on', observedOn)
    if (observationNotes) {
      formData.append('notes', observationNotes)
    }
    if (photo) {
      formData.append('photo', photo)
    }

    try {
      const response = await fetch(`${API_URL}/observations`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        setObservationError(`Could not save observation (${response.status}).`)
        return
      }

      const createdObservation = await response.json()
      setObservations([...observations, createdObservation])
      setObservedOn('')
      setObservationNotes('')
      setPhoto(null)
    } catch {
      setObservationError('Could not reach the server.')
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-green-700">Orchard Vision</h1>
      {loadError && <p className="text-red-700">{loadError}</p>}
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
        {treeError && <p className="text-red-700">{treeError}</p>}
      </div>

      <ul className="mt-6">
        {trees.map((tree) => (
          <li key={tree.id}>
            <button
              className={
                selectedTreeId === tree.id
                  ? 'text-left underline font-bold'
                  : 'text-left'
              }
              onClick={() => setSelectedTreeId(tree.id)}
            >
              #{tree.id} — {tree.variety}, {tree.section} row {tree.row_number}
            </button>
          </li>
        ))}
      </ul>

      {selectedTreeId !== null && (
        <div className="mt-6">
          <h2 className="text-xl font-bold">
            Observations for tree #{selectedTreeId}
          </h2>

          {observationError ? null : observations.length === 0 ? (
            <p>No observations logged.</p>
          ) : (
            <ul className="mt-2">
              {observations.map((observation) => (
                <li key={observation.id}>
                  {observation.observed_on} — {observation.notes ?? 'no notes'}
                </li>
              ))}
            </ul>
          )}

          <div className="flex flex-col gap-2 max-w-xs mt-4">
            <input className="border p-2" type="date"
              value={observedOn} onChange={(e) => setObservedOn(e.target.value)} />
            <input className="border p-2" placeholder="Observation notes"
              value={observationNotes}
              onChange={(e) => setObservationNotes(e.target.value)} />
            <input className="border p-2" type="file" accept="image/*"
              onChange={(e) => setPhoto(e.target.files?.[0] ?? null)} />
            <button className="bg-green-700 text-white p-2"
              onClick={handleObservationSubmit}>
              Log observation
            </button>
            {observationError && <p className="text-red-700">{observationError}</p>}
          </div>
        </div>
      )}
    </div>
  )
}

export default App