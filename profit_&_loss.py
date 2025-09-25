import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Optional

st.set_page_config(page_title="金税四期 损益计算", layout="wide")
st.title("金税四期 损益计算")

col_left, col_right = st.columns([1, 3], gap="large")

# ============================
# 左边栏：输入
# ============================
with col_left:
    st.header("输入参数")
    # 1) 合同与收款节奏
    st.subheader("合同与收款节奏")
    contract_total = st.number_input("合同总额（含税，3年期）", min_value=0.0, value=17_000_000.0, step=100_000.0, format="%.2f")
    down_pct = st.slider("首付款比例（%）", 0, 100, 30, 1) / 100.0
    mid_pct = st.slider("中期款比例（%）", 0, 100, 50, 1) / 100.0
    if down_pct + mid_pct > 1.0:
        st.error("首付比例 + 中期款比例 不能大于 100%。请调整。")
    tail_pct = max(0.0, 1.0 - down_pct - mid_pct)

    quarters_total = 12  # 3年×4季
    mid_per_quarter_gross = contract_total * mid_pct / quarters_total
    gross_receipt_y1 = contract_total * down_pct + mid_per_quarter_gross * 4  # 第一年的含税收款

    # 2) 增值税参数
    st.subheader("纳税人身份判定参数")
    levy_small = st.selectbox("小规模纳税人适用税率（%）", [1, 3], index=1) / 100.0
    vat_general = st.selectbox("一般纳税人适用税率（%）", [6, 9, 13], index=0) / 100.0

    st.caption("注：纳税人身份判定顺序为：先按小规模征收率试算不含税销售额 → 若>500万则切换一般纳税人并按适用税率重算。")

    # 3) 利润参数
    st.subheader("利润参数")
    gross_margin = st.slider("毛利率（%）", 0, 100, 20, 1) / 100.0
    opex_ratio = st.slider("期间费用率（%）", 0, 100, 0, 1) / 100.0  # 预留（销售费用 + 管理费用 + 财务费用），默认 0%

    # 4) 附加税费参数（基于应纳增值税计提）
    st.subheader("附加税费参数")
    urban_maint_pct = st.slider("城建税（%）", 0.0, 12.0, 7.0, 0.5) / 100.0
    edu_surcharge_pct = st.slider("教育费附加（%）", 0.0, 5.0, 3.0, 0.5) / 100.0
    local_edu_pct = st.slider("地方教育附加（%）", 0.0, 5.0, 2.0, 0.5) / 100.0

    # 5) 小微企业判定参数
    st.subheader("小型微利企业判定参数")
    headcount = st.number_input("从业人数", min_value=0, value=10, step=1)
    assets_total = st.number_input("资产总额（元）", min_value=0.0, value=3_000_000.0, step=100_000.0, format="%.2f")
    restricted_industry = st.checkbox("是否限制/禁止行业", value=False)

    # 6) 利润分配与预提
    st.subheader("利润分配与预提")
    stat_reserve_pct = st.slider("盈余公积当期提取比例（%）", 0, 20, 0, 1) / 100.0
    dividend_payout_pct = st.slider("分红比例（%，对可分配利润）", 0, 100, 100, 5) / 100.0
    dividend_iit_pct = st.slider("自然人股东分红个税率（%）", 0, 20, 20, 1) / 100.0


# ----------------------------
# 工具函数
# ----------------------------
def cny(x: float) -> str:
    return f"¥{x:,.2f}"


def pct(x: float) -> str:
    return f"{x * 100:.2f}%"


# ----------------------------
# 计算逻辑
# ----------------------------
# Step 1: 收入口径（含税）
down_payment = contract_total * down_pct
mid_payment_y1 = mid_per_quarter_gross * 4
tail_payment_y1 = 0.0  # 第一年没有尾款
gross_receipt_breakdown = {
    "首付款": down_payment,
    "中期款（当年4季）": mid_payment_y1,
    "尾款（当年）": tail_payment_y1,
}
# 校验
if abs((down_payment + contract_total * mid_pct + contract_total * tail_pct) - contract_total) > 1e-4:
    pass  # 比例拆分容忍浮动


