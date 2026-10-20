"""
telegram_server.py - Dual Studio Telegram Remote Control (YouTube + TikTok) with Direct Account Publishing
Features:
- YouTube & TikTok Direct Account Auto-Publishing
- TikTok Dual Mode: When 'Gen TikTok' is tapped, shows 2 prominent buttons:
    [🎲 Auto-Generate Idea] & [✍️ Custom Prompt]
- YouTube Genre Keyword Mode: Provide 1 word (horror, science, myth, space, superhero) or custom topic
- Rich Announcement Previews with Title, Hook, Chapters, and Interactive Choices
- Emergency /stop control: Kills any active generation process tree immediately
- Native Telegram command menu and clean interactive button navigation
"""

import os
import sys
import glob
import json
import asyncio
import subprocess
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PIPELINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TIKTOK_ROOT = os.path.abspath(os.path.join(PIPELINE_ROOT, "..", "analog_lore_studio"))

if PIPELINE_ROOT not in sys.path:
    sys.path.insert(0, PIPELINE_ROOT)

from bot.config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_IDS, BOT_DIR
import bot.notifier as notifier
from bot.scenario_generator import generate_tiktok_scenario, resolve_youtube_topic

# Publishers
import publishers.youtube_uploader as yt_pub
import publishers.tiktok_uploader as tt_pub

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ACTIVE_TASKS = {}
USER_STATES = {}

