#################################################################################################################
# Class: Instruction
#
# This class contains the core information for each instruction - the opcode,
# operands, and destination. Additionally, book-keeping information is
# recorded within the instruction for the Tomasulo algorithm and performance
# measurement.
#
# Purpose:
#
#   Instructions are fetched and placed into the InstructionQueue. They are
# issued to the execution unit when the Tomasulo Algorithm determines that
# there are free resources to execute the instruction and when all the
# operands and destination of the instruction are ready.
#
# Underlying Implmentation:
#   Node of a Singly Linked List
#
#   Note: Each instruction holds a pointer to the next instruction.
#
# Private Data Members:
#     String opcode           - pointer to the first instruction in the queue.
#     Register * destination  - Points to the register where the result of the instruction will be written.
#     Register * operand1     - Points to the register that contains the
#                               first operand of the instruction.
#     Register * operand2     - Points to the register that contains the
#                               second operand of the instruction.
#     Instruction * next      - Points to the next instruction in the linked list.
#     int issued_cycle        - Marks the cycle when this instruction was issued.
#     int execute_start_cycle - Timestamp (in clock-cycles) when instruction started executing.
#     int execute_end_cycle   - Timestamp (in clock-cycles) when instruction finished executing.
#     int write_back_cycle    - Timestamp (in clock-cycles) when instruction result was written to destination.
#
# Public Interface/Methods:
#     __init__ - Constructs a new instruction
#     __str__  - Outputs instruction content as a string
#
#     Accessor Methods:
#       RO (get_X):       opcode, destination, operand1, operand2
#       RW ({get|set}_X): issued_cycle, execute_start_cycle, write_back_cycle
#       WO (set_X):       issue_delay
#
#####################################################################################################################
class Instruction: 
    def __init__(self, opcode, destination, operand1, operand2, next=None, issued_cycle=0, execute_start_cycle=0, execute_end_cycle=0, write_back_cycle=0):
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
# Purpose:
#
#   The processor's instruction fetch unit will retrieve instructions from
#   memory and load each instruction into the instruction queue. It is from
#   this queue that instructions are introduced to the system and
#   are then dispatched to relevant portions of the Tomasulo sub-system.
#   Basic information required to run a given instruction are saved into the
#   queue; that same information is used later on to make scheduling decisions.
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
        self.soft_length = 0
        self.pseudo_head = None

    def __str__(self):
        instructions = "" 
        current = self.head
        while current:
            #instruction = []
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
        return self.soft_length == 0

    def get_length(self):
        return self.soft_length

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
    # Complexity: Constant - O(1)
    #   It will always take a maximum of 2 to 3 operations
    #   to queue an instruction.
    #   (i.e., set the head, tail, and length)
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
        self.soft_length +=1

    ###########################################################
    #
    # Method: dequeue
    #
    #     Shifts out the instruction waiting at the front of the
    # queue and then points the 'pseudo_head' to the next
    # instruction in the queue. Old instructions are retained
    # until explicity flushed, so that instruction history can
    # be used for later analysis and scheduling decisions.
    #
    # Parameters:
    #     InstructionQueue * self
    #
    # Returns: Instruction at the front of the queue or 'None'.
    #
    # Complexity: Constant - O(1)
    #   It will always take a maximum of 2 to 3 operations
    #   to dequeue an instruction.
    #   (i.e., set the head, tail, and length)
    #
    ###########################################################
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
        self.soft_length -= 1 # length also needs to be controlled by soft_dequeue to mimic dequeue even though its not accurate
        
        return instruction
    
    
############################################################################
# Class: ReservationStation
#
# TODO: Place class description here
#
# Purpose:
#
#   Reservation Stations are part of the Execution Unit. Instructions pulled
#   from the Instruction Queue are loaded into one of several available
#   Reservation Stations.

