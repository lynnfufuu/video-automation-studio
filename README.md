# 🎬 Video Automation Studio (YouTube 16:9 + TikTok 4:3)

An end-to-end automated production suite and remote control studio for generating high-retention video content:
1. **YouTube Long-Form Documentary Essay Pipeline (16:9)**: Dynamic AI narrative storytelling, Edge-TTS audio sync, chapter title cards, and zero-drift localized subtitle patch compositing.
2. **TikTok Analog Horror Studio (4:3)**: Liminal spaces, surreal VHS degradation, CRT scanlines, chromatic aberration, and eerie ambient drone soundscapes.
3. **Telegram Bot Remote Studio (`@ttytauto_bot`)**: Real-time generation triggers, emergency `/stop` process tree kill, rich hook/topic announcements, and direct account auto-publishing.
4. **Cloud On-Demand Generation (GitHub Actions)**: Generate videos 100% in the cloud from your phone via the GitHub Mobile App or Telegram webhooks, even when your computer is powered off or during power blackouts!

---

## 📱 Triggering Generations from your Phone (GitHub Actions)

Even with your laptop turned off or during power outages, you can trigger unlimited free cloud generations:
1. Open this repository in the **GitHub Mobile App** (or on your phone's browser).
2. Tap the **Actions** tab.
3. Select **Dual Studio Video Generator (Cloud Render)**.
4. Tap **Run workflow**:
   - Choose pipeline: `tiktok_analog` or `youtube_essay`.
   - Enter your keyword / prompt (e.g., `horror`, `science`, `myth`, or custom title).
   - Tap **Run workflow**.
5. GitHub will spin up a cloud runner in the US/EU, render the video, send it to your Telegram, and attach the `.mp4` under the run artifacts!

---

## 🛠️ Repository Architecture

```
video-automation-studio/
├── .github/workflows/
│   └── generate_video.yml          # Cloud generation workflow (100% free unlimited runs)
├── youtube_essay_pipeline/
│   ├── bot/
│   │   ├── telegram_server.py      # Dual Studio Telegram remote control server
│   │   ├── scenario_generator.py   # Autonomous multi-genre narrative engine
│   │   └── notifier.py             # Rich Telegram media dispatcher
│   ├── publishers/
│   │   ├── youtube_uploader.py     # Official YouTube Data API v3 uploader
│   │   └── tiktok_uploader.py      # TikTok publisher (session & mobile delivery)
│   ├── src/
│   │   ├── youtube_assembler.py    # Zero-drift 60+ FPS compositor & subtitle patcher
│   │   ├── story_generator.py      # Chapter & beat script generator
│   │   ├── tts_generator.py        # Edge-TTS sample-accurate voice engine
│   │   └── pipeline_runner.py      # Full essay orchestrator
│   └── run_telegram_bot.bat        # Windows 1-click local bot launcher
└── analog_lore_studio/
    ├── src/
    │   ├── engine.py               # TikTok analog engine
    │   ├── compositor.py           # 4:3 VHS shader compositor
    │   ├── sfx_synth.py            # Ambient drone soundscape synthesizer
    │   └── voice_engine.py         # Vintage voiceover processor
    └── run_studio.py               # Standalone runner for TikTok
```

---

## 🔐 GitHub Secrets Setup (Required for Cloud Runs)

Go to **Settings > Secrets and variables > Actions > New repository secret** and add:
- `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token (from `@BotFather`)
- `ALLOWED_CHAT_IDS`: Your Telegram numeric Chat ID
- `TIKTOK_SESSION_ID`: *(Optional)* Your TikTok Web session ID for direct upload

---

## 💻 Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Telegram Remote Control Bot
python youtube_essay_pipeline/bot/telegram_server.py
```
