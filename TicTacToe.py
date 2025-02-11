playerwins = 0
import random
import time

Players = 1
bots = 2

playerWinCheck = False
botWinCheck = False

# first 9 bits on right are player
# 9 bits on left are bot

boardstate = 0b0000000000000000000

botmask    = 0b111111111000000000
playermask = 0b000000000111111111

winscenarios = [
    0b111000000,
    0b000111000,
    0b000000111,
    0b100100100,
    0b010010010,
    0b001001001,
    0b100010001,
    0b001010100
]



tl = 0b100 << 6
tm = 0b010 << 6
tr = 0b001 << 6

ml = 0b100 << 3
mm = 0b010 << 3
mr = 0b001 << 3

bl = 0b100
bm = 0b010
br = 0b001

userinput = {
    "tl": tl,
    "tm": tm,
    "tr": tr,
    "ml": ml,
    "mm": mm,
    "mr": mr,
    "bl": bl,
    "bm": bm,
    "br": br
}

rpositions = [
  (2, 2), (2, 1), (2, 0),
  (1, 2), (1, 1), (1, 0),
  (0, 2), (0, 1), (0, 0)
]

choices = {
    0b000000000000000001 : mm,
    0b000000000000000010 : mm,

    0b000010000000000101 : bm,
    0b000010010010000101 : [ml, mr],

    0b000010000000000011 : bl,
    0b000010100001000011 : mr,
    0b000011100001100011 : [tl, tm],

    0b000110010010001101 : tr,
    0b000010000100000001 : [tm, ml, mr, bm],
    0b000010010110000001 : tr,
    0b010010100101000011 : [ml, mr],

    0b000010000010000010 : [tl, tr, bl, br],
    0b001010000010000110 : br,

    0b000010000100000010 : [tm, tr, ml, mr, bl, br],
    0b001010000100000110 : ml,
    0b001110000100001110 : br,
    0b110000100001010 : [tm, tr, bl, br],
    0b11000100100010 : bl,
    0b10001100100010 : bl,
    0b10100101000010 : tm,
    0b10010000100100010 : bl,
    0b11100101100010 : tm,
    0b10101101100010 : tm,
    0b110001101000110 : mr,
    0b10000010100000 : [tl, tr, bl],
    0b10001110100000 : [tr, bl],
    0b11000110100000 : [bl, tr],
    0b100001000010110000 : bm,
    0b1000000100010000 : br,
    0b1000001110010000 : mr,
    0b100000100000110001 : mr,
    0b101000010010110100 : mr,
    0b100000000000010010 : tm,
    0b100100100011000 : br,
    0b100101100011010 : tm,
    0b100000110011110000 : mr,
    0b10001100100110010 : br,
    0b1001000100110000 : br,
    0b1001100110000 : tr,
    0b1100010000 : [tm, tr, ml , br, bl, bm],
    0b11100010100 : ml,
    0b1100000000010101 : bm,
    0b1000001100010100 : mr,
    0b10001010101000 : tl,
    0b10001000101010 : tl,




    #Start in the Center
    0b000000000000010000 : [tl, tr, bl, br],
    0b100000000000110000 : mr,
    0b100001000000110100 : tr,
    0b101100000000011101 : tm,


    #win Scenarios
    0b000010001000100110 : tl,
    0b000010001000001110 : tl,
    0b000010001001000110 : tl,
    0b000010001010000110 : tl,

    0b100010100010100011 : tr,


}

draws = [
    0b010110001101001110,
    0b010011100101100011,
    0b001100011110011100,
    0b001110001110001110,

]

humanplayer = 0
botplayer = 1

def is_full():
    rval = False
    fullboard = ( boardstate >> 9 ) | ( boardstate & playermask)
    if (fullboard & playermask) == playermask:
        rval = True
    return rval

def int_to_matrix(subboard):
    matrix  = [[0] * 3 for _ in range(3)]

    rboard = 0
    for bit_pos in range(9):
        row, col = rpositions[bit_pos]
        matrix[row][col] = (subboard >> bit_pos) & 1

    return matrix

def matrix_to_int( matrix ):
    rboard = 0

    for bit_pos in range(9):
        row, col = rpositions[bit_pos]
        if matrix[row][col] == 1:
            rboard |= (1 << bit_pos)

    return rboard

