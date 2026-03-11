// ── Workflow Monitor — Frontend Application ─────────────────────────────────

const API = '';
let state = {
  tasks: [],
  schedule: [],
  currentBlock: null,
  settings: {},
  selectedTaskId: null,
  todayCompletions: [],
};

// ── Initialization ──────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
  startClock();
  setInterval(loadDashboard, 60000); // refresh every minute
});

async function loadDashboard() {
  try {
    const res = await fetch(`${API}/api/dashboard`);
    const data = await res.json();
    state.tasks = data.tasks;
    state.schedule = data.schedule;
    state.currentBlock = data.current_block;
    state.settings = data.settings;
    state.todayCompletions = data.today_completions || [];

    if (!state.selectedTaskId && state.tasks.length > 0) {
      // Default to current block's task, or first task
      state.selectedTaskId = state.currentBlock?.task_id || state.tasks[0].id;
    }

    renderSchedule();
    renderTasks();
    renderDailyProgress();
    updateModeToggle();
    loadMotivation();
    loadStarChart();
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

// ── Clock ───────────────────────────────────────────────────────────────────

function startClock() {
  const el = document.getElementById('clock');
  function update() {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-US', {
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
    });
  }
  update();
  setInterval(update, 1000);
}

// ── Schedule Rendering ──────────────────────────────────────────────────────

function renderSchedule() {
  const container = document.getElementById('schedule-list');
  const now = new Date();
  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  container.innerHTML = state.schedule.map(block => {
    const [sh, sm] = block.start.split(':').map(Number);
    const [eh, em] = block.end.split(':').map(Number);
    const startMin = sh * 60 + sm;
    const endMin = eh * 60 + em;
    const isPast = currentMinutes >= endMin;
    const isActive = currentMinutes >= startMin && currentMinutes < endMin;
    const isBreak = block.type === 'break';
    const isCall = block.type === 'call';
    const isReview = block.type === 'review';

    const classes = [
      'schedule-block',
      isActive ? 'active' : '',
      isPast ? 'past' : '',
      isBreak ? 'is-break' : '',
      isCall ? 'is-call' : '',
    ].filter(Boolean).join(' ');

    const dotClass = block.type === 'work' ? 'work' :
                     block.type === 'break' ? 'break' :
                     block.type === 'call' ? 'call' : 'review';

    const startFormatted = formatTime(block.start);
    const endFormatted = formatTime(block.end);

    return `
      <div class="${classes}" onclick="selectBlockTask('${block.task_id || ''}')">
        <div class="block-dot ${dotClass}"></div>
        <div class="block-time">${startFormatted}</div>
        <div class="block-info">
          <div class="block-title">${block.task_title}</div>
          <div class="block-category">${startFormatted} – ${endFormatted}</div>
        </div>
      </div>
    `;
  }).join('');

  // Update current block badge
  const badge = document.getElementById('current-block-badge');
  if (state.currentBlock) {
    badge.textContent = state.currentBlock.task_title;
    badge.style.display = 'inline-block';
  } else {
    badge.textContent = 'No active block';
    badge.style.display = 'inline-block';
  }
}

function selectBlockTask(taskId) {
  if (taskId) {
    state.selectedTaskId = taskId;
    renderTasks();
    loadMotivation();
  }
}

function formatTime(timeStr) {
  const [h, m] = timeStr.split(':').map(Number);
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 || 12;
  return `${h12}:${m.toString().padStart(2, '0')} ${ampm}`;
}

// ── Task Rendering ──────────────────────────────────────────────────────────

