import streamlit as st


# 1. 初始化会话状态，用于存储和更新数据
def initialize_session_state():
    """初始化所有财务报表数据为浮点数"""
    if 'data' not in st.session_state:
        st.session_state.data = {
            '资产负债表': {key: 0.0 for key in get_bs_data_structure()},
            '利润表': {key: 0.0 for key in get_income_data_structure()},
            '现金流量表': {key: 0.0 for key in get_cf_data_structure()},
        }


# 2. 定义精简后的报表结构
def get_income_data_structure():
    """精简版利润表数据结构"""
    return {
        '一、营业收入': {'key': '营业收入', 'type': 'input', 'level': 0},
        '减：营业成本': {'key': '营业成本', 'type': 'input', 'level': 0},
        '减：税金及附加': {'key': '税金及附加', 'type': 'input', 'level': 0},
        '减：销售费用': {'key': '销售费用', 'type': 'input', 'level': 0},
        '减：管理费用': {'key': '管理费用', 'type': 'input', 'level': 0},
        '减：财务费用': {'key': '财务费用', 'type': 'input', 'level': 0},
        '减：资产减值损失': {'key': '资产减值损失', 'type': 'input', 'level': 0},
        '加：投资收益（损失以“-”号填列）': {'key': '投资收益（损失以“-”号填列）', 'type': 'input', 'level': 0},
        '二、营业利润（亏损以“-”号填列）': {'key': '营业利润', 'type': 'output', 'level': 0, 'bold': True},
        '加：营业外收入': {'key': '营业外收入', 'type': 'input', 'level': 0},
        '减：营业外支出': {'key': '营业外支出', 'type': 'input', 'level': 0},
        '三、利润总额（亏损总额以“-”号填列）': {'key': '利润总额', 'type': 'output', 'level': 0, 'bold': True},
        '减：所得税费用': {'key': '所得税费用', 'type': 'input', 'level': 0},
        '四、净利润（净亏损以“-”号填列）': {'key': '净利润', 'type': 'output', 'level': 0, 'bold': True},
    }


def get_bs_data_structure():
    """精简版资产负债表数据结构"""
    return {
        '资产': {'key': '资产', 'type': 'heading'},
        '流动资产：': {'key': '流动资产：', 'type': 'header'},
        '货币资金': {'key': '货币资金', 'type': 'input', 'level': 1},
        '应收票据': {'key': '应收票据', 'type': 'input', 'level': 1},
        '应收账款': {'key': '应收账款', 'type': 'input', 'level': 1},
        '应收款项融资': {'key': '应收款项融资', 'type': 'input', 'level': 1},
        '预付款项': {'key': '预付款项', 'type': 'input', 'level': 1},
        '合同资产': {'key': '合同资产', 'type': 'input', 'level': 1},
        '其他应收款': {'key': '其他应收款', 'type': 'input', 'level': 1},
        '存货': {'key': '存货', 'type': 'input', 'level': 1},
        '流动资产合计': {'key': '流动资产合计', 'type': 'output', 'bold': True, 'level': 0},
        '非流动资产：': {'key': '非流动资产：', 'type': 'header'},
        '固定资产': {'key': '固定资产', 'type': 'input', 'level': 1},
        '在建工程': {'key': '在建工程', 'type': 'input', 'level': 1},
        '无形资产': {'key': '无形资产', 'type': 'input', 'level': 1},
        '递延所得税资产': {'key': '递延所得税资产', 'type': 'input', 'level': 1},
        '非流动资产合计': {'key': '非流动资产合计', 'type': 'output', 'bold': True, 'level': 0},
        '资产总计': {'key': '资产总计', 'type': 'output', 'bold': True, 'level': 0},
        '负债和所有者权益（或股东权益）': {'key': '负债和所有者权益（或股东权益）', 'type': 'heading'},
        '流动负债：': {'key': '流动负债：', 'type': 'header'},
        '短期借款': {'key': '短期借款', 'type': 'input', 'level': 1},
        '应付票据': {'key': '应付票据', 'type': 'input', 'level': 1},
        '应付账款': {'key': '应付账款', 'type': 'input', 'level': 1},
        '合同负债': {'key': '合同负债', 'type': 'input', 'level': 1},
        '应付职工薪酬': {'key': '应付职工薪酬', 'type': 'input', 'level': 1},
        '应交税费': {'key': '应交税费', 'type': 'input', 'level': 1},
        '应付利息': {'key': '应付利息', 'type': 'input', 'level': 1},
        '应付股利': {'key': '应付股利', 'type': 'input', 'level': 1},
        '其他应付款': {'key': '其他应付款', 'type': 'input', 'level': 1},
        '流动负债合计': {'key': '流动负债合计', 'type': 'output', 'bold': True, 'level': 0},
        '非流动负债：': {'key': '非流动负债：', 'type': 'header'},
        '长期借款': {'key': '长期借款', 'type': 'input', 'level': 1},
        '递延所得税负债': {'key': '递延所得税负债', 'type': 'input', 'level': 1},
        '非流动负债合计': {'key': '非流动负债合计', 'type': 'output', 'bold': True, 'level': 0},
        '负债合计': {'key': '负债合计', 'type': 'output', 'bold': True, 'level': 0},
        '所有者权益（或股东权益）：': {'key': '所有者权益（或股东权益）：', 'type': 'header'},
        '实收资本（或股本）': {'key': '实收资本（或股本）', 'type': 'input', 'level': 1},
        '资本公积': {'key': '资本公积', 'type': 'input', 'level': 1},
        '盈余公积': {'key': '盈余公积', 'type': 'input', 'level': 1},
        '未分配利润': {'key': '未分配利润', 'type': 'output', 'level': 1},
        '所有者权益（或股东权益）合计': {'key': '所有者权益（或股东权益）合计', 'type': 'output', 'bold': True, 'level': 0},
        '负债和所有者权益（或股东权益）总计': {
            'key': '负债和所有者权益（或股东权益）总计', 'type': 'output', 'bold': True, 'level': 0}
    }


