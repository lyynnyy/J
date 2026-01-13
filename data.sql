-- 数据表结构和示例数据
-- 时间窗：prev_7d: 2026-01-01~2026-01-07, curr_7d: 2026-01-08~2026-01-14

-- users表
INSERT INTO users (user_id, first_channel, user_type, created_at) VALUES
-- prev_7d 用户（转化率高）
('u_prev_1', 'organic', 'new', '2026-01-01 10:00:00'),
('u_prev_2', 'paid', 'new', '2026-01-02 11:00:00'),
('u_prev_3', 'organic', 'returning', '2026-01-03 12:00:00'),
('u_prev_4', 'paid', 'new', '2026-01-04 13:00:00'),
('u_prev_5', 'direct', 'new', '2026-01-05 14:00:00'),
-- curr_7d 用户（转化率低，decide→purchase断点大）
('u_curr_1', 'organic', 'new', '2026-01-08 10:00:00'),
('u_curr_2', 'paid', 'new', '2026-01-09 11:00:00'),
('u_curr_3', 'organic', 'returning', '2026-01-10 12:00:00'),
('u_curr_4', 'paid', 'new', '2026-01-11 13:00:00'),
('u_curr_5', 'direct', 'new', '2026-01-12 14:00:00'),
('u_curr_6', 'organic', 'new', '2026-01-13 15:00:00'),
('u_curr_7', 'paid', 'new', '2026-01-14 16:00:00');

-- journey_events表
-- prev_7d: 大多数用户完成compare→decide→purchase
INSERT INTO journey_events (je_id, user_id, ts, journey_id, step, step_name, order_id, amount) VALUES
-- u_prev_1: compare→decide→purchase (完成)
('je_prev_1_1', 'u_prev_1', '2026-01-01 10:00:00', 'j_prev_1', 'compare', 'compare', NULL, NULL),
('je_prev_1_2', 'u_prev_1', '2026-01-01 10:05:00', 'j_prev_1', 'decide', 'decide', NULL, NULL),
('je_prev_1_3', 'u_prev_1', '2026-01-01 10:10:00', 'j_prev_1', 'purchase', 'purchase', 'ord_prev_1', 199.99),
-- u_prev_2: compare→decide→purchase (完成)
('je_prev_2_1', 'u_prev_2', '2026-01-02 11:00:00', 'j_prev_2', 'compare', 'compare', NULL, NULL),
('je_prev_2_2', 'u_prev_2', '2026-01-02 11:05:00', 'j_prev_2', 'decide', 'decide', NULL, NULL),
('je_prev_2_3', 'u_prev_2', '2026-01-02 11:10:00', 'j_prev_2', 'purchase', 'purchase', 'ord_prev_2', 299.99),
-- u_prev_3: compare→decide→purchase (完成)
('je_prev_3_1', 'u_prev_3', '2026-01-03 12:00:00', 'j_prev_3', 'compare', 'compare', NULL, NULL),
('je_prev_3_2', 'u_prev_3', '2026-01-03 12:05:00', 'j_prev_3', 'decide', 'decide', NULL, NULL),
('je_prev_3_3', 'u_prev_3', '2026-01-03 12:10:00', 'j_prev_3', 'purchase', 'purchase', 'ord_prev_3', 149.99),
-- u_prev_4: compare→purchase (跳过decide)
('je_prev_4_1', 'u_prev_4', '2026-01-04 13:00:00', 'j_prev_4', 'compare', 'compare', NULL, NULL),
('je_prev_4_2', 'u_prev_4', '2026-01-04 13:05:00', 'j_prev_4', 'purchase', 'purchase', 'ord_prev_4', 99.99),
-- u_prev_5: compare→decide→purchase (完成)
('je_prev_5_1', 'u_prev_5', '2026-01-05 14:00:00', 'j_prev_5', 'compare', 'compare', NULL, NULL),
('je_prev_5_2', 'u_prev_5', '2026-01-05 14:05:00', 'j_prev_5', 'decide', 'decide', NULL, NULL),
('je_prev_5_3', 'u_prev_5', '2026-01-05 14:10:00', 'j_prev_5', 'purchase', 'purchase', 'ord_prev_5', 249.99);