function renderTasks() {
  const container = document.getElementById('task-cards');

  container.innerHTML = state.tasks.map(task => {
    const isSelected = task.id === state.selectedTaskId;
    const progressPct = Math.round((task.progress || 0) * 100);
    const completed = (task.completed_subtasks || []).length;
    const total = (task.subtasks || []).length;
    const priorityClass = task.priority_score >= 6.5 ? 'priority-high' :
                          task.priority_score >= 5 ? 'priority-medium' : 'priority-low';
    const priorityLabel = task.priority_score >= 6.5 ? 'HIGH' :
                          task.priority_score >= 5 ? 'MEDIUM' : 'LOW';

    const deadlineText = task.deadline
      ? `Deadline: ${new Date(task.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
      : 'No deadline';

    const daysLeft = task.deadline
      ? Math.ceil((new Date(task.deadline) - new Date()) / (1000 * 60 * 60 * 24))
      : null;

    const daysLeftText = daysLeft !== null
      ? (daysLeft > 0 ? `${daysLeft} days left` : 'Past due!')
      : '';

    return `
      <div class="task-card ${isSelected ? 'selected' : ''}" onclick="selectTask('${task.id}')">
        <div class="task-header">
          <div class="task-title">${task.title}</div>
          <span class="task-priority ${priorityClass}">${priorityLabel} ${task.priority_score}</span>
        </div>
        <div class="task-meta">
          <span>${deadlineText}</span>
          ${daysLeftText ? `<span>${daysLeftText}</span>` : ''}
          <span>Cognitive load: ${task.cognitive_load}/10</span>
          <span>${completed}/${total} subtasks</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar" style="width: ${progressPct}%"></div>
        </div>
        ${isSelected ? renderSubtasks(task) : ''}
        ${isSelected ? renderTaskActions(task) : ''}
      </div>
    `;
  }).join('');
}

function renderSubtasks(task) {
  const completedSet = new Set(task.completed_subtasks || []);
  const escId = task.id;
  return `
    <ul class="subtask-list">
      ${(task.subtasks || []).map((st, i) => {
        const isDone = completedSet.has(i);
        const escapedText = st.replace(/'/g, "\\'").replace(/"/g, '&quot;');
        return `
          <li class="subtask-item ${isDone ? 'completed' : ''}" id="subtask-${escId}-${i}">
            <label class="subtask-label" onclick="event.stopPropagation();">
              <input type="checkbox" class="subtask-checkbox-input"
                     ${isDone ? 'checked' : ''}
                     onchange="toggleSubtask('${escId}', ${i}, ${isDone})" />
              <span class="subtask-checkmark"></span>
              <span class="subtask-text">${st}</span>
              <span class="subtask-actions">
                <button class="subtask-action-btn" title="Edit" onclick="event.preventDefault(); startEditSubtask('${escId}', ${i}, '${escapedText}')">&#9998;</button>
                <button class="subtask-action-btn delete" title="Remove" onclick="event.preventDefault(); removeSubtask('${escId}', ${i})">&#10005;</button>
              </span>
            </label>
          </li>
        `;
      }).join('')}
    </ul>
    <div class="add-subtask-row" onclick="event.stopPropagation();">
      <input type="text" class="add-subtask-input" id="add-subtask-input-${escId}"
             placeholder="Add a subtask..." onkeydown="if(event.key==='Enter'){event.preventDefault(); addSubtask('${escId}')}" />
      <button class="add-subtask-btn" onclick="addSubtask('${escId}')">Add</button>
    </div>
  `;
}

function renderTaskActions(task) {
  return `
    <div class="task-actions">
      <button class="btn-sm edit" onclick="event.stopPropagation(); openEditTaskModal('${task.id}')">Edit Task</button>
      <button class="btn-sm delete" onclick="event.stopPropagation(); deleteTaskConfirm('${task.id}')">Delete</button>
      <button class="btn-sm" onclick="event.stopPropagation(); showResources('${task.id}')">Resources</button>
      <button class="btn-sm" onclick="event.stopPropagation(); loadMotivationForTask('${task.id}')">Get Motivated</button>
      <button class="btn-sm" onclick="event.stopPropagation(); showAllFrameworks('${task.id}')">All Frameworks</button>
    </div>
  `;
}

function selectTask(taskId) {
  state.selectedTaskId = taskId;
  renderTasks();
  loadMotivation();
}

async function toggleSubtask(taskId, index, isDone) {
  const endpoint = isDone ? 'uncomplete' : 'complete';
  try {
    const res = await fetch(`${API}/api/tasks/${taskId}/${endpoint}/${index}`, { method: 'POST' });
    const updatedTask = await res.json();
    // Update local state
    const idx = state.tasks.findIndex(t => t.id === taskId);
    if (idx >= 0) {
      state.tasks[idx] = { ...state.tasks[idx], ...updatedTask };
    }
    renderTasks();
    renderDailyProgress();
  } catch (err) {
    console.error('Failed to toggle subtask:', err);
  }
}

// ── Motivation Rendering ────────────────────────────────────────────────────

async function loadMotivation() {
  if (!state.selectedTaskId) return;
  try {
    const res = await fetch(`${API}/api/motivation/${state.selectedTaskId}`);
    const data = await res.json();
    renderMotivationCard(data, 'motivation-content');
  } catch (err) {
    console.error('Failed to load motivation:', err);
  }
}

async function loadMotivationForTask(taskId) {
  state.selectedTaskId = taskId;
  try {
    const res = await fetch(`${API}/api/motivation/${taskId}`);
    const data = await res.json();
    renderMotivationCard(data, 'motivation-content');
    // Switch to motivation tab
    switchTab('motivation');
  } catch (err) {
    console.error('Failed to load motivation:', err);
  }
}

async function refreshMotivation() {
  if (!state.selectedTaskId) return;
  try {
    const res = await fetch(`${API}/api/motivation/${state.selectedTaskId}`);
    const data = await res.json();
    renderMotivationCard(data, 'motivation-content');
  } catch (err) {
    console.error('Failed to refresh motivation:', err);
  }
}

async function showAllFrameworks(taskId) {
  try {
    const res = await fetch(`${API}/api/motivation/${taskId}/all`);
    const data = await res.json();
    const container = document.getElementById('motivation-content');
    if (Array.isArray(data)) {
      container.innerHTML = data.map(m => motivationCardHTML(m)).join('');
    }
    switchTab('motivation');
  } catch (err) {
    console.error('Failed to load all frameworks:', err);
  }
}

async function loadBriefing() {
  try {
    const res = await fetch(`${API}/api/motivation/briefing`);
    const data = await res.json();
    const container = document.getElementById('motivation-content');
    container.innerHTML = data.map(item => `
      <div class="motivation-card">
        <div class="motivation-framework">${item.task_title}</div>
        <div class="task-meta" style="margin-bottom:8px;">
          <span>Progress: ${item.progress} (${item.progress_pct}%)</span>
        </div>
        <div class="motivation-title">${item.motivation.title}</div>
        <div class="motivation-message">${formatMessage(item.motivation.message)}</div>
        <div class="motivation-action">${item.motivation.action}</div>
      </div>
    `).join('');
    switchTab('motivation');
  } catch (err) {
    console.error('Failed to load briefing:', err);
  }
}

function renderMotivationCard(data, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = motivationCardHTML(data);
}

function motivationCardHTML(data) {
  return `
    <div class="motivation-card">
      <div class="motivation-framework">${data.framework || ''}</div>
      <div class="motivation-title">${data.title || ''}</div>
      <div class="motivation-message">${formatMessage(data.message || '')}</div>
      <div class="motivation-principle">${data.principle || ''}</div>
      <div class="motivation-action">${data.action || ''}</div>
    </div>
  `;
}

function formatMessage(msg) {
  // Convert **bold** to <strong>
  return msg.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

// ── Resources ───────────────────────────────────────────────────────────────

async function showResources(taskId) {
  try {
    const res = await fetch(`${API}/api/resources/${taskId}`);
    const data = await res.json();
    const container = document.getElementById('resources-content');
    const resources = data.resources || {};

    let html = '';
    for (const [groupName, items] of Object.entries(resources)) {
      const label = groupName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      html += `<div class="resource-group-title">${label}</div>`;

      if (Array.isArray(items)) {
        html += items.map(item => {
          if (typeof item === 'string') {
            return `<div class="resource-item">${item}</div>`;
          }
          return `
            <div class="resource-item">
              <span class="resource-title">${item.title || item.name || ''}</span>
              ${item.type ? `<span class="resource-type">${item.type}</span>` : ''}
              ${item.url ? `<br><a href="${item.url}" target="_blank" style="color:var(--accent-blue);font-size:12px;">${item.url}</a>` : ''}
              ${item.note ? `<span class="resource-note">${item.note}</span>` : ''}
            </div>
          `;
        }).join('');
      }
    }

    container.innerHTML = html || '<div class="resource-item">No resources curated yet for this task.</div>';
    switchTab('resources');
  } catch (err) {
    console.error('Failed to load resources:', err);
  }
}

// ── Settings ────────────────────────────────────────────────────────────────

async function toggleMode() {
  try {
    const res = await fetch(`${API}/api/settings/toggle-mode`, { method: 'POST' });
    const data = await res.json();
    state.settings.energy_mode = data.energy_mode;
    updateModeToggle();
    loadDashboard(); // Reload to get new schedule
  } catch (err) {
    console.error('Failed to toggle mode:', err);
  }
}

function updateModeToggle() {
  const btn = document.getElementById('mode-toggle');
  const mode = state.settings.energy_mode || 'morning';
  const icon = mode === 'morning' ? '☀️' : '🌙';
  const label = mode === 'morning' ? 'Morning' : 'Night Owl';
  btn.innerHTML = `<span class="mode-icon">${icon}</span> ${label}`;
}

// ── Tab Navigation ──────────────────────────────────────────────────────────

function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.toggle('active', content.id === `tab-${tabName}`);
  });
}

// ── Daily Progress ──────────────────────────────────────────────────────────

function renderDailyProgress() {
  const el = document.getElementById('daily-progress');
  const completedToday = state.todayCompletions.length;
  const totalSubtasks = state.tasks.reduce((sum, t) => sum + (t.subtasks?.length || 0), 0);
  const totalCompleted = state.tasks.reduce((sum, t) => sum + (t.completed_subtasks?.length || 0), 0);
  const overallPct = totalSubtasks > 0 ? Math.round((totalCompleted / totalSubtasks) * 100) : 0;

  el.innerHTML = `
    <div class="stat">
      <span>Today:</span>
      <span class="stat-value">${completedToday} subtasks completed</span>
    </div>
    <div class="stat">
      <span>Overall:</span>
      <span class="stat-value">${totalCompleted}/${totalSubtasks} subtasks (${overallPct}%)</span>
    </div>
    <div class="stat">
      <span>Active tasks:</span>
      <span class="stat-value">${state.tasks.filter(t => t.status === 'active').length}</span>
    </div>
  `;
}

// ── Task CRUD (Add / Edit / Delete) ─────────────────────────────────────────

function openAddTaskModal() {
  document.getElementById('modal-title').textContent = 'Add Task';
  document.getElementById('form-submit-btn').textContent = 'Add Task';
  document.getElementById('form-task-id').value = '';
  document.getElementById('form-title').value = '';
  document.getElementById('form-description').value = '';
  document.getElementById('form-deadline').value = '';
  document.getElementById('form-category').value = 'general';
  document.getElementById('form-urgency').value = '5';
  document.getElementById('form-impact').value = '5';
  document.getElementById('form-cognitive-load').value = '5';
  document.getElementById('form-dependencies').value = '3';
  document.getElementById('task-modal').classList.add('open');
}

function openEditTaskModal(taskId) {
  const task = state.tasks.find(t => t.id === taskId);
  if (!task) return;

  document.getElementById('modal-title').textContent = 'Edit Task';
  document.getElementById('form-submit-btn').textContent = 'Save Changes';
  document.getElementById('form-task-id').value = task.id;
  document.getElementById('form-title').value = task.title;
  document.getElementById('form-description').value = task.description || '';
  document.getElementById('form-deadline').value = task.deadline ? task.deadline.split('T')[0] : '';
  document.getElementById('form-category').value = task.category || 'general';
  document.getElementById('form-urgency').value = task.urgency || 5;
  document.getElementById('form-impact').value = task.impact || 5;
  document.getElementById('form-cognitive-load').value = task.cognitive_load || 5;
  document.getElementById('form-dependencies').value = task.dependencies || 3;
  document.getElementById('task-modal').classList.add('open');
}

function closeTaskModal() {
  document.getElementById('task-modal').classList.remove('open');
}

async function saveTask() {
  const taskId = document.getElementById('form-task-id').value;
  const payload = {
    title: document.getElementById('form-title').value.trim(),
    description: document.getElementById('form-description').value.trim(),
    deadline: document.getElementById('form-deadline').value || null,
    category: document.getElementById('form-category').value,
    urgency: parseInt(document.getElementById('form-urgency').value) || 5,
    impact: parseInt(document.getElementById('form-impact').value) || 5,
    cognitive_load: parseInt(document.getElementById('form-cognitive-load').value) || 5,
    dependencies: parseInt(document.getElementById('form-dependencies').value) || 3,
  };

  if (!payload.title) return;

  try {
    if (taskId) {
      // Edit existing
      await fetch(`${API}/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } else {
      // Create new
      await fetch(`${API}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    }
    closeTaskModal();
    await loadDashboard();
  } catch (err) {
    console.error('Failed to save task:', err);
  }
}

async function deleteTaskConfirm(taskId) {
  const task = state.tasks.find(t => t.id === taskId);
  const name = task ? task.title : taskId;
  if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;

  try {
    await fetch(`${API}/api/tasks/${taskId}`, { method: 'DELETE' });
    if (state.selectedTaskId === taskId) {
      state.selectedTaskId = null;
    }
    await loadDashboard();
  } catch (err) {
    console.error('Failed to delete task:', err);
  }
}

// ── Subtask CRUD (Add / Edit / Remove) ──────────────────────────────────────

async function addSubtask(taskId) {
  const input = document.getElementById(`add-subtask-input-${taskId}`);
  const text = input.value.trim();
  if (!text) return;

  try {
    const res = await fetch(`${API}/api/tasks/${taskId}/subtasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const updatedTask = await res.json();
    updateLocalTask(taskId, updatedTask);
    renderTasks();
    renderDailyProgress();
    // Re-focus the input for quick batch entry
    setTimeout(() => {
      const newInput = document.getElementById(`add-subtask-input-${taskId}`);
      if (newInput) newInput.focus();
    }, 50);
  } catch (err) {
    console.error('Failed to add subtask:', err);
  }
}

function startEditSubtask(taskId, index, currentText) {
  const li = document.getElementById(`subtask-${taskId}-${index}`);
  if (!li) return;

  // Replace the label content with an inline edit input
  li.innerHTML = `
    <div class="subtask-label" onclick="event.stopPropagation();" style="width:100%">
      <input type="text" class="subtask-edit-input" id="edit-subtask-input-${taskId}-${index}"
             value="${currentText.replace(/"/g, '&quot;')}"
             onkeydown="handleEditSubtaskKey(event, '${taskId}', ${index})"
             onblur="commitEditSubtask('${taskId}', ${index})" />
    </div>
  `;
  const inp = document.getElementById(`edit-subtask-input-${taskId}-${index}`);
  if (inp) { inp.focus(); inp.select(); }
}

function handleEditSubtaskKey(event, taskId, index) {
  if (event.key === 'Enter') {
    event.preventDefault();
    commitEditSubtask(taskId, index);
  } else if (event.key === 'Escape') {
    renderTasks(); // Cancel — re-render to restore original
  }
}

async function commitEditSubtask(taskId, index) {
  const inp = document.getElementById(`edit-subtask-input-${taskId}-${index}`);
  if (!inp) return;
  const newText = inp.value.trim();
  if (!newText) {
    renderTasks();
    return;
  }

  // Check if text actually changed
  const task = state.tasks.find(t => t.id === taskId);
  if (task && task.subtasks[index] === newText) {
    renderTasks();
    return;
  }

  try {
    const res = await fetch(`${API}/api/tasks/${taskId}/subtasks/${index}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: newText }),
    });
    const updatedTask = await res.json();
    updateLocalTask(taskId, updatedTask);
    renderTasks();
  } catch (err) {
    console.error('Failed to edit subtask:', err);
    renderTasks();
  }
}

async function removeSubtask(taskId, index) {
  const task = state.tasks.find(t => t.id === taskId);
  const name = task?.subtasks?.[index] || '';
  if (!confirm(`Remove subtask "${name}"?`)) return;

  try {
    const res = await fetch(`${API}/api/tasks/${taskId}/subtasks/${index}`, { method: 'DELETE' });
    const updatedTask = await res.json();
    updateLocalTask(taskId, updatedTask);
    renderTasks();
    renderDailyProgress();
  } catch (err) {
    console.error('Failed to remove subtask:', err);
  }
}

function updateLocalTask(taskId, updatedTask) {
  const idx = state.tasks.findIndex(t => t.id === taskId);
  if (idx >= 0) {
    state.tasks[idx] = { ...state.tasks[idx], ...updatedTask };
  }
}

// ── Star Chart ─────────────────────────────────────────────────────────────

async function loadStarChart() {
  try {
    const res = await fetch(`${API}/api/progress/monthly`);
    const data = await res.json();
    renderStarChart(data);
  } catch (err) {
    console.error('Failed to load star chart:', err);
  }
}

function renderStarChart(data) {
  const grid = document.getElementById('star-chart-grid');
  const title = document.getElementById('star-chart-month');
  title.textContent = `${data.month_name} ${data.year}`;

  const maxCount = data.max_count || 1;

  // Build grid cells: start with empty cells for offset
  let html = '';
  for (let i = 0; i < data.first_weekday; i++) {
    html += '<div class="star-cell empty"></div>';
  }

  data.days.forEach(day => {
    const intensity = day.is_future ? 'future' : getStarIntensity(day.count, maxCount);
    const todayClass = day.is_today ? 'today' : '';
    const tooltip = day.is_future
      ? `${data.month_name} ${day.day}`
      : `${data.month_name} ${day.day}: ${day.count} subtask${day.count !== 1 ? 's' : ''}`;

    html += `
      <div class="star-cell ${todayClass}" title="${tooltip}">
        <div class="star ${intensity}" data-count="${day.count}">&#9733;</div>
        <div class="star-day">${day.day}</div>
      </div>
    `;
  });

  grid.innerHTML = html;
}

function getStarIntensity(count, maxCount) {
  if (count === 0) return 'dim';
  const ratio = count / maxCount;
  if (ratio <= 0.2) return 'low';
  if (ratio <= 0.5) return 'med';
  if (ratio <= 0.8) return 'high';
  return 'max';
}

// ── Nightly Anchor Report ──────────────────────────────────────────────────

let nightlyReportShownToday = false;

function checkNightlyReportTime() {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();

  // Auto-trigger at 10:00 PM (22:00)
  if (hour === 22 && minute === 0 && !nightlyReportShownToday) {
    nightlyReportShownToday = true;
    showNightlyReport();
  }

  // Reset the flag after midnight
  if (hour === 0) {
    nightlyReportShownToday = false;
  }
}

// Check every 30 seconds for report time
setInterval(checkNightlyReportTime, 30000);

async function showNightlyReport() {
  const modal = document.getElementById('nightly-report-modal');
  const body = document.getElementById('nightly-report-body');
  modal.classList.add('open');
  body.innerHTML = '<div class="loading"><span class="loading-dot">Generating your nightly anchor...</span></div>';

  try {
    const res = await fetch(`${API}/api/report/nightly`);
    const report = await res.json();
    body.innerHTML = renderNightlyReport(report);
  } catch (err) {
    console.error('Failed to load nightly report:', err);
    body.innerHTML = '<div class="loading">Failed to generate report. Try again.</div>';
  }
}

function closeNightlyReport() {
  document.getElementById('nightly-report-modal').classList.remove('open');
  document.getElementById('nightly-report-title').textContent = 'Your Nightly Anchor';
}

function renderNightlyReport(report) {
  const { summary, wins, tactical_reframes, tomorrow_plan, anchor } = report;

  // Determine summary tone styling
  const toneClass = `summary-${summary.tone}`;

  let html = '';

  // ── Summary Section
  html += `
    <div class="report-section report-summary ${toneClass}">
      <div class="report-summary-headline">${summary.headline}</div>
      <div class="report-summary-detail">${summary.detail}</div>
    </div>
  `;

  // ── Wins Section
  html += `<div class="report-section">`;
  html += `<div class="report-section-title"><span class="report-icon">&#9733;</span> Today's Wins</div>`;
  html += `<div class="report-section-message">${wins.message}</div>`;

  if (wins.has_wins && wins.items.length > 0) {
    wins.items.forEach(item => {
      html += `
        <div class="report-win-card">
          <div class="report-win-header">
            <span class="report-win-task">${item.task_title}</span>
            <span class="report-win-count">${item.count_today} completed</span>
          </div>
          <div class="report-win-progress">Overall: ${item.overall_progress}</div>
          <ul class="report-win-list">
            ${item.completed_today.map(st => `<li>${st}</li>`).join('')}
          </ul>
        </div>
      `;
    });
  }
  html += `</div>`;

  // ── Tactical Reframes Section
  html += `<div class="report-section">`;
  html += `<div class="report-section-title"><span class="report-icon">&#9881;</span> Tactical Reframes</div>`;
  html += `<div class="report-section-message">${tactical_reframes.message}</div>`;

  if (tactical_reframes.has_misses && tactical_reframes.items.length > 0) {
    tactical_reframes.items.forEach(item => {
      html += `
        <div class="report-reframe-card">
          <div class="report-reframe-task">${item.task_title}</div>
          <div class="report-reframe-text">${item.reframe}</div>
          <div class="report-reframe-action">
            <strong>Tomorrow:</strong> ${item.tomorrow_action}
          </div>
          ${item.next_subtask ? `<div class="report-reframe-next">Next up: "${item.next_subtask}" (${item.total_remaining} remaining)</div>` : ''}
        </div>
      `;
    });
  }
  html += `</div>`;

  // ── Tomorrow's Plan
  html += `<div class="report-section">`;
  html += `<div class="report-section-title"><span class="report-icon">&#9654;</span> Tomorrow's Game Plan</div>`;

  if (tomorrow_plan.plan_items.length > 0) {
    tomorrow_plan.plan_items.forEach(item => {
      const icon = item.type === 'momentum' ? '&#9889;' : '&#9888;';
      const typeLabel = item.type === 'momentum' ? 'MOMENTUM' : 'NEEDS ATTENTION';
      html += `
        <div class="report-plan-card ${item.type}">
          <div class="report-plan-header">
            <span class="report-plan-icon">${icon}</span>
            <span class="report-plan-type">${typeLabel}</span>
          </div>
          <div class="report-plan-title">${item.title}</div>
          <div class="report-plan-rationale">${item.rationale}</div>
          ${item.suggested_subtasks.length > 0 ? `
            <div class="report-plan-subtasks">
              <strong>Start with:</strong>
              <ul>${item.suggested_subtasks.map(s => `<li>${s}</li>`).join('')}</ul>
            </div>
          ` : ''}
        </div>
      `;
    });
  }

  if (tomorrow_plan.implementation_intention) {
    html += `
      <div class="report-intention">
        <div class="report-intention-label">Your Implementation Intention</div>
        <div class="report-intention-text">"${tomorrow_plan.implementation_intention}"</div>
        <div class="report-intention-principle">${tomorrow_plan.principle}</div>
      </div>
    `;
  }
  html += `</div>`;

  // ── Broader Outlook Section
  if (report.broader_outlook) {
    const outlook = report.broader_outlook;
    html += `<div class="report-section">`;
    html += `<div class="report-section-title"><span class="report-icon">&#9670;</span> Broader Outlook</div>`;
    html += `<div class="report-section-message">${outlook.message}</div>`;

    // Streak badge
    if (outlook.streak > 0) {
      html += `
        <div class="report-streak">
          <span class="report-streak-number">${outlook.streak}</span>
          <span class="report-streak-label">day streak</span>
        </div>
      `;
    }

    // Consistency note
    if (outlook.consistency_note) {
      html += `<div class="report-consistency">${outlook.consistency_note}</div>`;
    }

    // Daily counts mini chart
    if (outlook.has_history && outlook.daily_counts && outlook.daily_counts.length > 1) {
      const maxCount = Math.max(...outlook.daily_counts.map(d => d.count), 1);
      html += `<div class="report-chart">`;
      html += `<div class="report-chart-label">Completions per day</div>`;
      html += `<div class="report-chart-bars">`;
      outlook.daily_counts.forEach(d => {
        const height = Math.max((d.count / maxCount) * 60, 4);
        const dayLabel = d.date.slice(5); // MM-DD
        html += `
          <div class="report-chart-col">
            <div class="report-chart-count">${d.count}</div>
            <div class="report-chart-bar" style="height:${height}px"></div>
            <div class="report-chart-date">${dayLabel}</div>
          </div>
        `;
      });
      html += `</div></div>`;
    }

    // Task coverage
    if (outlook.has_history && outlook.task_coverage && outlook.task_coverage.length > 0) {
      html += `<div class="report-coverage-title">Task coverage (last ${outlook.daily_counts?.length || '?'} days)</div>`;
      outlook.task_coverage.forEach(tc => {
        html += `
          <div class="report-coverage-row">
            <span class="report-coverage-task">${tc.task_title}</span>
            <div class="report-coverage-bar-bg">
              <div class="report-coverage-bar-fill" style="width:${tc.coverage_pct}%"></div>
            </div>
            <span class="report-coverage-pct">${tc.days_active}/${tc.total_days} days</span>
          </div>
        `;
      });
    }

    html += `</div>`;
  }

  // ── Anchor Quote
  html += `
    <div class="report-section report-anchor">
      <div class="report-anchor-quote">"${anchor.quote}"</div>
      <div class="report-anchor-author">— ${anchor.author}</div>
      <div class="report-anchor-reflection">${anchor.reflection}</div>
    </div>
  `;

  // ── Sleep well footer
  html += `
    <div class="report-footer">
      Rest well. Tomorrow you start again — stronger, clearer, and one day closer.
    </div>
  `;

  return html;
}

// ── Report History ─────────────────────────────────────────────────────────

async function showReportHistory() {
  const modal = document.getElementById('nightly-report-modal');
  const body = document.getElementById('nightly-report-body');
  const title = document.getElementById('nightly-report-title');
  title.textContent = 'Past Reports';
  modal.classList.add('open');
  body.innerHTML = '<div class="loading"><span class="loading-dot">Loading history...</span></div>';

  try {
    const res = await fetch(`${API}/api/report/history`);
    const reports = await res.json();

    if (!reports || reports.length === 0) {
      body.innerHTML = `
        <div class="report-section">
          <div class="report-section-message">No saved reports yet. Your first report will be saved when you generate one.</div>
        </div>
      `;
      return;
    }

    let html = `
      <div class="report-history-header">
        <span>${reports.length} saved report${reports.length !== 1 ? 's' : ''} (max 5)</span>
        <button class="report-wipe-btn" onclick="wipeReports()">Wipe All Reports</button>
      </div>
    `;

    // Show reports in reverse chronological order
    const sorted = [...reports].reverse();
    sorted.forEach((report, idx) => {
      const reportDate = new Date(report.date + 'T00:00:00');
      const dateStr = reportDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
      const summary = report.summary || {};
      const wins = report.wins || {};
      const winCount = wins.has_wins ? wins.items.reduce((s, i) => s + i.count_today, 0) : 0;
      const toneClass = `summary-${summary.tone || 'gentle'}`;

      html += `
        <div class="report-history-card" onclick="toggleHistoryDetail(this)">
          <div class="report-history-summary ${toneClass}">
            <div class="report-history-date">${dateStr}</div>
            <div class="report-history-headline">${summary.headline || 'No summary'}</div>
            <div class="report-history-stats">
              <span>${winCount} subtask${winCount !== 1 ? 's' : ''} completed</span>
              ${report.broader_outlook?.streak ? `<span>Streak: ${report.broader_outlook.streak}</span>` : ''}
            </div>
          </div>
          <div class="report-history-detail" style="display:none">
            ${renderNightlyReport(report)}
          </div>
        </div>
      `;
    });

    body.innerHTML = html;
  } catch (err) {
    console.error('Failed to load report history:', err);
    body.innerHTML = '<div class="loading">Failed to load history.</div>';
  }
}

function toggleHistoryDetail(card) {
  const detail = card.querySelector('.report-history-detail');
  if (detail) {
    const isHidden = detail.style.display === 'none';
    detail.style.display = isHidden ? 'block' : 'none';
  }
}

async function wipeReports() {
  if (!confirm('Wipe all saved reports? This cannot be undone.')) return;

  try {
    await fetch(`${API}/api/report/wipe`, { method: 'POST' });
    showReportHistory(); // Refresh the view
  } catch (err) {
    console.error('Failed to wipe reports:', err);
  }
}

function closeNightlyReportAndReset() {
  document.getElementById('nightly-report-modal').classList.remove('open');
  document.getElementById('nightly-report-title').textContent = 'Your Nightly Anchor';
}