#   Instructions in a Reservation Station enter a 'waiting' state,
#   where the instruction delays execution until all resources required for
#   execution are obtained (for example, results to reach the register file,
#   memory loads, or execution unit availability, etc...). Once an instruction
#   and all of its required resources/data is deposited into a Reservation Station,
#   the instruction is dispatched to an appropriate execution unit
#   (adder, multiplier, etc.).
#
# Underlying Implmentation:
#   Singly Linked List
#
#   Note: The nodes are the instructions themselves,
#         and each one holds a pointer to the next instruction.
#
# Private Data Members:
#     
#     time - amount of time an instruction will take to execute once dispatched.
#     op   - instruction's opcode
#     Register * vj   - First operand of the instruction in this reservation station.
#                       If the reservation station is unoccupied, vj = None.
#     Register * qj   - First operand of the instruction in this reservation station.
#                       If the reservation station is unoccupied, qj = None.
#     Register * vk   - Second operand of the instruction in this reservation station.
#                       If the reservation station is unoccupied, vk = None.
#     Register * qk   - Second operand of the instruction in this reservation station.
#                       If the reservation station is unoccupied, qk = None.
#     Register * source -
#     Register * source_buffer -
#     bool busy -
#     int busy_cycles -
#     int executing_cycles -
#     float busy_fraction -
#     float executing_fraction -
#     Instruction * instruction_pointer - A handle to the instruction occupying
#                                         this Reservation station, so that
#                                         its start/end execution and
#                                         write-back cycles can be modified.
#                                        
#
# Public Interface/Methods:
#
# __init__, 
#
#######################################################################################
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
    def __init__(self, name, buffer=None):
        self.name = name
        self.buffer = buffer # should be a reservation station/ load buffer
        self.write_back = True

    def get_name(self):
        return self.name

    def get_buffer(self):
        return self.buffer

    def get_write_back(self):
        return self.write_back

    def set_buffer(self, buffer):
        self.buffer = buffer

    def set_write_back(self, boolean):
        self.write_back = boolean

    def __str__(self):
        return(f"Register: {self.name} | Buffer Station: {self.buffer.get_name() if self.buffer != None else None}")

