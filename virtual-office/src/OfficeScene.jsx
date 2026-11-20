import React, { useMemo, useRef } from "react";
import * as THREE from "three";
import { Canvas, useFrame } from "@react-three/fiber";
import { Html, OrbitControls, ContactShadows } from "@react-three/drei";

const ZONE_LAYOUT = {
  command: { title: "COMMAND CENTER", center: [-8.0, -4.0], accent: "#a78bfa", floor: "#e9e7f5" },
  research: { title: "MARKET & RESEARCH LAB", center: [-1.1, -4.0], accent: "#38bdf8", floor: "#e4f0f5" },
  studio: { title: "CONTENT & COMMERCE STUDIO", center: [5.9, -4.0], accent: "#fb7185", floor: "#f5e8eb" },
  finance: { title: "FINANCE & RISK SUITE", center: [-4.6, 3.1], accent: "#34d399", floor: "#e5f2eb" },
  trust: { title: "TRUST, RIGHTS & QA", center: [4.3, 3.1], accent: "#f59e0b", floor: "#f5efe2" }
};
const STATUS_COLORS = { working: "#42d6b1", waiting_input: "#f6b94a", idle: "#8391aa" };

function Desk({ position, accent, compact = false }) {
  const width = compact ? 1.0 : 1.3;
  return <group position={position}>
    <mesh position={[0, 0.48, 0]} castShadow receiveShadow><boxGeometry args={[width, 0.12, 0.72]} /><meshStandardMaterial color="#c7b9a7" roughness={0.8} /></mesh>
    {[-0.42, 0.42].map((x) => <mesh key={x} position={[x, 0.22, 0]} castShadow><boxGeometry args={[0.08, 0.45, 0.62]} /><meshStandardMaterial color="#aab4c2" /></mesh>)}
    <mesh position={[0, 0.91, -0.18]} castShadow><boxGeometry args={[0.68, 0.46, 0.08]} /><meshStandardMaterial color="#536178" metalness={0.2} roughness={0.45} /></mesh>
    <mesh position={[0, 0.92, -0.125]}><boxGeometry args={[0.57, 0.34, 0.012]} /><meshStandardMaterial color={accent} emissive={accent} emissiveIntensity={0.22} /></mesh>
    <mesh position={[0, 0.72, -0.15]}><boxGeometry args={[0.12, 0.08, 0.12]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[0.32, 0.57, 0.12]}><cylinderGeometry args={[0.07, 0.07, 0.025, 12]} /><meshStandardMaterial color="#d9c6a2" /></mesh>
  </group>;
}

function Zone({ zone }) {
  const x = zone.center[0], z = zone.center[1];
  return <group>
    <mesh position={[x, 0.03, z]} receiveShadow><boxGeometry args={[6.4, 0.18, 5.3]} /><meshStandardMaterial color={zone.floor} roughness={0.92} /></mesh>
    <mesh position={[x, 0.13, z - 2.53]}><boxGeometry args={[6.25, 0.035, 0.08]} /><meshStandardMaterial color={zone.accent} emissive={zone.accent} emissiveIntensity={0.12} /></mesh>
    <mesh position={[x - 3.1, 0.14, z]}><boxGeometry args={[0.06, 0.035, 5.1]} /><meshStandardMaterial color={zone.accent} /></mesh>
    <mesh position={[x + 3.1, 0.14, z]}><boxGeometry args={[0.06, 0.035, 5.1]} /><meshStandardMaterial color={zone.accent} /></mesh>
    <Desk position={[x, 0.14, z + 0.2]} accent={zone.accent} />
    <Desk position={[x - 2.0, 0.14, z - 0.8]} accent={zone.accent} compact />
    <mesh position={[x + 2.0, 0.48, z + 1.65]} castShadow><cylinderGeometry args={[0.42, 0.36, 0.13, 8]} /><meshStandardMaterial color="#806c5d" /></mesh>
    <mesh position={[x + 2.0, 0.9, z + 1.65]} castShadow><sphereGeometry args={[0.28, 8, 6]} /><meshStandardMaterial color="#4e8d72" roughness={1} /></mesh>
    <Html position={[x, 0.27, z - 2.05]} center distanceFactor={13} style={{ pointerEvents: "none" }}><div className="zone-label" style={{ borderColor: zone.accent }}>{zone.title}</div></Html>
  </group>;
}

