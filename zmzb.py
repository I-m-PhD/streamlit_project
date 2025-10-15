import streamlit as st
from urllib.parse import urlencode, unquote
import os, random, requests, time, pandas as pd
from lxml import html


# === Crawler ===
def run_crawler(kwd, logplaceholer):
    # --- Global Settings ---
    # Log function
    logs = []  # store log lines for multi-line display
    def log(msg):
        logs.append(msg)
        # Render as a code block for console-like appearance
        # logplaceholer.code("\n".join(logs))
        # HTML with auto-scroll to bottom
        html_logs = f"""
        <div id="log-box" style="height:300px; overflow-y:auto; background-color:#111; color:#0f0; padding:10px; font-family:monospace; font-size:14px;">
            {'<br>'.join(logs)}
        </div>
        <script>
        var logBox = document.getElementById('log-box');
        logBox.scrollTop = logBox.scrollHeight;
        </script>
        """
        logplaceholer.markdown(html_logs, unsafe_allow_html=True)
    # Build URLs
    channel_ids = "204,212,213,214,215,216,217,218,219,220,221,229,230,231,233,234,235,237,238,239,241,242,243,281,282,283"
    params = {
        "kwd": kwd,
        "channelIds": channel_ids,
        "pageNo": 1,
    }
    url_base = "https://www.zmzb.com"
    url_init = f"{url_base}/cms/search.htm?{urlencode(params)}"
    # Define database
    db = os.path.join(os.getcwd(), f"{kwd}.csv")
    # Define categories
    prefix = {
        "ywgg1": "招标公告",
        "ywgg2": "非招标公告",
        "ywgg3": "变更公告",
        "ywgg4": "候选人公示",
        "ywgg5": "中标公告",
        "ywgg6": "其他公告",
    }
    suffix = {
        "gc": "工程",
        "hw": "货物",
        "fw": "服务",
    }
    # Define headers
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
        "Opera/8.0 (Windows NT 5.1; U; en)",
        "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (Linux; U; Android 2.2.1; zh-cn; HTC_Wildfire_A3333 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
        "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
        "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
        "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
        "UCWEB7.0.2.37/28/999",
        "NOKIA5700/ UCWEB7.0.2.37/28/999",
        "Openwave/ UCWEB7.0.2.37/28/999",
        "Openwave/ UCWEB7.0.2.37/28/999",
    ]
    headers_request = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "JSESSIONID=51F765B7EB94CD0F027DD340CD5515A8;"
                  "JSESSIONID=51F765B7EB94CD0F027DD340CD5515A8;"
                  "JSESSIONID=51F765B7EB94CD0F027DD340CD5515A8;",
        "User-Agent": random.choice(user_agents),
    }

    # --- Get Max Page ---
    resp_max_page = requests.get(url=url_init, headers=headers_request)
    tree_max_page = html.fromstring(html=resp_max_page.text)
    str_max_item = tree_max_page.xpath("//div[@class='search-result']/em[1]/text()")[0]
    nbr_max_item = int(str_max_item)
    # print("Total", nbr_max_item, "items.")
    log(f"Total {nbr_max_item} items.")
    str_max_page = tree_max_page.xpath("//div[@class='pag-txt']/em[2]/text()")[0]
    nbr_max_page = int(str_max_page)
    # print("Total", nbr_max_page, "pages.")
    log(f"Total {nbr_max_page} pages.")

    # --- Build URLs ---
    url_targets = [f"https://www.zmzb.com/cms/search.htm?{urlencode({**params, 'pageNo': i})}"
                   for i in range(1, nbr_max_page + 1)]
    # print([unquote(url_target) for url_target in url_targets])
    log("Target URLs:")
    for u in url_targets:
        log(unquote(u))

    # --- Scrape Each Page ---
    for url_target in url_targets:
        headers_request["User-Agent"] = random.choice(user_agents)
                                        # ^ refreshes User-Agent per page request to better mimic natural browsing
        log(f"Fetching: {unquote(url_target)}")
        try:
            resp = requests.get(url=url_target, headers=headers_request, timeout=10)
            resp.raise_for_status()
            tree = html.fromstring(html=resp.text)
            items = tree.xpath("//*[@id='list1']/li")

            results = []
            for item in items:
                # Extract attributes
                hrefs = item.xpath(".//a/@href")
                titles = item.xpath(".//a/@title")
                if not hrefs or not titles:
                    continue
                href = hrefs[0]
                title = titles[0].strip()
                url_item = href if href.startswith("https") else url_base + href
                # Extract segment, e.g. /cms/channel/ywgg5hw/50902.htm → "ywgg5hw"
                parts = href.split("/")
                seg = parts[3] if len(parts) > 3 else ""
                # Split segment, e.g. "ywgg5" + "hw"
                seg_prefix = seg[:-2]
                seg_suffix = seg[-2:]
                # Map to human-readable category
                category = f"{prefix.get(seg_prefix, '')}-{suffix.get(seg_suffix, '')}"
                # Save into results
                results.append({
                    "title": title,
                    "url": url_item,
                    "category": category,
                })

            if results:
                df = pd.DataFrame(results)
                df.to_csv(db, mode="a", header=not os.path.exists(db), index=False, encoding="utf-8")
                                        # ^ ensures the header row is only written once
                # print(f"Processed: {unquote(url_target)}")
                log(f"Processed: {unquote(url_target)} ({len(results)} records)")

        except requests.RequestException as re:
            # print(f"Skipping {url_target}: {re}")
            log(f"Skipping {url_target}: {re}")
            continue

        time.sleep(random.uniform(1, 3))

    if os.path.exists(db):
        df = pd.read_csv(db, encoding="utf-8")
        df_unique = df.drop_duplicates(subset=["title", "url", "category"], keep="first")
        return df_unique
    return None


