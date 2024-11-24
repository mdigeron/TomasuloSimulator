# https://github.com/bubblecounter/Tomasulo-Algorithm/blob/main/main.py
# https://github.com/Zhannator/TomasuloAlgorithm
# ADD DESCRIPTIVE COMMENTS
# play around with different amounts of registers and calculate the utilization and plot results then optimize
# write output to a file to 
class Instruction: 
    def __init__(self, opcode, destination, operand1, operand2, next=None, issued_cycle=0, execute_start_cycle=0, execute_end_cycle=0, write_back_cycle=0): # possibly refactor into breaking up after passing i.e. instruction[0]...
        self.opcode = opcode
        self.destination = destination
        self.operand1 = operand1
        self.operand2 = operand2
        self.next = next
        self.issued_cycle = issued_cycle
        self.execute_start_cycle = execute_start_cycle
        self.execute_end_cycle = execute_end_cycle
        self.write_back_cycle = write_back_cycle
        self.issue_delay = True # stall a cycle to prevent executing same cycle as issue

    def __str__(self):
        return (f"{self.opcode} {self.destination.get_name()} {self.operand1.get_name()} {self.operand2.get_name()} | Cycle Issued: {self.issued_cycle} | Cycle Start Execute: {self.execute_start_cycle} | Cycle End Execute: {self.execute_end_cycle} | Cycle Write Back: {self.write_back_cycle}")

    def get_opcode(self):
        return self.opcode

    def get_destination(self):
        return self.destination

    def get_operand1(self):
        return self.operand1

    def get_operand2(self): 
        return self.operand2

    def get_issued_cycle(self):
        return self.issued_cycle
        
    def get_execute_start_cycle(self):
        return self.execute_start_cycle
        
    def get_execute_end_cycle(self):
        return self.execute_end_cycle
        
    def get_write_back_cycle(self):
        return self.write_back_cycle
        
    def set_issued_cycle(self, clock_cycle):
        self.issued_cycle = clock_cycle

    def set_execute_start_cycle(self, clock_cycle):
        self.execute_start_cycle = clock_cycle

    def set_execute_end_cycle(self, clock_cycle):
        self.execute_end_cycle = clock_cycle

    def set_write_back_cycle(self, clock_cycle):
        self.write_back_cycle = clock_cycle

    def set_issue_delay(self, boolean):
        self.issue_delay = boolean

############################################################################
# Class: InstructionQueue
#
# This class creates and removes instructions through the enqueue/dequeue
# operations specified in the InstructionQueue public interface.
#
# Underlying Implmentation:
#   Singly Linked List
#
#   Note: The nodes are the instructions themselves,
#         and each one holds a pointer to the next instruction.
#
# Private Data Members:
#     Instruction * head - pointer to the first instruction in the queue.
#                          head = None when the queue is empty.
#
#     Instruction * tail - pointer to the last instruction in the queue.
#                          tail = None when the queue is empty.
#
#     int length - count of instructions currently in the queue.
#                  length = 0 when the queue is empty.
#
#     Instruction * pseudo_head - represents the virtual start of the
#                                 queue, so that previous instructions are
#                                 still accessible for execution history.
#
# Public Interface/Methods:
#
# __init__, __str__, is_empty, get_length, enqueue, dequeue, soft_dequeue
#
############################################################################
class InstructionQueue: 
    def __init__(self):
        self.head = None 
        self.tail = None
        self.length = 0
        self.pseudo_head = None

    ###########################################################
    # InstructionQueue State/Status Methods
    #
    # is_empty(self) - returns true if there are no active
    #                  instructions avaiable for execution.
    #
    # get_length(self) - returns current number of active
    #                    instructions in the queue
    #                    that are avaiable for execution.
    #
    ###########################################################
    def is_empty(self):
        return self.length == 0

    def get_length(self):
        return self.length

    ###########################################################
    #
    # Method: enqueue
    #
    # Creates a new Instruction and inserts it at the end of
    # the queue or at the head of the queue when the
    # InstructionQueue is empty.
    #
    # Parameters:
    #     InstructionQueue * self
    #     string   opcode
    #     Register destination
    #     Register operand1
    #     Register operand2
    #
    # Returns: Does not return anything.
    #
    ###########################################################
    def enqueue(self, opcode, destination, operand1, operand2):
        new_instruction = Instruction(opcode, destination, operand1, operand2)
        
        if self.tail is not None:
            self.tail.next = new_instruction
            
        self.tail = new_instruction
        
        if self.head is None:
            self.head = new_instruction
            self.pseudo_head = new_instruction
            
        self.length += 1

    def dequeue(self): 
        if self.is_empty():
            return "Instruction queue is empty"
        
        instruction = self.head
        self.head = self.head.next
        
        if self.head is None:
            self.tail = None
            
        self.length -= 1
        
        return instruction

    ###########################################################
    #
    # Method: soft_dequeue
    #
    # Performs a "soft" deletion of an instruction from the
    # queue. A virtual head of the list is moved forward in the
    # list on each call of `soft_dequeue`, and it points to the
    # first instruction avaiable for execution in the queue.
    # Instructions that still exist before the virtual list head
    # are kept for historical information, and can only be
    # removed by the `dequeue` operation.
    #
    # Parameters:
    #     InstructionQueue * self
    #
    # Returns: Does not return anything.
    #
    ###########################################################
    def soft_dequeue(self): 
        if self.is_empty():
            return "Instruction queue is empty"
        
        instruction = self.pseudo_head
        self.pseudo_head = instruction.next
        self.length -= 1 # length also needs to be controlled by soft_dequeue to mimic dequeue even though its not accurate
        
        return instruction
    
    def __str__(self):
        instructions = "" 
        current = self.head
        while current:
            #instruction = []
            """
            instruction.append(current.opcode)
            instruction.append(current.destination.get_name())
            instruction.append(current.operand1.get_name())
            instruction.append(current.operand2.get_name())
            instructions.append(instruction)
            """
            #instructions += current.opcode + " | "
            #              + current.destination.get_name() + " | "
            #              + current.operand1.get_name() + " | "
            #              + current.operand2.get_name() + " | "
            #              + str(current.get_issued_cycle()) + " | "
            #              + str(current.get_execute_start_cycle()) + " | "
            #              + str(current.get_execute_end_cycle()) + " | "
            #              + str(current.get_write_back_cycle()) + "\n"
            instructions += str(current) + "\n"
            current = current.next
        return instructions

