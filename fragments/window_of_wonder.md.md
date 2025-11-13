**Tags:** audio-reactive, emotional UX, Phoenix pulse, winter ritual

#!/bin/bash

# Phoenix Ritual: auto_parse.sh
# Migrates clipboard content into Phoenix structure with emotional or strategic integrity

echo "📋 Reading clipboard..."
LOG=$(pbpaste)

# Save raw clipboard for debugging
mkdir -p ~/phoenix/rituals
echo "$LOG" > ~/phoenix/rituals/last_clipboard.txt

# Prompt for note type
read -p "Note type (frisson/general): " NOTE_TYPE

# If frisson, extract structured fields
if [ "$NOTE_TYPE" = "frisson" ]; then
  timestamp=$(echo "$LOG" | grep -i "^# *Emotion Log:" | sed 's/^# *Emotion Log: *//I')
  tags=$(echo "$LOG" | grep -i "^# *Tag:" | sed 's/^# *Tag: *//I')
  entry=$(echo "$LOG" | grep -i "^# *Entry:" | sed 's/^# *Entry: *//I')

  if [ -z "$timestamp" ] || [ -z "$tags" ] || [ -z "$entry" ]; then
    echo "⚠️ Parsing failed. Please format clipboard like:"
    echo "# Emotion Log: 2025-09-06 18:20"
    echo "# Tag: grief, memory, Nadya"
    echo "# Entry: Felt the ache of missed connection while folding laundry"
    echo "📎 Raw clipboard saved to: phoenix/rituals/last_clipboard.txt"
    exit 1
  fi

  DEST_DIR=~/phoenix/frisson_journal/entries
  mkdir -p "$DEST_DIR"
  filename="$DEST_DIR/$(echo "$timestamp" | sed 's/[: ]/-/g').md"

  {
    echo "# Frisson Entry: $timestamp"
    echo "**Tags:** $tags"
    echo "**Entry:** $entry"
  } > "$filename"

  echo "$(date): Frisson '$timestamp' → $filename | Tags: $tags" >> ~/phoenix/rituals/tag_index.txt
  echo "✅ Frisson entry saved to: $filename"

else
  # General note flow
  echo "📁 Choose destination folder:"
  select DEST_FOLDER in emotional_logs oslo_strategy phoenix_portfolio training_strategy resonance.sh cleansing rituals
  do
    break
  done

  read -p "Or type a new folder name (leave blank to skip): " NEW_FOLDER
  if [ -n "$NEW_FOLDER" ]; then
    DEST_FOLDER="$NEW_FOLDER"
  fi

  DEST_DIR=~/phoenix/$DEST_FOLDER
  mkdir -p "$DEST_DIR"

  read -p "Note title: " NOTE_TITLE
  read -p "Tags (comma-separated): " NOTE_TAGS
  filename="$DEST_DIR/${NOTE_TITLE// /_}.md"

  {
    echo "**Tags:** $NOTE_TAGS"
    echo ""
    echo "$LOG"
  } > "$filename"

  echo "$(date): General '$NOTE_TITLE' → $filename | Tags: $NOTE_TAGS" >> ~/phoenix/rituals/tag_index.txt
  echo "$(date): Archived '$NOTE_TITLE' to '$filename'" >> ~/phoenix/rituals/archive_log.txt

  echo "✅ General note saved to: $filename"
fi