def get_cf_data_structure():
    """精简版现金流量表数据结构"""
    return {
        '一、经营活动产生的现金流量：': {'key': '经营活动产生的现金流量：', 'type': 'header'},
        '销售商品、提供劳务收到的现金': {'key': '销售商品、提供劳务收到的现金', 'type': 'input', 'level': 1},
        '收到的税费返还': {'key': '收到的税费返还', 'type': 'input', 'level': 1},
        '收到其他与经营活动有关的现金': {'key': '收到其他与经营活动有关的现金', 'type': 'input', 'level': 1},
        '经营活动现金流入小计': {'key': '经营活动现金流入小计', 'type': 'output', 'level': 1},
        '购买商品、接受劳务支付的现金': {'key': '购买商品、接受劳务支付的现金', 'type': 'input', 'level': 1},
        '支付给职工以及为职工支付的现金': {'key': '支付给职工以及为职工支付的现金', 'type': 'input', 'level': 1},
        '支付的各项税费': {'key': '支付的各项税费', 'type': 'input', 'level': 1},
        '支付其他与经营活动有关的现金': {'key': '支付其他与经营活动有关的现金', 'type': 'input', 'level': 1},
        '经营活动现金流出小计': {'key': '经营活动现金流出小计', 'type': 'output', 'level': 1},
        '经营活动产生的现金流量净额': {'key': '经营活动产生的现金流量净额', 'type': 'output', 'bold': True, 'level': 0},
        '二、投资活动产生的现金流量：': {'key': '投资活动产生的现金流量：', 'type': 'header'},
        '收回投资收到的现金': {'key': '收回投资收到的现金', 'type': 'input', 'level': 1},
        '取得投资收益收到的现金': {'key': '取得投资收益收到的现金', 'type': 'input', 'level': 1},
        '处置固定资产、无形资产和其他长期资产收回的现金净额': {
            'key': '处置固定资产、无形资产和其他长期资产收回的现金净额', 'type': 'input', 'level': 1},
        '投资活动现金流入小计': {'key': '投资活动现金流入小计', 'type': 'output', 'level': 1},
        '购建固定资产、无形资产和其他长期资产支付的现金': {
            'key': '购建固定资产、无形资产和其他长期资产支付的现金', 'type': 'input', 'level': 1},
        '投资支付的现金': {'key': '投资支付的现金', 'type': 'input', 'level': 1},
        '投资活动现金流出小计': {'key': '投资活动现金流出小计', 'type': 'output', 'level': 1},
        '投资活动产生的现金流量净额': {'key': '投资活动产生的现金流量净额', 'type': 'output', 'bold': True, 'level': 0},
        '三、筹资活动产生的现金流量：': {'key': '筹资活动产生的现金流量：', 'type': 'header'},
        '吸收投资收到的现金': {'key': '吸收投资收到的现金', 'type': 'input', 'level': 1},
        '取得借款收到的现金': {'key': '取得借款收到的现金', 'type': 'input', 'level': 1},
        '筹资活动现金流入小计': {'key': '筹资活动现金流入小计', 'type': 'output', 'level': 1},
        '偿还债务支付的现金': {'key': '偿还债务支付的现金', 'type': 'input', 'level': 1},
        '分配股利、利润或偿付利息支付的现金': {'key': '分配股利、利润或偿付利息支付的现金', 'type': 'input', 'level': 1},
        '筹资活动现金流出小计': {'key': '筹资活动现金流出小计', 'type': 'output', 'level': 1},
        '筹资活动产生的现金流量净额': {'key': '筹资活动产生的现金流量净额', 'type': 'output', 'bold': True, 'level': 0},
        '四、汇率变动对现金及现金等价物的影响': {'key': '汇率变动对现金及现金等价物的影响', 'type': 'input', 'level': 0},
        '五、现金及现金等价物净增加额': {'key': '现金及现金等价物净增加额', 'type': 'output', 'bold': True, 'level': 0},
        '加：期初现金及现金等价物余额': {'key': '期初现金及现金等价物余额', 'type': 'input', 'level': 0},
        '六、期末现金及现金等价物余额': {'key': '期末现金及现金等价物余额', 'type': 'output', 'bold': True, 'level': 0},
    }