-- curr_7d: 很多用户在decide→purchase断点流失
INSERT INTO journey_events (je_id, user_id, ts, journey_id, step, step_name, order_id, amount) VALUES
-- u_curr_1: compare→decide (流失)
('je_curr_1_1', 'u_curr_1', '2026-01-08 10:00:00', 'j_curr_1', 'compare', 'compare', NULL, NULL),
('je_curr_1_2', 'u_curr_1', '2026-01-08 10:05:00', 'j_curr_1', 'decide', 'decide', NULL, NULL),
-- u_curr_2: compare→decide (流失)
('je_curr_2_1', 'u_curr_2', '2026-01-09 11:00:00', 'j_curr_2', 'compare', 'compare', NULL, NULL),
('je_curr_2_2', 'u_curr_2', '2026-01-09 11:05:00', 'j_curr_2', 'decide', 'decide', NULL, NULL),
-- u_curr_3: compare→decide (流失)
('je_curr_3_1', 'u_curr_3', '2026-01-10 12:00:00', 'j_curr_3', 'compare', 'compare', NULL, NULL),
('je_curr_3_2', 'u_curr_3', '2026-01-10 12:05:00', 'j_curr_3', 'decide', 'decide', NULL, NULL),
-- u_curr_4: compare→decide (流失)
('je_curr_4_1', 'u_curr_4', '2026-01-11 13:00:00', 'j_curr_4', 'compare', 'compare', NULL, NULL),
('je_curr_4_2', 'u_curr_4', '2026-01-11 13:05:00', 'j_curr_4', 'decide', 'decide', NULL, NULL),
-- u_curr_5: compare→decide→purchase (完成，少数)
('je_curr_5_1', 'u_curr_5', '2026-01-12 14:00:00', 'j_curr_5', 'compare', 'compare', NULL, NULL),
('je_curr_5_2', 'u_curr_5', '2026-01-12 14:05:00', 'j_curr_5', 'decide', 'decide', NULL, NULL),
('je_curr_5_3', 'u_curr_5', '2026-01-12 14:10:00', 'j_curr_5', 'purchase', 'purchase', 'ord_curr_5', 199.99),
-- u_curr_6: compare→decide (流失)
('je_curr_6_1', 'u_curr_6', '2026-01-13 15:00:00', 'j_curr_6', 'compare', 'compare', NULL, NULL),
('je_curr_6_2', 'u_curr_6', '2026-01-13 15:05:00', 'j_curr_6', 'decide', 'decide', NULL, NULL),
-- u_curr_7: compare→decide (流失)
('je_curr_7_1', 'u_curr_7', '2026-01-14 16:00:00', 'j_curr_7', 'compare', 'compare', NULL, NULL),
('je_curr_7_2', 'u_curr_7', '2026-01-14 16:05:00', 'j_curr_7', 'decide', 'decide', NULL, NULL);

-- decision_events表
-- 对于curr_7d中进入decide但未purchase的用户，模拟大量无效浏览
-- u_curr_1: 大量无效浏览，未到达category
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_1_1', 'u_curr_1', '2026-01-08 10:05:00', 'j_curr_1', 's_curr_1', 'home', 'page', 'view', NULL, 0),
('de_curr_1_2', 'u_curr_1', '2026-01-08 10:06:00', 'j_curr_1', 's_curr_1', 'home', 'page', 'view', NULL, 0),
('de_curr_1_3', 'u_curr_1', '2026-01-08 10:07:00', 'j_curr_1', 's_curr_1', 'home', 'page', 'click', 'back_home', 0),
('de_curr_1_4', 'u_curr_1', '2026-01-08 10:08:00', 'j_curr_1', 's_curr_1', 'product', 'page', 'view', NULL, 0),
('de_curr_1_5', 'u_curr_1', '2026-01-08 10:09:00', 'j_curr_1', 's_curr_1', 'home', 'page', 'click', 'random_btn', 0),
('de_curr_1_6', 'u_curr_1', '2026-01-08 10:10:00', 'j_curr_1', 's_curr_1', 'home', 'page', 'view', NULL, 0),
('de_curr_1_7', 'u_curr_1', '2026-01-08 10:11:00', 'j_curr_1', 's_curr_1', 'product', 'page', 'view', NULL, 0),
('de_curr_1_8', 'u_curr_1', '2026-01-08 10:12:00', 'j_curr_1', 's_curr_1', 'home', 'page', 'click', 'back_home', 0);

-- u_curr_2: 大量无效浏览，未到达category
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_2_1', 'u_curr_2', '2026-01-09 11:05:00', 'j_curr_2', 's_curr_2', 'home', 'page', 'view', NULL, 0),
('de_curr_2_2', 'u_curr_2', '2026-01-09 11:06:00', 'j_curr_2', 's_curr_2', 'product', 'page', 'view', NULL, 0),
('de_curr_2_3', 'u_curr_2', '2026-01-09 11:07:00', 'j_curr_2', 's_curr_2', 'home', 'page', 'click', 'random_btn', 0),
('de_curr_2_4', 'u_curr_2', '2026-01-09 11:08:00', 'j_curr_2', 's_curr_2', 'home', 'page', 'view', NULL, 0),
('de_curr_2_5', 'u_curr_2', '2026-01-09 11:09:00', 'j_curr_2', 's_curr_2', 'home', 'page', 'click', 'back_home', 0),
('de_curr_2_6', 'u_curr_2', '2026-01-09 11:10:00', 'j_curr_2', 's_curr_2', 'product', 'page', 'view', NULL, 0),
('de_curr_2_7', 'u_curr_2', '2026-01-09 11:11:00', 'j_curr_2', 's_curr_2', 'home', 'page', 'view', NULL, 0);