# 年度流水线
def yearly_pipeline(gross_receipt: float) -> dict:
    # Step 2: 身份判定（先小规模试算，超500万则切一般纳税人）
    sales_excl_tax_small_trial_y = gross_receipt / (1 + levy_small)
    taxpayer_type_y = "小规模纳税人"
    vat_rate_applied_y = levy_small
    sales_excl_tax_y = sales_excl_tax_small_trial_y
    if sales_excl_tax_small_trial_y > 5_000_000.0:
        taxpayer_type_y = "一般纳税人"
        vat_rate_applied_y = vat_general
        sales_excl_tax_y = gross_receipt / (1 + vat_general)

    # Step 3: 增值税与附加（演示口径：不计算进项抵扣，直接基于不含税销售额 × 税率估算应纳增值税）
    output_vat_y = sales_excl_tax_y * vat_rate_applied_y
    surtaxes_y = output_vat_y * (urban_maint_pct + edu_surcharge_pct + local_edu_pct)

    # Step 4: 毛利与成本
    gross_profit_y = sales_excl_tax_y * gross_margin
    cogs_y = sales_excl_tax_y - gross_profit_y

    # Step 5: 期间费用
    opex_y = sales_excl_tax_y * opex_ratio

    # Step 6: 会计利润（营业利润）
    # 注意：这里纳入了“附加税费”
    accounting_profit_y = max(0.0, gross_profit_y - surtaxes_y - opex_y)
    taxable_income_y = accounting_profit_y

    # Step 7: 小型微利企业判定
    is_small_micro_y = (
            (taxable_income_y <= 3_000_000.0) and
            (headcount <= 300) and
            (assets_total <= 50_000_000.0) and
            (not restricted_industry)
    )

    # Step 8: 企业所得税
    def eit_small_micro(amount: float) -> float:
        # 0–300万部分实际税负 5%，超出部分 25%
        portion = min(amount, 3_000_000.0)
        tax = portion * 0.05
        excess = max(amount - 3_000_000.0, 0.0)
        tax += excess * 0.25
        return tax

    eit_y = eit_small_micro(taxable_income_y) if is_small_micro_y else taxable_income_y * 0.25
    eit_effective_rate_y = (eit_y / taxable_income_y) if taxable_income_y > 0 else 0.0

    # Step 9: 税后净利、分配
    net_profit_after_eit_y = max(0.0, taxable_income_y - eit_y)
    stat_reserve_y = net_profit_after_eit_y * stat_reserve_pct
    distributable_y = max(0.0, net_profit_after_eit_y - stat_reserve_y)
    div_declared_y = distributable_y * dividend_payout_pct
    div_tax_y = div_declared_y * dividend_iit_pct
    div_to_shareholders_y = max(0.0, div_declared_y - div_tax_y)
    retained_y = max(0.0, distributable_y - div_declared_y)

    return dict(
        taxpayer_type=taxpayer_type_y,
        vat_rate_applied=vat_rate_applied_y,
        sales_excl_tax=sales_excl_tax_y,
        output_vat=output_vat_y,
        surtaxes=surtaxes_y,
        gross_profit=gross_profit_y,
        cogs=cogs_y,
        opex=opex_y,
        accounting_profit=accounting_profit_y,
        taxable_income=taxable_income_y,
        is_small_micro=is_small_micro_y,
        eit=eit_y,
        eit_effective_rate=eit_effective_rate_y,
        net_profit_after_eit=net_profit_after_eit_y,
        stat_reserve=stat_reserve_y,
        distributable=distributable_y,
        div_declared=div_declared_y,
        div_tax=div_tax_y,
        div_to_shareholders=div_to_shareholders_y,
        retained=retained_y,
        sales_excl_tax_small_trial=sales_excl_tax_small_trial_y
    )


# 第一年、第二年、第三年的含税收款
gross_receipt_y1 = contract_total * down_pct + mid_per_quarter_gross * 4
gross_receipt_y2 = mid_per_quarter_gross * 4  # 第二年：中期款4季
gross_receipt_y3 = mid_per_quarter_gross * 4 + contract_total * tail_pct  # 第三年：中期款4季 + 尾款

