import { useRef, useMemo } from 'react';
import { Canvas, useFrame, extend } from '@react-three/fiber';
import { OrbitControls, Sphere } from '@react-three/drei';
import * as THREE from 'three';
import { ShaderMaterial } from 'three';

// A helper for GLSL noise functions
const glslNoise = `
// Simplex Noise by Ashima Arts and released under MIT license.
vec3 mod289(vec3 x) {
  return x - floor(x * (1.0 / 289.0)) * 289.0;
}
vec4 mod289(vec4 x) {
  return x - floor(x * (1.0 / 289.0)) * 289.0;
}
vec4 permute(vec4 x) {
  return mod289(((x*34.0)+1.0)*x);
}
vec4 taylorInvSqrt(vec4 r) {
  return 1.79284291400159 - 0.85373472095314 * r;
}
float snoise(vec3 v) {
  const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
  const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 = v -   i + dot(i, C.xxx) ;
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;
  i = mod289(i);
  vec4 p = permute( permute( permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
  float n_ = 0.142857142857;
  vec3  ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);
  vec4 x = x_ * ns.x + ns.yyyy;
  vec4 y = y_ * ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww ;
  vec3 p0 = vec3(a0.xy,h.x);
  vec3 p1 = vec3(a0.zw,h.y);
  vec3 p2 = vec3(a1.xy,h.z);
  vec3 p3 = vec3(a1.zw,h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),
                                dot(p2,x2), dot(p3,x3) ) );
}
`;

// Extend ShaderMaterial to be usable with @react-three/fiber
extend({ ShaderMaterial });

function Jarvis_Orb() {
  const meshRef = useRef(null);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uAmp: { value: 0.1 },
      uFrequency: { value: 2.5 },
      uColor1: { value: new THREE.Color('#46a3ff') },
      uColor2: { value: new THREE.Color('#00ffe0') },
    }),
    []
  );

  const material = useMemo(
    () =>
      new ShaderMaterial({
        uniforms,
        vertexShader: `
          ${glslNoise}
          uniform float uTime;
          uniform float uAmp;
          uniform float uFrequency;
          varying vec3 vNormal;
          varying float vDisplacement;

          void main() {
            vNormal = normal;

            float noiseValue = snoise(vec3(position.x * uFrequency, position.y * uFrequency, position.z * uFrequency + uTime));
            vec3 newPosition = position + normal * noiseValue * uAmp;

            vDisplacement = noiseValue;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
          }
        `,
        fragmentShader: `
          uniform float uTime;
          uniform vec3 uColor1;
          uniform vec3 uColor2;
          varying vec3 vNormal;
          varying float vDisplacement;

          void main() {
            // Radial glow from center
            float radialFade = 1.0 - length(gl_PointCoord - vec2(0.5)) * 2.0;
            
            // Blend colors based on noise displacement and a simple vertical gradient
            vec3 color = mix(uColor1, uColor2, vNormal.y + 0.5);
            
            // Add a glow that follows the displacement
            float displacementGlow = smoothstep(0.0, 1.0, abs(vDisplacement)) * 0.8;
            color += color * displacementGlow * 1.5;
            
            gl_FragColor = vec4(color, 0.7 + displacementGlow * 0.3);
          }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
      }),
    [uniforms]
  );

  useFrame(({ clock }) => {
    uniforms.uTime.value = clock.getElapsedTime() * 0.5;
    uniforms.uAmp.value = 0.1 + Math.sin(clock.getElapsedTime() * 0.8) * 0.05;
  });

  return (
    <Sphere ref={meshRef} args={[1, 128, 128]}>
      <primitive object={material} attach="material" />
    </Sphere>
  );
}

export default function JarvisOrb() {
  return (
    <div style={{ width: '100vw', height: '100vh', background: 'black' }}>
      <Canvas camera={{ position: [0, 0, 3] }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[5, 5, 5]} intensity={1.5} />
        <Jarvis_Orb />
        <OrbitControls enableZoom={false} enableRotate={false} />
      </Canvas>
    </div>
  );
}