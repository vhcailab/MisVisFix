from .utils.pitfalls_helper import PitfallManager


def get_pitfalls():
    manager = PitfallManager()
    return manager.get_pitfalls()