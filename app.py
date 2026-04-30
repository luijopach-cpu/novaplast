"""
NovaPLAST CTG — Aplicación Python (Flask) — Archivo único sin dependencias externas
====================================================================================
Cómo ejecutar:
  1. Instalar dependencias:
       pip install flask openpyxl reportlab
  2. Ejecutar:
       python app.py
  3. Abrir en el navegador:
       http://localhost:5000
"""

from flask import Flask, request, send_file, jsonify, session, redirect, url_for, render_template_string
import json, io, os, hashlib, secrets
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ─── CREDENCIALES ADMIN ───────────────────────────────────────────────────────
# Cambia estos valores antes de usar en producción
ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("NovaPLAST2024!".encode()).hexdigest()

# ─── DECORADOR DE PROTECCIÓN ─────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── HTML LOGIN ───────────────────────────────────────────────────────────────
LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>NovaPLAST CTG — Acceso</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --acc: #00FF88;
      --acc2: #00CC6A;
      --accg: rgba(0,255,136,0.12);
      --bg: #060A0F;
      --card: rgba(13,17,23,0.82);
      --border: rgba(48,54,61,0.8);
      --t1: #E6EDF3;
      --t2: #8B949E;
      --t3: #484F58;
      --red: #FF4444;
      --sans: 'Syne', sans-serif;
      --mono: 'JetBrains Mono', monospace;
      --r: 14px;
    }

    body {
      font-family: var(--sans);
      background: var(--bg);
      color: var(--t1);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    /* ── LIGHT PILLAR CANVAS ── */
    #pillar-canvas {
      position: fixed;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 0;
    }

    /* ── OVERLAY OSCURO ── */
    .overlay {
      position: fixed;
      inset: 0;
      background: radial-gradient(ellipse at center, rgba(6,10,15,0.55) 0%, rgba(6,10,15,0.82) 100%);
      z-index: 1;
    }

    /* ── CARD LOGIN ── */
    .login-wrap {
      position: relative;
      z-index: 10;
      width: 100%;
      max-width: 420px;
      padding: 20px;
      animation: fadeUp 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(28px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .login-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 44px 40px 40px;
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      box-shadow:
        0 0 0 1px rgba(0,255,136,0.06),
        0 32px 64px rgba(0,0,0,0.6),
        0 0 80px rgba(0,255,136,0.05);
    }

    /* ── LOGO ── */
    .logo-area {
      text-align: center;
      margin-bottom: 36px;
    }

    .logo-icon {
      font-size: 42px;
      display: block;
      margin-bottom: 10px;
      filter: drop-shadow(0 0 12px rgba(0,255,136,0.5));
      animation: floatIcon 3s ease-in-out infinite;
    }

    @keyframes floatIcon {
      0%, 100% { transform: translateY(0); }
      50%       { transform: translateY(-5px); }
    }

    .logo-name {
      font-size: 22px;
      font-weight: 800;
      color: var(--acc);
      letter-spacing: -0.5px;
    }

    .logo-sub {
      font-size: 11px;
      color: var(--t3);
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-top: 4px;
      font-family: var(--mono);
    }

    .divider {
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--border), transparent);
      margin: 28px 0;
    }

    /* ── FORM ── */
    .fg { margin-bottom: 18px; }

    .fl {
      display: block;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1.5px;
      color: var(--t3);
      margin-bottom: 8px;
      font-family: var(--mono);
    }

    .fi-wrap {
      position: relative;
    }

    .fi-icon {
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 15px;
      opacity: 0.4;
      pointer-events: none;
    }

    .fi {
      width: 100%;
      padding: 13px 14px 13px 42px;
      background: rgba(6,10,15,0.7);
      border: 1px solid var(--border);
      border-radius: var(--r);
      color: var(--t1);
      font-family: var(--sans);
      font-size: 15px;
      transition: border-color 0.2s, box-shadow 0.2s;
      outline: none;
    }

    .fi::placeholder { color: var(--t3); }

    .fi:focus {
      border-color: var(--acc);
      box-shadow: 0 0 0 3px var(--accg), 0 0 20px rgba(0,255,136,0.08);
    }

    /* ── BOTÓN ── */
    .btn-login {
      width: 100%;
      padding: 14px;
      background: var(--acc);
      color: #060A0F;
      border: none;
      border-radius: var(--r);
      font-family: var(--sans);
      font-size: 15px;
      font-weight: 800;
      cursor: pointer;
      letter-spacing: 0.5px;
      transition: all 0.2s;
      margin-top: 8px;
      position: relative;
      overflow: hidden;
    }

    .btn-login::after {
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.15) 50%, transparent 70%);
      transform: translateX(-100%);
      transition: transform 0.5s;
    }

    .btn-login:hover {
      background: var(--acc2);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,255,136,0.3);
    }

    .btn-login:hover::after { transform: translateX(100%); }
    .btn-login:active { transform: translateY(0); }

    /* ── ERROR ── */
    .error-msg {
      background: rgba(255,68,68,0.1);
      border: 1px solid rgba(255,68,68,0.3);
      border-radius: var(--r);
      padding: 12px 16px;
      font-size: 13px;
      color: var(--red);
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 8px;
      animation: shake 0.4s ease;
    }

    @keyframes shake {
      0%,100% { transform: translateX(0); }
      20%,60%  { transform: translateX(-6px); }
      40%,80%  { transform: translateX(6px); }
    }

    /* ── FOOTER ── */
    .login-footer {
      text-align: center;
      margin-top: 28px;
      font-size: 11px;
      color: var(--t3);
      font-family: var(--mono);
    }

    .login-footer span { color: var(--acc); }
  </style>
</head>
<body>

  <!-- FONDO LIGHT PILLAR (WebGL) -->
  <canvas id="pillar-canvas"></canvas>
  <div class="overlay"></div>

  <!-- CARD DE LOGIN -->
  <div class="login-wrap">
    <div class="login-card">
      <div class="logo-area">
        <span class="logo-icon">🌴</span>
        <div class="logo-name">NovaPLAST CTG</div>
        <div class="logo-sub">Panel de Administración</div>
      </div>

      <div class="divider"></div>

      {% if error %}
      <div class="error-msg">⚠️ {{ error }}</div>
      {% endif %}

      <form method="POST" action="/login">
        <div class="fg">
          <label class="fl">Usuario</label>
          <div class="fi-wrap">
            <span class="fi-icon">👤</span>
            <input class="fi" type="text" name="username" placeholder="admin" autocomplete="username" required autofocus/>
          </div>
        </div>
        <div class="fg">
          <label class="fl">Contraseña</label>
          <div class="fi-wrap">
            <span class="fi-icon">🔑</span>
            <input class="fi" type="password" name="password" placeholder="••••••••••••" autocomplete="current-password" required/>
          </div>
        </div>
        <button class="btn-login" type="submit">Ingresar al sistema →</button>
      </form>

      <div class="login-footer">
        Sistema seguro · <span>NovaPLAST CTG</span> · © {{ year }}
      </div>
    </div>
  </div>

  <!-- SOFT AURORA WEBGL -->
  <script>
  (function(){
    var canvas = document.getElementById('pillar-canvas');
    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if(!gl){ canvas.style.background='#060A0F'; return; }

    var VS = [
      'attribute vec2 position;',
      'attribute vec2 uv;',
      'varying vec2 vUv;',
      'void main(){',
      '  vUv = uv;',
      '  gl_Position = vec4(position, 0.0, 1.0);',
      '}'
    ].join('\n');

    var FS = [
      'precision highp float;',
      'uniform float uTime;',
      'uniform vec3 uResolution;',
      'uniform float uSpeed;',
      'uniform float uScale;',
      'uniform float uBrightness;',
      'uniform vec3 uColor1;',
      'uniform vec3 uColor2;',
      'uniform float uNoiseFreq;',
      'uniform float uNoiseAmp;',
      'uniform float uBandHeight;',
      'uniform float uBandSpread;',
      'uniform float uOctaveDecay;',
      'uniform float uLayerOffset;',
      'uniform float uColorSpeed;',
      'uniform vec2 uMouse;',
      'uniform float uMouseInfluence;',
      'uniform bool uEnableMouse;',
      '#define TAU 6.28318',
      'vec3 gradientHash(vec3 p){',
      '  p=vec3(dot(p,vec3(127.1,311.7,234.6)),dot(p,vec3(269.5,183.3,198.3)),dot(p,vec3(169.5,283.3,156.9)));',
      '  vec3 h=fract(sin(p)*43758.5453123);',
      '  float phi=acos(2.0*h.x-1.0);',
      '  float theta=TAU*h.y;',
      '  return vec3(cos(theta)*sin(phi),sin(theta)*cos(phi),cos(phi));',
      '}',
      'float quinticSmooth(float t){float t2=t*t;float t3=t*t2;return 6.0*t3*t2-15.0*t2*t2+10.0*t3;}',
      'vec3 cosineGradient(float t,vec3 a,vec3 b,vec3 c,vec3 d){return a+b*cos(TAU*(c*t+d));}',
      'float perlin3D(float amplitude,float frequency,float px,float py,float pz){',
      '  float x=px*frequency;float y=py*frequency;',
      '  float fx=floor(x);float fy=floor(y);float fz=floor(pz);',
      '  float cx=ceil(x);float cy=ceil(y);float cz=ceil(pz);',
      '  vec3 g000=gradientHash(vec3(fx,fy,fz));vec3 g100=gradientHash(vec3(cx,fy,fz));',
      '  vec3 g010=gradientHash(vec3(fx,cy,fz));vec3 g110=gradientHash(vec3(cx,cy,fz));',
      '  vec3 g001=gradientHash(vec3(fx,fy,cz));vec3 g101=gradientHash(vec3(cx,fy,cz));',
      '  vec3 g011=gradientHash(vec3(fx,cy,cz));vec3 g111=gradientHash(vec3(cx,cy,cz));',
      '  float d000=dot(g000,vec3(x-fx,y-fy,pz-fz));float d100=dot(g100,vec3(x-cx,y-fy,pz-fz));',
      '  float d010=dot(g010,vec3(x-fx,y-cy,pz-fz));float d110=dot(g110,vec3(x-cx,y-cy,pz-fz));',
      '  float d001=dot(g001,vec3(x-fx,y-fy,pz-cz));float d101=dot(g101,vec3(x-cx,y-fy,pz-cz));',
      '  float d011=dot(g011,vec3(x-fx,y-cy,pz-cz));float d111=dot(g111,vec3(x-cx,y-cy,pz-cz));',
      '  float sx=quinticSmooth(x-fx);float sy=quinticSmooth(y-fy);float sz=quinticSmooth(pz-fz);',
      '  float lx00=mix(d000,d100,sx);float lx10=mix(d010,d110,sx);',
      '  float lx01=mix(d001,d101,sx);float lx11=mix(d011,d111,sx);',
      '  float ly0=mix(lx00,lx10,sy);float ly1=mix(lx01,lx11,sy);',
      '  return amplitude*mix(ly0,ly1,sz);',
      '}',
      'float auroraGlow(float t,vec2 shift){',
      '  vec2 uv=gl_FragCoord.xy/uResolution.y;',
      '  uv+=shift;',
      '  float noiseVal=0.0;float freq=uNoiseFreq;float amp=uNoiseAmp;',
      '  vec2 samplePos=uv*uScale;',
      '  for(float i=0.0;i<3.0;i+=1.0){',
      '    noiseVal+=perlin3D(amp,freq,samplePos.x,samplePos.y,t);',
      '    amp*=uOctaveDecay;freq*=2.0;',
      '  }',
      '  float yBand=uv.y*10.0-uBandHeight*10.0;',
      '  return 0.3*max(exp(uBandSpread*(1.0-1.1*abs(noiseVal+yBand))),0.0);',
      '}',
      'void main(){',
      '  vec2 uv=gl_FragCoord.xy/uResolution.xy;',
      '  float t=uSpeed*0.4*uTime;',
      '  vec2 shift=vec2(0.0);',
      '  if(uEnableMouse){shift=(uMouse-0.5)*uMouseInfluence;}',
      '  vec3 col=vec3(0.0);',
      '  col+=0.99*auroraGlow(t,shift)*cosineGradient(uv.x+uTime*uSpeed*0.2*uColorSpeed,vec3(0.5),vec3(0.5),vec3(1.0),vec3(0.3,0.20,0.20))*uColor1;',
      '  col+=0.99*auroraGlow(t+uLayerOffset,shift)*cosineGradient(uv.x+uTime*uSpeed*0.1*uColorSpeed,vec3(0.5),vec3(0.5),vec3(2.0,1.0,0.0),vec3(0.5,0.20,0.25))*uColor2;',
      '  col*=uBrightness;',
      '  float alpha=clamp(length(col),0.0,1.0);',
      '  gl_FragColor=vec4(col,alpha);',
      '}'
    ].join('\n');

    function mkShader(type,src){
      var s=gl.createShader(type);
      gl.shaderSource(s,src);gl.compileShader(s);
      if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))console.error(gl.getShaderInfoLog(s));
      return s;
    }
    var prog=gl.createProgram();
    gl.attachShader(prog,mkShader(gl.VERTEX_SHADER,VS));
    gl.attachShader(prog,mkShader(gl.FRAGMENT_SHADER,FS));
    gl.linkProgram(prog);
    if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){console.error(gl.getProgramInfoLog(prog));return;}
    gl.useProgram(prog);

    // Triángulo que cubre toda la pantalla + UVs
    var verts=new Float32Array([-1,-1, 3,-1, -1,3]);
    var uvs=new Float32Array([0,0, 2,0, 0,2]);
    function mkBuf(data){var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);return b;}
    var vBuf=mkBuf(verts), uBuf=mkBuf(uvs);

    function bindAttr(buf,name,size){
      gl.bindBuffer(gl.ARRAY_BUFFER,buf);
      var loc=gl.getAttribLocation(prog,name);
      if(loc>=0){gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,0,0);}
    }
    bindAttr(vBuf,'position',2);
    bindAttr(uBuf,'uv',2);

    var U=function(n){return gl.getUniformLocation(prog,n);};
    var uTime=U('uTime'),uRes=U('uResolution'),uSpeed=U('uSpeed'),uScale=U('uScale');
    var uBright=U('uBrightness'),uC1=U('uColor1'),uC2=U('uColor2');
    var uNFreq=U('uNoiseFreq'),uNAmp=U('uNoiseAmp'),uBH=U('uBandHeight');
    var uBS=U('uBandSpread'),uOD=U('uOctaveDecay'),uLO=U('uLayerOffset');
    var uCS=U('uColorSpeed'),uMouse=U('uMouse'),uMI=U('uMouseInfluence'),uEM=U('uEnableMouse');

    // Parámetros del Usage
    gl.uniform1f(uSpeed,  0.7);
    gl.uniform1f(uScale,  1.5);
    gl.uniform1f(uBright, 1.1);
    gl.uniform3f(uC1, 0.969, 0.969, 0.969); // #f7f7f7
    gl.uniform3f(uC2, 0.0,   1.0,   0.043); // #00ff0b
    gl.uniform1f(uNFreq,  2.5);
    gl.uniform1f(uNAmp,   1.0);
    gl.uniform1f(uBH,     0.5);
    gl.uniform1f(uBS,     1.4);
    gl.uniform1f(uOD,     0.1);
    gl.uniform1f(uLO,     0.0);
    gl.uniform1f(uCS,     1.0);
    gl.uniform1f(uMI,     0.25);
    gl.uniform1i(uEM,     1);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);

    var mouse=[0.5,0.5], target=[0.5,0.5];
    canvas.addEventListener('mousemove',function(e){
      var r=canvas.getBoundingClientRect();
      target[0]=(e.clientX-r.left)/r.width;
      target[1]=1.0-(e.clientY-r.top)/r.height;
    });
    canvas.addEventListener('mouseleave',function(){target=[0.5,0.5];});

    function resize(){
      canvas.width=window.innerWidth;canvas.height=window.innerHeight;
      gl.viewport(0,0,canvas.width,canvas.height);
      gl.uniform3f(uRes,canvas.width,canvas.height,canvas.width/canvas.height);
    }
    window.addEventListener('resize',resize);resize();

    var t0=performance.now();
    function loop(now){
      mouse[0]+= 0.05*(target[0]-mouse[0]);
      mouse[1]+= 0.05*(target[1]-mouse[1]);
      gl.uniform2f(uMouse,mouse[0],mouse[1]);
      gl.uniform1f(uTime,(now-t0)*0.001);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLES,0,3);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  })();
  </script>

</body>
</html>"""


LOGOUT_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>NovaPLAST CTG — Sesión cerrada</title>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    :root{
      --acc:#00FF88;--bg:#060A0F;--card:rgba(13,17,23,0.85);
      --border:rgba(48,54,61,0.8);--t1:#E6EDF3;--t2:#8B949E;--t3:#484F58;
      --sans:'Syne',sans-serif;--mono:'JetBrains Mono',monospace;
    }
    body{font-family:var(--sans);background:var(--bg);color:var(--t1);
         min-height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden;}

    #pillar-canvas{position:fixed;inset:0;width:100%;height:100%;z-index:0;}

    .overlay{position:fixed;inset:0;
      background:radial-gradient(ellipse at center,rgba(6,10,15,0.55) 0%,rgba(6,10,15,0.88) 100%);
      z-index:1;}

    .wrap{position:relative;z-index:10;width:100%;max-width:400px;padding:20px;
          animation:fadeUp .7s cubic-bezier(.22,1,.36,1) both;}
    @keyframes fadeUp{from{opacity:0;transform:translateY(28px);}to{opacity:1;transform:translateY(0);}}

    .card{background:var(--card);border:1px solid var(--border);border-radius:20px;
          padding:44px 40px 40px;backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
          box-shadow:0 0 0 1px rgba(0,255,136,.06),0 32px 64px rgba(0,0,0,.6),0 0 80px rgba(0,255,136,.05);
          text-align:center;}

    .icon{font-size:48px;display:block;margin-bottom:14px;
          filter:drop-shadow(0 0 14px rgba(0,255,136,.5));
          animation:float 3s ease-in-out infinite;}
    @keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-6px);}}

    .title{font-size:22px;font-weight:800;color:var(--acc);margin-bottom:6px;}
    .sub{font-size:13px;color:var(--t2);margin-bottom:28px;line-height:1.6;}

    .divider{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin-bottom:28px;}

    .btn-login{display:inline-flex;align-items:center;gap:8px;
               padding:13px 28px;background:var(--acc);color:#060A0F;
               border:none;border-radius:12px;font-family:var(--sans);
               font-size:15px;font-weight:800;cursor:pointer;text-decoration:none;
               transition:all .2s;position:relative;overflow:hidden;}
    .btn-login::after{content:'';position:absolute;inset:0;
      background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.15) 50%,transparent 70%);
      transform:translateX(-100%);transition:transform .5s;}
    .btn-login:hover{background:#00CC6A;transform:translateY(-2px);
                     box-shadow:0 8px 24px rgba(0,255,136,.3);}
    .btn-login:hover::after{transform:translateX(100%);}

    .footer{margin-top:24px;font-size:11px;color:var(--t3);font-family:var(--mono);}
    .footer span{color:var(--acc);}
  </style>
</head>
<body>
  <canvas id="pillar-canvas"></canvas>
  <div class="overlay"></div>

  <div class="wrap">
    <div class="card">
      <span class="icon">🌴</span>
      <div class="title">Sesión cerrada</div>
      <div class="sub">Has salido de <strong>NovaPLAST CTG</strong> de forma segura.<br>Tus datos han quedado protegidos.</div>
      <div class="divider"></div>
      <a class="btn-login" href="/login">🔐 Volver a ingresar</a>
      <div class="footer">Sistema seguro · <span>NovaPLAST CTG</span> · © {{ year }}</div>
    </div>
  </div>

  <script>
  (function(){
    var canvas=document.getElementById('pillar-canvas');
    var gl=canvas.getContext('webgl')||canvas.getContext('experimental-webgl');
    if(!gl){canvas.style.background='#060A0F';return;}

    var VS=[
      'attribute vec2 position;attribute vec2 uv;varying vec2 vUv;',
      'void main(){vUv=uv;gl_Position=vec4(position,0.0,1.0);}'
    ].join('\n');

    var FS=[
      'precision highp float;',
      'uniform float uTime;uniform vec3 uResolution;uniform float uSpeed;uniform float uScale;',
      'uniform float uBrightness;uniform vec3 uColor1;uniform vec3 uColor2;',
      'uniform float uNoiseFreq;uniform float uNoiseAmp;uniform float uBandHeight;',
      'uniform float uBandSpread;uniform float uOctaveDecay;uniform float uLayerOffset;',
      'uniform float uColorSpeed;uniform vec2 uMouse;uniform float uMouseInfluence;uniform bool uEnableMouse;',
      '#define TAU 6.28318',
      'vec3 gradientHash(vec3 p){',
      '  p=vec3(dot(p,vec3(127.1,311.7,234.6)),dot(p,vec3(269.5,183.3,198.3)),dot(p,vec3(169.5,283.3,156.9)));',
      '  vec3 h=fract(sin(p)*43758.5453123);float phi=acos(2.0*h.x-1.0);float theta=TAU*h.y;',
      '  return vec3(cos(theta)*sin(phi),sin(theta)*cos(phi),cos(phi));',
      '}',
      'float quinticSmooth(float t){float t2=t*t;float t3=t*t2;return 6.0*t3*t2-15.0*t2*t2+10.0*t3;}',
      'vec3 cosineGradient(float t,vec3 a,vec3 b,vec3 c,vec3 d){return a+b*cos(TAU*(c*t+d));}',
      'float perlin3D(float amplitude,float frequency,float px,float py,float pz){',
      '  float x=px*frequency;float y=py*frequency;',
      '  float fx=floor(x);float fy=floor(y);float fz=floor(pz);',
      '  float cx=ceil(x);float cy=ceil(y);float cz=ceil(pz);',
      '  vec3 g000=gradientHash(vec3(fx,fy,fz));vec3 g100=gradientHash(vec3(cx,fy,fz));',
      '  vec3 g010=gradientHash(vec3(fx,cy,fz));vec3 g110=gradientHash(vec3(cx,cy,fz));',
      '  vec3 g001=gradientHash(vec3(fx,fy,cz));vec3 g101=gradientHash(vec3(cx,fy,cz));',
      '  vec3 g011=gradientHash(vec3(fx,cy,cz));vec3 g111=gradientHash(vec3(cx,cy,cz));',
      '  float d000=dot(g000,vec3(x-fx,y-fy,pz-fz));float d100=dot(g100,vec3(x-cx,y-fy,pz-fz));',
      '  float d010=dot(g010,vec3(x-fx,y-cy,pz-fz));float d110=dot(g110,vec3(x-cx,y-cy,pz-fz));',
      '  float d001=dot(g001,vec3(x-fx,y-fy,pz-cz));float d101=dot(g101,vec3(x-cx,y-fy,pz-cz));',
      '  float d011=dot(g011,vec3(x-fx,y-cy,pz-cz));float d111=dot(g111,vec3(x-cx,y-cy,pz-cz));',
      '  float sx=quinticSmooth(x-fx);float sy=quinticSmooth(y-fy);float sz=quinticSmooth(pz-fz);',
      '  float lx00=mix(d000,d100,sx);float lx10=mix(d010,d110,sx);',
      '  float lx01=mix(d001,d101,sx);float lx11=mix(d011,d111,sx);',
      '  float ly0=mix(lx00,lx10,sy);float ly1=mix(lx01,lx11,sy);',
      '  return amplitude*mix(ly0,ly1,sz);',
      '}',
      'float auroraGlow(float t,vec2 shift){',
      '  vec2 uv=gl_FragCoord.xy/uResolution.y;uv+=shift;',
      '  float noiseVal=0.0;float freq=uNoiseFreq;float amp=uNoiseAmp;',
      '  vec2 sp=uv*uScale;',
      '  for(float i=0.0;i<3.0;i+=1.0){noiseVal+=perlin3D(amp,freq,sp.x,sp.y,t);amp*=uOctaveDecay;freq*=2.0;}',
      '  float yBand=uv.y*10.0-uBandHeight*10.0;',
      '  return 0.3*max(exp(uBandSpread*(1.0-1.1*abs(noiseVal+yBand))),0.0);',
      '}',
      'void main(){',
      '  vec2 uv=gl_FragCoord.xy/uResolution.xy;float t=uSpeed*0.4*uTime;',
      '  vec2 shift=vec2(0.0);if(uEnableMouse){shift=(uMouse-0.5)*uMouseInfluence;}',
      '  vec3 col=vec3(0.0);',
      '  col+=0.99*auroraGlow(t,shift)*cosineGradient(uv.x+uTime*uSpeed*0.2*uColorSpeed,vec3(0.5),vec3(0.5),vec3(1.0),vec3(0.3,0.20,0.20))*uColor1;',
      '  col+=0.99*auroraGlow(t+uLayerOffset,shift)*cosineGradient(uv.x+uTime*uSpeed*0.1*uColorSpeed,vec3(0.5),vec3(0.5),vec3(2.0,1.0,0.0),vec3(0.5,0.20,0.25))*uColor2;',
      '  col*=uBrightness;float alpha=clamp(length(col),0.0,1.0);',
      '  gl_FragColor=vec4(col,alpha);',
      '}'
    ].join('\n');

    function mkShader(type,src){
      var s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);
      if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))console.error(gl.getShaderInfoLog(s));
      return s;
    }
    var prog=gl.createProgram();
    gl.attachShader(prog,mkShader(gl.VERTEX_SHADER,VS));
    gl.attachShader(prog,mkShader(gl.FRAGMENT_SHADER,FS));
    gl.linkProgram(prog);
    if(!gl.getProgramParameter(prog,gl.LINK_STATUS)){console.error(gl.getProgramInfoLog(prog));return;}
    gl.useProgram(prog);

    var verts=new Float32Array([-1,-1,3,-1,-1,3]);
    var uvs=new Float32Array([0,0,2,0,0,2]);
    function mkBuf(data){var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);return b;}
    var vBuf=mkBuf(verts),uBuf=mkBuf(uvs);
    function bindAttr(buf,name,size){
      gl.bindBuffer(gl.ARRAY_BUFFER,buf);
      var loc=gl.getAttribLocation(prog,name);
      if(loc>=0){gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,0,0);}
    }
    bindAttr(vBuf,'position',2);bindAttr(uBuf,'uv',2);

    var U=function(n){return gl.getUniformLocation(prog,n);};
    gl.uniform1f(U('uSpeed'),0.7);gl.uniform1f(U('uScale'),1.5);gl.uniform1f(U('uBrightness'),1.1);
    gl.uniform3f(U('uColor1'),0.969,0.969,0.969);gl.uniform3f(U('uColor2'),0.0,1.0,0.043);
    gl.uniform1f(U('uNoiseFreq'),2.5);gl.uniform1f(U('uNoiseAmp'),1.0);
    gl.uniform1f(U('uBandHeight'),0.5);gl.uniform1f(U('uBandSpread'),1.4);
    gl.uniform1f(U('uOctaveDecay'),0.1);gl.uniform1f(U('uLayerOffset'),0.0);
    gl.uniform1f(U('uColorSpeed'),1.0);gl.uniform1f(U('uMouseInfluence'),0.25);
    gl.uniform1i(U('uEnableMouse'),1);

    gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);

    var uTime=U('uTime'),uRes=U('uResolution'),uMouse=U('uMouse');
    var mouse=[0.5,0.5],target=[0.5,0.5];
    canvas.addEventListener('mousemove',function(e){
      var r=canvas.getBoundingClientRect();
      target[0]=(e.clientX-r.left)/r.width;
      target[1]=1.0-(e.clientY-r.top)/r.height;
    });
    canvas.addEventListener('mouseleave',function(){target=[0.5,0.5];});

    function resize(){
      canvas.width=window.innerWidth;canvas.height=window.innerHeight;
      gl.viewport(0,0,canvas.width,canvas.height);
      gl.uniform3f(uRes,canvas.width,canvas.height,canvas.width/canvas.height);
    }
    window.addEventListener('resize',resize);resize();

    var t0=performance.now();
    function loop(now){
      mouse[0]+=0.05*(target[0]-mouse[0]);mouse[1]+=0.05*(target[1]-mouse[1]);
      gl.uniform2f(uMouse,mouse[0],mouse[1]);
      gl.uniform1f(uTime,(now-t0)*0.001);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLES,0,3);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  })();
  </script>
</body>
</html>"""

