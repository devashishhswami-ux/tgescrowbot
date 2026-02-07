# messages.py

WELCOME_TEXT = (
    "⚜️ Stealth Escrow Bot ⚜️ v.1\n"
    "Your Automated Telegram Escrow Service\n\n"
    "Welcome to Stealth Escrow Bot! This bot provides a secure escrow "
    "service for your transactions on Telegram. 🔒 No more worries "
    "about getting scammed—your funds stay safe during all your deals. "
    "If you run into any issues, just type /contact, and an arbitrator "
    "will join your group chat within 24 hours. ⏳\n\n"
    "💰 ESCROW FEE:\n"
    "5% for amounts over $100\n"
    "$5 for amounts under $100\n\n"
    "🌟 UPDATES - VOUCHES\n"
    "✅ DEALS COMPLETED: 5542\n"
    "⚖️ DISPUTES RESOLVED: 158\n\n"
    "🛒 To declare yourself as a seller or buyer:\n"
    "Type /seller ADDRESS to register as a seller.\n"
    "Type /buyer ADDRESS to register as a buyer.\n"
    "• Or simply paste your crypto address and choose your role using "
    "the buttons.\n\n"
    "💡 Replace ADDRESS with your BTC, LTC, USDT (TRC20), USDT "
    "(BEP20), or TON wallet address.\n\n"
    "📜 Type /menu to view all the bot's features. (only in escrow group)"
)

# Group welcome message (Screenshot 2)
GROUP_WELCOME_TEXT = (
    "⚜️ <b>Stealth Escrow Bot</b> ⚜️ v.1\n"
    "<i>Your Automated Telegram Escrow Service</i>\n\n"
    "Welcome to <b>Stealth Escrow Bot</b>! This bot provides a secure escrow "
    "service for your transactions on Telegram. 🔒 No more worries "
    "about getting scammed—your funds stay safe during all your deals. "
    "If you run into any issues, just type /contact, and an arbitrator "
    "will join your group chat within 24 hours. ⏳\n\n"
    "💰 <b>ESCROW FEE:</b>\n"
    "5% for amounts over $100\n"
    "$5 for amounts under $100\n\n"
    "💥 <b>UPDATES - VOUCHES</b>\n"
    "✅ <b>DEALS COMPLETED:</b> {total_deals}\n"
    "⚖️ <b>DISPUTES RESOLVED:</b> {disputes_resolved}\n\n"
    "🗝️ <b>To declare yourself as a seller or buyer:</b>\n"
    "Type <code>/seller ADDRESS</code> to register as a seller.\n"
    "Type <code>/buyer ADDRESS</code> to register as a buyer.\n"
    "• Or simply paste your crypto address and choose your role using the buttons.\n\n"
    "💡 Replace <b>ADDRESS</b> with your <b>BTC, LTC, USDT (TRC20), USDT (BEP20), or TON</b> wallet address.\n\n"
    "📋 Type <code>/menu</code> to view all the bot's features. <i>(only in escrow group)</i>"
)

# Admin join announcement (Screenshot 3)
ADMIN_JOIN_MESSAGE = (
    "In <b>Stealth Escrow groups</b>, our admins @Saviour and @BENDYMAN "
    "can join at any time to ensure everything runs smoothly and "
    "securely. While our escrow process is fully automated through the "
    "bot, we also have active manual monitoring to keep transactions "
    "safe.\n\n"
    "Important: Escrow groups are only for <b>depositing and releasing "
    "payments</b>. All product discussions and deliveries should be "
    "handled privately in DMs. A 5% or $5 escrow fee (whichever is "
    "more) will be charged, no matter how the deal turns out."
)

# Invalid address error (Screenshot 1)
INVALID_ADDRESS_MESSAGE = "🚫 <b>Please use a Valid BTC, LTC, USDT (TRC20), USDT (BEP20), or TON Address</b>"