class ReservationStation:
    def __init__(self, name, time=None, op=None, vj=None, vk=None, qj=None, qk=None, busy=False, source=None, instruction_pointer=None):
        self.name = name
        self.time = time
        self.op = op
        self.vj = vj
        self.vk = vk
        self.qj = qj
        self.qk = qk
        self.source = source
        self.source_buffer = None
        self.busy = busy
        self.busy_cycles = 0 # update while waiting/executing
        self.executing_cycles = 0 # only update while executing
        self.busy_fraction = 0
        self.executing_fraction = 0
        self.instruction_pointer = instruction_pointer # points to instruction in order to modify its start/end execution cycle and write back cycle

    def get_time(self):
        return self.time

    def set_time(self, time):
        self.time = time

    def get_name(self):
        return self.name

    def get_busy_status(self):
        return self.busy

    def get_op(self):
        return self.op

    def get_vj(self): 
        return self.vj

    def get_vk(self):
        return self.vk

    def get_qj(self):
        return self.qj

    def get_qk(self):
        return self.qk

    def get_source(self):
        return self.source

    def get_source_buffer(self):
        return self.source_buffer

    def get_instruction_pointer(self):
        return self.instruction_pointer
    
    def set_op(self, op):
        self.op = op

    def set_vj(self, vj):
        self.vj = vj

    def set_vk(self, vk):
        self.vk = vk

    def set_qj(self, qj):
        self.qj = qj

    def set_qk(self, qk):
        self.qk = qk

    def set_source(self, source):
        self.source = source

    def set_source_buffer(self, source):
        self.source_buffer = source

    def is_ready(self):
        return self.time == 0

    def set_busy_status(self, status):
        self.busy = status

    def set_instruction_pointer(self, instruction):
        self.instruction_pointer = instruction

    def __str__(self):
        return (f"Clock Cycles Remaining: {self.time} | Name: {self.name} | Busy: {self.busy} | Op: {self.op} | Source: {self.get_source().get_name() if self.get_source() != None else None} | Source Buffer: {self.get_source_buffer().get_name() if self.get_source_buffer() != None else None} | Vj: {self.vj.get_name()  if self.vj != None else None} | Vk: {self.vk.get_name() if self.vk != None else None} | Qj: {self.qj.get_name() if self.qj != None else None} | Qk: {self.qk.get_name() if self.qk != None else None}")

