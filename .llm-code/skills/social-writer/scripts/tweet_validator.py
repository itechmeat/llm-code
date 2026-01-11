#!/usr/bin/env python3
"""
Tweet Length Validator

Parses markdown file with tweets and validates character limits.

Usage:
    python tweet_validator.py path/to/tweets.md
"""

import sys
import re
from pathlib import Path


TWEET_LIMIT = 280
WARNING_THRESHOLD = 260  # Warn if close to limit


def parse_tweets(content: str) -> list[dict]:
    """Parse markdown file and extract tweets."""
    tweets = []
    
    # Split by horizontal rules (---)
    sections = re.split(r'\n---\n', content)
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
            
        # Extract header (## Reply N: Name or ## Main Tweet)
        header_match = re.match(r'^(?:#[^\n]*\n\n)?##\s+(.+?)(?:\n|$)', section)
        header = header_match.group(1).strip() if header_match else f"Section {i}"
        
        # Get content after header (skip file title like # X Thread...)
        lines = section.split('\n')
        content_lines = []
        skip_next = False
        
        for line in lines:
            # Skip file-level title
            if line.startswith('# ') and not line.startswith('## '):
                continue
            # Skip section headers
            if line.startswith('## '):
                continue
            content_lines.append(line)
        
        tweet_content = '\n'.join(content_lines).strip()
        
        # Remove markdown formatting for character count
        clean_content = tweet_content
        
        # Remove **bold** markers
        clean_content = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_content)
        
        # Remove code blocks
        clean_content = re.sub(r'```[\s\S]*?```', '', clean_content)
        clean_content = re.sub(r'`(.+?)`', r'\1', clean_content)
        
        tweets.append({
            'index': i,
            'header': header,
            'raw': tweet_content,
            'clean': clean_content,
            'length': len(clean_content)
        })
    
    return tweets


def validate_tweets(tweets: list[dict]) -> tuple[bool, list[str]]:
    """Validate tweet lengths and return status + messages."""
    all_valid = True
    messages = []
    
    for tweet in tweets:
        length = tweet['length']
        header = tweet['header']
        
        if length > TWEET_LIMIT:
            all_valid = False
            over = length - TWEET_LIMIT
            messages.append(f"❌ {header}: {length} chars (+{over} over limit)")
            # Show the tweet content
            messages.append(f"   Content: {tweet['clean'][:100]}...")
        elif length > WARNING_THRESHOLD:
            messages.append(f"⚠️  {header}: {length} chars (close to limit)")
        else:
            remaining = TWEET_LIMIT - length
            messages.append(f"✅ {header}: {length} chars ({remaining} remaining)")
    
    return all_valid, messages


def main():
    if len(sys.argv) < 2:
        print("Usage: python tweet_validator.py <path/to/tweets.md>")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    content = filepath.read_text()
    tweets = parse_tweets(content)
    
    print(f"\n📝 Tweet Validator")
    print(f"File: {filepath}")
    print(f"Found: {len(tweets)} sections")
    print(f"Limit: {TWEET_LIMIT} chars")
    print("-" * 50)
    
    all_valid, messages = validate_tweets(tweets)
    
    for msg in messages:
        print(msg)
    
    print("-" * 50)
    
    if all_valid:
        print("✅ All tweets within limit!")
        sys.exit(0)
    else:
        print("❌ Some tweets exceed limit")
        sys.exit(1)


if __name__ == '__main__':
    main()
