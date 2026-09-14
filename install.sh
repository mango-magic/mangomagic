#!/bin/bash
# MangoMagic 7.1 - One-line installer for ChatGPT Mac
# Usage: curl -fsSL https://raw.githubusercontent.com/manymangoes/mangomagic/main/install.sh | bash

set -e

echo ""
echo "🥭 MangoMagic 7.1 - B2B Sales Intelligence for ChatGPT"
echo "======================================================="
echo ""

# Check if ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📦 Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo ""
    echo "✅ Ollama installed."
else
    echo "✅ Ollama found."
fi

# Pull the model
echo ""
echo "⬇️  Pulling MangoMagic 7.1..."
ollama pull mangomagic/mangomagic-7.1

# Register with ChatGPT
echo ""
echo "🔌 Registering with ChatGPT..."
ollama launch chatgpt --model mangomagic/mangomagic-7.1 --config

# Done
echo ""
echo "═══════════════════════════════════════════════"
echo "🥭  MangoMagic 7.1 is ready!"
echo "═══════════════════════════════════════════════"
echo ""
echo "Open ChatGPT → click the model selector →"
echo "choose: mangomagic/mangomagic-7.1"
echo ""
echo "Try: \"Write a cold outreach message for a CFO struggling with manual invoice processing.\""
echo ""