class LoadBuffer:
    def __init__(self, name, time=None, vj=None, qj=None, address=None, busy=False, instruction_pointer=None):
        self.name = name
        self.address = address
        self.op = None
        self.source = None
        self.source_buffer = None
        self.busy = busy
        self.time = time
        self.vj = vj
        self.qj = qj
        self.busy_cycles = 0
        self.executing_cycles = 0
        self.busy_fraction = 0
        self.executing_fraction = 0
        self.instruction_pointer = instruction_pointer # points to instruction in order to modify its start/end execution cycle and write back cycle

    def get_name(self):
        return self.name

    def get_busy_status(self):
        return self.busy

    def get_address(self):
        return self.address

    def get_op(self):
        return self.op

    def get_time(self):
        return self.time

    def get_vj(self):
        return self.vj

    def get_qj(self):
        return self.qj

    def get_source(self):
        return self.source

    def get_source_buffer(self):
        return self.source_buffer

    def get_instruction_pointer(self):
        return self.instruction_pointer

    def set_time(self, time):
        self.time = time

    def set_address(self, address):
        self.address = address

    def set_op(self, opcode):
        self.op = opcode

    def set_vj(self, vj):
        self.vj = vj

    def set_qj(self, qj):
        self.qj = qj

    def set_busy_status(self, status):
        self.busy = status

    def set_source(self, source):
        self.source = source

    def set_source_buffer(self, source):
        self.source_buffer = source

    def set_instruction_pointer(self, instruction):
        self.instruction_pointer = instruction

    def __str__(self):
        return (f"Clock Cycles Remaining: {self.time} | Name: {self.name} | Busy: {self.busy} | Op: {self.op} | Source: {self.get_source().get_name() if self.get_source() != None else None} | Source Buffer: {self.get_source_buffer().get_name() if self.get_source_buffer() != None else None} | Address: {self.address}")
        

class Register:
    def __init__(self, name, value=None, buffer=None):
        self.name = name
        self.value = value
        self.buffer = buffer # should be a reservation station/ load buffer
        self.write_back = True

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_buffer(self):
        return self.buffer

    def get_write_back(self):
        return self.write_back

    def set_value(self, value):
        self.value = value

    def set_buffer(self, buffer):
        self.buffer = buffer

    def set_write_back(self, boolean):
        self.write_back = boolean

    def __str__(self):
        return(f"Register: {self.name} | Value: {self.value} | Buffer Station: {self.buffer.get_name() if self.buffer != None else None}")