def render_financial_item(report_name, display_name, item_info, period):
    """通用渲染函数，根据数据结构渲染单个财务报表项目"""
    data_key = item_info['key']
    item_type = item_info.get('type')
    level = item_info.get('level', 0)
    bold = item_info.get('bold', False)

    # 根据缩进级别和是否加粗渲染项目名称
    prefix = '>> ' * (level - 1) if level > 1 else '> ' * level
    display_text = f"**{display_name}**" if bold else display_name
    st.markdown(f"{prefix}{display_text}")

    key_with_period = f"{data_key}_{period}"

    # 渲染输入框或显示计算结果
    if item_type == 'input':
        st.session_state.data[report_name][key_with_period] = st.number_input(
            f"{data_key} ({period})",
            value=st.session_state.data[report_name].get(key_with_period, 0.0),
            format="%.2f",
            key=f"{report_name}_{period}_input_{data_key}",
            label_visibility="collapsed"
        )
    elif item_type == 'output':
        # 这里从会话状态中获取计算后的值
        value = st.session_state.data[report_name].get(key_with_period, 0.0)
        st.number_input(
            f"{data_key} ({period})",
            value=value,
            format="%.2f",
            key=f"{report_name}_{period}_output_{data_key}",
            disabled=True,
            label_visibility="collapsed"
        )


# 3. 渲染函数：读取会话状态并计算
def render_income_statement(period: str):
    st.header('利润表')
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.write('**项目**')
    with col2:
        st.write(f'**{period}金额**')

    # 集中计算所有项目
    calculated_values = calculate_income_statement(period)
    st.session_state.data['利润表'].update(calculated_values)

    # 使用通用函数和数据结构渲染报表
    income_data = get_income_data_structure()
    for display_name, item_info in income_data.items():
        if item_info['type'] == 'header':
            st.markdown(f"**{display_name}**")
        else:
            render_financial_item('利润表', display_name, item_info, period)


def calculate_income_statement(period: str):
    """计算利润表中的所有勾稽项目"""
    data = st.session_state.data['利润表']

    # 营业利润
    operating_profit = (
            data.get(f'营业收入_{period}', 0.0) -
            data.get(f'营业成本_{period}', 0.0) -
            data.get(f'税金及附加_{period}', 0.0) -
            data.get(f'销售费用_{period}', 0.0) -
            data.get(f'管理费用_{period}', 0.0) -
            data.get(f'财务费用_{period}', 0.0) -
            data.get(f'资产减值损失_{period}', 0.0) +
            data.get(f'投资收益（损失以“-”号填列）_{period}', 0.0)
    )

    # 利润总额
    total_profit = (
            operating_profit +
            data.get(f'营业外收入_{period}', 0.0) -
            data.get(f'营业外支出_{period}', 0.0)
    )

    # 净利润
    net_profit = total_profit - data.get(f'所得税费用_{period}', 0.0)

    return {
        f'营业利润_{period}': operating_profit,
        f'利润总额_{period}': total_profit,
        f'净利润_{period}': net_profit,
    }


