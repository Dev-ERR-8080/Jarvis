// import { useRef, useMemo, useEffect } from 'react';
// import { Canvas, useFrame, extend } from '@react-three/fiber';
// import * as THREE from 'three';
// import { ShaderMaterial } from 'three';

// // Extend ShaderMaterial to be usable with React Three Fiber
// extend({ ShaderMaterial });

// interface IUniforms {
//     uTime: { value: number };
//     [uniform: string]: THREE.IUniform;
// }

// const INSTANCE_COUNT = 4000;

// function FloatingOrb() {
//     const meshRef = useRef<THREE.InstancedMesh>(null!);
//     const particleRef = useRef<THREE.Points>(null!);

//     const uniforms: IUniforms = useMemo(
//         () => ({
//             uTime: { value: 0 },
//         }),
//         []
//     );

//     // --- Instanced Octahedrons Logic ---
//     const instancedObjects = useMemo(() => {
//         const temp = new THREE.Object3D();
//         const positions = new Float32Array(INSTANCE_COUNT * 3);
//         const randoms = new Float32Array(INSTANCE_COUNT);

//         const sphere = new THREE.SphereGeometry(1.0, 32, 32);
//         const spherePositions = sphere.attributes.position.array;

//         for (let i = 0; i < INSTANCE_COUNT; i++) {
//             // Pick a random vertex from a sphere to place an instance
//             const idx = Math.floor(Math.random() * spherePositions.length / 3) * 3;
//             const x = spherePositions[idx];
//             const y = spherePositions[idx + 1];
//             const z = spherePositions[idx + 2];
//             positions[i * 3] = x;
//             positions[i * 3 + 1] = y;
//             positions[i * 3 + 2] = z;
//             randoms[i] = Math.random();
//         }

//         return { positions, randoms, temp };
//     }, []);

//     // Set initial instance matrices
//     useEffect(() => {
//         if (!meshRef.current) return;
//         const { positions, randoms, temp } = instancedObjects;
//         for (let i = 0; i < INSTANCE_COUNT; i++) {
//             temp.position.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]);
//             temp.rotation.x = randoms[i] * Math.PI * 2;
//             temp.rotation.y = randoms[i] * Math.PI * 2;
//             temp.rotation.z = randoms[i] * Math.PI * 2;
//             temp.scale.setScalar(0.04 + randoms[i] * 0.05);
//             temp.updateMatrix();
//             meshRef.current.setMatrixAt(i, temp.matrix);
//         }
//         meshRef.current.instanceMatrix.needsUpdate = true;
//     }, [instancedObjects]);

//     // Animate instance positions and rotations on the CPU
//     useFrame((state) => {
//         const { positions, randoms, temp } = instancedObjects;
//         const t = state.clock.getElapsedTime();
//         uniforms.uTime.value = t;

//         for (let i = 0; i < INSTANCE_COUNT; i++) {
//             const x = positions[i * 3] + Math.sin(t * 0.2 + randoms[i] * 100) * 0.1;
//             const y = positions[i * 3 + 1] + Math.cos(t * 0.2 + randoms[i] * 100) * 0.1;
//             const z = positions[i * 3 + 2] + Math.sin(t * 0.2 + randoms[i] * 100) * 0.1;

//             temp.position.set(x, y, z);
//             temp.rotation.x = t * 0.5 + randoms[i] * Math.PI * 2;
//             temp.rotation.y = t * 0.5 + randoms[i] * Math.PI * 2;
//             temp.rotation.z = t * 0.5 + randoms[i] * Math.PI * 2;
//             temp.scale.setScalar(0.04 + randoms[i] * 0.05);

//             temp.updateMatrix();
//             meshRef.current.setMatrixAt(i, temp.matrix);
//         }
//         meshRef.current.instanceMatrix.needsUpdate = true;
//     });

//     // --- Particle System Logic ---
//     const particles = useMemo(() => {
//         const p = new Float32Array(INSTANCE_COUNT * 3);
//         const id = new Float32Array(INSTANCE_COUNT);
//         for (let i = 0; i < INSTANCE_COUNT; i++) {
//             // Position particles randomly in a larger sphere
//             const r = 3 + Math.random() * 2;
//             const theta = Math.random() * Math.PI * 2;
//             const phi = Math.random() * Math.PI;
//             p[i * 3] = r * Math.sin(phi) * Math.cos(theta);
//             p[i * 3 + 1] = r * Math.cos(phi);
//             p[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
//             id[i] = Math.random();
//         }
//         return { p, id };
//     }, []);

