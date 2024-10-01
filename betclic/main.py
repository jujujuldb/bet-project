from betclic.src.scheduler import Scheduler


def main():
    # Initialiser le scheduler avec un intervalle de 10 minutes (600 secondes)
    scheduler = Scheduler(interval=600)

    # Lancer la collecte et la comparaison
    scheduler.run()


if __name__ == "__main__":
    main()
