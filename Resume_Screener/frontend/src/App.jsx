import React, {useState} from 'react'
import axios from 'axios'

export default function App(){
  const [job, setJob] = useState('')
  const [files, setFiles] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if(!job.trim()) return alert('Please enter job description')
    const form = new FormData()
    form.append('job_description', job)
    if(files){
      for(let i=0;i<files.length;i++) form.append('files', files[i])
    }
    setLoading(true)
    try{
      const res = await axios.post('http://localhost:8000/screen', form, {headers: {'Content-Type':'multipart/form-data'}})
      setResults(res.data)
    }catch(err){
      console.error(err)
      alert(err?.response?.data?.detail || 'Error')
    }finally{setLoading(false)}
  }

  return (
    <div className="container">
      <h1>Resume Screener</h1>
      <form onSubmit={submit} className="form">
        <label>Job description</label>
        <textarea value={job} onChange={e=>setJob(e.target.value)} rows={8} />

        <label>Upload resumes (PDF/DOCX/TXT) - up to 200</label>
        <input type="file" multiple onChange={e=>setFiles(e.target.files)} />

        <button type="submit" disabled={loading}>{loading? 'Screening...':'Screen Resumes'}</button>
      </form>

      <h2>Results</h2>
      <div>
        {results.length===0 && <p>No results yet</p>}
        {results.map((r, i)=> (
          <div key={i} className="card">
            <div className="meta">
              <strong>{r.filename}</strong>
              <span>score: {r.score.toFixed(3)}</span>
            </div>
            <p className="snippet">{r.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
