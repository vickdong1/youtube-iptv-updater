5️⃣ README.md（可选）
# YouTube IPTV Updater

这个项目可以每天自动更新你的 YouTube 直播 IPTV M3U 播放列表。

## 使用方法

1. 在 `channels.txt` 添加你的 YouTube 直播频道，每行格式：


https://www.youtube.com/watch?v=xxxxx
 # 频道名称


2. Python 环境运行：
```bash
pip install yt-dlp
python generate_m3u.py


GitHub Actions 会每天自动更新 youtube_live.m3u 文件。


---

这个完整项目直接上传到 GitHub，手动执行一次 Actions 就可以生成 `youtube_live.m3u`。  
之后每天自动刷新直播地址，无需手动干预。

---

如果你需要，我可以帮你**修改版本，使得生成的 M3U 文件同时支持 VLC、iOS/IPTV App 直接播放 YouTube Live**，保证大部分设备都能播。  

你希望我帮你做吗？
