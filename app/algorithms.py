from enum import Enum
import copy
import cell
import knowledge_base


class Action(Enum):
    TURN_LEFT = 1
    TURN_RIGHT = 2
    TURN_UP = 3
    TURN_DOWN = 4
    MOVE_FORWARD = 5
    GRAB_GOLD = 6
    PERCEIVE_BREEZE = 7
    PERCEIVE_STENCH = 8
    SHOOT = 9
    KILL_WUMPUS = 10
    KILL_NO_WUMPUS = 11
    BE_EATEN_BY_WUMPUS = 12
    FALL_INTO_PIT = 13
    KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD = 14
    CLIMB_OUT_OF_THE_CAVE = 15
    DECTECT_PIT = 16
    DETECT_WUMPUS = 17
    DETECT_NO_PIT = 18
    DETECT_NO_WUMPUS = 19
    INFER_PIT = 20
    INFER_NOT_PIT = 21
    INFER_WUMPUS = 22
    INFER_NOT_WUMPUS = 23
    DETECT_SAFE = 24
    INFER_SAFE = 25


class AgentBrain:
    def __init__(self, map_filename, output_filename):
        self.output_filename = output_filename

        self.map_size = None
        self.cell_matrix = None
        self.init_cell_matrix = None

        self.cave_cell = cell.Cell((-1, -1), 10, cell.Object.EMPTY.value)
        self.agent_cell = None
        self.init_agent_cell = None
        self.KB = knowledge_base.KnowledgeBase()
        self.path = []
        self.action_list = []
        self.score = 0

        self.read_map(map_filename)


    def read_map(self, map_filename):
        file = open(map_filename, 'r')

        self.map_size = int(file.readline())
        raw_map = [line.split('.') for line in file.read().splitlines()]

        self.cell_matrix = [[None for _ in range(self.map_size)] for _ in range(self.map_size)]
        for ir in range(self.map_size):
            for ic in range(self.map_size):
                self.cell_matrix[ir][ic] = cell.Cell((ir, ic), self.map_size, raw_map[ir][ic])
                if cell.Object.AGENT.value in raw_map[ir][ic]:
                    self.agent_cell = self.cell_matrix[ir][ic]
                    self.agent_cell.update_parent(self.cave_cell)
                    self.init_agent_cell = copy.deepcopy(self.agent_cell)

        file.close()
        self.init_cell_matrix = copy.deepcopy(self.cell_matrix)


        result, pos = self.is_valid_map()
        if not result:
            if pos is None:
                raise TypeError('Input Error: The map is invalid! There is no Agent!')
            raise TypeError('Input Error: The map is invalid! Please check at row ' + str(pos[0]) + ' and column ' + str(pos[1]) + '.')


    def is_valid_map(self):
        for cell_row in self.cell_matrix:
            for cell in cell_row:
                adj_cell_list = cell.get_adj_cell_list(self.cell_matrix)
                if cell.exist_pit():
                    for adj_cell in adj_cell_list:
                        if not adj_cell.exist_breeze():
                            return False, cell.matrix_pos
                if cell.exist_wumpus():
                    for adj_cell in adj_cell_list:
                        if not adj_cell.exist_stench():
                            return False, cell.matrix_pos
        if self.agent_cell is None:
            return False, None
        return True, None


    def append_event_to_output_file(self, text: str):
        out_file = open(self.output_filename, 'a')
        out_file.write(text + '\n')
        out_file.close()


    def add_action(self, action):
        self.action_list.append(action)
        print(action)
        self.append_event_to_output_file(action.name)

        if action == Action.TURN_LEFT:
            pass
        elif action == Action.TURN_RIGHT:
            pass
        elif action == Action.TURN_UP:
            pass
        elif action == Action.TURN_DOWN:
            pass
        elif action == Action.MOVE_FORWARD:
            self.score -= 10
            print('Score: ' + str(self.score))
            self.append_event_to_output_file('Score: ' + str(self.score))
        elif action == Action.GRAB_GOLD:
            self.score += 100
            print('Score: ' + str(self.score))
            self.append_event_to_output_file('Score: ' + str(self.score))
        elif action == Action.PERCEIVE_BREEZE:
            pass
        elif action == Action.PERCEIVE_STENCH:
            pass
        elif action == Action.SHOOT:
            self.score -= 100
            print('Score: ' + str(self.score))
            self.append_event_to_output_file('Score: ' + str(self.score))
        elif action == Action.KILL_WUMPUS:
            pass
        elif action == Action.KILL_NO_WUMPUS:
            pass
        elif action == Action.BE_EATEN_BY_WUMPUS:
            self.score -= 10000
            print('Score: ' + str(self.score))
            self.append_event_to_output_file('Score: ' + str(self.score))
        elif action == Action.FALL_INTO_PIT:
            self.score -= 10000
            print('Score: ' + str(self.score))
            self.append_event_to_output_file('Score: ' + str(self.score))
        elif action == Action.KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD:
            pass
        elif action == Action.CLIMB_OUT_OF_THE_CAVE:
            self.score += 10
            print('Score: ' + str(self.score))
            self.append_event_to_output_file('Score: ' + str(self.score))
        elif action == Action.DECTECT_PIT:
            pass
        elif action == Action.DETECT_WUMPUS:
            pass
        elif action == Action.DETECT_NO_PIT:
            pass
        elif action == Action.DETECT_NO_WUMPUS:
            pass
        elif action == Action.INFER_PIT:
            pass
        elif action == Action.INFER_NOT_PIT:
            pass
        elif action == Action.INFER_WUMPUS:
            pass
        elif action == Action.INFER_NOT_WUMPUS:
            pass
        elif action == Action.DETECT_SAFE:
            pass
        elif action == Action.INFER_SAFE:
            pass
        else:
            raise TypeError("Error: " + self.add_action.__name__)


    def add_new_percepts_to_KB(self, cell_instance):
        adj_cell_list = cell_instance.get_adj_cell_list(self.cell_matrix)

       
        sign = '-'
        if cell_instance.exist_pit():
            sign = '+'
            self.KB.add_clause([cell_instance.get_literal(cell.Object.WUMPUS, '-')])
        self.KB.add_clause([cell_instance.get_literal(cell.Object.PIT, sign)])
        sign_pit = sign

        
        sign = '-'
        if cell_instance.exist_wumpus():
            sign = '+'
            self.KB.add_clause([cell_instance.get_literal(cell.Object.PIT, '-')])
        self.KB.add_clause([cell_instance.get_literal(cell.Object.WUMPUS, sign)])
        sign_wumpus = sign

  
        if sign_pit == sign_wumpus == '+':
            raise TypeError('Logic Error: Pit and Wumpus can not appear at the same cell.')

     
        sign = '-'
        if cell_instance.exist_breeze():
            sign = '+'
        self.KB.add_clause([cell_instance.get_literal(cell.Object.BREEZE, sign)])


        sign = '-'
        if cell_instance.exist_stench():
            sign = '+'
        self.KB.add_clause([cell_instance.get_literal(cell.Object.STENCH, sign)])

        
        if cell_instance.exist_breeze():
            
            clause = [cell_instance.get_literal(cell.Object.BREEZE, '-')]
            for adj_cell in adj_cell_list:
                clause.append(adj_cell.get_literal(cell.Object.PIT, '+'))
            self.KB.add_clause(clause)

          
            for adj_cell in adj_cell_list:
                clause = [cell_instance.get_literal(cell.Object.BREEZE, '+'),
                          adj_cell.get_literal(cell.Object.PIT, '-')]
                self.KB.add_clause(clause)

        
        else:
            for adj_cell in adj_cell_list:
                clause = [adj_cell.get_literal(cell.Object.PIT, '-')]
                self.KB.add_clause(clause)

        
        if cell_instance.exist_stench():
           
            clause = [cell_instance.get_literal(cell.Object.STENCH, '-')]
            for adj_cell in adj_cell_list:
                clause.append(adj_cell.get_literal(cell.Object.WUMPUS, '+'))
            self.KB.add_clause(clause)

            for adj_cell in adj_cell_list:
                clause = [cell_instance.get_literal(cell.Object.STENCH, '+'),
                          adj_cell.get_literal(cell.Object.WUMPUS, '-')]
                self.KB.add_clause(clause)

  
        else:
            for adj_cell in adj_cell_list:
                clause = [adj_cell.get_literal(cell.Object.WUMPUS, '-')]
                self.KB.add_clause(clause)

        print(self.KB.KB)
        self.append_event_to_output_file(str(self.KB.KB))


    def turn_to(self, next_cell):
        if next_cell.map_pos[0] == self.agent_cell.map_pos[0]:
            if next_cell.map_pos[1] - self.agent_cell.map_pos[1] == 1:
                self.add_action(Action.TURN_UP)
            else:
                self.add_action(Action.TURN_DOWN)
        elif next_cell.map_pos[1] == self.agent_cell.map_pos[1]:
            if next_cell.map_pos[0] - self.agent_cell.map_pos[0] == 1:
                self.add_action(Action.TURN_RIGHT)
            else:
                self.add_action(Action.TURN_LEFT)
        else:
            raise TypeError('Error: ' + self.turn_to.__name__)


    def move_to(self, next_cell):
        self.turn_to(next_cell)
        self.add_action(Action.MOVE_FORWARD)
        self.agent_cell = next_cell


    def backtracking_search(self):
       
        if self.agent_cell.exist_pit():
            self.add_action(Action.FALL_INTO_PIT)
            return False

        
        if self.agent_cell.exist_wumpus():
            self.add_action(Action.BE_EATEN_BY_WUMPUS)
            return False

  
        if self.agent_cell.exist_gold():
            self.add_action(Action.GRAB_GOLD)
            self.agent_cell.grab_gold()

        if self.agent_cell.exist_breeze():
            self.add_action(Action.PERCEIVE_BREEZE)

       
        if self.agent_cell.exist_stench():
            self.add_action(Action.PERCEIVE_STENCH)

       
            self.agent_cell.explore()
            self.add_new_percepts_to_KB(self.agent_cell)

      
        valid_adj_cell_list = self.agent_cell.get_adj_cell_list(self.cell_matrix)

        temp_adj_cell_list = []
        if self.agent_cell.parent in valid_adj_cell_list:
            valid_adj_cell_list.remove(self.agent_cell.parent)

       
        pre_agent_cell = self.agent_cell

       
        if not self.agent_cell.is_OK():
           
            temp_adj_cell_list = []
            for valid_adj_cell in valid_adj_cell_list:
                if valid_adj_cell.is_explored() and valid_adj_cell.exist_pit():
                    temp_adj_cell_list.append(valid_adj_cell)
            for adj_cell in temp_adj_cell_list:
                valid_adj_cell_list.remove(adj_cell)

            temp_adj_cell_list = []

        
            if self.agent_cell.exist_stench():
                valid_adj_cell: cell.Cell
                for valid_adj_cell in valid_adj_cell_list:
                    print("Infer: ", end='')
                    print(valid_adj_cell.map_pos)
                    self.append_event_to_output_file('Infer: ' + str(valid_adj_cell.map_pos))
                    self.turn_to(valid_adj_cell)

                    
                    self.add_action(Action.INFER_WUMPUS)
                    not_alpha = [[valid_adj_cell.get_literal(cell.Object.WUMPUS, '-')]]
                    have_wumpus = self.KB.infer(not_alpha)

             
                    if have_wumpus:
                        
                        self.add_action(Action.DETECT_WUMPUS)

                     
                        self.add_action(Action.SHOOT)
                        self.add_action(Action.KILL_WUMPUS)
                        valid_adj_cell.kill_wumpus(self.cell_matrix, self.KB)
                        self.append_event_to_output_file('KB: ' + str(self.KB.KB))

                
                    else:
                        
                        self.add_action(Action.INFER_NOT_WUMPUS)
                        not_alpha = [[valid_adj_cell.get_literal(cell.Object.WUMPUS, '+')]]
                        have_no_wumpus = self.KB.infer(not_alpha)

                 
                        if have_no_wumpus:
                      
                            self.add_action(Action.DETECT_NO_WUMPUS)

                        else:
                    
                            if valid_adj_cell not in temp_adj_cell_list:
                                temp_adj_cell_list.append(valid_adj_cell)


   
            if self.agent_cell.exist_stench():
                adj_cell_list = self.agent_cell.get_adj_cell_list(self.cell_matrix)
                if self.agent_cell.parent in adj_cell_list:
                    adj_cell_list.remove(self.agent_cell.parent)

                explored_cell_list = []
                for adj_cell in adj_cell_list:
                    if adj_cell.is_explored():
                        explored_cell_list.append(adj_cell)
                for explored_cell in explored_cell_list:
                    adj_cell_list.remove(explored_cell)

                for adj_cell in adj_cell_list:
                    print("Try: ", end='')
                    print(adj_cell.map_pos)
                    self.append_event_to_output_file('Try: ' + str(adj_cell.map_pos))
                    self.turn_to(adj_cell)

                    self.add_action(Action.SHOOT)
                    if adj_cell.exist_wumpus():
                        self.add_action(Action.KILL_WUMPUS)
                        adj_cell.kill_wumpus(self.cell_matrix, self.KB)
                        self.append_event_to_output_file('KB: ' + str(self.KB.KB))

                    if not self.agent_cell.exist_stench():
                        self.agent_cell.update_child_list([adj_cell])
                        break


          
            if self.agent_cell.exist_breeze():
                valid_adj_cell: cell.Cell
                for valid_adj_cell in valid_adj_cell_list:
                    print("Infer: ", end='')
                    print(valid_adj_cell.map_pos)
                    self.append_event_to_output_file('Infer: ' + str(valid_adj_cell.map_pos))
                    self.turn_to(valid_adj_cell)

             
                    self.add_action(Action.INFER_PIT)
                    not_alpha = [[valid_adj_cell.get_literal(cell.Object.PIT, '-')]]
                    have_pit = self.KB.infer(not_alpha)

                    if have_pit:
                      
                        self.add_action(Action.DECTECT_PIT)

                   
                        valid_adj_cell.explore()

                        self.add_new_percepts_to_KB(valid_adj_cell)

                        valid_adj_cell.update_parent(valid_adj_cell)

                        temp_adj_cell_list.append(valid_adj_cell)


                    else:
                      
                        self.add_action(Action.INFER_NOT_PIT)
                        not_alpha = [[valid_adj_cell.get_literal(cell.Object.PIT, '+')]]
                        have_no_pit = self.KB.infer(not_alpha)

                       
                        if have_no_pit:
                          
                            self.add_action(Action.DETECT_NO_PIT)

               
                        else:
                         
                            temp_adj_cell_list.append(valid_adj_cell)

        temp_adj_cell_list = list(set(temp_adj_cell_list))

        for adj_cell in temp_adj_cell_list:
            valid_adj_cell_list.remove(adj_cell)
        self.agent_cell.update_child_list(valid_adj_cell_list)


        for next_cell in self.agent_cell.child_list:
            self.move_to(next_cell)
            print("Move to: ", end='')
            print(self.agent_cell.map_pos)
            self.append_event_to_output_file('Move to: ' + str(self.agent_cell.map_pos))

            if not self.backtracking_search():
                return False

            self.move_to(pre_agent_cell)
            print("Backtrack: ", end='')
            print(pre_agent_cell.map_pos)
            self.append_event_to_output_file('Backtrack: ' + str(pre_agent_cell.map_pos))

        return True


    def solve_wumpus_world(self):
 
        out_file = open(self.output_filename, 'w')
        out_file.close()

        self.backtracking_search()

        victory_flag = True
        for cell_row in self.cell_matrix:
            for cell in cell_row:
                if cell.exist_gold() or cell.exist_wumpus():
                    victory_flag = False
                    break
        if victory_flag:
            self.add_action(Action.KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD)

        if self.agent_cell.parent == self.cave_cell:
            self.add_action(Action.CLIMB_OUT_OF_THE_CAVE)

        return self.action_list, self.init_agent_cell, self.init_cell_matrix