# ─── UTILIDADES ──────────────────────────────────────────────────────────────

def f_cop(val):
    return f"$ {int(round(val)):,}".replace(",", ".")

# ─── HTML INCRUSTADO ─────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>NovaPLAST CTG</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
  <style>
    :root{--bg:#060A0F;--bg2:#0D1117;--card:#161B22;--card2:#1C2128;--hover:#222831;--border:#30363D;--border2:#484F58;--acc:#00FF88;--acc2:#00CC6A;--accg:rgba(0,255,136,.15);--blue:#58A6FF;--blueg:rgba(88,166,255,.15);--orange:#FF9500;--red:#FF4444;--redg:rgba(255,68,68,.15);--yellow:#FFCC00;--purple:#BD93F9;--t1:#E6EDF3;--t2:#8B949E;--t3:#484F58;--sans:'Space Grotesk',sans-serif;--mono:'JetBrains Mono',monospace;--r:12px;--rs:8px;}
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
    body{font-family:var(--sans);background:var(--bg);color:var(--t1);min-height:100vh;overflow-x:hidden;}
    ::-webkit-scrollbar{width:6px;height:6px;} ::-webkit-scrollbar-track{background:var(--bg2);} ::-webkit-scrollbar-thumb{background:var(--border);border-radius:99px;}
    /* SIDEBAR */
    .sidebar{position:fixed;left:0;top:0;bottom:0;width:220px;background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;z-index:100;}
    .sb-logo{padding:24px 20px 20px;border-bottom:1px solid var(--border);}
    .sb-logo .icon{font-size:28px;display:block;margin-bottom:6px;}
    .sb-logo .name{font-size:16px;font-weight:700;color:var(--acc);}
    .sb-logo .sub{font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1.5px;margin-top:2px;}
    .sb-nav{padding:16px 12px;flex:1;}
    .nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:var(--rs);cursor:pointer;color:var(--t2);font-size:13.5px;font-weight:500;transition:all .2s;margin-bottom:2px;border:1px solid transparent;user-select:none;}
    .nav-item:hover{background:var(--hover);color:var(--t1);}
    .nav-item.active{background:var(--accg);color:var(--acc);border-color:rgba(0,255,136,.2);}
    .nav-item .ni{font-size:16px;width:20px;text-align:center;}
    .sb-foot{padding:16px;border-top:1px solid var(--border);font-size:11px;color:var(--t3);}
    .btn-session,.btn-shutdown{display:flex;align-items:center;gap:8px;width:100%;padding:9px 12px;border-radius:8px;font-family:var(--sans);font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--t2);transition:all .2s;margin-top:6px;white-space:nowrap;}
    .btn-session:hover{border-color:var(--acc);color:var(--acc);background:var(--accg);}
    .btn-shutdown:hover{border-color:var(--red);color:var(--red);background:var(--redg);}
    #particles-canvas{position:fixed;top:0;left:220px;right:0;bottom:0;width:calc(100% - 220px);height:100%;z-index:0;pointer-events:none;}
    .main{position:relative;z-index:1;}
    .sidebar{z-index:100;}
    /* MAIN */
    .main{margin-left:220px;min-height:100vh;}
    .topbar{background:var(--bg2);border-bottom:1px solid var(--border);padding:16px 32px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:50;}
    .topbar h1{font-size:18px;font-weight:600;}
    .topbar p{font-size:12px;color:var(--t3);margin-top:2px;}
    .badge-live{display:flex;align-items:center;gap:6px;background:var(--accg);border:1px solid var(--acc);border-radius:99px;padding:4px 12px;font-size:11px;color:var(--acc);font-weight:600;}
    .badge-live::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--acc);animation:pulse 1.5s infinite;}
    @keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(.8);}}
    /* PAGES */
    .page{display:none;padding:32px;}
    .page.active{display:block;}
    .sec-hdr{margin-bottom:28px;}
    .sec-hdr h2{font-size:24px;font-weight:700;display:flex;align-items:center;gap:10px;}
    .sec-hdr p{font-size:14px;color:var(--t2);margin-top:6px;}
    /* GRID */
    .g2{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
    .g3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;}
    .g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}
    /* CARDS */
    .card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:24px;}
    .card-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;}
    .card-ttl{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:var(--t3);}
    /* FORMS */
    .fg{margin-bottom:20px;}
    .fl{display:block;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--t3);margin-bottom:8px;}
    .fi,.fs{width:100%;padding:11px 14px;background:var(--bg2);border:1px solid var(--border);border-radius:var(--rs);color:var(--t1);font-family:var(--sans);font-size:14px;transition:border-color .2s,box-shadow .2s;outline:none;appearance:none;}
    .fi:focus,.fs:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--accg);}
    .fi::placeholder{color:var(--t3);}
    .fs option{background:var(--card);}
    .fr{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
    /* OBJETO GRID */
    .obj-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px;}
    .obj-card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--rs);padding:14px 10px;cursor:pointer;text-align:center;transition:all .2s;user-select:none;}
    .obj-card:hover{border-color:var(--acc);background:var(--accg);transform:translateY(-2px);}
    .obj-card.selected{border-color:var(--acc);background:var(--accg);box-shadow:0 0 24px rgba(0,255,136,.2);}
    .obj-card .oi{font-size:24px;display:block;margin-bottom:6px;}
    .obj-card .on{font-size:11px;font-weight:600;color:var(--t2);}
    .obj-card.selected .on{color:var(--acc);}
    /* MATERIAL CHIPS */
    .mat-chips{display:flex;flex-wrap:wrap;gap:10px;}
    .mat-chip{display:flex;align-items:center;gap:8px;padding:8px 14px;border-radius:99px;border:1.5px solid var(--border);cursor:pointer;font-size:13px;font-weight:600;transition:all .2s;user-select:none;background:var(--bg2);}
    .mat-chip:hover{border-color:currentColor;transform:scale(1.03);}
    .mat-chip.selected{background:var(--accg);border-color:var(--acc);color:var(--acc);}
    .mat-chip .cd{width:10px;height:10px;border-radius:50%;}
    .mat-chip .cc{font-family:var(--mono);font-size:10px;background:rgba(255,255,255,.1);padding:2px 6px;border-radius:4px;}
    /* BUTTONS */
    .btn{display:inline-flex;align-items:center;gap:8px;padding:11px 22px;border-radius:var(--rs);font-family:var(--sans);font-size:14px;font-weight:600;cursor:pointer;border:none;transition:all .2s;white-space:nowrap;}
    .btn-p{background:var(--acc);color:#060A0F;}
    .btn-p:hover{background:var(--acc2);transform:translateY(-1px);}
    .btn-p:disabled{opacity:.4;cursor:not-allowed;transform:none;}
    .btn-s{background:transparent;color:var(--t2);border:1px solid var(--border);}
    .btn-s:hover{border-color:var(--border2);color:var(--t1);}
    .btn-d{background:var(--redg);color:var(--red);border:1px solid var(--red);}
    .btn-d:hover{background:var(--red);color:#fff;}
    .btn-b{background:var(--blueg);color:var(--blue);border:1px solid var(--blue);}
    .btn-b:hover{background:var(--blue);color:#fff;}
    .btn-g{background:var(--accg);color:var(--acc);border:1px solid var(--acc);}
    .btn-g:hover{background:var(--acc);color:#060A0F;}
    .btn-sm{padding:7px 14px;font-size:12px;}
    .btn-grp{display:flex;gap:10px;flex-wrap:wrap;}
    /* APP LIST */
    .app-list{display:flex;flex-direction:column;gap:8px;}
    .app-item{background:var(--bg2);border:1px solid var(--border);border-radius:var(--rs);padding:12px 14px;cursor:pointer;transition:all .2s;display:flex;justify-content:space-between;align-items:center;}
    .app-item:hover{border-color:var(--acc);}
    .app-item.selected{border-color:var(--acc);background:var(--accg);}
    .ai-name{font-size:13px;font-weight:600;}
    .ai-mkt{font-size:11px;color:var(--t3);margin-top:2px;}
    .ai-kg{font-size:11px;font-family:var(--mono);color:var(--t3);}
    .vbar{width:60px;height:4px;background:var(--card2);border-radius:99px;overflow:hidden;margin-top:4px;}
    .vfill{height:100%;background:var(--acc);border-radius:99px;}
    /* MARGEN */
    .mrg-btns{display:flex;gap:8px;}
    .mrg-btn{flex:1;padding:9px;border-radius:var(--rs);border:1px solid var(--border);background:var(--bg2);color:var(--t2);cursor:pointer;text-align:center;font-size:12px;font-weight:600;font-family:var(--sans);transition:all .2s;}
    .mrg-btn:hover{border-color:var(--border2);color:var(--t1);}
    .mrg-btn.selected{border-color:var(--acc);color:var(--acc);background:var(--accg);}
    .mrg-btn .mp{font-size:16px;display:block;font-family:var(--mono);}
    /* PRICE INPUT */
    .pig{display:flex;align-items:center;border:1px solid var(--border);border-radius:var(--rs);overflow:hidden;transition:border-color .2s;}
    .pig:focus-within{border-color:var(--acc);}
    .pp{background:var(--card2);padding:11px 12px;font-size:13px;color:var(--t3);font-family:var(--mono);border-right:1px solid var(--border);}
    .ps{background:var(--card2);padding:11px 12px;font-size:11px;color:var(--t3);border-left:1px solid var(--border);}
    .pi{flex:1;border:none!important;border-radius:0!important;box-shadow:none!important;}
    /* METRICS */
    .mc{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px;position:relative;overflow:hidden;}
    .mc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
    .mc.green::before{background:var(--acc);}
    .mc.blue::before{background:var(--blue);}
    .mc.orange::before{background:var(--orange);}
    .mc.purple::before{background:var(--purple);}
    .mc.cyan::before{background:#00BCD4;}
    .mi{font-size:22px;margin-bottom:12px;}
    .mt{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--t3);}
    .mv{font-size:24px;font-weight:700;font-family:var(--mono);margin-top:4px;}
    .mc.green .mv{color:var(--acc);}
    .mc.blue .mv{color:var(--blue);}
    .mc.orange .mv{color:var(--orange);}
    .mc.purple .mv{color:var(--purple);}
    .mc.cyan .mv{color:#00BCD4;}
    .ms{font-size:11px;color:var(--t3);margin-top:4px;}
    /* PROGRESS */
    .pr{margin-bottom:14px;}
    .pr-hdr{display:flex;justify-content:space-between;margin-bottom:6px;}
    .pr-n{font-size:12px;color:var(--t2);}
    .pr-v{font-size:12px;font-family:var(--mono);font-weight:600;}
    .pr-t{height:6px;background:var(--bg2);border-radius:99px;overflow:hidden;}
    .pr-f{height:100%;border-radius:99px;transition:width .8s cubic-bezier(.4,0,.2,1);}
    /* COST TABLE */
    .ct-row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border);font-size:13px;}
    .ct-row:last-child{border-bottom:none;}
    .ct-row.tot{font-weight:700;font-size:14px;border-top:2px solid var(--border);padding-top:12px;margin-top:4px;}
    .ct-row.hi{color:var(--acc);}
    .ct-k{color:var(--t2);}
    .ct-row.tot .ct-k{color:var(--t1);}
    .ct-row.hi .ct-k{color:var(--acc);}
    .ct-a{font-family:var(--mono);}
    /* PROV */
    .prov-card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--rs);padding:16px;margin-bottom:10px;}
    .prov-card:hover{border-color:var(--blue);}
    .prov-n{font-size:14px;font-weight:600;}
    .prov-c{font-size:12px;color:var(--t3);margin-top:2px;}
    .prov-d{margin-top:10px;display:flex;gap:16px;flex-wrap:wrap;}
    .prov-dl{color:var(--t3);font-size:12px;}
    .prov-dv{color:var(--t1);font-weight:600;font-family:var(--mono);font-size:12px;}
    /* COMP TABLE */
    .ctbl{width:100%;border-collapse:collapse;}
    .ctbl th{text-align:left;padding:10px 14px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--t3);border-bottom:1px solid var(--border);}
    .ctbl td{padding:12px 14px;font-size:13px;border-bottom:1px solid var(--border);vertical-align:middle;}
    .ctbl tr:hover td{background:var(--hover);cursor:pointer;}
    .mono{font-family:var(--mono);}
    .ivc-badge{display:inline-block;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;font-family:var(--mono);}
    /* HIST TABLE */
    .htbl{width:100%;border-collapse:collapse;}
    .htbl th{text-align:left;padding:10px 14px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--t3);border-bottom:1px solid var(--border);background:var(--card2);}
    .htbl td{padding:12px 14px;font-size:12px;border-bottom:1px solid var(--border);}
    .htbl tr:hover td{background:var(--hover);}
    /* IVC GAUGE */
    .ivc-wrap{text-align:center;padding:20px 0;}
    .ivc-g{position:relative;width:160px;height:160px;margin:0 auto 16px;}
    .ivc-g svg{transform:rotate(-90deg);}
    .ivc-val{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;}
    .ivc-num{font-size:36px;font-weight:700;font-family:var(--mono);line-height:1;}
    .ivc-lbl{font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:1px;}
    .ivc-cls{font-size:16px;font-weight:700;margin-top:8px;}
    .ivc-rec{font-size:12px;color:var(--t2);margin-top:6px;max-width:280px;margin-left:auto;margin-right:auto;}
    /* PROP GRID */
    .prop-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
    .prop-item{background:var(--bg2);border-radius:var(--rs);padding:10px 12px;}
    .prop-k{font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:.8px;}
    .prop-v{font-size:13px;font-weight:600;margin-top:2px;}
    /* MAT CATALOG */
    .mat-cat-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);overflow:hidden;transition:border-color .2s,transform .2s;cursor:pointer;}
    .mat-cat-card:hover{transform:translateY(-2px);}
    .mat-cat-hdr{padding:20px 20px 16px;}
    .mat-cat-body{padding:0 20px 16px;}
    .mat-cat-apps{border-top:1px solid var(--border);padding:12px 20px;background:var(--card2);}
    .mat-app-tag{display:inline-block;background:var(--bg2);border:1px solid var(--border);border-radius:99px;padding:3px 10px;font-size:11px;color:var(--t2);margin:3px 3px 0 0;}
    /* TIEMPO */
    .t-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(0,188,212,.15);border:1px solid rgba(0,188,212,.3);border-radius:var(--rs);padding:8px 14px;font-size:13px;color:#00BCD4;font-weight:600;}
    /* TOAST */
    #toast{position:fixed;bottom:32px;right:32px;background:var(--card2);border:1px solid var(--border);border-radius:var(--rs);padding:14px 20px;font-size:14px;color:var(--t1);box-shadow:0 8px 32px rgba(0,0,0,.4);z-index:999;transform:translateY(20px);opacity:0;transition:all .3s;pointer-events:none;display:flex;align-items:center;gap:10px;max-width:340px;}
    #toast.show{transform:translateY(0);opacity:1;pointer-events:auto;}
    #toast.success{border-color:var(--acc);}
    #toast.error{border-color:var(--red);}
    #toast.info{border-color:var(--blue);}
    /* SPINNER */
    .spin{display:inline-block;width:18px;height:18px;border:2px solid var(--border);border-top-color:var(--acc);border-radius:50%;animation:sp .7s linear infinite;}
    @keyframes sp{to{transform:rotate(360deg);}}
    /* RESULTS */
    #results-panel{display:none;}
    #results-panel.vis{display:block;animation:fiu .4s ease;}
    @keyframes fiu{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
    /* EMPTY */
    .empty{text-align:center;padding:48px 24px;color:var(--t3);}
    .empty .ei{font-size:48px;margin-bottom:16px;opacity:.4;}
    /* MODAL */
    .modal-ov{position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:500;display:none;align-items:center;justify-content:center;}
    .modal-ov.show{display:flex;}
    .modal{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px;width:90%;max-width:520px;max-height:90vh;overflow-y:auto;}
    .modal-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}
    .modal-ttl{font-size:16px;font-weight:700;}
    .modal-x{background:none;border:none;color:var(--t3);font-size:20px;cursor:pointer;padding:4px;line-height:1;}
    /* CLIENTES */
    .cli-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px;transition:border-color .2s;}
    .cli-card:hover{border-color:var(--blue);}
    .cli-n{font-size:16px;font-weight:700;}
    .cli-s{font-size:12px;color:var(--t3);margin-top:2px;}
    .cli-bdg{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;}
    .cbdg{padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600;}
    .cbdg-p{background:var(--blueg);color:var(--blue);border:1px solid rgba(88,166,255,.3);}
    .cbdg-a{background:var(--accg);color:var(--acc);border:1px solid rgba(0,255,136,.3);}
    .cbdg-i{background:var(--redg);color:var(--red);border:1px solid rgba(255,68,68,.3);}
    .cli-info{margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:8px;}
    .cli-il{color:var(--t3);font-size:12px;}
    .cli-iv{color:var(--t1);font-weight:600;margin-top:2px;font-size:12px;}
    .cli-act{margin-top:14px;display:flex;gap:8px;}
    /* CHART */
    .ch-box{position:relative;height:220px;}
    @media(max-width:768px){.sidebar{width:60px;}.sb-logo .name,.sb-logo .sub,.nav-item span,.sb-foot{display:none;}.nav-item{justify-content:center;}.main{margin-left:60px;}.g2,.g3,.g4{grid-template-columns:1fr;}.page{padding:16px;}}
    /* COMP DETAIL */
    .cd-panel{margin-top:20px;display:none;}
    .cd-panel.vis{display:block;animation:fiu .3s ease;}
    /* divider */
    .divider{height:1px;background:var(--border);margin:24px 0;}

    /* ── RIPPLE SUTIL AL CLIC ── */
    .ripple{
      position:fixed;border-radius:50%;pointer-events:none;z-index:9999;
      background:radial-gradient(circle,rgba(0,255,136,.3) 0%,rgba(0,255,136,.07) 55%,transparent 72%);
      transform:scale(0);
      animation:ripple-out .55s cubic-bezier(0,0,.25,1) forwards;
    }
    @keyframes ripple-out{to{transform:scale(1);opacity:0;}}

    /* ── LOGO ANIMADO ── */
    .sb-logo .icon{animation:logo-float 3.2s ease-in-out infinite;filter:drop-shadow(0 0 8px rgba(0,255,136,.55));cursor:default;}
    .sb-logo .name{animation:logo-glow 3.2s ease-in-out infinite;}
    @keyframes logo-float{
      0%,100%{transform:translateY(0) rotate(0deg);}
      30%    {transform:translateY(-5px) rotate(-4deg);}
      65%    {transform:translateY(-3px) rotate(3deg);}
    }
    @keyframes logo-glow{
      0%,100%{text-shadow:0 0 6px rgba(0,255,136,.35);}
      50%    {text-shadow:0 0 20px rgba(0,255,136,.95),0 0 5px rgba(0,255,136,.5);}
    }

  </style>
</head>
<body>

<nav class="sidebar">
  <div class="sb-logo">
    <span class="icon">🌴</span>
    <div class="name">NovaPLAST CTG</div>
    <div class="sub">Circular Intelligence</div>
  </div>
  <div class="sb-nav">
    <div class="nav-item active" onclick="navTo('analyzer')"><span class="ni">🔬</span><span>Analizador</span></div>
    <div class="nav-item" onclick="navTo('materiales')"><span class="ni">🧪</span><span>Materiales</span></div>
    <div class="nav-item" onclick="navTo('comparador')"><span class="ni">📊</span><span>Comparador</span></div>
    <div class="nav-item" onclick="navTo('clientes')"><span class="ni">👥</span><span>Clientes</span></div>
    <div class="nav-item" onclick="navTo('proveedores')"><span class="ni">🏭</span><span>Proveedores</span></div>
    <div class="nav-item" onclick="navTo('historial')"><span class="ni">📋</span><span>Historial</span></div>
    <div class="nav-item" onclick="navTo('cotizador')"><span class="ni">🧾</span><span>Cotizador</span></div>
  </div>
  <div class="sb-foot">
    <div style="font-family:var(--mono);color:var(--acc2);margin-bottom:10px;">v3.0 · © 2025 NovaPLAST CTG</div>
    <button class="btn-session" onclick="cerrarSesion()">🔓 Cerrar sesión</button>
    <button class="btn-shutdown" onclick="apagarSistema()">⏻ Salir del sistema</button>
  </div>
</nav>

<!-- PARTÍCULAS DE FONDO -->
<canvas id="particles-canvas"></canvas>