function WaitingArea() {
  return <group position={[0, 0, 1.25]}>
    <mesh position={[0, 0.18, 0]} castShadow><cylinderGeometry args={[1.45, 1.6, 0.22, 8]} /><meshStandardMaterial color="#dce2eb" /></mesh>
    <mesh position={[0, 0.42, 0]} castShadow><cylinderGeometry args={[0.7, 0.82, 0.28, 8]} /><meshStandardMaterial color="#c9b49a" /></mesh>
    <mesh position={[0, 0.58, 0]}><cylinderGeometry args={[0.72, 0.72, 0.035, 8]} /><meshStandardMaterial color="#f3e9d9" /></mesh>
    <mesh position={[-1.15, 0.42, 0]} castShadow><boxGeometry args={[0.55, 0.45, 0.7]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[1.15, 0.42, 0]} castShadow><boxGeometry args={[0.55, 0.45, 0.7]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <Html position={[0, 0.9, -0.9]} center distanceFactor={12} style={{ pointerEvents: "none" }}><div className="zone-label review-label">OWNER INPUT / REVIEW</div></Html>
  </group>;
}

function OfficeGround() {
  return <group>
    <mesh position={[0, -0.12, 0]} receiveShadow><boxGeometry args={[25.2, 0.34, 17.2]} /><meshStandardMaterial color="#e7ebf2" roughness={0.95} /></mesh>
    <mesh position={[0, 0.06, 0]} receiveShadow><boxGeometry args={[24.8, 0.025, 16.8]} /><meshStandardMaterial color="#f7f8fb" roughness={0.9} /></mesh>
    {Array.from({ length: 14 }).map((_, i) => <mesh key={"tile-x-" + i} position={[-11.5 + i * 1.75, 0.078, 0]}><boxGeometry args={[0.018, 0.008, 16.3]} /><meshStandardMaterial color="#dce2eb" /></mesh>)}
    {Array.from({ length: 9 }).map((_, i) => <mesh key={"tile-z-" + i} position={[0, 0.079, -7.0 + i * 1.75]}><boxGeometry args={[24.2, 0.008, 0.018]} /><meshStandardMaterial color="#dce2eb" /></mesh>)}
    <mesh position={[0, 0.19, -7.9]} castShadow><boxGeometry args={[9.0, 0.38, 0.32]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[0, 0.43, -7.71]}><boxGeometry args={[8.1, 0.045, 0.035]} /><meshStandardMaterial color="#9b8cff" emissive="#9b8cff" emissiveIntensity={0.6} /></mesh>
    <Html position={[0, 0.75, -7.65]} center distanceFactor={14} style={{ pointerEvents: "none" }}><div className="brand-sign">AURA <span>REVENUE OPERATIONS</span></div></Html>
  </group>;
}

function AgentCharacter({ agent, homePosition, workPosition, waitingPosition, selected, onSelect }) {
  const group = useRef(), armLeft = useRef(), armRight = useRef();
  const target = useRef(new THREE.Vector3(...homePosition));
  const stateColor = STATUS_COLORS[agent.status] || STATUS_COLORS.idle;
  useFrame((frame, delta) => {
    if (!group.current) return;
    const destination = agent.status === "working" ? workPosition : agent.status === "waiting_input" ? waitingPosition : homePosition;
    target.current.set(destination[0], destination[1], destination[2]);
    group.current.position.lerp(target.current, 1 - Math.exp(-3.8 * delta));
    const walking = group.current.position.distanceTo(target.current) > 0.12;
    const active = agent.status === "working";
    const bob = Math.sin(frame.clock.elapsedTime * (active ? 8 : 2.2) + agent.name.length) * (active ? 0.035 : 0.012);
    group.current.position.y = destination[1] + bob;
    if (armLeft.current && armRight.current) {
      const swing = active ? Math.sin(frame.clock.elapsedTime * 9) * 0.36 : walking ? Math.sin(frame.clock.elapsedTime * 6) * 0.24 : 0;
      armLeft.current.rotation.z = swing;
      armRight.current.rotation.z = -swing;
    }
  });
  return <group ref={group} position={homePosition} onClick={(event) => { event.stopPropagation(); onSelect(agent.name); }}>
    <mesh position={[0, 0.06, 0]} rotation={[-Math.PI / 2, 0, 0]}><torusGeometry args={[selected ? 0.46 : 0.34, selected ? 0.035 : 0.018, 6, 24]} /><meshStandardMaterial color={selected ? "#ffffff" : stateColor} emissive={selected ? "#ffffff" : stateColor} emissiveIntensity={selected ? 0.45 : 0.2} /></mesh>
    <mesh position={[0, 0.18, 0.22]} castShadow><boxGeometry args={[0.34, 0.23, 0.35]} /><meshStandardMaterial color="#30384a" /></mesh>
    <mesh position={[0, 0.78, 0]} castShadow><cylinderGeometry args={[0.26, 0.34, 0.67, 7]} /><meshStandardMaterial color={agent.color} roughness={0.78} /></mesh>
    <mesh position={[0, 0.51, 0.02]}><boxGeometry args={[0.17, 0.2, 0.285]} /><meshStandardMaterial color="#e5e7eb" roughness={0.9} /></mesh>
    <group ref={armLeft} position={[-0.29, 0.93, 0]}><mesh position={[0, -0.19, 0]} rotation={[0, 0, -0.1]} castShadow><capsuleGeometry args={[0.095, 0.31, 3, 6]} /><meshStandardMaterial color={agent.color} /></mesh><mesh position={[0, -0.39, 0.025]}><sphereGeometry args={[0.085, 7, 6]} /><meshStandardMaterial color="#e4bda0" /></mesh></group>
    <group ref={armRight} position={[0.29, 0.93, 0]}><mesh position={[0, -0.19, 0]} rotation={[0, 0, 0.1]} castShadow><capsuleGeometry args={[0.095, 0.31, 3, 6]} /><meshStandardMaterial color={agent.color} /></mesh><mesh position={[0, -0.39, 0.025]}><sphereGeometry args={[0.085, 7, 6]} /><meshStandardMaterial color="#e4bda0" /></mesh></group>
    <mesh position={[-0.12, 0.24, 0]} castShadow><boxGeometry args={[0.14, 0.42, 0.16]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[0.12, 0.24, 0]} castShadow><boxGeometry args={[0.14, 0.42, 0.16]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[-0.12, 0.035, 0.045]}><boxGeometry args={[0.19, 0.08, 0.25]} /><meshStandardMaterial color="#111827" /></mesh>
    <mesh position={[0.12, 0.035, 0.045]}><boxGeometry args={[0.19, 0.08, 0.25]} /><meshStandardMaterial color="#111827" /></mesh>
    <mesh position={[0, 1.31, 0.015]} castShadow><sphereGeometry args={[0.245, 10, 8]} /><meshStandardMaterial color="#e8bea0" roughness={0.85} /></mesh>
    <mesh position={[0, 1.43, -0.025]}><sphereGeometry args={[0.248, 8, 6, 0, Math.PI * 2, 0, Math.PI * 0.58]} /><meshStandardMaterial color={agent.hair} roughness={1} /></mesh>
    <mesh position={[-0.08, 1.33, 0.225]}><sphereGeometry args={[0.024, 6, 5]} /><meshStandardMaterial color="#1e293b" /></mesh>
    <mesh position={[0.08, 1.33, 0.225]}><sphereGeometry args={[0.024, 6, 5]} /><meshStandardMaterial color="#1e293b" /></mesh>
    <mesh position={[0, 1.25, 0.25]}><sphereGeometry args={[0.027, 6, 5]} /><meshStandardMaterial color="#c18f75" /></mesh>
    {agent.archetype === "captain" && <mesh position={[0, 1.64, 0]}><coneGeometry args={[0.16, 0.2, 5]} /><meshStandardMaterial color="#f5d36e" metalness={0.55} /></mesh>}
    {agent.archetype === "analyst" && <mesh position={[0, 1.56, 0]}><boxGeometry args={[0.27, 0.045, 0.29]} /><meshStandardMaterial color="#dbeafe" /></mesh>}
    {agent.archetype === "headphones" && <mesh position={[0, 1.31, 0]}><torusGeometry args={[0.29, 0.055, 6, 14]} /><meshStandardMaterial color="#18212f" /></mesh>}
    {agent.archetype === "glasses" && <group position={[0, 1.34, 0.23]}><mesh position={[-0.075, 0, 0]}><torusGeometry args={[0.052, 0.012, 5, 10]} /><meshStandardMaterial color="#94a3b8" metalness={0.65} /></mesh><mesh position={[0.075, 0, 0]}><torusGeometry args={[0.052, 0.012, 5, 10]} /><meshStandardMaterial color="#94a3b8" metalness={0.65} /></mesh></group>}
    {agent.archetype === "cap" && <group position={[0, 1.51, 0]}><mesh><cylinderGeometry args={[0.19, 0.23, 0.1, 7]} /><meshStandardMaterial color={agent.color} /></mesh><mesh position={[0, -0.03, 0.13]}><boxGeometry args={[0.26, 0.035, 0.22]} /><meshStandardMaterial color={agent.color} /></mesh></group>}
    {agent.archetype === "beret" && <mesh position={[0.06, 1.51, 0]} scale={[1.1, 0.42, 0.9]}><sphereGeometry args={[0.19, 8, 6]} /><meshStandardMaterial color={agent.color} /></mesh>}
    {agent.archetype === "tie" && <mesh position={[0, 0.77, 0.17]}><coneGeometry args={[0.075, 0.32, 4]} /><meshStandardMaterial color="#f3e6d0" /></mesh>}
    {agent.archetype === "visor" && <mesh position={[0, 1.35, 0.235]}><boxGeometry args={[0.36, 0.085, 0.08]} /><meshStandardMaterial color="#1e293b" metalness={0.6} /></mesh>}
    {agent.archetype === "shield" && <mesh position={[0.29, 0.93, 0.08]} rotation={[0, 0, -0.2]}><octahedronGeometry args={[0.14, 0]} /><meshStandardMaterial color="#fecaca" metalness={0.25} /></mesh>}
    {agent.archetype === "badge" && <mesh position={[0.29, 0.91, 0.08]}><dodecahedronGeometry args={[0.11, 0]} /><meshStandardMaterial color="#e2e8f0" metalness={0.5} /></mesh>}
    <mesh position={[0.28, 1.77, 0]}><sphereGeometry args={[0.065, 8, 6]} /><meshStandardMaterial color={stateColor} emissive={stateColor} emissiveIntensity={0.7} /></mesh>
    <Html position={[0, 1.96, 0]} center distanceFactor={10} style={{ pointerEvents: "none" }}>
      <div className="agent-scene-tag"><span className="agent-tag-dot" style={{ background: stateColor }} /><span>{agent.name}</span></div>
    </Html>
  </group>;
}

function SceneContents({ agents, selectedAgent, onSelectAgent, controlsRef }) {
  const positionedAgents = useMemo(() => {
    const counts = {}, waitingCounts = {};
    return agents.map((agent) => {
      const zone = ZONE_LAYOUT[agent.zone] || ZONE_LAYOUT.command;
      const slot = counts[agent.zone] || 0;
      counts[agent.zone] = slot + 1;
      const col = slot % 3, row = Math.floor(slot / 3);
      const home = [zone.center[0] + (col - 1) * 1.75, 0.16, zone.center[1] + (row === 0 ? 1.25 : -0.7)];
      const work = [zone.center[0] + (col - 1) * 1.2, 0.16, zone.center[1] + (row === 0 ? 0.25 : -1.1)];
      const waitSlot = waitingCounts.waiting || 0;
      waitingCounts.waiting = waitSlot + 1;
      const waiting = [(waitSlot % 5 - 2) * 0.5, 0.16, 1.1 + Math.floor(waitSlot / 5) * 0.52];
      return { ...agent, home, work, waiting };
    });
  }, [agents]);
  return <>
    <color attach="background" args={["#f4f6fb"]} />
    <fog attach="fog" args={["#f4f6fb", 28, 48]} />
    <ambientLight intensity={1.65} />
    <hemisphereLight args={["#ffffff", "#d7deea", 1.35]} />
    <directionalLight position={[8, 18, 10]} intensity={2.0} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} />
    <pointLight position={[-8, 6, -4]} intensity={12} color="#b5a7f4" distance={15} />
    <pointLight position={[6, 5, 4]} intensity={10} color="#9bd8e9" distance={14} />
    <OfficeGround />
    {Object.entries(ZONE_LAYOUT).map(([key, zone]) => <Zone key={key} zone={zone} />)}
    <WaitingArea />
    <mesh position={[0, 0.24, -0.1]} castShadow><boxGeometry args={[0.82, 0.48, 0.45]} /><meshStandardMaterial color="#506079" /></mesh>
    <mesh position={[0, 0.53, -0.04]}><boxGeometry args={[0.67, 0.04, 0.06]} /><meshStandardMaterial color="#f3d48a" emissive="#f3d48a" emissiveIntensity={0.22} /></mesh>
    {positionedAgents.map((agent) => <AgentCharacter key={agent.name} agent={agent} homePosition={agent.home} workPosition={agent.work} waitingPosition={agent.waiting} selected={selectedAgent === agent.name} onSelect={onSelectAgent} />)}
    <ContactShadows position={[0, -0.025, 0]} opacity={0.28} scale={27} blur={2.2} far={9} />
    <OrbitControls ref={controlsRef} makeDefault target={[0, 0.7, 0]} minDistance={13} maxDistance={42} minPolarAngle={0.55} maxPolarAngle={1.38} enableDamping dampingFactor={0.08} enableZoom zoomSpeed={0.8} enablePan autoRotate autoRotateSpeed={0.22} />
  </>;
}

