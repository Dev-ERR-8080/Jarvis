
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import Flowing_Particles from './Flowing_Particles'
import Glassy_Orb from './Glassy_Orb'

export default function SiriScene() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: 'black' }}>
      <Canvas camera={{ position: [0, 0, 3] }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[3, 3, 5]} intensity={1.2} />
        <Flowing_Particles />
        <Glassy_Orb />
        <OrbitControls enableZoom={false} enableRotate={false} />
      </Canvas>
    </div>
  )
}