class Tomasulo:
    def __init__(self, instruction_queue, num_fp_add, num_fp_mult, num_loadstore, registers, opcodes, dispatch_size, verbose_mode, latencies = None):
        ####################################################################
        # Initialize the instruction queue for incoming instructions
        ####################################################################
        self.instruction_queue = instruction_queue

        ####################################################################
        # Initialize the functional unit buffers within the Execution Unit.
        ####################################################################
        self.num_fp_add = num_fp_add
        self.num_fp_mult = num_fp_mult
        self.num_loadstore = num_loadstore
        self.fp_adders = {}
        self.fp_multipliers = {}
        self.loadbuffers = {}

        for esh in range(self.num_fp_add):
            self.fp_adders["ADD" + str(esh + 1)] = ReservationStation("ADD" + str(esh + 1))
        for esh in range(self.num_fp_mult):
            self.fp_multipliers["MULT" + str(esh + 1)] = ReservationStation("MULT" + str(esh + 1))
        for esh in range(self.num_loadstore):
            self.loadbuffers["LOAD/STORE" + str(esh + 1)] = LoadBuffer("LOAD/STORE" + str(esh + 1))

        self.registers = registers
        self.dispatch_size = int(dispatch_size)
        self.verbose_mode = verbose_mode
        self.latencies = latencies
        self.parameters = [num_fp_add, num_fp_mult, num_loadstore, len(registers), instruction_queue.length, dispatch_size]
        self.clock_cycle = 0
        self.output = []

        ###########################################################################################
        # Obtain the execution time/latency (in clock-cycles) for each instruction either
        # from the user or from the latencies table.
        ###########################################################################################
        self.instruction_latency = {}
        if self.latencies == None:
            for opcode in opcodes:
                latency = None
                while type(latency) != type(1):
                    latency = int(input("Enter latency for " + opcode + ":"))
                self.instruction_latency[opcode] = latency
        else:
            for opcode in opcodes:
                self.instruction_latency[opcode] = self.latencies[opcode]
                
    #######################################################################
    #
    # CPU Clock Cycle Management
    #
    #######################################################################
        
    def increment_clock_cycle(self):
        self.clock_cycle += 1

    def get_clock_cycle(self):
        return self.clock_cycle

    #######################################################################
    #
    # Methods to Display the internal state of the Execution Unit or
    # convert the internal state of the Execution to a string.
    #
    #######################################################################

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

    ###############################################################################
    #
    # Tomasulo Scheduling Algorithm for issuing instructions to the Execution Unit
    #
    #
    #
    ###############################################################################
    def issue_instruction(self, instruction):
        issued = False
        opcode = instruction.get_opcode()
        destination = instruction.get_destination()
        operand1 = instruction.get_operand1()
        operand2 = instruction.get_operand2()
        
        registers = self.buffer_registers()

        ################################################################
        # Handle Instructions requiring the Adder Functional Unit
        ################################################################
        if opcode == "ADDD" or opcode == "SUBD":
            for rs in self.fp_adders.values():
                #####################################################################
                # Issue instruction to Adder Reservation station when all
                # the following conditions are satisfied:
                #
                # * ReservationStation isn't busy
                # * The instruction hasn't already been issued.
                # * The instruction's operands 
                # if it's available and the instruction hasn't already been issued.
                #####################################################################
                if rs.get_busy_status() == False and issued == False and destination.get_name() not in registers and operand1.get_name() not in registers and operand2.get_name() not in registers:
                    if self.verbose_mode == True:
                        print("Avaliable Reservation Station " + rs.get_name())
                    rs.set_op(opcode)
                    rs.set_time(self.instruction_latency[opcode])

                    ################################################
                    # Determine Instruction Register locations
                    #
                    # Note: Need to figure out how to
                    #       check j,k value and if they
                    #       they are busy.
                    #
                    # If the operand's value depends on the result
                    # of another station that hasn't completed yet
                    # (operandX.get_buffer() != None), then set
                    # the Reservation Station's qX parameter to
                    # the buffer it is waiting for.
                    #
                    # Otherwise, set the vX parameter to
                    # the current value of the register,
                    # and then update the latest location of the
                    # register to this Reservation Station in the
                    # Register Alias Table.
                    #
                    ################################################
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
                    
                    if self.verbose_mode == True:
                        print("Issued: ", instruction)
                        
        ################################################################
        # Handle Instructions requiring the Multiplier Functional Unit
        ################################################################
        elif opcode == "MULTD" or opcode == "DIVD":
            for rs in self.fp_multipliers.values():
                if rs.get_busy_status() == False and issued == False and destination.get_name() not in registers and operand1.get_name() not in registers and operand2.get_name() not in registers:
                    if self.verbose_mode == True:
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
                    if self.verbose_mode == True:
                        print("Issued: ", instruction)
                        
        ################################################################
        # Handle Instructions requiring the Memory Interface
        ################################################################
        else: # opcode == "LDDD" or opcode == "STDD"
            for lb in self.loadbuffers.values():
                if lb.get_busy_status() == False and issued == False and destination.get_name() not in registers and operand2.get_name() not in registers:
                    if self.verbose_mode == True:
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
                    if self.verbose_mode == True:
                        print("Issued: ", instruction)
                        
        if issued == False and self.verbose_mode == True:
            print("No avalible Function Units this  clock cycle for Instruction: ", instruction)
        return issued # determine if instruction issued or not, if not issued need to be next instrucion instead of new front of queue
    
    def execute_instructions(self):
        ######################################
        # Run Execution Cycle for the Adders
        ######################################
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
                
        ###########################################
        # Run Execution Cycle for the Multipliers
        ###########################################
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

        ################################################
        # Run Execution Cycle for the Memory Interface
        ################################################
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
                    lb.set_source(lb.get_source_buffer())
                    self.registers[lb.get_source_buffer().get_name()].set_buffer(lb)
                    lb.set_source_buffer(None)
                lb.instruction_pointer.set_issue_delay(False)
            if lb.get_busy_status() == True:
                lb.busy_cycles += 1    

    #############################################################
    # Write-Back Execution Results and clear stations/buffers
    #
    # Note: infinite loop caused because instruction is issued
    #       before qj/qk given to what needs it so make a check
    #       here to send it back on clock cycle 87
    #############################################################
    def write_back(self):

        # Write-back and clear adders
        for rs in self.fp_adders.values():
            if rs.get_busy_status() == True and rs.get_time() == 0:
                self.registers[rs.get_vj().get_name()].set_buffer(None) 
                self.registers[rs.get_vk().get_name()].set_buffer(None)
                self.registers[rs.get_source().get_name()].set_buffer(None)

                # Clear the Reservation Station
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

        # Write-back and clear Multipliers
        for rs in self.fp_multipliers.values():
            if rs.get_busy_status() == True and rs.get_time() == 0:
                self.registers[rs.get_vj().get_name()].set_buffer(None) 
                self.registers[rs.get_vk().get_name()].set_buffer(None)
                self.registers[rs.get_source().get_name()].set_buffer(None)

                # Clear the Reservation Station
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

        # Write-back and clear Load Buffers
        for lb in self.loadbuffers.values():
            if lb.get_busy_status() == True and lb.get_time() == 0: # lb is only set to false here 
                self.registers[lb.get_vj().get_name()].set_buffer(None)
                self.registers[lb.get_source().get_name()].set_buffer(None)

                # Clear the Load Buffer
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

    ##########################################################
    # Helper function used to prevent deadlocks from issued
    # instructions coming before buffers are set
    ##########################################################
    def check_register_buffers(self): # helper function used to prevent deadlocks from issued instructions coming before buffers are set
        # Check Adders
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

        # Check Multipliers
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

        # Check Load Buffers
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
        
        
    def run_algorithim(self): 
        self.update_simulation_results()
        if self.dispatch_size == 1:
            while self.instruction_queue.is_empty() != True:
                if self.verbose_mode == True:
                    print("\n")
                instruction = self.instruction_queue.soft_dequeue()
                issued = self.issue_instruction(instruction) # boolean based on if instruction was issued
                if issued == False:
                    while issued == False:
                        issued = self.issue_instruction(instruction)
                        self.write_back()
                        self.execute_instructions()
                        self.increment_clock_cycle()
                        self.update_utilizations()
                        if self.verbose_mode == True:
                            self.display_simulation()
                        self.update_simulation_results()
                else:
                    self.write_back()
                    self.execute_instructions()
                    self.increment_clock_cycle()
                    self.update_utilizations()
                    if self.verbose_mode == True:
                        self.display_simulation()
                    self.update_simulation_results()
            while self.empty_reservation_stations() != True: # finish execution after all instructions are issued 
                self.write_back()
                self.execute_instructions()
                self.increment_clock_cycle()
                self.update_utilizations()
                if self.verbose_mode == True:
                    self.display_simulation()
                self.update_simulation_results()
            if self.verbose_mode == True:
                print("\nRESULTS TABLE\n")
                print(self.instruction_queue)
            utilizations = self.return_utilizations()
            return self.instruction_queue, self.output, utilizations, self.parameters
        elif self.dispatch_size == 2:
            while self.instruction_queue.is_empty() != True:
                if self.verbose_mode == True:
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
                        self.increment_clock_cycle()
                        self.update_utilizations()
                        if self.verbose_mode == True:
                            self.display_simulation()
                        self.update_simulation_results()
                    while issued2 == False:
                        issued2 = self.issue_instruction(instruction2)
                        self.write_back()
                        self.execute_instructions()
                        self.increment_clock_cycle()
                        self.update_utilizations()
                        if self.verbose_mode == True:
                            self.display_simulation()
                        self.update_simulation_results()
                else:
                    self.write_back()
                    self.execute_instructions()
                    self.increment_clock_cycle()
                    self.update_utilizations()
                    if self.verbose_mode == True:
                        self.display_simulation()
                    self.update_simulation_results()
            while self.empty_reservation_stations() != True: # finish execution after all instructions are issued 
                self.write_back()
                self.execute_instructions()
                self.increment_clock_cycle()
                self.update_utilizations()
                if self.verbose_mode == True:
                    self.display_simulation()
                self.update_simulation_results()
            if self.verbose_mode == True:
                print("\nRESULTS TABLE\n")
                print(self.instruction_queue)
            utilizations = self.return_utilizations()
            return self.instruction_queue, self.output, utilizations, self.parameters  
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

    def return_utilizations(self):
        utilizations = []
        for rs in self.fp_adders.values():
            utilizations.append([rs.get_name(), rs.busy_fraction, rs.executing_fraction])
        for rs in self.fp_multipliers.values():
            utilizations.append([rs.get_name(), rs.busy_fraction, rs.executing_fraction])
        for lb in self.loadbuffers.values():
            utilizations.append([lb.get_name(), lb.busy_fraction, lb.executing_fraction])
        return utilizations