class Tomasulo:
    def __init__(self, instruction_queue, num_fp_add, num_fp_mult, num_loadstore, registers, opcodes, dispatch_size):
        self.instruction_queue = instruction_queue
        self.num_fp_add = num_fp_add
        self.num_fp_mult = num_fp_mult
        self.num_loadstore = num_loadstore
        self.dispatch_size = dispatch_size
        self.fp_adders = {}
        self.fp_multipliers = {}
        self.loadbuffers = {}
        self.registers = registers
        self.instruction_latency = {}
        self.dispatch_size = int(dispatch_size)
        for esh in range(self.num_fp_add):
            self.fp_adders["ADD" + str(esh + 1)] = ReservationStation("ADD" + str(esh + 1))
        for esh in range(self.num_fp_mult):
            self.fp_multipliers["MULT" + str(esh + 1)] = ReservationStation("MULT" + str(esh + 1))
        for esh in range(self.num_loadstore):
            self.loadbuffers["LOAD/STORE" + str(esh + 1)] = LoadBuffer("LOAD/STORE" + str(esh + 1))
        self.clock_cycle = 0
        for opcode in opcodes:
            latency = None
            while type(latency) != type(1):
                latency = int(input("Enter latency for " + opcode + ":"))
            self.instruction_latency[opcode] = latency
        self.output = []
        
    def increment_clock_cycle(self):
        self.clock_cycle += 1

    def get_clock_cycle(self):
        return self.clock_cycle

    def display_adders(self):
        for name, rs in self.fp_adders.items():
            print("Reservation Station: " + name + " ", rs,  " Busy Utilization: " + str(rs.busy_fraction) + " | Execution Utilization: " + str(rs.executing_fraction))

    def display_multipliers(self):
        for name, rs in self.fp_multipliers.items():
            print("Reservation Station: " + name + " ", rs, " Busy Utilization: " + str(rs.busy_fraction) + " | Execution Utilization: " + str(rs.executing_fraction))

    def display_loadbuffers(self):
        for name, lb in self.loadbuffers.items():
            print("Load/Store Buffer: " + name + " ", lb, " Busy Utilization: " + str(lb.busy_fraction) + " | Execution Utilization: " + str(lb.executing_fraction))

    def display_registers(self):
        for register in self.registers.values():
            print(register)

    def return_adders_string(self):
        output = ""
        for name, rs in self.fp_adders.items():
            output += str("Reservation Station: " + name + " " + str(rs) +  " Busy Utilization: " + str(rs.busy_fraction) + " | Execution Utilization: " + str(rs.executing_fraction))
            output += "\n"
        return output

    def return_multipliers_string(self):
        output = ""
        for name, rs in self.fp_multipliers.items():
            output += str("Reservation Station: " + name + " " + str(rs) +  " Busy Utilization: " + str(rs.busy_fraction) + " | Execution Utilization: " + str(rs.executing_fraction))
            output += "\n"
        return output

    def return_loadbuffers_string(self):
        output = ""
        for name, lb in self.loadbuffers.items():
            output += str("Load/Store Buffer: " + name + " " + str(lb) + " Busy Utilization: " + str(lb.busy_fraction) + " | Execution Utilization: " + str(lb.executing_fraction))
            output += "\n"
        return output

    def return_registers_string(self):
        output = ""
        for register in self.registers.values():
            output += str(register)
            output += "\n"
        return output


    def issue_instruction(self, instruction):
        issued = False
        opcode = instruction.get_opcode()
        destination = instruction.get_destination()
        operand1 = instruction.get_operand1()
        operand2 = instruction.get_operand2()
        registers = self.buffer_registers()
        if opcode == "ADDD" or opcode == "SUBD":
            for rs in self.fp_adders.values():
                if rs.get_busy_status() == False and issued == False and destination.get_name() not in registers and operand1.get_name() not in registers and operand2.get_name() not in registers:
                    print("Avaliable Reservation Station " + rs.get_name())
                    rs.set_op(opcode)
                    rs.set_time(self.instruction_latency[opcode])
                    if operand1.get_buffer() != None:
                        rs.set_qj(operand1)
                    else:
                        rs.set_vj(operand1)
                        self.registers[operand1.get_name()].set_buffer(rs)
                    if operand2.get_buffer() != None:
                        rs.set_qk(operand2)
                    else:
                        rs.set_vk(operand2)
                        self.registers[operand2.get_name()].set_buffer(rs)
                    if destination.get_buffer() != None:
                        rs.set_source_buffer(destination)
                    else:
                        rs.set_source(destination)
                        self.registers[destination.get_name()].set_buffer(rs)
                    rs.set_busy_status(True)
                    rs.set_instruction_pointer(instruction)
                    rs.instruction_pointer.set_issued_cycle(self.clock_cycle)
                    issued = True
                    print("Issued: ", instruction)
        elif opcode == "MULTD" or opcode == "DIVD":
            for rs in self.fp_multipliers.values():
                if rs.get_busy_status() == False and issued == False and destination.get_name() not in registers and operand1.get_name() not in registers and operand2.get_name() not in registers:
                    print("Avaliable Reservation Station " + rs.get_name())
                    rs.set_op(opcode)
                    rs.set_time(self.instruction_latency[opcode])
                    if operand1.get_buffer() != None:
                        rs.set_qj(operand1)
                    else:
                        rs.set_vj(operand1)
                        self.registers[operand1.get_name()].set_buffer(rs)
                    if operand2.get_buffer() != None:
                        rs.set_qk(operand2)
                    else:
                        rs.set_vk(operand2)
                        self.registers[operand2.get_name()].set_buffer(rs)
                    if destination.get_buffer() != None:
                        rs.set_source_buffer(destination)
                    else:
                        rs.set_source(destination)
                        self.registers[destination.get_name()].set_buffer(rs)
                    rs.set_busy_status(True)
                    rs.set_instruction_pointer(instruction)
                    rs.instruction_pointer.set_issued_cycle(self.clock_cycle)
                    issued = True
                    print("Issued: ", instruction)
        else: # opcode == "LDDD" or opcode == "STDD"
            for lb in self.loadbuffers.values():
                if lb.get_busy_status() == False and issued == False and destination.get_name() not in registers and operand2.get_name() not in registers:
                    print("Avaliable Load/Store Buffer " + lb.get_name())
                    lb.set_op(opcode)
                    lb.set_time(self.instruction_latency[opcode])
                    lb.set_address(str(operand1) + " " + operand2.get_name()) # check data types
                    if operand2.get_buffer() != None:
                        lb.set_qj(operand2)
                    else:
                        lb.set_vj(operand2)
                        self.registers[operand2.get_name()].set_buffer(lb)
                    if destination.get_buffer() != None:
                        lb.set_source_buffer(destination)
                    else:
                        lb.set_source(destination)
                        self.registers[destination.get_name()].set_buffer(lb)
                    lb.set_busy_status(True)
                    issued = True
                    lb.set_instruction_pointer(instruction)
                    lb.instruction_pointer.set_issued_cycle(self.clock_cycle)
                    print("Issued: ", instruction)
        if issued == False:
            print("No avalible Function Units this  clock cycle for Instruction: ", instruction)
        return issued # determine if instruction issued or not, if not issued need to be next instrucion instead of new front of queue
    
    def execute_instructions(self): 
        for rs in self.fp_adders.values():
            if rs.get_busy_status() == True and rs.get_qj() == None and rs.get_qk() == None and rs.get_source_buffer() == None:
                if rs.instruction_pointer.issue_delay == False and rs.get_vk().get_write_back() == True and rs.get_vj().get_write_back() == True and rs.get_source().get_write_back() == True:
                    if rs.get_time() == self.instruction_latency[rs.get_op()]:
                        rs.instruction_pointer.set_execute_start_cycle(self.clock_cycle)
                    rs.set_time(rs.get_time()- 1)
                    rs.executing_cycles += 1
                    if rs.get_time() == 0:
                        rs.instruction_pointer.set_execute_end_cycle(self.clock_cycle)
                else:  
                    rs.instruction_pointer.set_issue_delay(False)
                    if rs.get_vk().get_write_back() == False:
                        rs.get_vk().set_write_back(True)
                    if rs.get_vj().get_write_back() == False:
                        rs.get_vj().set_write_back(True)
                    if rs.get_source().get_write_back() == False:
                        rs.get_source().set_write_back(True)
            if rs.get_busy_status() == True and rs.get_qj() != None:
                if self.registers[rs.get_qj().get_name()].get_buffer() == None:
                    rs.set_vj(rs.get_qj())
                    self.registers[rs.get_vj().get_name()].set_buffer(rs)
                    rs.set_qj(None)
                rs.instruction_pointer.set_issue_delay(False)
            if rs.get_busy_status() == True and rs.get_qk() != None:
                if self.registers[rs.get_qk().get_name()].get_buffer() == None:
                    rs.set_vk(rs.get_qk())
                    self.registers[rs.get_vk().get_name()].set_buffer(rs)
                    rs.set_qk(None)
                rs.instruction_pointer.set_issue_delay(False)
            if rs.get_busy_status() == True and rs.get_source_buffer() != None:
                if self.registers[rs.get_source_buffer().get_name()].get_buffer() == None:
                    rs.set_source(rs.get_source_buffer())
                    self.registers[rs.get_source_buffer().get_name()].set_buffer(rs)
                    rs.set_source_buffer(None)
                rs.instruction_pointer.set_issue_delay(False)
            if rs.get_busy_status() == True:
                rs.busy_cycles += 1
        for rs in self.fp_multipliers.values():
            if rs.get_busy_status() == True and rs.get_qj() == None and rs.get_qk() == None and rs.get_source_buffer() == None:
                if rs.instruction_pointer.issue_delay == False and rs.get_vk().get_write_back() == True and rs.get_vj().get_write_back() == True and rs.get_source().get_write_back() == True:
                    if rs.get_time() == self.instruction_latency[rs.get_op()]:
                        rs.instruction_pointer.set_execute_start_cycle(self.clock_cycle)
                    rs.set_time(rs.get_time()- 1)
                    rs.executing_cycles += 1
                    if rs.get_time() == 0:
                        rs.instruction_pointer.set_execute_end_cycle(self.clock_cycle)
                else:
                    rs.instruction_pointer.set_issue_delay(False)
                    if rs.get_vk().get_write_back() == False:
                        rs.get_vk().set_write_back(True)
                    if rs.get_vj().get_write_back() == False:
                        rs.get_vj().set_write_back(True)
                    if rs.get_source().get_write_back() == False:
                        rs.get_source().set_write_back(True)
            if rs.get_busy_status() == True and rs.get_qj() != None:
                if self.registers[rs.get_qj().get_name()].get_buffer() == None:
                    rs.set_vj(rs.get_qj())
                    self.registers[rs.get_vj().get_name()].set_buffer(rs)
                    rs.set_qj(None)
                rs.instruction_pointer.set_issue_delay(False)
            if rs.get_busy_status() == True and rs.get_qk() != None:
                if self.registers[rs.get_qk().get_name()].get_buffer() == None:
                    rs.set_vk(rs.get_qk())
                    self.registers[rs.get_vk().get_name()].set_buffer(rs)
                    rs.set_qk(None)
                rs.instruction_pointer.set_issue_delay(False)
            if rs.get_busy_status() == True and rs.get_source_buffer() != None:
                if self.registers[rs.get_source_buffer().get_name()].get_buffer() == None:
                    rs.set_source(rs.get_source_buffer())
                    self.registers[rs.get_source_buffer().get_name()].set_buffer(rs)
                    rs.set_source_buffer(None)
                rs.instruction_pointer.set_issue_delay(False)
            if rs.get_busy_status() == True:
                    rs.busy_cycles += 1
        for lb in self.loadbuffers.values():
            if lb.get_busy_status() == True and lb.get_qj() == None and lb.get_source_buffer() == None:
                if lb.instruction_pointer.issue_delay == False and lb.get_vj().get_write_back() == True and lb.get_source().get_write_back() == True: # NOT GETTING IN HERE
                    if lb.get_time() == self.instruction_latency[lb.get_op()]:
                        lb.instruction_pointer.set_execute_start_cycle(self.clock_cycle)
                    lb.set_time(lb.get_time()- 1)
                    lb.executing_cycles += 1
                    if lb.get_time() == 0:
                        lb.instruction_pointer.set_execute_end_cycle(self.clock_cycle)
                else:
                    lb.instruction_pointer.set_issue_delay(False)
                    if lb.get_vj().get_write_back() == False:
                        lb.get_vj().set_write_back(True)
                    if lb.get_source().get_write_back() == False:
                        lb.get_source().set_write_back(True)
            if lb.get_busy_status() == True and lb.get_qj() != None:
                if self.registers[lb.get_qj().get_name()].get_buffer() == None:
                    lb.set_vj(lb.get_qj())
                    self.registers[lb.get_vj().get_name()].set_buffer(lb)
                    lb.set_qj(None)
                lb.instruction_pointer.set_issue_delay(False)
            if lb.get_busy_status() == True and lb.get_source_buffer() != None:
                if self.registers[lb.get_source_buffer().get_name()].get_buffer() == None:
                    # source and source buffer
                    lb.set_source(lb.get_source_buffer())
                    self.registers[lb.get_source_buffer().get_name()].set_buffer(lb)
                    lb.set_source_buffer(None)
                lb.instruction_pointer.set_issue_delay(False)
            if lb.get_busy_status() == True:
                lb.busy_cycles += 1    
     
    def write_back(self): 
        for rs in self.fp_adders.values():
            if rs.get_busy_status() == True and rs.get_time() == 0:
                self.registers[rs.get_vj().get_name()].set_buffer(None) 
                self.registers[rs.get_vk().get_name()].set_buffer(None)
                self.registers[rs.get_source().get_name()].set_buffer(None)
                rs.get_vk().set_write_back(False)
                rs.get_vj().set_write_back(False)
                rs.get_source().set_write_back(False)
                rs.set_time(None)
                rs.set_op(None)
                rs.set_vj(None)
                rs.set_vk(None)
                rs.set_qj(None)
                rs.set_qk(None)
                rs.set_source(None)
                rs.set_source_buffer(None)
                rs.set_busy_status(False)
                rs.instruction_pointer.set_write_back_cycle(self.clock_cycle)
                rs.set_instruction_pointer(None)
        for rs in self.fp_multipliers.values():
            if rs.get_busy_status() == True and rs.get_time() == 0:
                self.registers[rs.get_vj().get_name()].set_buffer(None) 
                self.registers[rs.get_vk().get_name()].set_buffer(None)
                self.registers[rs.get_source().get_name()].set_buffer(None)
                rs.get_vk().set_write_back(False)
                rs.get_vj().set_write_back(False)
                rs.get_source().set_write_back(False)
                rs.set_time(None)
                rs.set_op(None)
                rs.set_vj(None)
                rs.set_vk(None)
                rs.set_qj(None)
                rs.set_qk(None)
                rs.set_source(None)
                rs.set_source_buffer(None)
                rs.set_busy_status(False)
                rs.instruction_pointer.set_write_back_cycle(self.clock_cycle)
                rs.set_instruction_pointer(None)
        for lb in self.loadbuffers.values():
            if lb.get_busy_status() == True and lb.get_time() == 0: # lb is only set to false here 
                self.registers[lb.get_vj().get_name()].set_buffer(None)
                self.registers[lb.get_source().get_name()].set_buffer(None)
                lb.get_vj().set_write_back(False)
                lb.get_source().set_write_back(False)
                lb.set_time(None)
                lb.set_address(None)
                lb.set_vj(None)
                lb.set_qj(None)
                lb.set_busy_status(False)
                lb.set_source(None)
                lb.set_source_buffer(None)
                lb.instruction_pointer.set_write_back_cycle(self.clock_cycle)
                lb.set_instruction_pointer(None)
        self.check_register_buffers()
    
    def check_register_buffers(self): # helper function used to prevent deadlocks from issued instructions coming before buffers are set
        for rs in self.fp_adders.values():
            if rs.get_busy_status() == True and rs.get_qj() != None and self.registers[rs.get_qj().get_name()].get_buffer() == None: # python and is sequential so by checking to make sure not none then the last condition will not result in Nonetype error
                rs.set_vj(rs.get_qj())
                self.registers[rs.get_qj().get_name()].set_buffer(rs)
                rs.set_qj(None)
            elif rs.get_busy_status() == True and rs.get_qk() != None and self.registers[rs.get_qk().get_name()].get_buffer() == None:
                rs.set_vk(rs.get_qk())
                self.registers[rs.get_qk().get_name()].set_buffer(rs)
                rs.set_qk(None)
            elif rs.get_busy_status() == True and rs.get_source_buffer() != None and self.registers[rs.get_source_buffer().get_name()].get_buffer() == None:
                rs.set_source(rs.get_source_buffer())
                self.registers[rs.get_source_buffer().get_name()].set_buffer(rs)
                rs.set_source_buffer(None)
        for rs in self.fp_multipliers.values():
            if rs.get_busy_status() == True and rs.get_qj() != None and self.registers[rs.get_qj().get_name()].get_buffer() == None:
                rs.set_vj(rs.get_qj())
                self.registers[rs.get_qj().get_name()].set_buffer(rs)
                rs.set_qj(None)
            elif rs.get_busy_status() == True and rs.get_qk() != None and self.registers[rs.get_qk().get_name()].get_buffer() == None:
                rs.set_vk(rs.get_qk())
                self.registers[rs.get_qk().get_name()].set_buffer(rs)
                rs.set_qk(None)
            elif rs.get_busy_status() == True and rs.get_source_buffer() != None and self.registers[rs.get_source_buffer().get_name()].get_buffer() == None:
                rs.set_source(rs.get_source_buffer())
                self.registers[rs.get_source_buffer().get_name()].set_buffer(rs)
                rs.set_source_buffer(None)
        for lb in self.loadbuffers.values():
            if lb.get_busy_status() == True and lb.get_qj() != None and self.registers[lb.get_qj().get_name()].get_buffer() == None:
                lb.set_vj(lb.get_qj())
                self.registers[lb.get_qj().get_name()].set_buffer(lb)
                lb.set_qj(None)
            elif lb.get_busy_status() == True and lb.get_source_buffer() != None and self.registers[lb.get_source_buffer().get_name()].get_buffer() == None:
                lb.set_source(lb.get_source_buffer())
                self.registers[lb.get_source_buffer().get_name()].set_buffer(lb)
                lb.set_source_buffer(None)
    
    def empty_reservation_stations(self):
        for rs in self.fp_adders.values():
            if rs.get_busy_status() == True:
                return False
        for rs in self.fp_multipliers.values():
            if rs.get_busy_status() == True:
                return False
        for lb in self.loadbuffers.values():
            if lb.get_busy_status() == True:
                return False
        return True

    def update_utilizations(self):
        for rs in self.fp_adders.values():
            rs.busy_fraction = rs.busy_cycles/self.clock_cycle
            rs.executing_fraction = rs.executing_cycles/self.clock_cycle
        for rs in self.fp_multipliers.values():
            rs.busy_fraction = rs.busy_cycles/self.clock_cycle
            rs.executing_fraction = rs.executing_cycles/self.clock_cycle
        for lb in self.loadbuffers.values():
            lb.busy_fraction = lb.busy_cycles/self.clock_cycle
            lb.executing_fraction = lb.executing_cycles/self.clock_cycle

    def buffer_registers(self): # list of registers that are in qj, qk and source buffer to be used to check when to block issue instruction
        registers = []
        for rs in self.fp_adders.values():
            if rs.get_qj() != None:
                registers.append(rs.get_qj().get_name())
            if rs.get_qk() != None:
                registers.append(rs.get_qk().get_name())
            if rs.get_source_buffer() != None:
                registers.append(rs.get_source_buffer().get_name())
        for rs in self.fp_multipliers.values():
            if rs.get_qj() != None:
                registers.append(rs.get_qj().get_name())
            if rs.get_qk() != None:
                registers.append(rs.get_qk().get_name())
            if rs.get_source_buffer() != None:
                registers.append(rs.get_source_buffer().get_name())
        for lb in self.loadbuffers.values():
            if lb.get_qj() != None:
                registers.append(lb.get_qj().get_name())
            if lb.get_source_buffer() != None:
                registers.append(lb.get_source_buffer().get_name())
        return registers
        
        
    def run_algorithim(self): # add verbose mode to determine what is displayed
        self.update_simulation_results()
        if self.dispatch_size == 1:
            while self.instruction_queue.is_empty() != True:
                print("\n")
                instruction = self.instruction_queue.soft_dequeue()
                issued = self.issue_instruction(instruction) # boolean based on if instruction was issued
                if issued == False:
                    while issued == False:
                        issued = self.issue_instruction(instruction)
                        self.write_back()
                        self.execute_instructions()
                        #self.write_back()
                        self.increment_clock_cycle()
                        self.update_utilizations()
                        self.display_simulation()
                        self.update_simulation_results()
                else:
                    self.write_back()
                    self.execute_instructions()
                    #self.write_back()
                    self.increment_clock_cycle()
                    self.update_utilizations()
                    self.display_simulation()
                    self.update_simulation_results()
            while self.empty_reservation_stations() != True: # finish execution after all instructions are issued 
                self.write_back()
                self.execute_instructions()
                #self.write_back()
                self.increment_clock_cycle()
                self.update_utilizations()
                self.display_simulation()
                self.update_simulation_results()
            print("\nRESULTS TABLE\n")
            print(self.instruction_queue)
            return self.instruction_queue, self.output
        elif self.dispatch_size == 2:
            while self.instruction_queue.is_empty() != True:
                print("\n")
                instruction1 = self.instruction_queue.soft_dequeue()
                issued1 = self.issue_instruction(instruction1) # boolean based on if instruction was issued
                instruction2= self.instruction_queue.soft_dequeue()
                issued2 = self.issue_instruction(instruction2)
                if issued1 == False or issued2 == False:
                    while issued1 == False:
                        issued1 = self.issue_instruction(instruction1)
                        self.write_back()
                        self.execute_instructions()
                        #self.write_back()
                        self.increment_clock_cycle()
                        self.update_utilizations()
                        self.display_simulation()
                        self.update_simulation_results()
                    while issued2 == False:
                        issued2 = self.issue_instruction(instruction2)
                        self.write_back()
                        self.execute_instructions()
                        #self.write_back()
                        self.increment_clock_cycle()
                        self.update_utilizations()
                        self.display_simulation()
                        self.update_simulation_results()
                else:
                    self.write_back()
                    self.execute_instructions()
                    #self.write_back()
                    self.increment_clock_cycle()
                    self.update_utilizations()
                    self.display_simulation()
                    self.update_simulation_results()
            while self.empty_reservation_stations() != True: # finish execution after all instructions are issued 
                self.write_back()
                self.execute_instructions()
                #self.write_back()
                self.increment_clock_cycle()
                self.update_utilizations()
                self.display_simulation()
                self.update_simulation_results()
            print("\nRESULTS TABLE\n")
            print(self.instruction_queue)
            return self.instruction_queue, self.output # need to also return individual execution utilization values for plotting
        else:
            raise ValueError("Please make sure dispatch_size parameter in Tomalulo class variable is either 1 or 2")


    def display_simulation(self):
        print("\n")
        print(f"Clock Cycle: {self.clock_cycle}")
        print("\n")
        self.display_adders()
        print("\n")
        self.display_multipliers()
        print("\n")
        self.display_loadbuffers()
        print("\n")
        self.display_registers()
        print("\n")

    def update_simulation_results(self):
        o_string = self.return_adders_string() + self.return_multipliers_string() + self.return_loadbuffers_string() + self.return_registers_string()
        self.output.append([self.clock_cycle, o_string])
    
        