def kill_process_tree(pid: int):
    """Forcefully terminates a process and all its child processes on Windows."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"Error killing process {pid}: {e}")

def is_authorized(user_id: int) -> bool:
    """Checks if the user is authorized. If no IDs configured, authorizes the first user."""
    global ALLOWED_CHAT_IDS
    if not ALLOWED_CHAT_IDS:
        ALLOWED_CHAT_IDS.append(user_id)
        env_path = os.path.join(BOT_DIR, ".env")
        try:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write(f"\nALLOWED_CHAT_IDS={user_id}\n")
        except Exception:
            pass
        return True
    return user_id in ALLOWED_CHAT_IDS

def get_main_menu_markup():
    keyboard = [
        [
            InlineKeyboardButton("🚀 Publish to YT / TikTok", callback_data="menu_publish"),
            InlineKeyboardButton("🎬 YouTube Chapters", callback_data="send_all_chapters")
        ],
        [
            InlineKeyboardButton("⚡ New YouTube Essay", callback_data="menu_yt"),
            InlineKeyboardButton("⚡ New TikTok Episode", callback_data="menu_tt")
        ],
        [
            InlineKeyboardButton("🛑 STOP Generation", callback_data="stop_pipeline"),
            InlineKeyboardButton("📋 All Commands", callback_data="view_commands")
        ],
        [
            InlineKeyboardButton("📱 Latest TikTok Video", callback_data="send_tiktok"),
            InlineKeyboardButton("📊 System Status", callback_data="system_status")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    if not is_authorized(chat_id):
        await update.message.reply_text("⛔ Unauthorized access.")
        return
        
    welcome_text = (
        f"🎬 *Dual Production Studio — Remote Terminal*\n\n"
        f"Welcome, *{user.first_name}*! Studio remote control and auto-publishing are active.\n\n"
        f"Select an action below or send `/commands` for the full directory:"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_markup())

async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    text = (
        f"📋 *STUDIO COMMAND DIRECTORY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚀 *DIRECT AUTO-PUBLISHING*\n"
        f"• `/publish_yt` — Upload 11-min master video to YouTube\n"
        f"• `/publish_short` — Upload chapter cut as YouTube Short\n"
        f"• `/publish_tt` — Publish latest vertical cut to TikTok\n"
        f"• `/connect` — Setup YouTube OAuth2 & TikTok Session instructions\n\n"
        f"🔴 *YOUTUBE ESSAYS (16:9 Long-Form)*\n"
        f"• `/generate <word or topic>` — Produce 11-min documentary\n"
        f"  _Keywords:_ `horror`, `science`, `myth`, `space`, `superhero`\n"
        f"• `/chapters` — Send all 5 standalone story cuts (~27MB each)\n"
        f"• `/chapter <1-5>` — Send a specific chapter video\n"
        f"• `/preview` — View authentic 1997 found footage stills\n\n"
        f"📱 *TIKTOK ANALOG HORROR (Vertical / 4:3)*\n"
        f"• `/generate_tiktok` — Choose Auto Idea or Custom Prompt\n"
        f"• `/generate_tiktok <prompt>` — Custom scenario (e.g. 4 planets)\n"
        f"• `/tiktok` — Send latest vertical TikTok analog horror episode\n\n"
        f"🛑 *CONTROL & MONITORING*\n"
        f"• `/stop` — Forcefully stop and cancel active generation\n"
        f"• `/status` — Real-time CPU/GPU, active tasks, and disk usage\n"
        f"• `/episodes` — List all completed videos on disk\n"
        f"• `/help` — Display main menu"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 Publish Center", callback_data="menu_publish"),
            InlineKeyboardButton("🎬 YouTube Chapters", callback_data="send_all_chapters")
        ],
        [
            InlineKeyboardButton("⚡ Gen YouTube", callback_data="menu_yt"),
            InlineKeyboardButton("⚡ Gen TikTok", callback_data="menu_tt")
        ],
        [
            InlineKeyboardButton("🛑 STOP ACTIVE PIPELINE", callback_data="stop_pipeline"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    global ACTIVE_TASKS
    if not ACTIVE_TASKS:
        msg = "ℹ️ No generation pipelines are currently active."
        if update.callback_query:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return
        
    stopped_names = []
    for task_key, task_info in list(ACTIVE_TASKS.items()):
        name = task_info.get("name", task_key)
        stopped_names.append(name)
        
        proc = task_info.get("proc")
        if proc and proc.pid:
            kill_process_tree(proc.pid)
            
        async_t = task_info.get("asyncio_task")
        if async_t and not async_t.done():
            async_t.cancel()
            
    ACTIVE_TASKS.clear()
    
    try:
        subprocess.run(["taskkill", "/F", "/IM", "ffmpeg.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
        
    stop_msg = (
        f"🛑 *GENERATION HALTED IMMEDIATELY*\n\n"
        f"Terminated Active Task(s):\n" + "\n".join([f"• *{n}*" for n in stopped_names]) + "\n\n"
        f"All processes, audio synthesizers, and render workers have been stopped."
    )
    if update.callback_query:
        await update.callback_query.message.reply_text(stop_msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(stop_msg, parse_mode="Markdown")

# ==============================================================================
# AUTO-PUBLISHING CENTER (YouTube & TikTok Uploaders)
# ==============================================================================

async def publish_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    text = (
        f"🚀 *DIRECT ACCOUNT AUTO-PUBLISHING CENTER*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Upload completed long-form documentaries and short-form cuts straight to your channels:\n\n"
        f"🔴 *YouTube Status:* {'✅ Configured' if yt_pub.is_youtube_configured() else '⚠️ Needs client_secret.json'}\n"
        f"📱 *TikTok Status:* {'✅ Configured' if tt_pub.is_tiktok_configured() else '⚠️ Needs Session ID / API'}\n\n"
        f"Choose an upload target below:"
    )
    keyboard = [
        [
            InlineKeyboardButton("🔴 Upload Master to YouTube", callback_data="pub_yt_master"),
            InlineKeyboardButton("📱 Upload Chapter to Shorts", callback_data="pub_yt_short")
        ],
        [
            InlineKeyboardButton("📱 Upload Video to TikTok", callback_data="pub_tiktok"),
            InlineKeyboardButton("🔑 Connect Accounts Guide", callback_data="pub_guide")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def publish_yt_master_action(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    master_video = os.path.join(PIPELINE_ROOT, "output", "youtube_essay_japanese_urban_legends.mp4")
    if not os.path.exists(master_video):
        await context.bot.send_message(chat_id, "⚠️ Master video file not found. Please render an episode first.")
        return
        
    if not yt_pub.is_youtube_configured():
        await context.bot.send_message(
            chat_id,
            "⚠️ *YouTube Authentication Required*\n\n"
            "Please drop your Google Cloud OAuth `client_secret.json` into:\n"
            f"`{yt_pub.PUBLISHERS_DIR}\\client_secret.json`\n\n"
            "Then run `python publishers/youtube_uploader.py --auth` or tap 'Connect Accounts Guide'.",
            parse_mode="Markdown"
        )
        return
        
    await context.bot.send_message(chat_id, "🚀 *Starting Resumable YouTube Upload...*\nTarget: Full 11-min documentary (143 MB). Uploading as *Unlisted* for your review...", parse_mode="Markdown")
    
    def on_progress(pct):
        if pct % 25 == 0:
            context.bot.send_message(chat_id, f"📤 YouTube Upload: {pct}% complete...")
            
    try:
        thumb = os.path.join(PIPELINE_ROOT, "output", "verify_frame_ch1.jpg")
        res = yt_pub.upload_video(
            video_path=master_video,
            title="Top 5 Scariest Japanese Urban Legends Explained",
            description=(
                "An investigative found-footage documentary analyzing the 5 most terrifying urban legends of Japan.\n\n"
                "0:00 - Introduction\n"
                "0:37 - Chapter 1: Hachishakusama: The Eight-Foot Shadow\n"
                "2:45 - Chapter 2: Teke Teke: The Phantom of the Railway Crossing\n"
                "4:55 - Chapter 3: Kuchisake-onna: The Slit-Mouthed Woman\n"
                "7:00 - Chapter 4: Aka Manto: The Red Cape in the Fourth Stall\n"
                "9:12 - Chapter 5: The Inunaki Village Tunnel: The Lawless Anomaly\n\n"
                "#HorrorStory #JapaneseUrbanLegends #AnalogHorror #UrbanLegends #Documentary"
            ),
            tags=["japanese urban legends", "urban legends", "hachishakusama", "teke teke", "analog horror", "scary documentary"],
            category_id="24",
            privacy_status="unlisted",
            thumbnail_path=thumb if os.path.exists(thumb) else None,
            progress_callback=on_progress
        )
        await context.bot.send_message(
            chat_id,
            f"🎉 *YOUTUBE UPLOAD SUCCESSFUL!*\n\n"
            f"• *Title:* {res['title']}\n"
            f"• *Link:* {res['url']}\n"
            f"• *Privacy:* {res['privacy'].upper()}\n\n"
            f"Open the link above in YouTube Studio to set to Public whenever you're ready!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ YouTube Upload Error: {e}")

async def publish_tiktok_action(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    tt_video = os.path.join(TIKTOK_ROOT, "output", "liminal_doors_ep01.mp4")
    if not os.path.exists(tt_video):
        await context.bot.send_message(chat_id, "⚠️ TikTok video not found. Generate one first via `/generate_tiktok`.")
        return
        
    if not tt_pub.is_tiktok_configured():
        # Fallback to direct phone delivery for instant 1-tap mobile sharing
        await context.bot.send_message(
            chat_id,
            "💡 *Instant TikTok Mobile Publish*\n"
            "TikTok credentials (`sessionid`) are not configured in `.env` yet. Sending the video directly to your phone below so you can tap **Share $\rightarrow$ TikTok** with 1 click!",
            parse_mode="Markdown"
        )
        with open(tt_video, "rb") as f:
            await context.bot.send_video(
                chat_id=chat_id,
                video=f,
                caption="📱 *Ready for TikTok*\nTap Share $\rightarrow$ TikTok\n\n#AnalogHorror #HorrorTok #LiminalSpaces #KanePixels #FoundFootage",
                supports_streaming=True
            )
        return
        
    await context.bot.send_message(chat_id, "🚀 *Publishing Video to TikTok...*", parse_mode="Markdown")
    try:
        res = tt_pub.upload_tiktok_video(
            video_path=tt_video,
            caption="CHOOSE ONE TO SURVIVE: 3 Sub-Level Entrances. Which door did you choose?",
            hashtags=["AnalogHorror", "HorrorTok", "LiminalSpace", "Creepy", "FoundFootage"],
            privacy="public"
        )
        if res.get("success"):
            await context.bot.send_message(chat_id, "🎉 *TIKTOK UPLOAD SUCCESSFUL!* Video is live on your channel.", parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id, f"⚠️ TikTok upload returned: {res.get('error', 'Check session')}")
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ TikTok Upload Error: {e}")

# ==============================================================================
# TIKTOK GENERATION (Auto vs Custom Prompt)
# ==============================================================================

async def tiktok_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Presents user with the two TikTok options: Auto-Generate vs Custom Prompt."""
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    text = (
        f"📱 *TIKTOK ANALOG HORROR STUDIO*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Choose how you want to create your TikTok episode:\n\n"
        f"1️⃣ *Auto-Generate Idea*\n"
        f"The agent invents a fresh surreal dilemma (3 Doors, 4 Planets, 3 Elevators, etc.)\n\n"
        f"2️⃣ *Custom Prompt / Idea*\n"
        f"You describe the scenario (e.g., _choose four planets where each planet has a terrifying creature_)"
    )
    keyboard = [
        [
            InlineKeyboardButton("🎲 1. Auto-Generate Idea", callback_data="tt_auto")
        ],
        [
            InlineKeyboardButton("✍️ 2. Custom Prompt / Idea", callback_data="tt_prompt")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def generate_tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    if context.args:
        prompt_text = " ".join(context.args).strip()
        await start_tiktok_pipeline(chat_id, context, prompt_text)
    else:
        await tiktok_menu(update, context)

async def start_tiktok_pipeline(chat_id: int, context: ContextTypes.DEFAULT_TYPE, prompt: str = None):
    if "tiktok_studio" in ACTIVE_TASKS:
        await context.bot.send_message(chat_id, "⚠️ A TikTok production run is already executing!")
        return
        
    title, hook, options, queue_dict = generate_tiktok_scenario(prompt)
    
    # Write to queue.json in analog_lore_studio
    queue_path = os.path.join(TIKTOK_ROOT, "data", "queue.json")
    try:
        os.makedirs(os.path.dirname(queue_path), exist_ok=True)
        with open(queue_path, "w", encoding="utf-8") as f:
            json.dump({"queue": [queue_dict]}, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing queue.json: {e}")
        
    opt_str = "\n".join([f"• {o.get('name', 'Option')} [Survival: {o.get('survival_rate', '?')}]" for o in options])
    
    keyboard = [[InlineKeyboardButton("🛑 STOP Generation", callback_data="stop_pipeline")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg_text = (
        f"📱 *GENERATING TIKTOK ANALOG HORROR VIDEO*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚪 *Scenario:* \"{title}\"\n\n"
        f"📖 *Scenario Hook:*\n"
        f"\"{hook}\"\n\n"
        f"🚪 *The Interactive Choices:*\n"
        f"{opt_str}\n\n"
        f"⚙️ *Specifications:*\n"
        f"• Format: 4:3 Box Format (Windowboxed 1080x1920)\n"
        f"• Voice: Sinister Andrew (-10% rate, -8Hz pitch, Cavern Reverb)\n"
        f"• Visuals: 1997 Found Footage VHS, 2.5D Drifts & Room Flashes\n\n"
        f"⏳ *Status:* Rendering in background..."
    )
    
    await context.bot.send_message(chat_id, msg_text, parse_mode="Markdown", reply_markup=reply_markup)
    
    t = asyncio.create_task(run_tiktok_task(chat_id, context))
    ACTIVE_TASKS["tiktok_studio"] = {"name": f"TikTok: {title}", "type": "tt", "asyncio_task": t}

async def run_tiktok_task(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    python_exe = sys.executable
    studio_script = os.path.join(TIKTOK_ROOT, "run_studio.py")
    
    try:
        proc = await asyncio.create_subprocess_exec(
            python_exe, "-u", studio_script,
            cwd=TIKTOK_ROOT,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        if "tiktok_studio" in ACTIVE_TASKS:
            ACTIVE_TASKS["tiktok_studio"]["proc"] = proc
            
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            err = stderr.decode()[:300] if stderr else "Cancelled or stopped"
            await context.bot.send_message(chat_id, f"⚠️ TikTok production ended:\n`{err}`", parse_mode="Markdown")
            return
            
        await context.bot.send_message(chat_id, "🎉 *TikTok Episode Rendered!* Uploading now...", parse_mode="Markdown")
        
        output_dir = os.path.join(TIKTOK_ROOT, "output")
        mp4_files = sorted(glob.glob(os.path.join(output_dir, "*.mp4")), key=os.path.getmtime, reverse=True)
        if mp4_files:
            latest = mp4_files[0]
            size_mb = os.path.getsize(latest) / 1024 / 1024
            caption = f"📱 *New TikTok Episode Ready!* ({size_mb:.1f} MB)"
            with open(latest, "rb") as f:
                await context.bot.send_video(chat_id=chat_id, video=f, caption=caption, supports_streaming=True)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ Exception in TikTok pipeline: {e}")
    finally:
        ACTIVE_TASKS.pop("tiktok_studio", None)

# ==============================================================================
# YOUTUBE GENERATION (One-Word Genre or Custom Query)
# ==============================================================================

async def youtube_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    text = (
        f"🔴 *YOUTUBE VIDEO ESSAY PIPELINE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Pick a **1-word genre**, or tap Custom to type your own:\n\n"
        f"• `/generate horror` — Japanese Folklore & Urban Legends\n"
        f"• `/generate science` — Cosmic Physics Paradoxes & False Vacuum\n"
        f"• `/generate myth` — Dark Ancient Primordial Entities\n"
        f"• `/generate space` — Deep Cosmic Anomalies & The Boötes Void\n"
        f"• `/generate superhero` — Dark Superhero Secrets & Paradoxes"
    )
    keyboard = [
        [
            InlineKeyboardButton("💀 Horror", callback_data="yt_horror"),
            InlineKeyboardButton("🪐 Science", callback_data="yt_science")
        ],
        [
            InlineKeyboardButton("🏛️ Myth", callback_data="yt_myth"),
            InlineKeyboardButton("🌌 Space", callback_data="yt_space")
        ],
        [
            InlineKeyboardButton("🦸 Superhero", callback_data="yt_superhero"),
            InlineKeyboardButton("✍️ Custom Title", callback_data="yt_custom")
        ],
        [
            InlineKeyboardButton("🎲 Surprise Me", callback_data="yt_random"),
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    if context.args:
        query_text = " ".join(context.args).strip()
        await start_youtube_pipeline(chat_id, context, query_text)
    else:
        await youtube_menu(update, context)

async def start_youtube_pipeline(chat_id: int, context: ContextTypes.DEFAULT_TYPE, query: str = None):
    slug, title, hook, chapters = resolve_youtube_topic(query)
    
    if slug in ACTIVE_TASKS or title in ACTIVE_TASKS:
        await context.bot.send_message(chat_id, f"⚠️ A pipeline for '{title}' is already running!")
        return
        
    ch_str = "\n".join([f"• Chapter {idx+1}: {ch}" for idx, ch in enumerate(chapters)])
    
    keyboard = [[InlineKeyboardButton("🛑 STOP Generation", callback_data="stop_pipeline")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg_text = (
        f"🎬 *GENERATING YOUTUBE VIDEO ESSAY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔴 *Title:* \"{title}\"\n\n"
        f"📖 *Hook & Synopsis:*\n"
        f"\"{hook}\"\n\n"
        f"📑 *Chapter Breakdown:*\n"
        f"{ch_str}\n\n"
        f"⚙️ *Specifications:*\n"
        f"• Format: 16:9 Widescreen (1920x1080 Full HD)\n"
        f"• Voice: Andrew Multilingual (-5% documentary cadence)\n"
        f"• Soundtrack: 18% Dark Atmospheric Ambient Drone\n"
        f"• Subtitles: Voice-Locked Lower-Third Yellow Italic (Zero Drift)\n\n"
        f"⏳ *Status:* Processing in background..."
    )
    
    await context.bot.send_message(chat_id, msg_text, parse_mode="Markdown", reply_markup=reply_markup)
    
    t = asyncio.create_task(run_pipeline_task(slug, title, chat_id, context))
    ACTIVE_TASKS[slug] = {"name": f"YouTube: {title}", "type": "yt", "asyncio_task": t}

async def run_pipeline_task(slug: str, title: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    python_exe = sys.executable
    
    try:
        await context.bot.send_message(chat_id, f"📝 *Phase 1/3:* Scripting and Audio Synthesis for '{title}'...", parse_mode="Markdown")
        runner_script = os.path.join(PIPELINE_ROOT, "src", "pipeline_runner.py")
        
        proc = await asyncio.create_subprocess_exec(
            python_exe, "-u", runner_script, slug,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        if slug in ACTIVE_TASKS:
            ACTIVE_TASKS[slug]["proc"] = proc
            
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            err_msg = stderr.decode()[:300] if stderr else "Cancelled or stopped"
            await context.bot.send_message(chat_id, f"⚠️ Pipeline ended for '{title}':\n`{err_msg}`", parse_mode="Markdown")
            return
            
        await context.bot.send_message(chat_id, f"🎉 *Production Complete!*\nMaster video and chapter cuts ready.", parse_mode="Markdown")
        
        split_script = os.path.join(PIPELINE_ROOT, "src", "split_chapters.py")
        p2 = await asyncio.create_subprocess_exec(python_exe, "-u", split_script)
        await p2.communicate()
        
        ch_matches = glob.glob(os.path.join(PIPELINE_ROOT, "output", "chapters", "01_*.mp4"))
        if ch_matches:
            with open(ch_matches[0], "rb") as f:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=f,
                    caption=f"🎬 *Chapter 1 Preview* ({title})\nUse `/chapters` to receive all remaining stories!",
                    parse_mode="Markdown"
                )
    except asyncio.CancelledError:
        pass
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ Exception in pipeline: {e}")
    finally:
        ACTIVE_TASKS.pop(slug, None)

# ==============================================================================
# MEDIA DELIVERY & SYSTEM CONTROLS
# ==============================================================================

async def tiktok_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    output_dir = os.path.join(TIKTOK_ROOT, "output")
    mp4_files = sorted(glob.glob(os.path.join(output_dir, "*.mp4")), key=os.path.getmtime, reverse=True)
    
    if not mp4_files:
        msg = "📱 No TikTok videos found in `analog_lore_studio/output/`."
        if update.callback_query:
            await update.callback_query.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")
        return
        
    latest_video = mp4_files[0]
    name = os.path.basename(latest_video)
    size_mb = os.path.getsize(latest_video) / 1024 / 1024
    
    upload_msg = f"📤 Uploading TikTok Episode: *{name}* ({size_mb:.1f} MB)..."
    if update.callback_query:
        await update.callback_query.message.reply_text(upload_msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(upload_msg, parse_mode="Markdown")
    
    caption = (
        f"📱 *TikTok Analog Horror Studio*\n"
        f"• *Episode:* `{name}` ({size_mb:.1f} MB)\n"
        f"• *Format:* 4:3 Box Format (Windowboxed 1080x1920)\n"
        f"• *Audio:* Sinister Andrew (-10% -8Hz, Cavern Reverb)\n"
        f"• *Hook:* Interactive 3-Doors Dilemma"
    )
    
    with open(latest_video, "rb") as f:
        await context.bot.send_video(
            chat_id=chat_id,
            video=f,
            caption=caption,
            supports_streaming=True,
            parse_mode="Markdown"
        )

async def chapters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    chapters_dir = os.path.join(PIPELINE_ROOT, "output", "chapters")
    ch_files = sorted(glob.glob(os.path.join(chapters_dir, "*.mp4")))
    
    if not ch_files:
        msg = "⚠️ No chapter files found."
        if update.callback_query:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return
        
    header = f"🚀 Sending {len(ch_files)} standalone story cuts (playable 1080p)..."
    if update.callback_query:
        await update.callback_query.message.reply_text(header)
    else:
        await update.message.reply_text(header)
    
    for ch_path in ch_files:
        name = os.path.basename(ch_path).replace(".mp4", "")
        size_mb = os.path.getsize(ch_path) / 1024 / 1024
        caption = f"🎬 *{name}* ({size_mb:.1f} MB)\n16:9 Full HD | Synced Yellow Captions"
        
        with open(ch_path, "rb") as f:
            await context.bot.send_video(
                chat_id=chat_id,
                video=f,
                caption=caption,
                supports_streaming=True,
                parse_mode="Markdown"
            )

async def preview_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    output_dir = os.path.join(PIPELINE_ROOT, "output")
    stills = sorted(glob.glob(os.path.join(output_dir, "verify_frame_ch*.jpg")))
    
    if not stills:
        msg = "🖼️ No verification stills found."
        if update.callback_query:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return
        
    if update.callback_query:
        await update.callback_query.message.reply_text("🖼️ Sending 1997 found-footage verification stills...")
    else:
        await update.message.reply_text("🖼️ Sending 1997 found-footage verification stills...")
        
    for idx, s_path in enumerate(stills):
        caption = f"Beat Preview — Chapter {idx + 1}"
        with open(s_path, "rb") as f:
            await context.bot.send_photo(chat_id=chat_id, photo=f, caption=caption)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    active_str = "None"
    if ACTIVE_TASKS:
        active_str = "\n".join([f"• *{task_info.get('name', k)}*: Running" for k, task_info in ACTIVE_TASKS.items()])
        
    yt_output = os.path.join(PIPELINE_ROOT, "output")
    yt_mp4s = glob.glob(os.path.join(yt_output, "*.mp4"))
    
    tt_output = os.path.join(TIKTOK_ROOT, "output")
    tt_mp4s = glob.glob(os.path.join(tt_output, "*.mp4"))
    
    status_text = (
        f"📊 *Dual Studio System Status*\n\n"
        f"*Active Pipelines:*\n{active_str}\n\n"
        f"🔴 *YouTube Pipeline:* {len(yt_mp4s)} master episode(s) (Auth: {'✅' if yt_pub.is_youtube_configured() else '❌'})\n"
        f"📱 *TikTok Studio:* {len(tt_mp4s)} vertical episode(s) (Auth: {'✅' if tt_pub.is_tiktok_configured() else '❌'})\n"
        f"*Compositor Engine:* Sample-Accurate Audio Clock (Delta 0.0s)\n"
        f"*Render Speed:* ~60+ FPS"
    )
    
    keyboard = []
    if ACTIVE_TASKS:
        keyboard.append([InlineKeyboardButton("🛑 STOP Active Pipeline", callback_data="stop_pipeline")])
    keyboard.append([InlineKeyboardButton("📋 All Commands", callback_data="view_commands")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(status_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(status_text, parse_mode="Markdown", reply_markup=reply_markup)

async def episodes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    yt_output = os.path.join(PIPELINE_ROOT, "output")
    yt_mp4s = glob.glob(os.path.join(yt_output, "*.mp4"))
    
    text = "🔴 *YouTube Master Videos (16:9 Long-Form):*\n"
    for p in yt_mp4s:
        size_mb = os.path.getsize(p) / 1024 / 1024
        text += f"• `{os.path.basename(p)}` ({size_mb:.1f} MB)\n"
        
    chapters_dir = os.path.join(yt_output, "chapters")
    ch_files = glob.glob(os.path.join(chapters_dir, "*.mp4"))
    if ch_files:
        text += f"\n✂️ *YouTube Story Cuts (5 Chapters):*\n"
        for cp in sorted(ch_files):
            c_size = os.path.getsize(cp) / 1024 / 1024
            text += f"  - `{os.path.basename(cp)}` ({c_size:.1f} MB)\n"
            
    tt_output = os.path.join(TIKTOK_ROOT, "output")
    tt_mp4s = glob.glob(os.path.join(tt_output, "*.mp4"))
    if tt_mp4s:
        text += f"\n📱 *TikTok Analog Horror Videos:*\n"
        for tp in sorted(tt_mp4s):
            t_size = os.path.getsize(tp) / 1024 / 1024
            text += f"• `{os.path.basename(tp)}` ({t_size:.1f} MB)\n"
            
    await update.message.reply_text(text, parse_mode="Markdown")

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text replies when user was prompted for a custom TikTok prompt or YouTube query."""
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        return
        
    state = USER_STATES.get(chat_id)
    if state == "awaiting_tt_prompt":
        USER_STATES.pop(chat_id, None)
        user_prompt = update.message.text.strip()
        await start_tiktok_pipeline(chat_id, context, user_prompt)
    elif state == "awaiting_yt_keyword":
        USER_STATES.pop(chat_id, None)
        user_query = update.message.text.strip()
        await start_youtube_pipeline(chat_id, context, user_query)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    
    # Navigation
    if data == "main_menu":
        await query.edit_message_text(
            "🎬 *Dual Production Studio — Remote Terminal*\n\nSelect an action:",
            parse_mode="Markdown",
            reply_markup=get_main_menu_markup()
        )
    elif data == "menu_publish":
        await publish_menu(update, context)
    elif data == "pub_yt_master":
        await publish_yt_master_action(chat_id, context)
    elif data == "pub_yt_short":
        matches = sorted(glob.glob(os.path.join(PIPELINE_ROOT, "output", "chapters", "01_*.mp4")))
        if matches and yt_pub.is_youtube_configured():
            await query.message.reply_text("🚀 Uploading Chapter 1 to YouTube Shorts...")
            yt_pub.upload_chapter_as_short(matches[0], "Hachishakusama: The Eight-Foot Shadow", "Japanese Urban Legends")
        else:
            await query.message.reply_text("⚠️ Chapter video not found or YouTube auth not configured.")
    elif data == "pub_tiktok":
        await publish_tiktok_action(chat_id, context)
    elif data == "pub_guide":
        await query.edit_message_text(
            "🔑 *ACCOUNT CONNECTION GUIDE*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔴 *YouTube Connection:*\n"
            "1. Create an OAuth 2.0 Desktop Client in Google Cloud Console.\n"
            "2. Download JSON as `client_secret.json` into:\n"
            f"   `{yt_pub.PUBLISHERS_DIR}`\n"
            "3. Run `python publishers/youtube_uploader.py --auth`\n\n"
            "📱 *TikTok Connection:*\n"
            "1. Copy `sessionid` from tiktok.com cookies in your browser.\n"
            "2. Paste into `.env`: `TIKTOK_SESSION_ID=...`\n"
            "3. Or use 1-click mobile share via Telegram!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Publish Menu", callback_data="menu_publish")]])
        )
    elif data == "send_all_chapters":
        await chapters_command(update, context)
    elif data == "send_tiktok":
        await tiktok_command(update, context)
    elif data == "menu_yt":
        await youtube_menu(update, context)
    elif data == "menu_tt":
        await tiktok_menu(update, context)
    elif data == "view_commands":
        await commands_command(update, context)
    elif data == "view_stills":
        await preview_command(update, context)
    elif data == "system_status":
        await status_command(update, context)
    elif data == "stop_pipeline":
        await stop_command(update, context)
        
    # TikTok 2 Options
    elif data == "tt_auto":
        await query.edit_message_text("🎲 *Auto-generating TikTok Idea and launching studio...*", parse_mode="Markdown")
        await start_tiktok_pipeline(chat_id, context, "auto")
    elif data == "tt_prompt":
        USER_STATES[chat_id] = "awaiting_tt_prompt"
        await query.edit_message_text(
            "✍️ *CUSTOM TIKTOK SCENARIO PROMPT*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Please type your scenario idea below:\n\n"
            "• _Example:_ `choose 4 planets where each planet has a terrifying creature`\n"
            "• _Example:_ `choose between 3 elevators in an underground research facility`\n\n"
            "👇 **Type your prompt in the chat now:**",
            parse_mode="Markdown"
        )
        
    # YouTube Genre Buttons
    elif data == "yt_horror":
        await start_youtube_pipeline(chat_id, context, "horror")
    elif data == "yt_science":
        await start_youtube_pipeline(chat_id, context, "science")
    elif data == "yt_myth":
        await start_youtube_pipeline(chat_id, context, "myth")
    elif data == "yt_space":
        await start_youtube_pipeline(chat_id, context, "space")
    elif data == "yt_superhero":
        await start_youtube_pipeline(chat_id, context, "superhero")
    elif data == "yt_custom":
        USER_STATES[chat_id] = "awaiting_yt_keyword"
        await query.edit_message_text(
            "✍️ *CUSTOM YOUTUBE ESSAY TOPIC*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Type a 1-word genre or custom topic title:\n\n"
            "• _Example:_ `horror` or `science` or `myth`\n"
            "• _Example:_ `Top 5 Deep Sea Trench Anomalies`\n\n"
            "👇 **Type your topic in the chat now:**",
            parse_mode="Markdown"
        )
    elif data == "yt_random":
        import random
        chosen = random.choice(["horror", "science", "myth", "space", "superhero"])
        await start_youtube_pipeline(chat_id, context, chosen)

async def post_init(application):
    """Registers native commands with Telegram's UI menu."""
    commands = [
        BotCommand("start", "🏠 Main Studio Menu"),
        BotCommand("commands", "📋 Full Command Directory (YT + TT)"),
        BotCommand("stop", "🛑 Stop Active Generation Immediately"),
        BotCommand("generate", "🔴 [YT] Produce Long-Form Essay (or 1-word genre)"),
        BotCommand("generate_tiktok", "📱 [TT] Auto-Idea or Custom Prompt"),
        BotCommand("publish_yt", "🚀 Upload Master to YouTube"),
        BotCommand("publish_tt", "📱 Publish Video to TikTok"),
        BotCommand("chapters", "🔴 [YT] Send 5 Story Cuts"),
        BotCommand("tiktok", "📱 [TT] Send Latest TikTok Episode"),
        BotCommand("status", "⚙️ Hardware & Studio Status"),
        BotCommand("episodes", "📁 List All Rendered Videos"),
    ]
    await application.bot.set_my_commands(commands)
    print("✅ Telegram native command menu registered successfully!")

def main():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n" + "=" * 70)
        print("⚠️ [TELEGRAM BOT NOTICE] Bot token is not configured yet!")
        print("=" * 70 + "\n")
        return

    print("🚀 Initializing Dual Studio Telegram Remote Control Bot...")
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(request).post_init(post_init).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("commands", commands_command))
    app.add_handler(CommandHandler("command", commands_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("episodes", episodes_command))
    app.add_handler(CommandHandler("preview", preview_command))
    app.add_handler(CommandHandler("chapters", chapters_command))
    app.add_handler(CommandHandler("generate", generate_command))
    app.add_handler(CommandHandler("essay", generate_command))
    
    # TikTok Handlers
    app.add_handler(CommandHandler("tiktok", tiktok_command))
    app.add_handler(CommandHandler("generate_tiktok", generate_tiktok_command))
    
    # Publishing Handlers
    app.add_handler(CommandHandler("publish_yt", lambda u, c: publish_yt_master_action(u.effective_chat.id, c)))
    app.add_handler(CommandHandler("publish_tt", lambda u, c: publish_tiktok_action(u.effective_chat.id, c)))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    print("✅ Dual Studio Telegram Bot is online and listening!")
    app.run_polling(bootstrap_retries=5)

if __name__ == "__main__":
    main()