# 运行年度流水线
Y1 = yearly_pipeline(gross_receipt_y1)
Y2 = yearly_pipeline(gross_receipt_y2)
Y3 = yearly_pipeline(gross_receipt_y3)


# ----------------------------
# 输出渲染函数
# ----------------------------
def render_year(year_label: str, gross_receipt: float, result: dict):
    st.header(f"测算结果 {year_label}")

    # 详情 Step 1：收入口径
    st.metric("含税收款（当年）", cny(gross_receipt))
    with st.expander(f"步骤1：收入口径（含税）详情 | {year_label}"):
        if year_label == "第一年":
            st.markdown(f"""
            - **首付款：** 
                {cny(down_payment)}
            - **中期款：** 
                4个季度 × 每季度中期款 {cny(mid_per_quarter_gross)} 
                = {cny(mid_payment_y1)}
            - **尾款（当年）：** 
                0
            - **当年含税收款合计：** 
                {cny(gross_receipt)}
            """)
        elif year_label == "第二年":
            st.markdown(f"""
            - **中期款：** 
                4个季度 × 每季度中期款 {cny(mid_per_quarter_gross)} 
                = {cny(gross_receipt)}
            - **尾款（当年）：** 
                0
            """)
        else:
            st.markdown(f"""
            - **中期款：** 
                4个季度 × 每季度中期款 {cny(mid_per_quarter_gross)} 
                = {cny(mid_per_quarter_gross * 4)}
            - **尾款（第三年末）：** 
                {cny(contract_total * tail_pct)}
            - **当年含税收款合计：** 
                {cny(gross_receipt)}
            """)

    # 详情 Step 2：小规模判定
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("不含税销售额（当年）", cny(result["sales_excl_tax"]))
    with col_b:
        st.metric("小规模/一般判定", result["taxpayer_type"])
    with col_c:
        st.metric("适用增值税税率", pct(result["vat_rate_applied"]))
    with st.expander(f"步骤2：小规模纳税人判定详情 | {year_label}"):
        st.markdown(f"""
        - **不含税销售额（按小规模试算，征收率 {pct(levy_small)}）：** 
            含税收款 {cny(gross_receipt)} ÷ (1 + 征收率 {pct(levy_small)}) 
            = {cny(result["sales_excl_tax_small_trial"])}
        - **门槛：** 
            500万元（不含税）
        - **判定：** 
            {("超过门槛，切换为“一般纳税人”" if result["taxpayer_type"] == "一般纳税人" else "未超过门槛，维持“小规模纳税人”")}
        - **最终身份：** 
            {result["taxpayer_type"]}；**适用税率：** {pct(result["vat_rate_applied"])}
        """)

    # 详情 Step 3：增值税与附加
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("应纳增值税", cny(result["output_vat"]))
    with col_b:
        st.metric("附加税费", cny(result["surtaxes"]))
    with st.expander(f"步骤3：增值税与附加详情 | {year_label}"):
        st.markdown(f"""
        - **不含税销售额：** 
            {cny(result["sales_excl_tax"])}
        - **应纳增值税：** 
            不含税销售额 {cny(result["sales_excl_tax"])} × 适用税率 {pct(result["vat_rate_applied"])} 
            = {cny(result["output_vat"])}
        - **附加税费比例合计：** 
            城建 {pct(urban_maint_pct)} + 教育 {pct(edu_surcharge_pct)} + 地方教育 {pct(local_edu_pct)} 
            = {pct(urban_maint_pct + edu_surcharge_pct + local_edu_pct)}
        - **附加税费：** 
            应纳增值税 {cny(result["output_vat"])} × 附加比例 {pct(urban_maint_pct + edu_surcharge_pct + local_edu_pct)} 
            = {cny(result["surtaxes"])}
        > 注：未计算进项抵扣，若需更精确请加入进项参数与抵扣比。
        """)

    # 详情 Step 4：毛利与期间费用
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("毛利", cny(result["gross_profit"]))
    with col_b:
        st.metric("期间费用", cny(result["opex"]))
    with st.expander(f"步骤4：毛利与期间费用详情 | {year_label}"):
        st.markdown(f"""
        - **毛利率：** 
            {pct(gross_margin)}
        - **毛利：** 
            = 不含税销售额 {cny(result["sales_excl_tax"])} × 毛利率 {pct(gross_margin)} 
            = {cny(result["gross_profit"])}
        - **成本：** 
            = 不含税销售额 {cny(result["sales_excl_tax"])} − 毛利 {cny(result["gross_profit"])} 
            = {cny(result["cogs"])}
        - **期间费用率：** 
            {pct(opex_ratio)}
        - **期间费用：** 
            不含税销售额 {cny(result["sales_excl_tax"])} × 期间费用率 {pct(opex_ratio)} 
            = {cny(result["opex"])}
        - **会计利润（税前近似）：** 
            毛利 {cny(result["gross_profit"])} − 期间费用 {cny(result["opex"])} 
            = {cny(result["accounting_profit"])}
        """)

    # 详情 Step 5：小型微利企业判定
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("应纳税所得额", cny(result["taxable_income"]))
    with col_b:
        st.metric("小型微利企业判定", "符合" if result["is_small_micro"] else "不符合")
    with st.expander(f"步骤5：小型微利企业判定详情 | {year_label}"):
        st.markdown(f"""
        - **应纳税所得额：** 
            {cny(result["taxable_income"])}
        - **从业人数：** 
            {headcount}（要求 ≤ 300）
        - **资产总额：** 
            {cny(assets_total)}（要求 ≤ ¥50,000,000.00）
        - **行业限制：** 
            {"是" if restricted_industry else "否"}（要求为“否”）
        - **判定结果：** 
            {"符合" if result["is_small_micro"] else "不符合"}
        """)

    # 详情 Step 6：企业所得税
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("企业所得税", cny(result["eit"]))
    with col_b:
        st.metric("有效税率", pct(result['eit_effective_rate']))
    with st.expander(f"步骤6：企业所得税计算详情 | {year_label}"):
        if result["is_small_micro"]:
            portion = min(result["taxable_income"], 3_000_000.0)
            excess = max(result["taxable_income"] - 3_000_000.0, 0.0)
            st.markdown(f"""
            - **小型微利企业优惠：** 
                0–300万部分按实际5%税负，超出部分按25%
            - **0–300万部分：** 
                {cny(portion)} × 5% 
                = {cny(portion * 0.05)}
            - **超出部分：** 
                {cny(excess)} × 25% 
                = {cny(excess * 0.25)}
            - **企业所得税合计：** 
                {cny(result["eit"])}
            - **有效税率：** 
                {pct(result["eit_effective_rate"])}
            """)
        else:
            st.markdown(f"""
            - **常规税率：** 
                25%
            - **企业所得税：** 
                {cny(result["taxable_income"])} × 25% 
                = {cny(result["eit"])}
            - **有效税率：** 
                {pct(result["eit_effective_rate"])}
            """)

    # 详情 Step 7：分配与分红
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("税后净利润", cny(result["net_profit_after_eit"]))
    with col_b:
        st.metric("股东到手分红", cny(result["div_to_shareholders"]))
    with st.expander(f"步骤7：税后净利、盈余公积与分红详情 | {year_label}"):
        st.markdown(f"""
        - **税后净利润：** 
            应纳税所得额 {cny(result["taxable_income"])} − 企业所得税 {cny(result["eit"])} 
            = {cny(result["net_profit_after_eit"])}
        - **盈余公积：** 
            税后净利 {cny(result["net_profit_after_eit"])} × {pct(stat_reserve_pct)} 
            = {cny(result["stat_reserve"])}
        - **可分配利润：** 
            税后净利 {cny(result["net_profit_after_eit"])} − 盈余公积 {cny(result["stat_reserve"])} 
            = {cny(result["distributable"])}
        - **宣告分红：** 
            可分配利润 {cny(result["distributable"])} × {pct(dividend_payout_pct)} 
            = {cny(result["div_declared"])}
        - **分红个税：** 
            分红 {cny(result["div_declared"])} × {pct(dividend_iit_pct)} 
            = {cny(result["div_tax"])}
        - **股东到手分红：** 
            分红 {cny(result["div_declared"])} − 分红个税 {cny(result["div_tax"])} 
            = {cny(result["div_to_shareholders"])}
        - **留存收益：** 
            可分配利润 {cny(result["distributable"])} − 分红 {cny(result["div_declared"])} 
            = {cny(result["retained"])}
        """)


