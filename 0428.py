# 導入Discord.py模組
import discord
import os
from openai import OpenAI, OpenAIError  # 匯入 OpenAI 模組
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
import io
import textwrap

# OpenAI API 金鑰
openai_client = OpenAI(api_key="Your OpenAI Key!")

# client是跟discord連接，intents是要求機器人的權限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 創建一個列表來存儲訊息
message_log = []

# 載入字體
pdfmetrics.registerFont(TTFont('ChineseFont', 'C:/Users/scream/OneDrive/桌面/專題/jf-openhuninn-2.0.ttf'))

# 調用event函式庫
@client.event
# 當機器人完成啟動
async def on_ready():
    print(f"目前登入身份 --> {client.user}")

@client.event
async def on_message(message):
    # 排除機器人本身的訊息，避免無限循環
    if message.author == client.user:
        return

    # 新訊息包含"我要製作一份報告"，要求提供報告主題
    if message.content.startswith("我要製作一份報告"):
        await message.channel.send("請問您想要做什麼樣的報告？請提供主題。")
        # 將接收到的訊息添加到訊息日誌
        message_log.append(message.content)
    # 如果訊息日誌中已經有主題信息
    elif len(message_log) == 1:
        # 從訊息日誌中獲取報告主題
        report_topic = message.content
        supplemental_text = "請針對該主題，提出四個跟該主題有關的報告標題。"
        question_with_supplement = f"{report_topic}\n\n{supplemental_text}"
        try:
            # 調用 OpenAI GPT-4 模型
            response = openai_client.chat.completions.create(
                model="gpt-4", 
                messages=[{"role": "user", "content": question_with_supplement}], 
            )
            # 從response中提取文本內容
            response_text = response.choices[0].message.content
            # 使用提取的文本內容調用生成 PDF 的函數
            generate_pdf(report_topic, response_text)
            # 發送 PDF 文件
            await message.channel.send("這是基於您的主題生成的報告標題:")
            await message.channel.send(file=discord.File('response.pdf'))
        except OpenAIError as e:
            # 處理可能的 OpenAI 連線錯誤
            await message.channel.send(f"OpenAI 連線錯誤: {e}")
        # 清空訊息日誌
        message_log.clear()

# 生成 PDF 的函數
def generate_pdf(direction, content):
    # 處理文本換行
    lines = textwrap.wrap(content, width=30)
    # 設定行高
    line_height = 25
    # 計算文本總高度
    text_height = len(lines) * line_height
    # 計算頁面總高度
    page_height = text_height + 800
    
    # 創建 PDF 並設定頁面大小
    c = canvas.Canvas("response.pdf", pagesize=(A4[0], page_height))
    # 設定使用的字體
    c.setFont("ChineseFont", 12)
    # 寫入 PDF 標題和摘要
    c.drawString(100, page_height - 50, "標題：")
    c.drawString(150, page_height - 50, direction)
    c.drawString(100, page_height - 80, "摘要：")
    
    # 設定寫入文本的起始位置
    text_x = 100
    text_y = page_height - 80 - line_height
    # 遍歷每行文本並寫入 PDF
    for line in lines:
        c.drawString(text_x, text_y, line)
        text_y -= line_height
    # 保存 PDF 文件
    c.save()

client.run("Your Discord Key!")