import { useEffect, useRef, useState } from "react";
import { soundFX } from "../utils/soundFX";

export default function TorchRunner({ speed = 1.2, autoRun = true, interactive = true }) {
  const canvasRef = useRef(null);
  const [soundOn, setSoundOn] = useState(true);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;
    let width = (canvas.width = canvas.parentElement?.clientWidth || window.innerWidth);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 450);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.parentElement?.clientWidth || window.innerWidth;
      height = canvas.height = canvas.parentElement?.clientHeight || 450;
    };
    window.addEventListener("resize", handleResize);

    // Runner Boy State
    let posX = -120;
    let posY = height - 120;
    let legAngle = 0;
    let torchAngle = 0.2;
    let hasCaughtTorch = false;
    let torchFlyX = -50;
    let torchFlyY = posY - 150;
    let mousePos = { x: width * 0.6, y: height * 0.4 };
    let embers = [];

    const handleMouseMove = (e) => {
      if (!interactive) return;
      const rect = canvas.getBoundingClientRect();
      mousePos = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };
    canvas.addEventListener("mousemove", handleMouseMove);

    let lastWhoosh = 0;

    const render = (timestamp) => {
      ctx.clearRect(0, 0, width, height);

      // 1. Move Boy Runner
      if (autoRun) {
        posX += 2.8 * speed;
        if (posX > width + 150) {
          posX = -120;
          hasCaughtTorch = false;
          torchFlyX = -50;
          torchFlyY = posY - 150;
        }
      }

      // Catching the torch animation
      if (posX > 180 && !hasCaughtTorch) {
        hasCaughtTorch = true;
        soundFX.playTorchWhoosh();
      }

      legAngle += 0.18 * speed;
      torchAngle = Math.sin(timestamp * 0.005) * 0.15;

      const currentTorchX = hasCaughtTorch ? posX + 45 : Math.min(posX + 100, 200);
      const currentTorchY = hasCaughtTorch ? posY - 38 + Math.sin(legAngle * 2) * 4 : posY - 80;

      // 2. Draw Dynamic Torch Beam Cone
      ctx.save();
      const beamTargetX = interactive ? mousePos.x : currentTorchX + 400;
      const beamTargetY = interactive ? mousePos.y : currentTorchY - 80;

      const angleToTarget = Math.atan2(beamTargetY - currentTorchY, beamTargetX - currentTorchX);

      // Cone gradient
      const gradient = ctx.createRadialGradient(
        currentTorchX,
        currentTorchY,
        10,
        currentTorchX,
        currentTorchY,
        500
      );
      gradient.addColorStop(0, "rgba(255, 220, 130, 0.45)");
      gradient.addColorStop(0.3, "rgba(240, 180, 70, 0.25)");
      gradient.addColorStop(0.7, "rgba(200, 140, 40, 0.08)");
      gradient.addColorStop(1, "rgba(0, 0, 0, 0)");

      ctx.beginPath();
      ctx.moveTo(currentTorchX, currentTorchY);
      ctx.arc(currentTorchX, currentTorchY, 520, angleToTarget - 0.35, angleToTarget + 0.35);
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();
      ctx.restore();

      // 3. Embers / Flame Particles
      if (Math.random() < 0.6) {
        embers.push({
          x: currentTorchX,
          y: currentTorchY,
          vx: (Math.random() - 0.5) * 1.5 - 1.2,
          vy: -Math.random() * 2.5 - 0.5,
          life: 1.0,
          size: Math.random() * 3 + 1.5,
        });
      }

      for (let i = embers.length - 1; i >= 0; i--) {
        const p = embers[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.035;
        if (p.life <= 0) {
          embers.splice(i, 1);
          continue;
        }
        ctx.fillStyle = `rgba(255, ${Math.floor(140 + p.life * 100)}, 40, ${p.life})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }

      // 4. Torch Flame Glow
      ctx.save();
      const flameGlow = ctx.createRadialGradient(
        currentTorchX,
        currentTorchY,
        2,
        currentTorchX,
        currentTorchY,
        35
      );
      flameGlow.addColorStop(0, "rgba(255, 255, 220, 0.95)");
      flameGlow.addColorStop(0.4, "rgba(255, 180, 50, 0.7)");
      flameGlow.addColorStop(1, "rgba(230, 90, 20, 0)");
      ctx.fillStyle = flameGlow;
      ctx.beginPath();
      ctx.arc(currentTorchX, currentTorchY, 35, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // 5. Draw Silhouette Boy Runner
      ctx.save();
      const boyY = posY + Math.sin(legAngle * 2) * 5; // Bobbing motion
      ctx.fillStyle = "#161311";
      ctx.strokeStyle = "#161311";
      ctx.lineWidth = 6;
      ctx.lineCap = "round";

      // Head with Detective Hat
      ctx.beginPath();
      ctx.arc(posX, boyY - 55, 14, 0, Math.PI * 2);
      ctx.fill();

      // Hat Brim
      ctx.beginPath();
      ctx.ellipse(posX + 3, boyY - 62, 20, 5, 0.2, 0, Math.PI * 2);
      ctx.fill();

      // Body Coat
      ctx.beginPath();
      ctx.moveTo(posX, boyY - 42);
      ctx.lineTo(posX + 8, boyY - 10);
      ctx.lineTo(posX - 12, boyY - 10);
      ctx.closePath();
      ctx.fill();

      // Running Legs (oscillating angles)
      const leg1Angle = Math.sin(legAngle) * 0.7;
      const leg2Angle = -Math.sin(legAngle) * 0.7;

      // Leg 1
      ctx.beginPath();
      ctx.moveTo(posX - 3, boyY - 12);
      ctx.lineTo(posX - 3 + Math.sin(leg1Angle) * 22, boyY + Math.cos(leg1Angle) * 22);
      ctx.stroke();

      // Leg 2
      ctx.beginPath();
      ctx.moveTo(posX + 3, boyY - 12);
      ctx.lineTo(posX + 3 + Math.sin(leg2Angle) * 22, boyY + Math.cos(leg2Angle) * 22);
      ctx.stroke();

      // Arms: Holding Torch arm vs Free arm
      ctx.beginPath();
      ctx.moveTo(posX, boyY - 38);
      ctx.lineTo(currentTorchX - 10, currentTorchY + 15);
      ctx.lineTo(currentTorchX, currentTorchY);
      ctx.stroke();

      // Torch Handle
      ctx.lineWidth = 4;
      ctx.strokeStyle = "#5a3d28";
      ctx.beginPath();
      ctx.moveTo(currentTorchX - 12, currentTorchY + 18);
      ctx.lineTo(currentTorchX + 2, currentTorchY - 5);
      ctx.stroke();

      ctx.restore();

      animId = requestAnimationFrame(render);
    };

    animId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      if (canvas) canvas.removeEventListener("mousemove", handleMouseMove);
    };
  }, [speed, autoRun, interactive]);

  const toggleSound = () => {
    const state = soundFX.toggleSound();
    setSoundOn(state);
    if (state) soundFX.playClick();
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", overflow: "hidden" }}>
      <canvas
        ref={canvasRef}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          pointerEvents: interactive ? "auto" : "none",
          zIndex: 1,
        }}
      />
      <button
        onClick={toggleSound}
        style={{
          position: "absolute",
          top: 10,
          right: 14,
          zIndex: 10,
          background: "rgba(28, 24, 18, 0.85)",
          border: "1px solid var(--gold-dark)",
          color: soundOn ? "var(--gold)" : "var(--text-dim)",
          borderRadius: 6,
          padding: "4px 10px",
          fontSize: 12,
          cursor: "pointer",
        }}
      >
        {soundOn ? "🔊 SOUND ON" : "🔇 SOUND OFF"}
      </button>
    </div>
  );
}
