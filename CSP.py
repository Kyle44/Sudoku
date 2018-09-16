# Name: Kyle Fritz
# File: CSP.py
# Date Created: 11/1/16
# Description: Artificial Intelligence Project 3, given input of a sudoku board with constraints, use constraint satisfaction to solve all of the blank pieces and output the board.

import sys

# Sets up 2-D array of len*len elements, all initialized to -1
def setupArr(length):
	arr = [[-1 for x in range(0, length)] for y in range(0, length)] 
	return arr

# make squareValues hold top left position of every square
def makeSquareValuesArr():
	squareValues = []
	i = 0
	while i < 81: # i%27 == 0 every time in loop:
		squareValues.append(i)
		i+=3
		squareValues.append(i)
		i+=3
		squareValues.append(i)
		i+=21 # Want to advance i by 27 in total each loop
	return squareValues

# Get all of the values in all of the squares, from top left square to bottom right
def makeSquaresArrs(board, squares, squareValues):
	i = 0 # keep track of which square we're on in squares Array
	j = 0 # keep track of the number of values in the current square
	while i < 9:
		val = squareValues[i] # top left of current square i
		while j < 9:
			squares[i][j] = board[val] # set square i up with j values
			j+=1
			if val%3 == 2:
				val+=7 # next row
			else:
				val+=1 # next value
		i+=1
		j=0
	return squares

# Which square is val in?
def whichSquare(val, squares):
	i=0
	while val > 26: # not one of the top 3 squares
		val-=27 # subtract the square
		i+=3 # move up 3 squares

	if val%9 < 3:
		return i
	elif val%9 < 6:
		i+=1 # move over 1 more square 
	else:
		i+=2 # move over 2 more squares 
	return i

def findCurrPosInSquare(squareValues, posInSquare, squareNum):
	currPos = squareValues[squareNum] # closest thing to current position
	count = posInSquare # keep track of how many time you have to increase currPos\

	while count > 0:
		if count%3 == 0: 
			currPos+=7 # next row
		else:
			currPos+=1 # next value
		count-=1	
	return currPos

# Get the contents of the square that val is in
def getSquare(val, squares):
	i=0
	while val > 26: # one of the top 3 squares
		val-=27 # subtract the square
		i+=3 # move up 3 squares

	if val%9 < 3:
		square = squares[i] # now you know what square the blank is in
		return square
	elif val%9 < 6:
		i+=1 # move over 1 more square 
	else:
		i+=2 # move over 2 more squares 
	
	square = squares[i] # now you know what square the blank is in
	return square

# Check to see if we can learn any more info about the current position we are at, based on the square that we're in. possibleValues are all the values that board[pos] could be
def checkSquare(square, possibleValues):
	toRemove = [] # the values to get rid of
	for val in possibleValues: # Check all possible values 
		if val in square: # can't be this value
			toRemove.append(val)
	for val in toRemove: # Remove the values
		possibleValues.remove(val)
	return possibleValues

def findCurrPosInCol(posInCol, pos):
	currPos = pos%9 + posInCol * 9 # first val in column + the position in col * 9
	return currPos

# get the column that board[pos] is in
def getCol(pos, board):
	col = []
	start = pos%9
	end = pos%9 + 72

	while start < end:
		col.append(board[start])
		start+=9
	return col	

# Check to see if we can learn any more info about board[pos]. possibleValues are all the values that board[pos] could be
def checkColumn(board, pos, possibleValues): 
	start = pos%9 # first value in column
	end = pos%9 + 72 # last value in column

	while start <= end:
		val = board[start]
		if val in possibleValues:
			possibleValues.remove(val) # whatever is left is what is needed
		start+=9 # next value in column
	return possibleValues

def findCurrPosInRow(posInRow, pos):
	currPos = pos - pos%9 + posInRow # first val in the row + how many times we need to move to get to the position we need in the row
	return currPos

# get the row that board[pos] is in
def getRow(pos, board):
	row = []
	start = pos - pos%9
	end = pos - pos%9 + 9

	while start < end:
		row.append(board[start])
		start+=1
	return row

# Check to see if we can learn any more info about board[pos]. possibleValues are all the values that board[pos] could be
def checkRow(board, pos, possibleValues): 
	start = pos - pos%9 # first value in row
	end = pos - pos%9 + 9 # last value in row

	while start < end:
		val = board[start]
		if val in possibleValues:
			possibleValues.remove(val) # whatever is left is what is needed
		start+=1 # next value in row
	return possibleValues

# print the board
def printBoard(board):
	for pos in range(0, len(board)):
		if pos%9 == 0 and pos != 0:
			print()
		print(board[pos], end='')
	print("\n\n")

# Updates squares array and then gets the square that pos is in and returns them both
def updateSquares(pos, board, squares, squareValues):
	squares = makeSquaresArrs(board, squares, squareValues) # Remake the squares
	square = getSquare(pos, squares)
	return square, squares

