"""
BLOOM AI Agent - Twitter Integration
Monitors Twitter for opportunities and executes marketing strategies.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tweepy

logger = logging.getLogger(__name__)


class TwitterMonitor:
    """
    Monitors Twitter for marketing opportunities and executes strategies.
    """

    # Search keywords for finding opportunities
    SEARCH_KEYWORDS = [
        "art stolen AI",
        "music copyright theft",
        "protect my artwork",
        "AI scraped my art",
        "someone stole my design",
        "copyright infringement help",
        "AI training data consent",
        "unauthorized use of my art"
    ]

    def __init__(self):
        """Initialize Twitter API client"""
        # Twitter API v2 client
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET'),
            wait_on_rate_limit=True
        )

        # Track our tweets
        self.our_tweets: List[str] = []  # Tweet IDs

        logger.info("Twitter monitor initialized")

    def find_opportunities(self, max_results: int = 50) -> List[Dict]:
        """
        Search Twitter for relevant tweets.
        Returns list of opportunities with relevance scores.
        """
        opportunities = []

        for keyword in self.SEARCH_KEYWORDS:
            try:
                # Search recent tweets
                tweets = self.client.search_recent_tweets(
                    query=f"{keyword} -is:retweet -is:reply lang:en",
                    max_results=min(max_results, 100),
                    tweet_fields=['created_at', 'public_metrics', 'author_id'],
                    expansions=['author_id'],
                    user_fields=['username', 'name']
                )

                if not tweets.data:
                    continue

                # Process tweets
                for tweet in tweets.data:
                    # Skip if too old (>24 hours)
                    if isinstance(tweet.created_at, datetime):
                        tweet_age = datetime.now(tweet.created_at.tzinfo) - tweet.created_at
                        if tweet_age > timedelta(hours=24):
                            continue

                    # Calculate relevance
                    relevance = self._calculate_relevance(tweet.text, keyword)

                    if relevance > 0.3:  # Threshold
                        # Get author info
                        author = None
                        if tweets.includes and 'users' in tweets.includes:
                            author = next((u for u in tweets.includes['users'] if u.id == tweet.author_id), None)

                        opportunities.append({
                            'type': 'twitter_tweet',
                            'tweet_id': tweet.id,
                            'tweet_text': tweet.text,
                            'author_id': tweet.author_id,
                            'author_username': author.username if author else 'unknown',
                            'author_name': author.name if author else 'unknown',
                            'likes': tweet.public_metrics['like_count'],
                            'retweets': tweet.public_metrics['retweet_count'],
                            'replies': tweet.public_metrics['reply_count'],
                            'relevance_score': relevance,
                            'keyword': keyword,
                            'created_at': tweet.created_at.isoformat() if isinstance(tweet.created_at, datetime) else str(tweet.created_at)
                        })

                logger.info(f"Found {len([o for o in opportunities if o['keyword'] == keyword])} "
                          f"opportunities for keyword: '{keyword}'")

            except Exception as e:
                logger.error(f"Error searching Twitter for '{keyword}': {e}")

        # Sort by relevance score
        opportunities.sort(key=lambda x: x['relevance_score'], reverse=True)

        # Remove duplicates (same tweet ID)
        seen = set()
        unique_opportunities = []
        for opp in opportunities:
            if opp['tweet_id'] not in seen:
                seen.add(opp['tweet_id'])
                unique_opportunities.append(opp)

        logger.info(f"Total unique opportunities found: {len(unique_opportunities)}")
        return unique_opportunities

    def _calculate_relevance(self, text: str, keyword: str) -> float:
        """
        Calculate relevance score (0-1) based on content.
        """
        text_lower = text.lower()

        # Base score from keyword match
        score = 0.5 if keyword.lower() in text_lower else 0.3

        # Boost for questions
        if '?' in text:
            score *= 1.3

        # Boost for pain points
        pain_words = ['stolen', 'theft', 'unauthorized', 'help', 'scared', 'worried', 'protect']
        pain_count = sum(1 for word in pain_words if word in text_lower)
        score *= (1.0 + pain_count * 0.1)

        # Boost for mentions of AI
        if 'ai' in text_lower or 'artificial intelligence' in text_lower:
            score *= 1.2

        # Boost for creator mentions
        creator_words = ['artist', 'creator', 'musician', 'designer', 'developer']
        if any(word in text_lower for word in creator_words):
            score *= 1.1

        return min(score, 1.0)

    def post_tweet(self, text: str, tracking_id: str) -> Optional[str]:
        """
        Post a single tweet with tracking.
        Returns tweet ID if successful.
        """
        try:
            # Add UTM tracking to any BLOOM URLs
            tracked_text = self._add_tracking(text, tracking_id, 'tweet')

            response = self.client.create_tweet(text=tracked_text)

            tweet_id = response.data['id']
            self.our_tweets.append(tweet_id)

            logger.info(f"✅ Posted tweet | ID: {tweet_id} | Text: '{text[:50]}...'")

            return tweet_id

        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None

    def post_thread(self, tweets: List[str], tracking_id: str) -> Optional[List[str]]:
        """
        Post a thread of tweets.
        Returns list of tweet IDs if successful.
        """
        tweet_ids = []

        try:
            # Post first tweet
            first_tweet = self._add_tracking(tweets[0], tracking_id, 'thread')
            response = self.client.create_tweet(text=first_tweet)
            first_id = response.data['id']
            tweet_ids.append(first_id)
            self.our_tweets.append(first_id)

            # Post subsequent tweets as replies
            previous_id = first_id
            for i, tweet_text in enumerate(tweets[1:], 1):
                tracked = self._add_tracking(tweet_text, tracking_id, f'thread_{i}')
                response = self.client.create_tweet(
                    text=tracked,
                    in_reply_to_tweet_id=previous_id
                )
                tweet_id = response.data['id']
                tweet_ids.append(tweet_id)
                self.our_tweets.append(tweet_id)
                previous_id = tweet_id

            logger.info(f"✅ Posted thread with {len(tweet_ids)} tweets | First ID: {first_id}")

            return tweet_ids

        except Exception as e:
            logger.error(f"Error posting thread: {e}")
            return None

    def reply_to_tweet(self, tweet_id: str, reply_text: str, tracking_id: str) -> Optional[str]:
        """
        Reply to a specific tweet.
        Returns reply tweet ID if successful.
        """
        try:
            # Add UTM tracking
            tracked_reply = self._add_tracking(reply_text, tracking_id, 'reply')

            response = self.client.create_tweet(
                text=tracked_reply,
                in_reply_to_tweet_id=tweet_id
            )

            reply_id = response.data['id']
            self.our_tweets.append(reply_id)

            logger.info(f"✅ Posted reply to tweet {tweet_id} | Reply ID: {reply_id}")

            return reply_id

        except Exception as e:
            logger.error(f"Error replying to tweet {tweet_id}: {e}")
            return None

    def _add_tracking(self, text: str, tracking_id: str, action_type: str) -> str:
        """
        Add UTM tracking to BLOOM URLs in text.
        """
        bloom_url = f"https://bloom.com?utm_source=twitter&utm_medium=ai_agent&utm_campaign={tracking_id}&utm_content={action_type}"

        # If no URL in text, append it naturally
        if 'bloom.com' not in text.lower() and 'http' not in text.lower():
            # Check if we have space (Twitter limit is 280 chars)
            url_addition = f"\n\nCheck out BLOOM: {bloom_url}"
            if len(text + url_addition) <= 280:
                text += url_addition
            else:
                # Try shorter version
                url_addition = f"\n\n{bloom_url}"
                if len(text + url_addition) <= 280:
                    text += url_addition

        return text

    def get_tweet_performance(self, tweet_id: str) -> Dict:
        """
        Get performance metrics for a specific tweet.
        """
        try:
            tweet = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['public_metrics', 'created_at']
            )

            if not tweet.data:
                return {}

            return {
                'tweet_id': tweet_id,
                'likes': tweet.data.public_metrics['like_count'],
                'retweets': tweet.data.public_metrics['retweet_count'],
                'replies': tweet.data.public_metrics['reply_count'],
                'impressions': tweet.data.public_metrics.get('impression_count', 0),
                'created_at': tweet.data.created_at.isoformat() if isinstance(tweet.data.created_at, datetime) else str(tweet.data.created_at)
            }

        except Exception as e:
            logger.error(f"Error getting performance for tweet {tweet_id}: {e}")
            return {}

    def monitor_our_tweets(self) -> List[Dict]:
        """
        Check performance of all our tweets.
        """
        performance = []

        for tweet_id in self.our_tweets:
            metrics = self.get_tweet_performance(tweet_id)
            if metrics:
                performance.append(metrics)

        return performance


class TwitterStrategy:
    """
    Executes specific Twitter marketing strategies.
    """

    def __init__(self, monitor: TwitterMonitor, agent):
        """Initialize with TwitterMonitor and BloomAIAgent"""
        self.monitor = monitor
        self.agent = agent

    def execute_reply_strategy(self) -> bool:
        """
        Find opportunity and post helpful reply.
        Returns True if successful.
        """
        # Find opportunities
        opportunities = self.monitor.find_opportunities(max_results=30)

        if not opportunities:
            logger.info("No Twitter opportunities found")
            return False

        # Pick best opportunity
        best = opportunities[0]

        # Generate reply content
        context = {
            'tweet_text': best['tweet_text'],
            'author_username': best['author_username']
        }

        reply_text = self.agent.generate_content('twitter_reply', context)

        # Ensure reply is under 280 characters
        if len(reply_text) > 280:
            reply_text = reply_text[:277] + "..."

        # Post reply
        tracking_id = f"twitter_reply_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        reply_id = self.monitor.reply_to_tweet(
            tweet_id=best['tweet_id'],
            reply_text=reply_text,
            tracking_id=tracking_id
        )

        return reply_id is not None

    def execute_thread_strategy(self, topic: str = None) -> bool:
        """
        Create an educational thread.
        Returns True if successful.
        """
        # Generate topic if not specified
        if not topic:
            topic = "protecting your creative work from AI scraping"

        # Generate thread content
        context = {
            'topic': topic
        }

        content = self.agent.generate_content('twitter_thread', context)

        # Split into tweets (assume content has numbered tweets or line breaks)
        tweets = []
        lines = content.split('\n\n')

        for line in lines:
            line = line.strip()
            if line:
                # Remove numbering if present
                if line[0].isdigit() and '.' in line[:3]:
                    line = line.split('.', 1)[1].strip()

                # Ensure each tweet is under 280 characters
                if len(line) <= 280:
                    tweets.append(line)
                else:
                    # Split long tweet
                    words = line.split()
                    current = ""
                    for word in words:
                        if len(current + " " + word) <= 277:
                            current += " " + word if current else word
                        else:
                            tweets.append(current)
                            current = word
                    if current:
                        tweets.append(current)

        # Limit to reasonable thread length
        tweets = tweets[:5]

        if not tweets:
            logger.warning("No tweets generated for thread")
            return False

        # Post thread
        tracking_id = f"twitter_thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tweet_ids = self.monitor.post_thread(
            tweets=tweets,
            tracking_id=tracking_id
        )

        return tweet_ids is not None and len(tweet_ids) > 0
