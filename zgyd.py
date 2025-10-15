import streamlit as st
import random, requests, ssl, time, json, os
from requests.adapters import HTTPAdapter
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import datetime

# --- GLOBAL SETTINGS AND UTILITIES ---

# --- API Endpoints ---
BASE_URL = 'https://b2b.10086.cn'
POST_URL = f'{BASE_URL}/api-b2b/api-sync-es/white_list_api/b2b/publish/queryList'
# 使用固定的本地文件夹来存储数据
OUTPUT_DIR = "zgyd"

# 定义所有需要采集的任务配置
TASK_CONFIG = {
    "所有招采": {"payload": {}, "name": "所有招采"},
    "正在招标": {"payload": {"homePageQueryType": "Bidding"}, "name": "所有招采_正在招标"},
    "正在招标 (北京)": {"payload": {"homePageQueryType": "Bidding", "companyType": "BJ"}, "name": "所有招采_正在招标_北京"},
}

# 用于记录数据采集时间的文件
METADATA_PATH = os.path.join(OUTPUT_DIR, "metadata.json")

# --- User Agents (Keeping the mechanism but truncating list display) ---
USER_AGENTS = [
  # ... (Keeping the robust list of User Agents for scraping) ...
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
  "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
  "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
  "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
  "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
  "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
  "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
] * 10

def get_random_headers():
    """Generates standard headers with a random User-Agent."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': f'{BASE_URL}',
        'Referer': f'{BASE_URL}/',
    }

class CustomHttpAdapter(HTTPAdapter):
    """HTTPAdapter that handles the required SSL context fix."""
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.options |= 0x4
        context.check_hostname = False
        kwargs['ssl_context'] = context
        return super(CustomHttpAdapter, self).init_poolmanager(*args, **kwargs)

# --- METADATA HANDLER ---

def load_metadata():
    """Loads the last successful crawl time for all tasks."""
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            # 文件损坏或为空，返回空字典
            return {}
    return {}

def save_metadata(metadata):
    """Saves the last successful crawl time."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

# --- DATA SCRAPING FUNCTION (Writing to Disk) ---

def scrape_content(payload_override, output_name, status_placeholder):
    """
    Scrapes data and saves it to a local JSON file.

    Args:
        payload_override (dict): Payload for the POST request.
        output_name (str): The name of the task (used for filename).
        status_placeholder (st.empty): Placeholder for dynamic status updates.

    Returns:
        bool: True if scraping was successful, False otherwise.
    """

    # Base Payload structure (defaults)
    base_payload = {
        "size": 100, "current": 1, "companyType": "", "name": "",
        "publishType": "PROCUREMENT", "publishOneType": "PROCUREMENT",
        "homePageQueryType": "", "sfactApplColumn5": "PC"
    }

    payload = base_payload.copy()
    payload.update(payload_override)
    page_size = payload['size']
    current_page = payload['current']
    all_content = []

    session = requests.Session()
    session.mount('https://', CustomHttpAdapter())

    status_placeholder.info(f"[{output_name}] 开始抓取数据...")

    success = True
    while True:
        payload['current'] = current_page
        headers = get_random_headers()

        try:
            status_placeholder.text(f"[{output_name}] 正在抓取第 {current_page} 页，当前总计 {len(all_content)} 条记录...")
            response = session.post(POST_URL, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            response_json = response.json()

            page_content = response_json.get('data', {}).get('content', [])
            content_count = len(page_content)

            if not page_content:
                status_placeholder.text(f"[{output_name}] 第 {current_page} 页无内容。抓取停止。")
                break

            all_content.extend(page_content)

            if content_count < page_size:
                status_placeholder.text(f"[{output_name}] 已达到最后一页。总计 {len(all_content)} 条记录。")
                break

            current_page += 1
            time.sleep(random.uniform(2, 5))

        except requests.exceptions.RequestException as e:
            status_placeholder.error(f"[{output_name}] 请求第 {current_page} 页时发生错误: {e}")
            success = False
            time.sleep(10)
            break
        except json.JSONDecodeError:
            status_placeholder.error(f"[{output_name}] 无法解析第 {current_page} 页的 JSON 响应。")
            success = False
            time.sleep(10)
            break

    final_count = len(all_content)

    # --- Saving Data ---
    if success and final_count > 0:
        output_path = os.path.join(OUTPUT_DIR, f"{output_name}.json")
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_content, f, indent=4, ensure_ascii=False)
            status_placeholder.success(f"[{output_name}] 抓取完成。总计记录: **{final_count}** 条。")
            return True
        except Exception as e:
            status_placeholder.error(f"[{output_name}] 写入 JSON 文件失败: {e}")
            return False
    elif final_count == 0:
        status_placeholder.warning(f"[{output_name}] 未获取到任何记录。")
        return False
    else:
        return False