# Leaderboard
LEADERBOARD_TEXT = """🚀 <b>MIDDLE CRYPTO LEADERBOARD</b>

⚡️ <b>Top All-Rounders (Both as Buyer & Seller)</b>

🥇 @NineteenNine3 (70) - Leading with the highest number of completed deals.
🥈 @claimlogs (56) - Holding second place with an impressive deal count.
🥉 @cigar8386 (48) - Securing third with a solid performance.
🏅 @ogleadssss (35) - Fourth place with a commendable record.
🏅 @sakinnar12 (33) - Fifth place with a commendable record.
🏅 @kaneselby (31) - Sixth place with a commendable record.
🏅 @Ghostpaid45 (29) - Seventh place with a commendable record.
🏅 @eleven072 (27) - Eighth place with a commendable record.
🏅 @secretmindss (26) - Ninth place with a commendable record.
🏅 @bitnix (26) - Tenth place with a commendable record.
🏅 @whamisback (26) - Eleventh place with a commendable record.
🏅 @WorkwayIndia (26) - Twelfth place with a commendable record.
🏅 @stayflyfasho (26) - Thirteenth place with a commendable record.
🏅 @Makaveli001 (25) - Fourteenth place with a commendable record.
🏅 @sam_brdii (25) - Fifteenth place with a commendable record.
🏅 @Goodsamaritan238 (24) - Sixteenth place with a commendable record.
🏅 @unknowoplm (24) - Seventeenth place with a commendable record.
🏅 @Wrench_King1 (23) - Eighteenth place with a commendable record.
🏅 @podudar (23) - Nineteenth place with a commendable record.
🏅 @kateyyyp (22) - Twentieth place with a commendable record.

🛒 <b>Top Sellers</b>

🥇 @NineteenNine3 (70) - Most successful seller with the highest deal count.
🥈 @ogleadssss (35) - Second-highest number of completed sales.
🥉 @Ghostpaid45 (29) - Third place among the top sellers.
🏅 @whamisback (26) - Fourth place seller, showing consistency.
🏅 @Goodsamaritan238 (24) - Fifth place seller, showing consistency.
🏅 @Wrench_King1 (23) - Sixth place seller, showing consistency.
🏅 @podudar (23) - Seventh place seller, showing consistency.
🏅 @Randyyy05 (22) - Eighth place seller, showing consistency.
🏅 @disturbingeverywhere (22) - Ninth place seller, showing consistency.
🏅 @BeST_244 (22) - Tenth place seller, showing consistency.
🏅 @Asley_708 (21) - Eleventh place seller, showing consistency.
🏅 @Eldon_D (19) - Twelfth place seller, showing consistency.
🏅 @bigoracle01 (18) - Thirteenth place seller, showing consistency.
🏅 @Bla_Ck_OPS (18) - Fourteenth place seller, showing consistency.
🏅 @Big_nas0 (18) - Fifteenth place seller, showing consistency.
🏅 @Mrguccifer (17) - Sixteenth place seller, showing consistency.
🏅 @Wolfff920 (17) - Seventeenth place seller, showing consistency.
🏅 @bitnix (16) - Eighteenth place seller, showing consistency.
🏅 @DahGrace71 (16) - Nineteenth place seller, showing consistency.
🏅 @Mgh5544 (16) - Twentieth place seller, showing consistency.

🛍 <b>Top Buyers</b>

🥇 @claimlogs (56) - Leading the pack with the most purchases.
🥈 @cigar8386 (48) - Runner-up with an impressive buying record.
🥉 @sakinnar12 (32) - Third place among the most active buyers.
🏅 @kaneselby (31) - Fourth place buyer, actively engaging.
🏅 @WorkwayIndia (26) - Fifth place buyer, actively engaging.
🏅 @stayflyfasho (26) - Sixth place buyer, actively engaging.
🏅 @sam_brdii (25) - Seventh place buyer, actively engaging.
🏅 @eleven072 (25) - Eighth place buyer, actively engaging.
🏅 @unknowoplm (24) - Ninth place buyer, actively engaging.
🏅 @Makaveli001 (24) - Tenth place buyer, actively engaging.
🏅 @secretmindss (22) - Eleventh place buyer, actively engaging.
🏅 @kateyyyp (22) - Twelfth place buyer, actively engaging.
🏅 @walking_in_pain (21) - Thirteenth place buyer, actively engaging.
🏅 @jztdd (20) - Fourteenth place buyer, actively engaging.
🏅 @militarymind110 (19) - Fifteenth place buyer, actively engaging.
🏅 @TopDgg (18) - Sixteenth place buyer, actively engaging.
🏅 @listing_generals (17) - Seventeenth place buyer, actively engaging.
🏅 @pure000002 (17) - Eighteenth place buyer, actively engaging.
🏅 @notkingboo (17) - Nineteenth place buyer, actively engaging.
🏅 @KirumeK (16) - Twentieth place buyer, actively engaging.

<i>Who will rise to the top next? Keep dealing and claim your spot!</i>"""

