"""
BLOOM AI Agent - Reddit Integration
Monitors Reddit for opportunities and executes marketing strategies.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import praw
from praw.models import Submission, Comment

logger = logging.getLogger(__name__)


class RedditMonitor:
    """
    Monitors Reddit for marketing opportunities and executes strategies.
    """

    # Target subreddits with member counts and focus areas
    TARGET_SUBREDDITS = {
        'ArtistLounge': {
            'members': 487000,
            'focus': 'digital artists',
            'keywords': ['stolen', 'copyright', 'ai training', 'protect', 'theft']
        },
        'WeAreTheMusicMakers': {
            'members': 1200000,
            'focus': 'musicians',
            'keywords': ['copyright', 'stolen', 'streaming', 'rights', 'protect']
        },
        'gamedev': {
            'members': 1100000,
            'focus': 'game developers',
            'keywords': ['asset', 'stolen', 'copyright', 'protect', 'ai']
        },
        'freelance': {
            'members': 284000,
            'focus': 'freelancers',
            'keywords': ['client', 'theft', 'copyright', 'protect', 'work stolen']
        },
        'DigitalArt': {
            'members': 500000,
            'focus': 'digital artists',
            'keywords': ['ai', 'stolen', 'training', 'protect', 'copyright']
        }
    }

    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
            user_agent='BLOOM AI Agent v1.0'
        )

        # Track our posts and comments
        self.our_posts: List[str] = []  # Post IDs
        self.our_comments: List[str] = []  # Comment IDs

        logger.info("Reddit monitor initialized")

    def find_opportunities(self, limit: int = 50) -> List[Dict]:
        """
        Search target subreddits for relevant posts.
        Returns list of opportunities with relevance scores.
        """
        opportunities = []

        for subreddit_name, info in self.TARGET_SUBREDDITS.items():
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Get recent posts
                for submission in subreddit.new(limit=limit):
                    # Skip if too old (>24 hours)
                    post_age = datetime.utcnow() - datetime.utcfromtimestamp(submission.created_utc)
                    if post_age > timedelta(hours=24):
                        continue

                    # Calculate relevance
                    relevance = self._calculate_relevance(submission, info['keywords'])

                    if relevance > 0.3:  # Threshold for relevance
                        opportunities.append({
                            'type': 'reddit_post',
                            'subreddit': subreddit_name,
                            'post_id': submission.id,
                            'post_title': submission.title,
                            'post_content': submission.selftext,
                            'post_url': submission.url,
                            'author': str(submission.author),
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'relevance_score': relevance,
                            'created_utc': submission.created_utc
                        })

                logger.info(f"Found {len([o for o in opportunities if o['subreddit'] == subreddit_name])} "
                          f"opportunities in r/{subreddit_name}")

            except Exception as e:
                logger.error(f"Error scanning r/{subreddit_name}: {e}")

        # Sort by relevance score
        opportunities.sort(key=lambda x: x['relevance_score'], reverse=True)

        logger.info(f"Total opportunities found: {len(opportunities)}")
        return opportunities

    def _calculate_relevance(self, submission: Submission, keywords: List[str]) -> float:
        """
        Calculate relevance score (0-1) based on keyword matches.
        """
        text = f"{submission.title} {submission.selftext}".lower()

        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in text)

        # Base score from keyword density
        score = min(matches / len(keywords), 1.0)

        # Boost for questions (users seeking help)
        if '?' in submission.title:
            score *= 1.3

        # Boost for recent posts
        post_age_hours = (datetime.utcnow() - datetime.utcfromtimestamp(submission.created_utc)).total_seconds() / 3600
        if post_age_hours < 6:
            score *= 1.2

        # Boost for posts with engagement but not too much (avoid overwhelming threads)
        if 5 < submission.num_comments < 50:
            score *= 1.1

        return min(score, 1.0)

    def post_comment(self, post_id: str, comment_text: str, tracking_id: str) -> Optional[str]:
        """
        Post a comment on a Reddit post with tracking.
        Returns comment ID if successful.
        """
        try:
            submission = self.reddit.submission(id=post_id)

            # Add UTM tracking to any BLOOM URLs in the comment
            tracked_text = self._add_tracking(comment_text, tracking_id, 'comment')

            comment = submission.reply(tracked_text)

            self.our_comments.append(comment.id)

            logger.info(f"✅ Posted comment on r/{submission.subreddit.display_name} - "
                       f"Post: '{submission.title[:50]}...' | Comment ID: {comment.id}")

            return comment.id

        except Exception as e:
            logger.error(f"Error posting comment to {post_id}: {e}")
            return None

    def create_post(self, subreddit_name: str, title: str, text: str,
                   tracking_id: str) -> Optional[str]:
        """
        Create an educational post in a subreddit.
        Returns post ID if successful.
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Add UTM tracking to any BLOOM URLs
            tracked_text = self._add_tracking(text, tracking_id, 'post')

            submission = subreddit.submit(title=title, selftext=tracked_text)

            self.our_posts.append(submission.id)

            logger.info(f"✅ Created post in r/{subreddit_name} - "
                       f"Title: '{title}' | Post ID: {submission.id}")

            return submission.id

        except Exception as e:
            logger.error(f"Error creating post in r/{subreddit_name}: {e}")
            return None

    def _add_tracking(self, text: str, tracking_id: str, action_type: str) -> str:
        """
        Add UTM tracking to BLOOM URLs in text.
        """
        # If text contains bloom.com or mentions signing up, add tracking link
        bloom_url = f"https://bloom.com?utm_source=reddit&utm_medium=ai_agent&utm_campaign={tracking_id}&utm_content={action_type}"

        # If no URL in text, append it naturally
        if 'bloom.com' not in text.lower() and 'http' not in text.lower():
            text += f"\n\n(You can check out BLOOM at {bloom_url})"

        return text

    def get_post_performance(self, post_id: str) -> Dict:
        """
        Get performance metrics for a specific post.
        """
        try:
            submission = self.reddit.submission(id=post_id)

            return {
                'post_id': post_id,
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'views': getattr(submission, 'view_count', 0),
                'created_utc': submission.created_utc
            }

        except Exception as e:
            logger.error(f"Error getting performance for post {post_id}: {e}")
            return {}

    def monitor_our_posts(self) -> List[Dict]:
        """
        Check performance of all our posts.
        """
        performance = []

        for post_id in self.our_posts:
            metrics = self.get_post_performance(post_id)
            if metrics:
                performance.append(metrics)

        return performance


