class QM:
    def __init__(self, numInput, minterm, dontcare):
        self.numInput = numInput
        self.minterm = sorted(minterm)
        self.dontcare = sorted(dontcare)
        self.PI = []
        self.EPI = []
        self.petrickResult = []
        self.table = None
        self.rows = 0
        self.cols = 0
        self.expression = []

    def findPI(self):
        table = [[] for _ in range(self.numInput + 1)]
        for num in sorted(self.minterm + self.dontcare):
            numToBin = bin(num)[2:].zfill(self.numInput)
            table[numToBin.count('1')].append({'minterm': {num}, 'binary': numToBin, 'combined': False})

        appended = True
        while appended:
            appended = False
            nextTable = [[] for _ in range(self.numInput + 1)]

            for numOne in range(self.numInput):
                for upper in table[numOne]:
                    for lower in table[numOne + 1]:
                        diffCount = 0
                        for i in range(self.numInput):
                            if upper['binary'][i] != lower['binary'][i]:
                                diffCount += 1

                        if diffCount == 1:
                            appended = True
                            for i in range(self.numInput):
                                if upper['binary'][i] != lower['binary'][i]:
                                    binary = upper['binary']
                                    binary = binary[:i] + '-' + binary[i + 1:]
                                    newElem = {'minterm': set(), 'binary': binary, 'combined': False}
                                    newElem['minterm'] = upper['minterm'] | lower['minterm']

                                    for elem in nextTable[numOne]:
                                        if newElem['minterm'] == elem['minterm']:
                                            break
                                    else:
                                        nextTable[numOne].append(newElem)

                                    upper['combined'] = True
                                    lower['combined'] = True
                                    break

            mtLength = 0
            for numOne in range(len(table)):
                for implicant in table[numOne]:
                    mtLength = max(mtLength, len(str(implicant['minterm'])))
            mtLength = max(9, mtLength + 2)
            bnLength = max(8, self.numInput + 2)
            print('# of 1s │{{:^{}}}│{{:^{}}}│ Combined'.format(mtLength, bnLength).format('Minterm', 'Binary'))

            for numOne in range(len(table)):
                if table[numOne]:
                    first = True
                    for implicant in table[numOne]:
                        print('─' * 8 + '┼' + '─' * mtLength + '┼' + '─' * bnLength + '┼' + '─' * 10)
                        if first:
                            line = '{{:^{}}}'.format(8).format(' ' + str(numOne))
                            first = False
                        else:
                            line = ' ' * 8
                        line += '│{{:>{}}}'.format(mtLength).format(str(implicant['minterm']) + ' ')
                        line += '│{{:>{}}}'.format(bnLength).format(implicant['binary'] + ' ')
                        line += '│    ' + ('○' if implicant['combined'] else '')
                        print(line)

            print('\n')
            foundedPI = []
            for numOne in range(len(table)):
                for implicant in table[numOne]:
                    if not implicant['combined']:
                        implicant.pop('combined')
                        foundedPI.append(implicant)
                        self.PI.append(implicant)
            if foundedPI:
                print('Founded PI')
                print(*foundedPI, sep='\n')
                print('\n')
            table = nextTable

    def makeTable(self):
        table = [[None] + self.minterm]
        for i in range(len(self.PI)):
            row = [self.PI[i]]
            for num in self.minterm:
                row.append(num in self.PI[i]['minterm'])
            table.append(row)
        self.table = table
        self.rows = len(table)
        self.cols = len(table[0])
        self.printTable('After Find PI')

    def remakeTable(self, direction, willDelete):
        if direction == 'row':
            table = [self.table[0]]
            for r in range(1, self.rows):
                if r not in willDelete:
                    table.append(self.table[r])
        elif direction == 'col':
            table = [[self.table[r][0]] for r in range(self.rows)]
            for c in range(1, self.cols):
                if c not in willDelete:
                    for r in range(self.rows):
                        table[r].append(self.table[r][c])
        else:
            return

        self.table = table
        self.rows = len(table)
        self.cols = len(table[0])

    def printTable(self, progress=''):
        if self.rows == 1 or self.cols == 1:
            return

        infoLength = max([len(str(x[0])) for x in self.table[1:]])
        result = '{{:^{}}}'.format(infoLength).format(progress)
        for c in range(1, self.cols):
            result += '│{:>3}'.format(self.table[0][c])

        for row in self.table[1:]:
            result += '\n' + ('─' * infoLength) + ('┼───' * (self.cols - 1)) + '\n'
            result += '{{:>{}}}'.format(infoLength).format(str(row[0]))
            for i in range(1, self.cols):
                result += '│{:^3}'.format('○' if row[i] else '')

        print(result + '\n\n')

    def findEPI(self):
        EPI = set()
        for c in range(1, self.cols):
            taken = False
            epiR = None
            for r in range(1, self.rows):
                if self.table[r][c]:
                    epiR = r
                    if taken:
                        break
                    taken = True
            else:
                if taken:
                    EPI.add(epiR)
        for r in EPI:
            self.EPI.append(self.table[r][0])

        willDelete = set()
        for r in EPI:
            willDelete.update({self.table[0].index(x) for x in self.table[r][0]['minterm'] if x in self.table[0]})

        if willDelete:
            print('Founded EPI')
            for r in sorted(list(EPI)):
                print(self.table[r][0])
            print('\n')
            self.remakeTable('row', EPI)
            self.remakeTable('col', willDelete)
            self.printTable('After Find EPI')
            return True
        else:
            return False

    def rowDominance(self):
        willDelete = set()
        for i in range(1, self.rows):
            if i in willDelete:
                continue
            pivot = {c for c in range(1, self.cols) if self.table[i][c]}
            for j in range(1, self.rows):
                if i == j or j in willDelete:
                    continue

                compare = {c for c in range(1, self.cols) if self.table[j][c]}
                if compare.issubset(pivot):
                    if len(self.table[i][0]['minterm']) >= len(self.table[j][0]['minterm']):
                        print(self.table[i][0], 'Dominate', self.table[j][0])
                        willDelete.add(j)

        if willDelete:
            self.remakeTable('row', willDelete)
            print('\n')
            self.printTable('After Apply Row Dominance')
            return True
        else:
            return False

    def colDominance(self):
        willDelete = set()
        for i in range(1, self.cols):
            if i in willDelete:
                continue
            pivot = {r for r in range(1, self.rows) if self.table[r][i]}
            for j in range(1, self.cols):
                if i == j or j in willDelete:
                    continue

                compare = {r for r in range(1, self.rows) if self.table[r][j]}
                if pivot.issubset(compare):
                    print(self.table[0][j], 'Dominate', self.table[0][i])
                    willDelete.add(j)

        if willDelete:
            self.remakeTable('col', willDelete)
            print('\n')
            self.printTable('After Apply Column Dominance')
            return True
        else:
            return False

    def makeExpression(self):
        for c in range(1, self.cols):
            term = set()
            for r in range(1, self.rows):
                if self.table[r][c]:
                    term.add(frozenset([r]))
            self.expression.append(term)

    def printExpression(self, progress=''):
        result = ''
        for term in self.expression:
            result += '('
            for innerTerm in term:
                for var in innerTerm:
                    result += 'P' + str(var)
                result += ' + '
            result = result[:-3] + ')'

        if len(self.expression) == 1:
            result = result[1:-1]
        result = progress + ('\n' if progress else '') + 'F = ' + result + '\n'
        print(result)

    def petrick(self):
        self.printExpression()
        while self.distributive():
            self.printExpression('After Apply (X + Y)(X + Z) = X + YZ')
        if self.multiply():
            self.printExpression('After Multiplying Out')
        if self.absorption():
            self.printExpression('After Apply X + XY = X')

        minCost = float('inf')
        (expression,) = self.expression
        EPIIndex = []
        for term in sorted(list(expression), key=lambda x: list(x)):
            cost = 0
            for r in term:
                cost += self.numInput - len(self.table[r][0]['minterm']) ** 1 / 2 + 1
            if len(term) > 1:
                cost += len(term) + 1
            print('Cost of', ''.join(map(lambda x: 'P' + str(x), sorted(list(term)))), 'is', int(cost))

            if minCost > cost:
                minCost = cost
                EPIIndex = term

        result = '\n'
        for EPI in EPIIndex:
            self.petrickResult.append(self.table[EPI][0])
            result += 'P' + str(EPI)
        print(result, 'Has Chosen\n')

    def distributive(self):
        willDelete = []
        for l, r in [(l, r) for l in range(len(self.expression)) for r in range(l + 1, len(self.expression))]:
            if l in willDelete or r in willDelete:
                continue

            for i, j in [(i, j) for i in self.expression[l] for j in self.expression[r]]:
                if i == j:
                    newTerm = {i}
                    for x, y in [(x, y) for x in self.expression[l] - {i} for y in self.expression[r] - {j}]:
                        newTerm.add(frozenset(x | y))
                    self.expression.append(newTerm)
                    willDelete.extend([l, r])
                    break

        for i in sorted(willDelete, reverse=True):
            self.expression.pop(i)

        if willDelete:
            return True
        return False

    def multiply(self):
        multiplied = False
        while len(self.expression) > 1:
            multiplied = True
            termA = self.expression.pop()
            termB = self.expression.pop()
            newTerm = set()
            for a in termA:
                for b in termB:
                    newTerm.add(frozenset(a | b))
            self.expression.append(newTerm)
        return multiplied

    def absorption(self):
        willDelete = []
        expression = list(self.expression.pop())
        for i in range(len(expression)):
            if i in willDelete:
                continue
            pivot = expression[i]
            for j in range(len(expression)):
                if i == j or j in willDelete:
                    continue
                compare = expression[j]
                if pivot.issubset(compare):
                    willDelete.append(j)

        for i in sorted(willDelete, reverse=True):
            expression.pop(i)
        self.expression.append((expression))

        if willDelete:
            return True
        return False

    def showResult(self):
        print('< Result >')
        front = 'F = '
        for EPI in self.EPI:
            term = ''
            for i, binary in enumerate(EPI['binary']):
                if binary == '-':
                    continue
                term += chr(ord('A') + i) + ('\'' if binary == '0' else '')
            front += term + ' + '

        if self.petrickResult:
            back = ''
            for EPI in self.petrickResult:
                term = ''
                for i, binary in enumerate(EPI['binary']):
                    if binary == '-':
                        continue
                    term += chr(ord('A') + i) + ('\'' if binary == '0' else '')
                back += term + ' + '
            back += '\b\b\b   '
            print(front + back)
        else:
            print(front + '\b\b\b   ')

    def verification(self):
        output = []
        for num in range(0, 2**self.numInput):
            result = False
            numToBin = bin(num)[2:].zfill(self.numInput)
            for term in self.EPI + self.petrickResult:
                for i in range(self.numInput):
                    if term['binary'][i] == '-':
                        continue
                    if term['binary'][i] != numToBin[i]:
                        break
                else:
                    result = True
                    break
            if result:
                output.append(num)

        print('\nResult Of Verification :', output)
        print('Is Minterm Covered By Result? :', set(self.minterm).issubset(set(output)))
        print('Is Result Covered By Minterm + Don\'t Care? :', set(output).issubset(set(self.minterm + self.dontcare)))

    def solve(self):
        self.findPI()
        self.makeTable()

        shrunk = True
        while shrunk:
            shrunk = False
            for func in [self.findEPI, self.rowDominance, self.colDominance]:
                if self.rows >= 2 and self.cols >= 2 and func():
                    shrunk = True

        if self.rows >= 2 and self.cols >= 2:
            self.makeExpression()
            self.petrick()

        self.showResult()
        self.verification()


