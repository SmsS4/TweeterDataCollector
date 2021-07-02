import time
from typing import List, Callable, Optional, Tuple

import tweepy
import urllib3
import pandas as pd
from tweet import Tweet


def parse_tweets(func):
    """
    Cast tweepy.Status to tweet.Tweet
    """

    def outer_parser(*args, **kwargs) -> List[Tweet]:
        return [Tweet.deserializer(twt._json) for twt in func(*args, **kwargs)]

    return outer_parser


class Listener(tweepy.StreamListener):
    """
    Custom stream listener to call callback method
    """

    def __init__(self, api, callback: Callable[[Tweet], None]):
        super().__init__(api)
        self.__callback = callback

    def on_status(self, tweet):
        self.__callback(Tweet.deserializer(tweet._json))

    def on_error(self, status_code):
        print('error')
        print(status_code)


class DataGetter:
    MAX_COUNT = 200

    def __init__(
            self,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
    ):
        """
        Args:
            consumer_key: API key
            consumer_secret: API secret
            access_token: 3-legged OAuth token
            access_token_secret: 3-legged OAuth secret
        """
        # set auth
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # set api
        self.api = tweepy.API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True
        )

    def verify_authentication(self) -> bool:
        """
        Returns:
            True if authentication verified else False

        """
        try:
            return True if self.api.verify_credentials() else False
        except:
            return False

    def collect_tweets(self, method, count, *args, **kwargs) -> List[tweepy.Status]:
        """
        Tweeter API allow maximum 200 tweets to get
        so if we want to collect more than 200 we have
        to call method more than once

        Args:
            method: method to call
            count: number of tweets to collect
            *args: args of method
            **kwargs: kargs of methd

        Returns:

        """
        cnt = count
        oldest_id = None
        result: List[tweepy.Status] = []
        while cnt:
            if oldest_id is None:
                new_tweets = (
                    method(
                        count=min(self.MAX_COUNT, cnt),
                        *args,
                        **kwargs
                    )
                )
            else:
                new_tweets = (
                    method(
                        count=min(self.MAX_COUNT, cnt),
                        max_id=oldest_id - 1,
                        *args,
                        **kwargs
                    )
                )
            if len(new_tweets) == 0:
                break
            oldest_id = new_tweets[-1].id
            result.extend(new_tweets)
            cnt -= len(new_tweets)
        return result

    @parse_tweets
    def get_timeline_tweets(self, count: int) -> List[Tweet]:
        """
        Gets timeline tweets of api owner
        Args:
            count: number of tweets to get
        """
        return self.collect_tweets(
            self.api.home_timeline,
            count=count,
            tweet_mode='extended',
        )

    @parse_tweets
    def get_historical(self, count: int, users: List[str]) -> List[Tweet]:
        """
        Gets all tweets of users
        Args:
            count: number of tweets of each user
            users: list of users id
        """
        result = []
        for user_id in users:
            result.extend(
                self.collect_tweets(
                    self.api.user_timeline,
                    count=count,
                    screen_name=user_id,
                    tweet_mode='extended',
                )
            )
        return result

    def stream(self, users: List[str], callback: Callable[[Tweet], None]) -> None:
        """
        Get new tweets from users

        Args:
            users: list of users id
            callback: callback method
        """
        users_id = [user._json['id_str'] for user in self.api.lookup_users(screen_names=users)]
        listener = Listener(self.api, callback)
        stream = tweepy.Stream(auth=self.api.auth, listener=listener)
        while True:
            try:
                stream.filter(follow=users_id)
            except  urllib3.exceptions.ProtocolError as e:
                print('error')
                print(e)
                time.sleep(15)


def pretty_print(tweet: Tweet) -> str:
    if tweet.retweeted_status and not tweet.retweeted_status.quoted_status:
        return f'A new retweet\nsender: {tweet.user.screen_name}\nretweet from: {tweet.retweeted_status.user.screen_name}\ntext: {tweet.retweeted_status.full_text}'
    elif tweet.retweeted_status:
        return f'A new retweet\nsender: {tweet.user.screen_name}\nretweet from: {tweet.retweeted_status.user.screen_name}\nquoted from: {tweet.retweeted_status.quoted_status.user.screen_name}\ntext: {tweet.retweeted_status.full_text}\norigin text: {tweet.retweeted_status.quoted_status.full_text}'
    elif tweet.quoted_status:
        return f'A new quoted tweet\nsender: {tweet.user.screen_name}\nquoted from: {tweet.quoted_status.user.screen_name}\nquote text: {tweet.full_text}\norigin text: {tweet.quoted_status.full_text}'
    else:
        return f'A new tweet\nsender: {tweet.user.screen_name}\ntext: {tweet.full_text}'


def get_quote(tweet: Tweet) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns None, None if tweet is not quote
    otherwise return tuple of quoted tweet sender and text
    """
    if tweet.retweeted_status:
        return get_quote(tweet.retweeted_status)
    if not tweet.quoted_status:
        return None, None
    return tweet.quoted_status.user.screen_name, tweet.quoted_status.full_text


def tweets_to_df(tweets: List[Tweet]) -> pd.DataFrame:
    """
    Cast Tweet to df
    """
    return pd.DataFrame(
        [[
            tweet.created_at,
            tweet.user.screen_name,
            tweet.full_text,
            True if tweet.retweeted_status else False,
            None if not tweet.retweeted_status else tweet.retweeted_status.user.screen_name,
            True if get_quote(tweet)[0] else None,
            get_quote(tweet)[0],
            get_quote(tweet)[1]
        ] for tweet in tweets],
        columns=[
            'create time',
            'sender',
            'text',
            'is_retweet',
            'retweet_sender',
            'is_quote',
            'quoted_tweet_sender',
            'quoted_tweet_text'
        ]
    )


if __name__ == '__main__':
    dg = DataGetter(
        consumer_key="",  # API key
        consumer_secret="",  # API secret
        access_token="",
        access_token_secret="",
    )
    print(dg.verify_authentication())

    # for tweet in dg.get_timeline_tweets(1):
    #     print(tweets_to_df([tweet]))
    #     print(pretty_print(tweet))

    # for tweet in dg.get_historical(500, ['BTCTN']):
    #     print(pretty_print(tweet), end="\n---------------\n")

    # dg.stream(['teat65501837'], lambda tweet: print(pretty_print(tweet), end="\n---------------\n"))
