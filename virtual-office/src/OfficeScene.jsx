import React, { useMemo, useRef } from "react";
import * as THREE from "three";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Html, OrbitControls, ContactShadows } from "@react-three/drei";

const ZONE_LAYOUT = {
  command: { title: "EXECUTIVE HQ", center: [-9.2, -8.1], accent: "#a78bfa", floor: "#293047" },
  research: { title: "RESEARCH & OPPORTUNITY", center: [9.2, -8.1], accent: "#38bdf8", floor: "#1d3545" },
  marketing: { title: "CONTENT & AUDIENCE", center: [-9.2, 0], accent: "#fb7185", floor: "#3a2938" },
  sales: { title: "SALES & MONETIZATION", center: [9.2, 0], accent: "#34d399", floor: "#203b34" },
  operations: { title: "OPERATIONS & FINANCE", center: [-9.2, 8.1], accent: "#f59e0b", floor: "#3a3224" },
  engineering: { title: "TECHNOLOGY & AUTOMATION", center: [9.2, 8.1], accent: "#818cf8", floor: "#292d49" }
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

function OfficeRoom({ zone }) {
  const [x,z]=zone.center;
  return <group>
    <mesh position={[x,0.03,z]} receiveShadow><boxGeometry args={[7.8,0.18,7.2]}/><meshStandardMaterial color={zone.floor}/></mesh>
    <mesh position={[x,0.15,z-3.48]}><boxGeometry args={[7.75,0.06,0.08]}/><meshStandardMaterial color={zone.accent} emissive={zone.accent} emissiveIntensity={0.2}/></mesh>
    {[-3.82,3.82].map(dx=><mesh key={"side"+dx} position={[x+dx,0.94,z]} castShadow><boxGeometry args={[0.18,1.65,7]}/><meshStandardMaterial color="#59647a"/></mesh>)}
    <mesh position={[x,0.94,z-3.52]} castShadow><boxGeometry args={[7.8,1.65,0.18]}/><meshStandardMaterial color="#59647a"/></mesh>
    {[-2.35,2.35].map(dx=><mesh key={"door"+dx} position={[x+dx,0.94,z+3.52]} castShadow><boxGeometry args={[3.1,1.65,0.18]}/><meshStandardMaterial color="#59647a"/></mesh>)}
    {[-2.25,0,2.25].map(dx=>[-1.55,1.55].map(dz=><Desk key={dx+":"+dz} position={[x+dx,0.14,z+dz]} accent={zone.accent} compact/>))}
    <mesh position={[x+2.9,0.38,z-2.55]} castShadow><cylinderGeometry args={[0.38,0.34,0.12,8]}/><meshStandardMaterial color="#806c5d"/></mesh>
    <mesh position={[x+2.9,0.75,z-2.55]} castShadow><sphereGeometry args={[0.25,8,6]}/><meshStandardMaterial color="#4e8d72"/></mesh>
    <Html position={[x,2.1,z-3.1]} center distanceFactor={12} style={{pointerEvents:"none"}}><div className="zone-label" style={{borderColor:zone.accent}}>{zone.title}</div></Html>
  </group>;
}
function MeetingRoom() {
  return <group>
    <mesh position={[0,0.03,0]} receiveShadow><boxGeometry args={[8.6,0.2,7.4]}/><meshStandardMaterial color="#344052"/></mesh>
    {[-4.22,4.22].map(dx=><mesh key={dx} position={[dx,1.08,0]} castShadow><boxGeometry args={[0.18,1.9,7.2]}/><meshStandardMaterial color="#65738b"/></mesh>)}
    <mesh position={[0,1.08,-3.62]} castShadow><boxGeometry args={[8.5,1.9,0.18]}/><meshStandardMaterial color="#65738b"/></mesh>
    {[-2.65,2.65].map(dx=><mesh key={dx} position={[dx,1.08,3.62]} castShadow><boxGeometry args={[3,1.9,0.18]}/><meshStandardMaterial color="#65738b"/></mesh>)}
    <mesh position={[0,0.62,-0.1]} castShadow><boxGeometry args={[3.8,0.18,1.55]}/><meshStandardMaterial color="#9a7658"/></mesh>
    {Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return <group key={i} position={[Math.cos(a)*2.65,0,Math.sin(a)*1.75]}><mesh position={[0,0.34,0]} castShadow><boxGeometry args={[0.62,0.16,0.62]}/><meshStandardMaterial color="#273449"/></mesh><mesh position={[0,0.72,-0.22]} castShadow><boxGeometry args={[0.62,0.7,0.12]}/><meshStandardMaterial color="#475569"/></mesh></group>;})}
    <mesh position={[0,1.3,-3.45]}><boxGeometry args={[2.4,0.9,0.08]}/><meshStandardMaterial color="#172033"/></mesh>
    <Html position={[0,2.2,-3.2]} center distanceFactor={12} style={{pointerEvents:"none"}}><div className="zone-label review-label">AURA · ALL-DIVISION MEETING ROOM</div></Html>
  </group>;
}