######################################################
#
# Main Program
#
######################################################

import matplotlib.pyplot as plt
import tkinter as tk
import random
import numpy as np
import copy
#https://stackoverflow.com/questions/4698493/can-i-add-custom-methods-attributes-to-built-in-python-types

class address_offset(str):
    def get_name(self):
        return self

opcodes = ["ADDD", "SUBD", "MULTD", "DIVD", "LDDD", "STDD"]

# include this function outside class to keep consistent instruction stream among multiple tomasulo simulator confirgurations for testing functional unit utilization
def generate_instruction_queue(opcodes, registers, number_instructions): 
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
            operand1 = address_offset(str(random.choice(range(65536))) + "+") # extra wrapper for address_offset datatype
        instruction_queue.enqueue(opcode, destination, operand1, operand2)
    return instruction_queue

def generate_registers(num_registers):
    registers = {}
    for esh in range(num_registers):
            registers["F" + str(esh)] = Register("F" + str(esh))
    return registers

def add_labels(bars): # adds exact values on top of each bar
    for bar in bars:
        value = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, value, f'{value:.4f}', ha='center', va='bottom', fontsize=10)

def plot_results(rs_utilizations, clock_cycles, parameters):
    rs_name = [simulation[0] for simulation in rs_utilizations]
    busy_utilization = [simulation[1] for simulation in rs_utilizations]
    executing_utilization = [simulation[2] for simulation in rs_utilizations]
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    plt.figure(figsize=(screen_width/100, screen_height/100))
    width = .5
    x = np.arange(len(rs_name))
    bar1= plt.bar(x - width / 2, busy_utilization, width, label='Busy Utilization', color='cyan')
    bar2= plt.bar(x + width / 2, executing_utilization, width, label='Executing Utilization', color='lime')
    plt.xlabel('Function Unit Name')
    plt.ylabel('Utilizations')  
    plt.title('Utilizations per Function Unit')
    plt.suptitle(f"Total Instructions: {parameters[4]} | Clock_Cycles: {clock_cycles} | Num_FP_Add: {parameters[0]} |  Num_FP_Mult: {parameters[1]} | Num_Load/Store: {parameters[2]} | Num_Registers: {parameters[3]} | Dispatch_Size: {parameters[5]}")
    plt.xticks(x, rs_name)
    plt.grid()
    plt.legend()
    add_labels(bar1)
    add_labels(bar2)
    plt.show()
    plt.close()

