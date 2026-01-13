// 前端应用逻辑

const messagesContainer = document.getElementById('messages');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const suggestionsContainer = document.getElementById('suggestions');
const suggestionsChipContainer = document.getElementById('suggestions-container');

// 所有可用的下钻卡片定义
const ALL_DRILL_CARDS = [
    { id: 'C1', title: '旅程阶段断点下钻', description: '查看 compare→decide、decide→purchase 的边转化/流失', level: 'L1' },
    { id: 'C2', title: '渠道下钻', description: '按渠道查看 decide→purchase 断点', level: 'L1' },
    { id: 'C3', title: '购买决策细分下钻', description: '分析"进入决策阶段但未购买"用户的两类问题：无效浏览过多、列表无点击', level: 'L2' },
    { id: 'C31', title: '无效页面名称下钻', description: '查看Top无效页面，用于UI调整/删除页面', level: 'L3' },
    { id: 'C32', title: '未点击商品用户偏好下钻', description: '分析"到达列表页但未点击商品"用户的历史购买偏好', level: 'L3' }
];

// 跟踪已点击的下钻按钮
const clickedDrillCards = new Set();

// 处理 401 未授权错误
function handleUnauthorized(response) {
    if (response.status === 401) {
        // 跳转到登录页面
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        return true;
    }
    return false;
}

// 加载建议问题
async function loadSuggestions() {
    try {
        const response = await fetch('/api/suggestions');
        if (handleUnauthorized(response)) return;
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const suggestions = await response.json();
        
        suggestionsContainer.innerHTML = '';
        suggestions.forEach(suggestion => {
            const chip = document.createElement('button');
            chip.className = 'suggestion-chip';
            chip.textContent = suggestion;
            chip.onclick = () => sendMessage(suggestion);
            suggestionsContainer.appendChild(chip);
        });
    } catch (error) {
        console.error('加载建议问题失败:', error);
    }
}

// 发送消息
async function sendMessage(text) {
    if (!text.trim()) return;
    
    // 添加用户消息
    addMessage(text, 'user');
    
    // 建议问题保持显示，用户可以继续点击
    
    // 禁用输入
    input.disabled = true;
    sendBtn.disabled = true;
    
    try {
        // 发送请求
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: text })
        });
        
        if (handleUnauthorized(response)) return;
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 显示智能体回复
        addAgentMessage(data);
        
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage('抱歉，发生了错误，请稍后重试。', 'agent');
    } finally {
        // 恢复输入
        input.disabled = false;
        sendBtn.disabled = false;
        input.value = '';
        input.focus();
    }
}

// 下钻请求
async function drillDown(cardId) {
    console.log('drillDown called with cardId:', cardId);  // 调试信息
    
    // 记录已点击的下钻按钮
    clickedDrillCards.add(cardId);
    
    try {
        const response = await fetch('/api/drill', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ card_id: cardId })
        });
        
        if (handleUnauthorized(response)) return;
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('drillDown received data:', data);  // 调试信息
        console.log('drillDown - actions存在?', 'actions' in data, data.actions);  // 详细调试
        console.log('drillDown - next_drill_cards存在?', 'next_drill_cards' in data, data.next_drill_cards);  // 详细调试
        
        // 添加下钻结果
        addDrillResult(data);
        
    } catch (error) {
        console.error('下钻请求失败:', error);
        addMessage('抱歉，下钻请求失败，请稍后重试。', 'agent');
    }
}