//     const particleMaterial = useMemo(
//         () =>
//             new THREE.ShaderMaterial({
//                 uniforms,
//                 vertexShader: `
//                     uniform float uTime;
//                     attribute float id;
//                     void main() {
//                         vec3 pos = position;
//                         float offset = sin(id * 10.0 + uTime) * 0.2;
//                         pos += normalize(pos) * offset;
//                         vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
//                         gl_PointSize = (1.0 + offset) * (1.0 / -mvPosition.z);
//                         gl_Position = projectionMatrix * mvPosition;
//                     }
//                 `,
//                 fragmentShader: `
//                     void main() {
//                         vec2 cxy = 2.0 * gl_PointCoord - 1.0;
//                         float r = dot(cxy, cxy);
//                         if (r > 1.0) { discard; }
//                         float alpha = smoothstep(1.0, 0.0, r);
//                         gl_FragColor = vec4(0.2, 0.4, 1.0, alpha);
//                     }
//                 `,
//                 transparent: true,
//                 blending: THREE.AdditiveBlending,
//                 depthTest: false,
//             }),
//         [uniforms]
//     );

//     return (
//         <group>
//             {/* The main orb made of instanced octahedrons */}
//             <instancedMesh ref={meshRef} args={[undefined, undefined, INSTANCE_COUNT]}>
//                 <octahedronGeometry args={[1, 0]} />
//                 <shaderMaterial
//                     attach="material"
//                     transparent={true}
//                     blending={THREE.AdditiveBlending}
//                     uniforms={uniforms}
//                     vertexShader={`
//                         uniform float uTime;
//                         void main() {
//                             gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);
//                         }
//                     `}
//                     fragmentShader={`
//                         uniform float uTime;
//                         void main() {
//                             vec3 color = vec3(0.0, 0.5, 1.0);
//                             gl_FragColor = vec4(color, 0.2 + abs(sin(uTime)) * 0.1);
//                         }
//                     `}
//                 />
//             </instancedMesh>

//             {/* The wispy, flowing particle system */}
//             <points ref={particleRef} material={particleMaterial}>
//                 <bufferGeometry>
//                     <bufferAttribute attach='attributes-position' args={[particles.p, 3]} />
//                     <bufferAttribute attach='attributes-id' args={[particles.id, 1]} />
//                 </bufferGeometry>
//             </points>
//         </group>
//     );
// }
// export default FloatingOrb;

import { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export type OrbState = 'idle' | 'listening' | 'processing' | 'speaking'

interface FloatingOrbProps {
  state: OrbState
}

interface IUniforms {
  uTime: { value: number }
  uIntensity: { value: number }
  uColor: { value: THREE.Color }
  [key: string]: any
}

const INSTANCE_COUNT = 4000

export default function FloatingOrb({ state }: FloatingOrbProps) {
  const meshRef = useRef<THREE.InstancedMesh>(null!)
  const particleRef = useRef<THREE.Points>(null!)

  const uniforms: IUniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uIntensity: { value: 0.2 },
      uColor: { value: new THREE.Color('#3ab8ff') },
    }),
    []
  )

  // --- Instanced Orb Geometry ---
  const instancedObjects = useMemo(() => {
    const temp = new THREE.Object3D()
    const positions = new Float32Array(INSTANCE_COUNT * 3)
    const randoms = new Float32Array(INSTANCE_COUNT)

    const sphere = new THREE.SphereGeometry(1, 32, 32)
    const verts = sphere.attributes.position.array

    for (let i = 0; i < INSTANCE_COUNT; i++) {
      const idx = Math.floor(Math.random() * verts.length / 3) * 3
      positions[i * 3] = verts[idx]
      positions[i * 3 + 1] = verts[idx + 1]
      positions[i * 3 + 2] = verts[idx + 2]
      randoms[i] = Math.random()
    }

    return { positions, randoms, temp }
  }, [])

  useEffect(() => {
    if (!meshRef.current) return
    const { positions, randoms, temp } = instancedObjects

    for (let i = 0; i < INSTANCE_COUNT; i++) {
      temp.position.set(
        positions[i * 3],
        positions[i * 3 + 1],
        positions[i * 3 + 2]
      )
      temp.scale.setScalar(0.04 + randoms[i] * 0.05)
      temp.updateMatrix()
      meshRef.current.setMatrixAt(i, temp.matrix)
    }
    meshRef.current.instanceMatrix.needsUpdate = true
  }, [instancedObjects])

  // Animate based on state
  useFrame((stateFrame) => {
    const t = stateFrame.clock.getElapsedTime()
    uniforms.uTime.value = t

    // Animate orb intensity/color based on assistant state
    switch (state) {
      case 'idle':
        uniforms.uIntensity.value = 0.2 + Math.sin(t * 1.0) * 0.05
        uniforms.uColor.value.set('#3ab8ff')
        break
      case 'listening':
        uniforms.uIntensity.value = 0.4 + Math.sin(t * 2.5) * 0.2
        uniforms.uColor.value.set('#5df2ff') // cyan-ish
        break
      case 'processing':
        uniforms.uIntensity.value = 0.5 + Math.sin(t * 3.0) * 0.25
        uniforms.uColor.value.set('#7f5dff') // violet
        break
      case 'speaking':
        uniforms.uIntensity.value = 0.35 + Math.sin(t * 5.0) * 0.3
        uniforms.uColor.value.set('#ffd15d') // warm tone
        break
    }

    // Make the instanced mesh slightly "breathe"
    const { positions, randoms, temp } = instancedObjects
    for (let i = 0; i < INSTANCE_COUNT; i++) {
      const x = positions[i * 3] + Math.sin(t * 0.4 + randoms[i] * 100) * 0.08
      const y = positions[i * 3 + 1] + Math.cos(t * 0.4 + randoms[i] * 100) * 0.08
      const z = positions[i * 3 + 2] + Math.sin(t * 0.4 + randoms[i] * 100) * 0.08

      temp.position.set(x, y, z)
      temp.scale.setScalar(0.04 + randoms[i] * (0.05 + uniforms.uIntensity.value * 0.2))
      temp.updateMatrix()
      meshRef.current.setMatrixAt(i, temp.matrix)
    }
    meshRef.current.instanceMatrix.needsUpdate = true
  })

  // Particles
  const particles = useMemo(() => {
    const p = new Float32Array(INSTANCE_COUNT * 3)
    const id = new Float32Array(INSTANCE_COUNT)
    for (let i = 0; i < INSTANCE_COUNT; i++) {
      const r = 3 + Math.random() * 2
      const theta = Math.random() * Math.PI * 2
      const phi = Math.random() * Math.PI
      p[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      p[i * 3 + 1] = r * Math.cos(phi)
      p[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta)
      id[i] = Math.random()
    }
    return { p, id }
  }, [])

  const particleMaterial = useMemo(
    () =>
      new THREE.ShaderMaterial({
        uniforms,
        vertexShader: `
          uniform float uTime;
          uniform float uIntensity;
          attribute float id;
          void main() {
            vec3 pos = position;
            float offset = sin(id * 10.0 + uTime) * (0.1 + uIntensity * 0.3);
            pos += normalize(pos) * offset;
            vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
            gl_PointSize = (1.0 + offset) * (1.0 / -mvPosition.z);
            gl_Position = projectionMatrix * mvPosition;
          }
        `,
        fragmentShader: `
          uniform vec3 uColor;
          void main() {
            vec2 cxy = 2.0 * gl_PointCoord - 1.0;
            float r = dot(cxy, cxy);
            if (r > 1.0) discard;
            float alpha = smoothstep(1.0, 0.0, r);
            gl_FragColor = vec4(uColor, alpha);
          }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthTest: false,
      }),
    [uniforms]
  )

  return (
    <group>
      <instancedMesh ref={meshRef} args={[undefined, undefined, INSTANCE_COUNT]}>
        <octahedronGeometry args={[1, 0]} />
        <shaderMaterial
          transparent
          blending={THREE.AdditiveBlending}
          uniforms={uniforms}
          vertexShader={`
            uniform float uTime;
            void main() {
              gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);
            }
          `}
          fragmentShader={`
            uniform float uTime;
            uniform float uIntensity;
            uniform vec3 uColor;
            void main() {
              gl_FragColor = vec4(uColor, 0.15 + uIntensity * 0.5);
            }
          `}
        />
      </instancedMesh>

      <points ref={particleRef} material={particleMaterial}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[particles.p, 3]} />
          <bufferAttribute attach="attributes-id" args={[particles.id, 2]} />
        </bufferGeometry>
      </points>
    </group>
  )
}