random.seed(1)
default_latencies = {"ADDD": 2, "SUBD": 2, "MULTD": 10, "DIVD": 40, "LDDD": 1,"STDD": 1}
registers = generate_registers(11)
registers32 = generate_registers(32)
registers64 = generate_registers(64)
registers128 = generate_registers(128)
queue = generate_instruction_queue(opcodes, registers, 20)
queue2 = copy.deepcopy(queue)
queue3 = copy.deepcopy(queue)
queue4 = copy.deepcopy(queue)
queue5 = copy.deepcopy(queue)
queue6 = copy.deepcopy(queue)
queue7 = copy.deepcopy(queue)
queue8 = copy.deepcopy(queue)
queue9 = generate_instruction_queue(opcodes, registers, 100)
queue10 = generate_instruction_queue(opcodes, registers, 1000)
queue11 = generate_instruction_queue(opcodes, registers32, 1000)
queue12 = generate_instruction_queue(opcodes, registers64, 1000)
queue13 = generate_instruction_queue(opcodes, registers64, 10000)
queue14 = generate_instruction_queue(opcodes, registers64, 10000)
queue15 = generate_instruction_queue(opcodes, registers128, 100000)
queue16 = copy.deepcopy(queue)
# (instruction_queue, num_fp_add, num_fp_mult, num_loadstore, registers, opcodes, dispatch_size, verbose_mode, latencies=None)
tomasulo = Tomasulo(queue, 3, 2, 3, registers, opcodes, 1, False, latencies=default_latencies)
# results_table = [instruction_queue], simulation_results = [Clock_Cycle, RS and Register information], rs_utilizations = [RS name, busy_utilization, executing_utilization], parameters = [num_fp_add, num_fp_mult, num_loadstore, len(registers), instruction_queue.length]
results_table, simulation_results, rs_utilizations, parameters = tomasulo.run_algorithim()
print(f"Total Instructions: {parameters[4]} | Clock_Cycles: {simulation_results[-1][0]} | Num_FP_Add: {parameters[0]} |  Num_FP_Mult: {parameters[1]} | Num_Load/Store: {parameters[2]} | Num_Registers: {parameters[3]} | Dispatch_Size: {parameters[5]}\n")
print(results_table)
plot_results(rs_utilizations, simulation_results[-1][0], parameters)