# === Results ===
def show_results(kwd):
    db = os.path.join(os.getcwd(), f"{kwd}.csv")
    if os.path.exists(db):
        df = pd.read_csv(db, encoding="utf-8")
        return df
    return None


# === Streamlit App ===
st.set_page_config(page_title="Keyword-Based Crawler", layout="wide")
st.title(":rainbow[Keyword]-Based Crawler :sunglasses:")

col1, col2, col3 = st.columns([2, 1, 1])  # adjust ratio as needed
with col1:
    keyword = st.text_input(
        "Enter a keyword to crawl:",
        label_visibility="collapsed",
        placeholder="Enter a keyword to crawl..."
    )
with col2:
    crawl = st.button("Run Crawler", use_container_width=True)
with col3:
    show = st.button("Show Results", use_container_width=True)

db_file = os.path.join(os.getcwd(), "zmzb", f"{keyword}.csv")

if crawl:
    if keyword.strip():
        # Check if file exists
        if os.path.exists(db_file):
            st.warning(f"Data file already exists: {db_file}")
            st.info("Crawl cancelled.")
            st.stop()

        log_placeholder = st.empty()  # placeholder for multi-line logs

        with st.spinner(f"Crawling for '{keyword}'..."):
            try:
                data = run_crawler(keyword, log_placeholder)
                if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                    st.warning("No data found for that keyword.")
                else:
                    st.success(f"Crawl complete! {len(data)} records found.")
                    st.dataframe(data)
            except Exception as e:
                st.error(f"Error during crawl: {e}")
    else:
        st.warning("Please enter a keyword first!")
        st.stop()

if show:
    if keyword.strip():
        data = show_results(keyword)
        if data is None or (isinstance(data, pd.DataFrame) and data.empty):
            st.warning(f"No data found for the keyword '{keyword}'.")
        else:
            st.header("搜索结果")
            st.dataframe(data)

            st.subheader("招标公告", divider="rainbow")
            data_1 = data[data["category"].astype(str).str.match(r"^招标公告-", na=False)]
            st.dataframe(data_1)

            st.subheader("非招标公告", divider="rainbow")
            data_2 = data[data["category"].astype(str).str.match(r"^非招标公告-", na=False)]
            st.dataframe(data_2)
    else:
        st.warning("Please enter a keyword first!")
        st.stop()