export default function OfficeScene({ agents = [], selectedAgent, onSelectAgent }) {
  const controlsRef = useRef(null);
  const zoom = (direction) => {
    const controls = controlsRef.current;
    if (!controls) return;
    if (direction > 0) controls.dollyIn(1.22);
    else controls.dollyOut(1.22);
    controls.update();
  };
  const resetView = () => controlsRef.current?.reset();
  return <div className="scene-canvas-wrap">
    <Canvas shadows dpr={[1, 1.5]} camera={{ position: [21, 25, 22], zoom: 43, near: 0.1, far: 100, up: [0, 1, 0] }} gl={{ antialias: true, alpha: false }}>
      <SceneContents agents={agents} selectedAgent={selectedAgent} onSelectAgent={onSelectAgent} controlsRef={controlsRef} />
    </Canvas>
    <div className="scene-controls" aria-label="Floor plan controls">
      <button type="button" onClick={() => zoom(1)} aria-label="Zoom in" title="Zoom in">+</button>
      <button type="button" onClick={() => zoom(-1)} aria-label="Zoom out" title="Zoom out">−</button>
      <button type="button" onClick={resetView} aria-label="Reset view" title="Reset view">↺</button>
    </div>
    <div className="scene-gesture-hint">Drag to rotate · Pinch or scroll to zoom</div>
  </div>;
}