<main class="main">
  <div class="topbar">
    <div><h1 id="page-title">Analizador de Residuos</h1><p id="page-sub">Identifica, valora y reutiliza plásticos</p></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="badge-live">SISTEMA ACTIVO</div>
    </div>
  </div>

  <!-- ANALIZADOR -->
  <div class="page active" id="page-analyzer">
    <div class="sec-hdr"><h2>🔬 Análisis de Residuo Plástico</h2><p>Completa los pasos para obtener el análisis técnico-económico completo</p></div>
    <div class="g2" style="align-items:start;">
      <div style="display:flex;flex-direction:column;gap:20px;">
        <!-- Paso 1 -->
        <div class="card">
          <div class="card-hdr"><div><div class="card-ttl">Paso 1 — Tipo de Residuo</div><div style="font-size:13px;color:var(--t2);margin-top:4px;">¿Qué objeto es el plástico?</div></div><span id="obj-badge" style="font-size:20px;display:none;"></span></div>
          <div class="obj-grid" id="obj-grid"></div>
        </div>
        <!-- Paso 2 -->
        <div class="card" id="step-mat" style="opacity:.4;pointer-events:none;transition:opacity .3s;">
          <div class="card-hdr"><div><div class="card-ttl">Paso 2 — Material Plástico</div><div style="font-size:13px;color:var(--t2);margin-top:4px;">Selecciona el tipo de plástico</div></div></div>
          <div class="mat-chips" id="mat-chips"><div style="font-size:13px;color:var(--t3);">↑ Primero selecciona el tipo de residuo</div></div>
        </div>
        <!-- Paso 3 -->
        <div class="card" id="step-app" style="opacity:.4;pointer-events:none;transition:opacity .3s;">
          <div class="card-hdr"><div><div class="card-ttl">Paso 3 — Aplicación</div><div style="font-size:13px;color:var(--t2);margin-top:4px;">¿En qué producto se transformará?</div></div></div>
          <div class="app-list" id="app-list"><div style="font-size:13px;color:var(--t3);">↑ Selecciona el material primero</div></div>
        </div>
        <!-- Paso 4 -->
        <div class="card" id="step-par" style="opacity:.4;pointer-events:none;transition:opacity .3s;">
          <div class="card-hdr"><div class="card-ttl">Paso 4 — Parámetros Económicos</div></div>
          <div class="fr">
            <div class="fg"><label class="fl">💰 Precio Material (COP/kg)</label><div class="pig"><span class="pp">$</span><input type="number" class="fi pi" id="precio-input" placeholder="3500" step="1" min="1"><span class="ps">/ kg</span></div></div>
            <div class="fg"><label class="fl">📦 Cantidad a Procesar (kg)</label><input type="number" class="fi" id="cant-input" placeholder="Auto" step="0.01" min="0.01"></div>
          </div>
          <div class="fg"><label class="fl">📈 Margen de Ganancia</label>
            <div class="mrg-btns">
              <button class="mrg-btn" data-val="minimo" onclick="selMrg(this)"><span class="mp">25%</span>Mínimo</button>
              <button class="mrg-btn selected" data-val="objetivo" onclick="selMrg(this)"><span class="mp">40%</span>Objetivo</button>
              <button class="mrg-btn" data-val="premium" onclick="selMrg(this)"><span class="mp">60%</span>Premium</button>
            </div>
          </div>
          <div class="btn-grp" style="margin-top:8px;">
            <button class="btn btn-p" id="btn-analizar" onclick="ejecutarAnalisis()" disabled>🔬 Ejecutar Análisis</button>
            <button class="btn btn-s" onclick="resetForm()">↺ Reiniciar</button>
          </div>
        </div>
      </div>

      <!-- RESULTS PANEL -->
      <div id="results-panel">
        <div class="card" style="margin-bottom:20px;">
          <div class="card-ttl" style="margin-bottom:12px;">⏱️ Tiempo Estimado de Producción</div>
          <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
            <div class="t-badge" id="t-badge">— min</div>
            <div style="font-size:12px;color:var(--t2);" id="t-det"></div>
          </div>
          <div style="margin-top:10px;" id="t-desg"></div>
        </div>
        <div class="g2" style="margin-bottom:20px;">
          <div class="mc green"><div class="mi">💵</div><div class="mt">Costo Producción</div><div class="mv" id="r-costo">—</div><div class="ms">por unidad producida</div></div>
          <div class="mc blue"><div class="mi">🏷️</div><div class="mt">Precio de Venta</div><div class="mv" id="r-precio">—</div><div class="ms">precio estimado</div></div>
          <div class="mc orange"><div class="mi">📈</div><div class="mt">ROI</div><div class="mv" id="r-roi">—</div><div class="ms">retorno inversión</div></div>
          <div class="mc purple"><div class="mi">♻️</div><div class="mt">Reciclabilidad</div><div class="mv" id="r-rec">—</div><div class="ms">índice del material</div></div>
        </div>
        <div class="card" style="margin-bottom:20px;">
          <div class="card-ttl" style="margin-bottom:16px;">🔄 Índice de Viabilidad Circular</div>
          <div class="ivc-wrap">
            <div class="ivc-g">
              <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="68" fill="none" stroke="#1C2128" stroke-width="14"/>
                <circle id="ivc-circle" cx="80" cy="80" r="68" fill="none" stroke="#00FF88" stroke-width="14" stroke-dasharray="427 427" stroke-dashoffset="427" stroke-linecap="round" style="transition:stroke-dashoffset 1s cubic-bezier(.4,0,.2,1),stroke .5s;"/>
              </svg>
              <div class="ivc-val"><div class="ivc-num" id="ivc-num" style="color:var(--acc);">—</div><div class="ivc-lbl">/100</div></div>
            </div>
            <div class="ivc-cls" id="ivc-cls">Ejecuta un análisis</div>
            <div class="ivc-rec" id="ivc-rec">Completa los pasos para ver el índice de viabilidad circular.</div>
          </div>
          <div style="margin-top:20px;">
            <div class="pr" id="pr-tec" style="display:none;"><div class="pr-hdr"><span class="pr-n">Factor Técnico</span><span class="pr-v" id="pv-tec">0</span></div><div class="pr-t"><div class="pr-f" id="pb-tec" style="width:0%;background:var(--acc);"></div></div></div>
            <div class="pr" id="pr-mat" style="display:none;"><div class="pr-hdr"><span class="pr-n">Factor Material</span><span class="pr-v" id="pv-mat">0</span></div><div class="pr-t"><div class="pr-f" id="pb-mat" style="width:0%;background:var(--blue);"></div></div></div>
            <div class="pr" id="pr-eco" style="display:none;"><div class="pr-hdr"><span class="pr-n">Factor Económico</span><span class="pr-v" id="pv-eco">0</span></div><div class="pr-t"><div class="pr-f" id="pb-eco" style="width:0%;background:var(--orange);"></div></div></div>
            <div class="pr" id="pr-esc" style="display:none;"><div class="pr-hdr"><span class="pr-n">Factor de Escala</span><span class="pr-v" id="pv-esc">0</span></div><div class="pr-t"><div class="pr-f" id="pb-esc" style="width:0%;background:var(--purple);"></div></div></div>
          </div>
        </div>
        <div class="card" style="margin-bottom:20px;">
          <div class="card-ttl" style="margin-bottom:16px;">📈 Gráficas</div>
          <div class="g2" style="gap:16px;">
            <div><div style="font-size:11px;color:var(--t3);margin-bottom:8px;text-transform:uppercase;">Desglose Costos</div><div class="ch-box"><canvas id="chart-costos"></canvas></div></div>
            <div><div style="font-size:11px;color:var(--t3);margin-bottom:8px;text-transform:uppercase;">Factores IVC</div><div class="ch-box"><canvas id="chart-ivc"></canvas></div></div>
          </div>
          <div style="margin-top:16px;"><div style="font-size:11px;color:var(--t3);margin-bottom:8px;text-transform:uppercase;">Costo vs Venta vs Ganancia</div><div class="ch-box"><canvas id="chart-econ"></canvas></div></div>
        </div>
        <div class="card" style="margin-bottom:20px;">
          <div class="card-ttl" style="margin-bottom:16px;">💰 Desglose de Costos (COP/unidad)</div>
          <div id="cost-table"><div style="font-size:13px;color:var(--t3);text-align:center;padding:16px;">Sin datos</div></div>
        </div>
        <div class="card" style="margin-bottom:20px;">
          <div class="card-ttl" style="margin-bottom:16px;" id="mat-props-title">🧪 Propiedades del Material</div>
          <div class="prop-grid" id="mat-props-grid"></div>
        </div>
        <div class="card" style="margin-bottom:20px;">
          <div class="card-ttl" style="margin-bottom:16px;">🤝 Proveedores</div>
          <div id="prov-list"><div style="font-size:13px;color:var(--t3);text-align:center;padding:16px;">Sin datos</div></div>
        </div>
        <div class="card">
          <div class="card-ttl" style="margin-bottom:14px;">⚡ Acciones</div>
          <div class="btn-grp">
            <button class="btn btn-p btn-sm" onclick="guardarAnalisis()">💾 Guardar</button>
            <button class="btn btn-b btn-sm" onclick="irComparador()">📊 Comparador</button>
            <button class="btn btn-g btn-sm" onclick="navTo('cotizador')">🧾 Cotizar</button>
            <button class="btn btn-s btn-sm" onclick="exportarExcel()">📥 Excel</button>
            <button class="btn btn-s btn-sm" onclick="exportarPDF()">📄 PDF</button>
          </div>
        </div>
      </div>
      <div id="empty-results" class="card">
        <div class="empty"><div class="ei">🔬</div><div style="font-size:16px;font-weight:600;color:var(--t2);margin-bottom:8px;">Análisis listo para comenzar</div><p>Selecciona el residuo, material y aplicación.</p></div>
      </div>
    </div>
  </div>

  <!-- MATERIALES -->
  <div class="page" id="page-materiales">
    <div class="sec-hdr"><h2>🧪 Catálogo de Materiales</h2><p>Propiedades técnicas de cada tipo de plástico</p></div>
    <div class="g3" id="mat-catalog"></div>
  </div>

  <!-- COMPARADOR -->
  <div class="page" id="page-comparador">
    <div class="sec-hdr"><h2>📊 Comparador de Aplicaciones</h2><p>Haz clic en una fila para ver el análisis detallado</p></div>
    <div class="card" style="margin-bottom:20px;">
      <div class="fr" style="align-items:flex-end;">
        <div class="fg" style="margin-bottom:0;"><label class="fl">Material</label><select class="fs" id="comp-mat"><option value="">— Selecciona —</option></select></div>
        <div class="fg" style="margin-bottom:0;"><label class="fl">Precio (COP/kg)</label><div class="pig"><span class="pp">$</span><input type="number" class="fi pi" id="comp-precio" placeholder="Referencia" step="1"></div></div>
        <button class="btn btn-p" onclick="ejecutarComp()">Comparar →</button>
      </div>
    </div>
    <div class="card" id="comp-results"><div class="empty"><div class="ei">📊</div><p>Selecciona un material</p></div></div>
    <div class="cd-panel card" id="cd-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;"><div class="card-ttl" id="cd-title">Detalle</div><button class="btn btn-s btn-sm" onclick="cerrarDetalle()">✕ Cerrar</button></div>
      <div id="cd-content"></div>
    </div>
  </div>

  <!-- CLIENTES -->
  <div class="page" id="page-clientes">
    <div class="sec-hdr"><h2>👥 Clientes</h2><p>Empresas que te compran productos terminados — volumen expresado en unidades/mes</p></div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn btn-s btn-sm" onclick="filtCli('todos')" id="f-todos" style="border-color:var(--acc);color:var(--acc);">Todos</button>
        <button class="btn btn-s btn-sm" onclick="filtCli('activo')" id="f-activo">Activos</button>
        <button class="btn btn-s btn-sm" onclick="filtCli('potencial')" id="f-potencial">Potenciales</button>
        <button class="btn btn-s btn-sm" onclick="filtCli('inactivo')" id="f-inactivo">Inactivos</button>
      </div>
      <button class="btn btn-p btn-sm" onclick="abrirModal()">+ Agregar Cliente</button>
      <button class="btn btn-s btn-sm" onclick="exportarCliExcel()">📥 Exportar</button>
    </div>
    <div class="g3" id="cli-grid"></div>
  </div>

  <!-- PROVEEDORES -->
  <div class="page" id="page-proveedores">
    <div class="sec-hdr"><h2>🏭 Proveedores</h2><p>Gestión completa de materia prima — precios, volúmenes, análisis comparativo y KPIs</p></div>

    <!-- KPIs Proveedores -->
    <div class="g4" style="margin-bottom:24px;" id="prov-kpis">
      <div class="mc green"><div class="mi">🏭</div><div class="mt">Total Proveedores</div><div class="mv" id="kp-total">0</div><div class="ms">registrados</div></div>
      <div class="mc blue"><div class="mi">✅</div><div class="mt">Activos</div><div class="mv" id="kp-activos">0</div><div class="ms">en operación</div></div>
      <div class="mc orange"><div class="mi">💰</div><div class="mt">Precio Promedio</div><div class="mv" id="kp-precio">—</div><div class="ms">COP / kg</div></div>
      <div class="mc purple"><div class="mi">📦</div><div class="mt">Vol. Mín. Promedio</div><div class="mv" id="kp-vol">—</div><div class="ms">kg por pedido</div></div>
    </div>

    <!-- Barra de herramientas -->
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
        <input type="text" class="fi" id="prov-search" placeholder="🔍 Buscar proveedor..." style="width:200px;padding:8px 12px;font-size:13px;" oninput="renderProveedores()">
        <select class="fs" id="prov-filter-mat" style="width:140px;font-size:13px;padding:8px;" onchange="renderProveedores()">
          <option value="">Todos los materiales</option>
          <option>PET</option><option>HDPE</option><option>PVC</option>
          <option>LDPE</option><option>PP</option><option>PS</option>
          <option>ABS</option><option>LLDPE</option><option>PA</option>
        </select>
        <select class="fs" id="prov-filter-est" style="width:130px;font-size:13px;padding:8px;" onchange="renderProveedores()">
          <option value="">Todos los estados</option>
          <option value="activo">Activos</option>
          <option value="potencial">Potenciales</option>
          <option value="inactivo">Inactivos</option>
        </select>
        <select class="fs" id="prov-sort" style="width:160px;font-size:13px;padding:8px;" onchange="renderProveedores()">
          <option value="nombre">Ordenar: Nombre</option>
          <option value="precio_asc">Precio ↑ (menor)</option>
          <option value="precio_desc">Precio ↓ (mayor)</option>
          <option value="vol_asc">Vol. Mín. ↑</option>
          <option value="reciente">Más reciente</option>
        </select>
      </div>
      <div style="display:flex;gap:8px;">
        <button class="btn btn-s btn-sm" onclick="toggleProvView()" id="btn-prov-view">📊 Ver Análisis</button>
        <button class="btn btn-s btn-sm" onclick="exportarProvExcel()">📥 Exportar</button>
        <button class="btn btn-p btn-sm" onclick="abrirModalProv()">+ Agregar Proveedor</button>
      </div>
    </div>

    <!-- Panel de análisis comparativo (toggle) -->
    <div id="prov-analysis-panel" style="display:none;margin-bottom:24px;">
      <div class="g2" style="margin-bottom:20px;">
        <div class="card">
          <div class="card-hdr"><div class="card-ttl">💰 Precio/kg por Material</div></div>
          <div class="ch-box"><canvas id="chart-prov-precios"></canvas></div>
        </div>
        <div class="card">
          <div class="card-hdr"><div class="card-ttl">🗺️ Distribución por Ciudad</div></div>
          <div class="ch-box"><canvas id="chart-prov-ciudades"></canvas></div>
        </div>
      </div>
      <div class="card" style="margin-bottom:20px;">
        <div class="card-hdr"><div class="card-ttl">📊 Comparador de Precios — Mejor opción por material</div></div>
        <div id="prov-comparador-table"></div>
      </div>
    </div>

    <!-- Contador de resultados -->
    <div style="font-size:12px;color:var(--t3);margin-bottom:12px;" id="prov-count-label"></div>

    <!-- Grid de proveedores -->
    <div class="g3" id="prov-grid"></div>
  </div>

  <!-- HISTORIAL -->
  <div class="page" id="page-historial">
    <div class="sec-hdr"><h2>📋 Historial</h2><p>Registro de análisis y cotizaciones realizadas</p></div>
    <div class="card" style="margin-bottom:20px;">
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
        <button class="btn btn-s btn-sm" id="htab-analisis" onclick="switchHTab('analisis')" style="border-color:var(--acc);color:var(--acc);">🔬 Análisis</button>
        <button class="btn btn-s btn-sm" id="htab-cots" onclick="switchHTab('cots')">🧾 Cotizaciones</button>
      </div>
      <div class="btn-grp" id="hist-btns-analisis">
        <button class="btn btn-p btn-sm" onclick="renderHist()">🔄 Actualizar</button>
        <button class="btn btn-d btn-sm" onclick="limpiarHist()">🗑️ Limpiar Todo</button>
      </div>
      <div class="btn-grp" id="hist-btns-cots" style="display:none;">
        <button class="btn btn-p btn-sm" onclick="renderHistCots()">🔄 Actualizar</button>
        <button class="btn btn-d btn-sm" onclick="limpiarHistCots()">🗑️ Limpiar Todo</button>
      </div>
    </div>
    <div class="card" id="hist-panel-analisis"><div id="hist-content"><div class="empty"><div class="ei">📋</div><p>No hay análisis guardados</p></div></div></div>
    <div class="card" id="hist-panel-cots" style="display:none;"><div id="hist-cots-content"><div class="empty"><div class="ei">🧾</div><p>No hay cotizaciones guardadas</p></div></div></div>
  </div>

  <!-- COTIZADOR -->
  <div class="page" id="page-cotizador">
    <div class="sec-hdr"><h2>🧾 Cotizador Rápido</h2><p>Genera cotizaciones profesionales en segundos</p></div>
    <div class="g2" style="align-items:start;">
      <div style="display:flex;flex-direction:column;gap:20px;">
        <div class="card">
          <div class="card-ttl" style="margin-bottom:16px;">📋 Datos de la Cotización</div>
          <div class="fg"><label class="fl">Cliente</label><select class="fs" id="cot-cli"><option value="">— Selecciona un cliente —</option></select></div>
          <div class="fr">
            <div class="fg"><label class="fl">Producto</label><input type="text" class="fi" id="cot-prod" placeholder="Ej: Sillas PP reciclado"></div>
            <div class="fg"><label class="fl">Cantidad (unidades de producto terminado)</label><input type="number" class="fi" id="cot-cant" placeholder="100" min="1"></div>
          </div>
          <div class="fr">
            <div class="fg"><label class="fl">Precio Unitario (COP)</label><div class="pig"><span class="pp">$</span><input type="number" class="fi pi" id="cot-precio" placeholder="0" step="1"></div></div>
            <div class="fg"><label class="fl">Descuento (%)</label><input type="number" class="fi" id="cot-desc" placeholder="0" min="0" max="50"></div>
          </div>
          <div class="fg"><label class="fl">Notas</label><textarea class="fi" id="cot-notas" rows="3" placeholder="Condiciones de entrega..."></textarea></div>
          <button class="btn btn-p" onclick="genCot()" style="width:100%;">🧾 Generar Cotización</button>
        </div>
      </div>
      <div>
        <div id="cot-preview" style="display:none;" class="card">
          <div class="card-ttl" style="margin-bottom:16px;">👁️ Vista Previa</div>
          <div id="cot-prev-content"></div>
          <div class="btn-grp" style="margin-top:16px;">
            <button class="btn btn-p btn-sm" onclick="exportarCotPDF()">📄 Descargar PDF</button>
            <button class="btn btn-s btn-sm" onclick="window.print()">🖨️ Imprimir</button>
          </div>
        </div>
        <div id="cot-empty" class="card"><div class="empty"><div class="ei">🧾</div><p>Completa los datos para generar una cotización</p></div></div>
      </div>
    </div>
  </div>
</main>

<!-- MODAL CLIENTE -->
<div class="modal-ov" id="modal-cli">
  <div class="modal">
    <div class="modal-hdr"><div class="modal-ttl" id="modal-ttl">➕ Nuevo Cliente</div><button class="modal-x" onclick="cerrarModal()">✕</button></div>
    <div class="fg"><label class="fl">Nombre / Empresa *</label><input type="text" class="fi" id="cli-nom" placeholder="Nombre del cliente"></div>
    <div class="fr">
      <div class="fg"><label class="fl">Sector</label><select class="fs" id="cli-sec"><option>Construcción</option><option>Manufactura</option><option>Agricultura</option><option>Logística</option><option>Hogar / Retail</option><option>Electrónica</option><option>Automotriz</option><option>Municipal</option><option>Otro</option></select></div>
      <div class="fg"><label class="fl">Estado</label><select class="fs" id="cli-est"><option value="potencial">Potencial</option><option value="activo">Activo</option><option value="inactivo">Inactivo</option></select></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Ciudad</label><input type="text" class="fi" id="cli-ciu" placeholder="Cartagena"></div>
      <div class="fg"><label class="fl">Teléfono</label><input type="text" class="fi" id="cli-tel" placeholder="+57 300 000 0000"></div>
    </div>
    <div class="fg"><label class="fl">Email</label><input type="email" class="fi" id="cli-em" placeholder="contacto@empresa.com"></div>
    <div class="fr">
      <div class="fg"><label class="fl">Producto que le vendes</label><input type="text" class="fi" id="cli-prod" placeholder="Ej: Sillas PP reciclado"></div>
      <div class="fg"><label class="fl">Volumen mensual (unidades de producto terminado)</label><input type="number" class="fi" id="cli-vol" placeholder="500"></div>
    </div>
    <div class="fg"><label class="fl">Notas</label><textarea class="fi" id="cli-not" rows="2" placeholder="Observaciones..."></textarea></div>
    <div style="margin:10px 0 6px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--acc);border-top:1px solid var(--border);padding-top:12px;">📊 Parámetros de calificación</div>
    <div class="fr">
      <div class="fg"><label class="fl">Cotizaciones realizadas</label><input type="number" class="fi" id="cli-ncots" placeholder="0" min="0"></div>
      <div class="fg"><label class="fl">Puntualidad de pago (1-5)</label><select class="fs" id="cli-pago"><option value="1">1 – Siempre tarde</option><option value="2">2 – Frecuente retraso</option><option value="3" selected>3 – A veces tarde</option><option value="4">4 – Casi siempre puntual</option><option value="5">5 – Siempre puntual</option></select></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Volumen de compra mensual (und)</label><input type="number" class="fi" id="cli-vol" placeholder="500"></div>
      <div class="fg"><label class="fl">Frecuencia de compra</label><select class="fs" id="cli-freq"><option value="1">Única vez</option><option value="2">Ocasional</option><option value="3" selected>Mensual</option><option value="4">Quincenal</option><option value="5">Semanal</option></select></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Antigüedad (meses)</label><input type="number" class="fi" id="cli-antig" placeholder="0" min="0"></div>
      <div class="fg"><label class="fl">Calificación automática</label><input class="fi" id="cli-rating-preview" readonly style="color:var(--acc);font-weight:700;" placeholder="Se calcula al guardar"></div>
    </div>
    <div class="btn-grp"><button class="btn btn-p" onclick="guardarCliente()" style="flex:1;">Guardar</button><button class="btn btn-s" onclick="cerrarModal()">Cancelar</button></div>
  </div>
</div>

<!-- MODAL PROVEEDOR -->
<div class="modal-ov" id="modal-prov">
  <div class="modal" style="max-width:600px;">
    <div class="modal-hdr"><div class="modal-ttl" id="modal-prov-ttl">➕ Nuevo Proveedor</div><button class="modal-x" onclick="cerrarModalProv()">✕</button></div>
    <div class="fg"><label class="fl">Nombre / Empresa *</label><input type="text" class="fi" id="prov-nom" placeholder="Nombre del proveedor"></div>
    <div class="fr">
      <div class="fg"><label class="fl">Ciudad</label><input type="text" class="fi" id="prov-ciu" placeholder="Cartagena"></div>
      <div class="fg"><label class="fl">Teléfono</label><input type="text" class="fi" id="prov-tel" placeholder="+57 300 000 0000"></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Email / Contacto</label><input type="email" class="fi" id="prov-em" placeholder="ventas@proveedor.co"></div>
      <div class="fg"><label class="fl">Contacto / Representante</label><input type="text" class="fi" id="prov-contacto" placeholder="Juan García"></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Material principal</label><select class="fs" id="prov-mat"><option value="">— Selecciona —</option><option>PET</option><option>HDPE</option><option>PVC</option><option>LDPE</option><option>PP</option><option>PS</option><option>ABS</option><option>LLDPE</option><option>PA</option></select></div>
      <div class="fg"><label class="fl">Materiales adicionales</label><input type="text" class="fi" id="prov-mats-extra" placeholder="Ej: LDPE, PP (separados por coma)"></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Precio/kg (COP)</label><div class="pig"><span class="pp">$</span><input type="number" class="fi pi" id="prov-precio" placeholder="2500"></div></div>
      <div class="fg"><label class="fl">Precio negociado/kg</label><div class="pig"><span class="pp">$</span><input type="number" class="fi pi" id="prov-precio-neg" placeholder="2200"></div></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Volumen mínimo (kg)</label><input type="number" class="fi" id="prov-vol" placeholder="500"></div>
      <div class="fg"><label class="fl">Capacidad máx. mensual (kg)</label><input type="number" class="fi" id="prov-vol-max" placeholder="5000"></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Tiempo de entrega (días)</label><input type="number" class="fi" id="prov-entrega" placeholder="3" min="1"></div>
    </div>
    <div class="fr">
      <div class="fg"><label class="fl">Certificación / Calidad</label><input type="text" class="fi" id="prov-cert" placeholder="ISO 9001, RUC, etc."></div>
      <div class="fg"><label class="fl">Estado</label><select class="fs" id="prov-est"><option value="activo">Activo</option><option value="potencial">Potencial</option><option value="inactivo">Inactivo</option></select></div>
    </div>
    <div class="fg"><label class="fl">Condiciones de pago</label><select class="fs" id="prov-pago"><option value="">— Selecciona —</option><option>Contado</option><option>30 días</option><option>45 días</option><option>60 días</option><option>Anticipo 50%</option><option>Anticipo 30%</option></select></div>
    <div class="fg"><label class="fl">Notas / Observaciones</label><textarea class="fi" id="prov-not" rows="2" placeholder="Calidad del material, tiempos de entrega, condiciones especiales..."></textarea></div>

    <div style="margin:10px 0 6px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--acc);border-top:1px solid var(--border);padding-top:12px;">📊 Criterios de calificación automática</div>
    <div style="background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px;font-size:11px;color:var(--t3);line-height:1.8;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px 16px;">
        <div>⭐ <b style="color:var(--t2);">Precio competitivo</b> — vs. promedio del catálogo</div>
        <div>⭐ <b style="color:var(--t2);">Entrega rápida</b> — ≤1 día máximo, +días menos ★</div>
        <div>⭐ <b style="color:var(--t2);">Volumen disponible</b> — ≥10.000 kg/mes = perfecto</div>
        <div>⭐ <b style="color:var(--t2);">Certificación</b> — ISO, RUC u otra = 1★ completa</div>
        <div style="grid-column:1/-1;">⭐ <b style="color:var(--t2);">Estado activo</b> — Activo = 1★, Potencial = 0.5★, Inactivo = 0★</div>
      </div>
    </div>
    <div class="fr" style="margin-top:10px;">
      <div class="fg"><label class="fl">Vista previa calificación</label><input class="fi" id="prov-rating-preview" readonly style="color:var(--acc);font-weight:700;" placeholder="Se calcula al guardar"><input type="hidden" id="prov-rating" value="3"></div>
    </div>
    <div class="btn-grp"><button class="btn btn-p" onclick="guardarProveedor()" style="flex:1;">💾 Guardar Proveedor</button><button class="btn btn-s" onclick="cerrarModalProv()">Cancelar</button></div>
  </div>
</div>

<div id="toast"></div>

<script>
// ════════════════════════════════════════════════════════════════
//  NovaPLAST CTG — Motor Frontend (COP)
// ════════════════════════════════════════════════════════════════

