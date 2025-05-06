import './App.css'
import Sidebar from './components/Sidebar'
import ChatApp from './components/ChatApp'
import { Route, Routes } from 'react-router-dom'

function App() {


  return (
    <>
      <div>
      <Routes>
          <Route path="/" element={<ChatApp />} />
          <Route path="/conversation/:conversationId" element={<ChatApp />} />
        </Routes>
        <Sidebar userName="test_user" />
      </div>
    </>
  )
}

export default App