// 获取层级数值（用于比较层级高低）
function getLevelNumber(level) {
    const levelMap = { 'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3 };
    return levelMap[level] || 999;
}

// 获取未点击的下钻卡片
function getUnclickedDrillCards(currentLevel, displayedCardIds = []) {
    return ALL_DRILL_CARDS.filter(card => {
        // 排除已点击的
        if (clickedDrillCards.has(card.id)) {
            return false;
        }
        // 排除当前结论卡已显示的下钻按钮
        if (displayedCardIds.includes(card.id)) {
            return false;
        }
        // 仅展示上几层的按钮（当前层级之前的层级，或同层级）
        const currentLevelNum = getLevelNumber(currentLevel);
        const cardLevelNum = getLevelNumber(card.level);
        // 显示层级小于当前层级的卡片，或者同层级的卡片（用于L1显示其他L1卡片）
        if (cardLevelNum > currentLevelNum) {
            return false;
        }
        return true;
    });
}

// 添加未点击下钻按钮提示模块
function addUnclickedDrillCardsPrompt(parentElement, currentLevel, displayedCardIds = []) {
    // L0不显示提示
    if (currentLevel === 'L0' || !currentLevel) {
        return;
    }
    
    const unclickedCards = getUnclickedDrillCards(currentLevel, displayedCardIds);
    
    // 如果所有下钻按钮都已点击，不显示提示
    if (unclickedCards.length === 0) {
        return;
    }
    
    // 最多展示3个
    const cardsToShow = unclickedCards.slice(0, 3);
    
    const promptDiv = document.createElement('div');
    promptDiv.className = 'unclicked-drill-prompt';
    promptDiv.style.marginTop = '15px';
    
    // 模块标题：黑色字，字号小一些
    const promptTitle = document.createElement('div');
    promptTitle.style.fontWeight = 'bold';
    promptTitle.style.marginBottom = '8px';
    promptTitle.style.color = '#000000';
    promptTitle.style.fontSize = '13px';
    promptTitle.textContent = '您还可以进行其它下钻分析：';
    promptDiv.appendChild(promptTitle);
    
    // 创建单列表格样式（无表头）
    const table = document.createElement('table');
    table.className = 'unclicked-drill-table';
    table.style.width = '100%';
    table.style.borderCollapse = 'separate';
    table.style.borderSpacing = '0';
    table.style.marginTop = '4px';
    table.style.border = '1px solid #d0d0d0'; // 表格外边框：比填充色浅的灰色
    
    // 表体（单列）
    const tbody = document.createElement('tbody');
    const fillColor = '#e0e0e0'; // 浅灰色填充
    const borderColor = '#d0d0d0'; // 边框色：比填充色浅的灰色
    const hoverColor = '#f0f0f0'; // 悬停时的颜色
    
    cardsToShow.forEach((card, index) => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';
        row.style.backgroundColor = fillColor;
        row.setAttribute('data-card-id', card.id);
        row.onmouseover = () => {
            row.style.backgroundColor = hoverColor;
        };
        row.onmouseout = () => {
            row.style.backgroundColor = fillColor;
        };
        row.onclick = () => {
            drillDown(card.id);
        };
        
        const td = document.createElement('td');
        td.style.padding = '8px 12px';
        td.style.color = '#000000'; // 黑色文字
        td.style.fontSize = '13px'; // 字号大1号（从12px改为13px）
        td.style.borderTop = index === 0 ? 'none' : `1px solid ${borderColor}`; // 第一行无上边框，其他行有
        td.style.borderLeft = `1px solid ${borderColor}`; // 左边框
        td.style.borderRight = `1px solid ${borderColor}`; // 右边框
        td.style.borderBottom = index === cardsToShow.length - 1 ? 'none' : `1px solid ${borderColor}`; // 最后一行无下边框，其他行有
        td.textContent = `${card.title}：${card.description}  →`;
        
        row.appendChild(td);
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    promptDiv.appendChild(table);
    parentElement.appendChild(promptDiv);
}

// 添加消息
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加智能体消息（L0结论卡）
function addAgentMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-agent';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 结论卡
    const conclusionCard = document.createElement('div');
    conclusionCard.className = 'conclusion-card';
    
    const title = document.createElement('h3');
    title.textContent = '结论';
    
    const conclusion = document.createElement('div');
    conclusion.className = 'conclusion';
    conclusion.textContent = data.conclusion;
    
    conclusionCard.appendChild(title);
    conclusionCard.appendChild(conclusion);
    
    // 证据
    if (data.evidence && data.evidence.length > 0) {
        const evidenceDiv = document.createElement('div');
        evidenceDiv.className = 'evidence';
        data.evidence.forEach(ev => {
            const item = document.createElement('div');
            item.className = 'evidence-item';
            item.textContent = ev;
            evidenceDiv.appendChild(item);
        });
        conclusionCard.appendChild(evidenceDiv);
    }
    
    // 行动建议（兼容数组和对象两种格式）
    if (data.actions) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'actions';
        actionsDiv.style.marginTop = '15px';
        
        if (Array.isArray(data.actions)) {
            // 旧格式：数组
            data.actions.forEach(action => {
                const item = document.createElement('div');
                item.className = 'action-item';
                item.textContent = action;
                actionsDiv.appendChild(item);
            });
        } else if (typeof data.actions === 'object') {
            // 新格式：对象（ui_actions, audience_building, merch_strategy）
            if (data.actions.ui_actions && data.actions.ui_actions.length > 0) {
                const uiTitle = document.createElement('div');
                uiTitle.className = 'action-section-title';
                uiTitle.textContent = 'UI策略：';
                actionsDiv.appendChild(uiTitle);
                data.actions.ui_actions.forEach(action => {
                    const item = document.createElement('div');
                    item.className = 'action-item';
                    item.textContent = action;
                    actionsDiv.appendChild(item);
                });
            }
            
            if (data.actions.audience_building && Object.keys(data.actions.audience_building).length > 0) {
                const audTitle = document.createElement('div');
                audTitle.className = 'action-section-title';
                audTitle.textContent = '人群策略（筛选条件）：';
                actionsDiv.appendChild(audTitle);
                const audItem = document.createElement('div');
                audItem.className = 'action-item';
                audItem.textContent = JSON.stringify(data.actions.audience_building, null, 2);
                actionsDiv.appendChild(audItem);
            }
            
            if (data.actions.merch_strategy && Object.keys(data.actions.merch_strategy).length > 0) {
                const merchTitle = document.createElement('div');
                merchTitle.className = 'action-section-title';
                merchTitle.textContent = '商品策略：';
                actionsDiv.appendChild(merchTitle);
                const merchItem = document.createElement('div');
                merchItem.className = 'action-item';
                if (data.actions.merch_strategy.strategy) {
                    merchItem.textContent = `优先展示：${data.actions.merch_strategy.category}类目，商品：${data.actions.merch_strategy.items.join(', ')}`;
                } else {
                    merchItem.textContent = JSON.stringify(data.actions.merch_strategy, null, 2);
                }
                actionsDiv.appendChild(merchItem);
            }
        }
        
        if (actionsDiv.children.length > 0) {
            conclusionCard.appendChild(actionsDiv);
        }
    }
    
    contentDiv.appendChild(conclusionCard);
    
    // 收集已显示的下钻卡片ID
    const displayedCardIds = [];
    
    // 下钻卡
    if (data.drill_cards && data.drill_cards.length > 0) {
        const drillCardsDiv = document.createElement('div');
        drillCardsDiv.className = 'drill-cards';
        
        data.drill_cards.forEach(card => {
            displayedCardIds.push(card.id);
            
            const cardBtn = document.createElement('button');
            cardBtn.className = 'drill-card';
            cardBtn.setAttribute('data-card-id', card.id);  // 使用data属性，不绑定onclick
            
            const title = document.createElement('div');
            title.className = 'drill-card-title';
            title.textContent = card.title;
            
            const desc = document.createElement('div');
            desc.className = 'drill-card-desc';
            desc.textContent = card.description;
            
            cardBtn.appendChild(title);
            cardBtn.appendChild(desc);
            drillCardsDiv.appendChild(cardBtn);
        });
        
        contentDiv.appendChild(drillCardsDiv);
    }
    
    // 添加未点击下钻按钮提示模块（L0不显示）
    const currentLevel = data.level || 'L0';
    addUnclickedDrillCardsPrompt(contentDiv, currentLevel, displayedCardIds);
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加下钻结果（L1/L2）
function addDrillResult(data) {
    console.log('addDrillResult called with data:', data);  // 调试信息
    console.log('addDrillResult - data类型:', typeof data);  // 调试信息
    console.log('addDrillResult - data.keys:', Object.keys(data));  // 调试信息
    console.log('addDrillResult - actions存在?', 'actions' in data, data?.actions);  // 详细调试
    console.log('addDrillResult - next_drill_cards存在?', 'next_drill_cards' in data, data?.next_drill_cards);  // 详细调试
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-agent';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 下钻结果
    const drillResult = document.createElement('div');
    drillResult.className = 'drill-result';
    
    const title = document.createElement('h3');
    title.textContent = data.drill.title;
    
    const conclusion = document.createElement('div');
    conclusion.className = 'conclusion';
    conclusion.style.marginBottom = '15px';
    conclusion.style.lineHeight = '1.6';
    conclusion.style.whiteSpace = 'pre-line';  // 支持换行
    conclusion.textContent = data.conclusion;
    
    drillResult.appendChild(title);
    drillResult.appendChild(conclusion);
    
    // 证据
    if (data.evidence && data.evidence.length > 0) {
        const evidenceDiv = document.createElement('div');
        evidenceDiv.className = 'evidence';
        evidenceDiv.style.marginTop = '10px';
        data.evidence.forEach(ev => {
            const item = document.createElement('div');
            item.className = 'evidence-item';
            item.style.marginBottom = '5px';
            item.textContent = ev;
            evidenceDiv.appendChild(item);
        });
        drillResult.appendChild(evidenceDiv);
    }
    
    // 运营策略（如果有）
    console.log('检查actions:', 'actions' in data, data.actions);  // 详细调试
    if (data.actions) {
        console.log('Processing actions:', data.actions);  // 调试信息
        const cardId = data.drill && data.drill.card_id ? data.drill.card_id : '';
        const isC3 = cardId === 'C3';
        const isC32 = cardId === 'C32';
        
        let hasContent = false;
        
        // 检查是否有任何策略内容
        // C3不显示商品策略，C32显示商品策略
        if ((data.actions.ui_actions && data.actions.ui_actions.length > 0) ||
            (data.actions.audience_building && Object.keys(data.actions.audience_building).length > 0) ||
            (data.actions.merch_strategy && Object.keys(data.actions.merch_strategy).length > 0 && 
             !isC3 && data.actions.merch_strategy.strategy && !data.actions.merch_strategy.note)) {
            hasContent = true;
        }
        
        if (hasContent) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'actions';
            actionsDiv.style.marginTop = '15px';
            actionsDiv.style.padding = '15px';
            actionsDiv.style.backgroundColor = '#f0f8ff';
            actionsDiv.style.borderRadius = '5px';
            actionsDiv.style.border = '1px solid #d0e8ff';
            
            // 添加"运营策略建议"标题
            const mainTitle = document.createElement('div');
            mainTitle.className = 'actions-main-title';
            mainTitle.style.fontWeight = 'bold';
            mainTitle.style.fontSize = '16px';
            mainTitle.style.marginBottom = '15px';
            mainTitle.style.color = '#333';
            mainTitle.textContent = '运营策略建议';
            actionsDiv.appendChild(mainTitle);
            
            // UI策略
            if (data.actions.ui_actions && data.actions.ui_actions.length > 0) {
                const uiTitle = document.createElement('div');
                uiTitle.className = 'action-section-title';
                uiTitle.style.fontWeight = 'bold';
                uiTitle.style.marginTop = '10px';
                uiTitle.style.marginBottom = '5px';
                uiTitle.textContent = 'UI策略：';
                actionsDiv.appendChild(uiTitle);
                data.actions.ui_actions.forEach(action => {
                    const item = document.createElement('div');
                    item.className = 'action-item';
                    item.style.marginLeft = '15px';
                    item.style.marginBottom = '5px';
                    item.textContent = action;
                    actionsDiv.appendChild(item);
                });
            }
            
            // 人群策略
            if (data.actions.audience_building && Object.keys(data.actions.audience_building).length > 0) {
                const audTitle = document.createElement('div');
                audTitle.className = 'action-section-title';
                audTitle.style.fontWeight = 'bold';
                audTitle.style.marginTop = '10px';
                audTitle.style.marginBottom = '5px';
                audTitle.textContent = '人群策略：';
                actionsDiv.appendChild(audTitle);
                
                // 添加自然语言描述
                const desc = document.createElement('div');
                desc.style.marginLeft = '15px';
                desc.style.marginBottom = '8px';
                desc.style.color = '#555';
                desc.textContent = '建议下钻未点击商品用户的商品偏好，人群圈选规则为：';
                actionsDiv.appendChild(desc);
                
                // 创建筛选条件表格
                const tableWrapper = document.createElement('div');
                tableWrapper.style.marginLeft = '15px';
                tableWrapper.style.marginBottom = '10px';
                
                const table = document.createElement('table');
                table.className = 'filter-table';
                table.style.width = '100%';
                table.style.borderCollapse = 'collapse';
                table.style.marginBottom = '10px';
                
                // 表头
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                headerRow.style.backgroundColor = '#e3f2fd';
                headerRow.style.fontWeight = 'bold';
                
                const th1 = document.createElement('th');
                th1.style.padding = '8px 12px';
                th1.style.textAlign = 'left';
                th1.style.border = '1px solid #bbdefb';
                th1.textContent = '筛选属性名称';
                
                const th2 = document.createElement('th');
                th2.style.padding = '8px 12px';
                th2.style.textAlign = 'left';
                th2.style.border = '1px solid #bbdefb';
                th2.textContent = '属性值';
                
                headerRow.appendChild(th1);
                headerRow.appendChild(th2);
                thead.appendChild(headerRow);
                table.appendChild(thead);
                
                // 表体
                const tbody = document.createElement('tbody');
                const filters = data.actions.audience_building;
                
                // 筛选条件映射（中文名称）
                const filterNameMap = {
                    'period': '时间周期',
                    'journey_id': '旅程ID',
                    'in_decide': '进入决策阶段',
                    'no_purchase': '未完成购买',
                    'reached_category': '到达列表页',
                    'item_click': '商品点击',
                    'audience_size': '人群规模'
                };
                
                // 属性值映射（中文显示）
                const filterValueMap = {
                    '1': '是',
                    '0': '否',
                    'curr_7d': '最近7天',
                    'prev_7d': '上7天',
                    'J_BUY': '购买旅程'
                };
                
                Object.keys(filters).forEach(key => {
                    const row = document.createElement('tr');
                    
                    const td1 = document.createElement('td');
                    td1.style.padding = '8px 12px';
                    td1.style.border = '1px solid #e0e0e0';
                    td1.style.backgroundColor = '#fff';
                    td1.textContent = filterNameMap[key] || key;
                    
                    const td2 = document.createElement('td');
                    td2.style.padding = '8px 12px';
                    td2.style.border = '1px solid #e0e0e0';
                    td2.style.backgroundColor = '#fff';
                    const value = filters[key];
                    td2.textContent = filterValueMap[value] !== undefined ? filterValueMap[value] : value;
                    
                    row.appendChild(td1);
                    row.appendChild(td2);
                    tbody.appendChild(row);
                });
                
                table.appendChild(tbody);
                tableWrapper.appendChild(table);
                
                // 添加"创建人群包"按钮
                const createBtn = document.createElement('button');
                createBtn.className = 'create-audience-btn';
                createBtn.textContent = '创建人群包';
                createBtn.style.padding = '6px 16px';
                createBtn.style.marginTop = '5px';
                createBtn.style.backgroundColor = '#667eea';
                createBtn.style.color = 'white';
                createBtn.style.border = 'none';
                createBtn.style.borderRadius = '4px';
                createBtn.style.cursor = 'pointer';
                createBtn.style.fontSize = '14px';
                createBtn.style.fontWeight = '500';
                createBtn.style.transition = 'background-color 0.2s';
                createBtn.onmouseover = () => createBtn.style.backgroundColor = '#5568d3';
                createBtn.onmouseout = () => createBtn.style.backgroundColor = '#667eea';
                
                tableWrapper.appendChild(createBtn);
                actionsDiv.appendChild(tableWrapper);
            }
            
            // 商品策略（仅在C32显示，C3不显示）
            if (!isC3 && data.actions.merch_strategy && Object.keys(data.actions.merch_strategy).length > 0 && 
                data.actions.merch_strategy.strategy && !data.actions.merch_strategy.note) {
                const merchTitle = document.createElement('div');
                merchTitle.className = 'action-section-title';
                merchTitle.style.fontWeight = 'bold';
                merchTitle.style.marginTop = '10px';
                merchTitle.style.marginBottom = '5px';
                merchTitle.textContent = '商品策略：';
                actionsDiv.appendChild(merchTitle);
                const merchItem = document.createElement('div');
                merchItem.className = 'action-item';
                merchItem.style.marginLeft = '15px';
                merchItem.style.marginBottom = '5px';
                merchItem.textContent = `优先展示：${data.actions.merch_strategy.category}类目，商品：${data.actions.merch_strategy.items.join(', ')}`;
                actionsDiv.appendChild(merchItem);
            }
            
            console.log('Adding actionsDiv to drillResult');  // 调试信息
            drillResult.appendChild(actionsDiv);
        } else {
            console.log('actionsDiv has no content, not adding');  // 调试信息
        }
    } else {
        console.log('No actions in data');  // 调试信息
    }
    
    contentDiv.appendChild(drillResult);
    
    // 下一步下钻卡
    console.log('检查next_drill_cards:', 'next_drill_cards' in data, data.next_drill_cards);  // 详细调试
    if (data.next_drill_cards && data.next_drill_cards.length > 0) {
        console.log('Processing next_drill_cards:', data.next_drill_cards);  // 调试信息
        const drillCardsDiv = document.createElement('div');
        drillCardsDiv.className = 'drill-cards';
        drillCardsDiv.style.marginTop = '15px';
        drillCardsDiv.style.padding = '10px';
        drillCardsDiv.style.backgroundColor = '#e8f5e9';
        drillCardsDiv.style.borderRadius = '5px';
        drillCardsDiv.style.border = '1px solid #28a745';
        
        // 添加标题
        const cardsTitle = document.createElement('div');
        cardsTitle.style.fontWeight = 'bold';
        cardsTitle.style.marginBottom = '10px';
        cardsTitle.style.color = '#333';
        cardsTitle.textContent = '进一步下钻分析：';
        drillCardsDiv.appendChild(cardsTitle);
        
        data.next_drill_cards.forEach(card => {
            const cardBtn = document.createElement('button');
            cardBtn.className = 'drill-card';
            cardBtn.setAttribute('data-card-id', card.id);  // 使用data属性，不绑定onclick
            cardBtn.style.cursor = 'pointer';
            cardBtn.style.marginRight = '10px';
            cardBtn.style.marginBottom = '10px';
            
            const title = document.createElement('div');
            title.className = 'drill-card-title';
            title.textContent = card.title;
            
            const desc = document.createElement('div');
            desc.className = 'drill-card-desc';
            desc.textContent = card.description;
            
            cardBtn.appendChild(title);
            cardBtn.appendChild(desc);
            drillCardsDiv.appendChild(cardBtn);
        });
        
        contentDiv.appendChild(drillCardsDiv);
        console.log('Added drillCardsDiv to contentDiv');  // 调试信息
    } else {
        console.log('No next_drill_cards in data');  // 调试信息
    }
    
    // 收集已显示的下钻卡片ID（包括next_drill_cards）
    const displayedCardIds = [];
    if (data.next_drill_cards && data.next_drill_cards.length > 0) {
        data.next_drill_cards.forEach(card => {
            displayedCardIds.push(card.id);
        });
    }
    
    // 获取当前层级
    const currentLevel = data.level || 'L1';
    
    // 添加未点击下钻按钮提示模块
    addUnclickedDrillCardsPrompt(contentDiv, currentLevel, displayedCardIds);
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    console.log('addDrillResult completed');  // 调试信息
}

// 事件监听
sendBtn.onclick = () => sendMessage(input.value.trim());
input.onkeypress = (e) => {
    if (e.key === 'Enter') {
        sendMessage(input.value.trim());
    }
};

// 事件委托：在messages容器上绑定一次click事件，处理所有下钻按钮点击
messagesContainer.addEventListener('click', (e) => {
    // 检查点击的是否是下钻按钮
    const drillCard = e.target.closest('.drill-card');
    if (drillCard) {
        const cardId = drillCard.getAttribute('data-card-id');
        if (cardId) {
            drillDown(cardId);
        }
    }
});

// 初始化
loadSuggestions();