// ─── BASE DE DATOS ────────────────────────────────────────────
const DB = {
  objetos: {
    botella:    {nombre:"Botella / Envase",   icono:"🍶", mats:["PET","HDPE","PP"]},
    bolsa:      {nombre:"Bolsa / Film",        icono:"🛍️", mats:["LDPE","LLDPE","PP"]},
    tubo:       {nombre:"Tubo / Caño",         icono:"🔩", mats:["PVC","HDPE","PP"]},
    tapa:       {nombre:"Tapa / Cierre",       icono:"🔒", mats:["PP","HDPE","LDPE"]},
    caja:       {nombre:"Caja / Contenedor",   icono:"📦", mats:["PP","HDPE","ABS"]},
    silla:      {nombre:"Silla / Mueble",      icono:"🪑", mats:["PP","ABS","HDPE"]},
    film:       {nombre:"Film / Lámina",       icono:"📄", mats:["PET","LDPE","LLDPE","PP"]},
    espuma:     {nombre:"Espuma / Icopor",     icono:"🧊", mats:["PS"]},
    juguete:    {nombre:"Juguete / Figura",    icono:"🧸", mats:["ABS","PP","LDPE"]},
    maceta:     {nombre:"Maceta / Jardín",     icono:"⚱️", mats:["PP","HDPE","LDPE"]},
    bandeja:    {nombre:"Bandeja / Blíster",   icono:"🍱", mats:["PET","PS","PP"]},
    fibra:      {nombre:"Fibra / Textil",      icono:"🧵", mats:["PET","PP","PA"]},
    electronico:{nombre:"Electrónico",         icono:"📱", mats:["ABS","PS","PP"]},
    auto:       {nombre:"Pieza Automotriz",    icono:"🚗", mats:["ABS","PP","PVC","PA"]},
    medico:     {nombre:"Artículo Médico",     icono:"💉", mats:["PP","PVC","HDPE"]},
    agricola:   {nombre:"Artículo Agrícola",   icono:"🌾", mats:["LDPE","LLDPE","PP","PVC"]},
  },
  materiales: {
    PET:{nombre_completo:"Polietilentereftalato",codigo_reciclaje:1,color_hex:"#4FC3F7",
      descripcion:"El plástico más reciclado del mundo. Transparente, resistente y ligero.",
      propiedades:{densidad:"1.38 g/cm³",temp_fusion:"250-260°C",resistencia_quimica:"Alta",transparencia:"Alta",reciclabilidad:95},
      precio_base_kg:3500,tiempo_proceso_min_por_kg:12,
      aplicaciones:[
        {producto:"Fibra textil (ropa reciclada)",viabilidad:95,kg_necesarios:0.3,mercado:"Moda sostenible / Textil",tiempo_extra_min:20},
        {producto:"Nueva botella PET reciclada",viabilidad:90,kg_necesarios:0.05,mercado:"Bebidas / Alimentación",tiempo_extra_min:5},
        {producto:"Láminas y films de empaque",viabilidad:85,kg_necesarios:0.2,mercado:"Packaging / Alimentación",tiempo_extra_min:15},
        {producto:"Correas y cintas de embalaje",viabilidad:80,kg_necesarios:0.15,mercado:"Logística / Transporte",tiempo_extra_min:10},
        {producto:"Relleno geotextil",viabilidad:70,kg_necesarios:2.0,mercado:"Construcción / Civil",tiempo_extra_min:30},
        {producto:"Fleece y tejidos técnicos",viabilidad:88,kg_necesarios:0.25,mercado:"Deportes / Outdoor",tiempo_extra_min:25},
      ],
      proveedores:[
        {nombre:"ReciPET Colombia",ciudad:"Bogotá",contacto:"info@recipet.co",precio_compra:2500,volumen_min_kg:500},
        {nombre:"EcoCycle Medellín",ciudad:"Medellín",contacto:"ventas@ecocycle.com.co",precio_compra:2300,volumen_min_kg:1000},
        {nombre:"PlástiVerde Caribe",ciudad:"Barranquilla",contacto:"comercial@plastiverde.co",precio_compra:2700,volumen_min_kg:300},
      ]
    },
    HDPE:{nombre_completo:"Polietileno de Alta Densidad",codigo_reciclaje:2,color_hex:"#66BB6A",
      descripcion:"Rígido, resistente a impactos y químicos. Muy versátil para reciclaje.",
      propiedades:{densidad:"0.94-0.97 g/cm³",temp_fusion:"130-145°C",resistencia_quimica:"Muy Alta",transparencia:"Baja (opaco)",reciclabilidad:90},
      precio_base_kg:3000,tiempo_proceso_min_por_kg:10,
      aplicaciones:[
        {producto:"Tuberías para agua y gas",viabilidad:92,kg_necesarios:5.0,mercado:"Construcción / Acueductos",tiempo_extra_min:45},
        {producto:"Postes y mobiliario urbano",viabilidad:88,kg_necesarios:15.0,mercado:"Municipal / Urbanismo",tiempo_extra_min:90},
        {producto:"Contenedores de basura",viabilidad:85,kg_necesarios:8.0,mercado:"Saneamiento / Municipal",tiempo_extra_min:60},
        {producto:"Casco de seguridad industrial",viabilidad:75,kg_necesarios:0.4,mercado:"Seguridad industrial",tiempo_extra_min:15},
        {producto:"Tableros y madera plástica",viabilidad:82,kg_necesarios:10.0,mercado:"Carpintería / Construcción",tiempo_extra_min:75},
        {producto:"Canastas y pallets",viabilidad:78,kg_necesarios:6.0,mercado:"Logística / Almacenamiento",tiempo_extra_min:50},
      ],
      proveedores:[
        {nombre:"PoliRecicla SAS",ciudad:"Cali",contacto:"gerencia@polirecicla.co",precio_compra:2000,volumen_min_kg:800},
        {nombre:"Plastex Caribe",ciudad:"Cartagena",contacto:"ventas@plastexcaribe.co",precio_compra:1900,volumen_min_kg:500},
        {nombre:"GreenPlast Andes",ciudad:"Manizales",contacto:"comercial@greenplast.co",precio_compra:2100,volumen_min_kg:1000},
      ]
    },
    PVC:{nombre_completo:"Policloruro de Vinilo",codigo_reciclaje:3,color_hex:"#FFA726",
      descripcion:"Alta resistencia química. Reciclaje más complejo por sus aditivos.",
      propiedades:{densidad:"1.38 g/cm³",temp_fusion:"160-180°C",resistencia_quimica:"Muy Alta",transparencia:"Media",reciclabilidad:50},
      precio_base_kg:2200,tiempo_proceso_min_por_kg:15,
      aplicaciones:[
        {producto:"Tubería PVC reciclada",viabilidad:65,kg_necesarios:4.0,mercado:"Construcción / Saneamiento",tiempo_extra_min:40},
        {producto:"Perfiles para ventanas",viabilidad:60,kg_necesarios:3.0,mercado:"Construcción / Ventanas",tiempo_extra_min:35},
        {producto:"Suelas de calzado",viabilidad:55,kg_necesarios:0.5,mercado:"Calzado / Marroquinería",tiempo_extra_min:20},
        {producto:"Mangueras de riego",viabilidad:58,kg_necesarios:1.5,mercado:"Agricultura / Riego",tiempo_extra_min:25},
      ],
      proveedores:[
        {nombre:"VinylRec Colombia",ciudad:"Bogotá",contacto:"info@vinylrec.co",precio_compra:1400,volumen_min_kg:2000},
        {nombre:"ReciviniL SAS",ciudad:"Medellín",contacto:"ventas@recivinil.co",precio_compra:1200,volumen_min_kg:1500},
      ]
    },
    LDPE:{nombre_completo:"Polietileno de Baja Densidad",codigo_reciclaje:4,color_hex:"#AB47BC",
      descripcion:"Flexible, ligero y resistente a la humedad. Muy usado en films y bolsas.",
      propiedades:{densidad:"0.91-0.94 g/cm³",temp_fusion:"105-115°C",resistencia_quimica:"Media",transparencia:"Media-Alta",reciclabilidad:65},
      precio_base_kg:2600,tiempo_proceso_min_por_kg:8,
      aplicaciones:[
        {producto:"Bolsas de basura recicladas",viabilidad:80,kg_necesarios:0.05,mercado:"Consumo masivo",tiempo_extra_min:5},
        {producto:"Film para agricultura",viabilidad:75,kg_necesarios:1.0,mercado:"Agro / Horticultura",tiempo_extra_min:20},
        {producto:"Tuberías de goteo",viabilidad:70,kg_necesarios:0.8,mercado:"Agro / Riego",tiempo_extra_min:15},
        {producto:"Envolturas estirables",viabilidad:72,kg_necesarios:0.3,mercado:"Logística / Embalaje",tiempo_extra_min:10},
      ],
      proveedores:[
        {nombre:"AgroPlast SAS",ciudad:"Bucaramanga",contacto:"ventas@agroplast.co",precio_compra:1600,volumen_min_kg:600},
        {nombre:"EcoFilm Colombia",ciudad:"Pereira",contacto:"info@ecofilm.co",precio_compra:1500,volumen_min_kg:800},
      ]
    },
    PP:{nombre_completo:"Polipropileno",codigo_reciclaje:5,color_hex:"#26C6DA",
      descripcion:"Alta resistencia térmica y química. Versátil y muy reciclable.",
      propiedades:{densidad:"0.90-0.92 g/cm³",temp_fusion:"160-175°C",resistencia_quimica:"Alta",transparencia:"Media",reciclabilidad:85},
      precio_base_kg:2800,tiempo_proceso_min_por_kg:11,
      aplicaciones:[
        {producto:"Sillas y muebles plásticos",viabilidad:90,kg_necesarios:3.5,mercado:"Hogar / Comercial",tiempo_extra_min:35},
        {producto:"Tapas y cierres industriales",viabilidad:88,kg_necesarios:0.08,mercado:"Alimentario / Farmacéutico",tiempo_extra_min:5},
        {producto:"Cajas de almacenamiento",viabilidad:85,kg_necesarios:1.2,mercado:"Hogar / Industrial",tiempo_extra_min:20},
        {producto:"Pallets y tarimas",viabilidad:80,kg_necesarios:20.0,mercado:"Logística / Almacenamiento",tiempo_extra_min:120},
        {producto:"Macetas y artículos de jardín",viabilidad:82,kg_necesarios:0.8,mercado:"Jardinería / Retail",tiempo_extra_min:15},
        {producto:"Fibra de polipropileno (sacos)",viabilidad:78,kg_necesarios:0.5,mercado:"Agro / Packaging",tiempo_extra_min:18},
        {producto:"Componentes automotrices",viabilidad:76,kg_necesarios:2.0,mercado:"Automotriz",tiempo_extra_min:30},
      ],
      proveedores:[
        {nombre:"PropiRec Ltda",ciudad:"Bogotá",contacto:"gerencia@propirec.co",precio_compra:1800,volumen_min_kg:500},
        {nombre:"CircularPP Caribe",ciudad:"Barranquilla",contacto:"ventas@circularpp.co",precio_compra:1700,volumen_min_kg:700},
        {nombre:"PlastFuturo",ciudad:"Cali",contacto:"info@plastfuturo.co",precio_compra:1900,volumen_min_kg:400},
      ]
    },
    PS:{nombre_completo:"Poliestireno",codigo_reciclaje:6,color_hex:"#EF5350",
      descripcion:"Rígido o expandido (icopor). Reciclaje complejo, baja recuperación.",
      propiedades:{densidad:"1.04-1.09 g/cm³",temp_fusion:"210-249°C",resistencia_quimica:"Baja",transparencia:"Alta (PS) / Baja (EPS)",reciclabilidad:35},
      precio_base_kg:1800,tiempo_proceso_min_por_kg:18,
      aplicaciones:[
        {producto:"Marcos para cuadros",viabilidad:50,kg_necesarios:0.3,mercado:"Decoración / Retail",tiempo_extra_min:20},
        {producto:"Bloques de construcción aislante",viabilidad:45,kg_necesarios:5.0,mercado:"Construcción / Arquitectura",tiempo_extra_min:45},
        {producto:"Charolas y bandejas",viabilidad:48,kg_necesarios:0.2,mercado:"Alimentación / Retail",tiempo_extra_min:15},
      ],
      proveedores:[
        {nombre:"EcoEPS Colombia",ciudad:"Bogotá",contacto:"info@ecoeps.co",precio_compra:800,volumen_min_kg:3000},
      ]
    },
    ABS:{nombre_completo:"Acrilonitrilo Butadieno Estireno",codigo_reciclaje:7,color_hex:"#FF7043",
      descripcion:"Alta resistencia al impacto y rigidez. Muy usado en electrónica.",
      propiedades:{densidad:"1.03-1.06 g/cm³",temp_fusion:"220-240°C",resistencia_quimica:"Media",transparencia:"Baja (opaco)",reciclabilidad:75},
      precio_base_kg:4800,tiempo_proceso_min_por_kg:14,
      aplicaciones:[
        {producto:"Carcasas electrónicas",viabilidad:80,kg_necesarios:0.5,mercado:"Electrónica / Manufactura",tiempo_extra_min:20},
        {producto:"Piezas automotrices",viabilidad:75,kg_necesarios:2.0,mercado:"Automotriz",tiempo_extra_min:30},
        {producto:"Filamento para impresión 3D",viabilidad:85,kg_necesarios:1.0,mercado:"Manufactura / Prototipado",tiempo_extra_min:25},
        {producto:"Juguetes y figuras coleccionables",viabilidad:70,kg_necesarios:0.3,mercado:"Juguetería / Retail",tiempo_extra_min:18},
      ],
      proveedores:[
        {nombre:"TechPlast Colombia",ciudad:"Medellín",contacto:"info@techplast.co",precio_compra:3200,volumen_min_kg:300},
        {nombre:"ReciclaABS SAS",ciudad:"Bogotá",contacto:"ventas@reciclaabs.co",precio_compra:3000,volumen_min_kg:500},
      ]
    },
    LLDPE:{nombre_completo:"Polietileno Lineal de Baja Densidad",codigo_reciclaje:4,color_hex:"#CE93D8",
      descripcion:"Más resistente que el LDPE, flexible y con buena resistencia al desgarro.",
      propiedades:{densidad:"0.915-0.940 g/cm³",temp_fusion:"120-130°C",resistencia_quimica:"Media-Alta",transparencia:"Media",reciclabilidad:60},
      precio_base_kg:2900,tiempo_proceso_min_por_kg:9,
      aplicaciones:[
        {producto:"Film estirable para embalaje",viabilidad:78,kg_necesarios:0.3,mercado:"Logística / Packaging",tiempo_extra_min:10},
        {producto:"Geomembrana para rellenos",viabilidad:72,kg_necesarios:8.0,mercado:"Construcción / Ambiental",tiempo_extra_min:60},
        {producto:"Bolsas reforzadas",viabilidad:70,kg_necesarios:0.08,mercado:"Consumo masivo / Industria",tiempo_extra_min:8},
      ],
      proveedores:[
        {nombre:"PoliFilm SAS",ciudad:"Bogotá",contacto:"info@polifilm.co",precio_compra:1800,volumen_min_kg:600},
      ]
    },
    PA:{nombre_completo:"Poliamida (Nylon)",codigo_reciclaje:7,color_hex:"#F06292",
      descripcion:"Alta resistencia mecánica y térmica. Usado en textiles técnicos.",
      propiedades:{densidad:"1.12-1.14 g/cm³",temp_fusion:"220-260°C",resistencia_quimica:"Alta",transparencia:"Baja",reciclabilidad:55},
      precio_base_kg:8400,tiempo_proceso_min_por_kg:20,
      aplicaciones:[
        {producto:"Fibra textil técnica",viabilidad:72,kg_necesarios:0.2,mercado:"Deportes / Uniformes",tiempo_extra_min:25},
        {producto:"Componentes de ingeniería",viabilidad:68,kg_necesarios:1.5,mercado:"Manufactura / Automotriz",tiempo_extra_min:40},
        {producto:"Redes y cuerdas industriales",viabilidad:65,kg_necesarios:2.0,mercado:"Pesca / Industria",tiempo_extra_min:30},
      ],
      proveedores:[
        {nombre:"NylonRec Colombia",ciudad:"Bogotá",contacto:"info@nylonrec.co",precio_compra:6000,volumen_min_kg:200},
      ]
    },
  },
  costos_proceso:{lavado_kg:320,triturado_kg:480,peletizado_kg:600,mano_obra_hora:34000,energia_kwh_kg:720,overhead_pct:0.22},
  margenes:{minimo:0.25,objetivo:0.40,premium:0.60},
};

// ─── FORMATO COP ─────────────────────────────────────────────
function fCOP(v){return "$ "+Math.round(v).toLocaleString("es-CO");}

// ─── ESTADO ──────────────────────────────────────────────────
const S={objSel:null,matSel:null,appIdx:null,lastAnalisis:null,mrg:"objetivo",
  clientes:JSON.parse(localStorage.getItem("np_clientes")||"[]"),
  historial:JSON.parse(localStorage.getItem("np_hist")||"[]"),
  cotizaciones:JSON.parse(localStorage.getItem("np_cots")||"[]"),
  proveedores:JSON.parse(localStorage.getItem("np_provs")||"[]"),
};
function saveS(){
  localStorage.setItem("np_clientes",JSON.stringify(S.clientes));
  localStorage.setItem("np_hist",JSON.stringify(S.historial));
  localStorage.setItem("np_cots",JSON.stringify(S.cotizaciones));
  localStorage.setItem("np_provs",JSON.stringify(S.proveedores));
}

// ─── CLIENTES INICIALES ───────────────────────────────────────
const CLI_INIT=[
  {id:"c001",nombre:"Construmax Caribe SAS",sector:"Construcción",estado:"activo",ciudad:"Cartagena",tel:"+57 315 200 3000",email:"compras@construmax.co",producto:"Tuberías HDPE reciclado",volumen:200,notas:"Compra tuberías mensualmente para proyectos de acueducto."},
  {id:"c002",nombre:"AgroTécnica del Caribe",sector:"Agricultura",estado:"activo",ciudad:"Montería",tel:"+57 301 500 2200",email:"gerencia@agrotecnica.co",producto:"Film agrícola LDPE",volumen:1500,notas:"Film agrícola y tuberías de goteo para cultivos."},
  {id:"c003",nombre:"Muebles Pacífico Ltda",sector:"Hogar / Retail",estado:"activo",ciudad:"Barranquilla",tel:"+57 318 100 4400",email:"ventas@mueblespacifico.co",producto:"Sillas PP reciclado",volumen:800,notas:"Sillas y muebles de exterior fabricados con PP reciclado."},
  {id:"c004",nombre:"LogiCargo del Norte",sector:"Logística",estado:"potencial",ciudad:"Cartagena",tel:"+57 320 700 5500",email:"operaciones@logicargo.co",producto:"Pallets PP reciclado",volumen:300,notas:"Interesado en pallets de PP reciclado para su bodega."},
  {id:"c005",nombre:"Textiles Reciclar SA",sector:"Manufactura",estado:"potencial",ciudad:"Medellín",tel:"+57 312 300 6600",email:"compras@textilesr.co",producto:"Fibra PET reciclada",volumen:5000,notas:"Quieren fibra de PET para fabricar ropa técnica."},
];
if(!S.clientes.length){S.clientes=CLI_INIT;saveS();}

const PROV_INIT=[
  {id:"p001",nombre:"ReciPET Colombia",ciudad:"Bogotá",tel:"+57 310 100 2000",email:"info@recipet.co",contacto:"Carlos Mendoza",material:"PET",mats_extra:"LLDPE",precio_kg:2500,precio_neg:2300,volumen_min:500,volumen_max:8000,estado:"activo",entrega:3,rating:5,cert:"ISO 9001",pago:"30 días",notas:"Principal proveedor de PET. Entrega en 3 días hábiles. Certificado ISO."},
  {id:"p002",nombre:"Plastex Caribe",ciudad:"Cartagena",tel:"+57 315 400 6000",email:"ventas@plastexcaribe.co",contacto:"Ana Restrepo",material:"HDPE",mats_extra:"",precio_kg:1900,precio_neg:1750,volumen_min:500,volumen_max:5000,estado:"activo",entrega:1,rating:4,cert:"",pago:"Contado",notas:"Proveedor local. Recoger en planta. Excelente para volúmenes urgentes."},
  {id:"p003",nombre:"PropiRec Ltda",ciudad:"Bogotá",tel:"+57 317 200 8000",email:"gerencia@propirec.co",contacto:"Luis Vargas",material:"PP",mats_extra:"LDPE",precio_kg:1800,precio_neg:1650,volumen_min:500,volumen_max:10000,estado:"activo",entrega:4,rating:4,cert:"RUC",pago:"30 días",notas:"Buena calidad de PP molido. Volumen mínimo negociable para pedidos regulares."},
  {id:"p004",nombre:"EcoCycle Medellín",ciudad:"Medellín",tel:"+57 311 500 3000",email:"ventas@ecocycle.com.co",contacto:"María López",material:"PET",mats_extra:"ABS",precio_kg:2300,precio_neg:2100,volumen_min:1000,volumen_max:15000,estado:"activo",entrega:5,rating:5,cert:"ISO 14001",pago:"45 días",notas:"Especialistas en PET grado alimentario. Volumen mínimo alto pero precio competitivo."},
  {id:"p005",nombre:"CircularPP Caribe",ciudad:"Barranquilla",tel:"+57 316 300 7000",email:"ventas@circularpp.co",contacto:"Pedro Jiménez",material:"PP",mats_extra:"HDPE",precio_kg:1700,precio_neg:1600,volumen_min:700,volumen_max:6000,estado:"potencial",entrega:2,rating:3,cert:"",pago:"Contado",notas:"Precio competitivo pero calidad variable. Requiere inspección previa del lote."},
];
if(!S.proveedores.length){S.proveedores=PROV_INIT;saveS();}

// ─── CÁLCULOS ────────────────────────────────────────────────
function calcCostos(precio_kg,kg){
  const cp=DB.costos_proceso;
  const mp=precio_kg*kg;
  const lav=cp.lavado_kg*kg;
  const tri=cp.triturado_kg*kg;
  const pel=cp.peletizado_kg*kg;
  const hrs=Math.max(0.1,kg*0.08);
  const mo=cp.mano_obra_hora*hrs;
  const en=cp.energia_kwh_kg*kg;
  const sub=mp+lav+tri+pel+mo+en;
  const ov=sub*cp.overhead_pct;
  return{materia_prima:mp,lavado:lav,triturado:tri,peletizado:pel,mano_obra:mo,energia:en,overhead:ov,total:sub+ov};
}
function calcEcon(costo,mrg){
  const pct=DB.margenes[mrg]||0.40;
  const pv=costo/(1-pct);
  const gan=pv-costo;
  return{precio_venta:pv,ganancia:gan,margen_porcentaje:pct*100,roi:(gan/costo)*100};
}
function calcIVC(viab,recicla,roi,kg){
  const ft=Math.min(100,viab);
  const fm=Math.min(100,recicla);
  const fe=roi>=60?100:roi>=40?85:roi>=25?70:roi>=10?50:25;
  const fs=kg>=10?100:kg>=5?85:kg>=1?70:kg>=0.3?55:40;
  const ivc=Math.round(ft*0.35+fm*0.25+fe*0.25+fs*0.15);
  const cls=ivc>=85?["Excelente","#00E676","Alta prioridad de inversión. Proceso maduro y rentable."]:
            ivc>=70?["Bueno","#69F0AE","Viable con inversión moderada. Revisar cadena de suministro."]:
            ivc>=55?["Regular","#FFEB3B","Viable en economías de escala. Evaluar demanda local."]:
            ivc>=40?["Marginal","#FF9800","Requiere subsidios o asociaciones estratégicas."]:
                    ["Bajo","#F44336","No recomendado sin innovación tecnológica significativa."];
  return{ivc,clasificacion:cls[0],color:cls[1],recomendacion:cls[2],factores:{tecnico:ft,material:fm,economico:fe,escala:fs}};
}
function calcTiempo(mat,app,kg){
  const base=Math.round(mat.tiempo_proceso_min_por_kg*kg);
  return{base,extra:app.tiempo_extra_min,total:base+app.tiempo_extra_min};
}

