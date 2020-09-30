## Rules of Texas Hold Em found there : https://www.youtube.com/watch?v=GAoR9ji8D6A
## More informations on the blinds : https://en.wikipedia.org/wiki/Blind_(poker)
## More rules about all-in and side pots : https://www.youtube.com/watch?v=rxXzo3UXitY
## Informations on who wins based on hands : https://poker.stackexchange.com/questions/6680/how-to-determine-the-winning-hands-in-poker

import os
import sys
from game import Game

if __name__=='__main__':
    os.system('color')
    if sys.argv[1]=='autoplay':
        Game(6,1500,autoplay=True)
    else:
        Game(6,1500)