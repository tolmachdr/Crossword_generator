import random
import os

POPULATION_SIZE = 100


class Pair:
    """
    Class pair have key and the list for this key
    """

    def __init__(self):
        self.key = ""
        self.list = set()

    def __lt__(self, other):
        if len(self.list) > len(other.list):
            return True
        return False

    def print(self):
        print(f'{self.key} list {self.list}')


def create_grid():
    """
    This function creates default grid 20*20
    :return: grid
    """
    grid = [['.' for _ in range(20)] for _ in range(20)]
    return grid


def add_random(grid, word):
    """
    This function randomly add word in grid
    :param grid: crossword grid
    :param word: word that should be added
    :return: grid with this word
    """
    rows = 20
    cols = 20
    word_length = len(word)
    horizontal_placement = random.choice([True, False])
    if horizontal_placement:
        row = random.randint(0, rows - 1)
        col = random.randint(0, cols - word_length)
        grid[row][col:col + word_length] = list(word)
    else:
        col = random.randint(0, cols - 1)
        row = random.randint(0, rows - word_length)
        for j in range(word_length):
            grid[row + j][col] = word[j]


class Individual:
    """
    Class individual - crossword
    """

    def __init__(self, grid, words):
        self.grid = grid
        self.words = words
        self.intersections = self.pairs()
        self.position = self.positions()
        self.count = self.calculate_intersections()
        self.fit = len(self.words) - self.count + self.position

    def pairs(self):
        """
        This function create list of pairs for crossword, where I will save all words as a keys
        and in their lists will be saved all words that intersect with them
        :return: list with pair for all words
        """
        intersections = []
        for word in self.words:
            pair = Pair()
            pair.key = word
            intersections.append(pair)
        return intersections

    def positions(self):
        """
        This function find all mistakes in crossword (wrong positions) and intersections
        :return: all mistakes in crossword (wrong positions)
        """
        position = 0
        for i in range(20):
            string = ''.join(self.grid[i][:])
            index, word = find_word(string, self.words)
            if len(index) != 0:
                for j in range(len(index)):
                    if index[j] != 0:
                        if self.grid[i][index[j] - 1] != '.':
                            position += 1
                    if index[j] + len(word[j]) != 20:
                        if self.grid[i][index[j] + len(word[j])] != '.':
                            position += 1
                    for k in range(index[j], index[j] + len(word[j])):
                        string = self.get_column(k)
                        index_vertical, word_vertical = find_word(string, self.words)
                        check = True
                        if len(index_vertical) != 0:
                            for ind in range(len(index_vertical)):
                                if i in range(index_vertical[ind], index_vertical[ind] + len(word_vertical[ind])):
                                    self.intersections[self.words.index(word[j])].list.add(word_vertical[ind])
                                    check = False
                        if check:
                            if i > 0 and self.grid[i - 1][k] != '.':
                                position += 1
                            if i < 19 and self.grid[i + 1][k] != '.':
                                position += 1
            string = self.get_column(i)
            index, word = find_word(string, self.words)
            if len(index) != 0:
                for j in range(len(index)):
                    if index[j] != 0:
                        if self.grid[index[j] - 1][i] != '.':
                            position += 1
                    if index[j] + len(word[j]) != 20:
                        if self.grid[index[j] + len(word[j])][i] != '.':
                            position += 1
                    for k in range(index[j], index[j] + len(word[j])):
                        string = ''.join(self.grid[k][:])
                        index_horiz, word_horiz = find_word(string, self.words)
                        check = True
                        if len(index_horiz) != 0:
                            for ind in range(len(index_horiz)):
                                if i in range(index_horiz[ind], index_horiz[ind] + len(word_horiz[ind])):
                                    self.intersections[self.words.index(word[j])].list.add(word_horiz[ind])
                                    check = False
                        if check:
                            if i > 0 and self.grid[k][i - 1] != '.':
                                position += 1
                            if i < 19 and self.grid[k][i + 1] != '.':
                                position += 1
        return position

    def calculate_intersections(self):
        """
        :return:  the max number of interconnected crossed words
        """
        self.intersections.sort()
        pair = self.intersections[0]
        closed_list = []
        can_visit = [pair.key]
        for word in list(pair.list):
            can_visit.append(word)

        while len(can_visit) != 0:
            word = can_visit.pop()
            if word in closed_list:
                continue

            closed_list.append(word)
            pair = self.get_pair(word)
            for word in list(pair.list):
                can_visit.append(word)

        return len(closed_list)

    def mate(self, partner):
        """
        This function create new Individual - crossword based on two others
        :param partner: second parent for new crossword
        :return: child - new crossword
        """
        grid = create_grid()
        not_added = self.words.copy()
        while len(not_added) != 0:
            word = random.choice(not_added)
            parent = random.choice([0, 1, 2])
            if parent == 0:
                for i in range(20):
                    index = ''.join(self.grid[i][:]).find(word)
                    if index != -1:
                        grid[i][index:index + len(word)] = word
                        not_added.remove(word)
                        break
                    index = self.get_column(i).find(word)
                    if index != -1:
                        for j in range(index, index + len(word)):
                            grid[j][i] = self.grid[j][i]
                        not_added.remove(word)
                        break
            elif parent == 1:
                for i in range(20):
                    index = ''.join(partner.grid[i][:]).find(word)
                    if index != -1:
                        grid[i][index:index + len(word)] = word
                        not_added.remove(word)
                        break
                    index = partner.get_column(i).find(word)
                    if index != -1:
                        for j in range(index, index + len(word)):
                            grid[j][i] = partner.grid[j][i]
                        not_added.remove(word)
                        break
            else:
                add_random(grid, word)
                not_added.remove(word)
        child = Individual(grid, self.words)
        word = random.choice(self.words)
        grid = child.mutate(word)
        individual = Individual(grid, self.words)
        return individual

    def mutate(self, word):
        """
        In this function mutation happens
        Given word should be moved in another position
        :param word: word to move
        :return: mutated grid - for new crossword
        """
        grid = create_grid()
        for w in self.words:
            if w != word:
                for i in range(20):
                    index = ''.join(self.grid[i][:]).find(w)
                    if index != -1:
                        grid[i][index: index + len(w)] = self.grid[i][index: index + len(w)]
                        break
                    index = self.get_column(i).find(w)
                    if index != -1:
                        for j in range(index, len(w) + index):
                            grid[j][i] = self.grid[j][i]
                        break

        add_random(grid, word)
        return grid

    def get_pair(self, word):
        """
        :param word: this word should be found in list of intersections
        :return: this word and list of words that intersected with it
        """
        for pair in self.intersections:
            if pair.key == word:
                return pair

    def get_column(self, col):
        """
        :param col: the column of grid
        :return: column as a string
        """
        string = ""
        for row in self.grid:
            string += row[col]
        return string

    def __lt__(self, other):
        """
        :param other: crossword with which we should to compare this one
        :return: Whoever has less fitness has less crossword
        """
        return self.fit < other.fit


