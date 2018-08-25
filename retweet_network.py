"""
retweet_network
"""
import os
import json
import pylab
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import networkx as nx
from smappdragon import TweetParser


# It loads tweets from a given json/jsonl file
# and returns the list of tweets
def load_tweets(in_fname):
    tweets = []
    with open(in_fname, 'r') as f:
        for line in f:
            if len(line.strip()) > 0:
                tweets.append(json.loads(line))
    return tweets

def replace_none(s):
    if s is None:
        return 'NULL'
    return s

def retweet_network(user_timelines_dir, tweet_fields, user_fields):

    tp = TweetParser()
    dg = nx.DiGraph(name="retweet graph")

    valid_user_timeline_file = lambda f: os.path.isfile(user_timelines_dir + f) and f.startswith("user_timeline_") and f.endswith(".json")
    timeline_files = list(filter(valid_user_timeline_file, os.listdir(user_timelines_dir)))

    for timeline in timeline_files:

        # load tweets from each timeline in timelines_directory
        tweets = load_tweets(user_timelines_dir + timeline)

        for tweet in tweets:

            if "user" in tweet:
                um_dict = {field: replace_none(value) for field, value in tp.parse_columns_from_tweet(tweet["user"], user_fields)}
                t_dict = {field: replace_none(value) for field, value in tp.parse_columns_from_tweet(tweet, tweet_fields)}

                if tweet["user"]["id_str"] not in dg:
                    # um_dict = {key: replace_none(tweet["user"][key]) for key in tweet["user"].keys()}
                    dg.add_node(tweet["user"]["id_str"], **um_dict)
                if "retweeted_status" in tweet:

                    # Update retweeted_tweet_attributes from actual tweet
                    # if not avialable in retweet
                    for key in tweet_fields:
                        if t_dict[key] == 'NULL':
                            key, t_dict[key] = tp.parse_columns_from_tweet(tweet['retweeted_status'], [key])

                    rtu_dict = {field: replace_none(value) for field, value in tp.parse_columns_from_tweet(tweet['retweeted_status']['user'], user_fields)}
                    dg.add_node(tweet['retweeted_status']['user']['id_str'], **rtu_dict)
                    dg.add_edge(tweet['user']['id_str'], tweet['retweeted_status']['user']['id_str'], **t_dict)
            # else:
            # the tweet object is not a valid TWEET
            #     print(tweet)
    return dg

def plot_distance_distribution(digraph):
    x = range(len(digraph))
    y = digraph
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.bar(x, y, align='center', width=0.5)
    axes.set_xlabel('Distance')
    axes.set_ylabel('Relative Occurrence')
    axes.set_title('Distance Distribution')

    fig.savefig('data/distance_distribution.png')


def analyze(user_timelines_dir, outFname):


    tweet_fields = ['id_str', 'retweeted_status.id_str', 'created_at', 'text', 'lang']
    user_fields = ['id_str', 'screen_name', 'location', 'lang']

    digraph = retweet_network(user_timelines_dir, tweet_fields, user_fields)
    nx.write_graphml(digraph.to_undirected(), outFname)

    Gf = digraph.to_undirected()

    # Use graphviz
    prog = "neato"  # neato is default layout engine in GraphViz
    # pos = nx.graphviz_layout(Gf, prog=prog, root=None, args="")

    # labels = {}
    # for node in Gf.nodes():
    #     labels[node] = ""
    #     if len(Gf.edges(node)) > 10:
    #         labels[node] = node
    #
    # nx.draw_networkx(Gf, with_labels=True, alpha=0.2, labels=labels, font_size=20, font_family='sans-serif')
    # pylab.axis("off")
    # pylab.title("Followers in small Twitter network")
    # pylab.show()

    # digraph.to_undirected()

    # plot_distance_distribution(digraph.to_undirected())

    print("Network of retweets is exported at [%s]" % outFname)


if __name__ == "__main__":
    # fname = 'data/tweets.json'
    user_timelines_dir = 'data/User_Timelines_Real/'
    export_fname = 'data/collection_retweets.graphml'

    analyze(user_timelines_dir, export_fname)