// ─── NAVEGACIÓN ──────────────────────────────────────────────
const PAGES={
  analyzer:{id:"page-analyzer",title:"Analizador de Residuos",sub:"Identifica, valora y reutiliza plásticos con inteligencia"},
  materiales:{id:"page-materiales",title:"Catálogo de Materiales",sub:"Propiedades técnicas de cada tipo de plástico"},
  comparador:{id:"page-comparador",title:"Comparador de Aplicaciones",sub:"Evalúa y compara opciones de reutilización"},
  clientes:{id:"page-clientes",title:"Clientes",sub:"Empresas que compran tus productos terminados"},
  proveedores:{id:"page-proveedores",title:"Proveedores",sub:"Empresas que te venden materia prima plástica"},
  historial:{id:"page-historial",title:"Historial",sub:"Registro de análisis y cotizaciones realizadas"},
  cotizador:{id:"page-cotizador",title:"Cotizador Rápido",sub:"Genera cotizaciones profesionales para clientes"},
};
function navTo(name){
  document.querySelectorAll(".page").forEach(p=>p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active"));
  document.getElementById(PAGES[name].id).classList.add("active");
  const ni=document.querySelectorAll(".nav-item");
  const idx=Object.keys(PAGES).indexOf(name);
  if(ni[idx])ni[idx].classList.add("active");
  document.getElementById("page-title").textContent=PAGES[name].title;
  document.getElementById("page-sub").textContent=PAGES[name].sub;
  if(name==="historial"){renderHist();renderHistCots();}
  if(name==="materiales")renderCatalogo();
  if(name==="comparador")poblarComp();
  if(name==="clientes")renderCli();
  if(name==="proveedores")renderProveedores();
  if(name==="cotizador")poblarCotCli();
}

// ─── TOAST ───────────────────────────────────────────────────
let _tt;
function toast(msg,type="success"){
  const t=document.getElementById("toast");
  const ic={success:"✅",error:"❌",info:"ℹ️"};
  t.innerHTML=`<span>${ic[type]}</span> ${msg}`;
  t.className=`show ${type}`;
  clearTimeout(_tt);
  _tt=setTimeout(()=>{t.className="";},3500);
}

// ─── INIT ────────────────────────────────────────────────────
function init(){
  renderObjGrid();
}

// ─── OBJETO GRID ─────────────────────────────────────────────
function renderObjGrid(){
  const g=document.getElementById("obj-grid");
  g.innerHTML=Object.entries(DB.objetos).map(([id,o])=>`
    <div class="obj-card" data-id="${id}" onclick="selObj('${id}')">
      <span class="oi">${o.icono}</span><div class="on">${o.nombre}</div>
    </div>`).join("");
}
function selObj(id){
  S.objSel=id;S.matSel=null;S.appIdx=null;
  document.querySelectorAll(".obj-card").forEach(c=>c.classList.remove("selected"));
  document.querySelector(`.obj-card[data-id="${id}"]`).classList.add("selected");
  const obj=DB.objetos[id];
  const b=document.getElementById("obj-badge");b.textContent=obj.icono;b.style.display="block";
  const sm=document.getElementById("step-mat");sm.style.opacity="1";sm.style.pointerEvents="auto";
  const mats=obj.mats.map(id=>DB.materiales[id]?{id,...DB.materiales[id]}:null).filter(Boolean);
  document.getElementById("mat-chips").innerHTML=mats.map(m=>`
    <div class="mat-chip" data-id="${m.id}" onclick="selMat('${m.id}')" style="border-color:${m.color_hex}40;color:${m.color_hex};">
      <span class="cd" style="background:${m.color_hex};"></span>${m.id}<span class="cc">#${m.codigo_reciclaje}</span>
    </div>`).join("");
  ["step-app","step-par"].forEach(s=>{document.getElementById(s).style.opacity="0.4";document.getElementById(s).style.pointerEvents="none";});
  document.getElementById("app-list").innerHTML='<div style="font-size:13px;color:var(--t3);">↑ Selecciona el material primero</div>';
  document.getElementById("btn-analizar").disabled=true;
  hideRes();
}
function selMat(id){
  S.matSel=id;S.appIdx=null;
  document.querySelectorAll(".mat-chip").forEach(c=>c.classList.remove("selected"));
  document.querySelector(`.mat-chip[data-id="${id}"]`).classList.add("selected");
  const mat=DB.materiales[id];
  document.getElementById("precio-input").value=mat.precio_base_kg;
  document.getElementById("app-list").innerHTML=mat.aplicaciones.map((ap,i)=>`
    <div class="app-item" data-i="${i}" onclick="selApp(${i})">
      <div><div class="ai-name">${ap.producto}</div><div class="ai-mkt">🎯 ${ap.mercado}</div></div>
      <div style="text-align:right;"><div class="ai-kg">${ap.kg_necesarios} kg/ud</div>
        <div class="vbar"><div class="vfill" style="width:${ap.viabilidad}%"></div></div>
        <div style="font-size:10px;color:var(--t3);margin-top:2px;">${ap.viabilidad}%</div>
      </div>
    </div>`).join("");
  const sa=document.getElementById("step-app");sa.style.opacity="1";sa.style.pointerEvents="auto";
  document.getElementById("step-par").style.opacity="0.4";document.getElementById("step-par").style.pointerEvents="none";
  document.getElementById("btn-analizar").disabled=true;
}
function selApp(i){
  S.appIdx=i;
  document.querySelectorAll(".app-item").forEach(a=>a.classList.remove("selected"));
  document.querySelectorAll(".app-item")[i].classList.add("selected");
  const sp=document.getElementById("step-par");sp.style.opacity="1";sp.style.pointerEvents="auto";
  document.getElementById("btn-analizar").disabled=false;
}
function selMrg(btn){
  document.querySelectorAll(".mrg-btn").forEach(b=>b.classList.remove("selected"));
  btn.classList.add("selected");S.mrg=btn.dataset.val;
}

// ─── ANÁLISIS ────────────────────────────────────────────────
let charts={c:null,i:null,e:null};
function destroyCharts(){Object.values(charts).forEach(c=>{if(c)c.destroy();});charts={c:null,i:null,e:null};}

function ejecutarAnalisis(){
  const btn=document.getElementById("btn-analizar");
  btn.disabled=true;btn.innerHTML='<span class="spin"></span> Calculando...';
  const mat=DB.materiales[S.matSel];
  const app=mat.aplicaciones[S.appIdx];
  const precio=parseFloat(document.getElementById("precio-input").value)||mat.precio_base_kg;
  const kg=parseFloat(document.getElementById("cant-input").value)||app.kg_necesarios;
  const costos=calcCostos(precio,kg);
  const economia=calcEcon(costos.total,S.mrg);
  const ivc=calcIVC(app.viabilidad,mat.propiedades.reciclabilidad,economia.roi,kg);
  const tiempo=calcTiempo(mat,app,kg);
  S.lastAnalisis={objeto_id:S.objSel,material:{id:S.matSel,nombre:S.matSel,nombre_completo:mat.nombre_completo,codigo_reciclaje:mat.codigo_reciclaje,color_hex:mat.color_hex,propiedades:mat.propiedades,precio_kg:precio},aplicacion:app,cantidad_kg:kg,costos,economia,ivc,tiempo,proveedores:mat.proveedores||[],fecha:new Date().toISOString()};
  renderRes(S.lastAnalisis);
  toast("Análisis completado exitosamente");
  btn.disabled=false;btn.innerHTML="🔬 Ejecutar Análisis";
}

function renderRes(d){
  document.getElementById("empty-results").style.display="none";
  document.getElementById("results-panel").classList.add("vis");
  const t=d.tiempo;const hrs=Math.floor(t.total/60);const mins=t.total%60;
  const ts=hrs>0?`${hrs}h ${mins}min`:`${t.total} min`;
  const dias=(t.total/480).toFixed(2);
  document.getElementById("t-badge").textContent=`⏱️ ${ts}`;
  document.getElementById("t-det").textContent=`Para ${d.cantidad_kg} kg de ${d.material.nombre}`;
  document.getElementById("t-desg").innerHTML=`<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;"><div style="font-size:11px;color:var(--t3);">⚙️ Proceso: <span style="color:#00BCD4;font-weight:600;">${t.base} min</span></div><div style="font-size:11px;color:var(--t3);">🔨 Conformado: <span style="color:#00BCD4;font-weight:600;">${t.extra} min</span></div><div style="font-size:11px;color:var(--t3);">📅 Equivalente: <span style="color:#00BCD4;font-weight:600;">${dias} días</span></div></div>`;
  document.getElementById("r-costo").textContent=fCOP(d.costos.total);
  document.getElementById("r-precio").textContent=fCOP(d.economia.precio_venta);
  document.getElementById("r-roi").textContent=`${d.economia.roi.toFixed(1)}%`;
  document.getElementById("r-rec").textContent=`${d.material.propiedades.reciclabilidad}%`;
  // IVC gauge
  const ivc=d.ivc.ivc;const circ=2*Math.PI*68;
  const off=circ-(ivc/100)*circ;
  const circle=document.getElementById("ivc-circle");
  circle.style.strokeDashoffset=off;circle.style.stroke=d.ivc.color;
  document.getElementById("ivc-num").textContent=ivc;document.getElementById("ivc-num").style.color=d.ivc.color;
  document.getElementById("ivc-cls").textContent=d.ivc.clasificacion;document.getElementById("ivc-cls").style.color=d.ivc.color;
  document.getElementById("ivc-rec").textContent=d.ivc.recomendacion;
  [["tec","tecnico","var(--acc)"],["mat","material","var(--blue)"],["eco","economico","var(--orange)"],["esc","escala","var(--purple)"]].forEach(([k,f,col])=>{
    document.getElementById(`pr-${k}`).style.display="block";
    document.getElementById(`pv-${k}`).textContent=d.ivc.factores[f];
    const bar=document.getElementById(`pb-${k}`);bar.style.width="0%";bar.style.background=col;
    setTimeout(()=>{bar.style.width=`${d.ivc.factores[f]}%`;},100);
  });
  // Costos
  const c=d.costos;const e=d.economia;
  document.getElementById("cost-table").innerHTML=`
    <div class="ct-row"><span class="ct-k">Materia prima (${d.cantidad_kg} kg × ${fCOP(d.material.precio_kg)}/kg)</span><span class="ct-a">${fCOP(c.materia_prima)}</span></div>
    <div class="ct-row"><span class="ct-k">Lavado y pretratamiento</span><span class="ct-a">${fCOP(c.lavado)}</span></div>
    <div class="ct-row"><span class="ct-k">Triturado</span><span class="ct-a">${fCOP(c.triturado)}</span></div>
    <div class="ct-row"><span class="ct-k">Peletizado / Conformado</span><span class="ct-a">${fCOP(c.peletizado)}</span></div>
    <div class="ct-row"><span class="ct-k">Mano de obra</span><span class="ct-a">${fCOP(c.mano_obra)}</span></div>
    <div class="ct-row"><span class="ct-k">Energía eléctrica</span><span class="ct-a">${fCOP(c.energia)}</span></div>
    <div class="ct-row"><span class="ct-k">Overhead (22%)</span><span class="ct-a">${fCOP(c.overhead)}</span></div>
    <div class="ct-row tot"><span class="ct-k">COSTO TOTAL</span><span class="ct-a">${fCOP(c.total)}</span></div>
    <div class="ct-row tot hi"><span class="ct-k">PRECIO DE VENTA (${e.margen_porcentaje.toFixed(0)}% margen)</span><span class="ct-a">${fCOP(e.precio_venta)}</span></div>
    <div class="ct-row tot hi"><span class="ct-k">GANANCIA NETA</span><span class="ct-a">${fCOP(e.ganancia)}</span></div>`;
  // Propiedades
  const p=d.material.propiedades;
  document.getElementById("mat-props-title").textContent=`🧪 ${d.material.nombre_completo} — Código #${d.material.codigo_reciclaje}`;
  document.getElementById("mat-props-grid").innerHTML=`
    <div class="prop-item"><div class="prop-k">Densidad</div><div class="prop-v">${p.densidad}</div></div>
    <div class="prop-item"><div class="prop-k">Temp. Fusión</div><div class="prop-v">${p.temp_fusion}</div></div>
    <div class="prop-item"><div class="prop-k">Resistencia Química</div><div class="prop-v">${p.resistencia_quimica}</div></div>
    <div class="prop-item"><div class="prop-k">Transparencia</div><div class="prop-v">${p.transparencia}</div></div>
    <div class="prop-item"><div class="prop-k">Precio/kg ref.</div><div class="prop-v" style="color:var(--acc)">${fCOP(d.material.precio_kg)}</div></div>
    <div class="prop-item"><div class="prop-k">Reciclabilidad</div><div class="prop-v" style="color:var(--acc)">${p.reciclabilidad}%</div></div>`;
  // Proveedores
  document.getElementById("prov-list").innerHTML=d.proveedores.length?d.proveedores.map(p=>`
    <div class="prov-card">
      <div class="prov-n">🏭 ${p.nombre}</div><div class="prov-c">📍 ${p.ciudad}, Colombia</div>
      <div class="prov-d">
        <div><div class="prov-dl">Precio/kg</div><div class="prov-dv" style="color:var(--acc)">${fCOP(p.precio_compra)}</div></div>
        <div><div class="prov-dl">Vol. mínimo</div><div class="prov-dv">${p.volumen_min_kg.toLocaleString()} kg</div></div>
        <div><div class="prov-dl">Contacto</div><div class="prov-dv" style="color:var(--blue)">${p.contacto}</div></div>
      </div>
    </div>`).join(""):'<div style="font-size:13px;color:var(--t3);text-align:center;padding:16px;">Sin proveedores</div>';
  setTimeout(()=>renderCharts(d),200);
}

function renderCharts(d){
  destroyCharts();
  const c=d.costos;const e=d.economia;const f=d.ivc.factores;
  const cd={plugins:{legend:{labels:{color:"#8B949E",font:{family:"Space Grotesk",size:11}}}},responsive:true,maintainAspectRatio:false};
  charts.c=new Chart(document.getElementById("chart-costos"),{type:"doughnut",data:{labels:["Mat. Prima","Lavado","Triturado","Peletizado","Mano Obra","Energía","Overhead"],datasets:[{data:[c.materia_prima,c.lavado,c.triturado,c.peletizado,c.mano_obra,c.energia,c.overhead],backgroundColor:["#00FF88","#58A6FF","#FF9500","#BD93F9","#FF4444","#FFCC00","#4FC3F7"],borderWidth:0,hoverOffset:4}]},options:{...cd,cutout:"65%"}});
  charts.i=new Chart(document.getElementById("chart-ivc"),{type:"radar",data:{labels:["Técnico","Material","Económico","Escala"],datasets:[{label:"Factores IVC",data:[f.tecnico,f.material,f.economico,f.escala],backgroundColor:"rgba(0,255,136,.15)",borderColor:"#00FF88",borderWidth:2,pointBackgroundColor:"#00FF88"}]},options:{...cd,scales:{r:{beginAtZero:true,max:100,grid:{color:"#30363D"},ticks:{color:"#484F58",backdropColor:"transparent",font:{size:10}},pointLabels:{color:"#8B949E",font:{size:11}}}}}});
  charts.e=new Chart(document.getElementById("chart-econ"),{type:"bar",data:{labels:["Costo","Precio Venta","Ganancia"],datasets:[{label:"COP $",data:[c.total,e.precio_venta,e.ganancia],backgroundColor:["rgba(255,149,0,.7)","rgba(0,255,136,.7)","rgba(88,166,255,.7)"],borderColor:["#FF9500","#00FF88","#58A6FF"],borderWidth:1,borderRadius:6}]},options:{...cd,scales:{x:{grid:{color:"#30363D"},ticks:{color:"#8B949E"}},y:{grid:{color:"#30363D"},ticks:{color:"#8B949E",callback:v=>"$"+Math.round(v).toLocaleString("es-CO")}}}}});
}

function hideRes(){
  document.getElementById("results-panel").classList.remove("vis");
  document.getElementById("empty-results").style.display="block";
  destroyCharts();
}

function resetForm(){
  S.objSel=null;S.matSel=null;S.appIdx=null;S.lastAnalisis=null;
  document.querySelectorAll(".obj-card").forEach(c=>c.classList.remove("selected"));
  document.getElementById("obj-badge").style.display="none";
  document.getElementById("mat-chips").innerHTML='<div style="font-size:13px;color:var(--t3);">↑ Primero selecciona el tipo de residuo</div>';
  document.getElementById("app-list").innerHTML='<div style="font-size:13px;color:var(--t3);">↑ Selecciona el material primero</div>';
  document.getElementById("precio-input").value="";document.getElementById("cant-input").value="";
  ["step-mat","step-app","step-par"].forEach(s=>{document.getElementById(s).style.opacity="0.4";document.getElementById(s).style.pointerEvents="none";});
  document.getElementById("btn-analizar").disabled=true;
  hideRes();
}

// ─── CATÁLOGO ────────────────────────────────────────────────
function renderCatalogo(){
  document.getElementById("mat-catalog").innerHTML=Object.entries(DB.materiales).map(([id,m])=>`
    <div class="mat-cat-card" style="border-top:3px solid ${m.color_hex};" onclick="navTo('comparador');setTimeout(()=>{document.getElementById('comp-mat').value='${id}';ejecutarComp();},200)">
      <div class="mat-cat-hdr">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
          <div style="width:44px;height:44px;border-radius:10px;background:${m.color_hex}20;border:1px solid ${m.color_hex}40;display:flex;align-items:center;justify-content:center;"><span style="font-size:18px;font-weight:700;color:${m.color_hex};font-family:var(--mono);">${m.codigo_reciclaje}</span></div>
          <div><div style="font-size:18px;font-weight:700;color:${m.color_hex};">${id}</div><div style="font-size:11px;color:var(--t3);">${m.nombre_completo}</div></div>
        </div>
        <div style="font-size:12px;color:var(--t2);line-height:1.5;">${m.descripcion}</div>
      </div>
      <div class="mat-cat-body">
        <div class="pr"><div class="pr-hdr"><span class="pr-n">Reciclabilidad</span><span class="pr-v" style="color:${m.color_hex}">${m.propiedades.reciclabilidad}%</span></div><div class="pr-t"><div class="pr-f" style="width:${m.propiedades.reciclabilidad}%;background:${m.color_hex};"></div></div></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;">
          <div class="prop-item"><div class="prop-k">Precio ref.</div><div class="prop-v" style="color:var(--acc)">${fCOP(m.precio_base_kg)}/kg</div></div>
          <div class="prop-item"><div class="prop-k">Aplicaciones</div><div class="prop-v">${m.aplicaciones.length} opciones</div></div>
        </div>
      </div>
      <div class="mat-cat-apps"><div style="font-size:10px;color:var(--t3);margin-bottom:6px;text-transform:uppercase;">Productos posibles</div>${m.aplicaciones.map(a=>`<span class="mat-app-tag">${a.producto.split("(")[0].trim()}</span>`).join("")}</div>
    </div>`).join("");
}

// ─── COMPARADOR ──────────────────────────────────────────────
function poblarComp(){
  const sel=document.getElementById("comp-mat");
  if(sel.options.length>1)return;
  Object.entries(DB.materiales).forEach(([id,m])=>{const o=document.createElement("option");o.value=id;o.textContent=`${id} — ${m.nombre_completo}`;sel.appendChild(o);});
}
function ejecutarComp(){
  const matId=document.getElementById("comp-mat").value;
  if(!matId){toast("Selecciona un material","info");return;}
  const precio=parseFloat(document.getElementById("comp-precio").value);
  const mat=DB.materiales[matId];const p=precio||mat.precio_base_kg;
  const res=mat.aplicaciones.map((ap,i)=>{
    const c=calcCostos(p,ap.kg_necesarios);const e=calcEcon(c.total,"objetivo");const iv=calcIVC(ap.viabilidad,mat.propiedades.reciclabilidad,e.roi,ap.kg_necesarios);
    return{index:i,producto:ap.producto,mercado:ap.mercado,kg:ap.kg_necesarios,costo:c.total,venta:e.precio_venta,roi:e.roi,ivc:iv.ivc,color:iv.color,cls:iv.clasificacion};
  }).sort((a,b)=>b.ivc-a.ivc);
  document.getElementById("comp-results").innerHTML=`
    <div style="margin-bottom:16px;"><div style="font-size:14px;font-weight:600;">${matId} — ${mat.nombre_completo}</div><div style="font-size:12px;color:var(--t3);">Precio: <span style="color:var(--acc);font-family:var(--mono);">${fCOP(p)}/kg</span> · ${res.length} aplicaciones · <span style="color:var(--t2);">Clic en fila para detalle</span></div></div>
    <div style="overflow-x:auto;"><table class="ctbl"><thead><tr><th>#</th><th>Producto</th><th>Mercado</th><th>Kg/ud</th><th>Costo</th><th>Precio Venta</th><th>ROI</th><th>IVC</th></tr></thead>
    <tbody>${res.map((r,i)=>`<tr onclick="mostrarDetalle('${matId}',${r.index},${p})"><td style="color:var(--t3);">${i+1}</td><td style="font-weight:600;">${r.producto}</td><td style="color:var(--t3);font-size:11px;">${r.mercado}</td><td class="mono">${r.kg}</td><td class="mono">${fCOP(r.costo)}</td><td class="mono" style="color:var(--acc);">${fCOP(r.venta)}</td><td class="mono" style="color:var(--blue);">${r.roi.toFixed(1)}%</td><td><span class="ivc-badge" style="background:${r.color}20;color:${r.color};border:1px solid ${r.color}40;">${r.ivc} ${r.cls}</span></td></tr>`).join("")}
    </tbody></table></div>`;
  document.getElementById("cd-panel").classList.remove("vis");
}
function mostrarDetalle(matId,idx,precio){
  const mat=DB.materiales[matId];const app=mat.aplicaciones[idx];
  const c=calcCostos(precio,app.kg_necesarios);const e=calcEcon(c.total,"objetivo");const iv=calcIVC(app.viabilidad,mat.propiedades.reciclabilidad,e.roi,app.kg_necesarios);
  const t=calcTiempo(mat,app,app.kg_necesarios);const ts=Math.floor(t.total/60)>0?`${Math.floor(t.total/60)}h ${t.total%60}min`:`${t.total} min`;
  document.getElementById("cd-title").textContent=`📊 ${app.producto}`;
  document.getElementById("cd-content").innerHTML=`
    <div class="g2" style="gap:12px;margin-bottom:16px;">
      <div class="mc green" style="padding:14px;"><div class="mt">Costo Total</div><div class="mv" style="font-size:18px;">${fCOP(c.total)}</div><div class="ms">${app.kg_necesarios} kg/ud</div></div>
      <div class="mc blue" style="padding:14px;"><div class="mt">Precio Venta</div><div class="mv" style="font-size:18px;color:var(--blue);">${fCOP(e.precio_venta)}</div><div class="ms">Margen 40%</div></div>
      <div class="mc orange" style="padding:14px;"><div class="mt">ROI</div><div class="mv" style="font-size:18px;color:var(--orange);">${e.roi.toFixed(1)}%</div><div class="ms">Ganancia ${fCOP(e.ganancia)}</div></div>
      <div class="mc cyan" style="padding:14px;"><div class="mt">Tiempo Prod.</div><div class="mv" style="font-size:18px;color:#00BCD4;">${ts}</div><div class="ms">por unidad</div></div>
    </div>
    <div style="background:var(--card2);border-radius:var(--rs);padding:14px;margin-bottom:12px;">
      <div style="font-size:11px;color:var(--t3);margin-bottom:8px;">IVC: ${iv.clasificacion}</div>
      <div style="display:flex;align-items:center;gap:12px;"><div style="font-size:32px;font-weight:700;font-family:var(--mono);color:${iv.color};">${iv.ivc}</div><div style="font-size:12px;color:var(--t2);">${iv.recomendacion}</div></div>
    </div>
    <div style="font-size:12px;color:var(--t3);">🎯 Mercado: <span style="color:var(--t1)">${app.mercado}</span></div>`;
  document.getElementById("cd-panel").classList.add("vis");
  document.getElementById("cd-panel").scrollIntoView({behavior:"smooth",block:"nearest"});
}
function cerrarDetalle(){document.getElementById("cd-panel").classList.remove("vis");}
function irComparador(){
  if(!S.matSel){toast("Selecciona un material primero","info");return;}
  navTo("comparador");
  setTimeout(()=>{document.getElementById("comp-mat").value=S.matSel;ejecutarComp();},100);
}

// ─── HISTORIAL ───────────────────────────────────────────────
function renderHist(){
  const cont=document.getElementById("hist-content");
  if(!S.historial.length){cont.innerHTML='<div class="empty"><div class="ei">📋</div><p>No hay análisis guardados</p></div>';return;}
  cont.innerHTML=`<div style="overflow-x:auto;"><table class="htbl">
    <thead><tr><th>Fecha</th><th>Objeto</th><th>Material</th><th>Producto</th><th>Kg</th><th>Costo</th><th>Venta</th><th>ROI</th><th>IVC</th><th>Acciones</th></tr></thead>
    <tbody>${S.historial.map(h=>`<tr>
      <td style="color:var(--t3);font-size:11px;">${new Date(h.fecha).toLocaleDateString("es-CO")}</td>
      <td>${(h.objeto_id||"").toUpperCase()}</td>
      <td><span style="font-weight:700;color:var(--acc);">${h.material.nombre}</span></td>
      <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${h.aplicacion.producto}</td>
      <td class="mono">${h.cantidad_kg}</td>
      <td class="mono">${fCOP(h.costos.total)}</td>
      <td class="mono" style="color:var(--acc);">${fCOP(h.economia.precio_venta)}</td>
      <td class="mono" style="color:var(--blue);">${h.economia.roi.toFixed(1)}%</td>
      <td><span class="ivc-badge" style="background:${h.ivc.color}20;color:${h.ivc.color};border:1px solid ${h.ivc.color}40;">${h.ivc.ivc}</span></td>
      <td style="display:flex;gap:6px;">
        <button class="btn btn-p btn-sm" onclick="exportarAnalisisPDFById(S.historial.find(x=>x.id==='${h.id}'))">📄 PDF</button>
        <button class="btn btn-d btn-sm" onclick="delHist('${h.id}')">✕</button>
      </td>
    </tr>`).join("")}</tbody></table></div>`;
}
function guardarAnalisis(){
  if(!S.lastAnalisis){toast("Ejecuta un análisis primero","info");return;}
  S.historial.unshift({...S.lastAnalisis,id:"h_"+Date.now()});
  saveS();toast("Análisis guardado en historial");
}
function delHist(id){S.historial=S.historial.filter(h=>h.id!==id);saveS();renderHist();toast("Registro eliminado","info");}
function limpiarHist(){if(!confirm("¿Eliminar TODO el historial?"))return;S.historial=[];saveS();renderHist();toast("Historial limpiado","info");}

// ─── CLIENTES ────────────────────────────────────────────────
let _fCli="todos",_editId=null;
function renderCli(f){
  if(f)_fCli=f;
  const filtered=_fCli==="todos"?S.clientes:S.clientes.filter(c=>c.estado===_fCli);
  const grid=document.getElementById("cli-grid");
  if(!filtered.length){grid.innerHTML='<div style="grid-column:1/-1;"><div class="empty"><div class="ei">👥</div><p>Sin clientes en esta categoría</p></div></div>';return;}
  grid.innerHTML=filtered.map(c=>`
    <div class="cli-card">
      <div class="cli-n">${c.nombre}</div><div class="cli-s">🏢 ${c.sector} · Comprador de producto terminado</div>
      <div class="cli-bdg">
        <span class="cbdg cbdg-${c.estado[0]}">${c.estado.charAt(0).toUpperCase()+c.estado.slice(1)}</span>
        ${c.producto?`<span class="cbdg" style="background:rgba(0,255,136,.08);border:1px solid rgba(0,255,136,.2);color:var(--acc);">📦 ${c.producto}</span>`:""}
        ${c.rating?`<span style="font-size:11px;">${renderStars(c.rating)}</span>`:""}
      </div>
      <div class="cli-info">
        <div><div class="cli-il">Ciudad</div><div class="cli-iv">📍 ${c.ciudad||"—"}</div></div>
        <div><div class="cli-il">Unidades/mes</div><div class="cli-iv" style="color:var(--blue);">📦 ${c.volumen?(c.volumen.toLocaleString()+" und/mes"):"—"}</div></div>
        <div><div class="cli-il">Teléfono</div><div class="cli-iv">${c.tel||"—"}</div></div>
        <div><div class="cli-il">Email</div><div class="cli-iv" style="font-size:11px;word-break:break-all;">${c.email||"—"}</div></div>
      </div>
      ${c.notas?`<div style="margin-top:10px;font-size:11px;color:var(--t3);border-top:1px solid var(--border);padding-top:8px;">${c.notas}</div>`:""}
      <div class="cli-act">
        <button class="btn btn-b btn-sm" onclick="editCli('${c.id}')">✏️ Editar</button>
        <button class="btn btn-g btn-sm" onclick="cotizarCli('${c.id}')">🧾 Cotizar</button>
        <button class="btn btn-d btn-sm" onclick="delCli('${c.id}')">✕</button>
      </div>
    </div>`).join("");
}
function filtCli(t){
  _fCli=t;
  document.querySelectorAll("[id^='f-']").forEach(b=>{b.style.borderColor="";b.style.color="";});
  const btn=document.getElementById("f-"+t);
  if(btn){btn.style.borderColor="var(--acc)";btn.style.color="var(--acc)";}
  renderCli();
}
function abrirModal(){
  _editId=null;document.getElementById("modal-ttl").textContent="➕ Nuevo Cliente";
  ["cli-nom","cli-tel","cli-em","cli-ciu","cli-not","cli-prod"].forEach(id=>document.getElementById(id).value="");
  document.getElementById("cli-sec").value="Construcción";document.getElementById("cli-est").value="potencial";
  document.getElementById("cli-vol").value="";
  document.getElementById("modal-cli").classList.add("show");
}
function editCli(id){
  const c=S.clientes.find(x=>x.id===id);if(!c)return;
  _editId=id;document.getElementById("modal-ttl").textContent="✏️ Editar Cliente";
  document.getElementById("cli-nom").value=c.nombre;
  document.getElementById("cli-sec").value=c.sector;
  document.getElementById("cli-est").value=c.estado;
  document.getElementById("cli-ciu").value=c.ciudad||"";
  document.getElementById("cli-tel").value=c.tel||"";
  document.getElementById("cli-em").value=c.email||"";
  document.getElementById("cli-prod").value=c.producto||"";
  document.getElementById("cli-vol").value=c.volumen||"";
  document.getElementById("cli-not").value=c.notas||"";
  document.getElementById("cli-freq").value=c.frecuencia||3;
  document.getElementById("cli-pago").value=c.puntualidad_pago||3;
  document.getElementById("cli-antig").value=c.antiguedad||0;
  document.getElementById("cli-ncots").value=c.n_cotizaciones||0;
  document.getElementById("cli-rating-preview").value=c.rating?renderStars(c.rating)+" ("+c.rating+"/5)":"—";
  document.getElementById("modal-cli").classList.add("show");
}
function guardarCliente(){
  const nom=document.getElementById("cli-nom").value.trim();
  if(!nom){toast("El nombre es obligatorio","error");return;}
  const base={
    id:_editId||"c_"+Date.now(),
    nombre:nom,
    sector:document.getElementById("cli-sec").value,
    estado:document.getElementById("cli-est").value,
    ciudad:document.getElementById("cli-ciu").value,
    tel:document.getElementById("cli-tel").value,
    email:document.getElementById("cli-em").value,
    producto:document.getElementById("cli-prod").value,
    volumen:parseInt(document.getElementById("cli-vol").value)||0,
    notas:document.getElementById("cli-not").value,
    frecuencia:parseInt(document.getElementById("cli-freq").value)||3,
    puntualidad_pago:parseInt(document.getElementById("cli-pago").value)||3,
    antiguedad:parseInt(document.getElementById("cli-antig").value)||0,
    n_cotizaciones:parseInt(document.getElementById("cli-ncots").value)||0,
  };
  base.rating = calcRatingCli(base);
  if(_editId){S.clientes=S.clientes.map(c=>c.id===_editId?base:c);toast("Cliente actualizado ✅");}
  else{S.clientes.unshift(base);toast("Cliente agregado ✅");}
  saveS();cerrarModal();renderCli();
}
function delCli(id){if(!confirm("¿Eliminar este cliente?"))return;S.clientes=S.clientes.filter(c=>c.id!==id);saveS();toast("Cliente eliminado","info");renderCli();}
function cerrarModal(){document.getElementById("modal-cli").classList.remove("show");}
function cotizarCli(id){
  navTo("cotizador");
  setTimeout(()=>{
    const c=S.clientes.find(x=>x.id===id);
    const sel=document.getElementById("cot-cli");sel.value=id;
    if(!sel.value&&c){const o=document.createElement("option");o.value=id;o.textContent=c.nombre;sel.appendChild(o);sel.value=id;}
  },300);
}

// ─── COTIZADOR ───────────────────────────────────────────────
function poblarCotCli(){
  const sel=document.getElementById("cot-cli");
  sel.innerHTML='<option value="">— Selecciona un cliente —</option>';
  S.clientes.forEach(c=>{const o=document.createElement("option");o.value=c.id;o.textContent=`${c.nombre} (${c.ciudad||c.sector})`;sel.appendChild(o);});
  if(S.lastAnalisis){
    document.getElementById("cot-prod").value=S.lastAnalisis.aplicacion.producto;
    document.getElementById("cot-precio").value=Math.round(S.lastAnalisis.economia.precio_venta);
  }
}
function genCot(){
  const cliId=document.getElementById("cot-cli").value;
  const prod=document.getElementById("cot-prod").value.trim();
  const cant=parseInt(document.getElementById("cot-cant").value)||0;
  const pu=parseFloat(document.getElementById("cot-precio").value)||0;
  const desc=parseFloat(document.getElementById("cot-desc").value)||0;
  const notas=document.getElementById("cot-notas").value;
  if(!prod||!cant||!pu){toast("Completa producto, cantidad y precio","error");return;}
  const sub=cant*pu;const dv=sub*(desc/100);const total=sub-dv;
  const cli=S.clientes.find(c=>c.id===cliId);
  const nro="COT-"+Date.now().toString().slice(-6);
  const fecha=new Date().toLocaleDateString("es-CO");
  document.getElementById("cot-empty").style.display="none";
  document.getElementById("cot-preview").style.display="block";
  document.getElementById("cot-prev-content").innerHTML=`
    <div style="border:1px solid var(--border);border-radius:var(--rs);padding:20px;background:var(--bg2);">
      <div style="display:flex;justify-content:space-between;margin-bottom:20px;">
        <div><div style="font-size:20px;font-weight:700;color:var(--acc);">🌴 NovaPLAST CTG</div><div style="font-size:11px;color:var(--t3);">Cartagena de Indias, Colombia</div></div>
        <div style="text-align:right;"><div style="font-size:14px;font-weight:700;">Nº ${nro}</div><div style="font-size:11px;color:var(--t3);">${fecha}</div></div>
      </div>
      ${cli?`<div style="background:var(--card2);border-radius:var(--rs);padding:12px;margin-bottom:16px;"><div style="font-size:11px;color:var(--t3);margin-bottom:4px;">PARA:</div><div style="font-weight:700;">${cli.nombre}</div><div style="font-size:12px;color:var(--t3);">${cli.sector} · ${cli.ciudad||""}</div></div>`:""}
      <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
        <thead><tr style="border-bottom:1px solid var(--border);"><th style="text-align:left;padding:8px;font-size:11px;color:var(--t3);">Producto</th><th style="text-align:right;padding:8px;font-size:11px;color:var(--t3);">Cant.</th><th style="text-align:right;padding:8px;font-size:11px;color:var(--t3);">P. Unit.</th><th style="text-align:right;padding:8px;font-size:11px;color:var(--t3);">Total</th></tr></thead>
        <tbody><tr><td style="padding:10px 8px;font-size:13px;">${prod}</td><td style="padding:10px 8px;text-align:right;font-family:var(--mono);">${cant} und</td><td style="padding:10px 8px;text-align:right;font-family:var(--mono);">${fCOP(pu)}</td><td style="padding:10px 8px;text-align:right;font-family:var(--mono);">${fCOP(sub)}</td></tr></tbody>
      </table>
      ${desc>0?`<div style="display:flex;justify-content:space-between;padding:6px 8px;font-size:13px;"><span style="color:var(--t3);">Descuento (${desc}%)</span><span style="color:var(--red);font-family:var(--mono);">-${fCOP(dv)}</span></div>`:""}
      <div style="display:flex;justify-content:space-between;padding:10px 8px;font-size:16px;font-weight:700;border-top:2px solid var(--border);"><span>TOTAL</span><span style="color:var(--acc);font-family:var(--mono);">${fCOP(total)}</span></div>
      ${notas?`<div style="margin-top:12px;padding:10px;background:var(--card2);border-radius:var(--rs);font-size:12px;color:var(--t2);">${notas}</div>`:""}
    </div>`;
  window._cot={id:nro,cliId,cliente:cli?.nombre||"Sin cliente",producto:prod,cantidad:cant,precioUnit:pu,descuento:desc,subtotal:sub,descuentoValor:dv,total,notas,fecha};
  // Auto-guardar en historial de cotizaciones
  S.cotizaciones.unshift({...window._cot});
  saveS();
  toast(`Cotización ${nro} guardada automáticamente ✅`);
}
function exportarCotPDF(){
  if(!window._cot){toast("Genera una cotización primero","info");return;}
  exportarCotPDFById(window._cot);
}
async function exportarCotPDFById(cot){
  try{
    const r=await fetch("/exportar/cotizacion_pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(cot)});
    if(!r.ok){const e=await r.json();toast(e.error||"Error al exportar","error");return;}
    const blob=await r.blob();const url=URL.createObjectURL(blob);
    const a=document.createElement("a");a.href=url;a.download=`Cotizacion_${cot.id}.pdf`;a.click();
    toast("PDF de cotización descargado ✅");
  }catch(e){toast("Error: "+e.message,"error");}
}
function guardarCot(){
  // Mantener por compatibilidad, ya se guarda automáticamente
  toast("La cotización ya fue guardada automáticamente","info");
}
async function exportarAnalisisPDFById(analisis){
  if(!analisis){toast("Análisis no disponible","error");return;}
  try{
    const r=await fetch("/exportar/pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(analisis)});
    if(!r.ok){const e=await r.json();toast(e.error||"Error al exportar","error");return;}
    const blob=await r.blob();const url=URL.createObjectURL(blob);
    const a=document.createElement("a");a.href=url;
    a.download=`NovaPLAST_Analisis_${analisis.material?.nombre||""}_.pdf`;a.click();
    toast("PDF de análisis descargado ✅");
  }catch(e){toast("Error: "+e.message,"error");}
}

// ─── HISTORIAL TABS ───────────────────────────────────────────
let _htab="analisis";
function switchHTab(tab){
  _htab=tab;
  document.getElementById("hist-panel-analisis").style.display=tab==="analisis"?"block":"none";
  document.getElementById("hist-panel-cots").style.display=tab==="cots"?"block":"none";
  document.getElementById("hist-btns-analisis").style.display=tab==="analisis"?"flex":"none";
  document.getElementById("hist-btns-cots").style.display=tab==="cots"?"flex":"none";
  document.getElementById("htab-analisis").style.borderColor=tab==="analisis"?"var(--acc)":"";
  document.getElementById("htab-analisis").style.color=tab==="analisis"?"var(--acc)":"";
  document.getElementById("htab-cots").style.borderColor=tab==="cots"?"var(--acc)":"";
  document.getElementById("htab-cots").style.color=tab==="cots"?"var(--acc)":"";
}
function renderHistCots(){
  const cont=document.getElementById("hist-cots-content");
  if(!S.cotizaciones.length){cont.innerHTML='<div class="empty"><div class="ei">🧾</div><p>No hay cotizaciones guardadas</p></div>';return;}
  cont.innerHTML=`<div style="overflow-x:auto;"><table class="htbl">
    <thead><tr><th>Nº</th><th>Fecha</th><th>Cliente</th><th>Producto</th><th>Cant.</th><th>Total</th><th>Acciones</th></tr></thead>
    <tbody>${S.cotizaciones.map(ct=>`<tr>
      <td class="mono" style="color:var(--acc);">${ct.id}</td>
      <td style="color:var(--t3);font-size:11px;">${ct.fecha}</td>
      <td style="font-weight:600;">${ct.cliente}</td>
      <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${ct.producto}</td>
      <td class="mono">${(ct.cantidad||0).toLocaleString()} und</td>
      <td class="mono" style="color:var(--acc);">${fCOP(ct.total)}</td>
      <td style="display:flex;gap:6px;">
        <button class="btn btn-p btn-sm" onclick="exportarCotPDFById(${JSON.stringify(ct).replace(/"/g,"&quot;")})">📄 PDF</button>
        <button class="btn btn-d btn-sm" onclick="delCot('${ct.id}')">✕</button>
      </td>
    </tr>`).join("")}</tbody></table></div>`;
}
function delCot(id){S.cotizaciones=S.cotizaciones.filter(c=>c.id!==id);saveS();renderHistCots();toast("Cotización eliminada","info");}
function limpiarHistCots(){if(!confirm("¿Eliminar TODAS las cotizaciones?"))return;S.cotizaciones=[];saveS();renderHistCots();toast("Cotizaciones eliminadas","info");}

