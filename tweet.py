import re
from dataclasses import dataclass
import enum
from pprint import pprint
from typing import Optional, List, Tuple


@dataclass
class TweetUser:
    """
    information of the user who posted a tweet

    https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user

    Attributes:
        id: The integer representation of the unique identifier for this User.
        name: The name of the user, as they’ve defined it. Not necessarily a person’s name.
            Typically capped at 50 characters, but subject to change.
        screen_name: The screen name, handle, or alias that this user identifies themselves with.
            screen_names are unique but subject to change
        lcoation: Nullable . The user-defined location for this account’s profile.
            Not necessarily a location, nor machine-parseable.
        url: Nullable . A URL provided by the user in association with their profile.
        description: Nullable . The user-defined UTF-8 string describing their account.
        protected: When true, indicates that this user has chosen to protect their Tweets.
        verified: When true, indicates that the user has a verified account.
        followers_count: The number of followers this account currently has. Under certain conditions of duress,
            this field will temporarily indicate “0”
        friends_count: The number of users this account is following (AKA their “followings”).
            Under certain conditions of duress, this field will temporarily indicate “0”.
        listed_count: The number of public lists that this user is a member of
        favourites_count:  The number of Tweets this user has liked in the account’s lifetime.
        statuses_count:  The number of Tweets (including retweets) issued by the user
        created_at:  he UTC datetime that the user account was created on Twitter Example:
            "Mon Nov 29 21:18:15 +0000 2010"
        profile_banner_url: The HTTPS-based URL pointing to the standard web representation
            of the user’s uploaded profile banner.
            By adding a final path element of the URL, it is possible to obtain different
            image sizes optimized for specific displays.
        profile_image_url_https: A HTTPS-based URL pointing to the user’s profile image
        default_profile: When true, indicates that the user has not altered the theme or
            background of their user profile
        default_profile_image: When true, indicates that the user has not uploaded their own profile image
            and a default image is used instead.
        withheld_in_countries: When present, indicates a list of uppercase two-letter country codes this content
            is withheld from. Twitter supports the following non-country values for this field:
                “XX” - Content is withheld in all countries
                “XY” - Content is withheld due to a DMCA request
            two-letter country codes: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    """
    id: int
    name: str
    screen_name: str
    location: Optional[str]
    url: Optional[str]
    description: Optional[str]
    protected: bool
    verified: bool
    followers_count: int
    friends_count: int
    listed_count: int
    favourites_count: int
    statuses_count: int
    created_at: str
    profile_banner_url: Optional[str]
    profile_image_url_https: str
    default_profile: bool
    default_profile_image: bool
    withheld_in_countries: List[str]

    @staticmethod
    def deserializer(data: dict) -> 'TweetUser':
        return TweetUser(
            id=data['id'],
            name=data['name'],
            screen_name=data['screen_name'],
            location=data['location'],
            url=data['url'],
            description=data['description'],
            protected=data['protected'],
            verified=data['verified'],
            followers_count=data['followers_count'],
            friends_count=data['friends_count'],
            listed_count=data['listed_count'],
            favourites_count=data['favourites_count'],
            statuses_count=data['statuses_count'],
            created_at=data['created_at'],
            profile_banner_url=data.get('profile_banner_url', None),
            profile_image_url_https=data['profile_image_url_https'],
            default_profile=data['default_profile'],
            default_profile_image=data['default_profile_image'],
            withheld_in_countries=data['withheld_in_countries'],
        )


@dataclass
class Hashtag:
    """
    he ``Entities`` section will contain a ``Hashtag`` array containing an object for
    every hashtag included in the Tweet body,
    and include an empty array if no hashtags are present.

    Attributes:
        indices: An array of integers indicating the offsets within the Tweet text
            where the hashtag begins and ends. The first integer represents the location
            of the # character in the Tweet text string. The second integer represents the
            location of the first character after the hashtag. Therefore the difference between
            the two numbers will be the length of the hashtag name plus one (for the ‘#’ character)
        text: Name of the hashtag, minus the leading ‘#’ character.
    """
    indices: Tuple[int, int]
    text: str

    @staticmethod
    def deserializer(data: dict) -> 'Hashtag':
        return Hashtag(
            indices=tuple(data['indices']),
            text=data['text'],
        )


