import os
import tweepy


def post_to_x(message: str) -> None:
    try:
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        )

        response = client.create_tweet(text=message)

        if response and "data" in response and "id" in response.data:
            print(
                f"[X] Publicación enviada: https://x.com/user/status/{response.data['id']}"
            )
        else:
            print(f"[X] Publicación enviada pero sin respuesta clara: {response}")
    except Exception as e:
        print(f"[X] Error al publicar en X: {e}")