// ─── PROVEEDORES ──────────────────────────────────────────────
let _editProvId=null;
let _provCharts={precios:null,ciudades:null};
let _provViewActive=false;

function getFilteredProveedores(){
  const search=(document.getElementById("prov-search")?.value||"").toLowerCase();
  const fMat=document.getElementById("prov-filter-mat")?.value||"";
  const fEst=document.getElementById("prov-filter-est")?.value||"";
  const sort=document.getElementById("prov-sort")?.value||"nombre";
  let list=[...S.proveedores];
  if(search)list=list.filter(p=>p.nombre.toLowerCase().includes(search)||((p.ciudad||"").toLowerCase().includes(search))||((p.material||"").toLowerCase().includes(search)));
  if(fMat)list=list.filter(p=>p.material===fMat||(p.mats_extra||"").includes(fMat));
  if(fEst)list=list.filter(p=>p.estado===fEst);
  if(sort==="precio_asc")list.sort((a,b)=>(a.precio_kg||0)-(b.precio_kg||0));
  else if(sort==="precio_desc")list.sort((a,b)=>(b.precio_kg||0)-(a.precio_kg||0));
  else if(sort==="vol_asc")list.sort((a,b)=>(a.volumen_min||0)-(b.volumen_min||0));
  else if(sort==="reciente")list.sort((a,b)=>(b.id>a.id?1:-1));
  else list.sort((a,b)=>a.nombre.localeCompare(b.nombre));
  return list;
}

function renderProvKPIs(){
  const all=S.proveedores;
  const activos=all.filter(p=>p.estado==="activo");
  const conPrecio=all.filter(p=>p.precio_kg>0);
  const avgPrecio=conPrecio.length?Math.round(conPrecio.reduce((s,p)=>s+p.precio_kg,0)/conPrecio.length):0;
  const conVol=all.filter(p=>p.volumen_min>0);
  const avgVol=conVol.length?Math.round(conVol.reduce((s,p)=>s+p.volumen_min,0)/conVol.length):0;
  document.getElementById("kp-total").textContent=all.length;
  document.getElementById("kp-activos").textContent=activos.length;
  document.getElementById("kp-precio").textContent=avgPrecio?fCOP(avgPrecio):"—";
  document.getElementById("kp-vol").textContent=avgVol?(avgVol.toLocaleString("es-CO")+" kg"):"—";
}

function renderStars(r){return"⭐".repeat(parseInt(r)||0)+"☆".repeat(5-(parseInt(r)||0));}

// ── CALIFICACIÓN AUTOMÁTICA PROVEEDORES ──────────────────────────────────────
// Criterios (cada uno vale hasta 1 estrella):
// 1. Precio competitivo vs promedio del catálogo
// 2. Tiempo de entrega (≤2 días = perfecto)
// 3. Volumen disponible (≥5000 kg = alto)
// 4. Tiene certificación (ISO, RUC, etc.)
// 5. Estado activo
function calcRatingProv(p){
  let score=0;
  // 1. Precio: comparar con promedio de proveedores activos
  const precios=S.proveedores.filter(x=>x.precio_kg>0&&x.id!==p.id).map(x=>x.precio_kg);
  const avg=precios.length?precios.reduce((a,b)=>a+b,0)/precios.length:p.precio_kg||2000;
  const precio=parseFloat(p.precio_kg)||avg;
  if(precio<=avg*0.85)score+=1;       // muy competitivo
  else if(precio<=avg*1.05)score+=0.6;// dentro del promedio
  else score+=0.2;                     // caro
  // 2. Entrega rápida
  const ent=parseInt(p.entrega)||7;
  if(ent<=1)score+=1;
  else if(ent<=3)score+=0.8;
  else if(ent<=5)score+=0.5;
  else score+=0.1;
  // 3. Volumen máximo disponible
  const vol=parseInt(p.volumen_max)||0;
  if(vol>=10000)score+=1;
  else if(vol>=5000)score+=0.7;
  else if(vol>=2000)score+=0.4;
  else score+=0.1;
  // 4. Certificación
  score += (p.cert&&p.cert.trim().length>0)?1:0;
  // 5. Estado activo
  score += (p.estado==="activo")?1:(p.estado==="potencial"?0.5:0);
  return Math.min(5,Math.max(1,Math.round(score)));
}

// ── CALIFICACIÓN AUTOMÁTICA CLIENTES ────────────────────────────────────────
// Criterios (cada uno vale hasta 1 estrella):
// 1. Volumen de compra mensual (≥1000 und = excelente)
// 2. Frecuencia de compra (semanal = perfecto)
// 3. Puntualidad de pago (escala 1-5 → directa)
// 4. Antigüedad (≥12 meses = consolidado)
// 5. Número de cotizaciones realizadas (≥5 = cliente comprometido)
function calcRatingCli(c){
  let score=0;
  // 1. Volumen
  const vol=parseInt(c.volumen)||0;
  if(vol>=1000)score+=1;
  else if(vol>=500)score+=0.7;
  else if(vol>=100)score+=0.4;
  else score+=0.1;
  // 2. Frecuencia (1-5 directa → normalizada a 0-1)
  score += ((parseInt(c.frecuencia)||3)-1)/4;
  // 3. Puntualidad pago (1-5 → normalizada)
  score += ((parseInt(c.puntualidad_pago)||3)-1)/4;
  // 4. Antigüedad
  const ant=parseInt(c.antiguedad)||0;
  if(ant>=24)score+=1;
  else if(ant>=12)score+=0.7;
  else if(ant>=6)score+=0.4;
  else if(ant>=1)score+=0.2;
  else score+=0;
  // 5. Cotizaciones
  const nc=parseInt(c.n_cotizaciones)||0;
  if(nc>=10)score+=1;
  else if(nc>=5)score+=0.7;
  else if(nc>=2)score+=0.4;
  else if(nc>=1)score+=0.2;
  return Math.min(5,Math.max(1,Math.round(score)));
}

function renderProveedores(){
  renderProvKPIs();
  const list=getFilteredProveedores();
  const grid=document.getElementById("prov-grid");
  const label=document.getElementById("prov-count-label");
  if(label)label.textContent=`Mostrando ${list.length} de ${S.proveedores.length} proveedores`;
  if(!list.length){
    grid.innerHTML='<div style="grid-column:1/-1;"><div class="empty"><div class="ei">🏭</div><p>Sin proveedores que coincidan con los filtros</p></div></div>';
    return;
  }
  grid.innerHTML=list.map(p=>{
    const ahorro=p.precio_neg&&p.precio_kg?(p.precio_kg-p.precio_neg):0;
    const matsLabel=[p.material,p.mats_extra].filter(Boolean).join(", ");
    return`<div class="cli-card" style="border-top:3px solid var(--blue);">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">
        <div>
          <div class="cli-n">🏭 ${p.nombre}</div>
          <div class="cli-s">📍 ${p.ciudad||"—"}, Colombia</div>
        </div>
        <div style="text-align:right;">
          <span class="cbdg cbdg-${p.estado==="activo"?"a":p.estado==="potencial"?"p":"i"}" style="font-size:10px;">${p.estado.charAt(0).toUpperCase()+p.estado.slice(1)}</span>
          ${p.rating?`<div style="font-size:11px;margin-top:4px;">${renderStars(p.rating)}</div>`:""}
        </div>
      </div>
      <div class="cli-bdg" style="margin-top:8px;">
        ${matsLabel?`<span class="cbdg" style="background:rgba(88,166,255,.1);border:1px solid rgba(88,166,255,.3);color:var(--blue);">♻️ ${matsLabel}</span>`:""}
        ${p.cert?`<span class="cbdg" style="background:rgba(0,255,136,.08);border:1px solid rgba(0,255,136,.2);color:var(--acc);">✔️ ${p.cert}</span>`:""}
        ${p.pago?`<span class="cbdg" style="background:rgba(255,149,0,.1);border:1px solid rgba(255,149,0,.3);color:var(--orange);">💳 ${p.pago}</span>`:""}
      </div>
      <div class="cli-info" style="margin-top:12px;">
        <div><div class="cli-il">Precio / kg</div><div class="cli-iv" style="color:var(--acc);">💰 ${p.precio_kg?fCOP(p.precio_kg):"—"}</div></div>
        <div><div class="cli-il">Precio neg.</div><div class="cli-iv" style="color:${p.precio_neg?"#69F0AE":"var(--t3)"};">${p.precio_neg?fCOP(p.precio_neg)+"  ✅":"—"}</div></div>
        <div><div class="cli-il">Vol. mínimo</div><div class="cli-iv">📦 ${p.volumen_min?(p.volumen_min.toLocaleString("es-CO")+" kg"):"—"}</div></div>
        <div><div class="cli-il">Vol. máx. mes</div><div class="cli-iv">${p.volumen_max?(p.volumen_max.toLocaleString("es-CO")+" kg"):"—"}</div></div>
        <div><div class="cli-il">Entrega</div><div class="cli-iv">🚚 ${p.entrega?(p.entrega+" días hábiles"):"—"}</div></div>
        <div><div class="cli-il">Contacto</div><div class="cli-iv" style="font-size:11px;">${p.contacto||"—"}</div></div>
      </div>
      ${ahorro>0?`<div style="margin-top:10px;background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.3);border-radius:var(--rs);padding:8px 12px;font-size:12px;color:var(--acc);">💡 Ahorro negociado: ${fCOP(ahorro)}/kg vs precio base</div>`:""}
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
        ${p.tel?`<a href="tel:${p.tel}" style="text-decoration:none;"><button class="btn btn-s btn-sm">📞 ${p.tel}</button></a>`:""}
        ${p.email?`<a href="mailto:${p.email}" style="text-decoration:none;"><button class="btn btn-s btn-sm">✉️ Email</button></a>`:""}
      </div>
      ${p.notas?`<div style="margin-top:10px;font-size:11px;color:var(--t3);border-top:1px solid var(--border);padding-top:8px;">📝 ${p.notas}</div>`:""}
      <div class="cli-act">
        <button class="btn btn-b btn-sm" onclick="editProv('${p.id}')">✏️ Editar</button>
        <button class="btn btn-g btn-sm" onclick="contactarProv('${p.id}')">📋 Contactar</button>
        <button class="btn btn-d btn-sm" onclick="delProv('${p.id}')">✕</button>
      </div>
    </div>`;
  }).join("");
  if(_provViewActive)renderProvCharts();
}

function toggleProvView(){
  _provViewActive=!_provViewActive;
  const panel=document.getElementById("prov-analysis-panel");
  const btn=document.getElementById("btn-prov-view");
  panel.style.display=_provViewActive?"block":"none";
  btn.textContent=_provViewActive?"📋 Ver Tarjetas":"📊 Ver Análisis";
  if(_provViewActive)renderProvCharts();
}

function renderProvCharts(){
  if(_provCharts.precios){_provCharts.precios.destroy();_provCharts.precios=null;}
  if(_provCharts.ciudades){_provCharts.ciudades.destroy();_provCharts.ciudades=null;}

  // Agrupar por material — precio promedio
  const byMat={};
  S.proveedores.filter(p=>p.material&&p.precio_kg>0).forEach(p=>{
    if(!byMat[p.material])byMat[p.material]={sum:0,n:0,min:p.precio_kg,max:p.precio_kg};
    byMat[p.material].sum+=p.precio_kg;byMat[p.material].n++;
    byMat[p.material].min=Math.min(byMat[p.material].min,p.precio_kg);
    byMat[p.material].max=Math.max(byMat[p.material].max,p.precio_kg);
  });
  const matLabels=Object.keys(byMat);
  const matAvg=matLabels.map(m=>Math.round(byMat[m].sum/byMat[m].n));
  const matMin=matLabels.map(m=>byMat[m].min);
  const matColors=["#4FC3F7","#66BB6A","#FFA726","#AB47BC","#26C6DA","#EF5350","#FF7043","#CE93D8","#F06292"];
  const cd={plugins:{legend:{labels:{color:"#8B949E",font:{family:"Space Grotesk",size:11}}}},responsive:true,maintainAspectRatio:false};

  const ctxP=document.getElementById("chart-prov-precios");
  if(ctxP&&matLabels.length){
    _provCharts.precios=new Chart(ctxP,{type:"bar",data:{labels:matLabels,datasets:[
      {label:"Precio promedio (COP/kg)",data:matAvg,backgroundColor:matColors.slice(0,matLabels.length).map(c=>c+"BB"),borderColor:matColors.slice(0,matLabels.length),borderWidth:1,borderRadius:6},
      {label:"Precio mínimo",data:matMin,backgroundColor:"rgba(0,255,136,.3)",borderColor:"#00FF88",borderWidth:1,borderRadius:6,type:"bar"}
    ]},options:{...cd,scales:{x:{grid:{color:"#30363D"},ticks:{color:"#8B949E"}},y:{grid:{color:"#30363D"},ticks:{color:"#8B949E",callback:v=>"$"+Math.round(v).toLocaleString("es-CO")}}}}});
  }

  // Ciudades
  const byCity={};
  S.proveedores.forEach(p=>{const c=p.ciudad||"Otra";byCity[c]=(byCity[c]||0)+1;});
  const cityLabels=Object.keys(byCity);
  const cityVals=cityLabels.map(c=>byCity[c]);
  const ctxC=document.getElementById("chart-prov-ciudades");
  if(ctxC&&cityLabels.length){
    _provCharts.ciudades=new Chart(ctxC,{type:"doughnut",data:{labels:cityLabels,datasets:[{data:cityVals,backgroundColor:["#00FF88","#58A6FF","#FF9500","#BD93F9","#FF4444","#FFCC00","#4FC3F7"],borderWidth:0}]},options:{...cd,cutout:"60%"}});
  }

  // Comparador tabla mejor precio por material
  const tbl=document.getElementById("prov-comparador-table");
  if(tbl){
    const rows=Object.keys(byMat).sort().map(mat=>{
      const provs=S.proveedores.filter(p=>p.material===mat&&p.precio_kg>0).sort((a,b)=>a.precio_kg-b.precio_kg);
      const mejor=provs[0];
      return mejor?`<tr>
        <td style="font-weight:700;color:var(--blue);">♻️ ${mat}</td>
        <td style="font-weight:600;">${mejor.nombre}</td>
        <td style="color:var(--t3);font-size:12px;">📍 ${mejor.ciudad||"—"}</td>
        <td class="mono" style="color:var(--acc);">${fCOP(mejor.precio_kg)}/kg</td>
        <td class="mono">${mejor.volumen_min?(mejor.volumen_min.toLocaleString("es-CO")+" kg"):"—"}</td>
        <td style="font-size:11px;color:var(--t3);">${mejor.pago||"—"}</td>
        <td>${renderStars(mejor.rating)}</td>
      </tr>`:""}).join("");
    tbl.innerHTML=`<div style="overflow-x:auto;"><table class="ctbl">
      <thead><tr><th>Material</th><th>Mejor Proveedor</th><th>Ciudad</th><th>Precio/kg</th><th>Vol. Mín.</th><th>Pago</th><th>Rating</th></tr></thead>
      <tbody>${rows||'<tr><td colspan="7" style="text-align:center;color:var(--t3);padding:20px;">Sin datos suficientes</td></tr>'}</tbody>
    </table></div>`;
  }
}

function contactarProv(id){
  const p=S.proveedores.find(x=>x.id===id);if(!p)return;
  const lineas=[`Proveedor: ${p.nombre}`,`Ciudad: ${p.ciudad||"—"}`,`Material: ${p.material||"—"}`,`Precio/kg: ${p.precio_kg?fCOP(p.precio_kg):"—"}`,`Tel: ${p.tel||"—"}`,`Email: ${p.email||"—"}`,`Contacto: ${p.contacto||"—"}`].join("\n");
  alert("📋 Datos de contacto:\n\n"+lineas);
}

async function exportarCliExcel(){
  const clis = S.clientes;
  if(!clis || !clis.length){ toast("No hay clientes para exportar","info"); return; }
  toast("Generando Excel de clientes...","info");
  try{
    const r = await fetch("/exportar/clientes_excel", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({clientes: clis})
    });
    if(!r.ok){ const e=await r.json(); toast(e.error||"Error al exportar","error"); return; }
    const blob = await r.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `NovaPLAST_Clientes_${new Date().toISOString().slice(0,10)}.xlsx`;
    a.click();
    toast("Excel de clientes descargado ✅");
  } catch(e){ toast("Error: "+e.message,"error"); }
}

async function exportarProvExcel(){
  const provs = S.proveedores;
  if(!provs || !provs.length){ toast("No hay proveedores para exportar","info"); return; }
  toast("Generando Excel de proveedores...","info");
  try{
    const r = await fetch("/exportar/proveedores_excel", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({proveedores: provs})
    });
    if(!r.ok){ const e=await r.json(); toast(e.error||"Error al exportar","error"); return; }
    const blob = await r.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `NovaPLAST_Proveedores_${new Date().toISOString().slice(0,10)}.xlsx`;
    a.click();
    toast("Excel de proveedores descargado ✅");
  } catch(e){ toast("Error: "+e.message,"error"); }
}

function abrirModalProv(){
  _editProvId=null;document.getElementById("modal-prov-ttl").textContent="➕ Nuevo Proveedor";
  ["prov-nom","prov-ciu","prov-tel","prov-em","prov-contacto","prov-mats-extra","prov-precio","prov-precio-neg","prov-vol","prov-vol-max","prov-entrega","prov-cert","prov-not"].forEach(id=>{const el=document.getElementById(id);if(el)el.value="";});
  document.getElementById("prov-mat").value="";document.getElementById("prov-est").value="activo";
  document.getElementById("prov-rating").value="3";
  document.getElementById("prov-rating-preview").value="Se calcula al guardar";
  document.getElementById("prov-pago").value="";
  document.getElementById("modal-prov").classList.add("show");
}
function editProv(id){
  const p=S.proveedores.find(x=>x.id===id);if(!p)return;
  _editProvId=id;document.getElementById("modal-prov-ttl").textContent="✏️ Editar Proveedor";
  document.getElementById("prov-nom").value=p.nombre;document.getElementById("prov-ciu").value=p.ciudad||"";
  document.getElementById("prov-tel").value=p.tel||"";document.getElementById("prov-em").value=p.email||"";
  document.getElementById("prov-contacto").value=p.contacto||"";document.getElementById("prov-mats-extra").value=p.mats_extra||"";
  document.getElementById("prov-mat").value=p.material||"";document.getElementById("prov-precio").value=p.precio_kg||"";
  document.getElementById("prov-precio-neg").value=p.precio_neg||"";document.getElementById("prov-vol").value=p.volumen_min||"";
  document.getElementById("prov-vol-max").value=p.volumen_max||"";document.getElementById("prov-est").value=p.estado||"activo";
  document.getElementById("prov-entrega").value=p.entrega||"";
  document.getElementById("prov-rating").value=p.rating||"3";
  const pr=parseInt(p.rating)||0;
  document.getElementById("prov-rating-preview").value=pr?("⭐".repeat(pr)+"☆".repeat(5-pr)+" ("+pr+"/5)"):"Se calcula al guardar";
  document.getElementById("prov-cert").value=p.cert||"";document.getElementById("prov-pago").value=p.pago||"";
  document.getElementById("prov-not").value=p.notas||"";
  document.getElementById("modal-prov").classList.add("show");
}
function guardarProveedor(){
  const nom=document.getElementById("prov-nom").value.trim();
  if(!nom){toast("El nombre es obligatorio","error");return;}
  const nuevo={
    id:_editProvId||"p_"+Date.now(),nombre:nom,
    ciudad:document.getElementById("prov-ciu").value,tel:document.getElementById("prov-tel").value,
    email:document.getElementById("prov-em").value,contacto:document.getElementById("prov-contacto").value,
    material:document.getElementById("prov-mat").value,mats_extra:document.getElementById("prov-mats-extra").value,
    precio_kg:parseFloat(document.getElementById("prov-precio").value)||0,
    precio_neg:parseFloat(document.getElementById("prov-precio-neg").value)||0,
    volumen_min:parseInt(document.getElementById("prov-vol").value)||0,
    volumen_max:parseInt(document.getElementById("prov-vol-max").value)||0,
    estado:document.getElementById("prov-est").value,
    entrega:parseInt(document.getElementById("prov-entrega").value)||0,
    rating:3, // se recalcula abajo
    cert:document.getElementById("prov-cert").value,
    pago:document.getElementById("prov-pago").value,
    notas:document.getElementById("prov-not").value
  };
  nuevo.rating = calcRatingProv(nuevo);
  document.getElementById("prov-rating-preview").value="⭐".repeat(nuevo.rating)+"☆".repeat(5-nuevo.rating)+" ("+nuevo.rating+"/5)";
  if(_editProvId){S.proveedores=S.proveedores.map(p=>p.id===_editProvId?nuevo:p);toast("Proveedor actualizado ✅");}
  else{S.proveedores.unshift(nuevo);toast("Proveedor agregado ✅");}
  saveS();cerrarModalProv();renderProveedores();
}
function delProv(id){if(!confirm("¿Eliminar este proveedor?"))return;S.proveedores=S.proveedores.filter(p=>p.id!==id);saveS();toast("Proveedor eliminado","info");renderProveedores();}
function cerrarModalProv(){document.getElementById("modal-prov").classList.remove("show");}

