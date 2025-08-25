import requests
from bs4 import BeautifulSoup
import os

# 从 GitHub Secrets 读取 Server酱 KEY（后面会配置）
SERVERCHAN_KEY = os.getenv("SERVERCHAN_KEY")

def send_message(title, content):
    """使用 Server酱 API 推送到微信"""
    if not SERVERCHAN_KEY:
        print("❌ 没有找到 SERVERCHAN_KEY，请在 GitHub Secrets 里配置")
        return
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data, timeout=15)
        print("推送结果：", resp.text)
    except Exception as e:
        print("推送异常：", e)

def get_articles(wechat_id):
    """示例：通过搜狗微信检索公众号并抓取最新文章（页面结构变动时需调整选择器）"""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    # 1) 搜索公众号
    search_url = f"https://weixin.sogou.com/weixin?type=1&query={wechat_id}"
    r1 = requests.get(search_url, headers=headers, timeout=20)
    soup1 = BeautifulSoup(r1.text, "lxml")
    account_link = soup1.select_one(".tit a")
    if not account_link:
        print("未找到公众号：", wechat_id)
        return []

    # 2) 进入公众号聚合页
    account_url = account_link["href"]
    r2 = requests.get(account_url, headers=headers, timeout=20)
    soup2 = BeautifulSoup(r2.text, "lxml")

    # 3) 解析文章卡片（以下选择器基于常见结构，如有变动需适配）
    articles = []
    for item in soup2.select(".weui_media_box"):
        title_el = item.select_one(".weui_media_title")
        date_el = item.select_one(".weui_media_extra_info")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        # hrefs 是搜狗用于跳转的属性（注意不是 href）
        hrefs = title_el.get("hrefs")
        url = ("https://weixin.sogou.com" + hrefs) if hrefs else None
        date = date_el.get_text(strip=True) if date_el else ""
        if url:
            articles.append((title, url, date))

    return articles

def main():
    # 👉 在这里配置你要监控的公众号名称（可改成你的清单）
    wechat_list = ["南大后勤", "南大就业","南大青年","南大青协","南大社团","南大全球交流","南大社团","南大体育","南大研会","南大研招","南京大学","南京大学本科教育","南京大学心理中心","南京大学学生会","南京大学研究生教育","南哪助手","南青科创","南青实践"]
    all_msgs = []
    for account in wechat_list:
        arts = get_articles(account)
        if arts:
            for title, url, date in arts[:3]:  # 每个号取最新3条
                all_msgs.append(f"### {title}\n- 链接: {url}\n- 时间: {date}\n")
        else:
            all_msgs.append(f"**{account}**：未获取到文章（可能被反爬或结构变更）")

    if all_msgs:
        send_message("公众号新消息提醒", "\n\n".join(all_msgs))
    else:
        print("未获取到任何文章")

if __name__ == "__main__":
    main()