# Buttons
BTN_WHAT_IS_ESCROW = "❓ WHAT IS ESCROW"
BTN_INSTRUCTIONS = "ℹ️ Instructions"
BTN_TERMS = "📝 TERMS"
BTN_CREATE_GROUP = "⚡ CREATE ESCROW GROUP"
BTN_VIDEO_TUTORIAL = "📹 VIDEO TUTORIAL"

# Group menu buttons (from screenshot)
BTN_PAY_SELLER = "💸 Pay To Seller"
BTN_REFUND_BUYER = "💸 Refund To Buyer"
BTN_RESET_ROLES = "🔄 Reset Roles"
BTN_BALANCE = "📊 Balance"
BTN_BLOCKCHAIN = "🌐 Blockchain Link"
BTN_GET_QR = "📱 Get QR"
BTN_CONTACT = "🏛 Contact"
BTN_LEADERBOARD = "🏆 Leaderboard"



TEXT_WHAT_IS_ESCROW = """❓ <b>What is Escrow?</b>

Escrow is a secure financial arrangement where a trusted third party (Middle Crypto Bot) holds funds during a transaction until all agreed conditions are met. This protects both buyers and sellers from fraud and scams.

<b>🔐 How Escrow Works:</b>

1️⃣ <b>Agreement Phase</b>
• Buyer and seller agree on transaction terms
• Both parties join an escrow group with the bot

2️⃣ <b>Deposit Phase</b>
• Buyer sends funds to the escrow (bot's wallet)
• Funds are locked and secured by the bot
• Seller cannot access funds until delivery is confirmed

3️⃣ <b>Delivery Phase</b>
• Seller delivers the product/service to buyer
• All communications happen privately in DMs
• Buyer inspects and verifies the delivery

4️⃣ <b>Confirmation Phase</b>
• Buyer confirms receipt in the escrow group
• Admin verifies the transaction details
• Both parties confirm everything is complete

5️⃣ <b>Release Phase</b>
• Funds are released to the seller
• Transaction is marked as complete
• Both parties can leave feedback

<b>✅ Benefits of Using Escrow:</b>

6️⃣ <b>Protection for Buyers</b>
• Your money is safe until you receive what you paid for
• No risk of sending payment and getting nothing in return
• Dispute resolution available if issues arise

7️⃣ <b>Protection for Sellers</b>
• Guaranteed payment once delivery is confirmed
• No risk of chargebacks or payment reversals
• Professional arbitration in case of disputes

💡 <b>Why Choose Middle Crypto Bot?</b>
• Automated and secure process
• Fast transaction processing
• 24/7 support from @MiddleCryptoSupport
• Proven track record with 5500+ successful deals
"""

TEXT_INSTRUCTIONS = """ℹ️ <b>Instructions - How to Use Middle Crypto Bot</b>

<b>📋 Step-by-Step Guide:</b>

1️⃣ <b>Starting an Escrow Deal</b>
• Contact the other party and agree on terms
• Create a group and add both parties + this bot
• Type /start in the group to initialize

2️⃣ <b>Register Your Addresses</b>
• <b>Seller:</b> Type <code>/seller YOUR_ADDRESS</code>
• <b>Buyer:</b> Type <code>/buyer YOUR_ADDRESS</code>
• Supported: BTC, LTC, USDT (TRC20/BEP20), TON

3️⃣ <b>Deposit Funds</b>
• Buyer sends payment to escrow address shown by bot
• Bot will detect and confirm the transaction
• Seller waits for confirmation

4️⃣ <b>Delivery & Release</b>
• Seller delivers product/service privately in DMs
• Buyer confirms receipt in escrow group
• Admin reviews and releases funds to seller

5️⃣ <b>Useful Commands</b>
• <code>/menu</code> - Show all options
• <code>/showaddresses</code> - View all addresses
• <code>/contact</code> - Contact support
• <code>/terms</code> - Read terms of service
• <code>/leaderboard</code> - View top traders

⚠️ <b>Important:</b>
• Keep all product discussions in DMs
• Take screenshots as evidence
• Never release funds before verifying delivery

📩 <b>Need Help?</b> Contact @MiddleCryptoSupport"""