def rotate_matrix(matrix):
    rmatrix = [[0] * 3 for _ in range(3)]

    for i in range(3):
        for j in range(3):
            rmatrix[j][2-i] = matrix[i][j]

    return rmatrix

def rotate_matrix_ccw(matrix):
    rmatrix = [[0] * 3 for _ in range(3)]

    for i in range(3):
        for j in range(3):
            rmatrix[2 - j][i] = matrix[i][j]

    return rmatrix

def rotate_board_part(subboard):
    matrix = int_to_matrix( subboard )
    rmatrix = rotate_matrix(matrix)
    rboard = matrix_to_int(rmatrix)

    return rboard

def rotate_board_part_ccw(subboard):
    matrix = int_to_matrix( subboard )
    rmatrix = rotate_matrix_ccw(matrix)
    rboard = matrix_to_int(rmatrix)

    return rboard

def mirror_matrix_ltr(matrix):
    mirrored = [row[::-1] for row in matrix]
    return mirrored

def mirror_matrix_ttb(matrix):
    mirrored = matrix[::-1]
    return mirrored

def mirror_board(board, rtype):
    playerpart = board & playermask
    botpart = board >> 9

    rfunc = [
      mirror_matrix_ltr,
      mirror_matrix_ttb
    ]

    matrix = int_to_matrix( playerpart )
    mmatrix = rfunc[rtype](matrix)
    mpp = matrix_to_int(mmatrix)

    matrix = int_to_matrix( botpart )
    mmatrix = rfunc[rtype](matrix)
    mbp = matrix_to_int(mmatrix)

    newboard = (mbp << 9) | mpp

    return newboard

def rotate_board(board):
    playerpart = board & playermask
    botpart = board >> 9

    rpp = rotate_board_part(playerpart)
    rbp = rotate_board_part(botpart)

    newboard = (rbp << 9) | rpp

    return newboard

def turn(player, move):
    global boardstate
    if checkAvailable( move):
        if player == botplayer:
            boardstate = boardstate | move << 9
        else:
            boardstate |= move

        return True
    else:
        return False




def testWin():
    global boardstate

    winstate = 0
    botstate = boardstate >> 9
    playerstate = boardstate & playermask

    for scen in winscenarios:
        botscen = botstate & scen
        plyscen = playerstate & scen

        if  botscen == scen:
            winstate = 1

        if plyscen == scen:
                winstate = 2

    return winstate

def decide():
    choice = 0
    rn = 0
    mh = False
    mv = False

    nboardstate = boardstate;

    for r in range(3):
        print("searching boardstate: " + bin(nboardstate))
        if nboardstate in choices:
            print("found boardstate rot: "  + str(rn) + " " + bin(nboardstate))
            choice = choices[nboardstate]
            break
        else:
            mhboardstate = mirror_board(nboardstate, 0)
            if mhboardstate in choices:
                print("found boardstate mh: " + bin(mhboardstate))
                choice = choices[mhboardstate]
                mh = True
                break

            print("before mirror v: " + bin(nboardstate))
            mvboardstate = mirror_board(nboardstate, 1)
            if mvboardstate in choices:
                print("found boardstate mv: " + bin(mvboardstate))
                choice = choices[mvboardstate]
                mv = True
                break

            mhvboardstate = mirror_board(mhboardstate, 1)
            if mhvboardstate in choices:
                print("found boardstate mvh: " + bin(mhvboardstate))
                choice = choices[mhvboardstate]
                mv = True
                mh = True
                break

            nboardstate = rotate_board(nboardstate)
            rn += 1

    print( "rotations: " + str(rn) )
    print( "mh: " + str(mh) )
    print( "mv: " + str(mv) )


    if isinstance(choice, list):
        array_length = len(choice)
        random_index = random.randint(0, array_length - 1)
        choice = choice[random_index]

    print( "choice: " + bin(choice) )

    for r in range( rn ):
        print("-r")
        choice = rotate_board_part_ccw(choice)

    if mh:
        print("-mh")
        matrix = int_to_matrix( choice )
        if rn == 1:
            mmatrix = mirror_matrix_ttb(matrix)
        else:
            mmatrix = mirror_matrix_ltr(matrix)
        choice = matrix_to_int(mmatrix)

    if mv:
        print("-mv")
        matrix = int_to_matrix( choice )
        if rn == 1:
            mmatrix = mirror_matrix_ltr(matrix)
        else:
            mmatrix = mirror_matrix_ttb(matrix)
        choice = matrix_to_int(mmatrix)

    print( "choice after: " + bin(choice) )

    return choice

