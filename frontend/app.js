/* ==========================================================================
   VAANI AI - Client Application Logic (JavaScript)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // DOM Elements
  const dropZone = document.getElementById('dropZone');
  const audioInput = document.getElementById('audioInput');
  const demoBtn = document.getElementById('demoBtn');
  
  const processingCard = document.getElementById('processingCard');
  const processingStatus = document.getElementById('processingStatus');
  const processingDetail = document.getElementById('processingDetail');
  const progressBar = document.getElementById('progressBar');
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const step3 = document.getElementById('step3');

  const dashboard = document.getElementById('dashboard');
  const audioPlayer = document.getElementById('audioPlayer');
  const meetingTitle = document.getElementById('meetingTitle');
  const meetingDuration = document.getElementById('meetingDuration');
  const speedBtns = document.querySelectorAll('.speed-btn');

  const summaryText = document.getElementById('summaryText');
  const decisionsList = document.getElementById('decisionsList');
  const actionsList = document.getElementById('actionsList');
  const keypointsList = document.getElementById('keypointsList');
  const transcriptList = document.getElementById('transcriptList');
  const transcriptSearch = document.getElementById('transcriptSearch');
  
  const decisionsCount = document.getElementById('decisionsCount');
  const actionsCount = document.getElementById('actionsCount');
  const keypointsCount = document.getElementById('keypointsCount');

  const chatInput = document.getElementById('chatInput');
  const sendChatBtn = document.getElementById('sendChatBtn');
  const chatMessages = document.getElementById('chatMessages');
  const promptChips = document.querySelectorAll('.prompt-chip');

  // Application State
  let currentMeetingId = null;
  let meetingData = null;
  let audioSegments = [];

  // ==========================================
  // EVENT LISTENERS: FILE UPLOAD & DRAG/DROP
  // ==========================================

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  audioInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  demoBtn.addEventListener('click', loadDemoMeeting);

  // ==========================================
  // FILE UPLOAD HANDLER
  // ==========================================

  async function handleFileUpload(file) {
    if (!file.type.startsWith('audio/')) {
      alert('Please upload a valid audio file (MP3, WAV, M4A, etc.)');
      return;
    }

    showProcessingState('Uploading audio file...', 'Transferring file to backend server', 25, 1);

    const formData = new FormData();
    formData.append('audio', file);

    try {
      showProcessingState('Transcribing with Whisper STT...', 'Processing speech-to-text with word timestamps', 55, 2);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to upload audio');
      }

      showProcessingState('Extracting Insights with Groq LLM...', 'Generating summary, decisions, action items & knowledge graph', 90, 3);

      const data = await response.json();
      
      // Load audio stream source
      audioPlayer.src = `/api/audio/${data.meeting_id}.wav`;
      meetingTitle.textContent = file.name;

      renderMeetingDashboard(data);
      hideProcessingState();

    } catch (error) {
      hideProcessingState();
      alert(`Error processing audio: ${error.message}`);
      console.error(error);
    }
  }

  // ==========================================
  // LOAD DEMO MEETING
  // ==========================================

  async function loadDemoMeeting() {
    showProcessingState('Loading Sample Meeting...', 'Fetching pre-computed audio transcript & LLM insights', 50, 2);
    
    try {
      const response = await fetch('/api/demo');
      if (!response.ok) {
        throw new Error('Demo data not available');
      }

      const data = await response.json();
      audioPlayer.src = '/api/audio/meeting.mp3';
      meetingTitle.textContent = 'Sample Team Building Meeting.mp3';

      renderMeetingDashboard(data);
      hideProcessingState();

    } catch (error) {
      hideProcessingState();
      alert(`Demo Error: ${error.message}`);
    }
  }

  // ==========================================
  // PROCESSING OVERLAY HELPERS
  // ==========================================

  function showProcessingState(status, detail, progress, step) {
    processingCard.classList.remove('hidden');
    processingStatus.textContent = status;
    processingDetail.textContent = detail;
    progressBar.style.width = `${progress}%`;

    [step1, step2, step3].forEach((s, idx) => {
      if (idx + 1 <= step) {
        s.classList.add('active');
      } else {
        s.classList.remove('active');
      }
    });
  }

  function hideProcessingState() {
    processingCard.classList.add('hidden');
  }

  // ==========================================
  // DASHBOARD RENDERER
  // ==========================================

  function renderMeetingDashboard(data) {
    currentMeetingId = data.meeting_id;
    meetingData = data;
    audioSegments = data.segments || [];

    const structured = data.structured_data || {};

    // 1. Executive Summary
    summaryText.textContent = structured.summary || 'No summary available.';

    // 2. Decisions List
    const decisions = structured.decisions || [];
    decisionsCount.textContent = decisions.length;
    renderDecisions(decisions);

    // 3. Action Items List
    const actions = structured.action_items || [];
    actionsCount.textContent = actions.length;
    renderActionItems(actions);

    // 4. Key Points
    const keypoints = structured.key_points || [];
    keypointsCount.textContent = keypoints.length;
    renderKeyPoints(keypoints);

    // 5. Knowledge Graph Visualizer
    renderKnowledgeGraph(structured.knowledge_graph);

    // 6. Transcript
    renderTranscript(audioSegments);

    // Show Dashboard Grid
    dashboard.classList.remove('hidden');
  }

  // ==========================================
  // INSIGHT CARDS RENDERERS
  // ==========================================

  function renderDecisions(decisions) {
    if (decisions.length === 0) {
      decisionsList.innerHTML = '<p class="text-muted">No explicit decisions detected in this meeting.</p>';
      return;
    }

    decisionsList.innerHTML = decisions.map(d => `
      <div class="insight-card">
        <div class="insight-card-title"><i class="fa-solid fa-circle-check text-success"></i> ${escapeHtml(d.decision)}</div>
        <div class="meta-tags">
          <span class="meta-tag"><i class="fa-regular fa-user"></i> Proposed by: ${escapeHtml(d.proposed_by || 'Unknown')}</span>
        </div>
        ${d.evidence_quote ? `
          <div class="evidence-quote">
            <span>"${escapeHtml(d.evidence_quote)}"</span>
            <button class="seek-badge" onclick="seekToTime(${d.evidence_timestamp || 0})">
              <i class="fa-solid fa-play"></i> ${formatTime(d.evidence_timestamp || 0)}
            </button>
          </div>
        ` : ''}
      </div>
    `).join('');
  }

  function renderActionItems(actions) {
    if (actions.length === 0) {
      actionsList.innerHTML = '<p class="text-muted">No action items assigned in this meeting.</p>';
      return;
    }

    actionsList.innerHTML = actions.map(a => `
      <div class="insight-card">
        <div class="insight-card-title"><i class="fa-solid fa-square-check text-primary"></i> ${escapeHtml(a.task)}</div>
        <div class="meta-tags">
          <span class="meta-tag"><i class="fa-solid fa-user-tag"></i> Assignee: ${escapeHtml(a.assigned_to || 'Unassigned')}</span>
          ${a.deadline ? `<span class="meta-tag"><i class="fa-regular fa-clock"></i> Due: ${escapeHtml(a.deadline)}</span>` : ''}
        </div>
        ${a.evidence_quote ? `
          <div class="evidence-quote">
            <span>"${escapeHtml(a.evidence_quote)}"</span>
            <button class="seek-badge" onclick="seekToTime(${a.evidence_timestamp || 0})">
              <i class="fa-solid fa-play"></i> ${formatTime(a.evidence_timestamp || 0)}
            </button>
          </div>
        ` : ''}
      </div>
    `).join('');
  }

  function renderKeyPoints(keypoints) {
    if (keypoints.length === 0) {
      keypointsList.innerHTML = '<p class="text-muted">No key points listed.</p>';
      return;
    }

    keypointsList.innerHTML = keypoints.map(k => `
      <div class="insight-card">
        <div class="insight-card-title"><i class="fa-regular fa-lightbulb text-warning"></i> ${escapeHtml(k.point)}</div>
        <div class="meta-tags">
          <span class="meta-tag"><i class="fa-regular fa-comment"></i> Speaker: ${escapeHtml(k.speaker || 'Unknown')}</span>
        </div>
        ${k.evidence_quote ? `
          <div class="evidence-quote">
            <span>"${escapeHtml(k.evidence_quote)}"</span>
            <button class="seek-badge" onclick="seekToTime(${k.evidence_timestamp || 0})">
              <i class="fa-solid fa-play"></i> ${formatTime(k.evidence_timestamp || 0)}
            </button>
          </div>
        ` : ''}
      </div>
    `).join('');
  }

  // ==========================================
  // KNOWLEDGE GRAPH SVG VISUALIZER
  // ==========================================

  function renderKnowledgeGraph(graph) {
    const svg = document.getElementById('knowledgeGraphSvg');
    svg.innerHTML = '';

    if (!graph || !graph.nodes || graph.nodes.length === 0) {
      svg.innerHTML = '<text x="50%" y="50%" fill="#64748b" text-anchor="middle">No knowledge graph data</text>';
      return;
    }

    const width = svg.clientWidth || 600;
    const height = svg.clientHeight || 340;
    const nodeCount = graph.nodes.length;
    const radius = Math.min(width, height) * 0.35;
    const centerX = width / 2;
    const centerY = height / 2;

    // Calculate node coordinates in circle
    const nodeCoords = {};
    graph.nodes.forEach((node, i) => {
      const angle = (i / nodeCount) * 2 * Math.PI - Math.PI / 2;
      nodeCoords[node.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        type: node.type || 'topic',
        label: node.id
      };
    });

    // Draw directed edge lines
    const edgesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    (graph.edges || []).forEach(edge => {
      const source = nodeCoords[edge.from];
      const target = nodeCoords[edge.to];
      if (source && target) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', source.x);
        line.setAttribute('y1', source.y);
        line.setAttribute('x2', target.x);
        line.setAttribute('y2', target.y);
        line.setAttribute('stroke', 'rgba(255, 255, 255, 0.15)');
        line.setAttribute('stroke-width', '2');
        edgesGroup.appendChild(line);

        // Edge label
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', midX);
        text.setAttribute('y', midY);
        text.setAttribute('fill', '#94a3b8');
        text.setAttribute('font-size', '10');
        text.setAttribute('text-anchor', 'middle');
        text.textContent = edge.relation;
        edgesGroup.appendChild(text);
      }
    });
    svg.appendChild(edgesGroup);

    // Draw node circles & text
    const colorMap = {
      topic: '#00f2fe',
      person: '#f107a3',
      decision: '#00e676',
      money: '#ffd700'
    };

    graph.nodes.forEach(node => {
      const coords = nodeCoords[node.id];
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');

      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', coords.x);
      circle.setAttribute('cy', coords.y);
      circle.setAttribute('r', '18');
      circle.setAttribute('fill', colorMap[coords.type] || '#00f2fe');
      circle.setAttribute('opacity', '0.85');
      circle.setAttribute('stroke', '#ffffff');
      circle.setAttribute('stroke-width', '2');

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', coords.x);
      text.setAttribute('y', coords.y + 32);
      text.setAttribute('fill', '#f0f4fc');
      text.setAttribute('font-size', '11');
      text.setAttribute('font-family', 'Outfit, sans-serif');
      text.setAttribute('font-weight', '600');
      text.setAttribute('text-anchor', 'middle');
      text.textContent = coords.label;

      g.appendChild(circle);
      g.appendChild(text);
      svg.appendChild(g);
    });
  }

  // ==========================================
  // TRANSCRIPT STREAM
  // ==========================================

  function renderTranscript(segments) {
    if (!segments || segments.length === 0) {
      transcriptList.innerHTML = '<p class="text-muted">No transcript available.</p>';
      return;
    }

    transcriptList.innerHTML = segments.map((seg, idx) => `
      <div class="transcript-line" id="seg-${idx}" onclick="seekToTime(${seg.start})">
        <span class="time-stamp">[${formatTime(seg.start)}]</span>
        <span class="line-text">${escapeHtml(seg.text)}</span>
      </div>
    `).join('');
  }

  // Live Audio Time Sync with Transcript
  audioPlayer.addEventListener('timeupdate', () => {
    const currentTime = audioPlayer.currentTime;
    
    // Highlight active transcript segment
    audioSegments.forEach((seg, idx) => {
      const lineEl = document.getElementById(`seg-${idx}`);
      if (lineEl) {
        if (currentTime >= seg.start && currentTime <= seg.end) {
          lineEl.classList.add('active');
        } else {
          lineEl.classList.remove('active');
        }
      }
    });

    meetingDuration.textContent = `Time: ${formatTime(currentTime)} / ${formatTime(audioPlayer.duration || 0)}`;
  });

  // Transcript Search Filter
  transcriptSearch.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const lines = transcriptList.querySelectorAll('.transcript-line');
    lines.forEach(line => {
      const text = line.textContent.toLowerCase();
      line.style.display = text.includes(query) ? 'flex' : 'none';
    });
  });

  // Audio Playback Speed Controls
  speedBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      speedBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      audioPlayer.playbackRate = parseFloat(btn.dataset.speed);
    });
  });

  // Global Seek Helper
  window.seekToTime = function(seconds) {
    audioPlayer.currentTime = seconds;
    audioPlayer.play();
  };

  // ==========================================
  // TABS SWITCHING LOGIC
  // ==========================================

  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) {
        targetPane.classList.add('active');
      }

      if (btn.dataset.tab === 'tab-graph' && meetingData) {
        renderKnowledgeGraph(meetingData.structured_data?.knowledge_graph);
      }
    });
  });

  // ==========================================
  // AI Q&A CHAT INTERACTION
  // ==========================================

  sendChatBtn.addEventListener('click', handleChatSubmit);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleChatSubmit();
  });

  promptChips.forEach(chip => {
    chip.addEventListener('click', () => {
      chatInput.value = chip.dataset.prompt;
      handleChatSubmit();
    });
  });

  async function handleChatSubmit() {
    const question = chatInput.value.trim();
    if (!question) return;

    if (!currentMeetingId) {
      alert('Please upload an audio file or load a sample meeting first.');
      return;
    }

    // Append User Message
    appendChatMessage(question, 'user');
    chatInput.value = '';

    // Append Bot Loading Message
    const loadingId = appendChatMessage('<i class="fa-solid fa-spinner fa-spin"></i> Analyzing meeting context...', 'bot');

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          meeting_id: currentMeetingId,
          question: question
        })
      });

      const data = await response.json();
      removeChatMessage(loadingId);

      if (response.ok && data.answer) {
        appendChatMessage(data.answer, 'bot');
      } else {
        appendChatMessage(`Error: ${data.error || 'Failed to get answer'}`, 'bot');
      }

    } catch (error) {
      removeChatMessage(loadingId);
      appendChatMessage(`Connection error: ${error.message}`, 'bot');
    }
  }

  function appendChatMessage(text, sender) {
    const msgId = `msg-${Date.now()}`;
    const messageEl = document.createElement('div');
    messageEl.className = `chat-bubble ${sender}-message`;
    messageEl.id = msgId;

    const icon = sender === 'user' ? 'fa-user' : 'fa-robot';
    
    messageEl.innerHTML = `
      <div class="avatar"><i class="fa-solid ${icon}"></i></div>
      <div class="bubble-content">${text}</div>
    `;

    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgId;
  }

  function removeChatMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // ==========================================
  // UTILITY HELPERS
  // ==========================================

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

});