# --- DATA LOADING (Reading from Disk) ---

def load_data(task_name):
    """Loads data from a local JSON file."""
    output_path = os.path.join(OUTPUT_DIR, f"{task_name}.json")
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

# --- DATA ANALYSIS AND PLOTTING FUNCTION ---

# Setting plotly template
pio.templates.default = "plotly_dark"

def show_statistics(all_content, data_name, crawl_time):
    """
    Performs feature engineering and generates plots for display in Streamlit.
    """

    st.markdown("---")
    st.header(f"数据分析: {data_name}")

    # 6. 显示数据采集时间
    if crawl_time:
        st.caption(f"数据采集时间：**{crawl_time}**")
    else:
        st.caption("尚未成功采集该任务数据。请点击上方按钮采集。")

    if not all_content:
        st.warning("无数据可供分析。")
        return

    df = pd.DataFrame(all_content)

    # ... (保持原有的日期转换、过滤、特征工程逻辑) ...
    if df.empty or 'publishDate' not in df.columns:
        st.warning("DataFrame 为空或缺少 'publishDate' 字段。无法生成图表。")
        return

    try:
        df['PublishDateTime'] = pd.to_datetime(df['publishDate'])
    except Exception as e:
        st.error(f"日期格式转换错误: {e}")
        return

    cutoff_date = pd.to_datetime('2024-01-01')
    initial_count = len(df)
    df = df[df['PublishDateTime'] >= cutoff_date]
    filtered_count = len(df)

    if initial_count != filtered_count:
        st.info(f"已过滤 {initial_count - filtered_count} 条早于 {cutoff_date.date()} 的历史噪音记录。")

    df['PublishDateOnly'] = df['PublishDateTime'].dt.date
    df['PublishHour'] = df['PublishDateTime'].dt.hour
    df['PublishDayOfWeek'] = df['PublishDateTime'].dt.day_name(locale='en_GB')
    day_map = {'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三', 'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'}
    df['PublishDayOfWeek'] = df['PublishDayOfWeek'].map(day_map)
    day_order = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    df['PublishDayOfWeek'] = pd.Categorical(df['PublishDayOfWeek'], categories=day_order, ordered=True)

    # --- Plotting Logic (保持不变，仅使用 st.plotly_chart) ---

    # PLOT 1: 每日更新频次
    st.subheader("1. 每日更新频次")
    frequency_df = df.groupby(['PublishDateOnly', 'PublishDayOfWeek'], observed=True)['PublishDateTime'].count().reset_index()
    frequency_df.columns = ['PublishDate', 'PublishDayOfWeek', 'UpdateCount']
    frequency_df = frequency_df.sort_values('PublishDate')

    fig_freq = px.bar(
        frequency_df, x='PublishDate', y='UpdateCount', title='每日更新频次 (可缩放)',
        labels={'UpdateCount': '更新频次', 'PublishDate': '日期', 'PublishDayOfWeek': '周几'},
        hover_data=['PublishDayOfWeek'], height=500
    )
    fig_freq.update_xaxes(
        tickangle=-45, rangeslider_visible=True,
        rangeselector=dict(
            bgcolor="#333333", activecolor="#555555", font=dict(color="white"),
            buttons=[
                dict(count=7, label="1周", step="day", stepmode="backward"),
                dict(count=1, label="1月", step="month", stepmode="backward"),
                dict(count=3, label="1季", step="month", stepmode="backward"),
                dict(count=1, label="1年", step="year", stepmode="backward"),
                dict(step="all", label="全部")
            ]),
        tickformat="%Y-%m-%d"
    )
    st.plotly_chart(fig_freq, use_container_width=True)

    # PLOT 2 & 3: 更新活跃时刻与热力图
    st.subheader("2. 更新活跃度分析")
    col1, col2 = st.columns(2)

    with col1:
        time_df_hour = df.groupby('PublishHour', observed=True)['PublishDateTime'].count().reset_index(name='UpdateCount')
        fig_hour = px.bar(
            time_df_hour, x='PublishHour', y='UpdateCount', title='全时段更新活跃度',
            labels={'PublishHour': '时刻 (0-23)', 'UpdateCount': '更新频次'}, height=400
        )
        fig_hour.update_layout(xaxis={'tickmode': 'linear', 'dtick': 1})
        st.plotly_chart(fig_hour, use_container_width=True)

    with col2:
        hour_order = list(range(24))
        time_df_heatmap = df.groupby(['PublishHour', 'PublishDayOfWeek'], observed=True).size().reset_index(name='UpdateCount')
        index = pd.MultiIndex.from_product([hour_order, day_order], names=['PublishHour', 'PublishDayOfWeek'])
        time_df_heatmap = time_df_heatmap.set_index(['PublishHour', 'PublishDayOfWeek']).reindex(index, fill_value=0).reset_index()
        time_df_heatmap['PublishDayOfWeek'] = pd.Categorical(time_df_heatmap['PublishDayOfWeek'], categories=day_order, ordered=True)

        fig_heatmap = px.density_heatmap(
            time_df_heatmap, x="PublishHour", y="PublishDayOfWeek", z="UpdateCount",
            title='更新活跃度: 时刻 vs. 周几',
            labels={"PublishHour": "时刻", "PublishDayOfWeek": "周几", "UpdateCount": "更新频次"},
            category_orders={"PublishDayOfWeek": day_order, "PublishHour": hour_order},
            nbinsx=24, color_continuous_scale=px.colors.sequential.Viridis, height=400
        )
        fig_heatmap.update_xaxes(range=[-0.5, 23.5], tickmode='linear', dtick=1)
        st.plotly_chart(fig_heatmap, use_container_width=True)


    # --- 新增：第 3 个板块：原始数据表格 ---
    # 仅为 '所有招采_正在招标_北京' 这个数据集添加表格
    if data_name == "所有招采_正在招标_北京":
        st.subheader("3. 原始数据表")

        # 1. 定义我们期望的列及其用户友好的名称 (已更新为 JSON 中实际存在的字段)
        required_cols_map = {
            'publishDate': '发布时间',
            'companyTypeName': '公司区域', # 根据 JSON 示例的字段进行映射
            'name': '标题',               # 使用 'name' 替换不存在的 'publishTitle'
            'tenderSaleDeadline': '截标时间',
            'backDate': '退回时间'
        }

        # 2. 检查哪些必需的列在 DataFrame (df) 中实际存在
        # 使用原始的 df (未经过日期过滤) 来确保所有原始数据都可用
        available_cols = [col for col in required_cols_map.keys() if col in df.columns]

        if not available_cols:
            st.warning("无法显示数据表：抓取的数据中缺少必要的字段。")
            # 即使无法显示表格，也不应阻止 Streamlit 运行
            return

        # 3. 仅选择存在的列，并准备重命名映射
        rename_map = {col: required_cols_map[col] for col in available_cols}

        # 4. 创建用于展示的 DataFrame (使用原始 df，然后精简列)
        display_df = df[available_cols].rename(columns=rename_map)

        # 降序排列（最新的在最上面），使用中文列名
        if '发布时间' in display_df.columns:
            display_df = display_df.sort_values(by='发布时间', ascending=False)

        # 使用 st.dataframe 展示数据表
        st.dataframe(
            display_df,
            use_container_width=True, # 占满容器宽度
            height=600 # 设定表格高度，避免页面过长
        )


