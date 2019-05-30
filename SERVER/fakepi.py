class LED:
    def __init__(self, id):
        print('Initialized pin', id)

        self.id = id

    def on(self):
        print('PIN %i IS HIGH' % self.id)

    def off(self):
        print('PIN %i IS LOW' % self.id)