# -------------------------
# 结构化图表
# -------------------------
def render_bar_chart(year_label: str, gross_receipt: float, result: dict):
    """
    按既定顺序渲染‘结构化视图（金额）’柱状图。
    year_label: "第一年"/"第二年"/"第三年"
    gross_receipt: 当年含税收款
    result: yearly_pipeline
    """
    st.text(f"柱状图（{year_label}）")

    labels = [
        "含税收款", "不含税销售", "应纳增值税", "附加税费",
        "毛利", "期间费用", "应纳税所得额",
        "企业所得税", "税后净利润", "盈余公积",
        "分红宣告", "分红个税", "股东到手", "留存收益"
    ]
    values = [
        gross_receipt, result["sales_excl_tax"], result["output_vat"], result["surtaxes"],
        result["gross_profit"], result["opex"], result["taxable_income"],
        result["eit"], result["net_profit_after_eit"], result["stat_reserve"],
        result["div_declared"], result["div_tax"], result["div_to_shareholders"], result["retained"]
    ]

    df_chart = pd.DataFrame({"项目": labels, "金额": values})
    df_chart["项目"] = pd.Categorical(df_chart["项目"], categories=labels, ordered=True)
    df_chart = df_chart.set_index("项目")
    st.bar_chart(df_chart)


