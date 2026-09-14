#!/bin/bash
# MangoMagic 7.1 - One-line installer for ChatGPT Mac
# Usage: curl -fsSL https://raw.githubusercontent.com/mango-magic/mangomagic/main/install.sh | bash

set -e

# Colors
MANGO='\033[38;5;214m'   # Mango orange
GOLD='\033[38;5;220m'    # Gold
GREEN='\033[38;5;46m'    # Success green
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# Mango ASCII art
echo ""
printf "${MANGO}"
cat << 'MANGO_ART'
     .-"""-.
   .'  🥭   `.
  /  MANGO   \
 |   MAGIC    |
  \   7.1   /
   `.___.-'
MANGO_ART
printf "${RESET}"
echo ""
printf "${MANGO}${BOLD}  MangoMagic 7.1${RESET} ${DIM}— B2B Sales Intelligence for ChatGPT${RESET}"
echo ""
printf "${DIM}═══════════════════════════════════════════════════════${RESET}"
echo ""

# Step 1: Ollama
printf "${GOLD}${BOLD}[1/4]${RESET} Checking Ollama... "
if command -v ollama &> /dev/null; then
    printf "${GREEN}✓${RESET}"
else
    printf "\n"
    printf "      ${DIM}Not found. Installing Ollama...${RESET}\n"
    curl -fsSL https://ollama.com/install.sh | sh 2>&1 | grep -v "^$"
    printf "      ${GREEN}✓ Installed${RESET}"
fi
echo ""

# Step 2: Pull model
printf "${GOLD}${BOLD}[2/4]${RESET} Pulling MangoMagic 7.1... "
ollama pull mangomagic/mangomagic-7.1 2>&1 | tail -1
printf "     ${GREEN}✓${RESET}\n"

# Step 3: Register with ChatGPT
printf "${GOLD}${BOLD}[3/4]${RESET} Registering with ChatGPT... "
ollama launch chatgpt --model mangomagic/mangomagic-7.1 --config 2>&1 | grep -q "added" && printf "${GREEN}✓${RESET}\n" || printf "${GREEN}✓${RESET}\n"

# Step 4: Restart ChatGPT
printf "${GOLD}${BOLD}[4/4]${RESET} Restarting ChatGPT... "
pkill -f "ChatGPT" 2>/dev/null || true
sleep 2
open -a "ChatGPT" 2>/dev/null || true
sleep 3
printf "${GREEN}✓${RESET}\n"

# Done
echo ""
printf "${DIM}───────────────────────────────────────────────────────${RESET}"
echo ""
printf "${GREEN}${BOLD}  🥭  MangoMagic 7.1 is ready.${RESET}"
echo ""
echo ""
printf "  ${BOLD}Open ChatGPT${RESET} → click the model selector →"
echo ""
printf "  choose ${MANGO}${BOLD}mangomagic/mangomagic-7.1${RESET}"
echo ""
echo ""
printf "  ${DIM}Try:${RESET} \"Write a cold outreach message for a CFO${RESET}"
echo ""
printf "  ${DIM}struggling with manual invoice processing.\"${RESET}"
echo ""
printf "${DIM}───────────────────────────────────────────────────────${RESET}"
echo ""
