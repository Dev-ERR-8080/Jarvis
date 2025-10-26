// import './App.css'
// import { Canvas } from '@react-three/fiber'
// import FloatingOrb, { type OrbState } from './components/FloatingOrb'
// import { OrbitControls } from '@react-three/drei'
// import * as THREE from 'three'
// import { useEffect, useState } from 'react'
// import { hotwordService } from './hotwordService'

// function App() {

//   const [orbState, setOrbState] = useState<OrbState>('idle')
  
//   useEffect(() => {
//     hotwordService.onWake(() => setOrbState('listening'));
//   }, [setOrbState]);
  
//   return (
//     <>
//       <div style={{ width: '220px', height: '220px', bottom: 0, right: 0,  background: 'transparent', overflow: 'hidden', position:'fixed' }} >
//             <Canvas
//                 camera={{ position: [0, 0, 15], fov: 60 }}
//                 onCreated={({ gl }) => {
//                     gl.setClearColor(new THREE.Color(0x000000), 0); // Set alpha to 0 for transparency
//                 }}
//             >
//                 <ambientLight intensity={0.5} />
//                 <pointLight position={[10, 10, 10]} intensity={1.5} />
                
//                 <FloatingOrb state = {orbState}/>
//                <OrbitControls enableZoom={false} />
//             </Canvas>
//         </div >
//     </>
//   )
// }

// export default App


import { useEffect, useState } from "react"
import FloatingOrb from "./components/FloatingOrb"
import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import * as THREE from "three"

export default function App() {
  const [state, setState] = useState<"idle"|"listening"|"processing"| "speaking">("idle")

  useEffect(() => {
  const ws = new WebSocket("ws://localhost:8765");

  
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.event){
      setState(data.event);
      console.log("State changed to:", data.event);
    }
  };

  ws.onopen = () => console.log("Connected to Python Daemon!");
  ws.onerror = (err) => console.error("WebSocket error:", err);
  ws.onclose = () => {console.warn("WebSocket closed.");};
  return () => ws.close();

}, []);

  return (
    <>
         <div style={{ width: '220px', height: '220px', bottom: 0, right: 0,  background: 'transparent', overflow: 'hidden', position:'fixed' }} >
          <Canvas
                  camera={{ position: [0, 0, 15], fov: 60 }}
                  onCreated={({ gl }) => {      
                      gl.setClearColor(new THREE.Color(0x000000), 0); // Set alpha to 0 for transparency
                  }}
              >
                  <ambientLight intensity={0.5} />
                  <pointLight position={[10, 10, 10]} intensity={1.5} />
                  
                  <FloatingOrb state = {state}/>
                 <OrbitControls enableZoom={false} />
              </Canvas>
          </div >
      </>
  )
}