def render_waterfall_chart(year_label: str, gross_receipt: float, result: dict):
    """
    严格按照会计利润表顺序展示瀑布图：
    收入(不含税) → 成本 → 毛利 → 税金及附加 → 期间费用 → 营业利润 → 所得税 → 净利润 → 盈余公积 → 可分配利润 → 分红个税 → 股东到手 → 留存收益
    """
    st.text(f"瀑布图（{year_label}）")

    steps = [
        ("含税收款", gross_receipt, "absolute"),
        ("增值税", -result["output_vat"], "relative"),
        ("不含税销售额", result["sales_excl_tax"], "absolute"),

        ("成本", -result["cogs"], "relative"),
        ("毛利", result["gross_profit"], "absolute"),

        ("税金及附加", -result["surtaxes"], "relative"),
        ("期间费用", -result["opex"], "relative"),
        ("营业利润", result["accounting_profit"], "absolute"),

        ("企业所得税", -result["eit"], "relative"),
        ("税后净利润", result["net_profit_after_eit"], "absolute"),

        ("盈余公积", -result["stat_reserve"], "relative"),
        ("可分配利润", result["distributable"], "absolute"),

        ("分红个税", -result["div_tax"], "relative"),
        ("股东到手分红", result["div_to_shareholders"], "absolute"),

        ("留存收益", result["retained"], "absolute"),
    ]

    fig = go.Figure(go.Waterfall(
        name="资金流",
        orientation="v",
        measure=[m for _, _, m in steps],
        x=[lab for lab, _, _ in steps],
        y=[val for _, val, _ in steps],
        text=[f"{val:,.0f}" for _, val, _ in steps],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))

    fig.update_layout(
        # title=f"{year_label} 会计口径资金拆解瀑布图",
        showlegend=False,
        waterfallgap=0.3,
        yaxis_title="金额 (元)"
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sankey_chart(year_label: str, result: dict):
    """
    严格遵循会计利润表顺序的 Sankey Diagram：
    含税收款 → 增值税 + 不含税销售额
    不含税销售额 → 成本 + 毛利
    毛利 → 税金及附加 + 期间费用 + 营业利润
    营业利润 → 企业所得税 + 税后净利润
    税后净利润 → 盈余公积 + 可分配利润
    可分配利润 → 分红个税 + 股东到手分红 + 留存收益
    """
    st.text(f"桑基图（{year_label}）")

    labels = [
        "含税收款", "增值税", "不含税销售额",
        "成本", "毛利",
        "税金及附加", "期间费用", "营业利润",
        "企业所得税", "税后净利润",
        "盈余公积", "可分配利润",
        "分红个税", "股东到手分红", "留存收益"
    ]
    idx = {lab: i for i, lab in enumerate(labels)}

    sources = [
        idx["含税收款"], idx["含税收款"],
        idx["不含税销售额"], idx["不含税销售额"],
        idx["毛利"], idx["毛利"], idx["毛利"],
        idx["营业利润"], idx["营业利润"],
        idx["税后净利润"], idx["税后净利润"],
        idx["可分配利润"], idx["可分配利润"], idx["可分配利润"]
    ]

    targets = [
        idx["增值税"], idx["不含税销售额"],
        idx["成本"], idx["毛利"],
        idx["税金及附加"], idx["期间费用"], idx["营业利润"],
        idx["企业所得税"], idx["税后净利润"],
        idx["盈余公积"], idx["可分配利润"],
        idx["分红个税"], idx["股东到手分红"], idx["留存收益"]
    ]

    values = [
        result["output_vat"], result["sales_excl_tax"],
        result["cogs"], result["gross_profit"],
        result["surtaxes"], result["opex"], result["accounting_profit"],
        result["eit"], result["net_profit_after_eit"],
        result["stat_reserve"], result["distributable"],
        result["div_tax"], result["div_to_shareholders"], result["retained"]
    ]

    # 1. 流线用彩虹色循环
    rainbow_colors = [
        "rgba(148, 0,   211, 0.5)",  # 紫
        "rgba(75,  0,   130, 0.5)",  # 靛
        "rgba(0,   0,   255, 0.5)",  # 蓝
        "rgba(0,   255, 0,   0.5)",  # 绿
        "rgba(255, 255, 0,   0.5)",  # 黄
        "rgba(255, 127, 0,   0.5)",  # 橙
        "rgba(255, 0,   0,   0.5)",  # 红
    ]
    link_colors = [rainbow_colors[i % len(rainbow_colors)] for i in range(len(values))]

    # 2. 节点优先继承“上游”流线色
    node_colors: list[Optional[str]] = [None] * len(labels)
    for i, (src, tgt) in enumerate(zip(sources, targets)):
        if node_colors[tgt] is None:  # 只取第一个上游流线的颜色
            node_colors[tgt] = link_colors[i]

    # 3. 对仍为 None 的节点，尝试继承第一个下游流线色
    for node_idx in range(len(labels)):
        if node_colors[node_idx] is None:
            # 找第一个以它为 source 的 link
            downstream = [j for j, s in enumerate(sources) if s == node_idx]
            if downstream:
                node_colors[node_idx] = link_colors[downstream[0]]
            else:
                node_colors[node_idx] = "grey"  # 最后兜底

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            label=[f"¥{v:,.0f}" for v in values],
            color=link_colors
        )
    )])

    fig.update_layout(
        # title_text=f"{year_label} 企业资金流向 Sankey 图（会计口径）",
        font_size=12
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================
# 右边栏：输出
# ============================
with col_right:
    # 使用统一的渲染函数，避免重复
    for label, gross in [
        ("第一年", gross_receipt_y1),
        ("第二年", gross_receipt_y2),
        ("第三年", gross_receipt_y3),
    ]:
        rslt = yearly_pipeline(gross)

        # 渲染逐步计算结果
        render_year(label, gross, rslt)

        # 在每个年度的图表上方添加单独的选择控件
        chart_type = st.radio(
            f"选择图表类型",
            ["瀑布图", "桑基图"],
            index=1,
            horizontal=True,
            key=f"chart_type_{label}"  # 每个年度必须有唯一 key
        )

        # 根据选择渲染对应图表
        if chart_type == "瀑布图":
            render_waterfall_chart(label, gross, rslt)
        else:
            render_sankey_chart(label, rslt)