# Get all of the possibilities of the given board[pos] to try and minimize the size of possibleValues
def findPossibilities(board, pos, square, possibleValues):
	if board[pos] != '-':
		return board, []
	possibleValues = checkRow(board, pos, possibleValues)
	possibleValues = checkColumn(board, pos, possibleValues)
	possibleValues = checkSquare(square, possibleValues)
	if len(possibleValues) == 1:
		board[pos] = possibleValues[0] # only one possibility
		return board, []
	else: # all the possibilities at this position
		return board, possibleValues

# If one number only shows up once in a square, then you can fill in that position. Use square, row, and col of your current position as safeguards
def fillInBoard(pos, board, listOfPossibilities, currPos, square):
	col = getCol(pos, board) # the values in the column that you're in
	row = getRow(pos, board) # the values in the row that you're in
	possibleValues = ['1','2','3','4','5','6','7','8','9']
	solvable = [] # will contain the solvable values in the square
	numPossibilities = [] # numPossibilities[i] is the amount of times that you find i+1 in listOfPossibilities
	for i in range(0,9):
		numPossibilities.append(0) # eg numPossibilities[0] = 0 counts of '1' in listOfPossibilities

	for possibilities in listOfPossibilities: # eg [2, 4, 7]
		for possibility in possibilities: # eg 2 in [2, 4, 7]
			possibility = int(possibility)-1
			numPossibilities[possibility]+=1 # eg numPossibilities[2-1] = numPossibilities[1]

	for i in range(0,9): # eg 
		if numPossibilities[i] == 1 and str(i+1) not in square and str(i+1) not in row and str(i+1) not in col: # don't try and solve numbers already in the square, row ,or column
			solvable.append(i+1) # i is 0-8, so add 1

	for val in solvable:
		val = str(val)
		for i in range(0,9):
			if val in listOfPossibilities[i]:
				pos = currPos[i]
				board[pos] = val
	return board

def main():
	possibleValues = ['1','2','3','4','5','6','7','8','9','-']
	filename = sys.argv[1] # name of file
	openedFile = open(filename) # open the file
	board = list(openedFile.read()) # board is an array of the board
	for elem in board:
		if elem not in possibleValues: # clear the board to make it only numbers and blanks('-')
			board.remove(elem)

	squareValues = makeSquareValuesArr() # array that holds top left position of every square, used to make squares Array
	squares = setupArr(9) # array containing arrays that hold the square values from top left to bottom right. Setup array
	squares = makeSquaresArrs(board, squares, squareValues) # makes all of the squares

	printBoard(board)

	while '-' in board: # while board not solved
		print("---------->\n\n")
		for pos in range(0, len(board)): # go through each position
			if board[pos] == '-':

				# Fill in square
				square = getSquare(pos, squares) # find the square that you're in currently
				squareNum = whichSquare(pos, squares) # find out which square you're in
				squarePossibilities = [] # Array of arrays containing the possibilities for the values in the current square.
				currPosInSquare = [] # positions on the board in the square that you're in				
				for i in range(0, 9):
					possibleValues = ['1','2','3','4','5','6','7','8','9'] # the possible values that position pos could be			
					currPosInSquare.append(findCurrPosInSquare(squareValues, i, squareNum)) # find the position that you're at in the square
					board, possibleValues = findPossibilities(board, currPosInSquare[i], square, possibleValues)
					squarePossibilities.append(possibleValues) # Get all of the possibilities for every value in square
				square, squares = updateSquares(pos, board, squares, squareValues) # Quick update, because of findPossibilities updating board
				board = fillInBoard(pos, board, squarePossibilities, currPosInSquare, square)

				# Fill in Row
				rowPossibilities = []
				currPosInRow = [] # positions in the row that you're in
				for i in range(0, 9):
					possibleValues = ['1','2','3','4','5','6','7','8','9'] # the possible values that position pos could be			
					currPosInRow.append(findCurrPosInRow(i, pos)) # find the position that you're at in the row
					square = getSquare(currPosInRow[i], squares) # find the square that you're in currently, using the row
					board, possibleValues = findPossibilities(board, currPosInRow[i], square, possibleValues)
					rowPossibilities.append(possibleValues) # Get all of the possibilities for every value in row
				square, squares = updateSquares(pos, board, squares, squareValues) # Quick update
				board = fillInBoard(pos, board, rowPossibilities, currPosInRow, square)

				# Fill in Column
				colPossibilities = []
				currPosInCol = [] # positions in the column that you're in
				for i in range(0, 9):
					possibleValues = ['1','2','3','4','5','6','7','8','9'] # the possible values that position pos could be			
					currPosInCol.append(findCurrPosInCol(i, pos)) # find the position that you're at in the col
					square = getSquare(currPosInCol[i], squares) # find the square that you're in currently, using the col
					board, possibleValues = findPossibilities(board, currPosInCol[i], square, possibleValues)
					colPossibilities.append(possibleValues) # Get all of the possibilities for every value in col
				square, squares = updateSquares(pos, board, squares, squareValues) # Quick update
				board = fillInBoard(pos, board, colPossibilities, currPosInCol, square)
		printBoard(board)

#	printBoard(board)
	return 1
main()