def render_balance_sheet(period: str):
    st.header('资产负债表')
    calculated_values = calculate_balance_sheet(period)
    st.session_state.data['资产负债表'].update(calculated_values)

    bs_data = get_bs_data_structure()

    # 按照资产和负债/所有者权益部分分割数据结构
    asset_items = []
    liab_equity_items = []
    is_asset_section = True
    for display_name, item_info in bs_data.items():
        if item_info['key'] == '负债和所有者权益（或股东权益）':
            is_asset_section = False
        if is_asset_section:
            asset_items.append((display_name, item_info))
        else:
            liab_equity_items.append((display_name, item_info))

    col_asset, col_liab_equity = st.columns(2)

    # 在第一列中渲染资产部分
    with col_asset:
        for display_name, item_info in asset_items:
            if item_info['type'] == 'heading' or item_info['type'] == 'header':
                st.markdown(f"**{display_name}**")
            elif item_info['key'] == '货币资金':
                # 货币资金与现金流量表期末余额自动勾稽
                cash_end_balance = st.session_state.data['现金流量表'].get(f'期末现金及现金等价物余额_{period}', 0.0)
                st.session_state.data['资产负债表'][f'货币资金_{period}'] = cash_end_balance
                render_financial_item(
                    '资产负债表',
                    f"**{display_name}**",
                    {'key': '货币资金', 'type': 'output', 'level': 1, 'bold': True},
                    period
                )
            else:
                render_financial_item('资产负债表', display_name, item_info, period)

    # 在第二列中渲染负债和所有者权益部分
    with col_liab_equity:
        for display_name, item_info in liab_equity_items:
            if item_info['type'] == 'heading' or item_info['type'] == 'header':
                st.markdown(f"**{display_name}**")
            else:
                render_financial_item('资产负债表', display_name, item_info, period)


def calculate_balance_sheet(period: str):
    """计算资产负债表中的所有勾稽项目"""
    data = st.session_state.data['资产负债表']

    # 资产总计
    assets_flow_items = ['货币资金', '应收票据', '应收账款', '应收款项融资', '预付款项', '合同资产', '其他应收款', '存货']
    assets_non_flow_items = ['固定资产', '在建工程', '无形资产', '递延所得税资产']

    assets_flow_sum = sum(data.get(f'{item}_{period}', 0.0) for item in assets_flow_items)
    assets_non_flow_sum = sum(data.get(f'{item}_{period}', 0.0) for item in assets_non_flow_items)
    assets_total = assets_flow_sum + assets_non_flow_sum

    # 负债及所有者权益总计
    liabilities_flow_items = [
        '短期借款', '应付票据', '应付账款', '合同负债', '应付职工薪酬', '应交税费', '应付利息', '应付股利', '其他应付款']
    liabilities_non_flow_items = ['长期借款', '递延所得税负债']
    equity_items = ['实收资本（或股本）', '资本公积', '盈余公积']

    liabilities_flow_sum = sum(data.get(f'{item}_{period}', 0.0) for item in liabilities_flow_items)
    liabilities_non_flow_sum = sum(data.get(f'{item}_{period}', 0.0) for item in liabilities_non_flow_items)
    liabilities_total = liabilities_flow_sum + liabilities_non_flow_sum

    # 未分配利润从利润表获取
    net_profit = st.session_state.data['利润表'].get(f'净利润_{period}', 0.0)

    if period == '本期':
        # 假设上期未分配利润为期初，本期期初 = 上期期末
        last_retained_earnings = st.session_state.data['资产负债表'].get('未分配利润_上期', 0.0)
    else:
        # 上期期初可以看作0，或者根据实际情况处理
        last_retained_earnings = 0.0

    current_retained_earnings = last_retained_earnings + net_profit

    equity_sum = sum(data.get(f'{item}_{period}', 0.0) for item in equity_items)
    equity_total = equity_sum + current_retained_earnings
    liabilities_and_equity_total = liabilities_total + equity_total

    return {
        f'流动资产合计_{period}': assets_flow_sum,
        f'非流动资产合计_{period}': assets_non_flow_sum,
        f'资产总计_{period}': assets_total,
        f'流动负债合计_{period}': liabilities_flow_sum,
        f'非流动负债合计_{period}': liabilities_non_flow_sum,
        f'负债合计_{period}': liabilities_total,
        f'未分配利润_{period}': current_retained_earnings,
        f'所有者权益（或股东权益）合计_{period}': equity_total,
        f'负债和所有者权益（或股东权益）总计_{period}': liabilities_and_equity_total
    }


