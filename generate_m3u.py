import os
import subprocess
import datetime

# 文件路径
CHANNELS_FILE = "channels.txt"
OUTPUT_FILE = "youtube_live.m3u"
COOKIES_FILE = "cookies.txt"

def log(msg):
    print(msg, flush=True)

def refresh_cookies():
    """
    从浏览器（Chrome）提取 cookies 并保存成 cookies.txt
    """
    log("🍪 正在从浏览器提取 YouTube 登录 cookie ...")
    try:
        subprocess.run(
            ["yt-dlp", "--cookies-from-browser", "chrome", "--write-cookies", COOKIES_FILE, "--skip-download", "https://www.youtube.com"],
            check=True
        )
        log("✅ cookie 已更新: cookies.txt")
    except subprocess.CalledProcessError:
        log("⚠️ 提取 cookie 失败，请确认浏览器已登录 YouTube")

def get_stream_url(video_url):
    """
    获取 YouTube 直播流地址
    """
    try:
        result = subprocess.run(
            ["yt-dlp", "-g", "--cookies", COOKIES_FILE, video_url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        log(f"❌ 获取失败: {video_url}")
        return None

def main():
    # 刷新 cookie
    refresh_cookies()

    log("\n📺 正在生成最新的 YouTube IPTV 播放列表...\n")

    m3u_lines = ["#EXTM3U"]
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue
            url, *name = line.split("#", 1)
            name = name[0].strip() if name else "未命名频道"
            url = url.strip()

            log(f"▶ 正在获取：{name}")
            stream_url = get_stream_url(url)
            if stream_url:
                m3u_lines.append(f'#EXTINF:-1 group-title="YouTube直播",{name}')
                m3u_lines.append(stream_url)
                log(f"✅ {name} 成功获取\n")
            else:
                log(f"❌ {name} 获取失败\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(m3u_lines))

    log(f"✅ 已生成最新 {OUTPUT_FILE} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

if __name__ == "__main__":
    main()
