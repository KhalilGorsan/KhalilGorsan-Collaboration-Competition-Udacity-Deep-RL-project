import random
from collections import deque

import gym
import matplotlib.pyplot as plt
import numpy as np
import torch

from core import TennisWrapper
from maddpg import Maddpg


def train_maddpg(env, maddpg_agent, n_episodes=100, max_t=10000, print_every=100):
    scores_deque = deque(maxlen=print_every)
    scores = []
    for i_episode in range(1, n_episodes + 1):
        states = env.reset()
        maddpg_agent.reset()
        score = []
        while True:
            actions = maddpg_agent.act(states)
            next_states, rewards, dones = env.step(actions)
            maddpg_agent.step(states, actions, rewards, next_states, dones)
            states = next_states
            score += rewards
            if any(dones):
                break
        max_score = np.max(score)
        scores_deque.append(max_score)
        scores.append(max_score)
        print(
            "\rEpisode {}\tAverage Score: {:.2f}".format(
                i_episode, np.mean(scores_deque)
            ),
            end="",
        )
        if i_episode % print_every == 0:
            print(
                "\rEpisode {}\tAverage Score: {:.2f}".format(
                    i_episode, np.mean(scores_deque)
                )
            )
        if np.mean(scores_deque) >= 0.5:
            print(
                "\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}".format(
                    i_episode, np.mean(scores_deque)
                )
            )
            torch.save(maddpg_agent.actor_local.state_dict(), "checkpoint_actor.pth")
            torch.save(maddpg_agent.critic_local.state_dict(), "checkpoint_critic.pth")
            break
    return scores


def main():
    env = TennisWrapper(file_name="./Tennis")
    # state_size = env.observation_size
    # the state size returned by the env is 24 and not 8.
    state_size = 24
    action_size = env.action_size
    random_seed = 10

    maddpg_agent = Maddpg(
        state_size=state_size,
        action_size=action_size,
        num_agents=2,
        random_seed=random_seed,
    )

    scores = train_maddpg(env=env, maddpg_agent=maddpg_agent)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(np.arange(1, len(scores) + 1), scores)
    plt.ylabel("Scores")
    plt.xlabel("Episode #")
    plt.show()


if __name__ == "__main__":
    main()
