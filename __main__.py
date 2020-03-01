import json
import trello
from datetime import timedelta, datetime
from typing import Optional, Tuple, Any, Dict, List
from trello import TrelloApi


def _main() -> None:
    config: Dict[str, Any]
    trello: TrelloApi
    config, trello = _get_config()

    for trello_list in trello.boards.get_list(config['board_id']):
        print("Updating due dates")
        set_due_based_on_title(trello, trello_list, config['delay'])
        set_due_based_on_list(trello, trello_list, config['delay'])
        print("Updating members")
        set_members(trello, trello_list, config['member_ids'])
        print("Upading order")
        sort_by_due(trello, trello_list)


def _get_config() -> Tuple[Dict[str, Any], Any]:
    config_fp = 'config.json'
    with open(config_fp, "r") as fp:
        config = json.load(fp)

    trello = TrelloApi(config['app_key'])
    if 'token' not in config:
        url = trello.get_token_url(app_name='Timeboxer',
                                   expires='30days',
                                   write_access=True)
        print(url)
        print('Use the aforementioned url to get a token, then paste it here.')
        config['token'] = input("Paste token:")
        with open(config_fp, "w+") as fp:
            json.dump(config, fp)

    trello.set_token(config['token'])
    return config, trello


def set_due_based_on_title(trello: TrelloApi,
                           trello_list: trello.Lists,
                           delays: Dict[str, int]) -> None:
    """
    Update all cards in a trello list to have a due date if it doesn't exist.

    The due date is 'extra days' from today.
    """
    for card in trello.lists.get_card(trello_list['id']):
        if card['due'] is None:
            for key, value in delays.items():
                if key in card['name']:
                    due = datetime.now() + timedelta(days=value)
                    trello.cards.update(card['id'], due=due)
                    break


def set_due_based_on_list(trello: TrelloApi,
                          trello_list: trello.Lists,
                          delays: Dict[str, int]) -> None:
    """
    Update all cards in a trello list to have a due date if it doesn't exist.

    The due date is 'extra days' from today.
    """
    for key, value in delays.items():
        if key in trello_list['name']:
            _update_due(trello, trello_list, value)
            break
    else:
        _update_due(trello, trello_list, 3)


def _update_due(trello: TrelloApi,
                trello_list: Dict[str, Any],
                extra_days: int) -> None:
    for card in trello.lists.get_card(trello_list['id']):
        if card['due'] is None:
            due = datetime.now() + timedelta(days=extra_days)
            trello.cards.update(card['id'], due=due)


def sort_by_due(trello: TrelloApi, trello_list: trello.Lists) -> None:
    """Sort cards in a list by due date."""
    cards = trello.lists.get_card(trello_list['id'])

    def get_due(x: trello.cards) -> datetime:
        return datetime.strptime(x['due'], "%Y-%m-%dT%H:%M:%S.%fZ")

    for i, card in enumerate(sorted(cards, key=get_due)):
        if i != card['pos']:
            trello.cards.update(card['id'], pos=i)


def set_members(trello: TrelloApi,
                trello_list: trello.Lists,
                members: List[str]) -> None:
    """Set the members for each card in a trello list."""
    card = trello.cards
    for card in trello.lists.get_card(trello_list['id']):
        if not card['idMembers']:
            trello.cards.update(card['id'], idMembers=members)


if __name__ == "__main__":
    _main()
