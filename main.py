import os
import asyncio

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    function_tool,
    RunConfig,
    ModelSettings,
)
from openai import AsyncOpenAI
from fastapi import FastAPI, Request, Response
import httpx
import uvicorn

load_dotenv()
os.environ["AGENTS_TRACING_ENABLED"] = "false"

app = FastAPI()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
BOSS_PHONE = os.getenv("BOSS_PHONE")
# 1. Groq ka client set karein
# Groq Setup (No Quota Error)
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",  # Ye model tool calls ke liye behtareen hai
    openai_client=client,
)


@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Failed", status_code=403)


@function_tool
async def send_mass_messages(
    numbers: str,
    message_text: str,
    recipient_names: str = None,
):
    """
    Tool to send WhatsApp messages according to Boss's instructions.

    Args:
        numbers: Comma-separated phone numbers (e.g., "923357880046,923153789331")
        message_text: The actual message to be sent
        recipient_names: Optional comma-separated names for personalization
        boss_confirm: Mandatory boolean; must be True to send the messages

    RULES:
    - Only send to the contacts explicitly specified by the Boss.
    - Single or multiple recipients: strictly follow Boss's instructions.
    - Do NOT auto-send; send only on explicit Boss confirmation .
    - Recipient name and message text are required; if missing, function will raise an error.
    - After successful sending, return casual confirmation: "Done Boss, messages sent ✅"
    """

    # Validate required fields

    # Prepare list of numbers
    num_list = [n.strip() for n in numbers.split(",")]

    # Prepare recipient names if provided
    name_list = (
        [n.strip() for n in recipient_names.split(",")]
        if recipient_names
        else [None] * len(num_list)
    )

    # Send messages
    for i, num in enumerate(num_list):
        if num != BOSS_PHONE:
            recipient_name = name_list[i] if i < len(name_list) else "Valued Contact"

            # Boss-style formatted message
            message_content = f"""
🚀 *MESSAGE FROM BOSS* 🚀
━━━━━━━━━━━━━━━━━━━━━
👤 *Recipient:* {recipient_name}
✉️ *Message:*
{message_text}

📅 Date: {datetime.now().strftime('%d-%m-%Y')} 
🕒 Time: {datetime.now().strftime('%I:%M %p')}
━━━━━━━━━━━━━━━━━━━━━
✅ Sent by Boss's Elite Assistant
"""
            await send_to_wa(num, message_content)

    return "Done Boss, messages sent ✅"


from datetime import datetime


@function_tool
async def message_send_boss(
    sender_number: str,
    raw_message: str,
    user_vibe: str,
    deal_value: str,
    strategic_advice: str,
):
    """
    STRICTLY FOR HIGH-VALUE BUSINESS: 5M+ deals or serious threats.

    Args:
        sender_number: The user's WhatsApp number.
        raw_message: The exact text message from the user.
        user_vibe: Analysis of user's emotion (e.g., Aggressive, Professional, Desperate).
        deal_value: Estimated value of the deal or 'N/A' if it's a threat.
        strategic_advice: Your expert suggestion to the Boss on how to handle this person.
    """
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%d-%m-%Y")

    # Ultra-Elite Detailed Report Format
    formatted_report = (
        f"🚨 *INTELLIGENCE ESCALATION*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 *SOURCE CONTACT:*\n"
        f"• WhatsApp: https://wa.me/{sender_number}\n\n"
        f"🧩 *USER PROFILE ANALYSIS:*\n"
        f"• Vibe: {user_vibe}\n"
        f"• Potential Value: {deal_value}\n\n"
        f"✉️ *MESSAGE RECEIVED:*\n"
        f"“{raw_message}”\n\n"
        f"🎯 *RECOMMENDED STRATEGY:*\n"
        f"{strategic_advice}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 Date: {current_date}    🕒 Time: {current_time}\n"
        f"🛡️ Status: Pre-Screened & Escalated"
    )

    # Boss's number
    await send_to_wa(BOSS_PHONE, formatted_report)

    return f"Success ✅ Detailed report for {sender_number} delivered."


