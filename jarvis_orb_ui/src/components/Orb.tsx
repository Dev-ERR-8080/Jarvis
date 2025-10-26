import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

function AnimatedSphere() {
  const meshRef = useRef<THREE.Mesh>(null!)

  // rotate and slightly scale the orb
  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    meshRef.current.rotation.y = t * 0.5
    meshRef.current.scale.setScalar(1 + Math.sin(t * 2) * 0.05)
  })

  return (
    <Sphere ref={meshRef} args={[1, 64, 64]}>
      <meshStandardMaterial
        color="#4e5bff"
        emissive="#4e5bff"
        emissiveIntensity={1.5}
        roughness={0.2}
        metalness={0.8}
      />
    </Sphere>
  )
}

export default function Orb() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: 'black' }}>
      <Canvas camera={{ position: [0, 0, 3] }}>
        {/* Lights */}
        <ambientLight intensity={0.5} />
        <pointLight position={[5, 5, 5]} intensity={1.5} />

        {/* Our animated glowing sphere */}
        <AnimatedSphere />

        {/* Optional: drag to move camera */}
        <OrbitControls enableZoom={false} />
      </Canvas>
    </div>
  )
}