tomasulo16 = Tomasulo(queue16, 1, 1, 1, registers, opcodes, 1, False, latencies=default_latencies)
results_table16, simulation_results16, rs_utilizations16, parameters16 = tomasulo16.run_algorithim()
print(f"Total Instructions: {parameters16[4]} | Clock_Cycles: {simulation_results16[-1][0]} | Num_FP_Add: {parameters16[0]} |  Num_FP_Mult: {parameters16[1]} | Num_Load/Store: {parameters16[2]} | Num_Registers: {parameters16[3]} | Dispatch_Size: {parameters16[5]}\n")
print(results_table16)
plot_results(rs_utilizations16, simulation_results16[-1][0], parameters16)

tomasulo2 = Tomasulo(queue2, 3, 4, 3, registers, opcodes, 1, False, latencies=default_latencies)
results_table2, simulation_results2, rs_utilizations2, parameters2 = tomasulo2.run_algorithim()
print(f"Total Instructions: {parameters2[4]} | Clock_Cycles: {simulation_results2[-1][0]} | Num_FP_Add: {parameters2[0]} |  Num_FP_Mult: {parameters2[1]} | Num_Load/Store: {parameters2[2]} | Num_Registers: {parameters2[3]} | Dispatch_Size: {parameters2[5]}\n")
print(results_table2)
plot_results(rs_utilizations2, simulation_results2[-1][0], parameters2)

tomasulo3 = Tomasulo(queue3, 3, 8, 3, registers, opcodes, 1, False, latencies=default_latencies)
results_table3, simulation_results3, rs_utilizations3, parameters3 = tomasulo3.run_algorithim()
print(f"Total Instructions: {parameters3[4]} | Clock_Cycles: {simulation_results3[-1][0]} | Num_FP_Add: {parameters3[0]} |  Num_FP_Mult: {parameters3[1]} | Num_Load/Store: {parameters3[2]} | Num_Registers: {parameters3[3]} | Dispatch_Size: {parameters3[5]}\n")
print(results_table3)
plot_results(rs_utilizations3, simulation_results3[-1][0], parameters3)

tomasulo4 = Tomasulo(queue4, 3, 16, 3, registers, opcodes, 1, False, latencies=default_latencies)
results_table4, simulation_results4, rs_utilizations4, parameters4 = tomasulo4.run_algorithim()
print(f"Total Instructions: {parameters4[4]} | Clock_Cycles: {simulation_results4[-1][0]} | Num_FP_Add: {parameters4[0]} |  Num_FP_Mult: {parameters4[1]} | Num_Load/Store: {parameters4[2]} | Num_Registers: {parameters4[3]} | Dispatch_Size: {parameters4[5]}\n")
print(results_table4)
plot_results(rs_utilizations4, simulation_results4[-1][0], parameters4)