def checkAvailable( move ):
    rval = True
    if (boardstate & move) != 0:
        rval = False
    elif (boardstate & ( move << 9 )) != 0:
        rval = False
    return rval

def fgr(space):
    rval = " "
    if ((boardstate >> 9) & space) == space:
        rval = "O"
    elif ((boardstate & playermask) & space) == space:
       rval = "X"
    return rval

def print_board():
    print(fgr(tl) + "|" + fgr(tm) + "|" + fgr(tr))
    print("-----")
    print(fgr(ml) + "|" + fgr(mm) + "|" + fgr(mr))
    print("-----")
    print(fgr(bl) + "|" + fgr(bm) + "|" + fgr(br))


def testScenarios():

    if turn( humanplayer, tl):
        print("you went")
    else:
        print("already there man")

    if turn( humanplayer, tm):
        print("you went")
    else:
        print("already there man")


    if turn( humanplayer, tr):
        print("you went")
    else:
        print("already there man")

    testWin()

    for scenario in winscenarios:

        boardstate = 0
        boardstate |= ( scenario )
        turn( botplayer, tl)
        turn( botplayer, mm)
        print_board()
        testWin()

        boardstate = 0
        boardstate |= ( scenario << 9)
        turn( humanplayer, tl)
        turn( humanplayer, mm)
        print_board()
        testWin()

def main():

    global boardstate
    global playerwins

    iterations = 3
    games = 0
    playerwins = 0

    print("Tictactoe first to 3 you are X and can go tl, tm, tr, ml, mm, mr, bl, bm, br (also reset, exit, rotate, mh, mv)")

    boardstate = 0

    for i in range(iterations):

        while games < 3:
            print("Game Number " + str(games + 1))

            print_board()

            move = input("Where do you want to go?")

            if move == "exit":
                exit()
            elif move == "reset":
                boardstate = 0
                continue
            elif move == "rotate":
                boardstate = rotate_board(boardstate)
                continue
            elif move == "mh":
                boardstate = mirror_board(boardstate, 0)
                continue
            elif move == "mv":
                boardstate = mirror_board(boardstate, 1)
                continue
            elif move == "decide":
                choice = decide()
                strasdf = bin(choice)
                print("choice " + strasdf)
                continue


            elif move in userinput:
                choice = userinput[move]
                if turn( humanplayer, choice):
                    print("You placed an X on the board :3")

                else:
                    print("GO SOMEWHERE ELSE! THAT SPOT IT ALREADY TAKEN!")
                    continue
            else:
                print("Tictactoe first to 3 you are X and can go tl, tm, tr, ml, mm, mr, bl, bm, br")
                continue

            #if boardstate in draws:
            if not testWin() and is_full():
                print("Draw NO ONE WINS")
                boardstate = 0
                games += 1
                continue

            if not is_full():

                choice = decide()
                print(choice)
                if choice:
                    turn (botplayer, choice)

                else:
                    randomChoice = [
                        tl,
                        tm,
                        tr,
                        ml,
                        mm,
                        mr,
                        bl,
                        bm,
                        br,
                    ]
                    while True:
                        theChoice = randomChoice [random.randint(0, 8)]

                        if turn(botplayer, theChoice):
                            print("IT DID RANDOM THINGY")
                            break

                    binary_string = bin(boardstate)
                    print("Missing board state in choices " + binary_string)

            winstate = testWin()
            if winstate == 2 or winstate == 1:
                boardstate = 0
                games += 1
            if winstate == 2:
                playerwins += 1
                print("Player wins!")
            elif winstate == 1:
                print("Bot wins!")



main()


for ii in "YOU WON " + str(playerwins) + " GAMES":
    print(ii, flush=True, end="")
    time.sleep(0.5)

if playerwins == 0:
    print("loser, im in :D")
    print("Wiping memory >:)")


exit()
