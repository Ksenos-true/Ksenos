namespace UVM_Assembler.Interpreter;

public class Interpreter
{
    private Memory memory;
    private Stack<int> stack;
    
    public Interpreter()
    {
        memory = new Memory();
        stack = new Stack<int>();
    }
    
    public void Execute(Assembler.Program program)
    {
        foreach (var instruction in program.Instructions)
        {
            ExecuteInstruction(instruction);
        }
    }
    
    private void ExecuteInstruction(Assembler.Instruction instruction)
    {
        switch (instruction.Type)
        {
            case Assembler.InstructionType.LOAD_CONST:
                if (!instruction.B.HasValue)
                    throw new InvalidOperationException("LOAD_CONST requires B parameter");
                
                stack.Push(instruction.B.Value);
                break;
                
            case Assembler.InstructionType.READ_MEM:
                if (!instruction.B.HasValue)
                    throw new InvalidOperationException("READ_MEM requires B parameter");
                
                int address = stack.Pop();
                int value = memory.Read(address + instruction.B.Value);
                stack.Push(value);
                break;
                
            case Assembler.InstructionType.WRITE_MEM:
                int valueToWrite = stack.Pop();
                int addressToWrite = stack.Pop();
                memory.Write(addressToWrite, valueToWrite);
                break;
                
            case Assembler.InstructionType.DIVIDE:
                if (!instruction.B.HasValue)
                    throw new InvalidOperationException("DIVIDE requires B parameter");
                
                int divisor = memory.Read(instruction.B.Value);
                int dividend = stack.Pop();
                int result = ALU.Divide(dividend, divisor);
                stack.Push(result);
                break;
                
            default:
                throw new InvalidOperationException($"Unknown instruction type: {instruction.Type}");
        }
    }
    
    public void SaveMemoryDump(string filePath, int startAddress, int endAddress)
    {
        string xml = memory.DumpToXml(startAddress, endAddress);
        File.WriteAllText(filePath, xml);
    }
    
    public int StackCount => stack.Count;
}