def render_cash_flow_statement(period: str):
    st.header('现金流量表')
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.write('**项目**')
    with col2:
        st.write(f'**{period}金额**')

    # 集中计算所有项目
    calculated_values = calculate_cash_flow_statement(period)
    st.session_state.data['现金流量表'].update(calculated_values)

    # 使用通用函数和数据结构渲染报表
    cf_data = get_cf_data_structure()
    for display_name, item_info in cf_data.items():
        if item_info['type'] == 'header':
            st.markdown(f"**{display_name}**")
        else:
            render_financial_item('现金流量表', display_name, item_info, period)


def calculate_cash_flow_statement(period: str):
    """计算现金流量表中的所有勾稽项目"""
    data = st.session_state.data['现金流量表']

    # 经营活动现金流
    operating_in_items = ['销售商品、提供劳务收到的现金', '收到的税费返还', '收到其他与经营活动有关的现金']
    operating_out_items = [
        '购买商品、接受劳务支付的现金', '支付给职工以及为职工支付的现金', '支付的各项税费', '支付其他与经营活动有关的现金']

    operating_in_sum = sum(data.get(f'{item}_{period}', 0.0) for item in operating_in_items)
    operating_out_sum = sum(data.get(f'{item}_{period}', 0.0) for item in operating_out_items)
    operating_net_cash = operating_in_sum - operating_out_sum

    # 投资活动现金流
    investing_in_items = ['收回投资收到的现金', '取得投资收益收到的现金', '处置固定资产、无形资产和其他长期资产收回的现金净额']
    investing_out_items = ['购建固定资产、无形资产和其他长期资产支付的现金', '投资支付的现金']

    investing_in_sum = sum(data.get(f'{item}_{period}', 0.0) for item in investing_in_items)
    investing_out_sum = sum(data.get(f'{item}_{period}', 0.0) for item in investing_out_items)
    investing_net_cash = investing_in_sum - investing_out_sum

    # 筹资活动现金流
    financing_in_items = ['吸收投资收到的现金', '取得借款收到的现金']
    financing_out_items = ['偿还债务支付的现金', '分配股利、利润或偿付利息支付的现金']

    financing_in_sum = sum(data.get(f'{item}_{period}', 0.0) for item in financing_in_items)
    financing_out_sum = sum(data.get(f'{item}_{period}', 0.0) for item in financing_out_items)
    financing_net_cash = financing_in_sum - financing_out_sum

    # 现金及现金等价物净增加额
    fx_effect = data.get(f'汇率变动对现金及现金等价物的影响_{period}', 0.0)
    total_net_cash_increase = operating_net_cash + investing_net_cash + financing_net_cash + fx_effect

    # 期末余额
    cash_start = data.get(f'期初现金及现金等价物余额_{period}', 0.0)
    cash_end = cash_start + total_net_cash_increase

    return {
        f'经营活动现金流入小计_{period}': operating_in_sum,
        f'经营活动现金流出小计_{period}': operating_out_sum,
        f'经营活动产生的现金流量净额_{period}': operating_net_cash,
        f'投资活动现金流入小计_{period}': investing_in_sum,
        f'投资活动现金流出小计_{period}': investing_out_sum,
        f'投资活动产生的现金流量净额_{period}': investing_net_cash,
        f'筹资活动现金流入小计_{period}': financing_in_sum,
        f'筹资活动现金流出小计_{period}': financing_out_sum,
        f'筹资活动产生的现金流量净额_{period}': financing_net_cash,
        f'现金及现金等价物净增加额_{period}': total_net_cash_increase,
        f'期末现金及现金等价物余额_{period}': cash_end,
    }


# 页面布局
initialize_session_state()
st.set_page_config(layout="wide", page_title="交互式财务报表")
st.title('交互式财务报表')
st.markdown("请在下方的输入框中填写数据，勾稽关系将自动更新。")
st.divider()

tab1, tab2 = st.tabs(["本期金额", "上期金额"])

with tab1:
    # st.markdown('### 本期')
    col_income, col_balance, col_cashflow = st.columns([1, 2, 1], gap="large")
    with col_income:
        render_income_statement('本期')
    with col_balance:
        render_balance_sheet('本期')
    with col_cashflow:
        render_cash_flow_statement('本期')

with tab2:
    # st.markdown('### 上期')
    col_income_prev, col_balance_prev, col_cashflow_prev = st.columns([1, 2, 1], gap="large")
    with col_income_prev:
        render_income_statement('上期')
    with col_balance_prev:
        render_balance_sheet('上期')
    with col_cashflow_prev:
        render_cash_flow_statement('上期')
