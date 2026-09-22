"""Cinematic, skippable, visual-only intro sequence. No audio, no music,
no autoplay sound of any kind — the animation is pure CSS inside an
isolated iframe (st.components.v1.html) so it always renders identically
regardless of Streamlit's markdown sanitization quirks.
"""
import streamlit.components.v1 as components

INTRO_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body {
    height: 100%;
    background: #030710;
    overflow: hidden;
    font-family: 'Space Grotesk', 'Inter', -apple-system, sans-serif;
  }
  .stage {
    position: relative;
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background:
      radial-gradient(ellipse 60% 45% at 50% 105%, rgba(34,211,238,0.16), transparent 60%),
      radial-gradient(ellipse 90% 60% at 50% -10%, rgba(59,130,246,0.10), transparent 60%),
      #030710;
    overflow: hidden;
  }
  .glow-orb {
    position: absolute;
    width: 460px; height: 460px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34,211,238,0.22), rgba(59,130,246,0.06) 55%, transparent 72%);
    filter: blur(4px);
    opacity: 0;
    animation: orbIn 2.6s ease-out forwards;
  }
  @keyframes orbIn {
    0% { opacity: 0; transform: scale(0.6); }
    100% { opacity: 1; transform: scale(1); }
  }
  .beam {
    position: absolute;
    top: -10%;
    width: 2px;
    height: 55%;
    background: linear-gradient(180deg, rgba(34,211,238,0.55), transparent);
    opacity: 0;
    animation: beamIn 2s ease-out forwards;
    transform-origin: top center;
  }
  @keyframes beamIn { 0% { opacity: 0; } 100% { opacity: 0.55; } }
  .b1 { left: 22%; animation-delay: 0.2s; transform: rotate(-8deg); }
  .b2 { left: 38%; animation-delay: 0.5s; transform: rotate(-2deg); }
  .b3 { left: 58%; animation-delay: 0.35s; transform: rotate(4deg); }
  .b4 { left: 74%; animation-delay: 0.65s; transform: rotate(9deg); }

  .particle {
    position: absolute;
    width: 3px; height: 3px;
    border-radius: 50%;
    background: #22d3ee;
    opacity: 0;
    animation: floatUp 6s linear infinite;
  }
  @keyframes floatUp {
    0% { opacity: 0; transform: translateY(0) translateX(0); }
    10% { opacity: 0.8; }
    90% { opacity: 0.3; }
    100% { opacity: 0; transform: translateY(-220px) translateX(20px); }
  }

  .wordmark { position: relative; text-align: center; z-index: 5; }

  .pl {
    font-size: 6.2rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    background: linear-gradient(90deg, #ffffff, #22d3ee 55%, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    opacity: 0;
    filter: blur(10px);
    animation: revealPL 1.1s ease-out 2.3s forwards;
    line-height: 1;
  }
  @keyframes revealPL {
    0% { opacity: 0; filter: blur(14px); transform: translateY(14px) scale(0.96); letter-spacing: 0.3em; }
    100% { opacity: 1; filter: blur(0); transform: translateY(0) scale(1); letter-spacing: 0.06em; }
  }

  .intelligence {
    font-size: 1.55rem;
    font-weight: 600;
    letter-spacing: 0.5em;
    color: #e8edf7;
    margin-top: 0.4rem;
    opacity: 0;
    animation: fadeUp 1s ease-out 3.15s forwards;
  }
  @keyframes fadeUp {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
  }

  .tagline {
    margin-top: 1.6rem;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: #8b96ad;
    opacity: 0;
    animation: fadeUp 1s ease-out 3.75s forwards;
  }

  .hairline {
    width: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #22d3ee, transparent);
    margin: 1.1rem auto 0;
    animation: growLine 1.2s ease-out 3.5s forwards;
  }
  @keyframes growLine { 0% { width: 0; } 100% { width: 220px; } }

  .pitch {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 32%;
    background: linear-gradient(180deg, transparent, rgba(34,211,238,0.05));
    -webkit-mask-image: linear-gradient(180deg, transparent, black 90%);
    opacity: 0;
    animation: fadeUp 2s ease-out 0.3s forwards;
  }
  .pitch::before {
    content: "";
    position: absolute; inset: 0;
    background-image: repeating-linear-gradient(90deg, rgba(34,211,238,0.08) 0 1px, transparent 1px 90px);
    transform: perspective(300px) rotateX(55deg);
    transform-origin: bottom;
  }
</style>
</head>
<body>
  <div class="stage">
    <div class="pitch"></div>
    <div class="beam b1"></div>
    <div class="beam b2"></div>
    <div class="beam b3"></div>
    <div class="beam b4"></div>
    <div class="glow-orb"></div>
    <div id="particles"></div>
    <div class="wordmark">
      <div class="pl">PL</div>
      <div class="intelligence">INTELLIGENCE</div>
      <div class="hairline"></div>
      <div class="tagline">Data Drives A Deeper Game</div>
    </div>
  </div>
<script>
  const container = document.getElementById('particles');
  for (let i = 0; i < 26; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = (Math.random() * 100) + '%';
    p.style.top = (55 + Math.random() * 40) + '%';
    p.style.animationDelay = (Math.random() * 6) + 's';
    p.style.animationDuration = (5 + Math.random() * 4) + 's';
    container.appendChild(p);
  }
</script>
</body>
</html>
"""


def render_intro(height: int = 560):
    components.html(INTRO_HTML, height=height, scrolling=False)