class RedditStrategy:
    """
    Executes specific Reddit marketing strategies.
    """

    def __init__(self, monitor: RedditMonitor, agent):
        """Initialize with RedditMonitor and BloomAIAgent"""
        self.monitor = monitor
        self.agent = agent

    def execute_value_comment_strategy(self) -> bool:
        """
        Find opportunity and post valuable comment.
        Returns True if successful.
        """
        # Find opportunities
        opportunities = self.monitor.find_opportunities(limit=30)

        if not opportunities:
            logger.info("No Reddit opportunities found")
            return False

        # Pick best opportunity
        best = opportunities[0]

        # Generate comment content
        context = {
            'subreddit': best['subreddit'],
            'post_title': best['post_title'],
            'post_content': best['post_content']
        }

        comment_text = self.agent.generate_content('reddit_value_comment', context)

        # Post comment
        tracking_id = f"reddit_comment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        comment_id = self.monitor.post_comment(
            post_id=best['post_id'],
            comment_text=comment_text,
            tracking_id=tracking_id
        )

        return comment_id is not None

    def execute_educational_post_strategy(self, subreddit: str = None,
                                         topic: str = None) -> bool:
        """
        Create an educational post in target subreddit.
        Returns True if successful.
        """
        # Choose subreddit if not specified
        if not subreddit:
            subreddit = list(self.monitor.TARGET_SUBREDDITS.keys())[0]

        # Generate topic if not specified
        if not topic:
            topic = "protecting your digital content from unauthorized AI training"

        # Generate post content
        context = {
            'subreddit': subreddit,
            'topic': topic
        }

        content = self.agent.generate_content('reddit_educational_post', context)

        # Extract title (first line) and body
        lines = content.split('\n', 1)
        title = lines[0].replace('#', '').strip()
        body = lines[1].strip() if len(lines) > 1 else content

        # Create post
        tracking_id = f"reddit_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        post_id = self.monitor.create_post(
            subreddit_name=subreddit,
            title=title,
            text=body,
            tracking_id=tracking_id
        )

        return post_id is not None