function OfficeGround() {
  return <group>
    <mesh position={[0, -0.12, 0]} receiveShadow><boxGeometry args={[28.2, 0.34, 25.2]} /><meshStandardMaterial color="#111827" roughness={0.95} /></mesh>
    <mesh position={[0, 0.06, 0]} receiveShadow><boxGeometry args={[27.8, 0.025, 24.8]} /><meshStandardMaterial color="#0f172a" roughness={0.9} /></mesh>
    {Array.from({ length: 16 }).map((_, i) => <mesh key={"tile-x-" + i} position={[-13.0 + i * 1.73, 0.078, 0]}><boxGeometry args={[0.018, 0.008, 24.2]} /><meshStandardMaterial color="#dce2eb" /></mesh>)}
    {Array.from({ length: 14 }).map((_, i) => <mesh key={"tile-z-" + i} position={[0, 0.079, -11.5 + i * 1.77]}><boxGeometry args={[27.2, 0.008, 0.018]} /><meshStandardMaterial color="#dce2eb" /></mesh>)}
    <mesh position={[0, 0.19, -12.0]} castShadow><boxGeometry args={[5.0, 0.38, 0.32]} /><meshStandardMaterial color="#aab4c2" /></mesh>
    <mesh position={[0, 0.43, -11.81]}><boxGeometry args={[4.6, 0.045, 0.035]} /><meshStandardMaterial color="#9b8cff" emissive="#9b8cff" emissiveIntensity={0.6} /></mesh>
    <Html position={[0, 0.75, -11.75]} center distanceFactor={14} style={{ pointerEvents: "none" }}><div className="brand-sign">AURA <span>REVENUE OPERATIONS</span></div></Html>
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
    const distanceForWidth = 28.2 / (2 * Math.tan(halfFov) * aspect);
    const distanceForDepth = 25.2 / (2 * Math.tan(halfFov));
    const distance = Math.max(distanceForWidth, distanceForDepth) * 1.08;
    const target = new THREE.Vector3(0, 0.7, 0);
    const direction = new THREE.Vector3(0, 0.9, 0.44).normalize();
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
    const counts = {};
    return agents.map((agent) => {
      const zone = ZONE_LAYOUT[agent.zone] || ZONE_LAYOUT.command;
      const slot = counts[agent.zone] || 0;
      counts[agent.zone] = slot + 1;
      const col = slot % 3, row = Math.floor(slot / 3) % 2;
      const dx = (col - 1) * 2.25;
      const deskZ = zone.center[1] + (row === 0 ? -1.55 : 1.55);
      const home = [zone.center[0] + dx, 0.16, deskZ + 0.95];
      const work = [zone.center[0] + dx, 0.16, deskZ + 0.72];
      const waiting = [zone.center[0] + (col - 1) * 0.7, 0.16, zone.center[1] + 2.85];
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
    {Object.entries(ZONE_LAYOUT).map(([key, zone]) => <OfficeRoom key={key} zone={zone} />)}
    
    <mesh position={[0, 0.24, -0.1]} castShadow><boxGeometry args={[0.82, 0.48, 0.45]} /><meshStandardMaterial color="#506079" /></mesh>
    <mesh position={[0, 0.53, -0.04]}><boxGeometry args={[0.67, 0.04, 0.06]} /><meshStandardMaterial color="#f3d48a" emissive="#f3d48a" emissiveIntensity={0.22} /></mesh>
    {positionedAgents.map((agent) => <AgentCharacter key={agent.name} agent={agent} homePosition={agent.home} workPosition={agent.work} waitingPosition={agent.waiting} selected={selectedAgent === agent.name} onSelect={onSelectAgent} />)}
    <ContactShadows position={[0, -0.025, 0]} opacity={0.28} scale={27} blur={2.2} far={9} />
    <OrbitControls ref={controlsRef} makeDefault target={[0, 0.7, 0]} minDistance={18} maxDistance={105} minPolarAngle={0.55} maxPolarAngle={1.28} enableDamping dampingFactor={0.08} enableZoom zoomSpeed={0.65} enablePan={false} />
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