// ─── EXPORTAR ────────────────────────────────────────────────
async function exportarExcel(){
  if(!S.lastAnalisis){toast("Ejecuta un análisis primero","info");return;}
  try{
    const r=await fetch("/exportar/excel",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(S.lastAnalisis)});
    if(!r.ok){const e=await r.json();toast(e.error||"Error al exportar","error");return;}
    const blob=await r.blob();const url=URL.createObjectURL(blob);
    const a=document.createElement("a");a.href=url;a.download=`NovaPLAST_${S.lastAnalisis.material.nombre}_${Date.now()}.xlsx`;a.click();
    toast("Excel descargado ✅");
  }catch(e){toast("Error: "+e.message,"error");}
}
async function exportarPDF(){
  if(!S.lastAnalisis){toast("Ejecuta un análisis primero","info");return;}
  try{
    const r=await fetch("/exportar/pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(S.lastAnalisis)});
    if(!r.ok){const e=await r.json();toast(e.error||"Error al exportar","error");return;}
    const blob=await r.blob();const url=URL.createObjectURL(blob);
    const a=document.createElement("a");a.href=url;a.download=`NovaPLAST_${S.lastAnalisis.material.nombre}_${Date.now()}.pdf`;a.click();
    toast("PDF descargado ✅");
  }catch(e){toast("Error: "+e.message,"error");}
}

// ─── BOOT ────────────────────────────────────────────────────
init();

// ─── RIPPLE SUTIL AL CLIC ────────────────────────────────────
document.addEventListener('click', function(e){
  const size = 120;
  const r = document.createElement('div');
  r.className = 'ripple';
  r.style.cssText =
    'width:' + size + 'px;' +
    'height:' + size + 'px;' +
    'left:' + (e.clientX - size/2) + 'px;' +
    'top:' + (e.clientY - size/2) + 'px;';
  document.body.appendChild(r);
  setTimeout(function(){ r.remove(); }, 600);
});

// ─── CERRAR SESIÓN ────────────────────────────────────────────
function cerrarSesion(){
  if(confirm("¿Cerrar sesión y volver al login?")){
    window.location.href="/logout";
  }
}

// ─── APAGAR SISTEMA ───────────────────────────────────────────
async function apagarSistema(){
  if(!confirm("¿Deseas cerrar completamente el sistema? La aplicación se detendrá.")){return;}
  try{
    await fetch("/shutdown",{method:"POST"});
    document.body.innerHTML='<div style="font-family:monospace;background:#060A0F;color:#00FF88;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;"><div style=\'font-size:48px\'>🌴</div><div style=\'font-size:20px;font-weight:700\'>Sistema detenido</div><div style=\'color:#8B949E;font-size:13px\'>Puedes cerrar esta ventana.</div></div>';
  }catch(e){alert("Sistema detenido. Cierra esta ventana.");}
}

// ─── PARTÍCULAS WEBGL ─────────────────────────────────────────
(function(){
  const canvas = document.getElementById("particles-canvas");
  if(!canvas) return;
  const gl = canvas.getContext("webgl",{alpha:true,antialias:false});
  if(!gl) return;

  const vSrc=`
    attribute vec3 position;
    attribute vec4 random;
    attribute vec3 color;
    uniform mat4 modelMatrix;
    uniform mat4 viewMatrix;
    uniform mat4 projectionMatrix;
    uniform float uTime;
    uniform float uSpread;
    uniform float uBaseSize;
    varying vec4 vRandom;
    varying vec3 vColor;
    void main(){
      vRandom=random;vColor=color;
      vec3 pos=position*uSpread;pos.z*=10.0;
      vec4 mPos=modelMatrix*vec4(pos,1.0);
      float t=uTime;
      mPos.x+=sin(t*random.z+6.28*random.w)*mix(0.1,1.5,random.x);
      mPos.y+=sin(t*random.y+6.28*random.x)*mix(0.1,1.5,random.w);
      mPos.z+=sin(t*random.w+6.28*random.y)*mix(0.1,1.5,random.z);
      vec4 mvPos=viewMatrix*mPos;
      gl_PointSize=uBaseSize/length(mvPos.xyz);
      gl_Position=projectionMatrix*mvPos;
    }`;
  const fSrc=`
    precision highp float;
    uniform float uTime;
    varying vec4 vRandom;
    varying vec3 vColor;
    void main(){
      vec2 uv=gl_PointCoord.xy;
      float d=length(uv-vec2(0.5));
      if(d>0.5)discard;
      gl_FragColor=vec4(vColor+0.2*sin(uv.yxx+uTime+vRandom.y*6.28),1.0);
    }`;

  function mkShader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);return s;}
  const prog=gl.createProgram();
  gl.attachShader(prog,mkShader(gl.VERTEX_SHADER,vSrc));
  gl.attachShader(prog,mkShader(gl.FRAGMENT_SHADER,fSrc));
  gl.linkProgram(prog);gl.useProgram(prog);

  const count=200;
  const positions=new Float32Array(count*3);
  const randoms=new Float32Array(count*4);
  const colors=new Float32Array(count*3);
  for(let i=0;i<count;i++){
    let x,y,z,len;
    do{x=Math.random()*2-1;y=Math.random()*2-1;z=Math.random()*2-1;len=x*x+y*y+z*z;}while(len>1||len===0);
    const r=Math.cbrt(Math.random());
    positions.set([x*r,y*r,z*r],i*3);
    randoms.set([Math.random(),Math.random(),Math.random(),Math.random()],i*4);
    colors.set([1,1,1],i*3);
  }

  function mkBuf(data,attr,size){
    const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);
    gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);
    const loc=gl.getAttribLocation(prog,attr);
    gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,0,0);
  }
  mkBuf(positions,"position",3);
  mkBuf(randoms,"random",4);
  mkBuf(colors,"color",3);

  const uTime=gl.getUniformLocation(prog,"uTime");
  const uSpread=gl.getUniformLocation(prog,"uSpread");
  const uBase=gl.getUniformLocation(prog,"uBaseSize");
  const uMod=gl.getUniformLocation(prog,"modelMatrix");
  const uView=gl.getUniformLocation(prog,"viewMatrix");
  const uProj=gl.getUniformLocation(prog,"projectionMatrix");

  function mat4(){return new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);}
  function perspective(fov,aspect,near,far){
    const f=1/Math.tan(fov/2),nf=1/(near-far);
    const m=mat4();m[0]=f/aspect;m[5]=f;m[10]=(far+near)*nf;m[11]=-1;m[14]=2*far*near*nf;m[15]=0;return m;
  }
  function lookAt(eye){
    const m=mat4();m[14]=-eye;return m;
  }
  function rotY(a){const c=Math.cos(a),s=Math.sin(a),m=mat4();m[0]=c;m[2]=s;m[8]=-s;m[10]=c;return m;}

  function resize(){
    canvas.width=canvas.clientWidth;canvas.height=canvas.clientHeight;
    gl.viewport(0,0,canvas.width,canvas.height);
  }
  window.addEventListener("resize",resize);resize();

  gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  gl.uniform1f(uSpread,10);gl.uniform1f(uBase,60);

  const t0=performance.now();let rot=0;
  function loop(now){
    requestAnimationFrame(loop);
    resize();
    gl.clear(gl.COLOR_BUFFER_BIT);
    const t=(now-t0)*0.001;
    rot+=0.0005;
    const aspect=canvas.width/Math.max(canvas.height,1);
    gl.uniformMatrix4fv(uMod,false,rotY(rot));
    gl.uniformMatrix4fv(uView,false,lookAt(20));
    gl.uniformMatrix4fv(uProj,false,perspective(0.26,aspect,0.1,100));
    gl.uniform1f(uTime,t*0.1);
    gl.drawArrays(gl.POINTS,0,count);
  }
  requestAnimationFrame(loop);
})();
</script>
</body>
</html>"""


# ─── RUTAS DE AUTENTICACIÓN ───────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        if username == ADMIN_USER and pass_hash == ADMIN_PASS_HASH:
            session["logged_in"] = True
            session["user"] = username
            return redirect(url_for("index"))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template_string(LOGIN_HTML, error=error, year=datetime.now().year)

@app.route("/logout")
def logout():
    session.clear()
    return render_template_string(LOGOUT_HTML, year=datetime.now().year)

@app.route("/shutdown", methods=["POST"])
@login_required
def shutdown():
    import threading, signal
    def stop():
        import time; time.sleep(0.5)
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=stop, daemon=True).start()
    return jsonify({"ok": True})

@app.route("/")
@login_required
def index():
    return HTML


@app.route("/exportar/excel", methods=["POST"])
@login_required
def exportar_excel():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from openpyxl.chart import BarChart, Reference, PieChart
        from openpyxl.chart.series import SeriesLabel

        data = request.get_json()
        if not data:
            return jsonify({"error": "Sin datos"}), 400

        d = data
        c = d["costos"]
        e = d["economia"]
        ivc = d["ivc"]
        mat = d["material"]
        app_data = d["aplicacion"]
        proveedores = d.get("proveedores", [])
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        wb = Workbook()
        ws = wb.active
        ws.title = "Análisis NovaPLAST"

        verde_oscuro = "00662B"
        gris_header  = "2D2D2D"
        verde_claro  = "E6F4EA"
        blanco       = "FFFFFF"
        azul         = "1565C0"

        h1 = Font(name="Calibri", bold=True, size=16, color=blanco)
        h2 = Font(name="Calibri", bold=True, size=11, color=blanco)
        bold_green = Font(name="Calibri", bold=True, color=verde_oscuro, size=11)
        normal = Font(name="Calibri", size=10)
        bold = Font(name="Calibri", bold=True, size=10)

        fill_header  = PatternFill("solid", fgColor=verde_oscuro)
        fill_section = PatternFill("solid", fgColor=gris_header)
        fill_total   = PatternFill("solid", fgColor=verde_claro)
        fill_azul    = PatternFill("solid", fgColor="DBEAFE")

        thin = Side(style="thin", color="CCCCCC")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        center = Alignment(horizontal="center", vertical="center")
        left   = Alignment(horizontal="left",   vertical="center", indent=1)

        ws.merge_cells("A1:F1")
        ws["A1"] = "🌴 NovaPLAST CTG — Análisis de Residuo Plástico"
        ws["A1"].font = h1
        ws["A1"].fill = fill_header
        ws["A1"].alignment = center
        ws.row_dimensions[1].height = 36

        ws.merge_cells("A2:F2")
        ws["A2"] = f"Generado el {fecha}  ·  Cartagena de Indias, Colombia"
        ws["A2"].font = Font(name="Calibri", italic=True, color="888888", size=9)
        ws["A2"].alignment = center
        ws.row_dimensions[2].height = 18

        row = 4

        def section_header(title, r, cols="A:F"):
            c1, c2 = cols.split(":")
            ws.merge_cells(f"{c1}{r}:{c2}{r}")
            ws[f"{c1}{r}"] = title
            ws[f"{c1}{r}"].font = Font(name="Calibri", bold=True, size=11, color=blanco)
            ws[f"{c1}{r}"].fill = fill_section
            ws[f"{c1}{r}"].alignment = left
            ws.row_dimensions[r].height = 22
            return r + 1

        def data_row(label, value, r, highlight=False, cols="ABCDEF"):
            ws[f"A{r}"] = label
            ws[f"A{r}"].font = bold if highlight else normal
            ws[f"A{r}"].alignment = left
            ws.merge_cells(f"B{r}:F{r}")
            ws[f"B{r}"] = value
            ws[f"B{r}"].font = bold_green if highlight else normal
            ws[f"B{r}"].alignment = left
            if highlight:
                for col in "ABCDEF":
                    ws[f"{col}{r}"].fill = fill_total
            for col in "ABCDEF":
                ws[f"{col}{r}"].border = border
            ws.row_dimensions[r].height = 18
            return r + 1

        row = section_header("📋 INFORMACIÓN GENERAL", row)
        row = data_row("Material", f"{mat['nombre']} — {mat['nombre_completo']}", row)
        row = data_row("Código de reciclaje", f"#{mat['codigo_reciclaje']}", row)
        row = data_row("Aplicación / Producto", app_data["producto"], row)
        row = data_row("Mercado objetivo", app_data["mercado"], row)
        row = data_row("Cantidad a procesar", f"{d['cantidad_kg']} kg", row)
        row = data_row("Viabilidad", f"{app_data['viabilidad']}%", row)
        row += 1

        # ── Datos de costos para gráfica ──
        cost_start_row = row + 1  # después del header
        row = section_header("💰 DESGLOSE DE COSTOS (COP por unidad)", row)
        cost_labels = [
            ("Materia prima",      c["materia_prima"]),
            ("Lavado y pretrat.",  c["lavado"]),
            ("Triturado",          c["triturado"]),
            ("Peletizado",         c["peletizado"]),
            ("Mano de obra",       c["mano_obra"]),
            ("Energía eléctrica",  c["energia"]),
            ("Overhead (22%)",     c["overhead"]),
        ]
        cost_data_start = row
        for label, val in cost_labels:
            row = data_row(label, f_cop(val), row)
        cost_data_end = row - 1

        row = data_row("COSTO TOTAL", f_cop(c["total"]), row, highlight=True)
        row = data_row(f"PRECIO DE VENTA ({e['margen_porcentaje']:.0f}% margen)", f_cop(e["precio_venta"]), row, highlight=True)
        row = data_row("GANANCIA NETA", f_cop(e["ganancia"]), row, highlight=True)
        row = data_row("ROI", f"{e['roi']:.1f}%", row, highlight=True)
        row += 1

        row = section_header("🔄 ÍNDICE DE VIABILIDAD CIRCULAR (IVC)", row)
        ivc_data_start = row
        row = data_row("IVC Total", f"{ivc['ivc']} / 100", row, highlight=True)
        row = data_row("Clasificación", ivc["clasificacion"], row)
        row = data_row("Recomendación", ivc["recomendacion"], row)
        ivc_factors_start = row
        row = data_row("Factor Técnico",   str(ivc["factores"]["tecnico"]),   row)
        row = data_row("Factor Material",  str(ivc["factores"]["material"]),  row)
        row = data_row("Factor Económico", str(ivc["factores"]["economico"]), row)
        row = data_row("Factor de Escala", str(ivc["factores"]["escala"]),    row)
        ivc_factors_end = row - 1
        row += 1

        props = mat.get("propiedades", {})
        row = section_header("🧪 PROPIEDADES DEL MATERIAL", row)
        row = data_row("Densidad", props.get("densidad","—"), row)
        row = data_row("Temperatura de fusión", props.get("temp_fusion","—"), row)
        row = data_row("Resistencia química", props.get("resistencia_quimica","—"), row)
        row = data_row("Transparencia", props.get("transparencia","—"), row)
        row = data_row("Reciclabilidad", f"{props.get('reciclabilidad',0)}%", row)
        row += 1

        if proveedores:
            row = section_header("🤝 PROVEEDORES", row)
            headers = ["Proveedor", "Ciudad", "Precio/kg (COP)", "Vol. Mínimo (kg)", "Contacto"]
            for i, h in enumerate(headers, 1):
                cell = ws.cell(row=row, column=i, value=h)
                cell.font = Font(name="Calibri", bold=True, size=10, color=blanco)
                cell.fill = PatternFill("solid", fgColor="444444")
                cell.alignment = center
                cell.border = border
            ws.row_dimensions[row].height = 20
            row += 1
            for p in proveedores:
                vals = [p["nombre"], p["ciudad"], f_cop(p["precio_compra"]),
                        f"{p['volumen_min_kg']:,} kg".replace(",","."), p["contacto"]]
                for i, v in enumerate(vals, 1):
                    cell = ws.cell(row=row, column=i, value=v)
                    cell.font = normal
                    cell.alignment = left
                    cell.border = border
                ws.row_dimensions[row].height = 18
                row += 1

        footer_row = row + 1
        ws.merge_cells(f"A{footer_row}:F{footer_row}")
        ws[f"A{footer_row}"] = f"© {datetime.now().year} NovaPLAST CTG · Cartagena de Indias, Colombia"
        ws[f"A{footer_row}"].font = Font(name="Calibri", italic=True, color="AAAAAA", size=9)
        ws[f"A{footer_row}"].alignment = center

        for i, w in enumerate([38, 10, 20, 18, 28, 12], 1):
            ws.column_dimensions[get_column_letter(i)].width = w

        # ══════════════════════════════════════════════════════════
        # HOJA 2: Gráficas de análisis
        # ══════════════════════════════════════════════════════════
        ws2 = wb.create_sheet("Gráficas de Análisis")

        ws2["A1"] = "🌴 NovaPLAST CTG — Gráficas de Análisis"
        ws2["A1"].font = Font(name="Calibri", bold=True, size=14, color="FFFFFF")
        ws2["A1"].fill = PatternFill("solid", fgColor="00662B")
        ws2.merge_cells("A1:J1")
        ws2["A1"].alignment = Alignment(horizontal="center")
        ws2.row_dimensions[1].height = 30

        # ── Datos auxiliares para gráficas en ws2 ──
        # Tabla de costos numérica (para BarChart)
        ws2["A3"] = "Concepto de Costo"
        ws2["B3"] = "Valor (COP)"
        ws2["A3"].font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws2["A3"].fill = PatternFill("solid", fgColor="2D2D2D")
        ws2["B3"].font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws2["B3"].fill = PatternFill("solid", fgColor="2D2D2D")
        ws2.column_dimensions["A"].width = 26
        ws2.column_dimensions["B"].width = 16

        cost_chart_data = [
            ("Materia prima",     c["materia_prima"]),
            ("Lavado",            c["lavado"]),
            ("Triturado",         c["triturado"]),
            ("Peletizado",        c["peletizado"]),
            ("Mano de obra",      c["mano_obra"]),
            ("Energía",           c["energia"]),
            ("Overhead",          c["overhead"]),
        ]
        for i, (lbl, val) in enumerate(cost_chart_data, start=4):
            ws2.cell(row=i, column=1, value=lbl).font = Font(name="Calibri", size=10)
            ws2.cell(row=i, column=2, value=round(val)).font = Font(name="Calibri", size=10)

        # BarChart — Costos
        bar1 = BarChart()
        bar1.type = "bar"
        bar1.grouping = "clustered"
        bar1.title = "Desglose de Costos de Producción"
        bar1.y_axis.title = "COP $"
        bar1.x_axis.title = "Concepto"
        bar1.style = 10
        bar1.width = 18
        bar1.height = 12
        data_ref = Reference(ws2, min_col=2, min_row=3, max_row=3+len(cost_chart_data))
        cats_ref = Reference(ws2, min_col=1, min_row=4, max_row=3+len(cost_chart_data))
        bar1.add_data(data_ref, titles_from_data=True)
        bar1.set_categories(cats_ref)
        bar1.series[0].graphicalProperties.solidFill = "00882B"
        ws2.add_chart(bar1, "D3")

        # Tabla comparativa Costo / Venta / Ganancia
        econ_row = 4 + len(cost_chart_data) + 2
        ws2.cell(row=econ_row, column=1, value="Métricas Económicas").font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws2.cell(row=econ_row, column=1).fill = PatternFill("solid", fgColor="1565C0")
        ws2.cell(row=econ_row, column=2, value="Valor (COP)").font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws2.cell(row=econ_row, column=2).fill = PatternFill("solid", fgColor="1565C0")
        econ_data = [
            ("Costo Total",     round(c["total"])),
            ("Precio de Venta", round(e["precio_venta"])),
            ("Ganancia Neta",   round(e["ganancia"])),
        ]
        for i, (lbl, val) in enumerate(econ_data, start=econ_row+1):
            ws2.cell(row=i, column=1, value=lbl).font = Font(name="Calibri", size=10)
            ws2.cell(row=i, column=2, value=val).font = Font(name="Calibri", size=10)

        bar2 = BarChart()
        bar2.type = "bar"
        bar2.title = "Costo vs Precio Venta vs Ganancia"
        bar2.y_axis.title = "COP $"
        bar2.style = 10
        bar2.width = 14
        bar2.height = 9
        econ_data_ref = Reference(ws2, min_col=2, min_row=econ_row, max_row=econ_row+len(econ_data))
        econ_cats_ref = Reference(ws2, min_col=1, min_row=econ_row+1, max_row=econ_row+len(econ_data))
        bar2.add_data(econ_data_ref, titles_from_data=True)
        bar2.set_categories(econ_cats_ref)
        bar2.series[0].graphicalProperties.solidFill = "1565C0"
        ws2.add_chart(bar2, "D" + str(econ_row))

        # Tabla IVC factores
        ivc_row = econ_row + len(econ_data) + 3
        ws2.cell(row=ivc_row, column=1, value="Factor IVC").font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws2.cell(row=ivc_row, column=1).fill = PatternFill("solid", fgColor="4A148C")
        ws2.cell(row=ivc_row, column=2, value="Puntuación (0-100)").font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws2.cell(row=ivc_row, column=2).fill = PatternFill("solid", fgColor="4A148C")
        ivc_data = [
            ("Técnico",   ivc["factores"]["tecnico"]),
            ("Material",  ivc["factores"]["material"]),
            ("Económico", ivc["factores"]["economico"]),
            ("Escala",    ivc["factores"]["escala"]),
        ]
        for i, (lbl, val) in enumerate(ivc_data, start=ivc_row+1):
            ws2.cell(row=i, column=1, value=lbl).font = Font(name="Calibri", size=10)
            ws2.cell(row=i, column=2, value=val).font = Font(name="Calibri", size=10)

        bar3 = BarChart()
        bar3.type = "bar"
        bar3.title = f"Factores IVC — Total: {ivc['ivc']}/100 ({ivc['clasificacion']})"
        bar3.y_axis.title = "Puntuación"
        bar3.y_axis.scaling.max = 100
        bar3.style = 10
        bar3.width = 14
        bar3.height = 9
        ivc_data_ref = Reference(ws2, min_col=2, min_row=ivc_row, max_row=ivc_row+len(ivc_data))
        ivc_cats_ref = Reference(ws2, min_col=1, min_row=ivc_row+1, max_row=ivc_row+len(ivc_data))
        bar3.add_data(ivc_data_ref, titles_from_data=True)
        bar3.set_categories(ivc_cats_ref)
        bar3.series[0].graphicalProperties.solidFill = "6A0DAD"
        ws2.add_chart(bar3, "D" + str(ivc_row))

        # ══════════════════════════════════════════════════════════
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        filename = f"NovaPLAST_{mat['nombre']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(buf, as_attachment=True, download_name=filename,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except ImportError:
        return jsonify({"error": "Instala openpyxl: pip install openpyxl"}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


@app.route("/exportar/pdf", methods=["POST"])
@login_required
def exportar_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
        from reportlab.graphics import renderPDF
        from reportlab.platypus import Image as RLImage
        import io as _io

        data = request.get_json()
        if not data:
            return jsonify({"error": "Sin datos"}), 400

        d = data
        c = d["costos"]
        e = d["economia"]
        ivc = d["ivc"]
        mat = d["material"]
        app_data = d["aplicacion"]
        proveedores = d.get("proveedores", [])
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        verde = colors.HexColor("#00662B")
        gris  = colors.HexColor("#2D2D2D")
        verde_claro = colors.HexColor("#E6F4EA")
        azul = colors.HexColor("#1565C0")

        style_title = ParagraphStyle("title", parent=styles["Title"], textColor=verde, fontSize=20, spaceAfter=4)
        style_sub = ParagraphStyle("sub", parent=styles["Normal"], textColor=colors.grey, fontSize=9, spaceAfter=16)
        style_section = ParagraphStyle("section", parent=styles["Heading2"], textColor=colors.white, fontSize=11,
                                       backColor=gris, spaceAfter=6, spaceBefore=12, leftIndent=6, borderPad=4)
        style_footer = ParagraphStyle("footer", parent=styles["Normal"], textColor=colors.grey, fontSize=8, alignment=TA_CENTER)
        style_chart_title = ParagraphStyle("ctitle", parent=styles["Normal"], textColor=gris, fontSize=10,
                                           fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=8)

        def tbl(rows, col_widths):
            t = Table(rows, colWidths=col_widths)
            t.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), gris),
                ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",  (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            return t

        # ── Helper: gráfica de pastel (pie chart) con reportlab Drawing ──
        def make_pie_chart(labels, values, colors_hex, title, width=430, height=200):
            """Genera una gráfica de pastel como Drawing de reportlab."""
            import math
            d = Drawing(width, height)
            total = sum(values)
            if total == 0:
                return d
            cx, cy, r = width * 0.38, height / 2, min(width * 0.30, height * 0.42)
            start = 0.0
            for i, (lbl, val, col) in enumerate(zip(labels, values, colors_hex)):
                frac = val / total
                angle = frac * 2 * math.pi
                end = start + angle
                steps = max(4, int(frac * 60))
                path_pts = [cx, cy]
                for s in range(steps + 1):
                    a = start + (angle * s / steps)
                    path_pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
                path_pts += [cx, cy]
                from reportlab.graphics.shapes import Polygon
                d.add(Polygon(path_pts, fillColor=colors.HexColor(col), strokeColor=colors.white, strokeWidth=1))
                # Etiqueta porcentaje en el sector
                if frac > 0.05:
                    mid_a = start + angle / 2
                    lx = cx + r * 0.65 * math.cos(mid_a)
                    ly = cy + r * 0.65 * math.sin(mid_a)
                    d.add(String(lx, ly - 3, f"{frac*100:.0f}%",
                                 fontSize=7, fillColor=colors.white,
                                 textAnchor="middle", fontName="Helvetica-Bold"))
                start = end
            # Leyenda a la derecha
            legend_x = cx + r + 18
            item_h = min(16, (height - 20) / len(labels))
            legend_y0 = cy + (len(labels) * item_h) / 2
            for i, (lbl, val, col) in enumerate(zip(labels, values, colors_hex)):
                y = legend_y0 - i * item_h
                d.add(Rect(legend_x, y - 5, 8, 8, fillColor=colors.HexColor(col), strokeColor=None))
                short = lbl if len(lbl) <= 16 else lbl[:14] + "…"
                d.add(String(legend_x + 12, y - 4, short,
                             fontSize=7, fillColor=colors.HexColor("#333333")))
            return d

        # ── Helper: gráfica de barras horizontales con reportlab Drawing ──
        def make_bar_chart_h(labels, values, bar_color, title, width=430, height=180):
            """Genera una gráfica de barras horizontales como Drawing de reportlab."""
            d = Drawing(width, height)
            if not values or max(values) == 0:
                return d
            max_val = max(values)
            n = len(labels)
            margin_left = 130
            margin_right = 20
            margin_top = 10
            margin_bottom = 20
            bar_area_w = width - margin_left - margin_right
            bar_h = max(10, (height - margin_top - margin_bottom) / n - 4)
            bar_col = colors.HexColor(bar_color)

            for i, (lbl, val) in enumerate(zip(labels, values)):
                y = height - margin_top - (i + 1) * (bar_h + 4) + 2
                bar_w = (val / max_val) * bar_area_w if max_val > 0 else 0
                # Barra fondo (gris)
                d.add(Rect(margin_left, y, bar_area_w, bar_h,
                           fillColor=colors.HexColor("#EEEEEE"), strokeColor=None))
                # Barra valor
                if bar_w > 0:
                    d.add(Rect(margin_left, y, bar_w, bar_h,
                               fillColor=bar_col, strokeColor=None))
                # Etiqueta izquierda
                short = lbl if len(lbl) <= 18 else lbl[:16] + "…"
                d.add(String(margin_left - 4, y + bar_h * 0.3, short,
                             fontSize=7.5, fillColor=colors.HexColor("#333333"),
                             textAnchor="end"))
                # Valor dentro/fuera barra
                val_str = "$ {:,.0f}".format(val).replace(",", ".")
                d.add(String(margin_left + bar_w + 4, y + bar_h * 0.3, val_str,
                             fontSize=7.5, fillColor=colors.HexColor("#555555"),
                             textAnchor="start"))
            # Línea base
            d.add(Line(margin_left, margin_bottom, margin_left, height - margin_top,
                       strokeColor=colors.HexColor("#CCCCCC"), strokeWidth=0.5))
            return d

        # ── Helper: gráfica de barras IVC ──
        def make_ivc_bar(factores, width=430, height=120):
            d = Drawing(width, height)
            labels = ["Técnico", "Material", "Económico", "Escala"]
            vals = [factores.get("tecnico",0), factores.get("material",0),
                    factores.get("economico",0), factores.get("escala",0)]
            bar_colors = ["#00FF88", "#58A6FF", "#FF9500", "#BD93F9"]
            n = len(labels)
            margin_l = 70; margin_r = 40; margin_t = 10; margin_b = 20
            area_w = width - margin_l - margin_r
            bar_h = (height - margin_t - margin_b) / n - 5
            for i, (lbl, val, bc) in enumerate(zip(labels, vals, bar_colors)):
                y = height - margin_t - (i+1)*(bar_h+5) + 2
                bar_w = (val/100)*area_w
                d.add(Rect(margin_l, y, area_w, bar_h, fillColor=colors.HexColor("#EEEEEE"), strokeColor=None))
                if bar_w > 0:
                    d.add(Rect(margin_l, y, bar_w, bar_h, fillColor=colors.HexColor(bc), strokeColor=None))
                d.add(String(margin_l-4, y+bar_h*0.3, lbl, fontSize=8, fillColor=colors.HexColor("#333333"), textAnchor="end"))
                d.add(String(margin_l+bar_w+4, y+bar_h*0.3, f"{val}/100", fontSize=8, fillColor=colors.HexColor("#555555"), textAnchor="start"))
            d.add(Line(margin_l, margin_b, margin_l, height-margin_t, strokeColor=colors.HexColor("#CCCCCC"), strokeWidth=0.5))
            return d

        story = []
        story.append(Paragraph("🌴 NovaPLAST CTG", style_title))
        story.append(Paragraph(f"Análisis de Residuo Plástico · {fecha} · Cartagena de Indias, Colombia", style_sub))
        story.append(HRFlowable(width="100%", thickness=2, color=verde))
        story.append(Spacer(1, 10))

        story.append(Paragraph("INFORMACIÓN GENERAL", style_section))
        story.append(tbl([["Campo","Valor"],["Material",f"{mat['nombre']} — {mat['nombre_completo']}"],
                           ["Código de reciclaje",f"#{mat['codigo_reciclaje']}"],["Aplicación",app_data["producto"]],
                           ["Mercado",app_data["mercado"]],["Cantidad",f"{d['cantidad_kg']} kg"],
                           ["Viabilidad",f"{app_data['viabilidad']}%"]], [5*cm, 12*cm]))
        story.append(Spacer(1, 8))

        story.append(Paragraph("DESGLOSE DE COSTOS (COP por unidad)", style_section))
        cost_rows = [["Concepto", "Valor (COP)"]]
        cost_labels = ["Materia prima","Lavado","Triturado","Peletizado","Mano de obra","Energía","Overhead (22%)"]
        cost_vals   = [c["materia_prima"],c["lavado"],c["triturado"],c["peletizado"],c["mano_obra"],c["energia"],c["overhead"]]
        for label, val in zip(cost_labels, cost_vals):
            cost_rows.append([label, f_cop(val)])
        cost_rows += [["COSTO TOTAL",f_cop(c["total"])],[f"PRECIO VENTA ({e['margen_porcentaje']:.0f}%)",f_cop(e["precio_venta"])],
                      ["GANANCIA NETA",f_cop(e["ganancia"])],["ROI",f"{e['roi']:.1f}%"]]
        n_rows = len(cost_rows)
        t_cost = Table(cost_rows, colWidths=[10*cm, 7*cm])
        t_cost.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),gris),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),
            ("ROWBACKGROUNDS",(0,1),(-1,n_rows-5),[colors.white,colors.HexColor("#F5F5F5")]),
            ("BACKGROUND",(0,n_rows-4),(-1,-1),verde_claro),("FONTNAME",(0,n_rows-4),(-1,-1),"Helvetica-Bold"),
            ("TEXTCOLOR",(0,n_rows-4),(-1,-1),verde),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#CCCCCC")),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),5),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),8),("ALIGN",(1,0),(1,-1),"RIGHT"),
        ]))
        story.append(t_cost)
        story.append(Spacer(1, 10))

        pie_colors_costos = ["#00FF88","#58A6FF","#FF9500","#BD93F9","#FF4444","#FFCC00","#4FC3F7"]
        pie_colors_ivc    = ["#00FF88","#58A6FF","#FF9500","#BD93F9"]

        # ── GRÁFICA 1: Costos desglosados — Barras ──
        story.append(Paragraph("📊 Gráfica de Barras — Desglose de Costos de Producción", style_chart_title))
        chart_costos = make_bar_chart_h(
            cost_labels, cost_vals,
            "#00662B", "Costos", width=430, height=200
        )
        story.append(chart_costos)
        story.append(Spacer(1, 8))

        # ── GRÁFICA 1b: Costos desglosados — Pastel ──
        story.append(Paragraph("🥧 Gráfica de Pastel — Proporción de Costos de Producción", style_chart_title))
        pie_costos = make_pie_chart(cost_labels, cost_vals, pie_colors_costos, "Costos", width=430, height=210)
        story.append(pie_costos)
        story.append(Spacer(1, 8))

        # ── GRÁFICA 2: Comparativa Costo / Venta / Ganancia — Barras ──
        story.append(Paragraph("💰 Gráfica de Barras — Costo vs Precio de Venta vs Ganancia", style_chart_title))
        chart_econ = make_bar_chart_h(
            ["Costo Total", f"Precio Venta ({e['margen_porcentaje']:.0f}%)", "Ganancia Neta"],
            [c["total"], e["precio_venta"], e["ganancia"]],
            "#1565C0", "Economía", width=430, height=110
        )
        story.append(chart_econ)
        story.append(Spacer(1, 8))

        # ── GRÁFICA 2b: Costo / Venta / Ganancia — Pastel ──
        story.append(Paragraph("🥧 Gráfica de Pastel — Distribución Económica", style_chart_title))
        pie_econ = make_pie_chart(
            ["Costo Total", f"Precio Venta ({e['margen_porcentaje']:.0f}%)", "Ganancia Neta"],
            [c["total"], e["precio_venta"], e["ganancia"]],
            ["#FF9500","#00FF88","#58A6FF"], "Economía", width=430, height=160
        )
        story.append(pie_econ)
        story.append(Spacer(1, 8))

        story.append(Paragraph("ÍNDICE DE VIABILIDAD CIRCULAR (IVC)", style_section))
        story.append(tbl([["Indicador","Valor"],["IVC Total",f"{ivc['ivc']} / 100"],
                           ["Clasificación",ivc["clasificacion"]],["Factor Técnico",str(ivc["factores"]["tecnico"])],
                           ["Factor Material",str(ivc["factores"]["material"])],
                           ["Factor Económico",str(ivc["factores"]["economico"])],
                           ["Factor de Escala",str(ivc["factores"]["escala"])],
                           ["Recomendación",ivc["recomendacion"]]], [5*cm, 12*cm]))
        story.append(Spacer(1, 8))

        # ── GRÁFICA 3: Factores IVC — Barras ──
        story.append(Paragraph("🔄 Gráfica de Barras — Factores del Índice de Viabilidad Circular", style_chart_title))
        chart_ivc = make_ivc_bar(ivc["factores"], width=430, height=130)
        story.append(chart_ivc)
        story.append(Spacer(1, 8))

        # ── GRÁFICA 3b: Factores IVC — Pastel ──
        story.append(Paragraph("🥧 Gráfica de Pastel — Proporción de Factores IVC", style_chart_title))
        ivc_f = ivc["factores"]
        pie_ivc = make_pie_chart(
            ["Técnico","Material","Económico","Escala"],
            [ivc_f.get("tecnico",0), ivc_f.get("material",0), ivc_f.get("economico",0), ivc_f.get("escala",0)],
            pie_colors_ivc, "IVC", width=430, height=180
        )
        story.append(pie_ivc)
        story.append(Spacer(1, 10))

        # ── Proveedores ──
        if proveedores:
            story.append(Paragraph("PROVEEDORES DE MATERIA PRIMA", style_section))
            prov_rows = [["Proveedor","Ciudad","Precio/kg","Vol. Mín.","Contacto"]]
            for p in proveedores:
                prov_rows.append([p["nombre"], p["ciudad"], f_cop(p["precio_compra"]),
                                   f"{p['volumen_min_kg']:,} kg".replace(",","."), p["contacto"]])
            story.append(tbl(prov_rows, [5.5*cm, 3*cm, 3*cm, 2.5*cm, 3*cm]))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"© {datetime.now().year} NovaPLAST CTG · Cartagena de Indias, Colombia", style_footer))

        doc.build(story)
        buf.seek(0)
        filename = f"NovaPLAST_{mat['nombre']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(buf, as_attachment=True, download_name=filename, mimetype="application/pdf")

    except ImportError:
        return jsonify({"error": "Instala reportlab: pip install reportlab"}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


# ─── EXPORTAR PDF COTIZACIÓN ──────────────────────────────────────────────────

@app.route("/exportar/cotizacion_pdf", methods=["POST"])
@login_required
def exportar_cotizacion_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm, mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.pdfgen import canvas as pdfcanvas
        from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame

        data = request.get_json()
        if not data:
            return jsonify({"error": "Sin datos"}), 400

        # ── Paleta idéntica a la vista previa ──────────────────────────────
        BG          = colors.HexColor("#0D1117")   # fondo página
        CARD        = colors.HexColor("#161B22")   # fondo tarjeta
        CARD_INNER  = colors.HexColor("#1C2128")   # fondo secciones internas
        BORDER      = colors.HexColor("#30363D")   # bordes
        ACC         = colors.HexColor("#00FF88")   # verde acento
        ACC_DIM     = colors.HexColor("#00CC6A")   # verde subtítulo
        RED         = colors.HexColor("#FF4444")   # rojo descuento
        WHITE       = colors.HexColor("#E6EDF3")   # texto principal
        GREY        = colors.HexColor("#8B949E")   # texto secundario
        DARK_TXT    = colors.HexColor("#060A0F")   # texto sobre verde

        W, H = A4
        mg = 1.8*cm

        buf = io.BytesIO()

        # ── Canvas con fondo oscuro en cada página ─────────────────────────
        class DarkCanvas(BaseDocTemplate):
            def handle_pageBegin(self):
                super().handle_pageBegin()
                c = self.canv
                c.setFillColor(BG)
                c.rect(0, 0, W, H, fill=1, stroke=0)

        doc = DarkCanvas(buf, pagesize=A4,
                         leftMargin=mg, rightMargin=mg,
                         topMargin=mg, bottomMargin=mg)

        frame = Frame(mg, mg, W - 2*mg, H - 2*mg, id="main")
        doc.addPageTemplates([PageTemplate(id="dark", frames=frame,
            onPage=lambda c,d: (c.setFillColor(BG), c.rect(0,0,W,H,fill=1,stroke=0)))])

        styles = getSampleStyleSheet()

        def ps(name, **kw):
            return ParagraphStyle(name, parent=styles["Normal"], **kw)

        s_logo      = ps("logo",  textColor=ACC,   fontSize=20, fontName="Helvetica-Bold", spaceAfter=2, leading=24)
        s_logo_sub  = ps("lsub",  textColor=GREY,  fontSize=8,  spaceAfter=0)
        s_nro       = ps("nro",   textColor=WHITE,  fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT)
        s_nro_sub   = ps("nrsub", textColor=GREY,  fontSize=8,  alignment=TA_RIGHT)
        s_label     = ps("lbl",   textColor=GREY,  fontSize=7,  fontName="Helvetica-Bold",
                          spaceAfter=3, leading=9)
        s_cli_name  = ps("clin",  textColor=WHITE,  fontSize=13, fontName="Helvetica-Bold", spaceAfter=2)
        s_cli_sub   = ps("clisb", textColor=GREY,  fontSize=8,  spaceAfter=0)
        s_col_hdr   = ps("chdr",  textColor=GREY,  fontSize=8,  fontName="Helvetica-Bold")
        s_prod      = ps("prod",  textColor=WHITE,  fontSize=11, fontName="Helvetica-Bold")
        s_mono      = ps("mono",  textColor=WHITE,  fontSize=11, alignment=TA_RIGHT)
        s_desc_lbl  = ps("dlbl",  textColor=GREY,  fontSize=9)
        s_desc_val  = ps("dval",  textColor=RED,   fontSize=9,  alignment=TA_RIGHT)
        s_total_lbl = ps("tlbl",  textColor=WHITE,  fontSize=13, fontName="Helvetica-Bold")
        s_total_val = ps("tval",  textColor=ACC,   fontSize=16, fontName="Helvetica-Bold", alignment=TA_RIGHT)
        s_notas     = ps("nt",    textColor=GREY,  fontSize=9)
        s_foot      = ps("ft",    textColor=GREY,  fontSize=7,  alignment=TA_CENTER)

        sub      = data.get("subtotal", data.get("total", 0))
        desc_val = data.get("descuentoValor", 0)
        total    = data.get("total", 0)
        cant     = data.get("cantidad", 0)
        pu       = data.get("precioUnit", 0)
        desc_pct = data.get("descuento", 0)
        producto = data.get("producto", "—")
        cliente  = data.get("cliente", "Sin cliente")
        fecha_cot= data.get("fecha", datetime.now().strftime("%d/%m/%Y"))
        nro      = data.get("id", "COT-000000")

        CW = W - 2*mg   # ancho útil dentro de la tarjeta

        def card_table(rows, col_widths, style_cmds, row_heights=None):
            t = Table(rows, colWidths=col_widths, rowHeights=row_heights)
            base = [
                ("BACKGROUND",   (0,0), (-1,-1), CARD),
                ("ROWBACKGROUNDS",(0,0),(-1,-1), [CARD]),
                ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING",  (0,0), (-1,-1), 12),
                ("RIGHTPADDING", (0,0), (-1,-1), 12),
                ("TOPPADDING",   (0,0), (-1,-1), 10),
                ("BOTTOMPADDING",(0,0), (-1,-1), 10),
                ("BOX",          (0,0), (-1,-1), 0.6, BORDER),
                ("LINEBELOW",    (0,0), (-1,-2), 0.4, BORDER),
            ]
            t.setStyle(TableStyle(base + style_cmds))
            return t

        story = []

        # ══ HEADER: logo + número cotización ════════════════════════════════
        # Logo: badge verde + nombre (sin emojis — ReportLab no los soporta)
        s_badge = ps("badge", textColor=DARK_TXT, fontSize=14, fontName="Helvetica-Bold",
                     backColor=ACC, borderPad=4, leading=16)
        s_logo_name = ps("lname", textColor=ACC, fontSize=16, fontName="Helvetica-Bold",
                          spaceAfter=0, leading=20)

        logo_inner = Table([
            [Paragraph(" NP ", s_badge),
             Paragraph("NovaPLAST CTG", s_logo_name)],
        ], colWidths=[1.1*cm, CW*0.5])
        logo_inner.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), CARD),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
            ("LEFTPADDING",  (0,0),(0,-1),  0),
            ("RIGHTPADDING", (0,0),(0,-1),  6),
            ("LEFTPADDING",  (1,0),(1,-1),  6),
            ("TOPPADDING",   (0,0),(-1,-1), 0),
            ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ]))

        hdr = Table([
            [logo_inner,
             Paragraph(f"N° {nro}", s_nro)],
            [Paragraph("Cartagena de Indias, Colombia", s_logo_sub),
             Paragraph(fecha_cot, s_nro_sub)],
        ], colWidths=[CW*0.6, CW*0.4])
        hdr.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), CARD),
            ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
            ("VALIGN",       (1,0),(1,0),   "TOP"),
            ("LEFTPADDING",  (0,0),(-1,-1), 12),
            ("RIGHTPADDING", (0,0),(-1,-1), 12),
            ("TOPPADDING",   (0,0),(-1,-1), 14),
            ("BOTTOMPADDING",(0,0),(-1,-1), 14),
            ("LINEBELOW",    (0,0),(-1,0),  0.4, BORDER),
            ("BOX",          (0,0),(-1,-1), 0.6, BORDER),
        ]))
        story.append(hdr)
        story.append(Spacer(1, 4))

        # ══ CLIENTE ══════════════════════════════════════════════════════════
        if cliente and cliente != "Sin cliente":
            cli_info = data.get("clienteInfo", {})
            sector   = cli_info.get("sector", "") if isinstance(cli_info, dict) else ""
            ciudad   = cli_info.get("ciudad", "") if isinstance(cli_info, dict) else ""
            sub_line = " · ".join(filter(None, [sector, ciudad]))
            cli_tbl = card_table([
                [Paragraph("PARA:", s_label)],
                [Paragraph(cliente, s_cli_name)],
                [Paragraph(sub_line or "&nbsp;", s_cli_sub)],
            ], [CW], [
                ("TOPPADDING",   (0,0),(-1,0), 12),
                ("BOTTOMPADDING",(0,2),(-1,2), 12),
                ("TOPPADDING",   (0,1),(-1,2), 2),
                ("LINEBELOW",    (0,0),(-1,-1), 0, CARD),
                ("BOX",          (0,0),(-1,-1), 0.6, BORDER),
            ])
            story.append(cli_tbl)
            story.append(Spacer(1, 4))

        # ══ TABLA DE PRODUCTOS ════════════════════════════════════════════════
        col_hdr_row = [
            Paragraph("Producto",   s_col_hdr),
            Paragraph("Cant.",      s_col_hdr),
            Paragraph("P. Unit.",   s_col_hdr),
            Paragraph("Total",      s_col_hdr),
        ]
        prod_row = [
            Paragraph(producto,            s_prod),
            Paragraph(f"{cant:,} und".replace(",","."), ps("cu", textColor=WHITE, fontSize=11)),
            Paragraph(f_cop(pu),           s_mono),
            Paragraph(f_cop(sub),          s_mono),
        ]
        cws = [CW*0.38, CW*0.18, CW*0.22, CW*0.22]
        det_tbl = card_table(
            [col_hdr_row, prod_row],
            cws,
            [
                ("FONTNAME",     (0,0),(-1,0), "Helvetica"),
                ("TEXTCOLOR",    (0,0),(-1,0), GREY),
                ("TOPPADDING",   (0,0),(-1,0), 10),
                ("BOTTOMPADDING",(0,0),(-1,0), 10),
                ("ALIGN",        (1,0),(-1,-1), "RIGHT"),
                ("ALIGN",        (0,0),(0,-1),  "LEFT"),
                ("LINEBELOW",    (0,0),(-1,0),  0.6, BORDER),
                ("LINEBELOW",    (0,1),(-1,1),  0, CARD),
            ]
        )
        story.append(det_tbl)
        story.append(Spacer(1, 4))

        # ══ TOTALES ═══════════════════════════════════════════════════════════
        tot_rows = []
        tot_cmds = []

        if desc_pct > 0:
            tot_rows.append([
                Paragraph(f"Descuento ({int(desc_pct)}%)", s_desc_lbl),
                Paragraph(f"-{f_cop(desc_val)}",           s_desc_val),
            ])
            tot_cmds += [("TEXTCOLOR",(1,0),(1,0), RED)]

        r_total = len(tot_rows)
        tot_rows.append([
            Paragraph("TOTAL", s_total_lbl),
            Paragraph(f_cop(total), s_total_val),
        ])
        tot_cmds += [
            ("LINEABOVE",    (0, r_total),(-1, r_total), 0.6, BORDER),
            ("TOPPADDING",   (0, r_total),(-1, r_total), 14),
            ("BOTTOMPADDING",(0, r_total),(-1, r_total), 14),
        ]

        tot_tbl = card_table(tot_rows, [CW*0.6, CW*0.4], tot_cmds)
        story.append(tot_tbl)

        # ══ NOTAS ════════════════════════════════════════════════════════════
        if data.get("notas"):
            story.append(Spacer(1, 4))
            notas_tbl = card_table([
                [Paragraph(data["notas"], s_notas)]
            ], [CW], [("LINEBELOW",(0,0),(-1,-1),0,CARD)])
            story.append(notas_tbl)

        # ══ FOOTER ═══════════════════════════════════════════════════════════
        story.append(Spacer(1, 16))
        story.append(Paragraph(
            f"© {datetime.now().year} NovaPLAST CTG · Cartagena de Indias, Colombia · Sistema de Gestión Circular",
            s_foot))

        doc.build(story)
        buf.seek(0)
        fname = f"Cotizacion_{nro}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(buf, as_attachment=True, download_name=fname, mimetype="application/pdf")

    except ImportError:
        return jsonify({"error": "Instala reportlab: pip install reportlab"}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


# ─── EXPORTAR CLIENTES EXCEL ─────────────────────────────────────────────────

@app.route("/exportar/clientes_excel", methods=["POST"])
@login_required
def exportar_clientes_excel():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        data = request.get_json()
        if not data or not data.get("clientes"):
            return jsonify({"error": "Sin datos"}), 400

        clis = data["clientes"]

        wb = Workbook()
        ws = wb.active
        ws.title = "Clientes"

        C_BG   = "0D1117"; C_ACC  = "00FF88"; C_SEC  = "161B22"
        C_ALT  = "1C2128"; C_W    = "E6EDF3"; C_GR   = "8B949E"
        C_BRD  = "30363D"; C_RED  = "FF4444"; C_YEL  = "F0B429"

        thin  = Side(style="thin", color=C_BRD)
        brd   = Border(left=thin, right=thin, top=thin, bottom=thin)
        ctr   = Alignment(horizontal="center", vertical="center", wrap_text=True)
        lft   = Alignment(horizontal="left",   vertical="center", wrap_text=True)

        # Título
        ws.merge_cells("A1:L1")
        ws["A1"] = "NovaPLAST CTG — Directorio de Clientes"
        ws["A1"].font      = Font(name="Calibri", bold=True, size=16, color=C_ACC)
        ws["A1"].fill      = PatternFill("solid", fgColor=C_BG)
        ws["A1"].alignment = ctr
        ws.row_dimensions[1].height = 38

        ws.merge_cells("A2:L2")
        ws["A2"] = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}  ·  Cartagena de Indias, Colombia  ·  Total: {len(clis)} cliente(s)"
        ws["A2"].font      = Font(name="Calibri", italic=True, size=9, color=C_GR)
        ws["A2"].fill      = PatternFill("solid", fgColor=C_BG)
        ws["A2"].alignment = ctr
        ws.row_dimensions[2].height = 18
        ws.row_dimensions[3].height = 6

        # Leyenda de criterios de calificación
        ws.merge_cells("A3:L3")
        ws["A3"] = "Calificación automática: Vol. compra (1★) + Frecuencia (1★) + Puntualidad pago (1★) + Antigüedad (1★) + N° cotizaciones (1★)"
        ws["A3"].font      = Font(name="Calibri", italic=True, size=8, color=C_GR)
        ws["A3"].fill      = PatternFill("solid", fgColor=C_SEC)
        ws["A3"].alignment = ctr
        ws.row_dimensions[3].height = 14

        # Cabeceras
        COLS = [
            ("Cliente",             22), ("Sector",         14), ("Ciudad",       14),
            ("Estado",              11), ("Producto",        18), ("Vol./mes (und)",13),
            ("Frecuencia",          13), ("Puntualidad pago",15), ("Antigüedad (m)",13),
            ("Cotizaciones",        12), ("Calificación",    14), ("Notas",         28),
        ]
        for ci, (hdr, w) in enumerate(COLS, 1):
            cell = ws.cell(row=4, column=ci, value=hdr)
            cell.font      = Font(name="Calibri", bold=True, size=10, color=C_W)
            cell.fill      = PatternFill("solid", fgColor=C_SEC)
            cell.alignment = ctr
            cell.border    = brd
            ws.column_dimensions[get_column_letter(ci)].width = w
        ws.row_dimensions[4].height = 22

        FREQ_LBL = {1:"Única vez",2:"Ocasional",3:"Mensual",4:"Quincenal",5:"Semanal"}
        PAGO_LBL = {1:"Siempre tarde",2:"Frecuente retraso",3:"A veces tarde",4:"Casi siempre",5:"Siempre puntual"}

        for i, c in enumerate(clis):
            row  = 5 + i
            bg   = C_ALT if i % 2 == 0 else C_BG
            fill = PatternFill("solid", fgColor=bg)

            estado      = (c.get("estado") or "potencial").lower()
            estado_col  = C_ACC if estado=="activo" else C_RED if estado=="inactivo" else C_YEL
            freq        = int(c.get("frecuencia") or 3)
            pago        = int(c.get("puntualidad_pago") or 3)
            rating      = int(c.get("rating") or 1)

            vals = [
                c.get("nombre","—"),
                c.get("sector","—"),
                c.get("ciudad","—"),
                estado.capitalize(),
                c.get("producto","—"),
                c.get("volumen") or "—",
                FREQ_LBL.get(freq, str(freq)),
                PAGO_LBL.get(pago, str(pago)),
                c.get("antiguedad") or "0",
                c.get("n_cotizaciones") or "0",
                "★"*rating + "☆"*(5-rating),
                c.get("notas","—"),
            ]

            for ci2, val in enumerate(vals, 1):
                cell = ws.cell(row=row, column=ci2, value=str(val) if val is not None else "—")
                cell.fill      = fill
                cell.border    = brd
                cell.alignment = lft
                cell.font      = Font(name="Calibri", size=9, color=C_W)

            ws.cell(row=row, column=4).font  = Font(name="Calibri", bold=True, size=9, color=estado_col)
            ws.cell(row=row, column=11).font = Font(name="Calibri", size=9,
                                                    color=C_ACC if rating>=4 else C_YEL if rating>=3 else C_RED)
            ws.row_dimensions[row].height = 18

        # Fila resumen
        last = 5 + len(clis)
        ws.merge_cells(f"A{last}:C{last}")
        ws[f"A{last}"] = f"Total clientes: {len(clis)}"
        ws[f"A{last}"].font = Font(name="Calibri", bold=True, size=10, color=C_ACC)
        ws[f"A{last}"].fill = PatternFill("solid", fgColor=C_BG)
        ws[f"A{last}"].alignment = lft
        ws[f"A{last}"].border = brd

        activos = sum(1 for c in clis if (c.get("estado") or "").lower()=="activo")
        ws.merge_cells(f"D{last}:G{last}")
        ws[f"D{last}"] = f"Activos: {activos}  ·  Potenciales: {sum(1 for c in clis if (c.get('estado') or '').lower()=='potencial')}  ·  Inactivos: {len(clis)-activos-sum(1 for c in clis if (c.get('estado') or '').lower()=='potencial')}"
        ws[f"D{last}"].font = Font(name="Calibri", size=9, color=C_GR)
        ws[f"D{last}"].fill = PatternFill("solid", fgColor=C_BG)
        ws[f"D{last}"].alignment = lft
        ws[f"D{last}"].border = brd

        ws.freeze_panes = "A5"

        buf = io.BytesIO()
        wb.save(buf); buf.seek(0)
        fname = f"NovaPLAST_Clientes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return send_file(buf, as_attachment=True, download_name=fname,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except ImportError:
        return jsonify({"error": "Instala openpyxl: pip install openpyxl"}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


# ─── EXPORTAR PROVEEDORES EXCEL ──────────────────────────────────────────────

@app.route("/exportar/proveedores_excel", methods=["POST"])
@login_required
def exportar_proveedores_excel():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        data = request.get_json()
        if not data or not data.get("proveedores"):
            return jsonify({"error": "Sin datos"}), 400

        provs = data["proveedores"]

        wb = Workbook()
        ws = wb.active
        ws.title = "Proveedores"

        # ── Colores ──────────────────────────────────────────────────────────
        C_BG_HEAD  = "0D1117"   # negro fondo título
        C_ACC      = "00FF88"   # verde acento
        C_SEC      = "161B22"   # gris oscuro cabecera columnas
        C_ALT      = "1C2128"   # gris alternado filas
        C_WHITE    = "E6EDF3"
        C_GREY     = "8B949E"
        C_BORDER   = "30363D"

        thin   = Side(style="thin",   color=C_BORDER)
        brd    = Border(left=thin, right=thin, top=thin, bottom=thin)
        center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left   = Alignment(horizontal="left",   vertical="center", wrap_text=True)

        # ── Fila 1: Título ───────────────────────────────────────────────────
        ws.merge_cells("A1:L1")
        ws["A1"] = "NovaPLAST CTG — Directorio de Proveedores"
        ws["A1"].font      = Font(name="Calibri", bold=True, size=16, color=C_ACC)
        ws["A1"].fill      = PatternFill("solid", fgColor=C_BG_HEAD)
        ws["A1"].alignment = center
        ws.row_dimensions[1].height = 38

        # ── Fila 2: Subtítulo ────────────────────────────────────────────────
        ws.merge_cells("A2:L2")
        ws["A2"] = f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}  ·  Cartagena de Indias, Colombia  ·  Total: {len(provs)} proveedor(es)"
        ws["A2"].font      = Font(name="Calibri", italic=True, size=9, color=C_GREY)
        ws["A2"].fill      = PatternFill("solid", fgColor=C_BG_HEAD)
        ws["A2"].alignment = center
        ws.row_dimensions[2].height = 18

        ws.row_dimensions[3].height = 6  # espaciado

        # ── Fila 4: Cabeceras de columnas ────────────────────────────────────
        COLS = [
            ("Proveedor",          22),
            ("Ciudad",             16),
            ("Material",           16),
            ("Precio/kg (COP)",    16),
            ("Precio Neg. (COP)",  16),
            ("Vol. Mín. (kg)",     14),
            ("Vol. Máx. (kg)",     14),
            ("Entrega (días)",     13),
            ("Estado",             12),
            ("Rating",             10),
            ("Contacto",           20),
            ("Notas",              28),
        ]
        for col_idx, (hdr, w) in enumerate(COLS, 1):
            cell = ws.cell(row=4, column=col_idx, value=hdr)
            cell.font      = Font(name="Calibri", bold=True, size=10, color=C_WHITE)
            cell.fill      = PatternFill("solid", fgColor=C_SEC)
            cell.alignment = center
            cell.border    = brd
            ws.column_dimensions[get_column_letter(col_idx)].width = w
        ws.row_dimensions[4].height = 22

        # ── Filas de datos ────────────────────────────────────────────────────
        for i, p in enumerate(provs):
            row = 5 + i
            bg  = C_ALT if i % 2 == 0 else C_BG_HEAD
            fill = PatternFill("solid", fgColor=bg)

            # Estado con color
            estado = (p.get("estado") or "activo").lower()
            estado_color = "00FF88" if estado == "activo" else "FF4444" if estado == "inactivo" else "F0B429"

            valores = [
                p.get("nombre","—"),
                p.get("ciudad","—"),
                p.get("material","—"),
                p.get("precio_kg","—"),
                p.get("precio_neg","—"),
                p.get("volumen_min","—"),
                p.get("volumen_max","—"),
                p.get("entrega","—"),
                estado.capitalize(),
                p.get("rating","—"),
                f"{p.get('contacto','')} {p.get('tel','')} {p.get('email','')}".strip() or "—",
                p.get("notas","—"),
            ]

            for col_idx, val in enumerate(valores, 1):
                cell = ws.cell(row=row, column=col_idx, value=str(val) if val is not None else "—")
                cell.fill      = fill
                cell.border    = brd
                cell.alignment = left
                cell.font      = Font(name="Calibri", size=9, color=C_WHITE)

            # Estado en color
            est_cell = ws.cell(row=row, column=9)
            est_cell.font = Font(name="Calibri", bold=True, size=9, color=estado_color)

            # Rating con estrellas
            rating = int(p.get("rating") or 0)
            ws.cell(row=row, column=10).value = "★" * rating + "☆" * (5 - rating)
            ws.cell(row=row, column=10).font  = Font(name="Calibri", size=9,
                                                      color="F0B429" if rating >= 4 else C_WHITE)
            ws.row_dimensions[row].height = 18

        # ── Fila final: totales rápidos ───────────────────────────────────────
        last = 5 + len(provs)
        ws.merge_cells(f"A{last}:C{last}")
        ws[f"A{last}"] = f"Total proveedores: {len(provs)}"
        ws[f"A{last}"].font      = Font(name="Calibri", bold=True, size=10, color=C_ACC)
        ws[f"A{last}"].fill      = PatternFill("solid", fgColor=C_BG_HEAD)
        ws[f"A{last}"].alignment = left
        ws[f"A{last}"].border    = brd
        ws.row_dimensions[last].height = 20

        activos = sum(1 for p in provs if (p.get("estado") or "activo").lower() == "activo")
        ws.merge_cells(f"D{last}:F{last}")
        ws[f"D{last}"] = f"Activos: {activos}  ·  Inactivos: {len(provs)-activos}"
        ws[f"D{last}"].font      = Font(name="Calibri", size=9, color=C_GREY)
        ws[f"D{last}"].fill      = PatternFill("solid", fgColor=C_BG_HEAD)
        ws[f"D{last}"].alignment = left
        ws[f"D{last}"].border    = brd

        # Freeze panes debajo de cabecera
        ws.freeze_panes = "A5"

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        fname = f"NovaPLAST_Proveedores_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return send_file(buf, as_attachment=True, download_name=fname,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except ImportError:
        return jsonify({"error": "Instala openpyxl: pip install openpyxl"}), 500
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  🌴 NovaPLAST CTG — Sistema Inteligente de Plásticos")
    print("=" * 55)
    print("  Servidor iniciado en: http://localhost:5000")
    print("  Presiona Ctrl+C para detener")
    print("=" * 55)
    app.run(debug=True, host="0.0.0.0", port=5000)