tomasulo5 = Tomasulo(queue5, 3, 2, 3, registers, opcodes, 2, False, latencies=default_latencies)
results_table5, simulation_results5, rs_utilizations5, parameters5 = tomasulo5.run_algorithim()
print(f"Total Instructions: {parameters5[4]} | Clock_Cycles: {simulation_results5[-1][0]} | Num_FP_Add: {parameters5[0]} |  Num_FP_Mult: {parameters5[1]} | Num_Load/Store: {parameters5[2]} | Num_Registers: {parameters5[3]} | Dispatch_Size: {parameters5[5]}\n")
print(results_table5)
plot_results(rs_utilizations5, simulation_results5[-1][0], parameters5)

tomasulo6 = Tomasulo(queue6, 3, 4, 3, registers, opcodes, 2, False, latencies=default_latencies)
results_table6, simulation_results6, rs_utilizations6, parameters6 = tomasulo6.run_algorithim()
print(f"Total Instructions: {parameters6[4]} | Clock_Cycles: {simulation_results6[-1][0]} | Num_FP_Add: {parameters6[0]} |  Num_FP_Mult: {parameters6[1]} | Num_Load/Store: {parameters6[2]} | Num_Registers: {parameters6[3]} | Dispatch_Size: {parameters6[5]}\n")
print(results_table6)
plot_results(rs_utilizations6, simulation_results6[-1][0], parameters6)

tomasulo7 = Tomasulo(queue7, 3, 8, 3, registers, opcodes, 2, False, latencies=default_latencies)
results_table7, simulation_results7, rs_utilizations7, parameters7 = tomasulo7.run_algorithim()
print(f"Total Instructions: {parameters7[4]} | Clock_Cycles: {simulation_results7[-1][0]} | Num_FP_Add: {parameters7[0]} |  Num_FP_Mult: {parameters7[1]} | Num_Load/Store: {parameters7[2]} | Num_Registers: {parameters7[3]} | Dispatch_Size: {parameters7[5]}\n")
print(results_table7)
plot_results(rs_utilizations7, simulation_results7[-1][0], parameters7)

tomasulo8 = Tomasulo(queue8, 3, 16, 3, registers, opcodes, 2, False, latencies=default_latencies)
results_table8, simulation_results8, rs_utilizations8, parameters8 = tomasulo8.run_algorithim()
print(f"Total Instructions: {parameters8[4]} | Clock_Cycles: {simulation_results8[-1][0]} | Num_FP_Add: {parameters8[0]} |  Num_FP_Mult: {parameters8[1]} | Num_Load/Store: {parameters8[2]} | Num_Registers: {parameters8[3]} | Dispatch_Size: {parameters8[5]}\n")
print(results_table8)
plot_results(rs_utilizations8, simulation_results8[-1][0], parameters8)

tomasulo9 = Tomasulo(queue9, 3, 8, 3, registers, opcodes, 1, False, latencies=default_latencies)
results_table9, simulation_results9, rs_utilizations9, parameters9 = tomasulo9.run_algorithim()
print(f"Total Instructions: {parameters9[4]} | Clock_Cycles: {simulation_results9[-1][0]} | Num_FP_Add: {parameters9[0]} |  Num_FP_Mult: {parameters9[1]} | Num_Load/Store: {parameters9[2]} | Num_Registers: {parameters9[3]} | Dispatch_Size: {parameters9[5]}\n")
print(results_table9)
plot_results(rs_utilizations9, simulation_results9[-1][0], parameters9)