# --- MAIN APPLICATION ENTRY POINT ---

def main():
    st.set_page_config(
        page_title="招采数据监控",
        layout="wide",
        initial_sidebar_state="collapsed" # 1. 不采用侧边栏模式
    )

    st.title("招采数据监控")

    # 放置用于爬虫状态和控制的容器
    status_container = st.container()

    # 5. 执行爬虫按钮
    if st.button("现在采集", type="primary"):
        # 记录开始时间
        start_time = datetime.now()

        # 使用一个总的进度条来显示整体进度
        tasks = list(TASK_CONFIG.keys())
        total_tasks = len(tasks)
        progress_bar = status_container.progress(0, text="采集初始化中...")

        metadata = load_metadata()

        for i, task_key in enumerate(tasks):
            config = TASK_CONFIG[task_key]
            # 5. 每次点击就依次采集三个数据集
            success = scrape_content(config["payload"], config["name"], status_container)

            # 5. 记录采集时间
            if success:
                metadata[config["name"]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_metadata(metadata)

            # 更新进度条
            progress_bar.progress((i + 1) / total_tasks, text=f"任务 {i+1}/{total_tasks} 完成：{config['name']}")

        progress_bar.empty() # 清除进度条
        status_container.success(f"所有任务采集完成！耗时: {datetime.now() - start_time}")

        # 强制 Streamlit 重新运行，以加载新的数据并更新图表
        st.rerun()

    # st.markdown("---")

    # 4. 优先读取本地 json 文件并显示图表
    metadata = load_metadata()

    for task_key in TASK_CONFIG.keys(): # 2. 默认展示所有三个数据集
        config = TASK_CONFIG[task_key]
        task_name = config["name"]

        # 6. 读取采集时间
        crawl_time = metadata.get(task_name)

        # 4. 读取本地数据
        raw_data = load_data(task_name)

        # 4. & 6. 展示图表和采集时间
        show_statistics(raw_data, task_name, crawl_time)


if __name__ == "__main__":
    main()