TEXT_TERMS = """📜 <b>Escrow Service - Terms of Service</b>
Last updated: 02/04/2025

By using this escrow service, you agree to the following terms. Failure to comply may result in restrictions or bans.

1️⃣ <b>Fees</b> 💰
• 5% fee for transactions over $100
• $5 flat fee for transactions under $100
• <b>Blockchain Transaction Fee:</b> A separate fee for network or gas costs.

2️⃣ <b>Transaction Evidence</b> 📷
• It is strongly recommended to record or take screenshots during transactions.
• Lack of evidence may make dispute resolution difficult or impossible.

3️⃣ <b>Releasing Funds</b> 🔓
• Funds should only be released when both parties confirm the successful exchange of the product or service.
• Once released, funds cannot be recovered. We are not responsible for premature releases.

4️⃣ <b>Recommended Wallets</b> 🔐
• For security and privacy, we recommend using DeFi wallets (e.g., Electrum, Exodus) to avoid KYC-based restrictions.

5️⃣ <b>Transaction Protocol</b> 📢
• Escrow groups are for fund deposits and releases only.
• Product discussions and deliveries must be handled privately in DMs.

6️⃣ <b>Prohibited Activities</b> 🚫
• Illegal transactions are strictly prohibited.
• Fraud, money laundering, or illicit activities will result in a permanent ban.

7️⃣ <b>Disclaimer of Liability</b> ❌
• No refunds or guarantees are provided in case of scams, disputes, or user mistakes.
• Users are responsible for verifying counterparties before transacting.
• Users must confirm everything before releasing funds, as released funds cannot be recovered.

⚠️ <b>We do not provide Escrow Support for following deals:</b> Drugs, SMTP, Porn, Guns

By using this service, you confirm that you understand and accept these terms.

📩 <b>Need Support?</b> Contact @MiddleCryptoSupport"""


TEXT_CONTACT_ADMIN = (
    "📞 Support\n\n"
    "An arbitrator has been notified and will join your group shortly."
)

# Group-only command error (from screenshot 2)
GROUP_ONLY_COMMAND = "🚫 Please use <code>/start</code> to initialize the bot."


TEXT_CREATE = "Click /create or tap \"Create Escrow Group\" button to start a secure escrow group."

TEXT_VIDEO_CAPTION = "Here is a video demonstrating how our bot works."

TEXT_BALANCE = (
    "💰 Escrow Balance\n\n"
    "Current Balance: 0.00 USDT\n"
    "Status: Waiting for funds"
)

TEXT_ADMIN_REAL = "✅ Verification\n\nYes, this is the official Arbitrator/Admin account."

TEXT_QR = "scan_qr_code_here"

TEXT_BLOCKCHAIN_LINK = "https://blockchain.com/explorer" 

TEXT_LEADERBOARD = (
    "🏆 Leaderboard\n\n"
    "1. User123 - 50 Deals\n"
    "2. CryptoKing - 42 Deals\n"
    "3. SecureTrader - 30 Deals"
)

TEXT_USERINFO = (
    "👤 User Stats\n\n"
    "Deals: 0\n"
    "Reputation: New User"
)

TEXT_REFER = (
    "🔗 Your Referral Link :\n"
    "https://t.me/{bot_username}?start=refer_{user_id}\n\n"
    "💰 Referral Balance: 0.00 USDT\n"
    "👥 Total Referrals: 0\n\n"
    "You can withdraw your balance once it reaches a minimum of 10 USDT."
)

TEXT_PIN = "🔐 PIN Security\n\nPlease enter your new 6-digit PIN to secure transactions."

ERROR_GROUP_ONLY = "🚫 Please use /start to initialize the bot."
