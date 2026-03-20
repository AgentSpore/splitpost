PLATFORMS = {
    "twitter": {
        "name": "Twitter / X",
        "char_limit": 280,
        "style": "Short, punchy, conversational. Use line breaks for readability. Thread-friendly. Emojis sparingly.",
        "hashtag_count": 2,
        "supports_threads": True,
    },
    "linkedin": {
        "name": "LinkedIn",
        "char_limit": 3000,
        "style": "Professional yet personal. Hook in first line. Use line breaks generously. Storytelling format. End with question or CTA.",
        "hashtag_count": 5,
        "supports_threads": False,
    },
    "instagram": {
        "name": "Instagram",
        "char_limit": 2200,
        "style": "Visual-first caption. Start with a hook. Use emojis as section markers. Hashtags at the end separated by dots. Relatable and engaging.",
        "hashtag_count": 15,
        "supports_threads": False,
    },
    "telegram": {
        "name": "Telegram",
        "char_limit": 4096,
        "style": "Channel-style post. Markdown formatting (bold, italic). Structured with headers. Informative and direct. Can be longer.",
        "hashtag_count": 3,
        "supports_threads": False,
    },
    "tiktok": {
        "name": "TikTok Script",
        "char_limit": 2200,
        "style": "Video script format. Start with a hook (first 3 seconds). Conversational, gen-z friendly. Use [PAUSE], [CUT], [TEXT ON SCREEN] markers. End with CTA.",
        "hashtag_count": 5,
        "supports_threads": False,
    },
}

TONES = {
    "professional": "Professional, authoritative, credible. Clear language, backed by expertise.",
    "casual": "Friendly, approachable, conversational. Like talking to a friend.",
    "viral": "Attention-grabbing, bold, contrarian. Designed for maximum shares and engagement.",
    "witty": "Clever, humorous, sharp. Wordplay welcome. Smart but not try-hard.",
    "academic": "Formal, precise, evidence-based. Suitable for research and educational content.",
}