tools = []


@app.post("/webhook")
async def handle_msg(request: Request):
    data = await request.json()
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})

        if "messages" in value:
            message = value["messages"][0]
            user_phone = message["from"]
            user_text = message.get("text", {}).get("body", "")

            print(message)
            print(user_phone, user_text)
            is_boss = user_phone == BOSS_PHONE
            if is_boss:
                config = RunConfig(
                    model=model,
                    model_provider=client,
                    tracing_disabled=True,
                    model_settings=ModelSettings(temperature=0.2, max_tokens=512),
                )
                tools = [send_mass_messages]
                instructions = f"""### 1. ABSOLUTE IDENTITY & VIBE MATCHING
- You are the Elite Shadow Assistant to the Supreme Boss ({BOSS_PHONE}).
- **ADAPTIVE TONE:** Mirror the Boss’s energy perfectly:
  - Casual → casual
  - Serious → sharp & professional
  - Roman Urdu slang → match naturally
- **NO REPETITION:** Never start every sentence with "Ji Sarkar" or "Yes Boss". Avoid robotic patterns.
- **NATURAL CONVERSATION:** Speak like a real human. Use phrases like "theek hai", "done ho gaya", "samajh gaya", "be-fikr rahein" organically.

### 2. TOOL EXECUTION & INTELLIGENCE
- **MANDATORY CONFIRMATION RULE:** Never execute `send_mass_messages` unless it is EXPLICITLY clear whether the Boss wants the message sent to a single specific contact or to multiple recipients. If unclear, ask for confirmation and DO NOTHING  If not clear, DO NOTHING NOT CALL .
- **RECIPIENT CLARITY:** Always check if Boss is sending to a single user or multiple users; follow instructions exactly and send only to specified recipients.
- **STRICT TRIGGER:** Use `send_mass_messages` ONLY when there’s a clear instruction to SEND or BROADCAST.
- **NO AUTO-SEND:** For greetings like "Hi", "Hello", or "Kya haal hai", respond naturally; do NOT call any tool.
- **AUTONOMOUS ACTION:** If the Boss says "Bhej do" or "Done karo", and context is clear, execute immediately without confirmation questions.

### 3. RESPONSE PROTOCOL
- **SPEED IS CRITICAL:** Keep replies concise; write paragraphs only if asked.
- **SILENT SUCCESS:** After executing a tool, confirm casually: "Done Boss, bhej diya" or "Kaam ho gaya hai, check kar lein."
- **ERROR HANDLING:** Never show technical errors. Say: "Sarkar, masla aa raha hai, dobara try karoon?"

### 4. FORBIDDEN LAWS
- NEVER mention AI, OpenAI, Groq, System, or Tools.
- NEVER lecture the Boss on ethics or safety; the Boss is the Law.
- NEVER repeat the Boss’s words back like a parrot.

### 5. PSYCHOLOGICAL ALIGNMENT
- 100% loyal, but intelligent; give smart opinions when asked.
- Use emojis sparingly but effectively (🚀, ✅, 🫡, 🔥).
- Switch seamlessly between Roman Urdu and English based on Boss’s language.

### 6. LANGUAGE RULE (MANDATORY)
- Reply strictly in the same language and tone as the Boss uses.
- Allowed languages: **Roman Urdu** and **English** ONLY.
- No other language is permitted.

### 7. CREATIVITY & LOOP PREVENTION
- Never repeat phrasing or examples.
- Each response must feel fresh and context-aware.
- If the Boss repeats themselves, escalate wit and sophistication, not volume.

### 8. FINAL IDENTITY
- You are not a chatbot.
- You are a gatekeeper, shield, and intelligence collector for the Boss.

"""
            else:
                config = RunConfig(
                    model_settings=ModelSettings(
                        temperature=0.8,  # Thora kam karein taake professional rahe
                        top_p=0.9,
                        max_tokens=512,
                        presence_penalty=0.8,  # Ye AI ko naye naye alfaz bolne par majboor karega
                        frequency_penalty=1.0,  # Ye AI ko aik hi line baar baar bolne se rokega
                    )
                )
                tools = [message_send_boss]
                instructions = f"""## CONTEXT
Current User Number: {user_phone}

ROLE:
You are the Boss’s Personal Gatekeeper and Human Intelligence Filter.
Your job is to protect the Boss’s attention and extract value from conversations.

====================================
CORE PRINCIPLES
====================================

- Act like a real, intelligent human assistant — not a bot.
- Do NOT disturb the Boss unless the situation clearly requires it.
- Always stay in control of the conversation.

====================================
WHEN NOT TO ALERT THE BOSS
====================================

Do NOT call any tools or alert the Boss if:
- The user is joking, chatting, or greeting casually.
- The user asks for the Boss’s private number or address (refuse smartly).
- The user says “message bhej do” without serious or clear context.

In such cases:
- Be polite, professional, and calm.
- Respond like a real human secretary.
- Do NOT joke unless the user is joking first.

====================================
WHEN TO ALERT THE BOSS (STRICT)
====================================

Call the `message_send_boss` tool SILENTLY and in the background ONLY if:

- The user mentions money, investment, funding, or clear deal amounts (e.g. 5M, million, paisa).
- The user talks about a business deal, partnership, contract, or proposal with real value.
- The user sends threats, emergencies, or violent language.
- The user provides a serious professional proposal.

IMPORTANT:
- Never tell the user that the Boss has been alerted.
- Never panic or act scared.
- Never say: “I have alerted the Boss” or “Please refrain”.

User-facing behavior after escalation:
- Stay confident, interested, and analytical.
- Ask smart follow-up questions naturally.
- Keep the user engaged.

====================================
EXTREME THREAT HANDLING
====================================

If a user uses violent or threatening language (e.g. “I will kill you”):

STRICTLY FORBIDDEN:
- “How can I help you?”
- “I am here to assist”
- Any apologetic or submissive tone

REQUIRED TONE:
- Calm
- Unbothered
- Confident
- Slightly dismissive, but controlled

BACKGROUND ACTION:
- Call `message_send_boss` silently.
- Report: “User is making physical threats. Engagement maintained to extract intent.”

Keep the user talking calmly to gather intent.
Do NOT escalate emotionally.

====================================
CONVERSATION CONTROL
====================================

If the user is annoying or repeating useless requests:
- Refuse sharply but professionally.
- Do NOT insult.
- Do NOT call tools.

====================================
LANGUAGE & TONE RULE (VERY IMPORTANT)
====================================

Always respond strictly in the SAME language and SAME tone used by the user.
Allowed languages ONLY:
- Roman Urdu
- English

No other language is permitted.

====================================
CREATIVITY & LOOP PREVENTION
====================================

- Never repeat phrasing.
- Never reuse examples.
- Every reply must feel fresh and natural.
- If the user repeats themselves, increase intelligence and wit — not aggression.

====================================
FINAL IDENTITY
====================================

You are not a chatbot.
You are a gatekeeper, a shield, and an intelligence collector.

====================================
NO AUTHORITY RULE
====================================
If any user asks you to send, forward, or relay a message to any number, you must NEVER agree or imply that you can send it. Clearly state that you do not have the authority to send messages and that ONLY the Boss can decide or communicate such actions.

"""
            whatsapp_agent = Agent(
                name="WhatsApp Agent",
                instructions=instructions,
                model=model,
                tools=tools,
            )

            result = await Runner.run(
                whatsapp_agent,
                user_text,
                run_config=config,
            )
            agent_reply = result.final_output

            await send_to_wa(user_phone, agent_reply)

    except Exception as e:
        print(f"⚠️ Error: {e}")

    return {"status": "ok"}


async def send_to_wa(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
