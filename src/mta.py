from resource import Sub

class API:
    def __init__(self, url, token):
        self.url = url
        self.token = token





class Router:

    def subway(self, url):
        return Subway(url, self.token)

    def bus(self, url):
        return Bus(url, self.token)



def main():
    
    mta = API(
        token=5
    )

    mta.subway('ACE').get_station('207th Street Subway')

    mta.bus('BX12').get_stop('207th Street Bus')

main()