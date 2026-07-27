import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler

# ----------------------------------------------------
# THAY THÔNG TIN CỦA BẠN VÀO 2 DÒNG NÀY:
TOKEN = "8964731689:AAHT18jiRCZ7IxfZyt6sg3QOipntzwNkIVA"
CHAT_ID = "8120949547"
# ----------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Biến đếm dùng tạo ID tự động cho các nhắc nhở
job_counter = 1

# Hàm gửi tin nhắn


def send_message_to_user(bot, target_chat_id, message):
    bot.send_message(chat_id=target_chat_id, text=message,
                     parse_mode=ParseMode.MARKDOWN)

# Lệnh /start


def start(update, context):
    msg = (
        "👋 *Chào bạn! Mình là Remin_chan - robot nhắc nhở.*\n\n"
        "📌 *Các lệnh bạn có thể dùng:*\n"
        "• `/remind HH:MM Nội dung` : Đặt lịch nhắc mới\n"
        "• `/list` : Xem danh sách nhắc nhở đang có\n"
        "• `/del ID` : Xóa một nhắc nhở theo Mã ID"
    )
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# Lệnh /remind HH:MM Nội dung


def set_reminder(update, context):
    global job_counter
    # Lấy ID của chính người vừa nhắn tin cho bot
    user_chat_id = update.effective_chat.id

    try:
        time_str = context.args[0]
        message_text = " ".join(context.args[1:])

        if not message_text:
            update.message.reply_text(
                "❌ Cú pháp: `/remind HH:MM Nội dung`\n*Ví dụ:* `/remind 14:30 Uống nước`", parse_mode=ParseMode.MARKDOWN)
            return

        hour, minute = map(int, time_str.split(':'))
        job_id = f"job_{job_counter}"

        # Thêm lịch hẹn giờ cho đúng người vừa nhắn tin
        scheduler.add_job(
            send_message_to_user,
            'cron',
            hour=hour,
            minute=minute,
            args=[context.bot, user_chat_id, f"⏰ *Nhắc nhở:* {message_text}"],
            id=job_id,
            name=f"{time_str} - {message_text}"
        )

        update.message.reply_text(
            f"✅ *Đã hẹn giờ thành công!*\n"
            f"• **Nội dung:** {message_text}\n"
            f"• **Thời gian:** {time_str} hàng ngày\n"
            f"• **Mã ID:** `{job_counter}`",
            parse_mode=ParseMode.MARKDOWN
        )
        job_counter += 1
    except Exception as e:
        logging.error(f"Lỗi đặt lịch: {e}")
        update.message.reply_text(
            "❌ Sai cú pháp! Ví dụ đúng: `/remind 14:30 Uống nước`", parse_mode=ParseMode.MARKDOWN)

# Lệnh /list (Xem danh sách nhắc nhở của chính người dùng)


def list_reminders(update, context):
    user_chat_id = update.effective_chat.id
    jobs = scheduler.get_jobs()

    user_jobs = []
    for job in jobs:
        # Lọc ra các công việc gửi tới user_chat_id hiện tại
        if len(job.args) >= 2 and job.args[1] == user_chat_id:
            user_jobs.append(job)

    if not user_jobs:
        update.message.reply_text(
            "📭 Hiện tại bạn chưa cài đặt lịch nhắc nhở nào!")
        return

    msg = "📋 *DANH SÁCH LỊCH NHẮC NHỞ CỦA BẠN:* \n\n"
    for job in user_jobs:
        if job.id.startswith("job_"):
            clean_id = job.id.replace("job_", "")
            msg += f"🔹 *ID:* `{clean_id}` | ⏰ {job.name}\n"
        else:
            msg += f"📌 *Cố định:* ⏰ {job.name}\n"

    msg += "\n💡 Để xóa nhắc nhở, gõ: `/del ID` (Ví dụ: `/del 1`)"
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

# Lệnh /del ID (Xóa nhắc nhở theo ID)


def delete_reminder(update, context):
    try:
        req_id = context.args[0]
        target_job_id = f"job_{req_id}"

        job = scheduler.get_job(target_job_id)
        if job:
            scheduler.remove_job(target_job_id)
            update.message.reply_text(
                f"🗑️ Đã xóa thành công nhắc nhở có **ID: {req_id}**!", parse_mode=ParseMode.MARKDOWN)
        else:
            update.message.reply_text(
                f"❌ Không tìm thấy nhắc nhở nào có **ID: {req_id}**! Bạn hãy gõ `/list` để kiểm tra lại ID nhé.", parse_mode=ParseMode.MARKDOWN)
    except Exception:
        update.message.reply_text(
            "❌ Cú pháp chưa đúng! Ví dụ muốn xóa ID 1, gõ: `/del 1`", parse_mode=ParseMode.MARKDOWN)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Đăng ký các lệnh
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("remind", set_reminder))
    dp.add_handler(CommandHandler("list", list_reminders))
    dp.add_handler(CommandHandler("del", delete_reminder))

    scheduler.start()

    print("Bot đang chạy... Bấm Ctrl + C trong CMD để dừng.")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")
    main()
