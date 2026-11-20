import React, { useMemo, useRef } from "react";
import * as THREE from "three";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Html, OrbitControls, ContactShadows } from "@react-three/drei";

const ZONE_LAYOUT = {
  command: { title: "EXECUTIVE HQ", center: [-8.0, -4.0], accent: "#a78bfa", floor: "#20243a" },
  research: { title: "RESEARCH & OPPORTUNITY", center: [0.0, -4.0], accent: "#38bdf8", floor: "#172c3b" },
  marketing: { title: "CONTENT & AUDIENCE", center: [8.0, -4.0], accent: "#fb7185", floor: "#352333" },
  sales: { title: "SALES & MONETIZATION", center: [-8.0, 4.0], accent: "#34d399", floor: "#1b332e" },
  operations: { title: "OPERATIONS & FINANCE", center: [0.0, 4.0], accent: "#f59e0b", floor: "#342d20" },
  engineering: { title: "TECHNOLOGY & AUTOMATION", center: [8.0, 4.0], accent: "#818cf8", floor: "#222840" }
};
const STATUS_COLORS = { working: "#42d6b1", waiting_input: "#f6b94a", idle: "#8391aa" };

function Desk({ position, accent, compact = false }) {
  const width = compact ? 1.0 : 1.3;
  return <group position={position}>
    <mesh position={[0, 0.48, 0]} castShadow receiveShadow><boxGeometry args={[width, 0.12, 0.72]} /><meshStandardMaterial color="#475569" roughness={0.8} /></mesh>
    {[-0.42, 0.42].map((x) => <mesh key={x} position={[x, 0.22, 0]} castShadow><boxGeometry args={[0.08, 0.45, 0.62]} /><meshStandardMaterial color="#334155" /></mesh>)}
    <mesh position={[0, 0.91, -0.18]} castShadow><boxGeometry args={[0.68, 0.46, 0.08]} /><meshStandardMaterial color="#1e293b" metalness={0.2} roughness={0.45} /></mesh>
    <mesh position={[0, 0.92, -0.125]}><boxGeometry args={[0.57, 0.34, 0.012]} /><meshStandardMaterial color={accent} emissive={accent} emissiveIntensity={0.22} /></mesh>
    <mesh position={[0, 0.72, -0.15]}><boxGeometry args={[0.12, 0.08, 0.12]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[0.32, 0.57, 0.12]}><cylinderGeometry args={[0.07, 0.07, 0.025, 12]} /><meshStandardMaterial color="#64748b" /></mesh>
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
    <mesh position={[0, 0.18, 0]} castShadow><cylinderGeometry args={[1.45, 1.6, 0.22, 8]} /><meshStandardMaterial color="#25324a" /></mesh>
    <mesh position={[0, 0.42, 0]} castShadow><cylinderGeometry args={[0.7, 0.82, 0.28, 8]} /><meshStandardMaterial color="#c9b49a" /></mesh>
    <mesh position={[0, 0.58, 0]}><cylinderGeometry args={[0.72, 0.72, 0.035, 8]} /><meshStandardMaterial color="#f3e9d9" /></mesh>
    <mesh position={[-1.15, 0.42, 0]} castShadow><boxGeometry args={[0.55, 0.45, 0.7]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[1.15, 0.42, 0]} castShadow><boxGeometry args={[0.55, 0.45, 0.7]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <Html position={[0, 0.9, -0.9]} center distanceFactor={12} style={{ pointerEvents: "none" }}><div className="zone-label review-label">OWNER INPUT / REVIEW</div></Html>
  </group>;
}

function OfficeGround() {
  return <group>
    <mesh position={[0, -0.12, 0]} receiveShadow><boxGeometry args={[25.2, 0.34, 17.2]} /><meshStandardMaterial color="#111827" roughness={0.95} /></mesh>
    <mesh position={[0, 0.06, 0]} receiveShadow><boxGeometry args={[24.8, 0.025, 16.8]} /><meshStandardMaterial color="#0f172a" roughness={0.9} /></mesh>
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
  const skin = "#d9a889";
  return <group ref={group} position={homePosition} onClick={(event) => { event.stopPropagation(); onSelect(agent.name); }}>
    <mesh position={[0, 0.06, 0]} rotation={[-Math.PI / 2, 0, 0]}><torusGeometry args={[selected ? 0.48 : 0.35, selected ? 0.04 : 0.02, 6, 24]} /><meshStandardMaterial color={selected ? "#ffffff" : stateColor} emissive={selected ? "#ffffff" : stateColor} emissiveIntensity={selected ? 0.45 : 0.2} /></mesh>
    <mesh position={[0, 0.18, 0.22]} castShadow><boxGeometry args={[0.36, 0.22, 0.34]} /><meshStandardMaterial color="#273449" /></mesh>
    <mesh position={[0, 0.82, 0]} castShadow><boxGeometry args={[0.58, 0.62, 0.34]} /><meshStandardMaterial color={agent.color} roughness={0.76} /></mesh>
    <mesh position={[0, 0.84, 0.178]}><boxGeometry args={[0.24, 0.34, 0.018]} /><meshStandardMaterial color="#e2e8f0" /></mesh>
    <group ref={armLeft} position={[-0.36, 1.02, 0]}><mesh position={[0, -0.22, 0]} castShadow><boxGeometry args={[0.22, 0.52, 0.24]} /><meshStandardMaterial color={agent.color} /></mesh><mesh position={[0, -0.52, 0.015]}><boxGeometry args={[0.2, 0.18, 0.22]} /><meshStandardMaterial color={skin} /></mesh></group>
    <group ref={armRight} position={[0.36, 1.02, 0]}><mesh position={[0, -0.22, 0]} castShadow><boxGeometry args={[0.22, 0.52, 0.24]} /><meshStandardMaterial color={agent.color} /></mesh><mesh position={[0, -0.52, 0.015]}><boxGeometry args={[0.2, 0.18, 0.22]} /><meshStandardMaterial color={skin} /></mesh></group>
    <mesh position={[-0.16, 0.34, 0]} castShadow><boxGeometry args={[0.22, 0.48, 0.28]} /><meshStandardMaterial color="#334155" /></mesh>
    <mesh position={[0.16, 0.34, 0]} castShadow><boxGeometry args={[0.22, 0.48, 0.28]} /><meshStandardMaterial color="#334155" /></mesh>
    <mesh position={[-0.16, 0.075, 0.04]}><boxGeometry args={[0.25, 0.13, 0.34]} /><meshStandardMaterial color="#111827" /></mesh>
    <mesh position={[0.16, 0.075, 0.04]}><boxGeometry args={[0.25, 0.13, 0.34]} /><meshStandardMaterial color="#111827" /></mesh>
    <mesh position={[0, 1.42, 0.015]} castShadow><boxGeometry args={[0.52, 0.52, 0.46]} /><meshStandardMaterial color={skin} roughness={0.86} /></mesh>
    <mesh position={[0, 1.66, -0.015]} castShadow><boxGeometry args={[0.54, 0.12, 0.48]} /><meshStandardMaterial color={agent.hair} roughness={1} /></mesh>
    <mesh position={[-0.12, 1.44, 0.25]}><boxGeometry args={[0.045, 0.055, 0.025]} /><meshStandardMaterial color="#111827" /></mesh>
    <mesh position={[0.12, 1.44, 0.25]}><boxGeometry args={[0.045, 0.055, 0.025]} /><meshStandardMaterial color="#111827" /></mesh>
    <mesh position={[0, 1.34, 0.25]}><boxGeometry args={[0.08, 0.025, 0.025]} /><meshStandardMaterial color="#9f6b59" /></mesh>
    {agent.archetype === "captain" && <mesh position={[0, 1.82, 0]}><boxGeometry args={[0.34, 0.18, 0.32]} /><meshStandardMaterial color="#f5d36e" metalness={0.45} /></mesh>}
    {agent.archetype === "analyst" && <mesh position={[0, 1.75, 0]}><boxGeometry args={[0.48, 0.08, 0.5]} /><meshStandardMaterial color="#dbeafe" /></mesh>}
    {agent.archetype === "headphones" && <mesh position={[0, 1.42, 0]}><torusGeometry args={[0.31, 0.055, 6, 14]} /><meshStandardMaterial color="#0f172a" /></mesh>}
    {agent.archetype === "glasses" && <group position={[0, 1.44, 0.27]}><mesh position={[-0.12, 0, 0]}><boxGeometry args={[0.13, 0.1, 0.04]} /><meshStandardMaterial color="#94a3b8" metalness={0.65} /></mesh><mesh position={[0.12, 0, 0]}><boxGeometry args={[0.13, 0.1, 0.04]} /><meshStandardMaterial color="#94a3b8" metalness={0.65} /></mesh></group>}
    {agent.archetype === "cap" && <mesh position={[0, 1.75, 0.08]}><boxGeometry args={[0.58, 0.1, 0.58]} /><meshStandardMaterial color={agent.color} /></mesh>}
    {agent.archetype === "beret" && <mesh position={[0.05, 1.76, 0]}><boxGeometry args={[0.42, 0.12, 0.44]} /><meshStandardMaterial color={agent.color} /></mesh>}
    {agent.archetype === "tie" && <mesh position={[0, 0.83, 0.205]}><boxGeometry args={[0.1, 0.38, 0.05]} /><meshStandardMaterial color="#f3e6d0" /></mesh>}
    {agent.archetype === "visor" && <mesh position={[0, 1.44, 0.28]}><boxGeometry args={[0.5, 0.11, 0.07]} /><meshStandardMaterial color="#1e293b" metalness={0.6} /></mesh>}
    {agent.archetype === "shield" && <mesh position={[0.42, 1.02, 0.08]}><boxGeometry args={[0.18, 0.24, 0.1]} /><meshStandardMaterial color="#fecaca" metalness={0.25} /></mesh>}
    {agent.archetype === "badge" && <mesh position={[0.42, 1.02, 0.08]}><boxGeometry args={[0.15, 0.15, 0.08]} /><meshStandardMaterial color="#e2e8f0" metalness={0.5} /></mesh>}
    {agent.archetype === "tech" && <mesh position={[0, 1.77, 0]}><boxGeometry args={[0.38, 0.1, 0.38]} /><meshStandardMaterial color={agent.color} emissive={agent.color} emissiveIntensity={0.2} /></mesh>}
    <mesh position={[0.34, 1.86, 0]}><boxGeometry args={[0.12, 0.12, 0.12]} /><meshStandardMaterial color={stateColor} emissive={stateColor} emissiveIntensity={0.7} /></mesh>
    <Html position={[0, 2.12, 0]} center distanceFactor={10} style={{ pointerEvents: "none" }}>
      <div className="agent-scene-tag"><span className="agent-tag-dot" style={{ background: stateColor }} /><span>{agent.name}</span></div>
    </Html>
    <Html position={[0, 2.78, 0]} center distanceFactor={12} style={{ pointerEvents: "none" }}>
      <div className={"agent-notice " + (agent.status || "idle")}>
        <strong>{agent.status === "working" ? "SEDANG BEKERJA" : agent.status === "waiting_input" ? "MENUNGGU INPUT" : "SIAP / IDLE"}</strong>
        <span>{agent.current_task?.objective || (agent.status === "working" ? "Menjalankan tugas aktif" : agent.status === "waiting_input" ? "Butuh arahan pemilik" : "Belum ada tugas aktif")}</span>
      </div>
    </Html>
  </group>;
}
function FitCamera({ controlsRef }) {
  const { camera, size } = useThree();
  React.useEffect(() => {
    const aspect = size.width / Math.max(size.height, 1);
    const halfFov = THREE.MathUtils.degToRad((camera.fov || 42) / 2);
    const distanceForWidth = 25.2 / (2 * Math.tan(halfFov) * aspect);
    const distanceForDepth = 17.2 / (2 * Math.tan(halfFov));
    const distance = Math.max(distanceForWidth, distanceForDepth) * 1.08;
    const target = new THREE.Vector3(0, 0.65, 0);
    const direction = new THREE.Vector3(0, 0.78, 0.62).normalize();
    camera.position.copy(target).addScaledVector(direction, distance);
    camera.lookAt(target);
    camera.updateProjectionMatrix();
    if (controlsRef.current) {
      controlsRef.current.target.copy(target);
      controlsRef.current.update();
    }
  }, [camera, size.width, size.height, controlsRef]);
  return null;
}

function SceneContents({ agents, selectedAgent, onSelectAgent, controlsRef }) {
  const positionedAgents = useMemo(() => {
    const counts = {}, waitingCounts = {};
    return agents.map((agent) => {
      const zone = ZONE_LAYOUT[agent.zone] || ZONE_LAYOUT.command;
      const slot = counts[agent.zone] || 0;
      counts[agent.zone] = slot + 1;
      const col = slot % 2, row = Math.floor(slot / 2);
      const home = [zone.center[0] + (col - 0.5) * 2.35, 0.16, zone.center[1] + [1.45, 0, -1.45][row % 3]];
      const work = [zone.center[0] + (col - 0.5) * 1.8, 0.16, zone.center[1] + [0.45, 0, -0.45][row % 3]];
      const waitSlot = waitingCounts.waiting || 0;
      waitingCounts.waiting = waitSlot + 1;
      const waiting = [(waitSlot % 5 - 2) * 0.5, 0.16, 1.1 + Math.floor(waitSlot / 5) * 0.52];
      return { ...agent, home, work, waiting };
    });
  }, [agents]);
  return <>
    <FitCamera controlsRef={controlsRef} />
    <color attach="background" args={["#f4f6fb"]} />
    <fog attach="fog" args={["#0b1020", 30, 54]} />
    <ambientLight intensity={1.65} />
    <hemisphereLight args={["#ffffff", "#d7deea", 1.35]} />
    <directionalLight position={[8, 18, 10]} intensity={2.0} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} />
    <pointLight position={[-8, 6, -4]} intensity={12} color="#b5a7f4" distance={15} />
    <pointLight position={[6, 5, 4]} intensity={10} color="#9bd8e9" distance={14} />
    <OfficeGround />
    {Object.entries(ZONE_LAYOUT).map(([key, zone]) => <Zone key={key} zone={zone} />)}
    
    <mesh position={[0, 0.24, -0.1]} castShadow><boxGeometry args={[0.82, 0.48, 0.45]} /><meshStandardMaterial color="#506079" /></mesh>
    <mesh position={[0, 0.53, -0.04]}><boxGeometry args={[0.67, 0.04, 0.06]} /><meshStandardMaterial color="#f3d48a" emissive="#f3d48a" emissiveIntensity={0.22} /></mesh>
    {positionedAgents.map((agent) => <AgentCharacter key={agent.name} agent={agent} homePosition={agent.home} workPosition={agent.work} waitingPosition={agent.waiting} selected={selectedAgent === agent.name} onSelect={onSelectAgent} />)}
    <ContactShadows position={[0, -0.025, 0]} opacity={0.28} scale={27} blur={2.2} far={9} />
    <OrbitControls ref={controlsRef} makeDefault target={[0, 0.65, 0]} minDistance={18} maxDistance={90} minPolarAngle={0.55} maxPolarAngle={1.28} enableDamping dampingFactor={0.08} enableZoom zoomSpeed={0.65} enablePan={false} />
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
    <Canvas shadows dpr={[1, 1.5]} camera={{ position: [0, 44, 42], fov: 42, near: 0.1, far: 180, up: [0, 1, 0] }} gl={{ antialias: true, alpha: false }}>
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