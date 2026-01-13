#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web应用 - 分析型智能体Web POC
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import queries
import cards
import state
import json
import os

# 获取当前文件的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# 设置 secret_key 用于 session（支持环境变量）
app.secret_key = os.environ.get('SECRET_KEY', 'baa6261_secret_key_2024')

# 密码配置（支持环境变量）
PASSWORD = os.environ.get('PASSWORD', 'baa6261')

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            # 如果是 API 请求，返回 JSON 错误
            if request.path.startswith('/api/'):
                return jsonify({'error': '需要登录', 'login_required': True}), 401
            # 否则重定向到登录页面
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == PASSWORD:
            session['logged_in'] = True
            next_url = request.args.get('next') or url_for('index')
            return redirect(next_url)
        else:
            error = '密码错误，请重试'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    """首页"""
    return render_template('index.html')

@app.route('/roadmap')
@login_required
def roadmap():
    """工程任务看板"""
    return render_template('task_board/index.html')

@app.route('/product-roadmap')
@login_required
def product_roadmap():
    """产品 Roadmap 页面"""
    return render_template('product_roadmap.html')

@app.route('/api/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """获取建议问题列表"""
    suggestions = [
        "为什么当前周期转化率下降了？",
        "当前周期转化率对比",
        "分析转化率下降原因"
    ]
    return jsonify(suggestions)

@app.route('/api/ask', methods=['POST'])
@login_required
def ask():
    """处理用户提问，返回L0结论卡+下钻卡"""
    data = request.get_json()
    question = data.get('question', '')
    
    # L0查询
    l0_data = queries.get_l0()
    
    # 构建L0结论
    prev_rate = l0_data['prev_7d']['rate']
    curr_rate = l0_data['curr_7d']['rate']
    change = l0_data['change']
    
    conclusion = f"当前周期（2026-01-08至2026-01-14）总体转化率为 {curr_rate:.2f}%，较上周期（2026-01-01至2026-01-07）的 {prev_rate:.2f}% {'下降' if change < 0 else '上升'}了 {abs(change):.2f}个百分点。"
    
    evidence = [
        f"上周期：{l0_data['prev_7d']['compare_users']}个用户进入compare阶段，{l0_data['prev_7d']['purchase_users']}个完成购买，转化率 {prev_rate:.2f}%",
        f"当前周期：{l0_data['curr_7d']['compare_users']}个用户进入compare阶段，{l0_data['curr_7d']['purchase_users']}个完成购买，转化率 {curr_rate:.2f}%"
    ]
    
    actions = [
        "建议进一步下钻分析流失断点",
        "重点关注购买决策阶段的用户行为"
    ]
    
    # 下钻卡
    drill_cards = cards.L0_DRILL_CARDS
    
    result = {
        'type': 'conclusion',
        'level': 'L0',
        'conclusion': conclusion,
        'evidence': evidence,
        'actions': actions,
        'drill_cards': drill_cards
    }
    
    return jsonify(result)

@app.route('/api/drill', methods=['POST'])
@login_required
def drill():
    """处理下钻请求，返回L1/L2结果"""
    data = request.get_json()
    card_id = data.get('card_id', '')
    
    card = cards.get_drill_card(card_id)
    if not card:
        return jsonify({'error': 'Invalid card_id'}), 400
    
    level = card['level']
    
    if card_id == 'C1':
        # L1: 旅程阶段断点下钻
        l1_data = queries.get_l1_stage_drop()
        
        # 找出最大断点
        compare_to_decide_drop = l1_data['compare_to_decide']['drop_count']
        decide_to_purchase_drop = l1_data['decide_to_purchase']['drop_count']
        
        max_drop_edge = 'decide→purchase' if decide_to_purchase_drop > compare_to_decide_drop else 'compare→decide'
        
        conclusion = f"当前周期中，{max_drop_edge} 边的流失最为显著。"
        if max_drop_edge == 'decide→purchase':
            conclusion += f"从decide到purchase的转化率仅为 {l1_data['decide_to_purchase']['rate']:.2f}%，流失用户数为 {decide_to_purchase_drop}。"
        
        evidence = [
            f"compare→decide: {l1_data['compare_to_decide']['from_count']}个用户进入compare，{l1_data['compare_to_decide']['to_count']}个到达decide，转化率 {l1_data['compare_to_decide']['rate']:.2f}%",
            f"decide→purchase: {l1_data['decide_to_purchase']['from_count']}个用户进入decide，{l1_data['decide_to_purchase']['to_count']}个完成purchase，转化率 {l1_data['decide_to_purchase']['rate']:.2f}%"
        ]
        
        # 更新状态
        state.update_state(anomaly_edge=max_drop_edge)
        
        result = {
            'type': 'drill_result',
            'level': 'L1',
            'drill': {
                'card_id': card_id,
                'title': card['title']
            },
            'conclusion': conclusion,
            'evidence': evidence,
            'next_drill_cards': [cards.L1_DRILL_CARDS[0]]  # C3
        }
        
        return jsonify(result)
    
    elif card_id == 'C2':
        # L1: 渠道下钻
        channel_data = queries.get_l2_channel_drill()
        
        top_channels = sorted(channel_data, key=lambda x: x['drop_count'], reverse=True)[:3]
        
        conclusion = "按渠道分析decide→purchase断点，各渠道流失情况如下："
        
        evidence = []
        for ch in top_channels:
            evidence.append(f"{ch['channel']}渠道: {ch['decide_users']}个decide用户，{ch['purchase_users']}个完成购买，转化率 {ch['rate']:.2f}%，流失 {ch['drop_count']}人")
        
        result = {
            'type': 'drill_result',
            'level': 'L1',
            'drill': {
                'card_id': card_id,
                'title': card['title']
            },
            'conclusion': conclusion,
            'evidence': evidence,
            'next_drill_cards': []
        }
        
        return jsonify(result)
    
    elif card_id == 'C3':
        # L2: 购买决策细分下钻（v2：同时识别两类问题）
        l2_data = queries.get_l2_decision_diagnosis_v2()
        
        user_count = l2_data['user_count']
        invalid_avg = l2_data['invalid_view_avg']
        key_page_reach = l2_data['key_page_reach_users']
        no_click_users = l2_data['no_item_click_users']
        no_click_rate = l2_data['no_item_click_rate']
        
        # 构建结论：同时说明两类问题
        conclusion_parts = []
        conclusion_parts.append(f"在进入决策阶段但未购买的用户中（共{user_count}人），发现两类问题：\n")
        
        # 问题A：无效浏览
        if invalid_avg > 0:
            conclusion_parts.append(f"【问题A】无效页面浏览过多：平均无效浏览 {invalid_avg}次\n")
        
        # 问题B：列表无点击
        if no_click_users > 0:
            conclusion_parts.append(f"【问题B】列表无点击：{key_page_reach}人到达商品列表页（category），其中{no_click_users}人（{no_click_rate:.1f}%）未点击任何商品")
        
        conclusion = "".join(conclusion_parts)
        
        # 如果没有识别到问题，给出提示
        if invalid_avg == 0 and no_click_users == 0:
            conclusion = f"在进入决策阶段但未购买的用户中（共{user_count}人），未发现明显问题。"
        
        evidence = []
        if invalid_avg > 0:
            evidence.append(f"问题A - 无效浏览：平均 {invalid_avg}次无效浏览")
            if l2_data['top_invalid_pages']:
                top_pages = ', '.join([f"{p['page_name']}({p['events']}次, {p['users']}人)" for p in l2_data['top_invalid_pages'][:3]])
                evidence.append(f"Top无效页面：{top_pages}")
        
        if no_click_users > 0:
            evidence.append(f"问题B - 列表无点击：{key_page_reach}人到达category，{no_click_users}人未点击商品（{no_click_rate}%）")
            if l2_data.get('impression_items_avg', 0) > 0:
                evidence.append(f"平均曝光商品数：{l2_data['impression_items_avg']}个")
        
        # 运营策略输出
        actions = {
            'ui_actions': [],
            'audience_building': {}
            # merch_strategy不在C3中输出，只在C32中输出
        }
        
        # UI策略：基于top_invalid_pages
        if l2_data['top_invalid_pages']:
            top_pages = l2_data['top_invalid_pages'][:3]
            actions['ui_actions'] = [
                f"删除/合并无效页面：{top_pages[0]['page_name']}（{top_pages[0]['events']}次浏览，{top_pages[0]['users']}人）",
                "优化路径：减少回首页路径，增加直达列表页入口",
                f"考虑合并相似页面：{', '.join([p['page_name'] for p in top_pages[:2]])}"
            ]
        
        # 人群策略：输出筛选条件（不真正创建）
        if no_click_users > 0:
            actions['audience_building'] = {
                'period': 'curr_7d',
                'journey_id': 'J_BUY',
                'in_decide': 1,
                'no_purchase': 1,
                'reached_category': 1,
                'item_click': 0,
                'audience_size': no_click_users
            }
        
        # 商品策略：C3中不输出，只在C32中输出
        # actions['merch_strategy'] 不在C3中输出
        
        result = {
            'type': 'drill_result',
            'level': 'L2',
            'drill': {
                'card_id': card_id,
                'title': card['title']
            },
            'conclusion': conclusion,
            'evidence': evidence,
            'next_drill_cards': cards.L2_DRILL_CARDS,  # C31, C32
            'actions': actions
        }
        
        return jsonify(result)
    
    elif card_id == 'C31':
        # L3: 无效页面名称下钻
        l3_data = queries.get_l3_invalid_pages()
        
        top_pages = l3_data['top_invalid_pages']
        
        if not top_pages:
            conclusion = "未发现无效页面。"
            evidence = []
        else:
            conclusion = f"发现 {len(top_pages)} 个Top无效页面，建议优先处理。"
            evidence = []
            for i, page in enumerate(top_pages, 1):
                evidence.append(f"{i}. {page['page_name']}：{page['events']}次浏览，涉及{page['users']}人")
        
        result = {
            'type': 'drill_result',
            'level': 'L3',
            'drill': {
                'card_id': card_id,
                'title': card['title']
            },
            'conclusion': conclusion,
            'evidence': evidence,
            'next_drill_cards': []
        }
        
        return jsonify(result)
    
    elif card_id == 'C32':
        # L3: 未点击商品用户偏好下钻
        l3_data = queries.get_l3_no_click_preference()
        
        audience_size = l3_data['audience_size']
        top_items = l3_data['historical_top_items']
        top_categories = l3_data['historical_top_categories']
        filters = l3_data['audience_filters']
        
        if audience_size == 0:
            conclusion = "未发现符合条件的人群（到达列表页但未点击商品）。"
            evidence = []
            actions = {}
        else:
            conclusion = f"圈出 {audience_size} 位\"到达列表页但未点击商品\"的用户，基于历史购买偏好分析："
            
            evidence = []
            if top_categories:
                evidence.append("历史购买Top类目：")
                for cat in top_categories:
                    evidence.append(f"  - {cat['category_name']}：{cat['buyer_count']}人购买，{cat['item_count']}种商品，总购买量{cat['total_qty']}件")
            
            if top_items:
                evidence.append("历史购买Top商品：")
                for item in top_items[:5]:
                    evidence.append(f"  - {item['item_name']}（{item['category_name']}）：{item['buyer_count']}人购买，{item['total_qty']}件，总金额{item['total_amount']}元")
            
            # 运营策略输出
            actions = {
                'ui_actions': [],
                'audience_building': filters,
                'merch_strategy': {}
            }
            
            # 人群策略：输出筛选条件
            actions['audience_building'] = filters
            actions['audience_building']['audience_size'] = audience_size
            
            # 商品策略：基于历史购买偏好
            if top_categories and top_items:
                # 找出最偏好的类目
                top_category = top_categories[0]['category_name']
                # 找出该类目下的商品
                category_items = [item for item in top_items if item['category_name'] == top_category]
                item_ids = [item['item_id'] for item in category_items[:3]]
                
                actions['merch_strategy'] = {
                    'strategy': 'prioritize',
                    'category': top_category,
                    'items': item_ids,
                    'reason': f"基于历史购买偏好：{top_category}类目有{top_categories[0]['buyer_count']}人购买"
                }
        
        result = {
            'type': 'drill_result',
            'level': 'L3',
            'drill': {
                'card_id': card_id,
                'title': card['title']
            },
            'conclusion': conclusion,
            'evidence': evidence,
            'next_drill_cards': [],
            'actions': actions
        }
        
        return jsonify(result)
    
    return jsonify({'error': 'Unknown card_id'}), 400

@app.route('/api/state', methods=['GET'])
@login_required
def get_state():
    """获取当前状态"""
    return jsonify(state.load_state())

@app.route('/api/reset', methods=['POST'])
@login_required
def reset():
    """重置状态"""
    new_state = state.reset_state()
    return jsonify(new_state)

@app.route('/api/health', methods=['GET'])
@login_required
def health():
    """健康检查端点"""
    return jsonify({'status': 'ok', 'message': '服务器运行正常'})

if __name__ == '__main__':
    print("=" * 50)
    print("启动分析型智能体 Web POC")
    print("=" * 50)
    print(f"访问地址: http://127.0.0.1:5000")
    print(f"健康检查: http://127.0.0.1:5000/api/health")
    print("=" * 50)
    print("如果端口5000被占用，请先运行: killall -9 Python")
    print("=" * 50)
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=True)
    except OSError as e:
        if 'Address already in use' in str(e):
            print("\n错误: 端口5000已被占用")
            print("请运行以下命令清理端口:")
            print("  killall -9 Python")
            print("或者修改代码使用其他端口（如5001）")
        else:
            raise
