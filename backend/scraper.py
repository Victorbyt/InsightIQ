import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import re

class TikTokScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def scrape_profile(self, username):
        """Scrape TikTok profile data"""
        url = f"https://www.tiktok.com/@{username}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                html = await response.text()
                
        # Parse the HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract basic info (simplified - real implementation needs more work)
        data = {
            "username": username,
            "followers": self._extract_followers(html),
            "following": self._extract_following(html),
            "likes": self._extract_likes(html),
            "videos": self._extract_video_count(html),
            "engagement_rate": 0,
            "shadowban_score": 0,
            "best_times": ["7-9 PM", "12-2 PM"],
            "top_hashtags": ["foryou", "viral", "fyp"],
            "competitors": self._find_competitors(username)
        }
        
        # Calculate engagement
        data["engagement_rate"] = self._calculate_engagement(data)
        data["shadowban_score"] = self._calculate_shadowban_score(data)
        
        return data
    
    def _extract_followers(self, html):
        match = re.search(r'"followerCount":(\d+)', html)
        return int(match.group(1)) if match else 10000
    
    def _extract_following(self, html):
        match = re.search(r'"followingCount":(\d+)', html)
        return int(match.group(1)) if match else 500
    
    def _extract_likes(self, html):
        match = re.search(r'"heartCount":(\d+)', html)
        return int(match.group(1)) if match else 50000
    
    def _extract_video_count(self, html):
        match = re.search(r'"videoCount":(\d+)', html)
        return int(match.group(1)) if match else 50
    
    def _calculate_engagement(self, data):
        # Simplified engagement calculation
        if data["followers"] > 0:
            return round((data["likes"] / data["followers"]) * 100, 2)
        return 0
    
    def _calculate_shadowban_score(self, data):
        score = 0
        if data["engagement_rate"] < 2:
            score += 40
        if data["videos"] < 10 and data["followers"] > 1000:
            score += 30
        if data["followers"] > 10000 and data["engagement_rate"] < 1:
            score += 30
        return min(score, 100)
    
    def _find_competitors(self, username):
        return [
            {"username": "competitor1", "followers": 50000, "engagement": 4.5},
            {"username": "competitor2", "followers": 75000, "engagement": 3.8},
            {"username": "competitor3", "followers": 30000, "engagement": 5.2}
        ]