tomasulo10 = Tomasulo(queue10, 3, 8, 3, registers, opcodes, 1, False, latencies=default_latencies)
results_table10, simulation_results10, rs_utilizations10, parameters10 = tomasulo10.run_algorithim()
print(f"Total Instructions: {parameters10[4]} | Clock_Cycles: {simulation_results10[-1][0]} | Num_FP_Add: {parameters10[0]} |  Num_FP_Mult: {parameters10[1]} | Num_Load/Store: {parameters10[2]} | Num_Registers: {parameters10[3]} | Dispatch_Size: {parameters10[5]}\n")
print(results_table10)
plot_results(rs_utilizations10, simulation_results10[-1][0], parameters10)

tomasulo11 = Tomasulo(queue11, 3, 8, 3, registers32, opcodes, 2, False, latencies=default_latencies)
results_table11, simulation_results11, rs_utilizations11, parameters11 = tomasulo11.run_algorithim()
print(f"Total Instructions: {parameters11[4]} | Clock_Cycles: {simulation_results11[-1][0]} | Num_FP_Add: {parameters11[0]} |  Num_FP_Mult: {parameters11[1]} | Num_Load/Store: {parameters11[2]} | Num_Registers: {parameters11[3]} | Dispatch_Size: {parameters11[5]}\n")
print(results_table11)
plot_results(rs_utilizations11, simulation_results11[-1][0], parameters11)

tomasulo12 = Tomasulo(queue12, 3, 8, 3, registers64, opcodes, 1, False, latencies=default_latencies)
results_table12, simulation_results12, rs_utilizations12, parameters12 = tomasulo12.run_algorithim()
print(f"Total Instructions: {parameters12[4]} | Clock_Cycles: {simulation_results12[-1][0]} | Num_FP_Add: {parameters12[0]} |  Num_FP_Mult: {parameters12[1]} | Num_Load/Store: {parameters12[2]} | Num_Registers: {parameters12[3]} | Dispatch_Size: {parameters12[5]}\n")
print(results_table12)
plot_results(rs_utilizations12, simulation_results12[-1][0], parameters12)

tomasulo13 = Tomasulo(queue13, 3, 32, 3, registers64, opcodes, 1, False, latencies=default_latencies)
results_table13, simulation_results13, rs_utilizations13, parameters13 = tomasulo13.run_algorithim()
print(f"Total Instructions: {parameters13[4]} | Clock_Cycles: {simulation_results13[-1][0]} | Num_FP_Add: {parameters13[0]} |  Num_FP_Mult: {parameters13[1]} | Num_Load/Store: {parameters13[2]} | Num_Registers: {parameters13[3]} | Dispatch_Size: {parameters13[5]}\n")
print(results_table13)
plot_results(rs_utilizations13, simulation_results13[-1][0], parameters13)

tomasulo14 = Tomasulo(queue14, 3, 32, 3, registers64, opcodes, 2, False, latencies=default_latencies)
results_table14, simulation_results14, rs_utilizations14, parameters14 = tomasulo14.run_algorithim()
print(f"Total Instructions: {parameters14[4]} | Clock_Cycles: {simulation_results14[-1][0]} | Num_FP_Add: {parameters14[0]} |  Num_FP_Mult: {parameters14[1]} | Num_Load/Store: {parameters14[2]} | Num_Registers: {parameters14[3]} | Dispatch_Size: {parameters14[5]}\n")
print(results_table14)
plot_results(rs_utilizations14, simulation_results14[-1][0], parameters14)

tomasulo15 = Tomasulo(queue15, 3, 32, 3, registers128, opcodes, 2, False, latencies=default_latencies)
results_table15, simulation_results15, rs_utilizations15, parameters15 = tomasulo15.run_algorithim()
print(f"Total Instructions: {parameters15[4]} | Clock_Cycles: {simulation_results15[-1][0]} | Num_FP_Add: {parameters15[0]} |  Num_FP_Mult: {parameters15[1]} | Num_Load/Store: {parameters15[2]} | Num_Registers: {parameters15[3]} | Dispatch_Size: {parameters15[5]}\n")
print(results_table15)
plot_results(rs_utilizations15, simulation_results15[-1][0], parameters15)
>>>>>>> refs/remotes/origin/main:TomasuloSimulator.py
