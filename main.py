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
            update.message.reply_text("Cú pháp: `/remind HH:MM Nội dung`")
            return

        hour, minute = map(int, time_str.split(':'))
        job_id = f"job_{job_counter}"

        # Thêm lịch và truyền user_chat_id vào hàm send_message
        scheduler.add_job(
            send_message_to_user,
            'cron',
            hour=hour,
            minute=minute,
            args=[context.bot, user_chat_id, f"⏰ *Nhắc nhở:* {message_text}"],
            id=job_id,
            name=f"{time_str} - {message_text}"
        )
        # ... (các phần còn lại giữ nguyên)

        # Thêm công việc vào bộ lập lịch với ID riêng
        scheduler.add_job(
            send_message,
            'cron',
            hour=hour,
            minute=minute,
            args=[context.bot, f"⏰ *Nhắc nhở:* {message_text}"],
            id=job_id,
            # Lưu tên công việc để hiển thị ở /list
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
    except Exception:
        update.message.reply_text(
            "❌ Sai cú pháp! Ví dụ đúng: `/remind 14:30 Uống nước`", parse_mode=ParseMode.MARKDOWN)

# Lệnh /list (Xem danh sách nhắc nhở)


def list_reminders(update, context):
    jobs = scheduler.get_jobs()

    if not jobs:
        update.message.reply_text(
            "📭 Hiện tại bạn chưa cài đặt lịch nhắc nhở nào!")
        return

    msg = "📋 *DANH SÁCH LỊCH NHẮC NHỞ:* \n\n"
    for job in jobs:
        # Lấy ID dạng số từ string job_id (job_1 -> 1)
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

    # Các lịch cố định mặc định (Không mang ID động nên sẽ không bị xoá nhầm qua lệnh /del)
    scheduler.add_job(send_message_to_user, 'cron', hour=6, minute=0, args=[
        updater.bot, CHAT_ID, "☀️ *Dậy thôi bạn ơi!* Chúc bạn ngày mới tốt lành."], name="06:00 - Dậy sớm")
    scheduler.add_job(send_message_to_user, 'cron', hour=7, minute=30, args=[
        updater.bot, CHAT_ID, "📚 *Đến giờ đi học/đi làm rồi!*"], name="07:30 - Học bài")
    scheduler.add_job(send_message_to_user, 'cron', hour=0, minute=0, args=[
        updater.bot, CHAT_ID, "🌙 *Đến giờ đi ngủ rồi!* Cất điện thoại nghỉ ngơi thôi."], name="00:00 - Đi ngủ")

    scheduler.start()

    print("Bot đang chạy... Bấm Ctrl + C trong CMD để dừng.")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")
    main()