-- u_curr_3: 大量无效浏览，未到达category
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_3_1', 'u_curr_3', '2026-01-10 12:05:00', 'j_curr_3', 's_curr_3', 'home', 'page', 'view', NULL, 0),
('de_curr_3_2', 'u_curr_3', '2026-01-10 12:06:00', 'j_curr_3', 's_curr_3', 'product', 'page', 'view', NULL, 0),
('de_curr_3_3', 'u_curr_3', '2026-01-10 12:07:00', 'j_curr_3', 's_curr_3', 'home', 'page', 'click', 'back_home', 0),
('de_curr_3_4', 'u_curr_3', '2026-01-10 12:08:00', 'j_curr_3', 's_curr_3', 'home', 'page', 'view', NULL, 0),
('de_curr_3_5', 'u_curr_3', '2026-01-10 12:09:00', 'j_curr_3', 's_curr_3', 'home', 'page', 'click', 'random_btn', 0),
('de_curr_3_6', 'u_curr_3', '2026-01-10 12:10:00', 'j_curr_3', 's_curr_3', 'home', 'page', 'view', NULL, 0);

-- u_curr_4: 大量无效浏览，未到达category
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_4_1', 'u_curr_4', '2026-01-11 13:05:00', 'j_curr_4', 's_curr_4', 'home', 'page', 'view', NULL, 0),
('de_curr_4_2', 'u_curr_4', '2026-01-11 13:06:00', 'j_curr_4', 's_curr_4', 'home', 'page', 'click', 'random_btn', 0),
('de_curr_4_3', 'u_curr_4', '2026-01-11 13:07:00', 'j_curr_4', 's_curr_4', 'product', 'page', 'view', NULL, 0),
('de_curr_4_4', 'u_curr_4', '2026-01-11 13:08:00', 'j_curr_4', 's_curr_4', 'home', 'page', 'view', NULL, 0),
('de_curr_4_5', 'u_curr_4', '2026-01-11 13:09:00', 'j_curr_4', 's_curr_4', 'home', 'page', 'click', 'back_home', 0),
('de_curr_4_6', 'u_curr_4', '2026-01-11 13:10:00', 'j_curr_4', 's_curr_4', 'home', 'page', 'view', NULL, 0);

-- u_curr_5: 到达category（完成购买的用户）
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_5_1', 'u_curr_5', '2026-01-12 14:05:00', 'j_curr_5', 's_curr_5', 'category', 'page', 'view', NULL, 1),
('de_curr_5_2', 'u_curr_5', '2026-01-12 14:06:00', 'j_curr_5', 's_curr_5', 'product', 'page', 'view', NULL, 0);

-- u_curr_6: 少量无效浏览，未到达category
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_6_1', 'u_curr_6', '2026-01-13 15:05:00', 'j_curr_6', 's_curr_6', 'home', 'page', 'view', NULL, 0),
('de_curr_6_2', 'u_curr_6', '2026-01-13 15:06:00', 'j_curr_6', 's_curr_6', 'home', 'page', 'click', 'random_btn', 0),
('de_curr_6_3', 'u_curr_6', '2026-01-13 15:07:00', 'j_curr_6', 's_curr_6', 'product', 'page', 'view', NULL, 0);

-- u_curr_7: 大量无效浏览，未到达category
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
('de_curr_7_1', 'u_curr_7', '2026-01-14 16:05:00', 'j_curr_7', 's_curr_7', 'home', 'page', 'view', NULL, 0),
('de_curr_7_2', 'u_curr_7', '2026-01-14 16:06:00', 'j_curr_7', 's_curr_7', 'home', 'page', 'view', NULL, 0),
('de_curr_7_3', 'u_curr_7', '2026-01-14 16:07:00', 'j_curr_7', 's_curr_7', 'home', 'page', 'click', 'back_home', 0),
('de_curr_7_4', 'u_curr_7', '2026-01-14 16:08:00', 'j_curr_7', 's_curr_7', 'product', 'page', 'view', NULL, 0),
('de_curr_7_5', 'u_curr_7', '2026-01-14 16:09:00', 'j_curr_7', 's_curr_7', 'home', 'page', 'click', 'random_btn', 0),
('de_curr_7_6', 'u_curr_7', '2026-01-14 16:10:00', 'j_curr_7', 's_curr_7', 'home', 'page', 'view', NULL, 0);

