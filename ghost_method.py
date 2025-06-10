
def turno_ghots(perceptions, agents):
    """
    This function simulates a ghost's turn in a game, where it moves towards the player
    if the player is within a certain distance, otherwise it moves randomly.

    :param perceptions: A dictionary containing the positions of the player and the ghost.
    :param agents: A list of agents in the game.
    :return: The new position of the ghost.
    """
    # Retornar una lista de acciones por agente
    actions = []
    actions[0] = "id_agent.command"