def find_word(string, words):
    """
    :param string: String in which we are looking for any words
    :param words: the list of words that can be found
    :return: list of found words and index where they were found
    """
    index = []
    finding = []
    for word in words:
        if string.find(word) != -1:
            index.append(string.find(word))
            finding.append(word)
    # May happen that some words have common root, so we need to check
    # that we did not find several words in one
    if len(finding) > 0:
        for i in range(len(finding) - 1):
            if finding[i + 1].find(finding[i]) != -1:
                finding.remove(finding[i])
                index.remove(index[i])
                break
            if finding[i].find(finding[i + 1]) != -1:
                finding.remove(finding[i + 1])
                index.remove(index[i])
                break

    return index, finding


def create_individual(words, grid):
    """
    :param words: list of words that should be used to construct a crossword
    :param grid: the field 20 * 20
    :return: words-filled grid for crossword
    """
    rows = 20
    cols = 20
    add = words.copy()

    while (len(add)) != 0:
        word = random.choice(add)
        add.remove(word)
        word_length = len(word)
        horizontal_placement = random.choice([True, False])
        if horizontal_placement:
            row = random.randint(0, rows - 1)
            col = random.randint(0, cols - word_length)
            grid[row][col:col + word_length] = list(word)
        else:
            col = random.randint(0, cols - 1)
            row = random.randint(0, rows - word_length)
            for j in range(word_length):
                grid[row + j][col] = word[j]
    return grid


def print_positions(individual, words, file):
    """
    :param individual: crossword
    :param words: list of given words, that should be in crossword
    :param file: file where we should print words position
    """
    for word in words:
        for i in range(20):
            index = ''.join(individual.grid[i][:]).find(word)
            if index != -1:
                file.write(f'{i} {index} {0}\n')
                break
            index = individual.get_column(i).find(word)
            if index != -1:
                file.write(f'{index} {i} {1}\n')
                break


def main():
    """
    In the main function I have Genetic Algorithm
    1. Creates a field 20 * 20 where randomly distributed words from the list, such crossword are formed 100
    (population size), they are all recorded in the list individuals
    2. list with crosswords sorted by crossword fitness
    3. I check whether there is a crossword in the individuals, which satisfies the conditions
    for the solution (all words are crossed and stand correctly, ie fitness is 0)
    4. If no solution is found, I add the top 10% to the new generation and generate children from parents
    who are chosen randomly from the top 15 from the last generation and mutate them
    5. Sort the new generation also by fitness and mutate it
    6. I go back to step 2 until I find the correct crossword puzzle
    """
    global POPULATION_SIZE
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    input_file = "inputs\input3.txt"
    num = 3
    while os.path.isfile(input_file):
        words = []
        with open(input_file, 'r') as file:
            while True:
                word = file.readline().strip()
                if not word:
                    break
                words.append(word)

        individuals = []
        found = False

        for i in range(POPULATION_SIZE):
            grid = create_grid()
            ind_grid = create_individual(words, grid)
            individual = Individual(ind_grid, words)
            individuals.append(individual)

        while not found:
            individuals.sort()

            if individuals[0].count == len(words) and individuals[0].position == 0:
                output_file = "outputs\output"
                output_file += num.__str__()
                output_file += ".txt"
                with open(output_file, 'w') as file:
                    for row in individuals[0].grid:
                        print(''.join(row))
                    print_positions(individuals[0], words, file)
                break

            new_generation = []

            s = int((10 * POPULATION_SIZE) / 100)
            new_generation.extend(individuals[:s])

            s = int((90 * POPULATION_SIZE) / 100)
            for _ in range(s):
                parent1 = random.choice(individuals[:15])
                parent2 = random.choice(individuals[:15])
                child = parent1.mate(parent2)
                new_generation.append(child)

            new_generation.sort()
            for individual in new_generation:
                word = random.choice(words)
                grid = individual.mutate(word)
                child = Individual(grid, words)
                if child.fit <= individual.fit:
                    individual.__init__(grid, words)

            individuals = new_generation
        input_file = "inputs\input"
        num += 1
        input_file += num.__str__()
        input_file += ".txt"


if __name__ == '__main__':
    main()