if __name__ == '__main__':
    numInput = int(input('Number Of Input : '))
    minterm = list(map(int, input('Minterm : ').split()))
    dontcare = list(map(int, input('Don\'t Care : ').split()))
    print('\n')
    qm = QM(numInput, minterm, dontcare)
    qm.solve()

    # qm = QM(5, [1, 3, 4, 5, 6, 15, 16, 17, 18, 27, 30, 31], [0, 4, 11, 18, 20, 24])
    # qm = QM(3, [0, 1, 2, 5, 6, 7], [])
    # qm = QM(6, [0, 1, 2, 5, 10, 15, 17, 19, 20, 25, 26, 30, 31, 33, 41, 43, 44, 45, 48, 51, 52, 53, 54, 57, 58, 59, 62], [9, 28, 35, 40, 42, 50, 55, 56, 60])
    # qm = QM(6, [0, 2, 3, 6, 8, 11, 16, 17, 24, 26, 27, 29, 30, 31, 33, 35, 36, 38, 39, 42, 43, 44, 53, 55, 56, 57, 58, 61], [4, 18, 23, 40, 47, 59, 63])
    # qm.solve()

    # from random import randrange
    # 
    # minterm = set()
    # for _ in range(32):
    #     minterm.add(randrange(0, 64))
    # 
    # dontcare = set()
    # for _ in range(16):
    #     randInt = randrange(0, 64)
    #     if randInt not in minterm:
    #         dontcare.add(randInt)
    # qm = QM(6, sorted(list(minterm)), sorted(list(dontcare)))
    # qm.solve()
    # print('\n\nTesting Input Info')
    # print('numInpuf :', 6)
    # print('minterm :', sorted(list(minterm)))
    # print('dontcare :', sorted(list(dontcare)))
