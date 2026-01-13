// 导入任务数据
import TASKS from './tasks.js';

// 全局状态
let allTasks = [];
let filteredTasks = [];
let expandedSteps = new Set();

// DOM 元素
const mainContent = document.getElementById('mainContent');
const searchInput = document.getElementById('searchInput');
const stepFilter = document.getElementById('stepFilter');
const toggleAllBtn = document.getElementById('toggleAllBtn');
const toast = document.getElementById('toast');

// 任务数据映射（用于快速查找）
const tasksMap = new Map();

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    allTasks = TASKS;
    filteredTasks = [...allTasks];
    
    // 建立任务映射
    allTasks.forEach(task => {
        tasksMap.set(task.ticket_id, task);
    });
    
    // 初始化步骤过滤器选项
    initStepFilter();
    
    // 默认展开所有步骤
    const steps = [...new Set(allTasks.map(t => t.step))];
    steps.forEach(step => expandedSteps.add(step));
    
    // 渲染任务列表
    renderTasks();
    
    // 绑定事件
    searchInput.addEventListener('input', handleSearch);
    stepFilter.addEventListener('change', handleStepFilter);
    toggleAllBtn.addEventListener('click', handleToggleAll);
    
    // 事件委托处理按钮点击
    mainContent.addEventListener('click', handleCardClick);
});

// 初始化步骤过滤器
function initStepFilter() {
    const steps = [...new Set(allTasks.map(t => t.step))].sort();
    steps.forEach(step => {
        const option = document.createElement('option');
        option.value = step;
        option.textContent = step;
        stepFilter.appendChild(option);
    });
}

// 搜索处理
function handleSearch() {
    const query = searchInput.value.toLowerCase().trim();
    filterTasks(query, stepFilter.value);
}

// 步骤过滤处理
function handleStepFilter() {
    const query = searchInput.value.toLowerCase().trim();
    filterTasks(query, stepFilter.value);
}

// 过滤任务
function filterTasks(query, stepFilterValue) {
    filteredTasks = allTasks.filter(task => {
        // 步骤过滤
        if (stepFilterValue !== 'ALL' && task.step !== stepFilterValue) {
            return false;
        }
        
        // 搜索过滤
        if (!query) {
            return true;
        }
        
        const searchText = [
            task.title,
            task.goal,
            task.status || '',
            task.llm_note || '',
            ...task.definition_of_done
        ].join(' ').toLowerCase();
        
        return searchText.includes(query);
    });
    
    renderTasks();
}

// 切换全部展开/折叠
function handleToggleAll() {
    const steps = [...new Set(filteredTasks.map(t => t.step))];
    const allExpanded = steps.every(step => expandedSteps.has(step));
    
    if (allExpanded) {
        expandedSteps.clear();
    } else {
        steps.forEach(step => expandedSteps.add(step));
    }
    
    renderTasks();
}

// 处理卡片点击事件（事件委托）
function handleCardClick(e) {
    const target = e.target;
    
    // 切换步骤展开/折叠
    if (target.closest('.step-header')) {
        const stepHeader = target.closest('.step-header');
        const stepAccordion = stepHeader.closest('.step-accordion');
        const step = stepAccordion.getAttribute('data-step');
        toggleStep(step);
        return;
    }
}

// 切换步骤展开/折叠
function toggleStep(step) {
    if (expandedSteps.has(step)) {
        expandedSteps.delete(step);
    } else {
        expandedSteps.add(step);
    }
    renderTasks();
}


// 显示 Toast
function showToast(message) {
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// 渲染任务列表
function renderTasks() {
    if (filteredTasks.length === 0) {
        mainContent.innerHTML = `
            <div class="empty-state">
                <p>🔍 没有找到匹配的任务</p>
                <p>请尝试调整搜索条件或步骤筛选</p>
            </div>
        `;
        return;
    }
    
    // 按步骤分组
    const tasksByStep = {};
    filteredTasks.forEach(task => {
        if (!tasksByStep[task.step]) {
            tasksByStep[task.step] = [];
        }
        tasksByStep[task.step].push(task);
    });
    
    // 渲染步骤
    const steps = Object.keys(tasksByStep).sort();
    const html = steps.map(step => {
        const tasks = tasksByStep[step];
        const isExpanded = expandedSteps.has(step);
        const toggleIcon = isExpanded ? '▼' : '▶';
        
        // 获取第一个任务作为step的代表（通常每个step只有一个任务）
        const stepTask = tasks[0];
        const stepTitle = stepTask ? escapeHtml(stepTask.title) : '';
        const stepGoal = stepTask ? escapeHtml(stepTask.goal) : '';
        
        return `
            <div class="step-accordion" data-step="${escapeHtml(step)}">
                <div class="step-header">
                    <div class="step-header-left">
                        <h2>${escapeHtml(step)}</h2>
                        ${!isExpanded ? `
                            <div class="step-collapsed-info">
                                <span class="step-title">${stepTitle}</span>
                                <span class="step-goal">目标：${stepGoal}</span>
                            </div>
                        ` : ''}
                    </div>
                    <span class="step-toggle ${isExpanded ? '' : 'collapsed'}">${toggleIcon}</span>
                </div>
                <div class="step-content ${isExpanded ? 'expanded' : ''}">
                    ${tasks.map(task => renderTicketCard(task)).join('')}
                </div>
            </div>
        `;
    }).join('');
    
    mainContent.innerHTML = html;
}

// 渲染任务卡片
function renderTicketCard(task) {
    const dodList = task.definition_of_done.map(item => 
        `<li>${escapeHtml(item)}</li>`
    ).join('');
    
    // 状态标签样式
    const statusClass = {
        '已完成': 'status-completed',
        '部分完成': 'status-partial',
        '未完成': 'status-pending',
        '预留': 'status-reserved'
    }[task.status] || 'status-default';
    
    return `
        <div class="ticket-card">
            <div class="ticket-header">
                <span class="ticket-id">${escapeHtml(task.ticket_id)}</span>
                <h3 class="ticket-title">${escapeHtml(task.title)}</h3>
                <span class="ticket-status ${statusClass}">${escapeHtml(task.status || '未知')}</span>
            </div>
            
            <div class="ticket-goal">
                <strong>目标：</strong>${escapeHtml(task.goal)}
            </div>
            
            <div class="ticket-dod">
                <h4>任务拆分：</h4>
                <ul>${dodList}</ul>
            </div>
            
            ${task.llm_note ? `
            <div class="ticket-llm-note">
                <h4>LLM 接入说明：</h4>
                <div class="llm-note-content">${escapeHtml(task.llm_note)}</div>
            </div>
            ` : ''}
        </div>
    `;
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