@dataclass
class Url:
    """
    The ``Entities`` section will contain a ``Url`` array containing an object
    for every link included in the Tweet body, and include an empty array
    if no links are present.

    Attributes:
        display_url:  URL pasted/typed into Tweet
        expanded_url: Expanded version of `` display_url``
        indices:  An array of integers representing offsets within the Tweet text where the URL begins
            and ends. The first integer represents the location of the first character of the URL
            in the Tweet text. The second integer represents the location of the first non-URL
            character after the end of the URL
        url: Wrapped URL, corresponding to the value embedded directly into the
            raw Tweet text, and the values for the indices parameter
    """
    display_url: str
    expanded_url: str
    indices: Tuple[int, int]
    url: str

    @staticmethod
    def deserializer(data: dict) -> 'Url':
        return Url(
            display_url=data['display_url'],
            expanded_url=data['expanded_url'],
            indices=tuple(data['indices']),
            url=data['url'],
        )


@dataclass
class UserMention:
    """
    The ``Entities`` section will contain a ``UserMention`` array containing an object for every user mention
    included in the Tweet body, and include an empty array if no user mention is present.

    Attributes:
        id: ID of the mentioned user, as an integer.
        indices:  An array of integers representing the offsets within the Tweet text where the user reference
            begins and ends. The first integer represents the location of the ‘@’ character of the user mention.
            The second integer represents the location of the first non-screenname character following the user mention.
        name: Display name of the referenced user.
        screen_name: Screen name of the referenced user
    """
    id: int
    indices: Tuple[int, int]
    name: str
    screen_name: str

    @staticmethod
    def deserializer(data: dict) -> 'UserMention':
        return UserMention(
            id=data['id'],
            indices=tuple(data['indices']),
            name=data['name'],
            screen_name=data['screen_name'],

        )



@dataclass
class Symbol:
    """
    The ``Entities`` section will contain a ``Symbol`` array containing an object for every $cashtag included in
    the Tweet body, and include an empty array if no symbol is present.

    Attributes:
        indices: An array of integers indicating the offsets within the Tweet text where the symbol/cashtag
            begins and ends. The first integer represents the location of the $ character in the Tweet text string.
            The second integer represents the location of the first character after the cashtag.
            Therefore the difference between the two numbers will be the length of the hashtag name
            plus one (for the ‘$’ character).
        text: Name of the cashhtag, minus the leading ‘$’ character.
    """
    indices: Tuple[int, int]
    text: str
    @staticmethod
    def deserializer(data: dict) -> 'Symbol':
        return Symbol(
            indices=tuple(data['indices']),
            text    =data['text'],
        )


@dataclass
class Entities:
    """
    The entities object is a holder of arrays of other entity sub-objects.
    After illustrating the entities structure, data dictionaries for these sub-objects, and the Operators that match
    them, will be provided.

    Attributes:
        hashtags: Represents hashtags which have been parsed out of the Tweet text.
        urls: Represents URLs included in the text of a Tweet.
        user_mentions: Represents other Twitter users mentioned in the text of the Tweet.
        symbols: epresents symbols, i.e. $cashtags, included in the text of the Tweet.
    """
    hashtags: List[Hashtag]
    urls: List[Url]
    user_mentions: List[UserMention]
    symbols: List[Symbol]

    @staticmethod
    def deserializer(data: dict) -> 'Entities':
        return Entities(
            hashtags=[Hashtag.deserializer(x) for x in data['hashtags']],
            urls=[Url.deserializer(x) for x in data['urls']],
            user_mentions=[UserMention.deserializer(x) for x in data['user_mentions']],
            symbols=[Symbol.deserializer(x) for x in data['symbols']]
        )