-- 新增用户：u9, u10（用于列表无点击场景）
INSERT INTO users (user_id, first_channel, user_type, created_at) VALUES
('u9', 'ads', 'returning', '2026-01-08 10:00:00'),
('u10', 'organic', 'returning', '2026-01-09 11:00:00');

-- u9, u10的journey_events：都有compare→decide，均无purchase
INSERT INTO journey_events (je_id, user_id, ts, journey_id, step, step_name, order_id, amount) VALUES
-- u9: compare→decide (流失)
('je_u9_1', 'u9', '2026-01-08 10:00:00', 'j_u9', 'compare', 'compare', NULL, NULL),
('je_u9_2', 'u9', '2026-01-08 10:05:00', 'j_u9', 'decide', 'decide', NULL, NULL),
-- u10: compare→decide (流失)
('je_u10_1', 'u10', '2026-01-09 11:00:00', 'j_u10', 'compare', 'compare', NULL, NULL),
('je_u10_2', 'u10', '2026-01-09 11:05:00', 'j_u10', 'decide', 'decide', NULL, NULL);

-- u9, u10的decision_events：都到达category，到达前各有1条invalid页面
INSERT INTO decision_events (de_id, user_id, ts, journey_id, session_id, page_name, page_type, action, button_id, is_key_page) VALUES
-- u9: 1条invalid页面，然后到达category
('de_u9_1', 'u9', '2026-01-08 10:05:00', 'j_u9', 's_u9', 'home', 'page', 'view', NULL, 0),
('de_u9_2', 'u9', '2026-01-08 10:06:00', 'j_u9', 's_u9', 'category', 'page', 'view', NULL, 1),
-- u10: 1条invalid页面，然后到达category
('de_u10_1', 'u10', '2026-01-09 11:05:00', 'j_u10', 's_u10', 'product', 'page', 'view', NULL, 0),
('de_u10_2', 'u10', '2026-01-09 11:06:00', 'j_u10', 's_u10', 'category', 'page', 'view', NULL, 1);

-- items表：两类偏好商品
INSERT INTO items (item_id, item_name, category_name, tag) VALUES
-- Sports类目
('i101', '运动鞋A', 'Sports', 'sports'),
('i102', '运动服B', 'Sports', 'sports'),
('i103', '运动包C', 'Sports', 'sports'),
-- KidsSnack类目
('i201', '儿童零食A', 'KidsSnack', 'kids'),
('i202', '儿童零食B', 'KidsSnack', 'kids'),
('i203', '儿童零食C', 'KidsSnack', 'kids');

-- item_events表：u9/u10在category有item_impression，无item_click
INSERT INTO item_events (ie_id, user_id, ts, journey_id, session_id, page_name, event_name, item_id) VALUES
-- u9: 在category有3条item_impression（i101/i102/i103）
('ie_u9_1', 'u9', '2026-01-08 10:06:10', 'j_u9', 's_u9', 'category', 'item_impression', 'i101'),
('ie_u9_2', 'u9', '2026-01-08 10:06:20', 'j_u9', 's_u9', 'category', 'item_impression', 'i102'),
('ie_u9_3', 'u9', '2026-01-08 10:06:30', 'j_u9', 's_u9', 'category', 'item_impression', 'i103'),
-- u10: 在category有3条item_impression（i201/i202/i203）
('ie_u10_1', 'u10', '2026-01-09 11:06:10', 'j_u10', 's_u10', 'category', 'item_impression', 'i201'),
('ie_u10_2', 'u10', '2026-01-09 11:06:20', 'j_u10', 's_u10', 'category', 'item_impression', 'i202'),
('ie_u10_3', 'u10', '2026-01-09 11:06:30', 'j_u10', 's_u10', 'category', 'item_impression', 'i203');

-- order_items表：历史购买偏好
INSERT INTO order_items (oi_id, order_id, user_id, item_id, qty, amount) VALUES
-- u9：多次购买i101，少量i102 → 明确偏好Sports
('oi_u9_1', 'ord_u9_1', 'u9', 'i101', 3, 299.97),
('oi_u9_2', 'ord_u9_2', 'u9', 'i101', 2, 199.98),
('oi_u9_3', 'ord_u9_3', 'u9', 'i101', 1, 99.99),
('oi_u9_4', 'ord_u9_4', 'u9', 'i102', 1, 49.99),
-- u10：多次购买i201，少量i202 → 明确偏好KidsSnack
('oi_u10_1', 'ord_u10_1', 'u10', 'i201', 5, 149.95),
('oi_u10_2', 'ord_u10_2', 'u10', 'i201', 3, 89.97),
('oi_u10_3', 'ord_u10_3', 'u10', 'i201', 2, 59.98),
('oi_u10_4', 'ord_u10_4', 'u10', 'i202', 1, 19.99);