import matplotlib.pyplot as plt
import random
import builtins
#https://stackoverflow.com/questions/4698493/can-i-add-custom-methods-attributes-to-built-in-python-types

class address_offset(str):
    def get_name(self):
        return self

__builtins__.str = address_offset

opcodes = ["ADDD", "SUBD", "MULTD", "DIVD", "LDDD", "STDD"]

# include this function outside class to keep consistent instruction stream among multiple tomasulo simulator confirgurations for testing functional unit utilization
def generate_instruction_queue(opcodes, registers, number_instructions): # need to add checks to make sure loads are done first also to change the addresses of loads (probably not anymore)
    instruction_queue = InstructionQueue()
    for esh in range(number_instructions):
        opcode = random.choice(opcodes)
        destination = random.choice(list(registers.values()))
        operand1 = random.choice(list(registers.values()))
        operand2 = random.choice(list(registers.values()))
        while operand1.get_name() == destination.get_name():
            operand1 = random.choice(list(registers.values()))
        while operand2.get_name() == destination.get_name() or operand2.get_name() == operand1.get_name():
            operand2 = random.choice(list(registers.values()))
        if opcode == "LDDD" or opcode == "STDD":
            operand1 = str(str(random.choice(range(65536))) + "+") # extra wrapper for address_offset datatype
        instruction_queue.enqueue(opcode, destination, operand1, operand2)
    return instruction_queue

def generate_registers(num_registers):
    registers = {}
    for esh in range(num_registers):
            registers["F" + str(esh)] = Register("F" + str(esh))
    return registers

# output each clock cycle contents into a data structure to be able to print out any given clock cycle

# TEST CODE
# default latencies of 2 2 10 40 1 1
random.seed(1)
default_latencies = [2,2,10,40,1,1]
registers = generate_registers(11)
queue = generate_instruction_queue(opcodes, registers, 20) # change amount of instructions for different tests
print(queue)
# (instruction_queue, num_fp_add, num_fp_mult, num_loadstore, registers, opcodes, dispatch_size)
tomasulo = Tomasulo(queue, 3, 2, 3, registers, opcodes, 1) 
results_table, simulation_results = tomasulo.run_algorithim()