@dataclass
class Tweet:
    """

    Notes:
        status is tweet

    Tweeter status document
    https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet

    Attributes:
        created_at: UTC time when this Tweet was created. Example: Wed Oct 10 20:19:24 +0000 2018
        id: The integer representation of the unique identifier for this Tweet.
        text: The actual UTF-8 text of the status update
        source: Utility used to post the Tweet, as an HTML-formatted string.
        in_reply_to_status_id: Nullable. If the represented Tweet is a reply,
            this field will contain the integer representation of the original Tweet’s ID.
        in_reply_to_user_id: Nullable. If the represented Tweet is a reply, this field will contain the integer
            representation of the original Tweet’s author ID.
            This will not necessarily always be the user directly mentioned in the
        in_reply_to_screen_name: Nullable. If the represented Tweet is a reply,
            this field will contain the screen name of the original Tweet’s author
        coordinates: Nullable. Represents the geographic location of this Tweet as reported by the user
            or client application. The inner coordinates array is formatted
            as geoJSON (longitude first, then latitude).
            Example:
                {
                    "coordinates":
                    [
                        -75.14310264,
                        40.05701649
                    ],
                    "type":"Point"
                }
        place: Nullable When present, indicates that the tweet is associated (but not necessarily originating from) a Place
            Example:
                {
                  "attributes":{},
                   "bounding_box":
                  {
                     "coordinates":
                     [[
                           [-77.119759,38.791645],
                           [-76.909393,38.791645],
                           [-76.909393,38.995548],
                           [-77.119759,38.995548]
                     ]],
                     "type":"Polygon"
                  },
                   "country":"United States",
                   "country_code":"US",
                   "full_name":"Washington, DC",
                   "id":"01fbe706f872cb32",
                   "name":"Washington",
                   "place_type":"city",
                   "url":"http://api.twitter.com/1/geo/id/0172cb32.json"
                }
        quoted_status_id: This field contains the integer value Tweet ID of the quoted Tweet
        is_quote_status: Indicates whether this is a Quoted Tweet.
        quoted_status: This attribute contains the Tweet object of the original Tweet that was quoted.
        retweet_count: Number of times this Tweet has been retweeted.
        favorite_count: Nullable. Indicates approximately how many times this Tweet has been liked by Twitter users.
        entities:  Entities which have been parsed out of the text of the Tweet.
        extended_entities: TODO
        favorited:  Nullable. Indicates whether this Tweet has been liked by the authenticating user
        retweeted: Indicates whether this Tweet has been Retweeted by the authenticating user.
        possibly_sensitive: Nullable. This field only surfaces when a Tweet contains a link. The meaning of the field
            doesn’t pertain to the Tweet content itself, but instead it is an indicator that the URL contained in
            the Tweet may contain content or media identified as sensitive content
        lang: ullable. When present, indicates a BCP 47 language identifier corresponding to
            the machine-detected language of the Tweet text, or und
    """
    created_at: str
    id: int
    full_text: str
    source: str
    in_reply_to_status_id: Optional[int]
    in_reply_to_user_id: Optional[int]
    in_reply_to_screen_name: Optional[str]
    user: TweetUser
    coordinates: Optional[dict]
    place: Optional[dict]
    is_quote_status: bool
    quoted_status_id: Optional[int]
    quoted_status: Optional['Tweet']
    retweet_count: int
    favorite_count: int
    entities: Entities
    favorited: Optional[bool]
    retweeted: Optional[bool]
    possibly_sensitive: Optional[bool]
    lang: Optional[str]
    retweeted_status: Optional['Tweet']

    @staticmethod
    def deserializer(data: dict) -> 'Tweet':
        if 'full_text' not in data:
            if data['truncated'] and 'extended_tweet' in data:
                data['full_text'] = data['extended_tweet']['full_text']
            elif 'retweeted_status' in data and 'extended_tweet' in data['retweeted_status']:
                data['full_text'] = data['retweeted_status']['extended_tweet']['full_text']
            else:
                data['full_text'] = data['text']

        return Tweet(
            created_at=data['created_at'],
            id=data['id'],
            full_text=data['full_text'],
            source=data['source'],  # <a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>
            in_reply_to_status_id=data['in_reply_to_status_id'],
            in_reply_to_user_id=data['in_reply_to_user_id'],
            in_reply_to_screen_name=data['in_reply_to_screen_name'],
            user=TweetUser.deserializer(data['user']),
            coordinates=data['coordinates'],
            place=data['place'],
            is_quote_status=data['is_quote_status'],
            quoted_status_id=data.get('quoted_status_id', None),
            quoted_status=Tweet.deserializer(data['quoted_status']) if 'quoted_status' in data else None,
            retweet_count=data['retweet_count'],
            favorite_count=data['favorite_count'],
            entities=Entities.deserializer(data['entities']),
            favorited=data['favorited'],
            retweeted=data['retweeted'],
            possibly_sensitive=data.get('possibly_sensitive', None),
            lang=data['lang'],
            retweeted_status=Tweet.deserializer(data['retweeted_status']) if 'retweeted_status' in data else None
        )
