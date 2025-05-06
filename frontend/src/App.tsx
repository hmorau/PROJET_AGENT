import './App.css'
import Sidebar from './components/Sidebar'
import ChatApp from './components/ChatApp'
import { Route, Routes } from 'react-router-dom'
import AdminAgents from './components/AdminAgents'

function App() {


  return (
    <>
      <div>
      <Routes>
          <Route path="/" element={<ChatApp />} />
          <Route path="/conversation/:conversationId" element={<ChatApp />} />
          <Route path="/admin" element={<AdminAgents />} />

        </Routes>
        <Sidebar userName="test_user" />
      </div>
    </>
  )
}

export default App
